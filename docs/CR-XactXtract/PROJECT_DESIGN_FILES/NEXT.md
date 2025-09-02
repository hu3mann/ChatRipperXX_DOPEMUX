Title: NEXT
Status: Draft | Owner: You | Last Updated: 2025-08-16 PT

## Open 
- Detector thresholds default? (conservative start; unit tests)
- Episode hysteresis per platform?
- Default chunking: ✅ turns:20, stride:10 (dense) | daily (sparse)
- Local model shortlist and quantization settings: ✅ gemma-2-9b-q4_K_M

- NUANCE_LEVEL default: CONFIRM `balanced` as the default for cloud prompting.
- Label taxonomies: Lock enums for `relationship_structure`, `relationship_dynamic`, and `influence_class`; finalize `labels.yml` coarse/fine sets.
- Confidence calibration: Document how `confidence_llm` is computed and calibrated across local vs cloud; add acceptance thresholds.
- Retro-processing policy: Define when new issues/labels trigger backfill and how to version results.
- Cloud provider allowlist: Confirm which providers MAY be used (`openai|anthropic|…`) and how we rotate/pin models.
- Hard-fail classes: Publish the canonical list and remediation response for each failure type.
- Idempotency & cache: Confirm `source_hash` composition and cache invalidation rules on schema/model/prompt changes.

## Next Actions (Prioritized)
1) **Policy Shield module (MUST)** — Implement pseudonymization, opaque tokens, coverage meter (≥0.995; strict 0.999), hard-fail classes, and emit `redaction_report.json`. Wire into `chatx preflight cloud`. 
2) **Local enrichment backend (MUST)** — Add on-device LLM client (e.g., Ollama) returning schema-locked Message/CU JSON with fixed seed, temp=0, streaming disabled. Compute `confidence_llm` and gate cloud.
3) **Hybrid cascade routing (MUST)** — Enforce τ=0.7, block cloud unless `--allow-cloud` + preflight pass; tag `source = local|cloud`; persist `merge.*` provenance.
4) **Schema validators (MUST)** — Implement JSON Schema/Pydantic validators for Message Enrichment and CU Enrichment; clamp enums and [0,1] bounds; drop invalid rows.
5) **Index & retrieval (SHOULD)** — Chroma per-contact collections; index redacted chunks + enrichment facets; enable label/time filters; default local embeddings.
6) **Tests & CI (MUST)** — Golden fixtures; AC Gherkin tests (visibility, provenance/shield, merge provenance, influence, relationship); performance smoke (≥25 msg/s local); fail on coverage <0.995, leak, or schema violation.
7) **Field visibility enforcement (MUST)** — Assert `fine_labels_local` and attachments never appear in any cloud prompt; add E_VISIBILITY_LEAK checks.
8) **Docs & ADRs (SHOULD)** — Reconcile/number ADR-0001…; mark superseded drafts; add NUANCE_LEVEL and influence taxonomy to ADRs; update README examples.
9) **Telemetry & cost (SHOULD)** — Persist `token_usage`, `latency_ms`; add `tokens inspect` workflow; batch controls + backoff.
10) **Retro-processing job (MAY)** — Implement backfill job when new issues/labels are added; update Temporal Issue Graph edges.

## Decision Backlog
- Approve default local model (`gemma2:9b` IT, 4-bit) and pin build.
- Approve NUANCE_LEVEL=balanced as default.
- Approve canonical hard-fail classes & error codes (E_PRECHECK_COVERAGE_LOW, E_HARDFAIL_CLASS, E_UNALLOWED_CLOUD, E_SCHEMA_INVALID, E_VISIBILITY_LEAK, E_IDEMPOTENCY_MISMATCH, E_ATTACHMENT_PRESENT).
- Approve acceptance of `provenance`, `shield`, and `merge` as mandatory fields in enrichment outputs.
- Approve performance targets (extraction ≥5k msgs/min; local tagging ≥25 msgs/s; rollups ≤5s/50k; graph ≤10s/50k).

## Changes Since Last Update
- 2025-08-16: **CLOUD_ENRICHMENT.md** expanded with `provenance`, `shield`, `merge`, influence/relationship fields, and JSON Schemas; field-visibility matrix added.
- 2025-08-16: **INTERFACES.md** updated to mirror enrichment fields, error codes, and visibility rules; enriched CLI contracts clarified.
- 2025-08-16: **ACCEPTANCE_CRITERIA.md** extended with Gherkin for field visibility, provenance/shield, merge provenance, influence scoring, relationship labels, idempotency, and minimal-context checks.
- 2025-08-15: Architecture, ADRs, and NFRs aligned on local-first hybrid cascade, mandatory Policy Shield, schema-locked outputs, and temporal analytics foundation.

