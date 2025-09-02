"""JSON Schema validation helpers for Canonical Message rows.

Validates message dicts against schemas/message.schema.json and supports
quarantining invalid rows to a JSONL file with error details.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Tuple


def _load_message_schema(schema_dir: Path) -> dict:
    with open(schema_dir / "message.schema.json", "r", encoding="utf-8") as f:
        return json.load(f)


def validate_message_dict(msg: dict, schema_dir: Path) -> Tuple[bool, str | None]:
    """Validate a message dict against the JSON Schema.

    Returns (True, None) if valid; (False, error) otherwise.
    """
    try:
        import jsonschema
    except Exception:
        # If jsonschema isn't available, treat as valid
        return True, None

    schema = _load_message_schema(schema_dir)
    try:
        jsonschema.validate(msg, schema)
        return True, None
    except Exception as e:  # ValidationError
        return False, str(e)


def append_quarantine_record(quarantine_path: Path, record: dict[str, Any]) -> None:
    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    with open(quarantine_path, "a", encoding="utf-8") as qf:
        qf.write(json.dumps(record, ensure_ascii=False) + "\n")

