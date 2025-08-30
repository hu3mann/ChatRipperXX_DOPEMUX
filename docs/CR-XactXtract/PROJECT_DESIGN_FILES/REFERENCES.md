Title: References
Status: Draft | Owner: XtractXact | Last Updated: 2025-08-16 PT

## Canonical References
- **ARCHITECTURE.md** — C4 L1–L2 narrative, key flows (ingest → redact → index → enrich), hybrid cascade (local-first, optional cloud), security boundaries, and canonical message/CU schemas. Also defines cloud prompt constraints (temp ≤ 0.3; max_out ≤ 800).  
  Evidence: Hybrid cascade & Pass B rules; security boundaries; schemas; cloud constraints.

- **INTERFACES.md** — CLI surface area (ingest/transform/redact/index/label/issues/episodes/graph/enrich/query/simulate/reply/tokens/preflight), principles (provenance, local-first, pre-cloud redaction), and SLAs & limits (cloud off by default; context ±2; max_out 800; attachments never uploaded).  
  Evidence: Preflight threshold and CLI; SLAs & limits.

- **NON_FUNCTIONAL.md** — Measurable targets for performance (ingestion, redaction, local/cloud enrichment, indexing), reliability (determinism & idempotency), privacy/security (fine labels local-only; no attachments to cloud), observability (metrics, artifacts), cost (token budgets, caching).  
  Evidence: perf targets; coverage thresholds; artifacts.

- **ACCEPTANCE_CRITERIA.md** — Gherkin stories and DoD spanning Policy Shield, hybrid gating (τ=0.7), schema-locked enrichment with evidence, label-aware retrieval, Issues/Episodes & Temporal Issue Graph, and safe handling of sex-work contexts.  
  Evidence: Policy Shield/coverage; gating rule; schema lock; retrieval; temporal graph; sex-work handling.

- **ADRS.md** — Canonical ADR set: local-first CLI, per-contact Chroma, local embeddings default with cloud optional, Policy Shield before any cloud, and ADR-0011 hybrid cascade (τ=0.7).  
  Evidence: ADR-0011 decision; per-contact Chroma; cloud optional embeddings.

- **README_PROJECT.md** — Purpose, local-LLM-first principle, scope (IN/OUT), and governance standards (ADR/Nygard, RFC 2119, Conventional Commits, SemVer).  
  Evidence: local-LLM-first; governance standards.

- **HISYTORY.md** — Earlier drafts of ACs/NFRs and decisions; useful for provenance and evolution of defaults (e.g., sessionization defaults).

- **CLOUD_ENRICHMENT.md** — Cloud pipeline contract, schemas, field visibility matrix, provenance/shield/merge fields. (Added in this project; external URLs TBD.)

## Requirement Mapping (Spec ↔ Evidence)
| Requirement | Evidence (Doc § / key lines) |
|---|---|
| Policy Shield mandatory before any cloud; coverage ≥ 0.995 (strict ≥ 0.999); hard-fail classes | ARCHITECTURE: Security & Compliance; INTERFACES: preflight; AC: Shield & coverage; NON_FUNCTIONAL: S2/S1 |
| Cloud disabled by default; requires `--allow-cloud` and preflight pass | INTERFACES: SLAs & Limits |
| Hybrid cascade with τ=0.7; record `source=local|cloud` | ADRS: ADR-0011; INTERFACES: Enrichment backends; AC: gating |
| Minimal context (±2 turns), temp ≤ 0.3, max_out ≤ 800 | ARCHITECTURE: Cloud constraints; INTERFACES: SLAs & Limits |
| Attachments never uploaded; fine labels local-only | ARCHITECTURE: Security & Compliance; INTERFACES: SLAs; AC: sex-work & visibility |
| Canonical enrichment schemas (Message/CU) and evidence linking (`map_refs`/`evidence_index`) | ARCHITECTURE: Appendix A (Enrichment) |
| Provenance recorded for every call; deterministic local inference | INTERFACES: Principles; ARCHITECTURE: Operational Concerns |
| Per-contact Chroma collections; local embeddings by default | ADRS: ADR-0002; ARCHITECTURE: Memory |
| Temporal Issue Graph (non-causal) with edges and lags | ADRS: ADR-0009; AC: Temporal Issue Graph |
| Performance targets for ingestion/redaction/local tagging/indexing | NON_FUNCTIONAL: Performance |
| Observability: artifacts (redaction_report.json; validation); metrics | NON_FUNCTIONAL: Observability |
| Governance: ADRs (Nygard), RFC 2119, SemVer, Conventional Commits | README_PROJECT: Governance |

## Artifacts & Schemas (Where to look)
- **Message (pre-redaction)** — Canonical fields for ingestion/transform.  
- **Chunk (LLM-ready; redacted)** — Cloud-eligible text + metadata.  
- **Enrichment (Message)** — speech_act, intent, stance, tone, emotion_primary, certainty, directness, boundary_signal, repair_attempt, inferred_meaning, map_refs, confidence_llm, source.  
- **Enrichment (CU)** — topic_label, vibe_trajectory, escalation_curve, ledgers, evidence_index, confidence_llm, source.  
- **Cloud Enrichment** — Adds provenance, shield, merge, labels (coarse vs fine), relationship and influence fields (see CLOUD_ENRICHMENT.md).

## External Standards & Methods (mentioned in repo)
- **RFC 2119 (MUST/SHOULD/MAY)** — Usage mandated across specs. (Link TBD)
- **C4 Model (Architecture narration)** — Used for level 1–2 description. (Link TBD)
- **Nygard ADRs** — Governance pattern for decisions. (Link TBD)
- **SemVer & Conventional Commits** — Versioning and commit discipline. (Link TBD)

## Traceability Notes
- Acceptance Criteria reference all critical privacy and gating rules; cross-check with INTERFACES (preflight CLI) and ARCHITECTURE (Security & Compliance).  
- ADR-0011 and ARCHITECTURE’s LLM Orchestrator both assert the local-first rule and confidence-based escalation.  
- NON_FUNCTIONAL encodes measurable thresholds used in AC DoD and CI gates.

## Gaps / To add
- External URLs for RFC 2119, C4, Nygard ADRs, SemVer, Conventional Commits (repo mentions them; links not yet embedded).
- Ensure CLOUD_ENRICHMENT.md is linked from INTERFACES and ACs where schemas are referenced.
- Confirm latest Non-Functional targets match hardware baselines and adjust if needed.
