import sqlite3

from slopo.result.clustering import (
    build_clusters,
    filter_clusters,
    reorder_clusters,
)
from slopo.result.analysis.ignore import ensure_ignore_file, load_ignored
from slopo.result.identity import to_hashed_cluster
from slopo.result.rerank import rerank_all_clusters
from slopo.result.analysis.similarity import find_similar_pairs
from slopo.result.db import load_duplicate_hashes, load_units
from slopo.result.models import AnalyzeResult, HashedCluster, UnitRecord
from slopo.result.overlap import (
    exclude_overlapping_cluster_units,
    exclude_overlapping_pairs,
)
from slopo.config import Config
from slopo.embedding.db import load_embeddings
from slopo.progress import ProgressReporter

# Rows of the similarity matrix computed per iteration. Caps the size of
# the intermediate (block_size, n) product so it doesn't blow up at large n.
_BLOCK_SIZE = 1000


def run_analyze(
    conn: sqlite3.Connection,
    cfg: Config,
    log: ProgressReporter,
) -> AnalyzeResult | None:
    embeddings = load_embeddings(conn)

    log("Calculating similarity...")
    pairs = find_similar_pairs(
        embeddings, cfg.analyze_similarity_threshold, _BLOCK_SIZE
    )

    if not pairs:
        log("No similar code found.")
        return None

    referenced_ids = {uid for p in pairs for uid in (p.unit_id_a, p.unit_id_b)}
    units = load_units(conn, referenced_ids)
    pairs = exclude_overlapping_pairs(pairs, units)

    if not pairs:
        log("No similar code found.")
        return None

    log("Clustering and ranking...")
    clusters = build_clusters(pairs)
    clusters = exclude_overlapping_cluster_units(clusters, units)

    reranked_pairs = rerank_all_clusters(clusters, pairs, units)
    clusters = reorder_clusters(clusters, reranked_pairs)
    clusters = filter_clusters(clusters, cfg.analyze_rerank_threshold)

    if not clusters:
        log("No similar code found.")
        return None

    hashed = to_hashed_cluster(clusters, units)

    ensure_ignore_file(cfg.ignore_file)

    ignored = load_ignored(cfg.ignore_file)
    if ignored:
        kept = [hc for hc in hashed if hc.hash not in ignored]
        ignored_count = len(hashed) - len(kept)
        hashed = kept
        if ignored_count:
            log(f"Ignored {ignored_count} previously reviewed clusters.")

    if not hashed:
        log("All similar code clusters are in the ignore list.")
        return None

    _report_summary(conn, hashed, units, log)

    return AnalyzeResult(hashed, units)


def _report_summary(
    conn: sqlite3.Connection,
    clusters: list[HashedCluster],
    units: dict[int, UnitRecord],
    log: ProgressReporter,
) -> None:
    duplicate_hashes = load_duplicate_hashes(conn)
    unique_units = {uid for hc in clusters for uid in hc.cluster.unit_ids}
    exact_copies = sum(
        1 for uid in unique_units if units[uid].body_hash in duplicate_hashes
    )

    log(
        f"{len(clusters)} clusters with {len(unique_units)} units"
        f" including {exact_copies} exact copies."
    )
