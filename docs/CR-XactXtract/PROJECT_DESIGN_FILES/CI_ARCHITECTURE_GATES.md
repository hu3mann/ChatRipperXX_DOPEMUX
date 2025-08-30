Title: Architecture Gates — CI Checklist
Status: Draft | Owner: You | Last Updated: 2025-08-16 PT

## Purpose
Automate enforcement of architectural invariants: **redaction coverage**, **hybrid gating**, **schema validity**, **visibility rules**, **determinism/idempotency**, and **observability**.

## Inputs & Artifacts
- Raw exports under `./data/` (fixture corpus)
- Redacted windows under `./out/redacted/`
- Enrichment outputs: `./out/enrich/enrichment_*.jsonl`
- Reports: `redaction_report.json`, `validation.json`, `run_report.json`
- Schemas in repo (`schemas/*.json` or embedded in code)

## Mandatory Gates (MUST)
1) **Preflight Coverage**
   - Command: `chatx redact --strict --report ./out/redaction_report.json`
   - Check: coverage >= **0.995** (strict >= **0.999**)
   - Fail Codes: `E_PRECHECK_COVERAGE_LOW`, `E_HARDFAIL_CLASS`

2) **Visibility Linter**
   - Assert no `fine_labels_local` or attachments are present in any **cloud** prompt or payload.
   - Fail Code: `E_VISIBILITY_LEAK`, `E_ATTACHMENT_PRESENT`

3) **Hybrid Gating**
   - With `--backend hybrid --tau 0.7`, ensure cloud is **not** called when local `confidence_llm >= τ`.
   - Ensure cloud is only called if `--allow-cloud` **and** preflight passed.
   - Provenance fields `merge.source_last_enrichment` and `merge.reason` MUST be present.

4) **Schema Validity**
   - Validate Message/CU enrichments against JSON Schemas; enums clamped; [0,1] bounds enforced.
   - Fail Code: `E_SCHEMA_INVALID`

5) **Determinism & Idempotency**
   - Re-run local enrichment on identical redacted inputs; expect cache hit or identical outputs.
   - Keys: `(model_id, model_sha, prompt_hash, source_hash, schema_v)`.

6) **Performance Smoke**
   - Local enrichment throughput ≥ **25 msgs/s** on reference machine (p95 ≤ 250ms/msg).

7) **Observability Presence**
   - Required metrics present: coverage, throughput/latency, token_usage, cache_hit_ratio, schema_invalid_count, visibility_leak_count.
   - Required artifacts present: `redaction_report.json`, validation summary, run report.

## Nice-to-Have (SHOULD)
- `tokens inspect` budget report under `./out/metrics/`
- Retrieval latency sampler (p95 ≤ 150ms) on 10k random queries

## Example Commands
```bash
chatx redact --input ./out/chunks/*.json --pseudonymize --opaque --strict --report ./out/redaction_report.json
chatx enrich messages --contact "fixture" --backend hybrid --tau 0.7 --context 2 --max-out 800
chatx validate --schemas ./schemas --inputs ./out/enrich/*.jsonl --report ./out/validation.json
chatx metrics summarize --inputs ./out/metrics/*.jsonl --out ./out/reports/run_report.json
```

- **Index-Update Embedding Guard:** `chatx index update` **MUST NOT** modify embeddings nor chunk `text`. CI runs a smoke test that attempts a text/embedding change and expects `POLICY_EMBEDDING_IMMUTABLE`.
