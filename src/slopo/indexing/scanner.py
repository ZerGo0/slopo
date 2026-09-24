import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from slopo.indexing.parsing.base import CodeUnit
from slopo.indexing.parsing.registry import get_parser
from slopo.indexing.scan_filter import ScanFilter

logger = logging.getLogger(__name__)

_MAX_BODY_CHARS = 10_000


@dataclass(frozen=True)
class NodeCountThresholds:
    function: int
    block: int


def scan_directory(root: Path, scan_filter: ScanFilter) -> Iterator[str]:
    for relative_file in walk_files(root, scan_filter):
        if (
            scan_filter.should_keep_file(relative_file)
            and (root / relative_file).is_file()
        ):
            # Normalize to forward slashes so relative paths have consistent format
            # in generated reports and cluster hashes used in the ignore file.
            yield relative_file.as_posix()


def walk_files(root: Path, scan_filter: ScanFilter) -> Iterator[Path]:
    for current, directories, files in os.walk(root):
        relative_dir = Path(current).relative_to(root)
        directories[:] = [
            directory
            for directory in directories
            if scan_filter.should_enter_dir(relative_dir / directory)
        ]
        for file in files:
            yield relative_dir / file


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
