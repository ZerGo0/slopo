import sqlite3

import pytest

from slopo import db
from slopo.indexing.db import (
    delete_file_units,
    delete_files,
    insert_file_units,
    prune_orphan_embeddings,
)
from slopo.indexing.parsing.base import CodeUnit


def _insert_file(conn: sqlite3.Connection) -> int:
    conn.execute("INSERT INTO files (path, mtime) VALUES ('Calculator.java', 0)")
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def test_inserts_unit_fields_into_matching_columns(conn: sqlite3.Connection):
    file_id = _insert_file(conn)
    unit = CodeUnit(
        body="int increment(int a) { return a + 1; }",
        start_line=2,
        end_line=4,
        body_node_count=7,
        body_hash="abc123",
        kind="function",
        context="int increment(int a)",
    )

    insert_file_units(conn, file_id, [unit])

    row = conn.execute(
        "SELECT file_id, context, body, start_line, end_line, body_node_count, body_hash"
        " FROM code_units"
    ).fetchone()
    assert row == (
        file_id,
        "int increment(int a)",
        "int increment(int a) { return a + 1; }",
        2,
        4,
        7,
        "abc123",
    )


def test_inserts_all_units_with_sequential_ids(conn: sqlite3.Connection):
    file_id = _insert_file(conn)
    units = [
        CodeUnit("body1", 1, 2, 3, "hash1", kind="function", context="ctx1"),
        CodeUnit("body2", 4, 5, 6, "hash2", kind="function", context="ctx2"),
    ]

    insert_file_units(conn, file_id, units)

    rows = conn.execute("SELECT id, context FROM code_units ORDER BY id").fetchall()
    assert rows == [(1, "ctx1"), (2, "ctx2")]


def test_deletes_file_and_its_units(conn: sqlite3.Connection):
    file_id = _insert_file(conn)
    insert_file_units(
        conn, file_id, [CodeUnit("body", 1, 2, 3, "hash", kind="function")]
    )

    delete_files(conn, [file_id])

    assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM code_units").fetchone()[0] == 0


def test_deletes_files_spanning_multiple_chunks(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(db, "_MAX_SQL_VARIABLES", 2)
    file_ids = []
    for i in range(5):
        conn.execute("INSERT INTO files (path, mtime) VALUES (?, 0)", (f"F{i}.java",))
        file_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        insert_file_units(
            conn, file_id, [CodeUnit("body", 1, 2, 3, f"h{i}", kind="function")]
        )
        file_ids.append(file_id)

    delete_files(conn, file_ids)

    assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM code_units").fetchone()[0] == 0


def test_deletes_units_of_modified_file(conn: sqlite3.Connection):
    file_id = _insert_file(conn)
    insert_file_units(
        conn, file_id, [CodeUnit("body", 1, 2, 3, "hash", kind="function")]
    )

    delete_file_units(conn, file_id)

    assert conn.execute("SELECT COUNT(*) FROM code_units").fetchone()[0] == 0


def test_prune_removes_embeddings_with_no_remaining_units(conn: sqlite3.Connection):
    conn.execute(
        "INSERT INTO embeddings (body_hash, embedding) VALUES ('gone', X'0000803f')"
    )

    prune_orphan_embeddings(conn)

    assert conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0] == 0


def test_prune_keeps_embedding_while_a_unit_shares_its_hash(conn: sqlite3.Connection):
    file_id = _insert_file(conn)
    insert_file_units(
        conn, file_id, [CodeUnit("body", 1, 2, 3, "shared", kind="function")]
    )
    conn.execute(
        "INSERT INTO embeddings (body_hash, embedding) VALUES ('shared', X'0000803f')"
    )

    prune_orphan_embeddings(conn)

    assert conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0] == 1
