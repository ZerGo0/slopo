from datetime import datetime

from slopo.result.models import Cluster, UnitRecord
from slopo.result.report.naming import cluster_filename
from slopo.result.report.markdown.shared import (
    format_table,
    group_by_body_hash,
    group_by_context,
    lang_tag,
    similarity_range,
)


def build_index_review(
    clusters: list[Cluster],
    units: dict[int, UnitRecord],
    generated_at: datetime,
) -> str:
    total = len(clusters)
    headers = ["Cluster", "Score", "Code units", "Unique files"]
    rows: list[list[str]] = []
    for i, cluster in enumerate(clusters, 1):
        link = f"[Cluster {i}]({cluster_filename(i, total)})"
        records = [units[uid] for uid in cluster.unit_ids]
        unit_count = len(records)
        unique_files = len({record.file_path for record in records})
        rows.append(
            [
                link,
                similarity_range(cluster),
                str(unit_count),
                str(unique_files),
            ]
        )
    timestamp = generated_at.strftime("%Y-%m-%d %H:%M:%S")
    return f"Generated {timestamp}\n\n{format_table(headers, rows)}"


def build_cluster_review(
    number: int,
    cluster: Cluster,
    units: dict[int, UnitRecord],
    changed_ids: set[int],
) -> str:
    parts: list[str] = [
        f"## ({number}) score {similarity_range(cluster)}",
    ]
    for group_number, group in enumerate(
        group_by_body_hash(cluster.unit_ids, units), 1
    ):
        parts.append(f"### ______ {group_number} ______")
        lang = lang_tag(group[0].file_path)
        records = sorted(group, key=lambda record: record.file_path)
        for context_group in group_by_context(records):
            for record in context_group:
                marker = "**CHANGED** " if record.unit_id in changed_ids else ""
                parts.append(
                    f"- {marker}`{record.file_path}` lines "
                    f"{record.start_line}-{record.end_line}"
                )
            context = context_group[0].context
            if context is not None:
                parts.append(f"```{lang}\n{context}\n```")
        parts.append(f"```{lang}\n{group[0].body}\n```")
    return "\n\n".join(parts) + "\n"
