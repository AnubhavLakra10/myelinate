"""Document extraction via Claude for markdown, text, and RST files."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from myelinate.extract.llm import extract_with_claude
from myelinate.models import Confidence, Extraction

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a knowledge extraction engine. Extract concepts and their relationships \
from the document below.

Return nodes for: key concepts, ideas, terms, techniques, and named entities.
Return edges for relationships like: is_a, part_of, uses, related_to, described_by, \
depends_on, contains.

Focus on substantive concepts — skip formatting, boilerplate, and trivial filler.

"""


def extract_doc(path: Path) -> Extraction:
    """Extract concepts from a markdown, text, or RST document using Claude."""
    filename = str(path)

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logger.warning("Could not read file: %s", path)
        return Extraction(source_file=filename)

    if not text.strip():
        return Extraction(source_file=filename)

    content = [{"type": "text", "text": text}]

    return extract_with_claude(
        content=content,
        system_prompt=_SYSTEM_PROMPT,
        source_file=filename,
        confidence=Confidence.INFERRED,
    )
