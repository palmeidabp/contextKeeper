"""ContextKeeper Summary - Generate memory digests."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional

from config import DEFAULT_DB_PATH
from db_utils import get_connection


def fetch_recent_memories(days: int = 7, db_path: Path = None) -> List[Dict[str, Any]]:
    """Fetch memories from the last N days."""
    with get_connection(db_path) as conn:
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.execute(
            """SELECT id, content, category, keywords, importance, timestamp 
               FROM memories
               WHERE timestamp >= ?
               ORDER BY timestamp DESC""",
            (cutoff,)
        )

        return [dict(row) for row in cursor.fetchall()]


def extract_key_topics(memories: List[Dict[str, Any]], top_n: int = 5) -> List[str]:
    """Extract key topics from categories and keywords."""
    all_topics = []
    for memory in memories:
        if memory.get('category'):
            all_topics.append(memory['category'].lower())
        if memory.get('keywords'):
            keywords = [k.strip().lower() for k in memory['keywords'].split(',')]
            all_topics.extend(keywords)

    topic_counts = Counter(t for t in all_topics if t)
    return [t for t, _ in topic_counts.most_common(top_n)]


def generate_summary_text(memories: List[Dict[str, Any]], days: int) -> str:
    """Generate a human-readable summary text."""
    if not memories:
        return f"No memories recorded in the last {days} days."

    key_topics = extract_key_topics(memories)

    lines = [
        f"# Memory Digest: Last {days} Days",
        "",
        f"**Total Memories:** {len(memories)}",
        f"**Key Topics:** {', '.join(key_topics) if key_topics else 'None identified'}",
        "",
        "## Recent Memories",
        ""
    ]

    for memory in memories[:20]:
        ts = memory.get('timestamp', 'N/A')
        if isinstance(ts, str) and len(ts) > 16:
            ts = ts[:16]

        importance = memory.get('importance', 5)
        fire = '🔥' * (importance // 3) if importance > 5 else ''
        category = memory.get('category', 'note')
        content = memory['content'][:150] + '...' if len(memory['content']) > 150 else memory['content']
        lines.append(f"- **{ts}** [{category}] {fire} {content}")

    return '\n'.join(lines)


class SummaryGenerator:
    """High-level interface for generating summaries."""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def generate(self, days: int = 7) -> str:
        """Generate summary for the last N days."""
        memories = fetch_recent_memories(days, self.db_path)
        return generate_summary_text(memories, days)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate memory digests')
    parser.add_argument('-d', '--days', type=int, default=7, help='Days to include')
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()

    sg = SummaryGenerator()
    summary = sg.generate(args.days)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(summary)
        print(f"Summary saved to {args.output}")
    else:
        print(summary)


if __name__ == '__main__':
    main()
