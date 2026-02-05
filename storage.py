#!/usr/bin/env python3
"""ContextKeeper Storage - SQLite persistence layer."""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = Path(os.path.expanduser("~/.openclaw/workspace/contextkeeper/memory.db"))

@contextmanager
def get_connection():
    """Context manager for database connections."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def save_memory(content: str, source: str = 'manual', category: str = None, 
                keywords: str = None, importance: int = 5, session_key: str = None) -> int:
    """Save a memory to the database."""
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO memories 
               (content, source, category, keywords, importance, session_key)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (content, source, category, keywords, importance, session_key)
        )
        return cursor.lastrowid

def load_memory(memory_id: int) -> Optional[Dict[str, Any]]:
    """Load a specific memory by ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,)
        ).fetchone()
        if row:
            return dict(row)
        return None

def search_memories(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search memories by content or keywords."""
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT * FROM memories 
               WHERE content LIKE ? OR keywords LIKE ?
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_recent_memories(limit: int = 100, days: int = None) -> List[Dict[str, Any]]:
    """Get recent memories, optionally filtered by days."""
    with get_connection() as conn:
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
        global DB_PATH
        if db_path:
            DB_PATH = Path(db_path)
    
    def save(self, content: str, category: str = None, keywords: str = None, 
             importance: str = None, source: str = 'manual', session_key: str = None) -> int:
        """Save a memory with metadata."""
        imp = 5
        if importance:
            try:
                imp = int(importance) if str(importance).isdigit() else 5
            except:
                pass
        
        return save_memory(
            content=content, 
            source=source, 
            category=category,
            keywords=keywords,
            importance=imp,
            session_key=session_key
        )
    
    def get(self, memory_id: int) -> Optional[Dict]:
        """Get a memory by ID."""
        return load_memory(memory_id)
    
    def list_all(self, limit: int = 100) -> List[Dict]:
        """List all memories."""
        return get_recent_memories(limit=limit)
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search memories."""
        return search_memories(query, limit)
