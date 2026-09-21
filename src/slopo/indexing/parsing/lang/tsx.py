import tree_sitter_typescript
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments
from slopo.indexing.parsing.lang.common import js_family

_LANGUAGE = Language(tree_sitter_typescript.language_tsx())
_PARSER = Parser(_LANGUAGE)

_FUNCTION_TYPES = js_family.NAMED_FUNCTION_TYPES | js_family.ANON_FUNCTION_TYPES
_JSX_TYPES = {"jsx_element", "jsx_fragment", "jsx_self_closing_element"}


def parse(source: bytes) -> list[CodeUnit]:
    stripped = strip_comments(to_utf8(source), _PARSER, _should_strip)
    tree = _PARSER.parse(stripped)
    units: list[CodeUnit] = []
    _collect_units(tree.root_node, stripped, units)
    normalize_indents(units)
    return units


def _should_strip(node: Node) -> bool:
    if node.type in js_family.COMMENT_TYPES:
        return True
    if node.type != "jsx_expression":
        return False

    children = node.named_children
    return bool(children) and all(
        child.type in js_family.COMMENT_TYPES for child in children
    )


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
    if _is_template_only(body_node):
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
    if node.type == "return_statement":
        return _template_entries(_returned_value(node), node)
    if node.type == "arrow_function":
        return _template_entries(node.child_by_field_name("body"), node)
    return []


def _template_entries(
    expr: Node | None, owner: Node
) -> list[tuple[str, Node, list[Node]]]:
    template = _template_node(expr)
    if template is None:
        return []
    return [(_enclosing_signature(owner), owner, [template])]


def _enclosing_signature(node: Node) -> str:
    fn: Node | None = node
    while fn is not None and fn.type not in _FUNCTION_TYPES:
        fn = fn.parent
    if fn is None:
        return ""
    anchor = fn
    if fn.type in js_family.ANON_FUNCTION_TYPES:
        anchor = js_family.binding_node(fn) or fn
    body = fn.child_by_field_name("body")
    text = anchor.text
    assert text is not None
    end = (body.start_byte if body is not None else fn.end_byte) - anchor.start_byte
    return text[:end].decode().strip()


def _is_template_only(body: Node) -> bool:
    if body.type == "statement_block":
        statements = [c for c in body.children if c.is_named]
        if len(statements) != 1 or statements[0].type != "return_statement":
            return False
        return _template_node(_returned_value(statements[0])) is not None
    return _template_node(body) is not None


def _template_node(expr: Node | None) -> Node | None:
    if expr is None:
        return None
    if expr.type == "parenthesized_expression":
        inner = _first_named_child(expr)
        return expr if inner is not None and inner.type in _JSX_TYPES else None
    return expr if expr.type in _JSX_TYPES else None


def _returned_value(return_statement: Node) -> Node | None:
    return _first_named_child(return_statement)


def _first_named_child(node: Node) -> Node | None:
    return next((c for c in node.children if c.is_named), None)
