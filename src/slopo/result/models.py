from typing import NamedTuple


class Cluster(NamedTuple):
    unit_ids: list[int]
    min_similarity: float
    max_similarity: float


class HashedCluster(NamedTuple):
    cluster: Cluster
    hash: str


class SimilarPair(NamedTuple):
    similarity: float
    unit_id_a: int
    unit_id_b: int


class UnitRecord(NamedTuple):
    unit_id: int
    file_path: str
    context: str | None
    start_line: int
    end_line: int
    body: str
    body_hash: str
    language: str | None = None


class ReviewResult(NamedTuple):
    clusters: list[HashedCluster]
    units: dict[int, UnitRecord]
    changed_ids: set[int]


class AnalyzeResult(NamedTuple):
    clusters: list[HashedCluster]
    units: dict[int, UnitRecord]
