import tree_sitter_typescript
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_typescript.language_typescript())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

# Bodyless signatures (function_signature, abstract_method_signature,
# method_signature) and type-only declarations are intentionally absent:
# they carry no executable body to compare.
_NAMED_FUNCTION_TYPES = {
    "function_declaration",
    "generator_function_declaration",
    "method_definition",
}
_ANON_FUNCTION_TYPES = {"arrow_function", "function_expression"}

_BINDING_TYPES = {
    "variable_declarator",
    "assignment_expression",
    "pair",
    "field_definition",
}

_LOOP_TYPES = {
    "for_statement",
    "for_in_statement",
    "while_statement",
    "do_statement",
}


def parse(source: bytes) -> list[CodeUnit]:
    stripped = strip_comments(to_utf8(source), _PARSER, _should_strip)
    tree = _PARSER.parse(stripped)
    units: list[CodeUnit] = []
    _collect_units(tree.root_node, stripped, units)
    normalize_indents(units)
    return units


def _should_strip(node: Node) -> bool:
    return node.type in _COMMENT_TYPES


def _collect_units(node: Node, source: bytes, units: list[CodeUnit]) -> None:
    if node.type in _NAMED_FUNCTION_TYPES or node.type in _ANON_FUNCTION_TYPES:
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    # An arrow's body is a statement_block or a bare expression; both are kept.
    body_node = node.child_by_field_name("body")
    if body_node is None:
        return None
    body = source[body_node.start_byte : body_node.end_byte].decode()
    anchor = node
    if node.type in _ANON_FUNCTION_TYPES:
        anchor = _binding_node(node) or node
    context = source[anchor.start_byte : body_node.start_byte].decode().strip()
    return CodeUnit(
        name="<unset>",
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _binding_node(node: Node) -> Node | None:
    parent = node.parent
    if parent is not None and parent.type in _BINDING_TYPES:
        return parent
    return None


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "switch_statement":
        return _case_entries(node)
    if node.type == "try_statement":
        return _try_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = _field_block(node, "consequence")
    if consequence is not None:
        entries.append((_header(node, consequence), node, [consequence]))
    # The alternative is an else_clause wrapping either a block (plain else) or a
    # nested if_statement (else if); the walk reaches that nested if on its own.
    alternative = node.child_by_field_name("alternative")
    if alternative is not None:
        block = _child_of_type(alternative, "statement_block")
        if block is not None:
            entries.append(("else", alternative, [block]))
    return entries


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _case_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    switch_body = node.child_by_field_name("body")
    if switch_body is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for case in switch_body.children:
        if case.type not in {"switch_case", "switch_default"}:
            continue
        statements = case.children_by_field_name("body")
        if statements:
            entries.append((_header(case, statements[0]), case, statements))
    return entries


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _field_block(node, "body")
    if body is not None:
        entries.append((_header(node, body), node, [body]))
    handler = node.child_by_field_name("handler")  # catch_clause
    if handler is not None:
        catch_body = _field_block(handler, "body")
        if catch_body is not None:
            entries.append((_header(handler, catch_body), handler, [catch_body]))
    finalizer = node.child_by_field_name("finalizer")  # finally_clause
    if finalizer is not None:
        finally_body = _field_block(finalizer, "body")
        if finally_body is not None:
            entries.append(("finally", finalizer, [finally_body]))
    return entries


def _header(node: Node, body: Node) -> str:
    # The source before the body: a signature, a loop/branch header, or a bare
    # keyword/label (`else`, `try`, `case 1:`, `default:`).
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _block_unit(
    context: str, start: Node, body_nodes: list[Node], source: bytes
) -> CodeUnit:
    body = source[body_nodes[0].start_byte : body_nodes[-1].end_byte].decode()
    return CodeUnit(
        name="<unset>",
        body=body,
        start_line=start.start_point[0] + 1,
        end_line=body_nodes[-1].end_point[0] + 1,
        body_node_count=sum(_count_named_nodes(n) for n in body_nodes),
        body_hash=hash_body(body),
        kind="block",
        context=context,
    )


def _field_block(node: Node, field: str) -> Node | None:
    child = node.child_by_field_name(field)
    return child if child is not None and child.type == "statement_block" else None


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
