"""Tests for document extraction."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from myelinate.extract.doc import extract_doc
from myelinate.models import Confidence

if TYPE_CHECKING:
    from pathlib import Path


def _mock_claude_response(text: str) -> MagicMock:
    """Build a mock Anthropic response object."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


class TestDocExtraction:
    """Test document extraction with mocked Claude API."""

    def test_extracts_concepts_from_markdown(self, tmp_path: Path) -> None:
        doc = tmp_path / "notes.md"
        doc.write_text("# Attention Mechanism\n\nAttention is all you need.\n")

        response_json = json.dumps(
            {
                "nodes": [
                    {"id": "attention", "label": "Attention Mechanism", "node_type": "concept"},
                    {"id": "transformer", "label": "Transformer", "node_type": "concept"},
                ],
                "edges": [
                    {"source": "transformer", "target": "attention", "relation": "uses"},
                ],
            }
        )
        mock_response = _mock_claude_response(response_json)

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}),
            patch("myelinate.extract.llm.get_client") as mock_get,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = extract_doc(doc)

        assert len(result.nodes) == 2
        assert len(result.edges) == 1
        assert result.edges[0].confidence == Confidence.INFERRED
        assert result.source_file == str(doc)

    def test_passes_file_content_to_claude(self, tmp_path: Path) -> None:
        doc = tmp_path / "test.txt"
        doc.write_text("This is my test document content.")

        response_json = json.dumps({"nodes": [], "edges": []})
        mock_response = _mock_claude_response(response_json)

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}),
            patch("myelinate.extract.llm.get_client") as mock_get,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_get.return_value = mock_client

            extract_doc(doc)

            # Verify the file content was passed to the API
            call_args = mock_client.messages.create.call_args
            messages = call_args.kwargs["messages"]
            user_content = messages[0]["content"]
            assert any(
                block.get("text") == "This is my test document content." for block in user_content
            )

    def test_empty_file_returns_empty_extraction(self, tmp_path: Path) -> None:
        doc = tmp_path / "empty.md"
        doc.write_text("")
        result = extract_doc(doc)
        assert len(result.nodes) == 0
        assert len(result.edges) == 0

    def test_unreadable_file_returns_empty_extraction(self, tmp_path: Path) -> None:
        doc = tmp_path / "missing.md"
        result = extract_doc(doc)
        assert len(result.nodes) == 0
        assert len(result.edges) == 0
