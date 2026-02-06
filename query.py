"""ContextKeeper Query - Search memories with FTS5 support."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from config import DEFAULT_DB_PATH
from db_utils import get_connection, search_fts


def search_memories(
    keywords: List[str],
    category: Optional[str] = None,
    source: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 50,
    db_path: Path = None
) -> List[Dict[str, Any]]:
    """Search memories by keywords using FTS5 if available, fallback to LIKE."""
    path = db_path or DEFAULT_DB_PATH

    # If single keyword/query, use FTS5 for better performance
    if len(keywords) == 1 and not category and not source and min_importance <= 1:
        return search_fts(keywords[0], limit, path)

    # Complex query: use regular search with filters
    with get_connection(path) as conn:
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
        return [dict(row) for row in cursor.fetchall()]


def get_recent_memories(limit: int = 100, db_path: Path = None) -> List[Dict[str, Any]]:
    """Get recent memories."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """SELECT * FROM memories 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


class QueryEngine:
    """High-level query interface for ContextKeeper."""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memories by query string using FTS5."""
        # Use FTS5 for full-text search (much faster than LIKE)
        return search_fts(query, limit, self.db_path)

    def search_filtered(self, query: str, category: str = None,
                        source: str = None, min_importance: int = 1,
                        limit: int = 10) -> List[Dict]:
        """Search with filters."""
        keywords = query.split() if query else []
        return search_memories(
            keywords, category, source, min_importance, limit, self.db_path
        )

    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get most recent memories."""
        return get_recent_memories(limit, self.db_path)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Search ContextKeeper memories')
    parser.add_argument('keywords', nargs='*', help='Keywords to search for')
    parser.add_argument('-c', '--category', help='Filter by category')
    parser.add_argument('-s', '--source', help='Filter by source')
    parser.add_argument('-i', '--min-importance', type=int, default=1)
    parser.add_argument('-l', '--limit', type=int, default=50)
    parser.add_argument('--fts', action='store_true', help='Use FTS5 search')

    args = parser.parse_args()

    if args.fts and args.keywords:
        # Use FTS5
        results = search_fts(' '.join(args.keywords), args.limit)
    else:
        # Use regular search with filters
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
        ts = m['timestamp'][:16] if isinstance(m['timestamp'], str) and len(m['timestamp']) > 16 else m['timestamp']

        importance = m.get('importance', 5)
        fire = '🔥' * (importance // 3) if importance > 5 else ''
        category = m.get('category', 'note')
        content = m['content'][:100] + '...' if len(m['content']) > 100 else m['content']
        print(f"[{m['id']}] {ts} | {category} | {fire}")
        print(f"  {content}\n")


if __name__ == "__main__":
    main()
