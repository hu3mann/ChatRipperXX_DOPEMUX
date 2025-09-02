from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture()
def jpeg_file(tmp_path: Path) -> Path:
    img = Image.new("RGB", (1, 1), color="red")
    exif = Image.Exif()
    exif[271] = "ChatX"  # Make tag
    path = tmp_path / "test.jpg"
    img.save(path, exif=exif)
    return path


@pytest.fixture()
def png_file(tmp_path: Path) -> Path:
    img = Image.new("RGB", (1, 1), color="red")
    path = tmp_path / "test.png"
    img.save(path)
    return path


@pytest.fixture()
def gif_file(tmp_path: Path) -> Path:
    img = Image.new("RGB", (1, 1), color="red")
    path = tmp_path / "test.gif"
    img.save(path, format="GIF")
    return path


@pytest.fixture()
def tiff_file(tmp_path: Path) -> Path:
    img = Image.new("RGB", (1, 1), color="red")
    path = tmp_path / "test.tiff"
    img.save(path, format="TIFF")
    return path


@pytest.fixture()
def heic_file(tmp_path: Path) -> Path:
    # Minimal HEIC header bytes sufficient for sniffing
    data = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00"
    path = tmp_path / "test.heic"
    path.write_bytes(data)
    return path
