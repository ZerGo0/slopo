import tree_sitter_svelte
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, normalize_indents, to_utf8
from slopo.indexing.parsing.lang import javascript, typescript

_PARSER = Parser(Language(tree_sitter_svelte.language()))


def parse(source: bytes) -> list[CodeUnit]:
    source = to_utf8(source)
    root = _PARSER.parse(source).root_node
    units: list[CodeUnit] = []
    template_language = _template_language(root, source)
    _collect_units(root, source, template_language, units)
    normalize_indents(units)
    return units


def _collect_units(
    node: Node,
    source: bytes,
    template_language: str,
    units: list[CodeUnit],
) -> None:
    if node.type == "script_element":
        _script_units(node, source, units)
        return
    if node.type == "style_element":
        return
    if node.type == "svelte_raw_text":
        _embedded_units(node, source, template_language, units)
        return
    for child in node.named_children:
        _collect_units(child, source, template_language, units)


def _script_units(node: Node, source: bytes, units: list[CodeUnit]) -> None:
    start_tag = _child(node, "start_tag")
    body = _child(node, "raw_text")
    if start_tag is None or body is None:
        return
    language = _script_language(start_tag, source)
    if language is not None:
        _embedded_units(body, source, language, units)


def _embedded_units(
    node: Node, source: bytes, language: str, units: list[CodeUnit]
) -> None:
    embedded = source[node.start_byte : node.end_byte]
    parser = typescript.parse if language == "typescript" else javascript.parse
    for unit in parser(embedded):
        unit.start_line += node.start_point[0]
        unit.end_line += node.start_point[0]
        unit.language = language
        units.append(unit)


def _template_language(root: Node, source: bytes) -> str:
    for child in root.named_children:
        if child.type != "script_element":
            continue
        start_tag = _child(child, "start_tag")
        if (
            start_tag is not None
            and _script_language(start_tag, source) == "typescript"
        ):
            return "typescript"
    return "javascript"


def _script_language(start_tag: Node, source: bytes) -> str | None:
    for attribute in start_tag.named_children:
        if attribute.type != "attribute":
            continue
        name = _child(attribute, "attribute_name")
        if name is None or _text(name, source).lower() != "lang":
            continue
        value = _attribute_value(attribute, source).lower()
        if value in {"ts", "typescript"}:
            return "typescript"
        if value in {"js", "javascript"}:
            return "javascript"
        return None
    return "javascript"


def _attribute_value(attribute: Node, source: bytes) -> str:
    value = _child(attribute, "attribute_value")
    if value is not None:
        return _text(value, source)
    quoted = _child(attribute, "quoted_attribute_value")
    if quoted is not None:
        inner = _child(quoted, "attribute_value")
        return _text(inner, source) if inner is not None else ""
    return ""


def _child(node: Node, type_: str) -> Node | None:
    return next((child for child in node.named_children if child.type == type_), None)


def _text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode()
