"""Tests for EXIF extraction utilities."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from chatx.media.exif import read_exif


def test_read_exif(tmp_path: Path) -> None:
    file_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (1, 1), color="green")
    exif = Image.Exif()
    exif[270] = "sample"  # ImageDescription
    img.save(file_path, exif=exif)

    data = read_exif(file_path)
    assert data.get("ImageDescription") == "sample"


def test_read_exif_empty(tmp_path: Path) -> None:
    file_path = tmp_path / "plain.jpg"
    Image.new("RGB", (1, 1)).save(file_path, format="JPEG")
    assert read_exif(file_path) == {}
