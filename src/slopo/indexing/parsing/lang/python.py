import tree_sitter_python
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_python.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_LOOP_TYPES = {"for_statement", "while_statement"}

_CONDITIONAL_BODY_FIELDS = {
    "if_statement": "consequence",
    "elif_clause": "consequence",
    "else_clause": "body",
}


def parse(source: bytes) -> list[CodeUnit]:
    stripped = strip_comments(to_utf8(source), _PARSER, _should_strip)
    tree = _PARSER.parse(stripped)
    units: list[CodeUnit] = []
    _collect_units(tree.root_node, stripped, units)
    # No normalize_indents(), implemented inside parser
    return units


def _should_strip(node: Node) -> bool:
    return node.type in _COMMENT_TYPES or _is_docstring(node)


def _collect_units(node: Node, source: bytes, units: list[CodeUnit]) -> None:
    if node.type == "function_definition":
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    elif node.type == "lambda":
        unit = _lambda_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_block = node.child_by_field_name("body")
    if body_block is None:
        return None
    body = _normalize_indent(
        source, body_block, source[body_block.start_byte : body_block.end_byte].decode()
    )
    outer = (
        node.parent
        if node.parent is not None and node.parent.type == "decorated_definition"
        else node
    )
    context = _normalize_indent(
        source, outer, source[outer.start_byte : body_block.start_byte].decode()
    ).strip()
    return CodeUnit(
        body=body,
        start_line=outer.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _lambda_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_node = node.child_by_field_name("body")
    if body_node is None:
        return None
    body = source[body_node.start_byte : body_node.end_byte].decode()
    lambda_header = source[node.start_byte : body_node.start_byte].decode().strip()
    context = _lambda_context(node, lambda_header)
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _lambda_context(node: Node, lambda_header: str) -> str:
    parent = node.parent
    if parent is None:
        return lambda_header
    if parent.type == "assignment":
        left = parent.child_by_field_name("left")
        if left is not None and left.text is not None:
            return f"{left.text.decode()} = {lambda_header}"
    call_ancestor = parent.parent if parent.type == "keyword_argument" else parent
    if call_ancestor is not None and call_ancestor.type == "argument_list":
        call = call_ancestor.parent
        if call is not None and call.type == "call":
            func = call.child_by_field_name("function")
            if func is not None and func.text is not None:
                return f"{func.text.decode()} {lambda_header}"
    return lambda_header


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type in _CONDITIONAL_BODY_FIELDS:
        return _conditional_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "try_statement":
        return _try_entries(node)
    if node.type == "match_statement":
        return _match_entries(node)
    if node.type == "with_statement":
        return _with_entries(node)
    return []


def _conditional_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    field = _CONDITIONAL_BODY_FIELDS[node.type]
    block = _field_block(node, field)
    return [(_header(node, block), node, [block])] if block is not None else []


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _field_block(node, "body")
    if body is not None:
        entries.append((_header(node, body), node, [body]))
    for child in node.children:
        if child.type in {"except_clause", "finally_clause"}:
            block = _child_of_type(child, "block")
            if block is not None:
                entries.append((_header(child, block), child, [block]))
    return entries


def _match_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = node.child_by_field_name("body")
    if body is None:
        return []
    for case in body.children:
        if case.type == "case_clause":
            consequence = _field_block(case, "consequence")
            if consequence is not None:
                entries.append((_header(case, consequence), case, [consequence]))
    return entries


def _with_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, [body])] if body is not None else []


def _header(node: Node, body: Node) -> str:
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _block_unit(
    context: str, start: Node, body_nodes: list[Node], source: bytes
) -> CodeUnit:
    body = _normalize_indent(
        source,
        body_nodes[0],
        source[body_nodes[0].start_byte : body_nodes[-1].end_byte].decode(),
    )
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


def _normalize_indent(source: bytes, node: Node, text: str) -> str:
    col = node.start_point[1]
    if col == 0:
        return text
    indent = source[node.start_byte - col : node.start_byte].decode()
    lines = text.splitlines(keepends=True)
    return "".join(line.removeprefix(indent) for line in lines)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count


def _is_docstring(node: Node) -> bool:
    if node.type != "expression_statement":
        return False
    if [c.type for c in node.named_children] != ["string"]:
        return False
    parent = node.parent
    return (
        parent is not None
        and parent.type in {"module", "block"}
        and (node == parent.named_children[0])
    )
