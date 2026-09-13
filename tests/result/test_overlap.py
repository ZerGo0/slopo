from slopo.result.models import Cluster, SimilarPair, UnitRecord
from slopo.result.overlap import (
    exclude_overlapping_cluster_units,
    exclude_overlapping_pairs,
)


def _unit(unit_id: int, file_path: str, start: int, end: int) -> UnitRecord:
    return UnitRecord(
        unit_id=unit_id,
        file_path=file_path,
        context=f"unit{unit_id}",
        start_line=start,
        end_line=end,
        body="",
        body_hash="",
    )


# --- exclude_overlapping_pairs ---


def test_drops_pair_where_one_unit_is_nested_in_the_other():
    units = {
        1: _unit(1, "a.js", 1, 10),
        2: _unit(2, "a.js", 3, 6),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == []


def test_containment_detected_regardless_of_pair_order():
    units = {
        1: _unit(1, "a.js", 3, 6),
        2: _unit(2, "a.js", 1, 10),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == []


def test_keeps_pair_of_disjoint_units_in_same_file():
    units = {
        1: _unit(1, "a.js", 1, 5),
        2: _unit(2, "a.js", 7, 12),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == pairs


def test_keeps_pair_with_same_line_span_in_different_files():
    units = {
        1: _unit(1, "a.js", 1, 10),
        2: _unit(2, "b.js", 3, 6),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == pairs


def test_keeps_pair_of_units_sharing_one_boundary_line():
    units = {
        1: _unit(1, "a.js", 1, 10),
        2: _unit(2, "a.js", 10, 15),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == pairs


def test_keeps_overlapping_units_that_do_not_contain_each_other():
    units = {
        1: _unit(1, "a.js", 1, 6),
        2: _unit(2, "a.js", 4, 10),
    }
    pairs = [SimilarPair(similarity=0.99, unit_id_a=1, unit_id_b=2)]
    assert exclude_overlapping_pairs(pairs, units) == pairs


# --- exclude_overlapping_cluster_units ---


def test_keeps_first_unit_when_they_overlap():
    units = {
        1: _unit(1, "a.java", 1, 30),
        2: _unit(2, "a.java", 5, 25),
        3: _unit(3, "a.java", 10, 20),
        4: _unit(4, "b.java", 1, 30),
        5: _unit(5, "b.java", 5, 25),
        6: _unit(6, "c.java", 3, 7),
    }
    cluster = Cluster([2, 6, 4, 1, 3, 5], 0.8, 0.99)

    result = exclude_overlapping_cluster_units([cluster], units)

    assert result == [Cluster([2, 6, 4], 0.8, 0.99)]


def test_keeps_cluster_units_sharing_one_boundary_line():
    units = {
        1: _unit(1, "a.java", 1, 10),
        2: _unit(2, "a.java", 10, 20),
    }
    clusters = [Cluster([1, 2], 0.8, 0.99)]

    assert exclude_overlapping_cluster_units(clusters, units) == clusters


def test_keeps_non_overlapping_units():
    units = {
        1: _unit(1, "a.java", 1, 10),
        2: _unit(2, "a.java", 12, 20),
        3: _unit(3, "b.java", 1, 10),
    }
    clusters = [Cluster([1, 2, 3], 0.8, 0.99)]

    assert exclude_overlapping_cluster_units(clusters, units) == clusters
