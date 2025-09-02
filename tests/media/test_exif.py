"""Tests for EXIF parsing utilities."""

from chatx.media.exif import read_exif


def test_read_exif_returns_metadata(jpeg_file):
    exif = read_exif(str(jpeg_file))
    assert exif.get("Make") == "ChatX"


def test_read_exif_missing_returns_empty(png_file):
    assert read_exif(str(png_file)) == {}
