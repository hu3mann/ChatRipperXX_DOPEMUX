"""MIME sniffing utilities."""

from __future__ import annotations

from pathlib import Path


def sniff_mime(path: str | Path) -> str:
    """Return a best-effort MIME type for *path*.

    The implementation uses magic byte checks for common image formats
    (PNG, JPEG and HEIC). Unknown files default to
    ``application/octet-stream``.
    """

    p = Path(path)
    try:
        with p.open("rb") as fh:
            header = fh.read(12)
    except OSError:
        return "application/octet-stream"

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in {
        b"heic",
        b"heix",
        b"hevc",
        b"hevx",
        b"mif1",
        b"msf1",
    }:
        return "image/heic"
    return "application/octet-stream"
