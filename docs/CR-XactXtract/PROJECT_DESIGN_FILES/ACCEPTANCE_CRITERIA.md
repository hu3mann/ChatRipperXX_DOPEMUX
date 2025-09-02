Title: Acceptance Criteria
Status: Draft | Owner: You | Last Updated: 2025-08-16 PT

## User Stories (Gherkin)

### Story: Extract iMessage for a single contact with replies, reactions, and provenance
- AC:
  - Given a valid `chat.db` copied to a temp path,
    When I run `chatx imessage pull --contact "<id>" [--include-attachments]`,
    Then messages MUST include `is_me`, ISO-8601 timestamps, folded reactions, stable `reply_to_msg_id` for replies, attachment references (no binaries), and provenance (`source_ref`).

### Story: Extract Instagram DM for a username
- AC:
  - Given an Instagram data ZIP with `messages/inbox/<thread>/message_*.json`,
    When I run `chatx instagram pull --contact "<user>" --zip ./instagram.zip`,
    Then all parts MUST merge and sort ascending, likes/reactions MUST be folded, and media MUST be referenced (no uploads).

### Story: Transform raw extracts to Dialogue JSONL and chunked blocks
- AC:
  - Given extractor JSON,
    When I run `chatx transform --to jsonl [--chunk turns:40|daily] --contact "<key>"`,
    Then output MUST be one JSON object per line with fields {msg_id, conv_id, platform, sender, sender_id, is_me, timestamp, text, reply_to_msg_id?, reactions[], attachments[], source_ref}.
  - Given Dialogue JSONL,
    When I run chunking,
    Then Chunked Blocks MUST include `chunk_id`, `conv_id`, concatenated `text`, and `meta` with {contact, date_start, date_end, platform, labels_coarse?, episode_ids?}.

### Story: Policy Shield redaction before any cloud operation
- AC:
  - Given redaction thresholds (default 0.995; strict 0.999),
    When any task requests cloud (`--allow-cloud` true or HTTP `allow_cloud=true`),
    Then a preflight MUST pass on **redacted** inputs; hard-fail classes MUST be blocked; fine labels MUST remain local-only; attachments MUST never be uploaded.

### Story: Index and retrieval with label/time filters
- AC:
  - Given redacted chunks,
    When I run `chatx index --store chroma --collection chatx_<contact>`,
    Then the collection MUST support metadata filters by contact, date range, and coarse labels.
  - Given an indexed collection,
    When I run `chatx query "<question>" --contact "<key>" [--since --until] [--labels-any --labels-all --labels-not] --k 32`,
    Then the answer MUST include citations to retrieved chunks/messages and MUST honor the filters.

### Story: Local-first enrichment with optional hybrid escalation
- AC:
  - Given `--backend local|hybrid` and τ=0.7,
    When local `confidence_llm ≥ τ`,
    Then NO cloud call occurs.
  - Given `confidence_llm < τ` and `--allow-cloud`,
    When preflight passes on redacted windows,
    Then a cloud pass MAY run; results MUST merge with provenance (`source: local|cloud`) and confidence recorded.

### Story: HTTP API — Query (dev-only server, loopback)
- AC:
  - Given the HTTP server is enabled and bound to 127.0.0.1,
    When I `POST /v1/query` with JSON {contact, question, filters?, k?, retriever?, allow_cloud?},
    Then the server MUST return a 200 JSON body: {answer, citations[], retrieval, metrics}.
  - Citations MUST be non-empty unless the server returns a refusal with an error status.
  - Filters MUST be honored (time range and **coarse** labels only).
  - If `X-Request-Id` is supplied, the server MUST echo it.

### Story: HTTP API — Simulate
- AC:
  - Given the HTTP server is enabled and bound to 127.0.0.1,
    When I `POST /v1/simulate` with {contact, scenario, allow_cloud?},
    Then the server MUST return 200 with {simulation, evidence_refs[]} tied to chunk/message ids.

### Story: HTTP API — Reply
- AC:
  - Given a message window and selected tone,
    When I `POST /v1/reply` with {contact, message_id, tone, allow_cloud?},
    Then the server MUST return 200 with {suggested_reply, citations[]} grounded in recent context.

### Story: Retro backfill with updated labels
- AC:
  - Given raw messages for a contact and a revised `labels.yml`,
    When I run `chatx backfill --contact "<id>" --raw <file> --labels <labels.yml>`,
    Then outputs MUST be written under a new `run_id` without overwriting prior data, and new labels MUST appear in issues and the graph.

## System-Level Scenarios

### S1 — Determinism and provenance
- Given local runs,
  When streaming is disabled and seeds are fixed,
  Then enrichments and chunking MUST be reproducible; all outputs MUST carry provenance (contact, platform, source_ref).

### S2 — Privacy & safety
- Cloud MUST be off by default.
- Redaction MUST precede any cloud call (preflight required); attachments MUST never be uploaded.
- Fine-grained labels MUST remain local-only; only coarse facets MAY be used for cloud filters.

### S3 — Performance & scalability
- Extraction SHOULD reach ≥5k msgs/min/contact on a modern laptop.
- Detectors SHOULD process ≥200 msgs/s locally (quantized).
- Weekly rollups SHOULD complete in ≤5s for 50k messages; graph build ≤10s/50k.
- CLI operations SHOULD complete under ~60s for 10k messages/contact on M‑series (tunable by batch/parallelism).

### S4 — Observability
- Each run MUST emit structured logs and artifacts (e.g., `redaction_report.json`, enrichment validation, coverage metrics).

### S5 — HTTP SLA & Error model
- Each HTTP request MUST complete in ≤60 seconds or stream partials; otherwise the server MUST return a `TIMEOUT` error.
- Error responses MUST be RFC‑7807 JSON with fields: `error`, `code`, `detail`, `hint`.
- The server MUST implement at least the following machine-readable codes:
  - `INVALID_INPUT` (schema/field errors)
  - `INVALID_CONTACT` (unknown contact or bad window)
  - `POLICY_SHIELD_FAILURE` (preflight failed / hard‑fail content)
  - `CLOUD_DISABLED` (cloud requested when disabled or not explicitly allowed)
  - `TIMEOUT` (exceeded SLA without streaming)
  - `INTERNAL` (unexpected failure; SHOULD echo `X-Request-Id`)

## Exit Criteria (Definition of Done)
- ✅ iMessage & Instagram extractors pass golden fixtures (replies, reactions, provenance, attachment refs).
- ✅ Transform & chunking produce schema-valid JSONL and Chunked Blocks.
- ✅ Policy Shield preflight enforces coverage ≥0.995 (≥0.999 strict) and blocks hard-fail classes.
- ✅ Indexing enables time/label filters; queries return answers WITH citations.
- ✅ Enrichment cascade obeys τ gate; provenance (`source`) recorded.
- ✅ HTTP server (if enabled) binds to 127.0.0.1 and fulfills Query/Simulate/Reply contracts above with required error handling.
- ✅ Observability artifacts are produced; all tests/linters/type checks pass; new code ≥90% coverage.

## Label Taxonomy Scenarios (New)

### S6 — Coarse vs Fine data egress
- Given a labeled dataset with both `coarse` and `fine_local_only` tags,
  When the system prepares any cloud-bound prompt or payload,
  Then ONLY `coarse` labels MAY be present and `fine_local_only` labels MUST be excluded.

### S7 — Placeholder mapping
- Given raw text that matches `placeholders.yml` patterns (e.g., SUBSTANCE_USE_PSYCHEDELICS),
  When Policy Shield runs,
  Then redaction MUST replace matched spans with placeholders and map them to the configured **coarse** label (e.g., `substance_influence_psychedelics`).

### S8 — Mutual exclusion
- Given the relationship structure labels,
  When labeling a single span,
  Then labels in the mutual exclusion set (monogamy|open|polyamory|swinging) MUST NOT co-exist on the same span.

### S9 — Co-occurrence hints
- Given a span with `chemsex_context`,
  When co-occurrence rules apply,
  Then detectors SHOULD elevate likelihood for `kink_context` and at least one `substance_influence_*` label in adjacent spans.

### S10 — False-positive notes are honored
- Given a span mentioning jealousy toward a celebrity/movie character,
  When labeling runs,
  Then the `jealousy` label SHOULD be suppressed unless there are adjacent relational cues.

### S11 — Aliases remain backward compatible
- Given older labeled data using `togetherness`, `substances`, or the mis-typed `attention_availare_bility`,
  When importing or re-labeling,
  Then the pipeline MUST map them to `intimacy_connection`, `substance_influence_generic`, and `attention_availability` respectively.

### S12 — Influence classes export (cloud-safe)
- Given an enrichment summary for cloud escalation,
  When summarizing influence classes,
  Then the system MAY export only the enumerated `influence_classes` value (e.g., `stimulants`) and MUST NOT export any **fine** compound detail.


## Story: Merge enrichment metadata without re-embedding
- **As a** data analyst
- **I want** to apply enrichment outputs as metadata onto existing indexed chunks
- **So that** retrieval can filter/sort by those attributes without recomputing embeddings

**AC:**
  - **Given** a populated Chroma collection `chatx_<contact>` built from redacted chunks
  - **And** valid `enrichment_message.jsonl` and/or `enrichment_cu.jsonl`
  - **When** I run `chatx index update --collection chatx_<contact> --enrich-msg ./out/enrich/enrichment_message.jsonl --enrich-cu ./out/enrich/enrichment_cu.jsonl`
  - **Then** the tool **MUST** validate each line against its JSON Schema
  - **And** it **MUST** upsert only metadata fields onto the matched chunks (by `message_ids[]` or `evidence_index[]`)
  - **And** it **MUST NOT** change embeddings or chunk `text`
  - **And** it **MUST** emit `out/reports/index_update_report.json` with counts
  - **And** a subsequent `chatx query ... --labels-*` **SHOULD** filter on newly upserted labels
  - **And** attempting to alter embeddings or `text` **MUST** error `POLICY_EMBEDDING_IMMUTABLE`
