"""Code extraction via tree-sitter AST parsing."""

from __future__ import annotations

import importlib
import logging
import re
from typing import TYPE_CHECKING

import tree_sitter as ts

from myelinate.models import Confidence, Edge, Extraction, Node

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

# Maps file extensions to (package_name, language_func_or_attr).
# language_func_or_attr is the callable that returns a language pointer.
# For TypeScript, the package exposes language_typescript() and language_tsx().
LANG_REGISTRY: dict[str, tuple[str, str]] = {
    ".py": ("tree_sitter_python", "language"),
    ".js": ("tree_sitter_javascript", "language"),
    ".ts": ("tree_sitter_typescript", "language_typescript"),
    ".tsx": ("tree_sitter_typescript", "language_tsx"),
    ".go": ("tree_sitter_go", "language"),
    ".rs": ("tree_sitter_rust", "language"),
    ".java": ("tree_sitter_java", "language"),
    ".c": ("tree_sitter_c", "language"),
    ".cpp": ("tree_sitter_cpp", "language"),
    ".rb": ("tree_sitter_ruby", "language"),
    ".cs": ("tree_sitter_c_sharp", "language"),
    ".kt": ("tree_sitter_kotlin", "language"),
    ".scala": ("tree_sitter_scala", "language"),
    ".php": ("tree_sitter_php", "language_php"),
}

# AST node types that represent function/method definitions, per language family.
_FUNCTION_TYPES = frozenset(
    {
        "function_definition",  # Python, PHP
        "function_declaration",  # JS, Go, C, C++
        "method_definition",  # JS, TS (class methods)
        "method_declaration",  # Java, C#, Kotlin
        "function_item",  # Rust (fn)
        "arrow_function",  # JS/TS (only when assigned to a variable)
        "function_def",  # Scala
    }
)

_CLASS_TYPES = frozenset(
    {
        "class_definition",  # Python
        "class_declaration",  # JS, TS, Java, C#, Kotlin, PHP
        "struct_item",  # Rust
        "struct_specifier",  # C/C++
        "type_declaration",  # Go
        "interface_declaration",  # TS, Java, C#, Kotlin
        "object_declaration",  # Scala, Kotlin
        "class_def",  # Scala
        "trait_item",  # Rust
        "enum_item",  # Rust
    }
)

_IMPORT_TYPES = frozenset(
    {
        "import_statement",  # Python, JS, TS, Java, Kotlin, Scala
        "import_from_statement",  # Python
        "import_declaration",  # Go
        "use_declaration",  # Rust
        "preproc_include",  # C/C++
        "using_directive",  # C#
        "namespace_use_declaration",  # PHP
    }
)

_CALL_TYPES = frozenset(
    {
        "call",  # Python
        "call_expression",  # JS, TS, Go, Rust, Java, C, C++, C#, Kotlin, PHP
    }
)


def _load_language(ext: str) -> ts.Language | None:
    """Load a tree-sitter language for the given file extension."""
    entry = LANG_REGISTRY.get(ext)
    if entry is None:
        return None
    pkg_name, func_name = entry
    try:
        mod = importlib.import_module(pkg_name)
        lang_func = getattr(mod, func_name)
        return ts.Language(lang_func())
    except (ImportError, AttributeError, OSError):
        logger.debug("tree-sitter grammar not available for %s", ext)
        return None


def _node_name(node: ts.Node) -> str:
    """Extract the name identifier from an AST node."""
    # Most languages use a 'name' field for functions/classes.
    name_node = node.child_by_field_name("name")
    if name_node is not None:
        return name_node.text.decode()

    # Arrow functions assigned to variables: look at the parent variable_declarator.
    if node.type == "arrow_function" and node.parent is not None:
        parent = node.parent
        if parent.type == "variable_declarator":
            id_node = parent.child_by_field_name("name")
            if id_node is not None:
                return id_node.text.decode()

    return ""


def _classify_node(node_type: str) -> str:
    """Classify an AST node type into our schema categories."""
    if node_type in _FUNCTION_TYPES:
        return "function"
    if node_type in _CLASS_TYPES:
        return "class"
    if node_type in _IMPORT_TYPES:
        return "import"
    return "unknown"


def _extract_import_target(node: ts.Node) -> str:
    """Extract the module/package name from an import node."""
    # Python: import_from_statement has a 'module_name' field
    mod = node.child_by_field_name("module_name")
    if mod is not None:
        return mod.text.decode()

    # General approach: find the first string or dotted_name child
    for child in node.children:
        if child.type in (
            "dotted_name",
            "string",
            "identifier",
            "scoped_identifier",
            "package_identifier",
        ):
            text = child.text.decode().strip("'\"")
            if text not in ("import", "from", "use", "require"):
                return text

    # Fallback: grab the whole node text minus keywords
    raw = node.text.decode()
    raw = re.sub(r"^(import|from|use|require|include|using|namespace)\s+", "", raw)
    raw = raw.split()[0] if raw.split() else raw
    return raw.strip(";'\"")


def _walk_tree(
    node: ts.Node,
    filename: str,
    nodes: list[Node],
    edges: list[Edge],
    parent_id: str | None = None,
    parent_fn: str | None = None,
) -> None:
    """Recursively walk the AST and extract nodes and edges."""
    category = _classify_node(node.type)
    line = node.start_point.row + 1  # 1-indexed

    if category == "function":
        name = _node_name(node)
        if not name:
            # Skip anonymous functions that aren't assigned
            for child in node.children:
                _walk_tree(child, filename, nodes, edges, parent_id, parent_fn)
            return

        node_id = f"{filename}::{name}"
        nodes.append(
            Node(
                id=node_id,
                label=name,
                source_file=filename,
                source_location=f"L{line}",
                node_type="function",
            )
        )

        if parent_id is not None:
            edges.append(
                Edge(
                    source=parent_id,
                    target=node_id,
                    relation="contains",
                    confidence=Confidence.EXTRACTED,
                )
            )

        # Recurse into the function body to find calls
        for child in node.children:
            _walk_tree(child, filename, nodes, edges, parent_id, name)
        return

    if category == "class":
        name = _node_name(node)
        if not name:
            for child in node.children:
                _walk_tree(child, filename, nodes, edges, parent_id, parent_fn)
            return

        node_id = f"{filename}::{name}"
        nodes.append(
            Node(
                id=node_id,
                label=name,
                source_file=filename,
                source_location=f"L{line}",
                node_type="class",
            )
        )

        # Recurse with this class as the parent
        for child in node.children:
            _walk_tree(child, filename, nodes, edges, node_id, parent_fn)
        return

    if category == "import":
        target = _extract_import_target(node)
        if target:
            node_id = f"{filename}::import::{target}"
            nodes.append(
                Node(
                    id=node_id,
                    label=target,
                    source_file=filename,
                    source_location=f"L{line}",
                    node_type="import",
                )
            )
            edges.append(
                Edge(
                    source=filename,
                    target=node_id,
                    relation="imports",
                    confidence=Confidence.EXTRACTED,
                )
            )
        for child in node.children:
            _walk_tree(child, filename, nodes, edges, parent_id, parent_fn)
        return

    # Check for call expressions
    if node.type in _CALL_TYPES and parent_fn is not None:
        fn_node = node.child_by_field_name("function")
        if fn_node is not None:
            call_name = fn_node.text.decode()
            # Only track simple calls (not chained method calls with dots)
            if "." not in call_name:
                caller_id = f"{filename}::{parent_fn}"
                callee_id = f"{filename}::{call_name}"
                edges.append(
                    Edge(
                        source=caller_id,
                        target=callee_id,
                        relation="calls",
                        confidence=Confidence.EXTRACTED,
                    )
                )

    # Default: recurse into children
    for child in node.children:
        _walk_tree(child, filename, nodes, edges, parent_id, parent_fn)


def _fallback_extract(path: Path) -> Extraction:
    """Basic regex fallback when tree-sitter grammar is unavailable."""
    filename = str(path)
    nodes: list[Node] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return Extraction(source_file=filename)

    # Simple regex for common function/class patterns
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        # Python/Ruby: def name
        match = re.match(r"(?:def|fn|func|function)\s+(\w+)", stripped)
        if match:
            name = match.group(1)
            nodes.append(
                Node(
                    id=f"{filename}::{name}",
                    label=name,
                    source_file=filename,
                    source_location=f"L{i}",
                    node_type="function",
                )
            )
            continue
        # Class/struct/interface
        match = re.match(r"(?:class|struct|interface|trait|enum)\s+(\w+)", stripped)
        if match:
            name = match.group(1)
            nodes.append(
                Node(
                    id=f"{filename}::{name}",
                    label=name,
                    source_file=filename,
                    source_location=f"L{i}",
                    node_type="class",
                )
            )

    return Extraction(source_file=filename, nodes=nodes)


def extract_code(path: Path) -> Extraction:
    """Extract concepts from source code using tree-sitter AST parsing."""
    filename = str(path)
    ext = path.suffix.lower()

    language = _load_language(ext)
    if language is None:
        return _fallback_extract(path)

    try:
        source = path.read_bytes()
    except OSError:
        logger.warning("Could not read file: %s", path)
        return Extraction(source_file=filename)

    parser = ts.Parser(language)
    tree = parser.parse(source)

    nodes: list[Node] = []
    edges: list[Edge] = []

    # Add a module-level node for the file itself
    nodes.append(
        Node(
            id=filename,
            label=path.stem,
            source_file=filename,
            source_location="L1",
            node_type="module",
        )
    )

    _walk_tree(tree.root_node, filename, nodes, edges)

    return Extraction(source_file=filename, nodes=nodes, edges=edges)
