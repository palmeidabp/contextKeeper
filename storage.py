"""ContextKeeper Storage - SQLite persistence layer."""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import DEFAULT_DB_PATH
from db_utils import get_connection, init_database


def save_memory(content: str, source: str = 'manual', category: str = None,
                keywords: str = None, importance: int = 5, session_key: str = None,
                db_path: Path = None) -> int:
    """Save a memory to the database."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """INSERT INTO memories 
               (content, source, category, keywords, importance, session_key)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (content, source, category, keywords, importance, session_key)
        )
        return cursor.lastrowid


def load_memory(memory_id: int, db_path: Path = None) -> Optional[Dict[str, Any]]:
    """Load a specific memory by ID."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,)
        ).fetchone()
        return dict(row) if row else None


def search_memories(query: str, limit: int = 50, db_path: Path = None) -> List[Dict[str, Any]]:
    """Search memories by content or keywords (legacy, uses LIKE)."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """SELECT * FROM memories 
               WHERE content LIKE ? OR keywords LIKE ?
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_recent_memories(limit: int = 100, days: int = None, db_path: Path = None) -> List[Dict[str, Any]]:
    """Get recent memories, optionally filtered by days."""
    with get_connection(db_path) as conn:
        if days:
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor = conn.execute(
                """SELECT * FROM memories 
                   WHERE timestamp >= ?
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (cutoff, limit)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM memories 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]


# High-level interface for main.py
class MemoryStore:
    """High-level interface for memory operations."""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def init(self):
        """Initialize database (create tables and indexes)."""
        init_database(self.db_path)

    def save(self, content: str, category: str = None, keywords: str = None,
             importance: str = None, source: str = 'manual', session_key: str = None) -> int:
        """Save a memory with metadata."""
        imp = 5
        if importance:
            try:
                imp = int(importance) if str(importance).isdigit() else 5
            except (ValueError, TypeError):
                pass

        return save_memory(
            content=content,
            source=source,
            category=category,
            keywords=keywords,
            importance=imp,
            session_key=session_key,
            db_path=self.db_path
        )

    def get(self, memory_id: int) -> Optional[Dict]:
        """Get a memory by ID."""
        return load_memory(memory_id, self.db_path)

    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all memories."""
        return get_recent_memories(limit=limit, db_path=self.db_path)

    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search memories."""
        return search_memories(query, limit, self.db_path)

    def search_fts(self, query: str, limit: int = 50) -> List[Dict]:
        """Search using FTS5 full-text search."""
        from db_utils import search_fts
        return search_fts(query, limit, self.db_path)
