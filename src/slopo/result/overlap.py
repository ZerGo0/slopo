from slopo.result.models import Cluster, SimilarPair, UnitRecord


def exclude_overlapping_pairs(
    pairs: list[SimilarPair], units: dict[int, UnitRecord]
) -> list[SimilarPair]:
    return [p for p in pairs if not _overlaps(units[p.unit_id_a], units[p.unit_id_b])]


def exclude_overlapping_cluster_units(
    clusters: list[Cluster], units: dict[int, UnitRecord]
) -> list[Cluster]:
    result: list[Cluster] = []
    for cluster in clusters:
        kept: list[int] = []
        for uid in cluster.unit_ids:
            if not any(_overlaps(units[uid], units[other]) for other in kept):
                kept.append(uid)
        result.append(cluster._replace(unit_ids=kept))
    return result


def _overlaps(a: UnitRecord, b: UnitRecord) -> bool:
    if a.file_path != b.file_path:
        return False
    return _contains(a, b) or _contains(b, a)


def _contains(outer: UnitRecord, inner: UnitRecord) -> bool:
    return outer.start_line <= inner.start_line and inner.end_line <= outer.end_line
