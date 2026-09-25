import tree_sitter_swift
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_swift.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment", "multiline_comment"}

_FUNCTION_TYPES = {
    "function_declaration",
    "init_declaration",
    "deinit_declaration",
    "lambda_literal",
    "computed_getter",
    "computed_setter",
    "willset_clause",
    "didset_clause",
    "computed_property",
}

_LOOP_TYPES = {"for_statement", "while_statement", "repeat_while_statement"}

_CONTROL_FLOW_TYPES = {
    "if_statement",
    "guard_statement",
    "switch_statement",
    "do_statement",
} | _LOOP_TYPES


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
    if node.type in _FUNCTION_TYPES:
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body, end in _block_entries(node):
        units.append(_block_unit(context, start, body, end, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body = _body_statements(node)
    if body is None:
        return None
    text = _body_text(body, source)
    return CodeUnit(
        body=text,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body),
        body_hash=hash_body(text),
        kind="function",
        context=_function_context(node, body, source),
    )


def _function_context(node: Node, body: Node, source: bytes) -> str | None:
    if node.type == "lambda_literal":
        return _lambda_context(node, source)
    if node.type == "computed_property":
        return _computed_property_context(node, source)
    return _header(node, body)


def _computed_property_context(node: Node, source: bytes) -> str | None:
    parent = node.parent
    if parent is None:
        return None
    return source[parent.start_byte : node.start_byte].decode().strip() or None


def _lambda_context(node: Node, source: bytes) -> str | None:
    label = _binding_label(node, source) or _call_label(node) or ""
    return (
        " ".join(part for part in (label, _lambda_header(node, source)) if part) or None
    )


def _lambda_header(node: Node, source: bytes) -> str:
    statements = _body_statements(node)
    end = statements.start_byte if statements is not None else node.end_byte
    return source[node.start_byte : end].decode().strip()


def _binding_label(node: Node, source: bytes) -> str | None:
    parent = node.parent
    if (
        parent is not None
        and parent.type == "property_declaration"
        and parent.child_by_field_name("value") == node
    ):
        return source[parent.start_byte : node.start_byte].decode().strip()
    return None


def _call_label(node: Node) -> str | None:
    parent = node.parent
    if parent is not None and parent.type == "value_argument":
        arguments = parent.parent
        parent = arguments.parent if arguments is not None else None
    if parent is None or parent.type != "call_suffix":
        return None
    call = parent.parent
    if call is None or call.type != "call_expression":
        return None
    callee = call.children[0]
    if callee.type == "navigation_expression":
        suffix = callee.child_by_field_name("suffix")
        member = suffix.child_by_field_name("suffix") if suffix is not None else None
        return member.text.decode() if member is not None and member.text else None
    return callee.text.decode() if callee.text else None


def _body_statements(node: Node) -> Node | None:
    body = node.child_by_field_name("body")
    container = body if body is not None else node
    return _child_of_type(container, "statements")


# (context, keyword node for start_line, body for text/count, node whose end marks end_line)
_BlockEntry = tuple[str | None, Node, Node, Node]


def _block_entries(node: Node) -> list[_BlockEntry]:
    if node.type == "if_statement":
        return _if_entries(node)
    if node.type == "guard_statement":
        return _guard_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "switch_statement":
        return _switch_entries(node)
    if node.type == "do_statement":
        return _do_entries(node)
    return []


def _if_entries(node: Node) -> list[_BlockEntry]:
    entries: list[_BlockEntry] = []
    consequence = _child_of_type(node, "statements")
    if consequence is not None:
        entries.append((_header(node, consequence), node, consequence, consequence))
    else_keyword = _child_of_type(node, "else")
    if else_keyword is not None:
        alternative = _statements_after(node, else_keyword)
        if alternative is not None:
            entries.append(("else", else_keyword, alternative, alternative))
    return entries


def _guard_entries(node: Node) -> list[_BlockEntry]:
    else_keyword = _child_of_type(node, "else")
    if else_keyword is None:
        return []
    body = _statements_after(node, else_keyword)
    if body is None:
        return []
    return [(_header(node, body), node, body, body)]


def _loop_entries(node: Node) -> list[_BlockEntry]:
    body = _child_of_type(node, "statements")
    return [(_header(node, body), node, body, body)] if body is not None else []


def _switch_entries(node: Node) -> list[_BlockEntry]:
    entries: list[_BlockEntry] = []
    for entry in node.children:
        if entry.type != "switch_entry":
            continue
        body = _child_of_type(entry, "statements")
        if body is not None:
            entries.append((_header(entry, body), entry, body, _last_named(body)))
    return entries


def _do_entries(node: Node) -> list[_BlockEntry]:
    entries: list[_BlockEntry] = []
    body = _child_of_type(node, "statements")
    if body is not None:
        entries.append((_header(node, body), node, body, body))
    for child in node.children:
        if child.type != "catch_block":
            continue
        catch_body = _child_of_type(child, "statements")
        if catch_body is not None:
            entries.append((_header(child, catch_body), child, catch_body, catch_body))
    return entries


def _header(node: Node, body: Node) -> str | None:
    text = node.text
    assert text is not None
    header = text[: body.start_byte - node.start_byte].decode().strip()
    header = header[:-1].strip() if header.endswith("{") else header
    return header or None


def _body_text(body: Node, source: bytes) -> str:
    return source[body.start_byte : body.end_byte].decode().rstrip()


def _block_unit(
    context: str | None, start: Node, body: Node, end: Node, source: bytes
) -> CodeUnit:
    text = _body_text(body, source)
    return CodeUnit(
        body=text,
        start_line=start.start_point[0] + 1,
        end_line=end.end_point[0] + 1,
        body_node_count=_count_named_nodes(body),
        body_hash=hash_body(text),
        kind="block",
        context=context,
    )


def _last_named(node: Node) -> Node:
    named = [child for child in node.children if child.is_named]
    return named[-1] if named else node


def _statements_after(node: Node, token: Node) -> Node | None:
    seen = False
    for child in node.children:
        if child == token:
            seen = True
        elif seen and child.type == "statements":
            return child
    return None


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
