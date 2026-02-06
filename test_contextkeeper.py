#!/usr/bin/env python3
"""Tests for ContextKeeper."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_DB_PATH
from db_utils import get_connection, init_database, search_fts
from extractor import process_text, categorize_content, extract_keywords
from storage import MemoryStore, save_memory
from query import QueryEngine, search_memories
from summary import SummaryGenerator, fetch_recent_memories


class TestExtractor(unittest.TestCase):
    """Tests for the extractor module."""

    def test_categorize_action(self):
        text = "Need to follow up on the project deadline tomorrow"
        self.assertEqual(categorize_content(text), 'action')

    def test_categorize_meeting(self):
        text = "We discussed the new architecture in the meeting"
        self.assertEqual(categorize_content(text), 'meeting_note')

    def test_categorize_note(self):
        text = "This is just a random observation"
        self.assertEqual(categorize_content(text), 'note')

    def test_extract_keywords(self):
        text = "Working on the Python project with Django framework"
        keywords = extract_keywords(text)
        self.assertIn('python', keywords)
        self.assertIn('django', keywords)

    def test_process_text(self):
        text = """We have a bug to fix in the codebase
An idea we had about the new feature
Just a regular observation without keywords"""
        results = process_text(text)
        self.assertEqual(len(results), 3)
        # 'bug' alone triggers 'issue' category
        self.assertEqual(results[0]['category'], 'issue')
        self.assertEqual(results[1]['category'], 'idea')   # idea mentioned


class TestDatabase(unittest.TestCase):
    """Tests for database operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        init_database(self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_tables(self):
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}
            self.assertIn('memories', tables)
            self.assertIn('memories_fts', tables)

    def test_save_and_load(self):
        memory_id = save_memory(
            content="Test memory",
            category="test",
            importance=8,
            db_path=self.db_path
        )
        self.assertGreater(memory_id, 0)

    def test_fts_search(self):
        # Save some test data
        save_memory("Python is great for web development", db_path=self.db_path)
        save_memory("JavaScript is used for frontend", db_path=self.db_path)
        save_memory("Rust is fast and safe", db_path=self.db_path)

        # Search
        results = search_fts("Python", db_path=self.db_path)
        self.assertEqual(len(results), 1)
        self.assertIn("Python", results[0]['content'])


class TestStorage(unittest.TestCase):
    """Tests for storage module."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.store = MemoryStore(self.db_path)
        self.store.init()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_get(self):
        memory_id = self.store.save(
            content="Test content",
            category="test",
            keywords="test,content",
            importance="8",
            source="test"
        )
        self.assertGreater(memory_id, 0)

        memory = self.store.get(memory_id)
        self.assertEqual(memory['content'], "Test content")


class TestQuery(unittest.TestCase):
    """Tests for query module."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        init_database(self.db_path)

        # Add test data
        from storage import save_memory
        save_memory("Python web development", category="code", db_path=self.db_path)
        save_memory("Machine learning project", category="ai", db_path=self.db_path)
        save_memory("Database optimization tips", category="code", db_path=self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_memories(self):
        results = search_memories(["Python"], db_path=self.db_path)
        self.assertGreaterEqual(len(results), 1)

    def test_query_engine(self):
        engine = QueryEngine(self.db_path)
        results = engine.search("Python")
        self.assertGreaterEqual(len(results), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for ContextKeeper."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow(self):
        from main import ContextKeeper

        # Initialize
        ck = ContextKeeper(self.db_path)

        # Save some memories
        text = """Meeting notes: We decided to use Python for the backend
TODO: Set up the database schema
Idea: Add full-text search functionality"""
        ids = ck.save_conversation(text, "integration_test")
        self.assertEqual(len(ids), 3)

        # Search
        results = ck.search("Python")
        self.assertGreaterEqual(len(results), 1)

        # Get recent
        recent = ck.list_recent(10)
        self.assertEqual(len(recent), 3)

        # Get summary
        summary = ck.get_summary(7)
        self.assertIn("**Total Memories:** 3", summary)


if __name__ == '__main__':
    print("Running ContextKeeper tests...")
    print(f"Python: {sys.version}")
    print(f"Testing in: {Path(__file__).parent}")
    print("-" * 50)

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
