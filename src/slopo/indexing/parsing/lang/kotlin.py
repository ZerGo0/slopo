import tree_sitter_kotlin
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_kotlin.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"line_comment", "block_comment"}

_FUNCTION_TYPES = {
    "function_declaration",
    "getter",
    "setter",
    "secondary_constructor",
    "anonymous_function",
    "anonymous_initializer",
    "lambda_literal",
}

_LOOP_TYPES = {"for_statement", "while_statement", "do_while_statement"}

_CONTROL_FLOW_TYPES = {
    "if_expression",
    "when_expression",
    "try_expression",
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
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    if node.type == "lambda_literal":
        # Lambda statements are direct children, with no separate body node.
        arrow = _child_of_type(node, "->")
        header_end = arrow.end_byte if arrow else node.children[0].end_byte
        text = "{" + source[header_end : node.end_byte].decode()
        body_nodes = [c for c in node.named_children if c.start_byte >= header_end]
    else:
        wrapper = _child_of_type(node, "function_body") or _child_of_type(node, "block")
        if wrapper is None:  # abstract function or body-less constructor
            return None
        value = _last_named(wrapper) if wrapper.type == "function_body" else wrapper
        if value is None:
            return None
        # An expression body's `=` belongs to the wrapper, not the body value.
        header_end = wrapper.start_byte
        text = source[value.start_byte : value.end_byte].decode()
        body_nodes = [value]
    parent = node.parent
    anchor = (
        parent
        if parent is not None
        and parent.type in {"property_declaration", "assignment"}
        and node.type in {"anonymous_function", "lambda_literal"}
        else node
    )
    return CodeUnit(
        body=text,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=sum(_count_named_nodes(n) for n in body_nodes)
        + (node.type == "lambda_literal"),
        body_hash=hash_body(text),
        kind="function",
        context=(
            _lambda_context(node, source, header_end)
            if node.type == "lambda_literal"
            else source[anchor.start_byte : header_end].decode().strip() or None
        ),
    )


def _lambda_context(node: Node, source: bytes, header_end: int) -> str | None:
    parent = node.parent
    label = ""
    if parent is not None and parent.type in {"property_declaration", "assignment"}:
        label = source[parent.start_byte : node.start_byte].decode().strip()
    else:
        if parent is not None and parent.type == "value_argument":
            parent = parent.parent
        call = parent.parent if parent is not None else None
        if call is not None and call.type == "call_expression":
            callee = call.children[0]
            while callee.type == "call_expression":
                callee = callee.children[0]
            if callee.type == "navigation_expression":
                callee = callee.named_children[-1]
            label = source[callee.start_byte : callee.end_byte].decode()
    parameters = source[node.children[0].end_byte : header_end].decode().strip()
    return " ".join(part for part in (label, parameters) if part) or None


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    if node.type == "if_expression":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "try_expression":
        return _try_entries(node)
    if node.type == "when_expression":
        return _when_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    # The consequence follows the `)` closing the condition; the alternative
    # follows `else`. An `else if` alternative is a nested if_expression the walk
    # reaches on its own, so _is_extractable skips it here.
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = _first_named_after(node, ")")
    if consequence is not None and _is_extractable(consequence):
        entries.append((_header(node, consequence), node, [consequence]))
    alternative = _first_named_after(node, "else")
    if alternative is not None and _is_extractable(alternative):
        else_keyword = _child_of_type(node, "else") or alternative
        entries.append(("else", else_keyword, [alternative]))
    return entries


def _loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    # for/while bodies follow the `)` closing the header; a do-while body
    # follows the `do` keyword (its `while (...)` comes after).
    anchor = "do" if node.type == "do_while_statement" else ")"
    body = _first_named_after(node, anchor)
    if body is None or not _is_extractable(body):
        return []
    return [(_header(node, body), node, [body])]


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = _child_of_type(node, "block")
    if body is not None:
        entries.append((_header(node, body), node, [body]))
    for child in node.children:
        if child.type == "catch_block":
            catch_body = _child_of_type(child, "block")
            if catch_body is not None:
                entries.append((_header(child, catch_body), child, [catch_body]))
        elif child.type == "finally_block":
            finally_body = _child_of_type(child, "block")
            if finally_body is not None:
                entries.append(("finally", child, [finally_body]))
    return entries


def _when_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    for entry in node.children:
        if entry.type != "when_entry":
            continue
        body = _first_named_after(entry, "->")
        if body is not None and _is_extractable(body):
            entries.append((_header(entry, body), entry, [body]))
    return entries


def _is_extractable(branch: Node) -> bool:
    # A branch that is itself a control-flow construct becomes its own unit;
    # wrapping it here would only duplicate that unit.
    return branch.type not in _CONTROL_FLOW_TYPES


def _header(node: Node, body: Node) -> str:
    # The source before the body: a signature, a block header, or a bare
    # keyword (`do`, `else ->`).
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


def _first_named_after(node: Node, token: str) -> Node | None:
    seen = False
    for child in node.children:
        if child.type == token:
            seen = True
        elif seen and child.is_named:
            return child
    return None


def _last_named(node: Node) -> Node | None:
    return next((c for c in reversed(node.children) if c.is_named), None)


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
