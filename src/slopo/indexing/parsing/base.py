import hashlib
import inspect
from dataclasses import dataclass
from typing import Callable, Literal

UnitKind = Literal["function", "block"]


@dataclass
class CodeUnit:
    name: str  # Deprecated
    body: str
    start_line: int
    end_line: int
    body_node_count: int
    body_hash: str
    kind: UnitKind
    context: str | None = None


CodeParser = Callable[[bytes], list[CodeUnit]]


def to_utf8(source: bytes) -> bytes:
    # tree-sitter accepts arbitrary bytes, but unit extraction decodes byte slices as UTF-8.
    # Normalize here so a stray non-UTF-8 byte can't abort parsing.
    return source.decode("utf-8", errors="replace").encode("utf-8")


def hash_body(body: str) -> str:
    normalized = " ".join(body.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_indents(units: list[CodeUnit]) -> None:
    for unit in units:
        unit.body = inspect.cleandoc(unit.body)
        if unit.context is not None:
            unit.context = inspect.cleandoc(unit.context)
