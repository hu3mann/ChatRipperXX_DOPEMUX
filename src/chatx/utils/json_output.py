"""JSON output utilities with schema validation."""

import json
from pathlib import Path
from typing import List

from chatx.schemas.message import CanonicalMessage


def write_messages_with_validation(messages: List[CanonicalMessage], output_path: Path) -> None:
    """Write messages to JSON file with schema validation.
    
    Args:
        messages: List of CanonicalMessage objects to write
        output_path: Path to output JSON file
        
    Raises:
        ValidationError: If any message fails schema validation
        OSError: If file cannot be written
    """
    # Validate all messages before writing
    for i, msg in enumerate(messages):
        try:
            # Pydantic validation happens automatically when accessing model fields
            _ = msg.model_dump()
        except Exception as e:
            raise ValueError(f"Message {i} failed validation: {e}")
    
    # Convert to JSON-serializable format
    messages_data = []
    for msg in messages:
        msg_dict = msg.model_dump()
        # Convert datetime to ISO string for JSON serialization
        if msg_dict.get('timestamp'):
            msg_dict['timestamp'] = msg.timestamp.isoformat()
        messages_data.append(msg_dict)
    
    # Write to file with pretty formatting
    output_data = {
        "messages": messages_data,
        "total_count": len(messages),
        "schema_version": "1.0"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)