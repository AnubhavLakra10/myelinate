"""Tests for the CLI entry point."""

from __future__ import annotations

from click.testing import CliRunner

from myelinate.cli import main


class TestCLI:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "knowledge graph" in result.output.lower()

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_ingest_with_valid_path(self, tmp_corpus) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["ingest", str(tmp_corpus)])
        assert result.exit_code == 0
        assert "Found" in result.output

    def test_ingest_nonexistent_path(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["ingest", "/nonexistent/path"])
        assert result.exit_code != 0
