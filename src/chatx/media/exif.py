"""EXIF parsing utilities."""

from __future__ import annotations

from pathlib import Path


def read_exif(path: str | Path) -> dict[str, object]:
    """Return EXIF metadata for *path*.

    Uses :mod:`Pillow` if available and falls back to an empty mapping when
    EXIF data cannot be read. Tag names are converted to human readable
    strings when possible.
    """

    try:
        from PIL import ExifTags, Image  # type: ignore
    except Exception:  # pragma: no cover - dependency missing
        return {}

    p = Path(path)
    try:
        with Image.open(p) as img:  # type: ignore[attr-defined]
            exif = img.getexif()
            if not exif:
                return {}
            tags: dict[str, object] = {}
            for tag_id, value in exif.items():
                name = ExifTags.TAGS.get(tag_id, str(tag_id))
                tags[name] = value
            return tags
    except Exception:
        return {}
