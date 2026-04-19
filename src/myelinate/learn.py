"""FSRS-based spaced repetition engine."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

DB_PATH = Path("myelinate-out/learn.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    card_id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_edge TEXT NOT NULL,
    difficulty REAL DEFAULT 0.3,
    stability REAL DEFAULT 1.0,
    due REAL DEFAULT 0.0,
    reps INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0,
    state INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
"""


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize the learning database."""
    target = db_path or DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def add_card(
    conn: sqlite3.Connection,
    card_id: str,
    question: str,
    answer: str,
    source_edge: str,
) -> None:
    """Insert a new review card."""
    now = time.time()
    conn.execute(
        """INSERT OR IGNORE INTO cards
        (card_id, question, answer, source_edge, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (card_id, question, answer, source_edge, now, now),
    )
    conn.commit()


def get_due_cards(
    conn: sqlite3.Connection,
    limit: int = 10,
    topic_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch cards that are due for review."""
    now = time.time()
    query = "SELECT * FROM cards WHERE due <= ? ORDER BY due ASC LIMIT ?"
    rows = conn.execute(query, (now, limit)).fetchall()
    return [dict(row) for row in rows]


def record_review(
    conn: sqlite3.Connection,
    card_id: str,
    rating: int,
) -> None:
    """Record a review and update scheduling via FSRS.

    Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    """
    row = conn.execute("SELECT * FROM cards WHERE card_id = ?", (card_id,)).fetchone()
    if row is None:
        return

    now = time.time()
    difficulty = row["difficulty"]
    stability = row["stability"]
    reps = row["reps"]
    lapses = row["lapses"]

    # Simplified FSRS scheduling
    if rating == 1:  # Again
        stability = max(0.1, stability * 0.5)
        difficulty = min(1.0, difficulty + 0.1)
        lapses += 1
        interval_days = 0.0  # review again immediately
    elif rating == 2:  # Hard
        stability = stability * 1.2
        difficulty = min(1.0, difficulty + 0.05)
        interval_days = stability * 0.8
    elif rating == 3:  # Good
        stability = stability * 2.5
        interval_days = stability
    else:  # Easy
        stability = stability * 3.5
        difficulty = max(0.0, difficulty - 0.05)
        interval_days = stability * 1.3

    due = now + (interval_days * 86400)
    reps += 1

    conn.execute(
        """UPDATE cards SET
        difficulty=?, stability=?, due=?, reps=?, lapses=?, updated_at=?
        WHERE card_id=?""",
        (difficulty, stability, due, reps, lapses, now, card_id),
    )
    conn.commit()
