import tree_sitter_c
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments
from slopo.indexing.parsing.lang.common import c_family

_LANGUAGE = Language(tree_sitter_c.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_LOOP_TYPES = {"for_statement", "while_statement", "do_statement"}


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
    if node.type == "function_definition":
        unit = _function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(c_family.block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_block = node.child_by_field_name("body")
    if body_block is None:
        return None
    body = source[body_block.start_byte : body_block.end_byte].decode()
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=c_family.count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=c_family.header(node, body_block),
    )


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return c_family.if_entries(node)
    if node.type in _LOOP_TYPES:
        return c_family.loop_entries(node)
    if node.type == "switch_statement":
        return c_family.switch_entries(node)
    return []
