"""SHA256 content-hash cache for incremental processing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CACHE_DIR = Path("myelinate-out/cache")


def file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache(cache_dir: Path | None = None) -> dict[str, str]:
    """Load the hash cache from disk."""
    cache_file = (cache_dir or CACHE_DIR) / "hashes.json"
    if not cache_file.exists():
        return {}
    with open(cache_file) as f:
        return json.load(f)


def save_cache(cache: dict[str, str], cache_dir: Path | None = None) -> None:
    """Save the hash cache to disk."""
    target = (cache_dir or CACHE_DIR) / "hashes.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w") as f:
        json.dump(cache, f, indent=2)


def partition_by_cache(
    files: list[Path],
    cache_dir: Path | None = None,
) -> tuple[list[Path], list[Path]]:
    """Split files into (changed, cached) based on content hash.

    Returns:
        Tuple of (files that need processing, files that are cached).
    """
    cache = load_cache(cache_dir)
    changed: list[Path] = []
    cached: list[Path] = []

    for f in files:
        current_hash = file_hash(f)
        key = str(f)
        if cache.get(key) == current_hash:
            cached.append(f)
        else:
            changed.append(f)

    return changed, cached
