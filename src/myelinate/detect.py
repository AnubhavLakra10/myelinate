"""File discovery and filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

CODE_EXTENSIONS = frozenset(
    {
        ".py",
        ".ts",
        ".js",
        ".go",
        ".rs",
        ".java",
        ".c",
        ".cpp",
        ".rb",
        ".cs",
        ".kt",
        ".scala",
        ".php",
    }
)

DOC_EXTENSIONS = frozenset({".md", ".txt", ".rst"})

PAPER_EXTENSIONS = frozenset({".pdf"})

IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif"})

ALL_EXTENSIONS = CODE_EXTENSIONS | DOC_EXTENSIONS | PAPER_EXTENSIONS | IMAGE_EXTENSIONS

IGNORED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".eggs",
        "myelinate-out",
    }
)


def collect_files(root: Path) -> list[Path]:
    """Collect all supported files under root, skipping ignored directories."""
    if root.is_file():
        return [root] if root.suffix in ALL_EXTENSIONS else []

    files: list[Path] = []
    for item in sorted(root.rglob("*")):
        if any(part in IGNORED_DIRS for part in item.parts):
            continue
        if item.is_file() and item.suffix in ALL_EXTENSIONS:
            files.append(item)
    return files


def classify_file(path: Path) -> str:
    """Return the file category: 'code', 'doc', 'paper', 'image', or 'unknown'."""
    suffix = path.suffix.lower()
    if suffix in CODE_EXTENSIONS:
        return "code"
    if suffix in DOC_EXTENSIONS:
        return "doc"
    if suffix in PAPER_EXTENSIONS:
        return "paper"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    return "unknown"
