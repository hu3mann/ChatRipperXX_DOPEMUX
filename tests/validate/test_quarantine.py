from __future__ import annotations

import json
from pathlib import Path

from chatx.validate.jsonschema import validate_message_dict, append_quarantine_record


def test_quarantine_on_jsonschema_failure(tmp_path: Path) -> None:
    # Minimal invalid message (missing required fields like msg_id)
    bad_msg = {
        "platform": "imessage",
        "conv_id": "conv",
        # missing msg_id, timestamp, sender, sender_id, is_me, etc.
    }

    schema_dir = Path(__file__).parent.parent.parent / "schemas"
    ok, err = validate_message_dict(bad_msg, schema_dir)
    assert ok is False
    assert err is not None

    quarantine = tmp_path / "quarantine" / "messages_bad.jsonl"
    append_quarantine_record(quarantine, {"error": err, "row": bad_msg})
    assert quarantine.exists()
    line = quarantine.read_text(encoding="utf-8").strip()
    obj = json.loads(line)
    assert "error" in obj and "row" in obj

