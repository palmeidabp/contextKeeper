#!/usr/bin/env python3
"""ContextKeeper Query - Search memories by keywords."""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

# Get DB path
DB_PATH = Path(os.path.expanduser("~/.openclaw/workspace/contextkeeper/memory.db"))

def _get_conn():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def search_memories(
    keywords: List[str],
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Search memories by keywords."""
    conn = _get_conn()
    conditions = ["1=1"]
    params = []

    if keywords:
        keyword_conditions = []
        for kw in keywords:
            keyword_conditions.append("(content LIKE ? OR keywords LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])
        conditions.append(f"({' OR '.join(keyword_conditions)})")

    if category:
        conditions.append("category = ?")
        params.append(category)

    if source:
        conditions.append("source = ?")
        params.append(source)

    if min_importance > 1:
        conditions.append("importance >= ?")
        params.append(min_importance)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT id, timestamp, source, category, content, keywords, importance, session_key
        FROM memories
        WHERE {where_clause}
        ORDER BY importance DESC, timestamp DESC
        LIMIT ?
    """
    params.append(limit)

    cursor = conn.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_recent_memories(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent memories."""
    conn = _get_conn()
    cursor = conn.execute(
        """SELECT * FROM memories 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (limit,)
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


class QueryEngine:
    """High-level query interface for ContextKeeper."""
    
    def __init__(self, db_path: str = None):
        pass
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memories by query string."""
        keywords = query.split() if query else []
        return search_memories(keywords, limit=limit)
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get most recent memories."""
        return get_recent_memories(limit=limit)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Search ContextKeeper memories')
    parser.add_argument('keywords', nargs='*', help='Keywords to search for')
    parser.add_argument('-c', '--category', help='Filter by category')
    parser.add_argument('-s', '--source', help='Filter by source')
    parser.add_argument('-i', '--min-importance', type=int, default=1)
    parser.add_argument('-l', '--limit', type=int, default=50)
    
    args = parser.parse_args()
    
    results = search_memories(
        keywords=args.keywords,
        category=args.category,
        source=args.source,
        min_importance=args.min_importance,
        limit=args.limit
    )

    if not results:
        print("No memories found.")
        return

    print(f"Found {len(results)} memories:\n")
    for m in results:
        print(f"[{m['id']}] {m['timestamp'][:16]} | {m.get('category', 'N/A')} | {m.get('importance', 5)}/10")
        content = m['content'][:100] + '...' if len(m['content']) > 100 else m['content']
        print(f"  {content}\n")


if __name__ == "__main__":
    main()
