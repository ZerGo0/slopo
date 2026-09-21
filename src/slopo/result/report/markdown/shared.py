from pathlib import Path

from slopo.result.models import Cluster, UnitRecord

LANG_MAP = {
    ".cs": "csharp",
    ".ex": "elixir",
    ".go": "go",
    ".java": "java",
    ".js": "javascript",
    ".kt": "kotlin",
    ".php": "php",
    ".py": "python",
    ".rs": "rust",
    ".ts": "typescript",
}


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        if rows
        else len(headers[col])
        for col in range(len(headers))
    ]

    def render(cells: list[str]) -> str:
        padded = [cells[col].ljust(widths[col]) for col in range(len(cells))]
        return "| " + " | ".join(padded) + " |"

    separator = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    lines = [render(headers), separator]
    lines.extend(render(row) for row in rows)
    return "\n".join(lines) + "\n"


def similarity_range(cluster: Cluster) -> str:
    low = f"{cluster.min_similarity:.2f}"
    high = f"{cluster.max_similarity:.2f}"
    return low if low == high else f"{low}-{high}"


def lang_tag(file_path: str, language: str | None = None) -> str:
    return language or LANG_MAP.get(Path(file_path).suffix, "")


def group_by_body_hash(
    unit_ids: list[int], units: dict[int, UnitRecord]
) -> list[list[UnitRecord]]:
    groups: dict[tuple[str, str], list[UnitRecord]] = {}
    order: list[tuple[str, str]] = []
    for uid in unit_ids:
        unit = units[uid]
        key = (unit.body_hash, lang_tag(unit.file_path, unit.language))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(unit)
    return [groups[key] for key in order]


def group_by_context(units: list[UnitRecord]) -> list[list[UnitRecord]]:
    groups: dict[str | None, list[UnitRecord]] = {}
    order: list[str | None] = []
    for unit in units:
        if unit.context not in groups:
            groups[unit.context] = []
            order.append(unit.context)
        groups[unit.context].append(unit)
    return [groups[context] for context in order]
