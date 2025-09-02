"""Tests for core iMessage extraction functionality."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from chatx.imessage.extract import apple_timestamp_to_iso, resolve_contact_handles


class TestAppleTimestampConversion:
    """Test Apple Core Data timestamp conversion."""
    
    def test_apple_epoch_conversion(self):
        """Test conversion of Apple epoch (2001-01-01 00:00:00 UTC)."""
        # Apple epoch in nanoseconds is 0
        result = apple_timestamp_to_iso(0)
        assert result == "2001-01-01T00:00:00Z"
    
    def test_known_timestamp_conversion(self):
        """Test conversion of a known timestamp."""
        # Jan 1, 2024 00:00:00 UTC = 23 years after Apple epoch
        # 23 years * 365.25 days/year * 24 hours/day * 3600 seconds/hour * 1e9 nanoseconds/second
        ns_since_apple_epoch = int(23 * 365.25 * 24 * 3600 * 1_000_000_000)
        result = apple_timestamp_to_iso(ns_since_apple_epoch)
        assert result.startswith("2024-01-01T")
    
    def test_negative_timestamp(self):
        """Test handling of negative timestamps (before Apple epoch)."""
        # 1 day before Apple epoch
        ns_before_epoch = -24 * 3600 * 1_000_000_000
        result = apple_timestamp_to_iso(ns_before_epoch)
        assert result == "2000-12-31T00:00:00Z"


class TestContactHandleResolution:
    """Test contact identifier resolution to handle IDs."""
    
    def test_placeholder_implementation(self):
        """Test placeholder returns empty list."""
        # TODO: Remove this test when real implementation is added in PR-1
        result = resolve_contact_handles(None, "test@example.com")
        assert result == []


class TestExtractMessages:
    """Test main message extraction function."""
    
    def test_not_implemented_error(self, tmp_path):
        """Test that extract_messages raises NotImplementedError."""
        from chatx.imessage.extract import extract_messages
        
        fake_db = tmp_path / "chat.db"
        fake_db.touch()
        
        with pytest.raises(NotImplementedError, match="Implementation will be added"):
            list(extract_messages(
                db_path=fake_db,
                contact="test@example.com",
                out_dir=tmp_path
            ))