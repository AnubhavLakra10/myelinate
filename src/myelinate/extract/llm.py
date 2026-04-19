"""Shared Claude API client for LLM-based extraction."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import anthropic

from myelinate.models import Confidence, Edge, Extraction, Node

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 4096

_EXTRACTION_SCHEMA = """\
Return a JSON object with exactly this structure (no markdown fences, pure JSON):
{
  "nodes": [
    {
      "id": "<unique_id>",
      "label": "<human-readable name>",
      "node_type": "<concept|term|technique|entity|section>"
    }
  ],
  "edges": [
    {
      "source": "<node_id>",
      "target": "<node_id>",
      "relation": "<is_a|part_of|uses|related_to|described_by|cites|contains|depends_on>"
    }
  ]
}

Rules:
- node IDs should be lowercase_snake_case derived from the label
- Every edge source and target must reference a node ID from the nodes list
- Extract at least the key concepts; do not extract trivial filler
- Return ONLY valid JSON, no surrounding text"""


def get_client() -> anthropic.Anthropic:
    """Return an Anthropic client, reading the API key from the environment."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        msg = (
            "ANTHROPIC_API_KEY environment variable is required for "
            "document/paper/image extraction. Set it and retry."
        )
        raise RuntimeError(msg)
    return anthropic.Anthropic(api_key=api_key)


def _parse_extraction_json(raw: str, source_file: str, confidence: Confidence) -> Extraction:
    """Parse Claude's JSON response into an Extraction object."""
    # Strip markdown fences if Claude wraps the response
    text = raw.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.index("\n")
        text = text[first_newline + 1 :]
    if text.endswith("```"):
        text = text[: text.rindex("```")]
    text = text.strip()

    data: dict[str, Any] = json.loads(text)

    nodes = [
        Node(
            id=n["id"],
            label=n["label"],
            source_file=source_file,
            node_type=n.get("node_type", "concept"),
        )
        for n in data.get("nodes", [])
    ]

    edges = [
        Edge(
            source=e["source"],
            target=e["target"],
            relation=e["relation"],
            confidence=confidence,
        )
        for e in data.get("edges", [])
    ]

    return Extraction(source_file=source_file, nodes=nodes, edges=edges)


def extract_with_claude(
    content: list[dict[str, Any]],
    system_prompt: str,
    source_file: str,
    confidence: Confidence = Confidence.INFERRED,
) -> Extraction:
    """Send content to Claude and parse the structured extraction response.

    Args:
        content: Message content blocks (text, image, or document).
        system_prompt: The system prompt describing what to extract.
        source_file: Path of the file being extracted.
        confidence: Confidence level to assign to all edges.

    Returns:
        Extraction with nodes and edges parsed from Claude's response.
    """
    try:
        client = get_client()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )

        raw_text = response.content[0].text
        return _parse_extraction_json(raw_text, source_file, confidence)

    except RuntimeError:
        # No API key — propagate so callers know extraction isn't available
        raise
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.warning("Failed to parse Claude response for %s: %s", source_file, exc)
        return Extraction(source_file=source_file)
    except anthropic.APIError as exc:
        logger.warning("Claude API error for %s: %s", source_file, exc)
        return Extraction(source_file=source_file)
