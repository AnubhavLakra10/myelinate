"""Tests for content-hash cache."""

from __future__ import annotations

from typing import TYPE_CHECKING

from myelinate.cache import file_hash, load_cache, partition_by_cache, save_cache

if TYPE_CHECKING:
    from pathlib import Path


class TestFileHash:
    def test_consistent_hash(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        assert file_hash(f) == file_hash(f)

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.write_text("world")
        assert file_hash(a) != file_hash(b)


class TestCachePersistence:
    def test_roundtrip(self, tmp_path: Path) -> None:
        cache = {"file.py": "abc123"}
        save_cache(cache, tmp_path)
        loaded = load_cache(tmp_path)
        assert loaded == cache

    def test_empty_cache_when_missing(self, tmp_path: Path) -> None:
        assert load_cache(tmp_path / "nonexistent") == {}


class TestPartitionByCache:
    def test_new_files_are_changed(self, tmp_path: Path) -> None:
        f = tmp_path / "new.py"
        f.write_text("x = 1")
        changed, cached = partition_by_cache([f], tmp_path)
        assert len(changed) == 1
        assert len(cached) == 0

    def test_cached_files_detected(self, tmp_path: Path) -> None:
        f = tmp_path / "cached.py"
        f.write_text("x = 1")
        cache = {str(f): file_hash(f)}
        save_cache(cache, tmp_path)

        changed, cached = partition_by_cache([f], tmp_path)
        assert len(changed) == 0
        assert len(cached) == 1
