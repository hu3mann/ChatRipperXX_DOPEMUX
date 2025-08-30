===FILE: ADRS_MASTER_BY_DATE.md===

Architectural Decision Records — Master Bundle (resequenced by date where known)

Format: Title | Status | Owner | Date → Context / Options / Decision / Consequences / Links.
STRICT TRACE: Minimal quotes; every claim cited.

⸻

ADR-0001 — Local-first CLI & single-user scope

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: “Private, on-device analysis… local-first CLI… privacy by default; no GUI.”  ￼ “Non-goals: … GUI.”  ￼
Options: Local CLI / background daemon / hosted app.  ￼
Decision: Adopt a local-first CLI for private, on-device workflow.  ￼
Consequences: Privacy by default; no GUI.  ￼  ￼
Links → ARCHITECTURE.md: Local-first; GUI out.  ￼
Links → INTERFACES.md: Principles (local-first; deterministic; pre-cloud redaction).  ￼

⸻

ADR-0002 — Local storage & vector memory: SQLite + Chroma (per contact)

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Memory uses “Chroma per-contact collections (local).”  ￼
Options: Chroma / FAISS / pgvector (noted alternatives in aggregate).  ￼
Decision: Adopt per-contact Chroma collections for vector memory.  ￼
Consequences: Simple, fast, portable; revisit for multi-user later.  ￼
Links → ARCHITECTURE.md: Memory container (local Chroma).  ￼
Links → INTERFACES.md: chatx index --store chroma --collection chatx_<contact>.  ￼

⸻

ADR-0003 — Source-of-truth extraction from iMessage chat.db

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: iMessage pipeline copies chat.db+WAL → read-only SQL → normalize → fold reactions → link replies.  ￼
Options: Parse PDFs vs chat.db vs external exporter (aggregate).  ￼
Decision: Prefer DB+WAL copy and SQL joins across message/handle/attachments; then JSONL.  ￼  ￼
Consequences: Accurate threading and provenance.  ￼
Links → ARCHITECTURE.md: Extractor + Key Flow (iMessage).  ￼  ￼
Links → INTERFACES.md: chatx imessage pull …; chatx transform --to jsonl.  ￼  ￼

⸻

ADR-0004 — Instagram DM extraction from official data ZIP

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: “unzip → merge/sort → fold likes → JSONL → …”  ￼
Options: Scrape web vs parse official downloads (aggregate trade-off).  ￼
Decision: Parse per-thread JSON from the official ZIP; fold likes; produce JSONL.  ￼
Consequences: Reproducible, version-tolerant pipeline.  ￼
Links → ARCHITECTURE.md: Extractor + Key Flow (Instagram).  ￼  ￼
Links → INTERFACES.md: chatx instagram pull … --zip ./instagram.zip; chatx transform --to jsonl.  ￼  ￼

⸻

ADR-0005 — Dialogue Transcript JSONL as LLM input canon

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Transformer “emit Dialogue JSONL and Chunked Blocks.”  ￼
Options: Raw rows vs JSONL with folded reactions vs YAML (aggregate).  ￼
Decision: Use JSONL with ids, timestamps, speaker, text, reply_to, reactions, attachments, platform, conv_id; chunk later.  ￼  ￼
Consequences: Readable, easy to embed, preserves links, minimal bloat.  ￼
Links → ARCHITECTURE.md: Canonical Schemas (Message, Chunk).  ￼
Links → INTERFACES.md: chatx transform --to jsonl [--chunk …] [--contact …].  ￼

⸻

ADR-0006 — Retrieval strategy: Hybrid with local default

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Queries pre-filter by time/labels; retrieval can be local or cloud.  ￼
Options: Local-only vs cloud-only vs hybrid.  ￼
Decision: Default to local; support --retriever local|cloud; cloud requires --allow-cloud.  ￼  ￼
Consequences: Privacy by default; explicit consent for cloud.  ￼
Links → ARCHITECTURE.md: Temporal chain ends in label-aware retrieval.  ￼
Links → INTERFACES.md: chatx query … --since/--until/--labels-* … --retriever local|cloud [--allow-cloud].  ￼

⸻

ADR-0007 — Embeddings policy: Local by default, cloud optional

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: “Local-LLM-first enrichment… Cloud models are optional and only used after Policy Shield if confidence is low or the task is complex.”  ￼
Decision: Default to local models; allow cloud only behind Policy Shield.  ￼
Consequences: Quality trade-offs but configurable via backend switch.  ￼
Links → ARCHITECTURE.md: Orchestrator Pass A (local) with confidence gate.  ￼
Links → INTERFACES.md: chatx enrich … --backend local|cloud|hybrid --local-model "<id>" --tau 0.7 --allow-cloud.  ￼

⸻

ADR-0008 — Mandatory Policy Shield redaction before any cloud call

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Redaction coverage ≥0.995 (0.999 strict), pseudonyms, opaque tokens; hard-fail classes; attachments never uploaded.  ￼
Decision: Cloud disabled by default; redaction MUST precede any cloud call.  ￼
Consequences: Strong privacy with engineering overhead.  ￼
Links → ARCHITECTURE.md: Security & Compliance.  ￼
Links → INTERFACES.md: chatx redact … --threshold 0.995 [--strict] …; chatx preflight cloud …; SLAs (cloud off by default; attachments never uploaded).  ￼  ￼  ￼

⸻

ADR-0009 — Cloud enrichment orchestrator (schema-locked, minimal context)

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Need consistent enrichment with predictable outputs.  ￼
Decision: Schema-locked prompts; minimal redacted context (±2 turns); JSON validation; caching.  ￼
Consequences: Predictability and repeatability with extra effort.  ￼
Links → ARCHITECTURE.md: Appendix B pipeline (steps 2–5).  ￼
Links → INTERFACES.md: chatx enrich messages|units … --backend … --tau 0.7 --allow-cloud [--context 2] [--max-out 800].  ￼

⸻

ADR-0010 — Label-aware retrieval keyed to Issues/Episodes

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Queries must target themes over time; Gherkin requires boolean label filters.  ￼  ￼
Decision: Use metadata pre-filters and boosts keyed to labels/time; return citations.  ￼
Consequences: More precise retrieval with richer metadata.  ￼
Links → ARCHITECTURE.md: Temporal flow → label-aware retrieval.  ￼
Links → INTERFACES.md: chatx query … [--since/--until] [--labels-any/all/not] --k 32.  ￼

⸻

ADR-0011 — Issue Registry with Temporal Issue Graph (non-causal)

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Track Issues and edges (co_occurs, precedes, amplifies, attenuates) with lags/confidence; non-causal disclaimer.  ￼  ￼
Decision: Build weekly rollups → graph with role/lag/link_score/confidence.  ￼  ￼
Consequences: Powerful insights with explicit non-causal stance.  ￼
Links → ARCHITECTURE.md: Analytics containers + Temporal flow.  ￼  ￼
Links → INTERFACES.md: issues build …, episodes detect …, issues graph build ….  ￼

⸻

ADR-0012 — Sensitive “sex-work contexts” handling

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Work contexts like escorting/clients appear; coarse vs fine split; opaque tokens; attachments never uploaded.  ￼  ￼  ￼
Decision: Only coarse facets in cloud; explicit details tokenized locally with opaque tokens; keep media local.  ￼  ￼
Consequences: Useful analytics without leakage; stricter detectors/policies.  ￼
Links → ARCHITECTURE.md: Security & Compliance defaults.  ￼
Links → INTERFACES.md: Principles (coarse vs fine split); SLAs (attachments never uploaded).  ￼  ￼

⸻

ADR-0013 — Local-first enrichment cascade (confidence-gated hybrid)

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Minimize cloud exposure while maintaining quality via local-first then escalate when confidence_llm < τ.  ￼  ￼
Decision: Run local model (Pass A); on low confidence or complex synthesis, preflight then cloud (Pass B); persist source=local|cloud.  ￼  ￼
Consequences: Better privacy/cost; determinism needs fixed seeds; higher complexity.  ￼
Links → ARCHITECTURE.md: Enrichment Key Flow & orchestration.  ￼  ￼
Links → INTERFACES.md: chatx enrich … --backend local|cloud|hybrid --tau 0.7 --allow-cloud + SLAs (determinism, max tokens/context).  ￼  ￼

⸻

ADR-0014 — AI-augmented development workflow & toolchain

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Use ADRs, RFC 2119, Conventional Commits, SemVer; MODE toggles.  ￼
Options: Copilot/Codeium + Aider + pre-commit + GHA (aggregate/history).  ￼
Decision: Adopt VS Code; permit Copilot or Codeium; mandate Aider; enforce pre-commit; Conventional Commits; GitHub Actions CI (as governance).  ￼
Consequences: Faster iteration with quality gates and reproducibility.  ￼
Links → ARCHITECTURE.md: Determinism expectations (seed/quantization).  ￼
Links → INTERFACES.md: (No direct CLI surface; governance in README.)  ￼

⸻

ADR-0015 — Retrieval backend: Local Vector DB vs hosted cloud

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Support both local and cloud retrieval paths in CLI.  ￼
Options: Local only; cloud only; switchable per command.  ￼
Decision: Keep local default; allow cloud via --retriever cloud with --allow-cloud.  ￼  ￼
Consequences: Local-first; explicit consent and observability for cloud runs.  ￼
Links → ARCHITECTURE.md: Memory local + optional hybrid retrieval (redacted chunks only).  ￼
Links → INTERFACES.md: chatx query … --retriever local|cloud [--allow-cloud].  ￼

⸻

ADR-0016 — iMessage PDF ingestion — Text-first with OCR fallback

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: Architecture favors DB-first iMessage extraction; PDF handling (if any) is fallback to preserve fidelity.  ￼
Options: Text layer vs OCR/vision fallback (implied by transform stage).  ￼
Decision: Prefer DB-first; where PDFs are used, extract text if present; otherwise allow OCR fallback; then JSONL → redact → index.  ￼  ￼
Consequences: Faster/cleaner on text; graceful fallback when needed.  ￼
Links → ARCHITECTURE.md: iMessage Key Flow (DB-first).  ￼
Links → INTERFACES.md: (No dedicated ingest <pdf> command; downstream transform --to jsonl exists.)  ￼

⸻

ADR-0017 — Enrichment SLAs & safety limits (cloud off by default)

Status: Proposed | Owner: You | Date: 2025-08-15 PT.  ￼
Context: SLAs: cloud off by default; deterministic local mode; max tokens 800; context ±2; attachments never uploaded.  ￼
Decision: Enforce --allow-cloud + preflight; validate structured outputs; keep provenance.  ￼
Consequences: Predictable costs/safety; reproducible runs.  ￼
Links → ARCHITECTURE.md: Security defaults; Appendix B steps.  ￼  ￼
Links → INTERFACES.md: SLAs block + preflight cloud command.  ￼
⸻

ADR-0018 — Backfill and Retro-Processing Job

Status: Proposed | Owner: You | Date: 2025-08-16 PT.
Context: Labels and issue definitions may evolve, requiring analytics to update.
Options: Manual re-run of each step vs dedicated backfill pipeline.
Decision: Provide `chatx backfill` to chain transform, label, issues, episodes, and graph rebuild on stored raw data with versioned run_ids.
Consequences: Keeps analytic views current while preserving prior results; consumes extra storage.
Links → INTERFACES.md: chatx backfill --contact <key> [--raw] [--labels].

===END===
