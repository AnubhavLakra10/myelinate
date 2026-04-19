"""Image extraction via Claude Vision."""

from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from myelinate.extract.llm import extract_with_claude
from myelinate.models import Confidence, Extraction

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_MEDIA_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

_SYSTEM_PROMPT = """\
You are a knowledge extraction engine for visual content.

Describe the concepts, entities, and relationships shown in this \
image, diagram, screenshot, or illustration.

Return nodes for: key concepts, entities, components, labels, and terms visible \
or implied in the image.

Return edges for relationships like: is_a, part_of, uses, related_to, \
described_by, connects_to, contains, flows_to.

Focus on meaningful information — skip decorative elements and background noise.

"""


def extract_image(path: Path) -> Extraction:
    """Extract concepts from an image using Claude Vision."""
    filename = str(path)
    ext = path.suffix.lower()

    media_type = _MEDIA_TYPES.get(ext)
    if media_type is None:
        logger.warning("Unsupported image format: %s", ext)
        return Extraction(source_file=filename)

    try:
        image_bytes = path.read_bytes()
    except OSError:
        logger.warning("Could not read file: %s", path)
        return Extraction(source_file=filename)

    if not image_bytes:
        return Extraction(source_file=filename)

    image_b64 = base64.standard_b64encode(image_bytes).decode("ascii")

    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_b64,
            },
        },
        {
            "type": "text",
            "text": "Extract the key concepts and relationships from this image.",
        },
    ]

    return extract_with_claude(
        content=content,
        system_prompt=_SYSTEM_PROMPT,
        source_file=filename,
        confidence=Confidence.INFERRED,
    )
