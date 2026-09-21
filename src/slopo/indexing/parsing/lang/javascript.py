import tree_sitter_javascript
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments
from slopo.indexing.parsing.lang.common import js_family

_LANGUAGE = Language(tree_sitter_javascript.language())
_PARSER = Parser(_LANGUAGE)


def parse(source: bytes) -> list[CodeUnit]:
    stripped = strip_comments(to_utf8(source), _PARSER, _should_strip)
    tree = _PARSER.parse(stripped)
    units: list[CodeUnit] = []
    _collect_units(tree.root_node, stripped, units)
    normalize_indents(units)
    return units


def _should_strip(node: Node) -> bool:
    return node.type in js_family.COMMENT_TYPES


def _collect_units(node: Node, source: bytes, units: list[CodeUnit]) -> None:
    if (
        node.type in js_family.NAMED_FUNCTION_TYPES
        or node.type in js_family.ANON_FUNCTION_TYPES
    ):
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(js_family.block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_node = node.child_by_field_name("body")
    if body_node is None:
        return None
    body = source[body_node.start_byte : body_node.end_byte].decode()
    anchor = node
    if node.type in js_family.ANON_FUNCTION_TYPES:
        anchor = js_family.binding_node(node) or node
    context = source[anchor.start_byte : body_node.start_byte].decode().strip()
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=js_family.count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return js_family.if_entries(node)
    if node.type in js_family.LOOP_TYPES:
        return js_family.loop_entries(node)
    if node.type == "switch_statement":
        return js_family.case_entries(node)
    if node.type == "try_statement":
        return js_family.try_entries(node)
    return []
