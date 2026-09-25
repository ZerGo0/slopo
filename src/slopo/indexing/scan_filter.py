from dataclasses import dataclass
from pathlib import Path

from pathspec import GitIgnoreSpec

from slopo.indexing.parsing.registry import supported_extensions


@dataclass(frozen=True)
class ScanFilter:
    exclude_files: GitIgnoreSpec
    exclude_dirs: GitIgnoreSpec
    extensions: frozenset[str]

    @classmethod
    def create(cls, exclude: list[str], include_extensions: list[str]) -> "ScanFilter":
        return cls(
            exclude_files=GitIgnoreSpec.from_lines(exclude),
            exclude_dirs=GitIgnoreSpec.from_lines(
                [_as_dir_pattern(pattern) for pattern in exclude]
            ),
            extensions=frozenset(include_extensions or supported_extensions()),
        )

    def should_enter_dir(self, relative_dir: Path) -> bool:
        return not self.exclude_dirs.match_file(relative_dir)

    def should_keep_file(self, relative_file: Path) -> bool:
        suffix = relative_file.suffix.lower()
        return suffix in self.extensions and not self.exclude_files.match_file(
            relative_file
        )


def _as_dir_pattern(pattern: str) -> str:
    if pattern.endswith("/") and len(pattern.lstrip("!")) > 1:
        return pattern[:-1]
    return pattern
