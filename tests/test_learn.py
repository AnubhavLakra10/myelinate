"""Tests for the spaced repetition engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from myelinate.learn import add_card, get_due_cards, init_db, record_review

if TYPE_CHECKING:
    from pathlib import Path


class TestLearnDB:
    def test_init_creates_table(self, tmp_path: Path) -> None:
        db_path = tmp_path / "learn.db"
        conn = init_db(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_add_and_fetch_card(self, tmp_path: Path) -> None:
        conn = init_db(tmp_path / "learn.db")
        add_card(conn, "c1", "What is attention?", "A mechanism for...", "a->b")
        cards = get_due_cards(conn, limit=10)
        assert len(cards) == 1
        assert cards[0]["question"] == "What is attention?"
        conn.close()

    def test_duplicate_card_ignored(self, tmp_path: Path) -> None:
        conn = init_db(tmp_path / "learn.db")
        add_card(conn, "c1", "Q1", "A1", "e1")
        add_card(conn, "c1", "Q2", "A2", "e2")
        cards = get_due_cards(conn, limit=10)
        assert len(cards) == 1
        assert cards[0]["question"] == "Q1"
        conn.close()


class TestReviewScheduling:
    def test_good_review_increases_stability(self, tmp_path: Path) -> None:
        conn = init_db(tmp_path / "learn.db")
        add_card(conn, "c1", "Q", "A", "e1")

        before = get_due_cards(conn)[0]
        record_review(conn, "c1", rating=3)
        after = conn.execute("SELECT * FROM cards WHERE card_id='c1'").fetchone()

        assert after["stability"] > before["stability"]
        assert after["reps"] == 1
        conn.close()

    def test_again_decreases_stability(self, tmp_path: Path) -> None:
        conn = init_db(tmp_path / "learn.db")
        add_card(conn, "c1", "Q", "A", "e1")

        # First do a good review to raise stability
        record_review(conn, "c1", rating=3)
        mid = conn.execute("SELECT * FROM cards WHERE card_id='c1'").fetchone()

        record_review(conn, "c1", rating=1)
        after = conn.execute("SELECT * FROM cards WHERE card_id='c1'").fetchone()

        assert after["stability"] < mid["stability"]
        assert after["lapses"] == 1
        conn.close()

    def test_easy_decreases_difficulty(self, tmp_path: Path) -> None:
        conn = init_db(tmp_path / "learn.db")
        add_card(conn, "c1", "Q", "A", "e1")

        before = get_due_cards(conn)[0]
        record_review(conn, "c1", rating=4)
        after = conn.execute("SELECT * FROM cards WHERE card_id='c1'").fetchone()

        assert after["difficulty"] < before["difficulty"]
        conn.close()
