"""Tests for ingestion utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from myelinate.ingest import is_url, save_to_corpus, validate_url

if TYPE_CHECKING:
    from pathlib import Path


class TestIsUrl:
    def test_http(self) -> None:
        assert is_url("http://example.com") is True

    def test_https(self) -> None:
        assert is_url("https://example.com") is True

    def test_file_path(self) -> None:
        assert is_url("/home/user/file.py") is False

    def test_relative_path(self) -> None:
        assert is_url("./folder/file.md") is False


class TestValidateUrl:
    def test_valid_https(self) -> None:
        assert validate_url("https://arxiv.org/abs/123") == "https://arxiv.org/abs/123"

    def test_rejects_file_protocol(self) -> None:
        with pytest.raises(ValueError, match="Only http/https"):
            validate_url("file:///etc/passwd")

    def test_rejects_ftp(self) -> None:
        with pytest.raises(ValueError, match="Only http/https"):
            validate_url("ftp://example.com/file")


class TestSaveToCorpus:
    def test_saves_file(self, tmp_path: Path) -> None:
        corpus = tmp_path / "corpus"
        path = save_to_corpus(b"hello world", "test.txt", corpus)
        assert path.exists()
        assert path.read_bytes() == b"hello world"

    def test_creates_directory(self, tmp_path: Path) -> None:
        corpus = tmp_path / "new" / "corpus"
        save_to_corpus(b"data", "file.txt", corpus)
        assert corpus.is_dir()
