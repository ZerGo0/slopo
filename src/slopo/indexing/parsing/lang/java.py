import tree_sitter_java
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_java.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"line_comment", "block_comment"}

_LOOP_TYPES = {
    "for_statement",
    "enhanced_for_statement",
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
    if node.type in {"method_declaration", "lambda_expression"}:
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_block = node.child_by_field_name("body")
    if body_block is None:  # abstract or interface method
        return None
    body = source[body_block.start_byte : body_block.end_byte].decode()
    context = _header(node, body_block)
    if node.type == "lambda_expression":
        label = _lambda_context(node)
        if label:
            context = f"{label} {context}"
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _lambda_context(node: Node) -> str | None:
    parent = node.parent
    if parent is None:
        return None
    if parent.type == "variable_declarator":  # Runnable r = () -> ...
        declaration = parent.parent
        name = parent.child_by_field_name("name")
        type_node = declaration.child_by_field_name("type") if declaration else None
        if type_node is not None and type_node.text and name is not None and name.text:
            return f"{type_node.text.decode()} {name.text.decode()} ="
        return None
    context_node = None
    if parent.type == "assignment_expression":  # this.cb = () -> ...
        context_node = parent.child_by_field_name("left")
        return (
            f"{context_node.text.decode()} ="
            if context_node and context_node.text
            else None
        )
    elif parent.type == "argument_list":  # filter(v -> ...)
        call = parent.parent
        if call is not None and call.type == "method_invocation":
            context_node = call.child_by_field_name("name")
    return context_node.text.decode() if context_node and context_node.text else None


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type in {"try_statement", "try_with_resources_statement"}:
        return _try_entries(node)
    if node.type == "switch_expression":
        return _switch_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    # An `else if` is a nested if_statement the walk reaches on its own.
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
    switch_block = _child_of_type(node, "switch_block")
    if switch_block is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for group in switch_block.children:
        if group.type == "switch_block_statement_group":
            statements = [
                c for c in group.children if c.is_named and c.type != "switch_label"
            ]
            if statements:
                entries.append((_header(group, statements[0]), group, statements))
        elif group.type == "switch_rule":
            block = _child_of_type(group, "block")
            if block is not None:
                entries.append((_header(group, block), group, [block]))
    return entries


def _header(node: Node, body: Node) -> str:
    # Keep the source before the body; for do-while this is just `do`.
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
