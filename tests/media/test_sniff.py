"""Tests for MIME sniffing utilities."""

from chatx.media.sniff import sniff_mime


def test_sniff_jpeg(jpeg_file):
    assert sniff_mime(str(jpeg_file)) == "image/jpeg"


def test_sniff_png(png_file):
    assert sniff_mime(str(png_file)) == "image/png"


def test_sniff_gif(gif_file):
    assert sniff_mime(str(gif_file)) == "image/gif"


def test_sniff_tiff(tiff_file):
    assert sniff_mime(str(tiff_file)) == "image/tiff"


def test_sniff_heic(heic_file):
    assert sniff_mime(str(heic_file)) == "image/heic"
