import os
import sqlite3
from pathlib import Path

from slopo.indexing.scanner import NodeCountThresholds
from slopo.indexing.sync import SyncStats, sync_index

_NO_THRESHOLDS = NodeCountThresholds(function=0, block=0)

# Two methods, so each file yields two code units.
_JAVA = """\
class Calculator {
    int increment(int a) {
        return a + 1;
    }

    int decrement(int a) {
        return a - 1;
    }
}
"""


def _indexed_files(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT path FROM files").fetchall()
    return {row[0] for row in rows}


def _unit_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM code_units").fetchone()[0]


def test_indexes_new_files_on_first_run(tmp_path: Path, conn: sqlite3.Connection):
    (tmp_path / "Calculator.java").write_text(_JAVA)
    (tmp_path / "Greeter.java").write_text(_JAVA)

    result = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])

    assert result == SyncStats(
        indexed_files=2, skipped_files=0, indexed_units=4, removed_files=0
    )
    assert _indexed_files(conn) == {"Calculator.java", "Greeter.java"}
    assert _unit_count(conn) == 4


def test_skips_unchanged_file_on_reindex(tmp_path: Path, conn: sqlite3.Connection):
    (tmp_path / "Calculator.java").write_text(_JAVA)

    result_first = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])
    assert result_first == SyncStats(
        indexed_files=1, skipped_files=0, indexed_units=2, removed_files=0
    )

    result_second = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])

    assert result_second == SyncStats(
        indexed_files=0, skipped_files=1, indexed_units=0, removed_files=0
    )
    assert _indexed_files(conn) == {"Calculator.java"}
    assert _unit_count(conn) == 2


def test_update_a_file_with_a_newer_mtime_on_reindex(
    tmp_path: Path, conn: sqlite3.Connection
):
    path = tmp_path / "Calculator.java"
    path.write_text(_JAVA)

    result_first = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])
    assert result_first == SyncStats(
        indexed_files=1, skipped_files=0, indexed_units=2, removed_files=0
    )

    os.utime(path, (path.stat().st_atime, path.stat().st_mtime + 10))
    result_second = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])

    assert result_second == SyncStats(
        indexed_files=1, skipped_files=0, indexed_units=2, removed_files=0
    )
    assert _indexed_files(conn) == {"Calculator.java"}
    assert _unit_count(conn) == 2


def test_removes_units_when_a_file_is_deleted(tmp_path: Path, conn: sqlite3.Connection):
    (tmp_path / "Calculator.java").write_text(_JAVA)
    gone = tmp_path / "Greeter.java"
    gone.write_text(_JAVA)

    result_first = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])
    assert result_first == SyncStats(
        indexed_files=2, skipped_files=0, indexed_units=4, removed_files=0
    )

    gone.unlink()
    result_second = sync_index(conn, tmp_path, _NO_THRESHOLDS, exclude=[])

    assert result_second == SyncStats(
        indexed_files=0, skipped_files=1, indexed_units=0, removed_files=1
    )
    assert _indexed_files(conn) == {"Calculator.java"}
    assert _unit_count(conn) == 2
