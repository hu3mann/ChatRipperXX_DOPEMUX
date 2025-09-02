Developer Guide

Status: Draft | Owner: You | Last Updated: 2025-08-26 PT

Setup
	•	Python 3.11+.
	•	uv or pip to install.
	•	Optional local LLM via Ollama (e.g., gemma:2-9b-q4_K_M).
	•	Copy .env.example to .env (do not commit). Cloud disabled by default.

Running the Pipeline (iMessage-first)
	1.	Extract: chatx imessage pull --contact "<id>" --db ~/Library/Messages/chat.db --out ./out
	2.	Transform: chatx transform --input ./out/raw/*.json --to jsonl --chunk turns:20 --stride 10 --contact CN_xxx
	3.	Redact: chatx redact --input ./out/chunks/*.json --pseudonymize --opaque --threshold 0.995 --salt-file ./salt.key --report ./out/redaction_report.json
	4.	Index: chatx index --input ./out/redacted/*.json --store chroma --collection chatx_<contact>
	5.	Query: chatx query "What changed after Feb?" --contact CN_xxx --since 2025-02-01 --k 32

Troubleshooting
	•	SQLite lock: ensure DB temp copy includes WAL; open read-only.
	•	Apple epoch drift: see IMESSAGE_SPEC.md.
	•	Determinism: disable streaming; fix seeds in config.