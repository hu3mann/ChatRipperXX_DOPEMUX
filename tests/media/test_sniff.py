"""Stub tests for media.sniff."""

import pytest

from chatx.media.sniff import sniff_mime


@pytest.mark.xfail(raises=NotImplementedError, strict=True, reason="stub")
def test_sniff_unimplemented():
    sniff_mime("/dev/null")
