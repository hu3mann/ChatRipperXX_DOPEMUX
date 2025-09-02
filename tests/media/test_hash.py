"""Tests for hashing utilities."""

from __future__ import annotations

from pathlib import Path

from chatx.media.hash import sha256_stream


def test_sha256_stream(tmp_path: Path) -> None:
    file_path = tmp_path / "data.bin"
    file_path.write_bytes(b"abc123")
    digest = sha256_stream(file_path)
    assert (
        digest
        == "6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090"
    )
