"""
Metrics logging utilities for the AI Debugging Copilot backend.

This module encapsulates SQLite interactions used to record metrics for each
diagnostic call. Metrics include the duration of the call in milliseconds,
approximate token counts for the prompt and completion, the total token
count, and the confidence returned by the model. The database path can be
configured via the `METRICS_DB` environment variable; it defaults to
`metrics.db` in the working directory.
"""

import os
import sqlite3
from typing import Optional

DB_PATH = os.environ.get("METRICS_DB", "metrics.db")


def init_db(db_path: Optional[str] = None) -> None:
    """Initialise the SQLite database and create the metrics table if absent.

    Parameters:
      db_path: Optional override for the database file path. Uses the
        `DB_PATH` environment value by default.
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    try:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration_ms INTEGER,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                confidence REAL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def log_call(
    duration_ms: int,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    confidence: float,
    db_path: Optional[str] = None,
) -> None:
    """Insert a metrics record for a diagnostic call.

    Parameters:
      duration_ms: The duration of the call in milliseconds.
      prompt_tokens: Approximate number of tokens in the prompt sent to the model.
      completion_tokens: Approximate number of tokens in the model's response.
      total_tokens: Sum of prompt_tokens and completion_tokens.
      confidence: The confidence value returned by the model.
      db_path: Optional override for the database file path.
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    try:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO metrics (
                duration_ms, prompt_tokens, completion_tokens, total_tokens, confidence
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (duration_ms, prompt_tokens, completion_tokens, total_tokens, confidence),
        )
        conn.commit()
    finally:
        conn.close()