import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from pathspec import PathSpec

from slopo.indexing.parsing.base import CodeUnit
from slopo.indexing.parsing.registry import get_parser, supported_extensions

logger = logging.getLogger(__name__)

_MAX_BODY_CHARS = 10_000


@dataclass(frozen=True)
class NodeCountThresholds:
    function: int
    block: int


def scan_directory(root: Path, exclude: list[str]) -> Iterator[str]:
    extensions = supported_extensions()
    spec = PathSpec.from_lines("gitignore", exclude)
    has_negated_patterns = any(pattern.include is False for pattern in spec.patterns)

    for current_root, directories, files in os.walk(root):
        current_path = Path(current_root)
        relative_root = current_path.relative_to(root)

        if not has_negated_patterns:
            directories[:] = [
                directory
                for directory in directories
                if not spec.match_file(f"{(relative_root / directory).as_posix()}/")
            ]

        for file in files:
            path = current_path / file
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            relative = path.relative_to(root)
            if not spec.match_file(relative):
                # Normalize to forward slashes so relative paths have consistent format
                # in generated reports and cluster hashes used in the ignore file.
                yield relative.as_posix()


def parse_file(path: Path) -> list[CodeUnit]:
    parser = get_parser(path)
    try:
        source = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return parser(source)
    except Exception as e:
        logger.warning("Skipping %s: %s", path, e)
        return []


def filter_units(
    units: list[CodeUnit], thresholds: NodeCountThresholds
) -> list[CodeUnit]:
    return [
        u
        for u in units
        if u.body_node_count >= _threshold_for(u, thresholds)
        and len(u.body) <= _MAX_BODY_CHARS
    ]


def _threshold_for(unit: CodeUnit, thresholds: NodeCountThresholds) -> int:
    return thresholds.block if unit.kind == "block" else thresholds.function
