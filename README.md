# ContextKeeper

Personal memory system for AI conversations using OpenClaw agent-relay.

## Quick Start

```bash
cd ~/.openclaw/workspace/contextkeeper

# Save a memory
echo "Important meeting about Bittensor tokens" | python3 main.py save

# Search memories
python3 query.py Bittensor

# Get recent memories
python3 main.py recent --limit 10

# Generate weekly summary
python3 main.py summary --days 7
```

## Components

| Module | Purpose |
|--------|---------|
| `extractor.py` | Parse text → structured JSON (category, keywords, importance) |
| `storage.py` | SQLite database operations |
| `query.py` | Search memories by keywords |
| `summary.py` | Generate weekly digest reports |
| `main.py` | Main ContextKeeper CLI and class |

## Database Schema

```sql
memories:
  id, timestamp, source, category, content, keywords, importance, session_key

summaries:
  id, week_start, week_end, summary_text, key_topics, created_at
```

## Created

2026-02-05 via agent-relay with Claude Code sub-agents
