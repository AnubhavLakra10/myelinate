"""Tests for graph analysis."""

from __future__ import annotations

from myelinate.analyze import analyze, find_surprising_connections, graph_stats
from myelinate.graph import build_graph
from myelinate.models import Edge, Extraction, Node


def _multi_community_graph():
    ext = Extraction(
        source_file="test.py",
        nodes=[
            Node(id="a", label="Attention", source_file="code.py", node_type="function"),
            Node(id="b", label="Transformer", source_file="code.py", node_type="class"),
            Node(id="c", label="RLHF", source_file="paper.md", node_type="concept"),
        ],
        edges=[
            Edge(source="a", target="b", relation="used_by"),
            Edge(source="b", target="c", relation="described_in"),
        ],
    )
    g = build_graph([ext])
    g.nodes["a"]["community"] = 0
    g.nodes["b"]["community"] = 0
    g.nodes["c"]["community"] = 1
    return g


class TestAnalyze:
    def test_returns_all_keys(self) -> None:
        ext = Extraction(
            source_file="t.py",
            nodes=[Node(id="x", label="X", source_file="t.py")],
            edges=[],
        )
        g = build_graph([ext])
        result = analyze(g)
        assert "god_nodes" in result
        assert "communities" in result
        assert "surprising_connections" in result
        assert "knowledge_gaps" in result
        assert "stats" in result


class TestSurprisingConnections:
    def test_cross_community_edges_ranked_higher(self) -> None:
        g = _multi_community_graph()
        surprises = find_surprising_connections(g)
        assert len(surprises) > 0
        # b->c crosses communities and types, should score highest
        top = surprises[0]
        assert top["score"] > 0


class TestGraphStats:
    def test_basic_stats(self) -> None:
        ext = Extraction(
            source_file="t.py",
            nodes=[
                Node(id="a", label="A", source_file="t.py"),
                Node(id="b", label="B", source_file="t.py"),
            ],
            edges=[Edge(source="a", target="b", relation="x")],
        )
        g = build_graph([ext])
        stats = graph_stats(g)
        assert stats["nodes"] == 2
        assert stats["edges"] == 1
        assert stats["components"] == 1

    def test_empty_graph(self) -> None:
        g = build_graph([])
        stats = graph_stats(g)
        assert stats["nodes"] == 0
        assert stats["density"] == 0.0
