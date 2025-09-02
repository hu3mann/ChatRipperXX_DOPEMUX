"""Stub tests for media.exif."""

import pytest

from chatx.media.exif import read_exif


@pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="stub")
def test_read_exif_unimplemented():
    read_exif("/dev/null")
