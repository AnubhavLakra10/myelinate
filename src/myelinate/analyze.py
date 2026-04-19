"""Graph analysis — god nodes, gaps, surprising connections."""

from __future__ import annotations

from typing import Any

import networkx as nx

from myelinate.graph import get_god_nodes


def analyze(g: nx.Graph) -> dict[str, Any]:
    """Run full analysis on the knowledge graph."""
    return {
        "god_nodes": get_god_nodes(g),
        "communities": count_communities(g),
        "surprising_connections": find_surprising_connections(g),
        "knowledge_gaps": find_gaps(g),
        "suggested_questions": suggest_questions(g),
        "stats": graph_stats(g),
    }


def count_communities(g: nx.Graph) -> int:
    """Count the number of distinct communities in the graph."""
    communities = {g.nodes[n].get("community", 0) for n in g.nodes}
    return len(communities)


def find_surprising_connections(g: nx.Graph, top_n: int = 10) -> list[dict[str, Any]]:
    """Find edges that connect different communities or file types."""
    surprises: list[dict[str, Any]] = []
    for u, v, data in g.edges(data=True):
        u_comm = g.nodes[u].get("community", 0)
        v_comm = g.nodes[v].get("community", 0)
        u_type = g.nodes[u].get("node_type", "")
        v_type = g.nodes[v].get("node_type", "")

        score = 0.0
        if u_comm != v_comm:
            score += 2.0
        if u_type != v_type:
            score += 1.0

        if score > 0:
            surprises.append(
                {
                    "source": u,
                    "target": v,
                    "score": score,
                    "relation": data.get("relation", ""),
                }
            )

    surprises.sort(key=lambda x: x["score"], reverse=True)
    return surprises[:top_n]


def find_gaps(g: nx.Graph) -> list[dict[str, Any]]:
    """Identify potential knowledge gaps — loosely connected subgraphs."""
    # TODO: implement gap detection via bridge/cut vertex analysis
    return []


def suggest_questions(g: nx.Graph) -> list[str]:
    """Generate questions the graph is uniquely positioned to answer."""
    # TODO: implement question generation from graph topology
    return []


def graph_stats(g: nx.Graph) -> dict[str, Any]:
    """Basic statistics about the graph."""
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "density": nx.density(g) if g.number_of_nodes() > 1 else 0.0,
        "components": nx.number_connected_components(g) if g.number_of_nodes() > 0 else 0,
    }
