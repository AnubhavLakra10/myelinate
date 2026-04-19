"""Knowledge graph construction and clustering."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import networkx as nx

if TYPE_CHECKING:
    from myelinate.models import Extraction


def build_graph(extractions: list[Extraction]) -> nx.Graph:
    """Build a NetworkX graph from a list of extractions."""
    g = nx.Graph()

    for ext in extractions:
        for node in ext.nodes:
            g.add_node(
                node.id,
                **{
                    "label": node.label,
                    "source_file": node.source_file,
                    "source_location": node.source_location,
                    "node_type": node.node_type,
                },
            )
        for edge in ext.edges:
            g.add_edge(
                edge.source,
                edge.target,
                **{
                    "relation": edge.relation,
                    "confidence": edge.confidence.value,
                    "weight": edge.weight,
                },
            )

    return g


def cluster(g: nx.Graph) -> nx.Graph:
    """Apply Leiden community detection and set community attribute on nodes."""
    if len(g) < 2:
        for node in g.nodes:
            g.nodes[node]["community"] = 0
        return g

    # TODO: implement Leiden clustering via graspologic
    for node in g.nodes:
        g.nodes[node]["community"] = 0
    return g


def get_god_nodes(g: nx.Graph, top_n: int = 10) -> list[dict[str, Any]]:
    """Return the highest-degree nodes in the graph."""
    degree_list = sorted(g.degree(), key=lambda x: x[1], reverse=True)
    return [
        {"id": node_id, "degree": deg, **g.nodes[node_id]} for node_id, deg in degree_list[:top_n]
    ]
