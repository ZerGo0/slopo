import tree_sitter_go
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_go.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_NAMED_FUNCTION_TYPES = {"function_declaration", "method_declaration"}

_SWITCH_TYPES = {
    "expression_switch_statement",
    "type_switch_statement",
    "select_statement",
}
_CASE_TYPES = {"expression_case", "type_case", "communication_case", "default_case"}

_BINDING_TYPES = {"var_spec", "short_var_declaration", "assignment_statement"}


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
    if node.type in _NAMED_FUNCTION_TYPES:
        unit = _function_unit(node, source, _header_context(node))
        if unit is not None:
            units.append(unit)
    elif node.type == "func_literal":
        unit = _function_unit(node, source, _func_literal_context(node, source))
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes, context: str | None) -> CodeUnit | None:
    body_block = node.child_by_field_name("body")
    if body_block is None:  # forward-declared function (assembly body elsewhere)
        return None
    body = source[body_block.start_byte : body_block.end_byte].decode()
    return CodeUnit(
        name="<unset>",
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _header_context(node: Node) -> str | None:
    body_block = node.child_by_field_name("body")
    return _header(node, body_block) if body_block is not None else None


def _func_literal_context(node: Node, source: bytes) -> str | None:
    # A func_literal is anonymous; label it with the header before its body. When
    # it is bound (f := func() {...} / w.cb = func() {...}), anchor at the binding
    # so the name is kept alongside the signature; otherwise just the signature.
    body_block = node.child_by_field_name("body")
    if body_block is None:
        return None
    anchor = _binding_node(node) or node
    return source[anchor.start_byte : body_block.start_byte].decode().strip()


def _binding_node(node: Node) -> Node | None:
    parent = node.parent  # the func_literal sits in an expression_list
    if parent is None or parent.type != "expression_list":
        return None
    binding = parent.parent
    if binding is not None and binding.type in _BINDING_TYPES:
        return binding
    return None


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type == "for_statement":
        return _loop_entries(node)
    if node.type in _SWITCH_TYPES:
        return _case_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    # An `else if` makes the alternative a nested if_statement, not a block, so
    # _field_block skips it here and the walk reaches that if on its own.
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = _field_block(node, "consequence")
    if consequence is not None:
        entries.append((_header(node, consequence), node, [consequence]))
    alternative = _field_block(node, "alternative")
    if alternative is not None:
        else_keyword = _child_of_type(node, "else") or alternative
        entries.append(("else", else_keyword, [alternative]))
    return entries


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _case_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    for case in node.children:
        if case.type not in _CASE_TYPES:
            continue
        statements = _child_of_type(case, "statement_list")
        if statements is not None:
            entries.append((_header(case, statements), case, [statements]))
    return entries


def _header(node: Node, body: Node) -> str:
    # The source before the body: a signature, a loop/branch header, or a bare
    # keyword/label (`else`, `case 1:`, `default:`).
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
    return child if child is not None and child.type == "block" else None


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
