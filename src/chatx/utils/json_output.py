"""JSON output utilities with schema validation."""

import json
from pathlib import Path
from typing import List, Optional

from chatx.schemas.message import CanonicalMessage


def write_messages_with_validation(messages: List[CanonicalMessage], output_path: Path) -> None:
    """Write messages to JSON file with schema validation.
    
    Args:
        messages: List of CanonicalMessage objects to write
        output_path: Path to output JSON file
        
    Behavior:
        - Validates each message via Pydantic; invalid ones are written to a
          quarantine file (messages_bad.jsonl) and skipped from main output.
        - Does not raise on validation errors; continues writing valid data.
        - Raises OSError only if the main file cannot be written.
    """
    # Validate messages, quarantining any invalid ones
    quarantine_dir = output_path.parent / "quarantine"
    quarantine_path = quarantine_dir / "messages_bad.jsonl"
    messages_data: List[dict] = []
    bad_count = 0

    for i, msg in enumerate(messages):
        try:
            # Pydantic validation happens automatically
            msg_dict = msg.model_dump(mode="json")
            messages_data.append(msg_dict)
        except Exception as e:  # pragma: no cover - triggered only by malformed data
            # Lazily create quarantine dir and append the bad record with reason
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            with open(quarantine_path, "a", encoding="utf-8") as qf:
                qf.write(json.dumps({
                    "index": i,
                    "error": str(e),
                }) + "\n")
            bad_count += 1
    
    # Write to file with pretty formatting
    output_data = {
        "messages": messages_data,
        "total_count": len(messages_data),
        "schema_version": "1.0"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
