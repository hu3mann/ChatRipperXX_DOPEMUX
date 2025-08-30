iMessage Extractor Specification

Status: Draft | Owner: You | Last Updated: 2025-08-26 PT

Purpose

Define the authoritative mapping from chat.db (macOS iMessage SQLite) to Canonical Message objects so extraction is deterministic, lossless (via source_meta), and testable. Aligns with INTERFACES.md (Message schema) and ACCEPTANCE_CRITERIA.md (replies, reactions, provenance).

Requirements (MUST/SHOULD)
	•	MUST read from a temp-copied DB (and WAL if present) to avoid file locks.
	•	MUST convert Apple Epoch to ISO-8601 UTC with robust unit handling (ns vs s).
	•	MUST output one JSON object per message to <out>/messages.jsonl, validating against message.schema.json.
	•	MUST fold reactions into target message reactions[].
	•	MUST set stable reply_to_msg_id when a DB row is a reply.
	•	MUST include source_ref.path and (if available) source_ref.guid for the chat; platform extras in source_meta.
	•	MUST NOT inline binary data or upload attachments; only references.

Apple Epoch Conversion (deterministic)
	•	Apple epoch = 2001-01-01T00:00:00Z. Column message.date can be in seconds or nanoseconds depending on macOS/iOS version/export.
	•	Conversion MUST:
	•	If abs(date) >= 10^11, treat as nanoseconds → divide by 1_000_000_000.
	•	Else treat as seconds.
	•	Add to Apple epoch; output ISO-8601 UTC with Z.

Core Tables & Joins
	•	message (alias m) — source rows.
	•	chat_message_join (cmj) — associates messages to chats.
	•	chat (c) — provides guid (conversation id).
	•	handle (h) — map m.handle_id → normalized address (id).
	•	message_attachment_join (maj) → attachment (a) — attachment metadata.

Canonical Query Sketch
```sql
SELECT
  m.ROWID            AS msg_rowid,
  m.guid             AS msg_guid,
  m.text             AS body,
  m.attributedBody   AS body_rich,
  m.is_from_me       AS is_me,
  m.handle_id        AS handle_id,
  m.service          AS service,         -- iMessage/SMS/MMS
  m.date             AS date_raw,
  m.associated_message_guid AS assoc_guid,
  m.associated_message_type AS assoc_type,
  m.cache_has_attachments   AS has_attachments,
  c.guid             AS chat_guid
FROM message m
LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
LEFT JOIN chat c                ON c.ROWID = cmj.chat_id
LEFT JOIN handle h              ON h.ROWID = m.handle_id;
```

Sender Resolution
	•	If is_from_me=1 → sender="Me", sender_id="me".
	•	Else sender displays h.id (phone/email); sender_id=h.id (normalized as-is).
	•	Include service in source_meta.service.

Reactions (Tapbacks)
	•	Reaction rows are messages with assoc_guid referencing the target message guid and assoc_type in {2000..2005}:
	•	2000=love, 2001=like, 2002=dislike, 2003=laugh, 2004=emphasize, 2005=question.
	•	Extraction MUST:
	•	group these into the target message’s reactions[] with {from, kind, ts}; where from is resolved sender; ts is reaction row timestamp.
	•	suppress the reaction row from output as a standalone message.
	•	Store the raw assoc_* in source_meta for both reaction and target rows to retain fidelity.

Replies
	•	Rows with assoc_guid that are not in the 2000–2005 reaction range SHOULD be treated as replies.
	•	Algorithm (stable mapping):
	1.	Build a map guid → msg_id for all non-reaction rows.
	2.	For each row with assoc_guid not mapped to reaction kinds, set reply_to_msg_id = map[assoc_guid] if present.
	3.	If unmapped (different export/version), leave reply_to_msg_id = null and record source_meta.reply_unresolved = assoc_guid.
	•	Note: Exact reply typing can vary by OS version; this strategy is deterministic and does not lose the relation, even if unresolved (tracked in source_meta). If you can provide a sample DB, we will lock this precisely.

Attachments
	•	Join via message_attachment_join → attachment; for each attachment emit:
	•	type best-effort (image|video|audio|file|unknown), filename from a.filename or transfer_name,
	•	optional abs_path when present, mime_type (if derivable), and uti.
	•	Store additional columns under source_meta.attachments[i].* to avoid loss.

Provenance
	•	Set source_ref = {"guid": chat_guid, "path": <original db path>}.
	•	Persist any additional DB columns as source_meta.*.

Output Validation
	•	Every emitted object MUST validate against message.schema.json.
	•	An extraction run MUST output out/messages.jsonl and a small run report (counts, reaction fold counts, unresolved reply count).
