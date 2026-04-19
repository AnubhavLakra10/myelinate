"""Tests for export functionality."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from myelinate.export import export_html, export_json, export_obsidian, export_report
from myelinate.graph import build_graph
from myelinate.models import Confidence, Edge, Extraction, Node

if TYPE_CHECKING:
    from pathlib import Path


def _sample_graph():
    ext = Extraction(
        source_file="test.py",
        nodes=[
            Node(id="a", label="Attention", source_file="test.py"),
            Node(id="b", label="Transformer", source_file="test.py"),
        ],
        edges=[
            Edge(source="a", target="b", relation="used_by", confidence=Confidence.EXTRACTED),
        ],
    )
    return build_graph([ext])


class TestExportJSON:
    def test_creates_file(self, tmp_output: Path) -> None:
        g = _sample_graph()
        path = export_json(g, tmp_output)
        assert path.exists()

    def test_valid_json(self, tmp_output: Path) -> None:
        g = _sample_graph()
        path = export_json(g, tmp_output)
        data = json.loads(path.read_text())
        assert "nodes" in data
        assert "edges" in data or "links" in data


class TestExportHTML:
    def test_creates_file(self, tmp_output: Path) -> None:
        g = _sample_graph()
        path = export_html(g, tmp_output)
        assert path.exists()

    def test_contains_vis_js(self, tmp_output: Path) -> None:
        g = _sample_graph()
        path = export_html(g, tmp_output)
        content = path.read_text()
        assert "vis-network" in content


class TestExportObsidian:
    def test_creates_vault(self, tmp_output: Path) -> None:
        g = _sample_graph()
        vault = export_obsidian(g, tmp_output)
        assert vault.is_dir()

    def test_creates_node_files(self, tmp_output: Path) -> None:
        g = _sample_graph()
        vault = export_obsidian(g, tmp_output)
        md_files = list(vault.glob("*.md"))
        assert len(md_files) == 2


class TestExportReport:
    def test_creates_report(self, tmp_output: Path) -> None:
        g = _sample_graph()
        analysis = {
            "god_nodes": [{"id": "b", "label": "Transformer", "degree": 1}],
            "communities": 1,
            "surprising_connections": [],
            "knowledge_gaps": [],
            "suggested_questions": [],
            "stats": {"nodes": 2, "edges": 1, "density": 1.0, "components": 1},
        }
        path = export_report(g, analysis, tmp_output)
        assert path.exists()
        content = path.read_text()
        assert "Transformer" in content
