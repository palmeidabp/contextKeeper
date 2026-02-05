# ContextKeeper - Usage Guide

## Quick Commands

```bash
# Navigate to project
cd ~/.openclaw/workspace/contextkeeper

# Save something you want to remember
echo "Meeting with Pedro about Bittensor subnet strategies" | python3 main.py save

# Search for memories about a topic
python3 query.py bittensor
python3 query.py meeting --limit 5

# See your recent memories  
python3 main.py recent

# Get a weekly summary
python3 main.py summary
python3 main.py summary --days 3  # Last 3 days
```

## How It Works

When you save text, ContextKeeper:
1. **Extracts** - Identifies category, keywords, importance
2. **Stores** - Saves to SQLite database with metadata
3. **Tags** - Adds category:meeting, importance:high, etc.

## Examples

```bash
# Save with category
echo "Idea: Build a dashboard for subnet metrics" | python3 main.py save

# Search all ideas
python3 query.py -c ideas

# Find important items
python3 query.py --min-importance 8

# Get everything from telegram source
python3 query.py -s telegram
```

## Integration with OpenClaw

I can now:
- Auto-save important parts of our conversations
- Search your memory when you ask about past topics
- Generate weekly summaries of what we discussed

Just ask me to "remember this" or "search for X" and I'll use ContextKeeper!
