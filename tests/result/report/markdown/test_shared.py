from slopo.result.models import UnitRecord
from slopo.result.report.markdown.shared import (
    group_by_body_hash,
    group_by_context,
    lang_tag,
)


def _unit(
    unit_id: int,
    body_hash: str,
    line: int = 1,
    context: str | None = None,
) -> UnitRecord:
    return UnitRecord(
        unit_id=unit_id,
        file_path=f"src/file{unit_id}.py",
        context=context,
        start_line=line,
        end_line=line + 1,
        body="body",
        body_hash=body_hash,
    )


# --- group_by_body_hash ---


def test_groups_units_sharing_a_body_hash():
    units = {
        1: _unit(1, "a"),
        2: _unit(2, "b"),
        3: _unit(3, "a"),
    }

    groups = group_by_body_hash([1, 2, 3], units)

    assert groups == [
        [units[1], units[3]],
        [units[2]],
    ]


def test_preserves_first_appearance_order_within_and_between_groups():
    units = {
        1: _unit(1, "a"),
        2: _unit(2, "a"),
        3: _unit(3, "b"),
    }

    groups = group_by_body_hash([2, 1, 3], units)

    assert groups == [
        [units[2], units[1]],
        [units[3]],
    ]


def test_collapses_exact_copies_into_one_group():
    units = {
        1: _unit(1, "a"),
        2: _unit(2, "a"),
    }

    groups = group_by_body_hash([1, 2], units)

    assert groups == [
        [units[1], units[2]],
    ]


def test_keeps_distinct_units_in_separate_groups():
    units = {
        1: _unit(1, "a"),
        2: _unit(2, "b"),
    }

    groups = group_by_body_hash([1, 2], units)

    assert groups == [
        [units[1]],
        [units[2]],
    ]


# --- group_by_context ---


def test_groups_units_sharing_a_context():
    first = _unit(1, "a", context="shared")
    different = _unit(2, "a", context="different")
    second = _unit(3, "a", context="shared")

    groups = group_by_context([first, different, second])

    assert groups == [
        [first, second],
        [different],
    ]


def test_groups_all_units_when_context_is_the_same():
    first = _unit(1, "a", context="shared")
    second = _unit(2, "a", context="shared")

    assert group_by_context([first, second]) == [
        [first, second],
    ]


def test_treats_missing_context_as_a_grouping_value():
    first_missing = _unit(1, "a", context=None)
    present = _unit(2, "a", context="present")
    second_missing = _unit(3, "a", context=None)

    assert group_by_context([first_missing, present, second_missing]) == [
        [first_missing, second_missing],
        [present],
    ]


def test_uses_embedded_language_for_svelte_script():
    assert lang_tag("src/components/Counter.svelte", "typescript") == "typescript"
    assert lang_tag("src/components/Counter.svelte", "javascript") == "javascript"


def test_separates_exact_copies_with_different_code_languages():
    typescript_unit = _unit(1, "same")._replace(
        file_path="src/Counter.svelte", language="typescript"
    )
    javascript_unit = _unit(2, "same")._replace(
        file_path="src/Counter.svelte", language="javascript"
    )

    assert group_by_body_hash([1, 2], {1: typescript_unit, 2: javascript_unit}) == [
        [typescript_unit],
        [javascript_unit],
    ]
