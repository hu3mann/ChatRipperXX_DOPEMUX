"""Stub tests for media.hash."""

import pytest

from chatx.media.hash import sha256_stream


@pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="stub")
def test_sha256_stream_unimplemented():
    sha256_stream("/dev/null")
