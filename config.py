"""Centralized configuration for ContextKeeper."""

from pathlib import Path

# Default paths
DEFAULT_WORKSPACE = Path.home() / '.openclaw' / 'workspace' / 'contextkeeper'
DEFAULT_DB_PATH = DEFAULT_WORKSPACE / 'memory.db'

# Database settings
DB_TIMEOUT = 30.0  # seconds
DB_ISOLATION_LEVEL = None  # autocommit mode for SQLite

# Search settings
FTS5_ENABLED = True
MAX_SEARCH_RESULTS = 100

# Extraction settings
MAX_KEYWORDS = 5
STOP_WORDS = {
    'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 
    'when', 'where', 'what', 'which', 'their', 'would', 'could', 'should'
}
