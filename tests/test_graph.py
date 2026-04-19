"""Tests for graph construction and analysis."""

from __future__ import annotations

from myelinate.graph import build_graph, cluster, get_god_nodes
from myelinate.models import Confidence, Edge, Extraction, Node


def _sample_extraction() -> Extraction:
    return Extraction(
        source_file="test.py",
        nodes=[
            Node(id="a", label="Attention", source_file="test.py"),
            Node(id="b", label="Transformer", source_file="test.py"),
            Node(id="c", label="Encoder", source_file="test.py"),
        ],
        edges=[
            Edge(source="a", target="b", relation="used_by", confidence=Confidence.EXTRACTED),
            Edge(source="b", target="c", relation="contains", confidence=Confidence.INFERRED),
        ],
    )


class TestBuildGraph:
    def test_creates_nodes(self) -> None:
        g = build_graph([_sample_extraction()])
        assert g.number_of_nodes() == 3

    def test_creates_edges(self) -> None:
        g = build_graph([_sample_extraction()])
        assert g.number_of_edges() == 2

    def test_node_attributes(self) -> None:
        g = build_graph([_sample_extraction()])
        assert g.nodes["a"]["label"] == "Attention"

    def test_edge_attributes(self) -> None:
        g = build_graph([_sample_extraction()])
        data = g.edges["a", "b"]
        assert data["relation"] == "used_by"
        assert data["confidence"] == "EXTRACTED"

    def test_empty_extractions(self) -> None:
        g = build_graph([])
        assert g.number_of_nodes() == 0

    def test_merges_multiple_extractions(self) -> None:
        ext1 = Extraction(
            source_file="a.py",
            nodes=[Node(id="x", label="X", source_file="a.py")],
            edges=[],
        )
        ext2 = Extraction(
            source_file="b.py",
            nodes=[Node(id="y", label="Y", source_file="b.py")],
            edges=[Edge(source="x", target="y", relation="calls")],
        )
        g = build_graph([ext1, ext2])
        assert g.number_of_nodes() == 2
        assert g.number_of_edges() == 1


class TestCluster:
    def test_assigns_community(self) -> None:
        g = build_graph([_sample_extraction()])
        g = cluster(g)
        for node in g.nodes:
            assert "community" in g.nodes[node]

    def test_single_node(self) -> None:
        ext = Extraction(
            source_file="s.py",
            nodes=[Node(id="solo", label="Solo", source_file="s.py")],
            edges=[],
        )
        g = build_graph([ext])
        g = cluster(g)
        assert g.nodes["solo"]["community"] == 0


class TestGodNodes:
    def test_returns_highest_degree(self) -> None:
        g = build_graph([_sample_extraction()])
        gods = get_god_nodes(g, top_n=1)
        assert len(gods) == 1
        # "b" (Transformer) has degree 2, highest
        assert gods[0]["id"] == "b"
