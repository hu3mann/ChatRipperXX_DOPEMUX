"""Stub tests for media.sniff."""

import pytest

from chatx.media.sniff import sniff_mime


def test_sniff_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        sniff_mime("/dev/null")
