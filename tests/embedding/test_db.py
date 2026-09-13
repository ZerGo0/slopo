import sqlite3

import numpy as np

from slopo.embedding.db import (
    count_unembedded_units,
    load_embeddings,
    load_next_batch,
    save_embeddings,
)
from slopo.embedding.models import EmbeddedUnit

# --- count_unembedded_units ---


def test_count_unembedded_units_ignores_embedded_hashes(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (2, 1, 'b', 'b', 1, 2, 3, 'hashB');
        INSERT INTO embeddings (body_hash, embedding) VALUES ('hashB', X'0000803f');
    """)

    assert count_unembedded_units(conn) == 1


def test_count_unembedded_units_counts_each_hash_once(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (2, 1, 'a', 'a', 1, 2, 3, 'hashA');
    """)

    assert count_unembedded_units(conn) == 1


# --- load_next_batch ---


def test_load_next_batch_skips_already_embedded_hashes(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (2, 1, 'b', 'b', 1, 2, 3, 'hashB');
        INSERT INTO embeddings (body_hash, embedding) VALUES ('hashA', X'0000803f');
    """)

    batch = load_next_batch(conn, max_items=10, max_chars=10_000)

    assert [u.body_hash for u in batch] == ["hashB"]


def test_load_next_batch_emits_each_hash_once(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (2, 1, 'a', 'a', 1, 2, 3, 'hashA');
    """)

    batch = load_next_batch(conn, max_items=10, max_chars=10_000)

    assert [u.body_hash for u in batch] == ["hashA"]


# --- load_embeddings ---


def test_load_embeddings_for_all_embedded_units(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (2, 1, 'a', 'a', 1, 2, 3, 'hashA');
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (3, 1, 'b', 'b', 1, 2, 3, 'hashB');
        INSERT INTO embeddings (body_hash, embedding) VALUES ('hashA', X'0000803f');
    """)

    assert sorted(load_embeddings(conn)) == [1, 2]


# --- save_embeddings ---


def test_save_then_load_embeddings_round_trips_the_vector(conn: sqlite3.Connection):
    conn.executescript("""
        INSERT INTO files (id, path, mtime) VALUES (1, 'File.java', 0);
        INSERT INTO code_units (id, file_id, context, body, start_line, end_line, body_node_count, body_hash)
            VALUES (1, 1, 'a', 'a', 1, 2, 3, 'hashA');
    """)

    save_embeddings(conn, [EmbeddedUnit(body_hash="hashA", vector=[1.0, 2.0, 3.0])])

    loaded = load_embeddings(conn)
    assert np.array_equal(loaded[1], np.array([1.0, 2.0, 3.0], dtype=np.float32))
