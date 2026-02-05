-- ContextKeeper Database Schema
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL, -- 'telegram', 'auto_detect', 'manual_tag'
    category TEXT, -- 'bittensor', 'skills', 'ideas', 'decisions'
    content TEXT NOT NULL,
    keywords TEXT, -- comma-separated for search
    importance INTEGER DEFAULT 5, -- 1-10
    session_key TEXT, -- link to OpenClaw session
    metadata JSON -- flexible extra data
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp);
CREATE INDEX IF NOT EXISTS idx_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_keywords ON memories(keywords);

-- For weekly summaries
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    summary_text TEXT NOT NULL,
    key_topics TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
