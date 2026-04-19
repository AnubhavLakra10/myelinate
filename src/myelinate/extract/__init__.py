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
            from myelinate.extract.code import extract_code

            return extract_code(path)
        case "doc":
            from myelinate.extract.doc import extract_doc

            return extract_doc(path)
        case "paper":
            from myelinate.extract.paper import extract_paper

            return extract_paper(path)
        case "image":
            from myelinate.extract.image import extract_image

            return extract_image(path)
        case _:
            return Extraction(source_file=str(path))
