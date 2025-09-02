"""MIME sniffing utilities."""

from __future__ import annotations


def sniff_mime(path: str) -> str:
    """Return the detected MIME type for *path*.

    The detector inspects file magic numbers for common image formats.
    Falls back to ``application/octet-stream`` when unknown.
    """

    with open(path, "rb") as f:
        header = f.read(12)

    if header.startswith(b"\xFF\xD8"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if header[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    if len(header) >= 12 and header[4:12] in (
        b"ftypheic",
        b"ftypheix",
        b"ftyphevc",
        b"ftyphevx",
        b"ftypmif1",
        b"ftypmsf1",
    ):
        return "image/heic"
    return "application/octet-stream"
