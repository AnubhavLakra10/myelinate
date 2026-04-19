"""Export knowledge graph to various formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

OUTPUT_DIR = Path("myelinate-out")


def export_json(g: nx.Graph, out_dir: Path | None = None) -> Path:
    """Export graph as JSON."""
    target = (out_dir or OUTPUT_DIR) / "graph.json"
    target.parent.mkdir(parents=True, exist_ok=True)

    data = nx.node_link_data(g)
    with open(target, "w") as f:
        json.dump(data, f, indent=2)
    return target


def export_html(g: nx.Graph, out_dir: Path | None = None) -> Path:
    """Export interactive HTML visualization using vis.js."""
    target = (out_dir or OUTPUT_DIR) / "graph.html"
    target.parent.mkdir(parents=True, exist_ok=True)

    nodes_js = json.dumps(
        [
            {
                "id": n,
                "label": g.nodes[n].get("label", n),
                "group": g.nodes[n].get("community", 0),
            }
            for n in g.nodes
        ]
    )
    edges_js = json.dumps(
        [
            {
                "from": u,
                "to": v,
                "label": d.get("relation", ""),
                "title": d.get("confidence", ""),
            }
            for u, v, d in g.edges(data=True)
        ]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>myelinate — knowledge graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; font-family: system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; }}
  #graph {{ width: 100vw; height: 100vh; }}
  #search {{ position: fixed; top: 16px; left: 16px; padding: 8px 12px;
    background: #1a1a1a; border: 1px solid #333; color: #e0e0e0;
    border-radius: 6px; font-size: 14px; width: 240px; z-index: 10; }}
  #search::placeholder {{ color: #666; }}
</style>
</head>
<body>
<input id="search" type="text" placeholder="Search concepts...">
<div id="graph"></div>
<script>
const nodes = new vis.DataSet({nodes_js});
const edges = new vis.DataSet({edges_js});
const container = document.getElementById("graph");
const network = new vis.Network(container, {{ nodes, edges }}, {{
  nodes: {{ shape: "dot", size: 16, font: {{ color: "#e0e0e0", size: 12 }} }},
  edges: {{ color: {{ color: "#444" }}, font: {{ color: "#888", size: 10 }} }},
  physics: {{ solver: "forceAtlas2Based", forceAtlas2Based: {{ gravitationalConstant: -30 }} }},
}});
document.getElementById("search").addEventListener("input", function(e) {{
  const q = e.target.value.toLowerCase();
  nodes.forEach(n => {{
    nodes.update({{ id: n.id, opacity: !q || n.label.toLowerCase().includes(q) ? 1 : 0.15 }});
  }});
}});
</script>
</body>
</html>"""

    with open(target, "w") as f:
        f.write(html)
    return target


def export_obsidian(g: nx.Graph, out_dir: Path | None = None) -> Path:
    """Export graph as an Obsidian vault with linked markdown files."""
    vault_dir = (out_dir or OUTPUT_DIR) / "obsidian"
    vault_dir.mkdir(parents=True, exist_ok=True)

    for node_id in g.nodes:
        data = g.nodes[node_id]
        label = data.get("label", node_id)
        neighbors = list(g.neighbors(node_id))

        links = "\n".join(f"- [[{g.nodes[n].get('label', n)}]]" for n in neighbors)
        content = f"# {label}\n\n"
        content += f"**Source:** {data.get('source_file', 'unknown')}\n"
        content += f"**Type:** {data.get('node_type', 'concept')}\n\n"
        if links:
            content += f"## Connections\n\n{links}\n"

        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in label)
        with open(vault_dir / f"{safe_name}.md", "w") as f:
            f.write(content)

    return vault_dir


def export_report(
    g: nx.Graph,
    analysis: dict[str, Any],
    out_dir: Path | None = None,
) -> Path:
    """Generate REPORT.md from graph analysis."""
    target = (out_dir or OUTPUT_DIR) / "REPORT.md"
    target.parent.mkdir(parents=True, exist_ok=True)

    stats = analysis.get("stats", {})
    lines = [
        "# myelinate — Knowledge Graph Report\n",
        f"**Nodes:** {stats.get('nodes', 0)} | "
        f"**Edges:** {stats.get('edges', 0)} | "
        f"**Communities:** {analysis.get('communities', 0)} | "
        f"**Density:** {stats.get('density', 0):.4f}\n",
        "## God Nodes\n",
    ]

    for gn in analysis.get("god_nodes", []):
        lines.append(f"- **{gn.get('label', gn['id'])}** (degree: {gn['degree']})")

    lines.append("\n## Surprising Connections\n")
    for sc in analysis.get("surprising_connections", []):
        lines.append(
            f"- {sc['source']} -- {sc['relation']} --> {sc['target']} (score: {sc['score']:.1f})"
        )

    lines.append("\n## Knowledge Gaps\n")
    gaps = analysis.get("knowledge_gaps", [])
    if gaps:
        for gap in gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("_No gaps detected yet._")

    lines.append("")
    with open(target, "w") as f:
        f.write("\n".join(lines))
    return target
