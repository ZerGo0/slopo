from tree_sitter import Node

from slopo.indexing.parsing.base import CodeUnit, hash_body


def if_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    consequence = field_block(node, "consequence")
    if consequence is not None:
        entries.append((header(node, consequence), node, [consequence]))
    else_clause = node.child_by_field_name("alternative")
    if else_clause is not None:
        alternative = child_of_type(else_clause, "compound_statement")
        if alternative is not None:
            else_keyword = child_of_type(else_clause, "else") or alternative
            entries.append(("else", else_keyword, [alternative]))
    return entries


def loop_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = field_block(node, "body")
    return [(header(node, body), node, [body])] if body is not None else []


def switch_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    body = node.child_by_field_name("body")
    if body is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    for case in body.children:
        if case.type != "case_statement":
            continue
        statements = case_statements(case)
        if statements:
            entries.append((header(case, statements[0]), case, statements))
    return entries


def case_statements(case: Node) -> list[Node]:
    colon = next((i for i, c in enumerate(case.children) if c.type == ":"), None)
    if colon is None:
        return []
    return [c for c in case.children[colon + 1 :] if c.is_named]


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
    return child if child is not None and child.type == "compound_statement" else None


def child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += count_named_nodes(child)
    return count
