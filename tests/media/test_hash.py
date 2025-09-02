"""Tests for media hashing utilities."""

import hashlib

from chatx.media.hash import sha256_stream


def test_sha256_stream_matches_hash(jpeg_file):
    expected = hashlib.sha256(jpeg_file.read_bytes()).hexdigest()
    assert sha256_stream(str(jpeg_file)) == expected
