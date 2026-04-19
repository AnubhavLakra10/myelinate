"""Concept and relationship extraction from files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from myelinate.detect import classify_file
from myelinate.models import Extraction

if TYPE_CHECKING:
    from pathlib import Path


def extract(path: Path) -> Extraction:
    """Extract concepts and relationships from a single file.

    Dispatches to the appropriate extractor based on file type:
    - code: tree-sitter AST parsing
    - doc: Claude LLM extraction
    - paper: PDF parsing + Claude extraction
    - image: Claude vision
    """
    file_type = classify_file(path)
    match file_type:
        case "code":
            return extract_code(path)
        case "doc":
            return extract_doc(path)
        case "paper":
            return extract_paper(path)
        case "image":
            return extract_image(path)
        case _:
            return Extraction(source_file=str(path))


def extract_code(path: Path) -> Extraction:
    """Extract concepts from source code using tree-sitter AST parsing."""
    # TODO: implement tree-sitter extraction
    return Extraction(source_file=str(path))


def extract_doc(path: Path) -> Extraction:
    """Extract concepts from markdown/text documents using Claude."""
    # TODO: implement Claude-based extraction
    return Extraction(source_file=str(path))


def extract_paper(path: Path) -> Extraction:
    """Extract concepts from PDF papers using Claude."""
    # TODO: implement PDF extraction
    return Extraction(source_file=str(path))


def extract_image(path: Path) -> Extraction:
    """Extract concepts from images using Claude vision."""
    # TODO: implement vision extraction
    return Extraction(source_file=str(path))
