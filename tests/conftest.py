"""Shared fixtures for myelinate tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def tmp_corpus(tmp_path: Path) -> Path:
    """Create a temporary corpus directory with sample files."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()

    (corpus / "example.py").write_text(
        'def greet(name: str) -> str:\n    return f"Hello, {name}"\n'
    )
    (corpus / "notes.md").write_text("# Attention\n\nAttention is all you need.\n")
    (corpus / "readme.txt").write_text("This is a sample readme file.\n")
    return corpus


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    out = tmp_path / "myelinate-out"
    out.mkdir()
    return out
