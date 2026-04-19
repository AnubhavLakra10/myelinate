"""Ingest files and URLs into the corpus."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from pathlib import Path


def is_url(s: str) -> bool:
    """Check if a string is a URL."""
    parsed = urlparse(s)
    return parsed.scheme in ("http", "https")


def validate_url(url: str) -> str:
    """Validate and normalize a URL. Only http/https allowed."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        msg = f"Only http/https URLs are allowed, got: {parsed.scheme}"
        raise ValueError(msg)
    return url


def save_to_corpus(content: bytes, filename: str, corpus_dir: Path) -> Path:
    """Save fetched content to the corpus directory."""
    corpus_dir.mkdir(parents=True, exist_ok=True)
    target = corpus_dir / filename
    with open(target, "wb") as f:
        f.write(content)
    return target
