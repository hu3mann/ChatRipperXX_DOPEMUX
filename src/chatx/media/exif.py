"""EXIF parsing utilities."""

from __future__ import annotations

from typing import Any, Dict


def read_exif(path: str) -> Dict[str, Any]:
    """Return EXIF metadata for *path*.

    Uses Pillow when available and falls back to an empty dict on failure.
    """
    try:
        from PIL import Image, ExifTags  # type: ignore

        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return {}
            result: Dict[str, Any] = {}
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                result[tag] = value
            return result
    except Exception:
        return {}
