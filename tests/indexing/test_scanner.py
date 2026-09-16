import logging
import os
from pathlib import Path

from slopo.indexing.scanner import (
    NodeCountThresholds,
    filter_units,
    parse_file,
    scan_directory,
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


def test_scans_all_supported_languages(tmp_path: Path):
    (tmp_path / "Calculator.java").write_text(_JAVA)
    (tmp_path / "Increment.kt").write_text(_KOTLIN)

    scanned = set(scan_directory(tmp_path, exclude=[]))

    assert scanned == {"Calculator.java", "Increment.kt"}


def test_recurses_into_subdirectories_with_paths_relative_to_root(tmp_path: Path):
    (tmp_path / "sub" / "nested").mkdir(parents=True)
    (tmp_path / "sub" / "nested" / "Increment.kt").write_text(_KOTLIN)

    scanned = list(scan_directory(tmp_path, exclude=[]))

    assert scanned == ["sub/nested/Increment.kt"]


def test_ignores_unsupported_file_types(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("not code")
    (tmp_path / "data.json").write_text("{}")

    assert list(scan_directory(tmp_path, exclude=[])) == []


def test_skips_files_under_excluded_directory(tmp_path: Path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "Generated.kt").write_text(_KOTLIN)
    (tmp_path / "Increment.kt").write_text(_KOTLIN)

    scanned = list(scan_directory(tmp_path, exclude=["build/"]))

    assert scanned == ["Increment.kt"]


def test_does_not_traverse_excluded_directory(tmp_path: Path, monkeypatch):
    (tmp_path / "build" / "nested").mkdir(parents=True)
    (tmp_path / "build" / "nested" / "Generated.kt").write_text(_KOTLIN)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Increment.kt").write_text(_KOTLIN)

    visited: list[str] = []
    real_walk = os.walk

    def tracking_walk(root):
        for directory, directories, files in real_walk(root):
            visited.append(Path(directory).relative_to(tmp_path).as_posix())
            yield directory, directories, files

    monkeypatch.setattr("slopo.indexing.scanner.os.walk", tracking_walk)

    scanned = list(scan_directory(tmp_path, exclude=["build/"]))

    assert scanned == ["src/Increment.kt"]
    assert "build" not in visited


def test_skips_files_matching_glob_pattern(tmp_path: Path):
    (tmp_path / "Increment.gen.kt").write_text(_KOTLIN)
    (tmp_path / "Increment.kt").write_text(_KOTLIN)

    scanned = list(scan_directory(tmp_path, exclude=["*.gen.kt"]))

    assert scanned == ["Increment.kt"]


def test_negation_pattern_reincludes_excluded_file(tmp_path: Path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "Keep.kt").write_text(_KOTLIN)
    (tmp_path / "build" / "Drop.kt").write_text(_KOTLIN)

    scanned = list(scan_directory(tmp_path, exclude=["build/", "!build/Keep.kt"]))

    assert scanned == ["build/Keep.kt"]


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
