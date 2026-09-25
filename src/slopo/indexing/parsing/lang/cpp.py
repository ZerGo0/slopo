import tree_sitter_cpp
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments
from slopo.indexing.parsing.lang.common import c_family

_LANGUAGE = Language(tree_sitter_cpp.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_LOOP_TYPES = {
    "for_statement",
    "for_range_loop",
    "while_statement",
    "do_statement",
}

_FUNCTION_TYPES = {"function_definition", "lambda_expression"}


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
    for context, start, body_nodes in _block_entries(node):
        units.append(c_family.block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    body_block = node.child_by_field_name("body")
    if body_block is None:
        return None
    body = source[body_block.start_byte : body_block.end_byte].decode()
    context = c_family.header(node, body_block)
    if node.type == "lambda_expression":
        prefix = _lambda_context(node)
        if prefix:
            context = f"{prefix} {context}"
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=c_family.count_named_nodes(body_block),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_statement":
        return c_family.if_entries(node)
    if node.type in _LOOP_TYPES:
        return c_family.loop_entries(node)
    if node.type == "switch_statement":
        return c_family.switch_entries(node)
    if node.type == "try_statement":
        return _try_entries(node)
    return []


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = c_family.field_block(node, "body")
    if body is not None:
        entries.append((c_family.header(node, body), node, [body]))
    for child in node.children:
        if child.type != "catch_clause":
            continue
        catch_body = c_family.field_block(child, "body")
        if catch_body is not None:
            entries.append((c_family.header(child, catch_body), child, [catch_body]))
    return entries


def _lambda_context(node: Node) -> str | None:
    parent = node.parent
    if parent is None:
        return None
    if parent.type == "init_declarator":
        declaration = parent.parent
        type_ = _text(declaration.child_by_field_name("type")) if declaration else None
        return _binding_label(type_, _text(parent.child_by_field_name("declarator")))
    if parent.type == "field_declaration":
        type_ = _text(parent.child_by_field_name("type"))
        return _binding_label(type_, _text(parent.child_by_field_name("declarator")))
    if parent.type == "assignment_expression":
        left = _text(parent.child_by_field_name("left"))
        return f"{left} =" if left else None
    return None


def _binding_label(type_: str | None, name: str | None) -> str | None:
    if name is None:
        return None
    return f"{type_} {name} =" if type_ else f"{name} ="


def _text(node: Node | None) -> str | None:
    return node.text.decode() if node is not None and node.text is not None else None
