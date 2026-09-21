import tree_sitter_elixir
from tree_sitter import Language, Node, Parser

from slopo.indexing.parsing.base import CodeUnit, hash_body, normalize_indents, to_utf8
from slopo.indexing.parsing.comments import strip_comments

_LANGUAGE = Language(tree_sitter_elixir.language())
_PARSER = Parser(_LANGUAGE)

_COMMENT_TYPES = {"comment"}

_DEFINERS = {"def", "defp"}

_DO_BODY_BLOCKS = {"if", "unless", "for", "with"}

_STAB_CLAUSE_BLOCKS = {"case", "cond", "receive"}

_STRUCTURAL_CHILDREN = {
    "do",
    "end",
    "else_block",
    "rescue_block",
    "catch_block",
    "after_block",
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
    if _definer(node) is not None:
        unit = _named_function_unit(node, source)
        if unit is not None:
            units.append(unit)
    elif node.type == "anonymous_function":
        unit = _anonymous_function_unit(node, source)
        if unit is not None:
            units.append(unit)
    for context, start, body_nodes in _block_entries(node):
        units.append(_block_unit(context, start, body_nodes, source))
    for child in node.children:
        _collect_units(child, source, units)


def _named_function_unit(node: Node, source: bytes) -> CodeUnit | None:
    do_block = _child_of_type(node, "do_block")
    if do_block is not None:
        body = source[do_block.start_byte : do_block.end_byte].decode()
        context = _header(node, do_block)
        return _make_function_unit(node, do_block, body, context)
    keyword_body = _keyword_do_body(node)
    if keyword_body is not None:
        body = source[keyword_body.start_byte : keyword_body.end_byte].decode()
        context = _header(node, keyword_body)
        return _make_function_unit(node, keyword_body, body, context)
    return None


def _anonymous_function_unit(node: Node, source: bytes) -> CodeUnit | None:
    bodies = _stab_bodies(node)
    if not bodies:
        return None
    body = source[bodies[0].start_byte : bodies[-1].end_byte].decode()
    context = _anon_context(node, bodies[0], source)
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=sum(_count_named_nodes(b) for b in bodies),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _anon_context(node: Node, first_body: Node, source: bytes) -> str | None:
    binding = _binding_node(node)
    if binding is not None:
        return source[binding.start_byte : first_body.start_byte].decode().strip()
    parent = node.parent
    if parent is not None and parent.type == "arguments":
        call = parent.parent
        if call is not None and call.type == "call":
            target = call.child_by_field_name("target")
            if target is not None and target.text:
                return f"{target.text.decode()} fn"
    return source[node.start_byte : first_body.start_byte].decode().strip() or None


def _binding_node(node: Node) -> Node | None:
    parent = node.parent
    if parent is None or parent.type != "binary_operator":
        return None
    operator = parent.children[1] if len(parent.children) > 1 else None
    if operator is not None and operator.type == "=":
        return parent
    return None


def _make_function_unit(
    node: Node, body_node: Node, body: str, context: str | None
) -> CodeUnit:
    return CodeUnit(
        body=body,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        body_node_count=_count_named_nodes(body_node),
        body_hash=hash_body(body),
        kind="function",
        context=context,
    )


def _block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    target = _call_target(node)
    if target is None:
        return []
    if target in _DO_BODY_BLOCKS:
        return _do_body_entries(node, target)
    if target in _STAB_CLAUSE_BLOCKS:
        return _stab_block_entries(node)
    if target == "try":
        return _try_entries(node)
    return []


def _do_body_entries(node: Node, target: str) -> list[tuple[str, Node, list[Node]]]:
    do_block = _child_of_type(node, "do_block")
    if do_block is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    body_nodes = _do_block_body_nodes(do_block)
    if body_nodes:
        context = _header(node, body_nodes[0])
        entries.append((context, node, body_nodes))
    if target in {"if", "with"}:
        else_block = _child_of_type(do_block, "else_block")
        if else_block is not None:
            if target == "if":
                else_bodies = _else_block_body_nodes(else_block)
                if else_bodies:
                    entries.append(("else", else_block, else_bodies))
            else:
                entries.extend(_stab_entries_from(else_block))
    return entries


def _stab_block_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    do_block = _child_of_type(node, "do_block")
    if do_block is None:
        return []
    entries = _stab_entries_from(do_block)
    after_block = _child_of_type(do_block, "after_block")
    if after_block is not None:
        entries.extend(_stab_entries_from(after_block))
    return entries


def _try_entries(node: Node) -> list[tuple[str, Node, list[Node]]]:
    do_block = _child_of_type(node, "do_block")
    if do_block is None:
        return []
    entries: list[tuple[str, Node, list[Node]]] = []
    body_nodes = _do_block_body_nodes(do_block)
    if body_nodes:
        context = _header(node, body_nodes[0])
        entries.append((context, node, body_nodes))
    for child in do_block.children:
        if child.type in {"rescue_block", "catch_block"}:
            entries.extend(_stab_entries_from(child))
        elif child.type == "after_block":
            after_bodies = _after_block_body_nodes(child)
            if after_bodies:
                entries.append(("after", child, after_bodies))
    return entries


def _stab_entries_from(
    container: Node,
) -> list[tuple[str, Node, list[Node]]]:
    entries: list[tuple[str, Node, list[Node]]] = []
    for child in container.children:
        if child.type != "stab_clause":
            continue
        statements = _stab_clause_statements(child)
        if not statements:
            continue
        context = _header(child, statements[0])
        entries.append((context, child, statements))
    return entries


def _stab_clause_statements(clause: Node) -> list[Node]:
    body = next((c for c in clause.children if c.type == "body"), None)
    if body is None:
        return []
    return [c for c in body.children if c.is_named]


def _do_block_body_nodes(do_block: Node) -> list[Node]:
    return [
        c
        for c in do_block.children
        if c.is_named and c.type not in _STRUCTURAL_CHILDREN
    ]


def _else_block_body_nodes(else_block: Node) -> list[Node]:
    return [c for c in else_block.children if c.is_named and c.type not in {"else"}]


def _after_block_body_nodes(after_block: Node) -> list[Node]:
    return [c for c in after_block.children if c.is_named and c.type not in {"after"}]


def _header(node: Node, body: Node) -> str:
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


def _definer(node: Node) -> str | None:
    if node.type != "call" or not node.children:
        return None
    head = node.children[0]
    if head.type != "identifier" or head.text is None:
        return None
    name = head.text.decode()
    return name if name in _DEFINERS else None


def _call_target(node: Node) -> str | None:
    if node.type != "call":
        return None
    target = node.child_by_field_name("target")
    if target is not None and target.type == "identifier" and target.text:
        return target.text.decode()
    return None


def _signature_node(node: Node) -> Node | None:
    args = next((c for c in node.children if c.type == "arguments"), None)
    if args is None or not args.named_children:
        return None
    head = args.named_children[0]
    if head.type == "binary_operator":
        head = head.children[0] if head.children else head
    return head


def _keyword_do_body(unit: Node) -> Node | None:
    args = next((c for c in unit.children if c.type == "arguments"), None)
    if args is None:
        return None
    keywords = next((c for c in args.named_children if c.type == "keywords"), None)
    if keywords is None:
        return None
    for pair in keywords.named_children:
        key = pair.child_by_field_name("key")
        if (
            key is not None
            and key.text is not None
            and key.text.decode().strip() == "do:"
        ):
            return pair.child_by_field_name("value")
    return None


def _stab_bodies(node: Node) -> list[Node]:
    return [
        body
        for clause in node.children
        if clause.type == "stab_clause"
        for body in clause.children
        if body.type == "body"
    ]


def _child_of_type(node: Node, type_: str) -> Node | None:
    return next((c for c in node.children if c.type == type_), None)


def _count_named_nodes(node: Node) -> int:
    count = 1 if node.is_named else 0
    for child in node.children:
        count += _count_named_nodes(child)
    return count
