import os
import sqlite3
import tempfile
import unittest

from app.utils.metrics import init_db, log_call


class TestMetrics(unittest.TestCase):
    def setUp(self) -> None:
        # Create a temporary file to use as the database
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.tmpfile.name
        self.tmpfile.close()
        # Ensure database does not exist yet
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def tearDown(self) -> None:
        # Remove temporary file
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass

    def test_init_and_log(self):
        # Initialize DB and verify table exists
        init_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
            self.assertIsNotNone(cur.fetchone(), "metrics table should exist after init_db")
        finally:
            conn.close()
        # Log a call and verify insertion
        init_db(self.db_path)  # re-init to ensure no duplicates
        log_call(123, 10, 20, 30, 0.8, db_path=self.db_path)
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT duration_ms, prompt_tokens, completion_tokens, total_tokens, confidence FROM metrics")
            row = cur.fetchone()
            self.assertIsNotNone(row, "A row should have been inserted")
            duration_ms, prompt_tokens, completion_tokens, total_tokens, confidence = row
            self.assertEqual(duration_ms, 123)
            self.assertEqual(prompt_tokens, 10)
            self.assertEqual(completion_tokens, 20)
            self.assertEqual(total_tokens, 30)
            self.assertAlmostEqual(confidence, 0.8)
        finally:
            conn.close()


if __name__ == '__main__':
    unittest.main()