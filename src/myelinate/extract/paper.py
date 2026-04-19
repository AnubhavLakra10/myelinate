"""PDF paper extraction via Claude."""

from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from myelinate.extract.llm import extract_with_claude
from myelinate.models import Confidence, Extraction

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a knowledge extraction engine for academic and technical papers.

Extract concepts and their relationships from the PDF document below.

Return nodes for: key concepts, theorems, methods, algorithms, datasets, \
metrics, authors/researchers (when central to the content), and technical terms.

Return edges for relationships like: is_a, part_of, uses, related_to, \
described_by, depends_on, cites, improves_on, evaluated_on, contains.

Focus on the paper's core contributions and methodology. Skip boilerplate \
(acknowledgments, formatting, page numbers).

"""


def extract_paper(path: Path) -> Extraction:
    """Extract concepts from a PDF paper using Claude."""
    filename = str(path)

    try:
        pdf_bytes = path.read_bytes()
    except OSError:
        logger.warning("Could not read file: %s", path)
        return Extraction(source_file=filename)

    if not pdf_bytes:
        return Extraction(source_file=filename)

    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("ascii")

    content = [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": pdf_b64,
            },
        },
        {
            "type": "text",
            "text": "Extract the key concepts and relationships from this paper.",
        },
    ]

    return extract_with_claude(
        content=content,
        system_prompt=_SYSTEM_PROMPT,
        source_file=filename,
        confidence=Confidence.INFERRED,
    )
