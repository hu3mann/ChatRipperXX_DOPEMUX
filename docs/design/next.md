Title: NEXT
Status: Draft | Owner: You | Last Updated: 2025-09-02 PT

## Open Questions

* iMessage iCloud completeness automation: What OS-supported or acceptable method will we implement to **force download** all evicted attachments at scale? (Manual = OK short-term).
* Voice note transcription: Choose local engine (e.g., Whisper variants), language coverage, quality/latency targets, and evaluation set.
* iPhone USB path: Which acquisition tool/UX do we standardize for backups (and required prompts/permissions)?
* Output layout & retention: Set workspace layout for `out/attachments/**`, hashing strategy, and default retention policy.
* Detector thresholds: What SHOULD the default detector thresholds be for each coarse label family (conservative vs balanced)? Capture as config + unit tests.
* Episode hysteresis: SHOULD episode start/stop rules vary by platform (iMessage vs Instagram vs WhatsApp)? Define per-source defaults.
* Default chunking: SHOULD we default to chunks of ±40 turns or daily windows per density? Confirm and codify.
* Local model default & quantization: PROPOSE `gemma2:9b` (IT) at 4-bit; CONFIRM as the project default and pin build hashes.
* NUANCE_LEVEL default: CONFIRM `balanced` as the default for cloud prompting.

## Next Actions

* Implement attachments metadata + `--copy-binaries` and completeness report.
* Implement `--transcribe-audio local` path with deterministic, local transcription (mock in tests, engine chosen via ADR).
* Wire schema validation & quarantine; perf smoke; CI gates per TEST_STRATEGY.md.
* Draft ADRs for transcription engine and iCloud/USB acquisition UX.

## Changes Since Last Update

* 2025-09-02: Implemented initial iMessage extractor with reaction folding, reply resolution, and attachment metadata; added unit and integration tests.
* 2025-08-16: **CLOUD_ENRICHMENT.md** expanded with `provenance`, `shield`, and confidence calibration details; added field-visibility matrix.
* 2025-08-16: **INTERFACES.md** updated to mirror enrichment fields, error codes, and visibility rules; enriched CLI contracts clarified.
* 2025-08-16: **ACCEPTANCE_CRITERIA.md** extended with Gherkin for chunking, relationship labels, idempotency, and minimal-context checks.
* 2025-08-15: Architecture, ADRs, and NFRs aligned on local-first operation, Policy Shield, schema-locked outputs, and temporal analytics foundation.
