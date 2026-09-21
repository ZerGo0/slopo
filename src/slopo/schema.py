import sqlite3

SCHEMA_VERSION = 4


# Bump SCHEMA_VERSION whenever schema changes
def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE schema_version (
            version INTEGER PRIMARY KEY
        );

        CREATE TABLE metadata (
            id                         INTEGER PRIMARY KEY CHECK (id = 1),
            source_dir                 TEXT NOT NULL,
            embedding_model            TEXT NOT NULL,
            embedding_dimensions       INTEGER NOT NULL,
            body_node_count_threshold  INTEGER NOT NULL,
            block_node_count_threshold INTEGER NOT NULL
        );

        CREATE TABLE files (
            id    INTEGER PRIMARY KEY,
            path  TEXT NOT NULL UNIQUE,
            mtime REAL NOT NULL
        );

        CREATE TABLE code_units (
            id               INTEGER PRIMARY KEY,
            file_id          INTEGER NOT NULL REFERENCES files(id),
            context          TEXT,
            body             TEXT NOT NULL,
            start_line       INTEGER NOT NULL,
            end_line         INTEGER NOT NULL,
            body_node_count  INTEGER NOT NULL,
            body_hash        TEXT NOT NULL,
            language         TEXT
        );

        CREATE TABLE embeddings (
            body_hash  TEXT PRIMARY KEY,
            embedding  BLOB NOT NULL
        );
    """)
    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
