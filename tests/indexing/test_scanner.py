import logging
from pathlib import Path

from slopo.indexing.scan_filter import ScanFilter
from slopo.indexing.scanner import (
    NodeCountThresholds,
    filter_units,
    parse_file,
    scan_directory,
    walk_files,
)

_JAVA = """\
class Calculator {
    int increment(int a) {
        return a + 1;
    }
}
"""

_KOTLIN = """\
fun increment(a: Int): Int {
    return b + 2
}
"""

_JAVA_WITH_BLOCK = """\
class Sample {
    void run(int[] xs) {
        for (int x : xs) {
            total += x;
            record(x);
            log(x);
        }
    }
}
"""


# --- scan_directory ---


def test_returns_kept_files_as_paths_relative_to_root(tmp_path: Path):
    (tmp_path / "sub" / "nested").mkdir(parents=True)
    (tmp_path / "sub" / "nested" / "Deep.kt").write_text(_KOTLIN)
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "Generated.kt").write_text(_KOTLIN)
    (tmp_path / "Increment.kt").write_text(_KOTLIN)
    (tmp_path / "notes.txt").write_text("not code")

    scan_filter = ScanFilter.create(exclude=["build/"], include_extensions=[])

    scanned = set(scan_directory(tmp_path, scan_filter))

    assert scanned == {"sub/nested/Deep.kt", "Increment.kt"}


def test_skips_file_reincluded_under_excluded_directory(tmp_path: Path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "Generated.kt").write_text(_KOTLIN)

    scan_filter = ScanFilter.create(
        exclude=["build/", "!build/Generated.kt"], include_extensions=[]
    )

    scanned = set(scan_directory(tmp_path, scan_filter))

    assert scanned == set()


# --- walk_files ---


def test_walks_all_files_in_nested_directories(tmp_path: Path):
    (tmp_path / "a" / "b" / "c").mkdir(parents=True)
    (tmp_path / "a" / "A.kt").write_text(_KOTLIN)
    (tmp_path / "a" / "b" / "c" / "Deep.kt").write_text(_KOTLIN)
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "notes.txt").write_text("not code")
    (tmp_path / "Root.kt").write_text(_KOTLIN)

    scan_filter = ScanFilter.create(exclude=[], include_extensions=[])

    walked = set(walk_files(tmp_path, scan_filter))

    assert walked == {
        Path("a/A.kt"),
        Path("a/b/c/Deep.kt"),
        Path("x/notes.txt"),
        Path("Root.kt"),
    }


def test_skips_files_under_excluded_directory(tmp_path: Path):
    (tmp_path / "build" / "nested").mkdir(parents=True)
    (tmp_path / "build" / "Generated.kt").write_text(_KOTLIN)
    (tmp_path / "build" / "nested" / "Generated.kt").write_text(_KOTLIN)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Increment.kt").write_text(_KOTLIN)

    scan_filter = ScanFilter.create(exclude=["build/"], include_extensions=[])

    walked = list(walk_files(tmp_path, scan_filter))

    assert walked == [Path("src/Increment.kt")]


# --- parse_file ---


def test_parses_units_from_relevant_languages(tmp_path: Path):
    (tmp_path / "Calculator.java").write_text(_JAVA)
    (tmp_path / "Increment.kt").write_text(_KOTLIN)

    java_unit = parse_file(tmp_path / "Calculator.java")[0]
    kotlin_unit = parse_file(tmp_path / "Increment.kt")[0]

    assert java_unit.body == "{\n    return a + 1;\n}"
    assert kotlin_unit.body == "{\n    return b + 2\n}"


def test_normalizes_crlf_line_endings_to_lf(tmp_path: Path):
    kotlin = tmp_path / "Increment.kt"
    kotlin.write_bytes(b"fun increment(a: Int): Int {\r\n    return b + 2\r\n}\r\n")

    unit = parse_file(kotlin)[0]

    assert unit.body == "{\n    return b + 2\n}"


def test_normalizes_cr_line_endings_to_lf(tmp_path: Path):
    kotlin = tmp_path / "Increment.kt"
    kotlin.write_bytes(b"fun increment(a: Int): Int {\r    return b + 2\r}\r")

    unit = parse_file(kotlin)[0]

    assert unit.body == "{\n    return b + 2\n}"


def test_skips_file_on_read_error(tmp_path: Path, caplog):
    vanished = tmp_path / "Increment.kt"
    vanished.write_text(_KOTLIN)
    vanished.unlink()

    with caplog.at_level(logging.WARNING):
        units = parse_file(vanished)

    assert units == []
    assert f"Skipping {vanished}:" in caplog.text


# --- filter_units ---


def test_excludes_units_below_body_node_count_threshold(tmp_path: Path):
    (tmp_path / "Calculator.java").write_text(_JAVA)
    units = parse_file(tmp_path / "Calculator.java")

    filtered = filter_units(units, NodeCountThresholds(function=1000, block=1000))

    assert filtered == []


def test_excludes_units_exceeding_max_body_chars(tmp_path: Path):
    big_body = "\n".join(f"int example{i} = {i};" for i in range(600))
    assert len(big_body) == 12979
    source = (
        "class Big {\n"
        "    void huge() {\n"
        f"{big_body}\n"
        "    }\n"
        "    int small(int a) {\n"
        "        return a + 1;\n"
        "    }\n"
        "}\n"
    )
    (tmp_path / "Big.java").write_text(source)
    units = parse_file(tmp_path / "Big.java")

    filtered = filter_units(units, NodeCountThresholds(function=0, block=0))

    assert [u.body for u in filtered] == ["{\n    return a + 1;\n}"]


def test_function_threshold_applies_to_functions_not_blocks(tmp_path: Path):
    (tmp_path / "Sample.java").write_text(_JAVA_WITH_BLOCK)
    units = parse_file(tmp_path / "Sample.java")

    filtered = filter_units(units, NodeCountThresholds(function=0, block=1000))

    assert {u.kind for u in filtered} == {"function"}


def test_block_threshold_applies_to_blocks_not_functions(tmp_path: Path):
    (tmp_path / "Sample.java").write_text(_JAVA_WITH_BLOCK)
    units = parse_file(tmp_path / "Sample.java")

    filtered = filter_units(units, NodeCountThresholds(function=1000, block=0))

    assert {u.kind for u in filtered} == {"block"}
