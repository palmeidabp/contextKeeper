#!/usr/bin/env python3
"""ContextKeeper - Personal memory system for conversations."""

import sys
import os
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_DB_PATH
from db_utils import init_database
from extractor import process_text
from storage import MemoryStore
from query import QueryEngine
from summary import SummaryGenerator


class ContextKeeper:
    """Main class that coordinates all memory functions."""

    def __init__(self, db_path=None):
        self.db_path = str(db_path) if db_path else str(DEFAULT_DB_PATH)

        # Initialize database if needed
        init_database(self.db_path)

        self.store = MemoryStore(self.db_path)
        self.query = QueryEngine(self.db_path)
        self.summary = SummaryGenerator(self.db_path)

    def save_conversation(self, text, source='manual'):
        """Extract and save conversation text to memory."""
        if not text or not text.strip():
            return []

        # Extract structured data
        extracted = process_text(text)

        # Save each item
        saved_ids = []
        for item in extracted:
            memory_id = self.store.save(
                content=item['content'],
                category=item['category'],
                keywords=','.join(item['keywords']),
                importance=item['importance'],
                source=source
            )
            saved_ids.append(memory_id)

        return saved_ids

    def search(self, query, limit=10):
        """Search memories using FTS5 full-text search."""
        return self.query.search(query, limit)

    def search_filtered(self, query, category=None, source=None, limit=10):
        """Search with filters."""
        return self.query.search_filtered(query, category, source, limit=limit)

    def get_summary(self, days=7):
        """Get summary of recent memories."""
        return self.summary.generate(days)

    def list_recent(self, limit=20):
        """List most recent memories."""
        return self.query.get_recent(limit)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='ContextKeeper - Memory system')
    parser.add_argument('action', choices=['save', 'search', 'summary', 'recent', 'init'],
                       help='Action to perform')
    parser.add_argument('--text', '-t', help='Text to save (for save action)')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--category', '-c', help='Filter by category')
    parser.add_argument('--source', '-s', help='Filter by source')
    parser.add_argument('--days', '-d', type=int, default=7, help='Days for summary')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Result limit')
    parser.add_argument('--db', help='Database path (default: ~/.openclaw/workspace/contextkeeper/memory.db)')

    args = parser.parse_args()

    ck = ContextKeeper(args.db)

    if args.action == 'init':
        print(f"Database initialized at: {args.db or DEFAULT_DB_PATH}")

    elif args.action == 'save':
        if args.text:
            text = args.text
        else:
            text = sys.stdin.read()

        ids = ck.save_conversation(text, args.source or 'manual')
        print(f"Saved {len(ids)} memories")

    elif args.action == 'search':
        if not args.query:
            print("Error: --query required for search")
            sys.exit(1)

        if args.category or args.source:
            results = ck.search_filtered(
                args.query,
                category=args.category,
                source=args.source,
                limit=args.limit
            )
        else:
            results = ck.search(args.query, args.limit)

        print(json.dumps(results, indent=2, default=str))

    elif args.action == 'summary':
        summary = ck.get_summary(args.days)
        print(summary)

    elif args.action == 'recent':
        results = ck.list_recent(args.limit)
        print(json.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    main()
