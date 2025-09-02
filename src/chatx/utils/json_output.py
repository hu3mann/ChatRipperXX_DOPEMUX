"""JSON output utilities with schema validation."""

import json
from pathlib import Path
from typing import List, Optional

from chatx.schemas.message import CanonicalMessage
from chatx.validate.jsonschema import validate_message_dict, append_quarantine_record


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

    # Locate schema dir for jsonschema validation
    schema_dir = output_path.parent.parent / "schemas"
    if not schema_dir.exists():
        # Fallback to project root schemas
        schema_dir = Path(__file__).parent.parent.parent / "schemas"

    for i, msg in enumerate(messages):
        try:
            # Pydantic validation happens automatically
            msg_dict = msg.model_dump(mode="json")
            # JSON Schema validation (secondary) — quarantine on failure
            ok, err = validate_message_dict(msg_dict, schema_dir)
            if ok:
                messages_data.append(msg_dict)
            else:
                quarantine_dir.mkdir(parents=True, exist_ok=True)
                append_quarantine_record(
                    quarantine_path,
                    {"index": i, "error": f"jsonschema: {err}", "row": msg_dict},
                )
                bad_count += 1
        except Exception as e:  # pragma: no cover - triggered only by malformed data
            # Lazily create quarantine dir and append the bad record with reason
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            append_quarantine_record(
                quarantine_path,
                {"index": i, "error": f"pydantic: {e}"},
            )
            bad_count += 1
    
    # Write to file with pretty formatting
    output_data = {
        "messages": messages_data,
        "total_count": len(messages_data),
        "schema_version": "1.0"
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
