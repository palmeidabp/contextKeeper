#!/usr/bin/env python3
"""ContextKeeper - Personal memory system for conversations."""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from extractor import process_text
    from storage import MemoryStore
    from query import QueryEngine
    from summary import SummaryGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class ContextKeeper:
    """Main class that coordinates all memory functions."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to workspace directory
            workspace = Path.home() / '.openclaw' / 'workspace' / 'contextkeeper'
            workspace.mkdir(parents=True, exist_ok=True)
            db_path = workspace / 'memory.db'
        
        self.db_path = str(db_path)
        self.store = MemoryStore(self.db_path)
        self.query = QueryEngine(self.db_path)
        self.summary = SummaryGenerator(self.db_path)
    
    def save_conversation(self, text, source='manual'):
        """Extract and save conversation text to memory."""
        if not text.strip():
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
        """Search memories by keywords or content."""
        return self.query.search(query, limit)
    
    def get_summary(self, days=7):
        """Get summary of recent memories."""
        return self.summary.generate(days)
    
    def list_recent(self, limit=20):
        """List most recent memories."""
        return self.query.get_recent(limit)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ContextKeeper - Memory system')
    parser.add_argument('action', choices=['save', 'search', 'summary', 'recent'],
                       help='Action to perform')
    parser.add_argument('--text', '-t', help='Text to save (for save action)')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--days', '-d', type=int, default=7, help='Days for summary')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Result limit')
    
    args = parser.parse_args()
    
    ck = ContextKeeper()
    
    if args.action == 'save':
        if args.text:
            text = args.text
        else:
            text = sys.stdin.read()
        
        ids = ck.save_conversation(text)
        print(f"Saved {len(ids)} memories")
        
    elif args.action == 'search':
        if not args.query:
            print("Error: --query required for search")
            sys.exit(1)
        
        results = ck.search(args.query, args.limit)
        print(json.dumps(results, indent=2))
        
    elif args.action == 'summary':
        summary = ck.get_summary(args.days)
        print(summary)
        
    elif args.action == 'recent':
        results = ck.list_recent(args.limit)
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
