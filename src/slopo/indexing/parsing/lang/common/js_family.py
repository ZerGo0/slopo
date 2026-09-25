from tree_sitter import Node

from slopo.indexing.parsing.base import CodeUnit, hash_body


COMMENT_TYPES = {"comment"}

NAMED_FUNCTION_TYPES = {
    "function_declaration",
    "generator_function_declaration",
    "method_definition",
}
ANON_FUNCTION_TYPES = {"arrow_function", "function_expression"}

BINDING_TYPES = {
    "variable_declarator",
    "assignment_expression",
    "pair",
    "field_definition",
}

LOOP_TYPES = {
    "for_statement",
    "for_in_statement",
    "while_statement",
    "do_statement",
}


def binding_node(node: Node) -> Node | None:
    parent = node.parent
    if parent is not None and parent.type in BINDING_TYPES:
        return parent
    return None


def if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = field_block(node, "consequence")
    if consequence is not None:
        entries.append((header(node, consequence), node, [consequence]))
    alternative = node.child_by_field_name("alternative")
    if alternative is not None:
        block = child_of_type(alternative, "statement_block")
        if block is not None:
            entries.append(("else", alternative, [block]))
    return entries


def loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = field_block(node, "body")
    return [(header(node, body), node, [body])] if body is not None else []


def case_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    switch_body = node.child_by_field_name("body")
    if switch_body is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for case in switch_body.children:
        if case.type not in {"switch_case", "switch_default"}:
            continue
        statements = case.children_by_field_name("body")
        if statements:
            entries.append((header(case, statements[0]), case, statements))
    return entries


def try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    body = field_block(node, "body")
    if body is not None:
        entries.append((header(node, body), node, [body]))
    handler = node.child_by_field_name("handler")  # catch_clause
    if handler is not None:
        catch_body = field_block(handler, "body")
        if catch_body is not None:
            entries.append((header(handler, catch_body), handler, [catch_body]))
    finalizer = node.child_by_field_name("finalizer")  # finally_clause
    if finalizer is not None:
        finally_body = field_block(finalizer, "body")
        if finally_body is not None:
            entries.append(("finally", finalizer, [finally_body]))
    return entries


def header(node: Node, body: Node) -> str:
    text = node.text
    assert text is not None
    return text[: body.start_byte - node.start_byte].decode().strip()


def block_unit(
    context: str, start: Node, body_nodes: list[Node], source: bytes
) -> CodeUnit:
    body = source[body_nodes[0].start_byte : body_nodes[-1].end_byte].decode()
    return CodeUnit(
        body=body,
        start_line=start.start_point[0] + 1,
        end_line=body_nodes[-1].end_point[0] + 1,
        body_node_count=sum(count_named_nodes(n) for n in body_nodes),
        body_hash=hash_body(body),
        kind="block",
        context=context,
    )


def field_block(node: Node, field: str) -> Node | None:
    child = node.child_by_field_name(field)
    return child if child is not None and child.type == "statement_block" else None


def child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += count_named_nodes(child)
    return count
