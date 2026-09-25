import tree_sitter_c_sharp
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_c_sharp.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_NAMED_FUNCTION_TYPES = {
    "method_declaration",
    "constructor_declaration",
    "local_function_statement",
    "accessor_declaration",
}
_ANON_FUNCTION_TYPES = {"lambda_expression", "anonymous_method_expression"}

_BINDING_TYPES = {"variable_declarator", "assignment_expression"}

_LOOP_TYPES = {
    "for_statement",
    "foreach_statement",
    "while_statement",
    "do_statement",
}

_SCOPE_TYPES = {"using_statement", "lock_statement"}


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
    body_node = _body_node(node)
    if body_node is None:
        return None
    body = source[body_node.start_byte : body_node.end_byte].decode()
    anchor = node
    if node.type in _ANON_FUNCTION_TYPES:
        anchor = _binding_node(node) or node
    context = source[anchor.start_byte : body_node.start_byte].decode().strip()
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=body_node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _binding_node(node: Node) -> Node | None:
    # An anonymous unit takes its label from what it is bound to; a callback passed
    # as a call argument has no binding, so its context is just its own header.
    parent = node.parent
    if parent is None or parent.type not in _BINDING_TYPES:
        return None
    if parent.type == "variable_declarator":
        # The declared type is a sibling of the declarator on the enclosing
        # variable_declaration, so anchor there to keep it in the label.
        declaration = parent.parent
        if declaration is not None and declaration.type == "variable_declaration":
            return declaration
    return parent


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "try_statement":
        return _try_entries(node)
    if node.type == "switch_statement":
        return _switch_entries(node)
    if node.type in _SCOPE_TYPES:
        return _scope_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    # An `else if` is a nested if_statement the walk reaches on its own.
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = _field_block(node, "consequence")
    if consequence is not None:
        entries.append((_header(node, consequence), node, [consequence]))
    alternative = node.child_by_field_name("alternative")
    if alternative is not None and alternative.type == "block":
        else_keyword = _child_of_type(node, "else") or alternative
        entries.append(("else", else_keyword, [alternative]))
    return entries


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _field_block(node, "body")
    if body is not None:
        entries.append((_header(node, body), node, [body]))
    for child in node.children:
        if child.type == "catch_clause":
            catch_body = _field_block(child, "body")
            if catch_body is not None:
                entries.append((_header(child, catch_body), child, [catch_body]))
        elif child.type == "finally_clause":
            finally_body = _child_of_type(child, "block")
            if finally_body is not None:
                entries.append(("finally", child, [finally_body]))
    return entries


def _switch_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = node.child_by_field_name("body")
    if body is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for section in body.children:
        if section.type != "switch_section":
            continue
        statements = _section_statements(section)
        if statements:
            header = _header(section, statements[0])
            entries.append((header, section, statements))
    return entries


def _section_statements(section: Node) -> list[Node]:
    # A switch_section has no fields: its labels (`case <pattern>:`, `default:`)
    # are loose tokens, so statements are the named children after the last colon.
    # Consecutive fall-through labels form their own empty sections, skipped above.
    colons = [i for i, c in enumerate(section.children) if c.type == ":"]
    if not colons:
        return []
    return [c for c in section.children[colons[-1] + 1 :] if c.is_named]


def _scope_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = node.child_by_field_name("body")  # using_statement
    if body is None:
        body = _child_of_type(node, "block")  # lock_statement
    if body is not None and body.type == "block":
        return [(_header(node, body), node, [body])]
    return []


def _header(node: Node, body: Node) -> str:
    # The source before the body: a signature, a loop/branch/scope header, or a
    # bare keyword/label (`else`, `finally`, `case 1:`, `default:`).
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _block_unit(
    context: str, start: Node, body_nodes: list[Node], source: bytes
) -> CodeUnit:
    body = source[body_nodes[0].start_byte : body_nodes[-1].end_byte].decode()
    return CodeUnit(
        body=body,
        start_line=start.start_point[0] + 1,
        end_line=body_nodes[-1].end_point[0] + 1,
        body_node_count=sum(_count_named_nodes(n) for n in body_nodes),
        body_hash=hash_body(body),
        kind="block",
        context=context,
    )


def _body_node(node: Node) -> Node | None:
    # Methods, constructors, local functions, accessors and lambdas expose their
    # body via the "body" field; anonymous_method_expression (`delegate(){}`) has
    # no such field, so its block is found by scanning children.
    body = node.child_by_field_name("body")
    if body is None:
        body = _child_of_type(node, "block")
    if body is not None and body.type == "arrow_expression_clause":
        # Normalize expression bodies so `=>` heads the context and the body is the
        # expression alone, matching a lambda's `x => expr` split.
        return next((c for c in body.children if c.is_named), body)
    return body


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
