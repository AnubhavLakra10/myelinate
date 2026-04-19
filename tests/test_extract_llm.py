"""Tests for the shared LLM extraction client."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from myelinate.extract.llm import (
    _parse_extraction_json,
    extract_with_claude,
    get_client,
)
from myelinate.models import Confidence


class TestGetClient:
    """Test the Claude client factory."""

    def test_raises_without_api_key(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"),
        ):
            get_client()

    def test_returns_client_with_api_key(self) -> None:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            client = get_client()
            assert client is not None


class TestParseExtractionJson:
    """Test JSON response parsing."""

    def test_parses_valid_json(self) -> None:
        raw = json.dumps(
            {
                "nodes": [
                    {"id": "attention", "label": "Attention", "node_type": "concept"},
                    {"id": "transformer", "label": "Transformer", "node_type": "concept"},
                ],
                "edges": [
                    {"source": "transformer", "target": "attention", "relation": "uses"},
                ],
            }
        )
        result = _parse_extraction_json(raw, "test.md", Confidence.INFERRED)
        assert len(result.nodes) == 2
        assert len(result.edges) == 1
        assert result.nodes[0].id == "attention"
        assert result.edges[0].confidence == Confidence.INFERRED
        assert result.source_file == "test.md"

    def test_strips_markdown_fences(self) -> None:
        raw = '```json\n{"nodes": [{"id": "x", "label": "X"}], "edges": []}\n```'
        result = _parse_extraction_json(raw, "test.md", Confidence.INFERRED)
        assert len(result.nodes) == 1
        assert result.nodes[0].id == "x"

    def test_strips_bare_fences(self) -> None:
        raw = '```\n{"nodes": [], "edges": []}\n```'
        result = _parse_extraction_json(raw, "test.md", Confidence.INFERRED)
        assert len(result.nodes) == 0

    def test_handles_empty_nodes_and_edges(self) -> None:
        raw = '{"nodes": [], "edges": []}'
        result = _parse_extraction_json(raw, "test.md", Confidence.INFERRED)
        assert len(result.nodes) == 0
        assert len(result.edges) == 0

    def test_defaults_node_type_to_concept(self) -> None:
        raw = json.dumps(
            {
                "nodes": [{"id": "foo", "label": "Foo"}],
                "edges": [],
            }
        )
        result = _parse_extraction_json(raw, "test.md", Confidence.INFERRED)
        assert result.nodes[0].node_type == "concept"

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises(json.JSONDecodeError):
            _parse_extraction_json("not json at all", "test.md", Confidence.INFERRED)


def _mock_claude_response(text: str) -> MagicMock:
    """Build a mock Anthropic response object."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


class TestExtractWithClaude:
    """Test the full extraction pipeline with mocked API."""

    def test_successful_extraction(self) -> None:
        response_json = json.dumps(
            {
                "nodes": [{"id": "foo", "label": "Foo", "node_type": "concept"}],
                "edges": [{"source": "foo", "target": "foo", "relation": "related_to"}],
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

            result = extract_with_claude(
                content=[{"type": "text", "text": "hello"}],
                system_prompt="Extract concepts.",
                source_file="test.md",
            )

        assert len(result.nodes) == 1
        assert result.nodes[0].label == "Foo"
        assert len(result.edges) == 1

    def test_returns_empty_on_json_error(self) -> None:
        mock_response = _mock_claude_response("this is not json")

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}),
            patch("myelinate.extract.llm.get_client") as mock_get,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_get.return_value = mock_client

            result = extract_with_claude(
                content=[{"type": "text", "text": "hello"}],
                system_prompt="Extract.",
                source_file="test.md",
            )

        assert len(result.nodes) == 0
        assert len(result.edges) == 0

    def test_returns_empty_on_api_error(self) -> None:
        import anthropic

        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}),
            patch("myelinate.extract.llm.get_client") as mock_get,
        ):
            mock_client = MagicMock()
            mock_client.messages.create.side_effect = anthropic.APIError(
                message="rate limited",
                request=MagicMock(),
                body=None,
            )
            mock_get.return_value = mock_client

            result = extract_with_claude(
                content=[{"type": "text", "text": "hello"}],
                system_prompt="Extract.",
                source_file="test.md",
            )

        assert len(result.nodes) == 0

    def test_raises_on_missing_api_key(self) -> None:
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"),
        ):
            extract_with_claude(
                content=[{"type": "text", "text": "hello"}],
                system_prompt="Extract.",
                source_file="test.md",
            )
