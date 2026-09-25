from pathlib import Path

from slopo.indexing.parsing.lang import (
    c,
    cpp,
    javascript,
    csharp,
    elixir,
    rust,
    swift,
    go,
    php,
    python,
    ruby,
    svelte,
    typescript,
    tsx,
    kotlin,
    java,
)
from slopo.indexing.parsing.base import CodeParser

_REGISTRY: dict[str, CodeParser] = {
    ".c": c.parse,
    ".cc": cpp.parse,
    ".cpp": cpp.parse,
    ".cs": csharp.parse,
    ".cxx": cpp.parse,
    ".h": cpp.parse,
    ".hh": cpp.parse,
    ".hpp": cpp.parse,
    ".hxx": cpp.parse,
    ".ex": elixir.parse,
    ".go": go.parse,
    ".java": java.parse,
    ".js": javascript.parse,
    ".kt": kotlin.parse,
    ".php": php.parse,
    ".py": python.parse,
    ".rb": ruby.parse,
    ".rs": rust.parse,
    ".svelte": svelte.parse,
    ".swift": swift.parse,
    ".ts": typescript.parse,
    ".tsx": tsx.parse,
}


def get_parser(path: Path) -> CodeParser:
    suffix = path.suffix.lower()
    parser = _REGISTRY.get(suffix)
    if parser is None:
        raise ValueError(f"No parser registered for '{suffix}' files")
    return parser


def supported_extensions() -> set[str]:
    return set(_REGISTRY)
