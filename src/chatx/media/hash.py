"""Hashing utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_stream(path: str | Path, chunk_size: int = 65536) -> str:
    """Return the SHA-256 hex digest for *path*.

    The file is read in chunks to avoid loading the entire file into memory.
    """

    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
