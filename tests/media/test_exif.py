"""Stub tests for media.exif."""

import pytest

from chatx.media.exif import read_exif


def test_read_exif_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        read_exif("/dev/null")
