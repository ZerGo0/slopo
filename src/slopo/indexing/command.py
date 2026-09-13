import sqlite3

from slopo.config import Config
from slopo.indexing.scanner import NodeCountThresholds
from slopo.indexing.sync import sync_index
from slopo.progress import ProgressReporter


def run_index(
    conn: sqlite3.Connection,
    cfg: Config,
    log: ProgressReporter,
) -> None:
    log("Indexing code...")

    thresholds = NodeCountThresholds(
        function=cfg.body_node_count_threshold,
        block=cfg.block_node_count_threshold,
    )

    with conn:
        stats = sync_index(conn, cfg.source_dir, thresholds, cfg.source_dir_exclude)

    log(
        f"Indexed {stats.indexed_units} code units from {stats.indexed_files} files"
        f" ({stats.skipped_files} unchanged, {stats.removed_files} removed)."
    )
