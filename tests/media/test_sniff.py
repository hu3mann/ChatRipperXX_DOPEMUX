"""Tests for MIME sniffing utilities."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from chatx.media.sniff import sniff_mime


def _create_png(path: Path) -> None:
    Image.new("RGB", (1, 1), color="red").save(path, format="PNG")


def _create_jpeg(path: Path) -> None:
    Image.new("RGB", (1, 1), color="blue").save(path, format="JPEG")


def _create_heic(path: Path) -> None:
    # Minimal HEIC header: size (24) + ftyp + brand
    header = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heic"
    path.write_bytes(header)


def test_sniff_png(tmp_path: Path) -> None:
    file_path = tmp_path / "test.png"
    _create_png(file_path)
    assert sniff_mime(file_path) == "image/png"


def test_sniff_jpeg(tmp_path: Path) -> None:
    file_path = tmp_path / "test.jpg"
    _create_jpeg(file_path)
    assert sniff_mime(file_path) == "image/jpeg"


def test_sniff_heic(tmp_path: Path) -> None:
    file_path = tmp_path / "test.heic"
    _create_heic(file_path)
    assert sniff_mime(file_path) == "image/heic"


def test_sniff_unknown(tmp_path: Path) -> None:
    file_path = tmp_path / "data.bin"
    file_path.write_bytes(b"abcdef")
    assert sniff_mime(file_path) == "application/octet-stream"


def test_sniff_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.bin"
    assert sniff_mime(missing) == "application/octet-stream"
