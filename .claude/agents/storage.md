# Storage Agent  

Your job: Save extracted memories to SQLite database.

## Input
JSON from Extraction Agent

## Actions
1. Connect to: ~/.openclaw/workspace/contextkeeper/memory.db
2. Insert into memories table
3. Confirm success/failure

## SQL Pattern
INSERT INTO memories (source, category, content, keywords, importance, session_key)
VALUES (?, ?, ?, ?, ?, ?);
