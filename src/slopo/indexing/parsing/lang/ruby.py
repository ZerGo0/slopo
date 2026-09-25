import tree_sitter_ruby
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_ruby.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_NAMED_FUNCTION_TYPES = {"method", "singleton_method"}

_BLOCK_TYPES = {"block", "do_block"}

_CLAUSE_FIELD = {
    "if": "consequence",
    "unless": "consequence",
    "elsif": "consequence",
    "while": "body",
    "until": "body",
    "for": "body",
    "when": "body",
    "in_clause": "body",
    "rescue": "body",
}

_SELF_BODY_TYPES = {"else", "ensure", "begin"}
_BEGIN_CLAUSE_TYPES = {"rescue", "else", "ensure"}

_MODIFIER_TYPES = {
    "if_modifier",
    "unless_modifier",
    "while_modifier",
    "until_modifier",
    "rescue_modifier",
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
    unit = _function_unit(node, source)
    if unit is not None:
        units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    if node.type in _NAMED_FUNCTION_TYPES:
        body = node.child_by_field_name("body")
        anchor = node
    elif node.type == "lambda":
        body = _lambda_body(node)
        anchor = _assignment_anchor(node)
    elif node.type in _BLOCK_TYPES and _is_call_block(node):
        body = node.child_by_field_name("body")
        assert node.parent is not None
        anchor = _call_block_anchor(node.parent)
    else:
        return None
    if body is None:
        return None
    body_text = source[body.start_byte : body.end_byte].decode()
    context = source[anchor.start_byte : body.start_byte].decode().strip()
    return CodeUnit(
        body=body_text,
        start_line=anchor.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body),
        body_hash=hash_body(body_text),
        kind="function",
        context=context,
    )


def _lambda_body(node: Node) -> Node | None:
    body = node.child_by_field_name("body")
    if body is not None and body.type in _BLOCK_TYPES:
        inner = body.child_by_field_name("body")
        return inner if inner is not None else body
    return body


def _assignment_anchor(node: Node) -> Node:
    parent = node.parent
    if (
        parent is not None
        and parent.type == "assignment"
        and parent.child_by_field_name("right") == node
    ):
        return parent
    return node


def _is_call_block(node: Node) -> bool:
    return node.parent is not None and node.parent.type == "call"


def _call_block_anchor(call: Node) -> Node:
    if _is_closure_constructor(call):
        return _assignment_anchor(call)
    return call


def _is_closure_constructor(call: Node) -> bool:
    method = call.child_by_field_name("method")
    if method is None:
        return False
    receiver = call.child_by_field_name("receiver")
    if receiver is None:
        return method.text in {b"lambda", b"proc"}
    return receiver.text == b"Proc" and method.text == b"new"


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type in _CLAUSE_FIELD:
        return _clause_field_entries(node)
    if node.type in _SELF_BODY_TYPES:
        return _self_body_entries(node)
    if node.type in _MODIFIER_TYPES:
        return _modifier_entries(node)
    return []


def _clause_field_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    clause = node.child_by_field_name(_CLAUSE_FIELD[node.type])
    if clause is None:
        return []
    body_nodes = [c for c in clause.children if c.is_named]
    if not body_nodes:
        return []
    return [(_header(node, body_nodes[0]), node, body_nodes)]


def _self_body_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    exclude = _BEGIN_CLAUSE_TYPES if node.type == "begin" else set()
    body_nodes = [c for c in node.children if c.is_named and c.type not in exclude]
    if not body_nodes:
        return []
    return [(_header(node, body_nodes[0]), node, body_nodes)]


def _modifier_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = node.child_by_field_name("body")
    if body is None:
        return []
    return [(_modifier_context(node, body), node, [body])]


def _header(node: Node, body: Node) -> str:
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _modifier_context(node: Node, body: Node) -> str:
    text = node.text
    assert text is not None
    return text[body.end_byte - node.start_byte :].decode().strip()


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


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
