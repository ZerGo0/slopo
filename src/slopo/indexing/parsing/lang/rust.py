import tree_sitter_rust
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_rust.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"line_comment", "block_comment"}

_FUNCTION_TYPES = {"function_item", "closure_expression", "async_block"}

_LOOP_TYPES = {"for_expression", "while_expression", "loop_expression"}

_CONTROL_FLOW_TYPES = {"if_expression", "match_expression"} | _LOOP_TYPES

_SCOPE_TYPES = {"unsafe_block"}

_BINDING_FIELDS = {"let_declaration": "value", "assignment_expression": "right"}


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
    for context, start, body in _block_entries(node):
        units.append(_block_unit(context, start, body, source))
    for child in node.children:
        _collect_units(child, source, units)


def _function_unit(node: Node, source: bytes) -> CodeUnit | None:
    # A closure body is the "body" field like a function's, but it is an arbitrary
    # expression unless the closure was written with braces.
    body = node.child_by_field_name("body") or _child_of_type(node, "block")
    if body is None:
        return None
    text = source[body.start_byte : body.end_byte].decode()
    return CodeUnit(
        body=text,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body),
        body_hash=hash_body(text),
        kind="function",
        context=_function_context(node, body),
    )


def _function_context(node: Node, body: Node) -> str:
    if node.type == "function_item":
        return _header(node, body)
    binding = _binding_node(node)
    if binding is not None:
        return _header(binding, body)
    label = _call_label(node)
    header = _header(node, body)
    return f"{label} {header}" if label else header


def _call_label(node: Node) -> str | None:
    parent = node.parent
    if parent is None or parent.type != "arguments":
        return None
    call = parent.parent
    if call is None or call.type != "call_expression":
        return None
    function = call.child_by_field_name("function")
    if function is not None and function.type == "field_expression":
        function = function.child_by_field_name("field")
    return function.text.decode() if function is not None and function.text else None


def _block_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    if node.type == "if_expression":
        return _if_entries(node)
    if node.type in _LOOP_TYPES:
        return _loop_entries(node)
    if node.type == "match_expression":
        return _match_entries(node)
    if node.type == "let_declaration":
        return _bail_out_entries(node)
    if node.type in _SCOPE_TYPES or _is_bare_block(node):
        return _scope_entries(node)
    return []


def _if_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    # `if let` is the same node with a let_condition, so its header comes out whole.
    entries: list[tuple[str | None, Node, Node]] = []
    consequence = _field_block(node, "consequence")
    if consequence is not None:
        entries.append((_header(node, consequence), node, consequence))
    else_clause = node.child_by_field_name("alternative")
    if else_clause is not None:
        # An `else if` holds an if_expression instead of a block; the walk reaches it.
        alternative = _child_of_type(else_clause, "block")
        if alternative is not None:
            entries.append(("else", else_clause, alternative))
    return entries


def _loop_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    body = _field_block(node, "body")
    return [(_header(node, body), node, body)] if body is not None else []


def _match_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    body = node.child_by_field_name("body")
    if body is None:
        return []
    entries: list[tuple[str | None, Node, Node]] = []
    for arm in body.children:
        if arm.type != "match_arm":
            continue
        # An arm's value is braced only when it needs to be; a one-expression arm
        # is that expression.
        value = arm.child_by_field_name("value")
        if value is not None and _is_extractable(value):
            entries.append((_header(arm, value), arm, value))
    return entries


def _bail_out_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    block = _field_block(node, "alternative")
    return [(_header(node, block), node, block)] if block is not None else []


def _scope_entries(node: Node) -> list[tuple[str | None, Node, Node]]:
    block = node if node.type == "block" else _child_of_type(node, "block")
    if block is None:
        return []
    # Anchor at the binding so `let task = async move` keeps the name; a scope in
    # statement position is headed by its keyword alone, and a bare block by nothing.
    anchor = _binding_node(node) or node
    return [(_header(anchor, block) or None, anchor, block)]


def _is_bare_block(node: Node) -> bool:
    # A block standing on its own rather than serving as some construct's body:
    # a statement, a block's trailing expression, or a bound value.
    if node.type != "block":
        return False
    parent = node.parent
    if parent is None:
        return False
    if parent.type in {"block", "expression_statement"}:
        return True
    return _binding_node(node) is not None


def _binding_node(node: Node) -> Node | None:
    parent = node.parent
    if parent is None:
        return None
    field = _BINDING_FIELDS.get(parent.type)
    if field is None:
        return None
    return parent if parent.child_by_field_name(field) == node else None


def _is_extractable(branch: Node) -> bool:
    # A branch that is itself a control-flow construct becomes its own unit;
    # wrapping it here would only duplicate that unit.
    return branch.type not in _CONTROL_FLOW_TYPES


def _header(node: Node, body: Node) -> str:
    # The source before the body: a signature, a loop/branch header, or a bare
    # keyword/pattern (`else`, `unsafe`, `Value::Int(i) =>`).
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def _block_unit(
    context: str | None, start: Node, body: Node, source: bytes
) -> CodeUnit:
    text = source[body.start_byte : body.end_byte].decode()
    return CodeUnit(
        body=text,
        start_line=start.start_point[0] + 1,
        end_line=body.end_point[0] + 1,
        body_node_count=_count_named_nodes(body),
        body_hash=hash_body(text),
        kind="block",
        context=context,
    )


def _field_block(node: Node, field: str) -> Node | None:
    child = node.child_by_field_name(field)
    return child if child is not None and child.type == "block" else None


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
