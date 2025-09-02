"""Hashing utilities for media files."""

from __future__ import annotations

import hashlib


def sha256_stream(path: str, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest for *path*.

    Reads the file in chunks to avoid loading the entire file into memory.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
