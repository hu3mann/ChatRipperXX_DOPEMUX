"""Stub tests for media.hash."""

import pytest

from chatx.media.hash import sha256_stream


def test_sha256_stream_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        sha256_stream("/dev/null")
