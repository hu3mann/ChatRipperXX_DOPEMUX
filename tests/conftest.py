"""Test configuration and fixtures."""

from pathlib import Path
from datetime import datetime, timezone

import pytest

from chatx.schemas.message import CanonicalMessage, SourceRef


@pytest.fixture
def sample_message() -> CanonicalMessage:
    """Create a sample canonical message for testing."""
    return CanonicalMessage(
        msg_id="123",
        conv_id="conv_456",
        platform="imessage",
        timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        sender="Test User",
        sender_id="test@example.com",
        is_me=False,
        text="Hello, world!",
        source_ref=SourceRef(
            guid="test-chat-guid",
            path="/test/path/chat.db"
        )
    )


@pytest.fixture 
def temp_chat_db(tmp_path: Path) -> Path:
    """Create a temporary SQLite database file for testing."""
    db_path = tmp_path / "test_chat.db"
    
    # Create an empty file (real tests would populate with SQLite data)
    db_path.touch()
    
    return db_path


@pytest.fixture
def sample_config_data() -> dict:
    """Sample configuration data for testing."""
    return {
        "verbose": False,
        "output_dir": "./output",
        "llm": {
            "provider": "local",
            "model": "llama2",
            "max_retries": 3,
            "timeout": 60
        },
        "redaction": {
            "strict_mode": True,
            "generate_report": True,
            "fail_on_leak": True
        },
        "batch_size": 10,
        "max_workers": 4
    }