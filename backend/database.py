"""Async SQLite persistence layer for documents, chunks, and chat messages."""
import json
from datetime import datetime, timezone
from typing import Any, Optional

import aiosqlite

from config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id           TEXT PRIMARY KEY,
    filename     TEXT NOT NULL,
    file_type    TEXT NOT NULL,
    upload_date  TEXT NOT NULL,
    char_count   INTEGER NOT NULL DEFAULT 0,
    chunk_count  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    id           TEXT PRIMARY KEY,
    doc_id       TEXT NOT NULL,
    chunk_index  INTEGER NOT NULL,
    content      TEXT NOT NULL,
    embedding    BLOB NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);

CREATE TABLE IF NOT EXISTS messages (
    id           TEXT PRIMARY KEY,
    session_id   TEXT NOT NULL,
    role         TEXT NOT NULL,
    content      TEXT NOT NULL,
    sources      TEXT NOT NULL DEFAULT '[]',
    timestamp    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
"""

_db: Optional[aiosqlite.Connection] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def connect() -> None:
    """Open the shared connection and ensure the schema exists."""
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA foreign_keys = ON;")
    await _db.executescript(_SCHEMA)
    await _db.commit()


async def close() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


def _conn() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return _db


# --- Documents ---------------------------------------------------------------

async def insert_document(doc_id: str, filename: str, file_type: str,
                          char_count: int, chunk_count: int) -> dict:
    upload_date = _now()
    await _conn().execute(
        "INSERT INTO documents (id, filename, file_type, upload_date, char_count, chunk_count)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (doc_id, filename, file_type, upload_date, char_count, chunk_count),
    )
    await _conn().commit()
    return {
        "id": doc_id,
        "filename": filename,
        "file_type": file_type,
        "upload_date": upload_date,
        "char_count": char_count,
        "chunk_count": chunk_count,
    }


async def list_documents() -> list[dict]:
    cur = await _conn().execute(
        "SELECT id, filename, file_type, upload_date, char_count, chunk_count"
        " FROM documents ORDER BY upload_date DESC"
    )
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def delete_document(doc_id: str) -> bool:
    cur = await _conn().execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    await _conn().commit()
    return cur.rowcount > 0


# --- Chunks ------------------------------------------------------------------

async def insert_chunks(rows: list[tuple[str, str, int, str, bytes]]) -> None:
    """rows: (chunk_id, doc_id, chunk_index, content, embedding_bytes)."""
    await _conn().executemany(
        "INSERT INTO chunks (id, doc_id, chunk_index, content, embedding)"
        " VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    await _conn().commit()


async def all_chunks() -> list[dict]:
    """Return every chunk joined with its document's filename."""
    cur = await _conn().execute(
        "SELECT c.id, c.doc_id, c.chunk_index, c.content, c.embedding, d.filename"
        " FROM chunks c JOIN documents d ON c.doc_id = d.id"
    )
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


# --- Messages ----------------------------------------------------------------

async def insert_message(msg_id: str, session_id: str, role: str,
                         content: str, sources: list[str]) -> None:
    await _conn().execute(
        "INSERT INTO messages (id, session_id, role, content, sources, timestamp)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, session_id, role, content, json.dumps(sources), _now()),
    )
    await _conn().commit()


async def get_history(session_id: str) -> list[dict]:
    cur = await _conn().execute(
        "SELECT role, content, sources, timestamp FROM messages"
        " WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,),
    )
    rows = await cur.fetchall()
    history = []
    for r in rows:
        d = dict(r)
        d["sources"] = json.loads(d["sources"])
        history.append(d)
    return history


async def clear_history(session_id: str) -> int:
    cur = await _conn().execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    await _conn().commit()
    return cur.rowcount
