Prompt Contracts (Local-first; Cloud optional)

Status: Draft | Owner: You | Last Updated: 2025-08-26 PT

Local Enrichment (Message)
	•	Input: redacted message body + ±2 turns (default), minimal metadata (platform, time).
	•	Budget: ≤ 800 output tokens.
	•	Output: must conform to enrichment_message.schema.json; include confidence_llm, source="local".

Hybrid Escalation
	•	Only when confidence_llm < τ (default 0.7) and --allow-cloud and preflight passed.
	•	Context limited to redacted chunk text + minimal coarse labels; attachments excluded.
	•	Provenance fields MUST be recorded for every call.