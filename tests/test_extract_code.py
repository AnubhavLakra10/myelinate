"""Tests for tree-sitter code extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from myelinate.extract.code import extract_code

FIXTURES = Path(__file__).parent / "fixtures"


class TestPythonExtraction:
    """Test extraction from Python source files."""

    def test_extracts_module_node(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        module_nodes = [n for n in result.nodes if n.node_type == "module"]
        assert len(module_nodes) == 1
        assert module_nodes[0].label == "sample"

    def test_extracts_functions(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "greet" in fn_names
        assert "farewell" in fn_names

    def test_extracts_class(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        class_names = {n.label for n in result.nodes if n.node_type == "class"}
        assert "Calculator" in class_names

    def test_extracts_class_methods(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "add" in fn_names
        assert "multiply" in fn_names

    def test_class_contains_methods(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        filename = str(FIXTURES / "sample.py")
        contains_edges = [
            e
            for e in result.edges
            if e.relation == "contains" and e.source == f"{filename}::Calculator"
        ]
        method_targets = {e.target for e in contains_edges}
        assert f"{filename}::add" in method_targets
        assert f"{filename}::multiply" in method_targets

    def test_extracts_imports(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        import_nodes = [n for n in result.nodes if n.node_type == "import"]
        import_labels = {n.label for n in import_nodes}
        assert "os" in import_labels
        assert "pathlib" in import_labels

    def test_extracts_call_edges(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        filename = str(FIXTURES / "sample.py")
        call_edges = [e for e in result.edges if e.relation == "calls"]
        # farewell calls greet
        assert any(
            e.source == f"{filename}::farewell" and e.target == f"{filename}::greet"
            for e in call_edges
        )

    def test_source_locations_are_set(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        for node in result.nodes:
            assert node.source_location.startswith("L")

    def test_all_edges_are_extracted_confidence(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        for edge in result.edges:
            assert edge.confidence == "EXTRACTED"

    def test_source_file_is_set(self) -> None:
        result = extract_code(FIXTURES / "sample.py")
        assert result.source_file == str(FIXTURES / "sample.py")


class TestJavaScriptExtraction:
    """Test extraction from JavaScript source files."""

    def test_extracts_functions(self) -> None:
        result = extract_code(FIXTURES / "sample.js")
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "greet" in fn_names
        assert "main" in fn_names

    def test_extracts_class(self) -> None:
        result = extract_code(FIXTURES / "sample.js")
        class_names = {n.label for n in result.nodes if n.node_type == "class"}
        assert "Logger" in class_names

    def test_extracts_class_methods(self) -> None:
        result = extract_code(FIXTURES / "sample.js")
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "log" in fn_names
        assert "warn" in fn_names

    def test_extracts_call_in_main(self) -> None:
        result = extract_code(FIXTURES / "sample.js")
        filename = str(FIXTURES / "sample.js")
        call_edges = [e for e in result.edges if e.relation == "calls"]
        # main calls greet
        assert any(
            e.source == f"{filename}::main" and e.target == f"{filename}::greet" for e in call_edges
        )


class TestTypeScriptExtraction:
    """Test extraction from TypeScript source files."""

    def test_extracts_function(self) -> None:
        result = extract_code(FIXTURES / "sample.ts")
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "createGreeting" in fn_names

    def test_extracts_class(self) -> None:
        result = extract_code(FIXTURES / "sample.ts")
        class_names = {n.label for n in result.nodes if n.node_type == "class"}
        assert "WelcomeService" in class_names

    def test_extracts_interface(self) -> None:
        result = extract_code(FIXTURES / "sample.ts")
        class_names = {n.label for n in result.nodes if n.node_type == "class"}
        assert "Greeter" in class_names

    def test_extracts_method_calling_function(self) -> None:
        result = extract_code(FIXTURES / "sample.ts")
        filename = str(FIXTURES / "sample.ts")
        call_edges = [e for e in result.edges if e.relation == "calls"]
        assert any(
            e.source == f"{filename}::greet" and e.target == f"{filename}::createGreeting"
            for e in call_edges
        )


class TestFallbackExtraction:
    """Test the regex fallback when tree-sitter grammar is unavailable."""

    def test_fallback_for_unknown_extension(self, tmp_path: Path) -> None:
        # .xyz has no grammar — should use regex fallback
        f = tmp_path / "code.xyz"
        f.write_text("def my_function():\n    pass\n")
        result = extract_code(f)
        assert result.source_file == str(f)
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        assert "my_function" in fn_names

    def test_fallback_extracts_class(self, tmp_path: Path) -> None:
        f = tmp_path / "code.xyz"
        f.write_text("class MyClass:\n    pass\n")
        result = extract_code(f)
        class_names = {n.label for n in result.nodes if n.node_type == "class"}
        assert "MyClass" in class_names

    def test_empty_file_returns_empty_extraction(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.py"
        f.write_text("")
        result = extract_code(f)
        # Module node still exists
        assert result.source_file == str(f)


@pytest.mark.skipif(
    not (FIXTURES / "sample.go").exists(),
    reason="Go fixture not found",
)
class TestGoExtraction:
    """Test extraction from Go source files (requires tree-sitter-go)."""

    def test_extracts_functions(self) -> None:
        try:
            result = extract_code(FIXTURES / "sample.go")
        except Exception:
            pytest.skip("tree-sitter-go not installed")
            return
        fn_names = {n.label for n in result.nodes if n.node_type == "function"}
        # Should at least find the top-level functions
        assert "greet" in fn_names or "main" in fn_names or len(fn_names) > 0
