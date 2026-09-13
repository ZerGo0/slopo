from typing import Callable

from tree_sitter import Node, Parser


def strip_comments(
    source: bytes,
    parser: Parser,
    should_strip: Callable[[Node], bool],
) -> bytes:
    root = parser.parse(source).root_node
    spans: list[tuple[int, int]] = []
    _collect_spans(root, should_strip, spans)
    buffer = bytearray(source)

    for start, end in spans:
        for i in range(start, end):
            if buffer[i] != ord("\n"):
                buffer[i] = ord(" ")

    lines = bytes(buffer).split(b"\n")
    tidied = [line.rstrip(b" \t") for line in lines]

    return b"\n".join(tidied)


def _collect_spans(
    node: Node,
    should_strip: Callable[[Node], bool],
    spans: list[tuple[int, int]],
) -> None:
    if should_strip(node):
        spans.append((node.start_byte, node.end_byte))
        return
    for child in node.children:
        _collect_spans(child, should_strip, spans)
