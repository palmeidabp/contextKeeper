"""Shared database utilities for ContextKeeper."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from config import DEFAULT_DB_PATH, DB_TIMEOUT


@contextmanager
def get_connection(db_path: Optional[Path] = None):
    """Get a database connection with proper settings."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path), timeout=DB_TIMEOUT)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(db_path: Optional[Path] = None):
    """Initialize the database with schema and indexes."""
    with get_connection(db_path) as conn:
        # Main memories table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT DEFAULT 'manual',
                category TEXT,
                keywords TEXT,
                importance INTEGER DEFAULT 5,
                session_key TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for common queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_timestamp 
            ON memories(timestamp DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_category 
            ON memories(category)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_session 
            ON memories(session_key)
        """)
        
        # FTS5 virtual table for full-text search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                content,
                content='memories',
                content_rowid='id'
            )
        """)
        
        # Triggers to keep FTS index in sync
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_insert 
            AFTER INSERT ON memories
            BEGIN
                INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
            END
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_delete 
            AFTER DELETE ON memories
            BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, content) 
                VALUES ('delete', old.id, old.content);
            END
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_update 
            AFTER UPDATE ON memories
            BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, content) 
                VALUES ('delete', old.id, old.content);
                INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
            END
        """)


def search_fts(query: str, limit: int = 50, db_path: Optional[Path] = None) -> list:
    """Search using FTS5 full-text search."""
    with get_connection(db_path) as conn:
        cursor = conn.execute("""
            SELECT m.* FROM memories m
            JOIN memories_fts fts ON m.id = fts.rowid
            WHERE memories_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        return [dict(row) for row in cursor.fetchall()]
