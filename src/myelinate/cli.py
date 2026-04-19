"""CLI entry point for myelinate."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """Drop files. Build a knowledge graph. Learn with spaced repetition."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--update", is_flag=True, help="Only process changed files.")
def ingest(path: Path, update: bool) -> None:
    """Add files or directories to the corpus."""
    from myelinate.cache import partition_by_cache
    from myelinate.detect import collect_files

    files = collect_files(path)
    if update:
        files, cached = partition_by_cache(files)
        console.print(f"[dim]{len(cached)} cached, {len(files)} to process[/dim]")

    console.print(f"[green]Found {len(files)} files to ingest.[/green]")


@main.command()
@click.option("--watch", is_flag=True, help="Auto-rebuild on file changes.")
def graph(watch: bool) -> None:
    """Build or rebuild the knowledge graph."""
    console.print("[yellow]Graph building not yet implemented.[/yellow]")


@main.command()
def gaps() -> None:
    """Find knowledge gaps in your graph."""
    console.print("[yellow]Gap detection not yet implemented.[/yellow]")


@main.command()
@click.option("--topic", default=None, help="Quiz on a specific subgraph.")
@click.option("--count", default=10, help="Number of cards per session.")
def quiz(topic: str | None, count: int) -> None:
    """Start a spaced repetition session."""
    console.print("[yellow]Quiz not yet implemented.[/yellow]")


@main.command()
@click.argument("source")
@click.argument("target")
def path(source: str, target: str) -> None:
    """Find the shortest path between two concepts."""
    console.print("[yellow]Path finding not yet implemented.[/yellow]")


@main.command()
@click.argument("concept")
def explain(concept: str) -> None:
    """Explain a concept at your current understanding level."""
    console.print("[yellow]Explain not yet implemented.[/yellow]")


@main.command()
def stats() -> None:
    """Show learning progress dashboard."""
    console.print("[yellow]Stats not yet implemented.[/yellow]")


@main.command()
@click.option("--obsidian", is_flag=True, help="Export as Obsidian vault.")
@click.option("--wiki", is_flag=True, help="Generate wiki articles.")
@click.option("--svg", is_flag=True, help="Export graph.svg.")
@click.option("--neo4j", is_flag=True, help="Generate Cypher for Neo4j.")
def export(obsidian: bool, wiki: bool, svg: bool, neo4j: bool) -> None:
    """Export the knowledge graph."""
    console.print("[yellow]Export not yet implemented.[/yellow]")
