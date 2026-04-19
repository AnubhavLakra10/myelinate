"""Tests for file detection and filtering."""

from __future__ import annotations

from pathlib import Path

from myelinate.detect import classify_file, collect_files


class TestCollectFiles:
    def test_collects_python_files(self, tmp_corpus: Path) -> None:
        files = collect_files(tmp_corpus)
        py_files = [f for f in files if f.suffix == ".py"]
        assert len(py_files) == 1

    def test_collects_markdown_files(self, tmp_corpus: Path) -> None:
        files = collect_files(tmp_corpus)
        md_files = [f for f in files if f.suffix == ".md"]
        assert len(md_files) == 1

    def test_skips_ignored_directories(self, tmp_path: Path) -> None:
        venv = tmp_path / ".venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "something.py").write_text("x = 1\n")
        (tmp_path / "real.py").write_text("y = 2\n")

        files = collect_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "real.py"

    def test_single_file_input(self, tmp_corpus: Path) -> None:
        single = tmp_corpus / "example.py"
        files = collect_files(single)
        assert len(files) == 1
        assert files[0] == single

    def test_unsupported_extension_ignored(self, tmp_path: Path) -> None:
        (tmp_path / "data.xlsx").write_text("not supported")
        files = collect_files(tmp_path)
        assert len(files) == 0

    def test_returns_sorted(self, tmp_corpus: Path) -> None:
        files = collect_files(tmp_corpus)
        assert files == sorted(files)


class TestClassifyFile:
    def test_python_is_code(self) -> None:
        assert classify_file(Path("foo.py")) == "code"

    def test_markdown_is_doc(self) -> None:
        assert classify_file(Path("notes.md")) == "doc"

    def test_pdf_is_paper(self) -> None:
        assert classify_file(Path("paper.pdf")) == "paper"

    def test_png_is_image(self) -> None:
        assert classify_file(Path("screenshot.png")) == "image"

    def test_unknown_extension(self) -> None:
        assert classify_file(Path("data.xyz")) == "unknown"
