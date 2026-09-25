import tree_sitter_php
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_php.language_php())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_LOOP_TYPES = {"for_statement", "foreach_statement", "while_statement", "do_statement"}


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
    if node.type in {
        "function_definition",
        "method_declaration",
        "anonymous_function",
        "arrow_function",
    }:
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    if node.type == "arrow_function":
        return _arrow_function_unit(node, source)
    body_block = node.child_by_field_name("body")
    if body_block is None:
        return None
    body = source[body_block.start_byte : body_block.end_byte].decode()
    header_start = _past_attributes(node)
    context = _header_from(header_start, body_block, source)
    if node.type == "anonymous_function":
        label = _anon_context(node)
        if label:
            context = f"{label} {context}"
    return CodeUnit(
        body=body,
        start_line=header_start.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _arrow_function_unit(node: Node, source: bytes) -> CodeUnit:
    body_node = node.child_by_field_name("body")
    assert body_node is not None
    body = source[body_node.start_byte : body_node.end_byte].decode()
    context = _header(node, body_node)
    label = _anon_context(node)
    if label:
        context = f"{label} {context}"
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _anon_context(node: Node) -> str | None:
    parent = node.parent
    if parent is None:
        return None
    if parent.type == "assignment_expression":
        left = parent.child_by_field_name("left")
        if left is not None and left.text:
            return f"{left.text.decode()} ="
        return None
    if parent.type == "argument":
        call = parent.parent  # arguments node
        if call is not None:
            call = call.parent  # function_call_expression
        if call is not None and call.type == "function_call_expression":
            fn = call.child_by_field_name("function")
            if fn is not None and fn.text:
                return fn.text.decode()
    return None


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "try_statement":
        return _try_entries(node)
    if node.type == "switch_statement":
        return _switch_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _field_block(node, "body")
    if body is not None:
        entries.append((_header(node, body), node, [body]))
    for child in node.children:
        if child.type == "else_if_clause":
            clause_body = _field_block(child, "body")
            if clause_body is not None:
                entries.append((_header(child, clause_body), child, [clause_body]))
        elif child.type == "else_clause":
            clause_body = _field_block(child, "body")
            if clause_body is not None:
                entries.append(("else", child, [clause_body]))
    return entries


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _field_block(node, "body")
    if body is not None:
        entries.append(("try", node, [body]))
    for child in node.children:
        if child.type == "catch_clause":
            catch_body = _field_block(child, "body")
            if catch_body is not None:
                entries.append((_header(child, catch_body), child, [catch_body]))
        elif child.type == "finally_clause":
            finally_body = _field_block(child, "body")
            if finally_body is not None:
                entries.append(("finally", child, [finally_body]))
    return entries


def _switch_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    switch_block = _child_of_type(node, "switch_block")
    if switch_block is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for child in switch_block.children:
        if child.type in {"case_statement", "default_statement"}:
            statements = [
                c
                for c in child.children
                if c.is_named and c.type not in {"encapsed_string", "string", "integer"}
            ]
            if statements:
                entries.append((_switch_label(child), child, statements))
    return entries


def _switch_label(node: Node) -> str:
    if node.type == "default_statement":
        return "default:"
    text = node.text
    assert text is not None
    full = text.decode()
    colon_pos = full.index(":")
    return full[: colon_pos + 1].strip()


def _past_attributes(node: Node) -> Node:
    for child in node.children:
        if child.type != "attribute_list":
            return child
    return node


def _header(node: Node, body: Node) -> str:
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _header_from(start: Node, body: Node, source: bytes) -> str:
    return source[start.start_byte : body.start_byte].decode().strip()


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
    return child if child is not None and child.type == "compound_statement" else None


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
