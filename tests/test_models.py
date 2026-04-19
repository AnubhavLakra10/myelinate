"""Tests for data models."""

from __future__ import annotations

from myelinate.models import Confidence, Edge, Extraction, Node, ReviewCard


class TestNode:
    def test_create_minimal(self) -> None:
        node = Node(id="a", label="Attention", source_file="test.py")
        assert node.id == "a"
        assert node.node_type == "concept"

    def test_defaults(self) -> None:
        node = Node(id="a", label="A", source_file="f.py")
        assert node.source_location == ""
        assert node.node_type == "concept"


class TestEdge:
    def test_create_with_defaults(self) -> None:
        edge = Edge(source="a", target="b", relation="calls")
        assert edge.confidence == Confidence.EXTRACTED
        assert edge.weight == 1.0

    def test_confidence_values(self) -> None:
        for conf in Confidence:
            edge = Edge(source="a", target="b", relation="x", confidence=conf)
            assert edge.confidence == conf


class TestExtraction:
    def test_empty_extraction(self) -> None:
        ext = Extraction(source_file="test.py")
        assert ext.nodes == []
        assert ext.edges == []

    def test_with_data(self) -> None:
        ext = Extraction(
            source_file="test.py",
            nodes=[Node(id="a", label="A", source_file="test.py")],
            edges=[Edge(source="a", target="b", relation="uses")],
        )
        assert len(ext.nodes) == 1
        assert len(ext.edges) == 1


class TestReviewCard:
    def test_defaults(self) -> None:
        card = ReviewCard(
            card_id="c1",
            question="What?",
            answer="That.",
            source_edge="a->b",
        )
        assert card.difficulty == 0.3
        assert card.stability == 1.0
        assert card.reps == 0
