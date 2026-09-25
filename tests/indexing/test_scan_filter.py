from pathlib import Path

import pytest

from slopo.indexing.scan_filter import ScanFilter


# --- should_enter_dir ---


@pytest.mark.parametrize(
    ("exclude", "relative_dir"),
    [
        ([], "src"),
        (["/build/"], "src/build"),
        (["src/build/dir"], "src/build"),
        (["build/dir"], "src/build/dir"),
        (["*.kt"], "src"),
        (
            ["build/", "target/", ".gradle/", "**/generated/**"],
            "buildSrc",
        ),
        (["**/test/**"], "src/test"),
        (["**/test/**"], "test"),
        (["build/**"], "build"),
        (["build/", "!src/build/"], "src/build"),
    ],
)
def test_enters_directory_not_excluded(exclude: list[str], relative_dir: str):
    scan_filter = ScanFilter.create(exclude, include_extensions=[])

    assert scan_filter.should_enter_dir(Path(relative_dir))


@pytest.mark.parametrize(
    ("exclude", "relative_dir"),
    [
        (["build/"], "build"),
        (["build/"], "src/build"),
        (["build"], "build"),
        (["/build"], "build"),
        (["src/build/dir"], "src/build/dir"),
        (["src/build/dir"], "src/build/dir/subdir"),
        (["**/test/**"], "src/test/sub"),
        (["*.gen"], "out.gen"),
        (
            ["build/", "target/", ".gradle/", "**/generated/**"],
            "src/main/generated/sub",
        ),
    ],
)
def test_skips_excluded_directory(exclude: list[str], relative_dir: str):
    scan_filter = ScanFilter.create(exclude, include_extensions=[])

    assert not scan_filter.should_enter_dir(Path(relative_dir))


# --- should_keep_file ---


def test_keeps_supported_file():
    scan_filter = ScanFilter.create(exclude=[], include_extensions=[])

    assert scan_filter.should_keep_file(Path("Increment.kt"))


def test_keeps_supported_file_with_uppercase_extension():
    scan_filter = ScanFilter.create(exclude=[], include_extensions=[])

    assert scan_filter.should_keep_file(Path("Increment.KT"))


def test_skips_unsupported_file():
    scan_filter = ScanFilter.create(exclude=[], include_extensions=[])

    assert not scan_filter.should_keep_file(Path("notes.txt"))


@pytest.mark.parametrize(
    ("exclude", "relative_file"),
    [
        (["*.gen.kt"], "Increment.gen.kt"),
        (["Increment.kt"], "src/Increment.kt"),
        (["build/"], "build/Increment.kt"),
        (["**/test/**"], "src/test/Increment.kt"),
        (
            ["*.ts", "*.tsx"],
            "*.tsx",
        ),
    ],
)
def test_skips_excluded_file(exclude: list[str], relative_file: str):
    scan_filter = ScanFilter.create(exclude, include_extensions=[])

    assert not scan_filter.should_keep_file(Path(relative_file))


@pytest.mark.parametrize(
    ("exclude", "relative_file"),
    [
        (
            ["**/generated/**", "!**/generated/Api.kt"],
            "src/generated/Api.kt",
        ),
        (
            ["*.test.ts", "!setup.test.ts"],
            "src/setup.test.ts",
        ),
    ],
)
def test_keeps_file_reincluded_by_negation(exclude: list[str], relative_file: str):
    scan_filter = ScanFilter.create(exclude, include_extensions=[])

    assert scan_filter.should_keep_file(Path(relative_file))


def test_keeps_only_included_extensions():
    scan_filter = ScanFilter.create(exclude=[], include_extensions=[".kt"])

    assert scan_filter.should_keep_file(Path("Increment.kt"))
    assert not scan_filter.should_keep_file(Path("Calculator.java"))


def test_skips_excluded_file_with_included_extension():
    scan_filter = ScanFilter.create(exclude=["*.kt"], include_extensions=[".kt"])

    assert not scan_filter.should_keep_file(Path("Increment.kt"))
