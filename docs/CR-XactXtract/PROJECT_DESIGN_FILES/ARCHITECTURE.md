Title: ChatX / XtractXact Architecture
Status: Draft | Owner: You | Last Updated: 2025-08-16 PT

## Context
**Problem.** We need a private, local-first forensic chat analysis tool that ingests large multi-platform exports, redacts and pseudonymizes sensitive data, enriches messages with structured meaning, and supports retrieval/analytics—while optionally escalating to cloud LLMs under strict controls.

**Goals.**
- Local-first enrichment with optional cloud escalation guarded by **Policy Shield**.
- Deterministic, schema-locked outputs with evidence links and full **provenance**.
- Fast ingestion/indexing and low-latency retrieval over large corpora (50k–1M messages).
- CI-enforced **privacy, validation, and performance** gates.
- Extensible adapters for new sources, models, stores.

**Non-Goals.**
- No always-on cloud processing. Cloud is opt-in per run.
- No GUI; CLI-only surface in this scope.
- No attachment uploads to cloud.

## System Overview (C4 L1–L2 narrative)
**External Systems & Users (L1).**
- *User (Analyst)* runs CLI on a workstation.
- *Cloud LLM Providers* (optional) receive only **redacted** text and **coarse** labels.
- *Filesystem* stores inputs, outputs, artifacts under `./out/`.
- *Optional: Vector Store (Chroma)* hosts per-contact collections on-device.

**Core Containers (Components).**
1) **Ingestor** — parses iMessage DB/PDF, Instagram JSON, WhatsApp JSON, TXT into canonical **Message** records.
2) **Transformer** — normalizes, sessionizes, and **chunks** conversations (turns:40 or daily windows).
3) **Policy Shield** — pseudonymizes people, tokenizes sensitive strings (⟦TKN:…⟧), measures redaction **coverage**; blocks hard-fail classes.
4) **Indexer** — writes redacted chunks + facets to **Chroma** collections (per contact) for retrieval.
5) **Local Enricher** — on-device LLM generates **Message/CU Enrichment** (schema-locked, deterministic).
6) **Hybrid Orchestrator** — gates by confidence **τ=0.7** and preflight; if allowed, performs **Cloud Enrichment** with minimal context and token ceilings.
7) **Validator** — enforces JSON Schemas; clamps enums & bounds; quarantines invalid rows.
8) **Observer** — metrics, logs, artifacts (e.g., `redaction_report.json`, validation summaries).

**Data at Rest.**
- `/raw` imports; `/chunks` normalized; `/redacted` windows; `/enrich` outputs; `/metrics` & `/reports` artifacts; `/cache` prompt/output cache.

## Key Flows
**Ingest → Transform.**
Trigger: `chatx <source> pull` → Components: Ingestor → Transformer → Data: canonical Message JSON → Outcome: normalized messages & chunks.

**Redact (Policy Shield).**
Trigger: `chatx redact` → Policy Shield → `redaction_report.json` with coverage ≥ 0.995 (0.999 strict) → Outcome: safe, pseudonymized windows.

**Index & Label.**
Trigger: `chatx index` / `chatx label build` → Indexer + Labeler → Data: Chroma embeddings + label facets → Outcome: low-latency retrieval by time/label/contact.

**Enrich (Local-first, Hybrid Optional).**
Trigger: `chatx enrich messages|units --backend hybrid --tau 0.7 [--allow-cloud]`  
Flow: Local Enricher → if `confidence_llm < τ` **and** preflight passed **and** `--allow-cloud`: Cloud Enricher → Validator → Outputs: `enrichment_message.jsonl`, `enrichment_cu.jsonl` with **provenance**, **shield**, **merge** fields and `source=local|cloud`.

**Validate & Observe.**
Trigger: CI or `chatx validate` → Validator + Observer → Artifacts: schema validation logs; metrics; cache reports; SLO checks.

## Data Model
**Message (canonical).**
- Fields: ids, timestamps, participants, direction, body (raw), body_redacted, attachments[], source/app metadata.
- PII & Sensitivity: phone/email/names → pseudonymized; explicit terms → ⟦TKN:…⟧ tokens.

**Chunk (LLM-ready redacted window).**
- Fields: chunk_id, contact_key, message_ids[], window spec (±N turns or daily), redacted_text, coarse_labels[].

**Enrichment (Message).**
- speech_act, intent, stance, tone, emotion_primary, certainty [0..1], directness [0..1], boundary_signal, repair_attempt, reply_to_consistent, inferred_meaning (≤200 chars), coarse_labels[], **fine_labels_local[]** (local-only), influence_class, influence_score [0..1], relationship_structure[], relationship_dynamic[], map_refs[], notes, confidence_llm [0..1], source, **provenance**, **shield**, **merge**.

**Enrichment (CU).**
- cu_id, topic_label, vibe_trajectory[], escalation_curve, coarse_labels[], **fine_labels_local[]** (local-only), relationship_structure[], relationship_dynamic[], ledgers{boundary, consent, decisions, commitments}, issue_refs[], evidence_index[], confidence_llm, source, **provenance**, **shield**, **merge**.

**Retention.**
- Raw inputs: local; retained per user setting.
- Redacted chunks & enrichments: retained for analytics; can be regenerated from raw + salt.
- Metrics/logs: rotated; pii-free by design.

**PII Notes.**
- Salted, deterministic pseudonyms; salt never leaves device.
- No attachments to cloud; fine labels never in cloud prompts.

## Operational Concerns
**Deploy.**
- Local CLI install; optional container for CI; configuration via env and `labels.yml`/YAML.

**Scale.**
- Batchable pipeline; checkpoints every ≤10k msgs; per-contact collections; caches keyed by (model_id, model_sha, prompt_hash, source_hash, schema_v).

**Observability.**
- Metrics: coverage, throughput/latency, token usage, cache hit ratio, schema_invalid_count, visibility_leak_count.
- Artifacts: `redaction_report.json`, enrichment validation reports, run report.

**Cost.**
- Token ceilings: max_output_tokens ≤ 800; input-token caps; QPS throttling; caching target ≥ 0.80 hit rate.

**Failure Modes & Rollback.**
- Coverage < threshold or hard-fail class → block cloud; log E_PRECHECK_COVERAGE_LOW/E_HARDFAIL_CLASS.
- Schema invalid → quarantine; E_SCHEMA_INVALID.
- Visibility leaks (fine labels/attachments) → block; E_VISIBILITY_LEAK/E_ATTACHMENT_PRESENT.
- Rollback is file-level: restore from `.bak` or rerun from redacted inputs + provenance/source_hash.

## Security & Compliance
**Threats.**
- Data exfiltration via accidental cloud prompts.
- Re-identification from unredacted logs.
- Provider over-collection.

**Controls.**
- Policy Shield preflight; coverage gates; hard-fail classes.
- Field Visibility Matrix (cloud-visible vs local-only).
- Deterministic pseudonymization with local salt.
- Cloud disabled by default; explicit `--allow-cloud` required.
- Provenance & shield recorded on every record for audit.

**Authn/Z.**
- Local CLI; OS user context; optional provider keys via env/Parameter Store.

**Regulatory Considerations.**
- Privacy by default; local processing; explicit consent for any cloud usage (documented in run report).

## Appendix
**Glossary.**
- **Policy Shield** — redaction + coverage + hard-fail guard before any cloud call.
- **Hybrid Cascade** — local enrich first; escalate to cloud only under confidence + policy gates.
- **Provenance** — schema_v, run_id, ts, model_id/sha, provider, prompt_hash, source_hash, token_usage, latency_ms, cache_hit.
- **Shield** — preflight_coverage, strict, hardfail_triggered, nuance_level.
- **Merge** — source_last_enrichment, reason (why cloud/local chosen).

**References.**
- See `CLOUD_ENRICHMENT.md` (schemas, visibility rules), `INTERFACES.md` (CLI, SLAs, error codes), `NON_FUNCTIONAL.md` (SLO/SLA), `ACCEPTANCE_CRITERIA.md` (Gherkin), `ADRS.md` (decisions), `labels.yml` (taxonomy).



## C4 Diagrams (ASCII)

### Level 1 — System Context
```
+----------------------+            +---------------------------+
|  Analyst (Person)    |  CLI cmds  |   ChatX / XtractXact      |
|  • runs locally      +----------->|   (System)                |
|  • reviews outputs   |            |                           |
+----------+-----------+            |  • Ingest, Redact,        |
           ^                        |    Index, Enrich, Validate|
           |                        +-----+---------------------+
           |                              |
           |                              | redacted text + coarse labels
           |                              v
+----------+-----------+            +-----+---------------------+
|  Filesystem           | artifacts | Optional Cloud LLMs       |
|  • inputs/outputs     +---------> | • receives redacted text  |
|  • metrics/reports    |           | • returns structured JSON |
+-----------------------+           +---------------------------+

             ^
             | embeddings / vectors (on-device)
             |
+-----------------------+
|  Chroma Vector Store  |
|  • per-contact colls  |
+-----------------------+
```

### Level 2 — Containers (Main Components)
```
+------------------------------- ChatX / XtractXact ----------------------------------+
|                                                                                     |
|  +---------+    +-----------+   +--------------+   +---------+   +--------------+   |
|  |Ingestor |--> |Transformer|-> | PolicyShield |-> | Indexer |-> | LocalEnricher|   |
|  +----+----+    +-----+-----+   +------+-------+   +----+----+   +-------+------+   |
|       |               |                 |                |                |          |
|       | raw           | chunks          | redacted       | embeddings     | enrich   |
|       v               v                 v                v                v          |
|  +----+----+    +-----+-----+     +----+----+      +----+----+     +-----+------+   |
|  | Files  |    | Chunk Repo|     | Redacted|      | Chroma   |     | Validator  |   |
|  +----+----+    +-----+-----+     +----+----+      +----+----+     +-----+------+   |
|       ^               ^                 |                ^                |          |
|       |               |                 | preflight ok?  |                v          |
|       |               |                 +-------+--------+         +------+-------+  |
|       |               |                         |                  |   Observer   |  |
|       |               |                         |                  +------+-------+  |
|       |               |                         |                         |          |
|       |               |                         v                         v          |
|       |               |                 +-------+--------+        metrics/logs       |
|       |               |                 | Hybrid Orchestr|                          |
|       |               |                 +-------+--------+                          |
|       |               |                         |                                   |
|       |               |        local ok (τ≥.7)? | yes -> done                       |
|       |               |                         | no                                |
|       |               |                         v                                   |
|       |               |                 +-------+--------+                          |
|       |               |                 |  CloudEnricher | (redacted text only)     |
|       |               |                 +----------------+                          |
|                                                                                     |
+-------------------------------------------------------------------------------------+
```

### Sequence — Enrichment (Hybrid)
```
Analyst -> PolicyShield: preflight(redacted windows)
PolicyShield -> Analyst: coverage >= 0.995 (strict 0.999)? hard-fail none?
Analyst -> LocalEnricher: enrich(messages|units)
LocalEnricher -> Validator: JSON schema validate
Validator -> HybridOrchestrator: confidence_llm < τ?
HybridOrchestrator -> CloudEnricher: if --allow-cloud && preflight passed
CloudEnricher -> Validator: JSON schema validate
Validator -> Observer: metrics, run report
Observer -> Analyst: enrichment_message.jsonl, enrichment_cu.jsonl
```

**Metadata Update (no re-embed).**
Trigger: `chatx index update` → Upserts enrichment-derived metadata onto existing chunks **without** changing embeddings or redacted text; improves filter/sort while preserving vector stability.
