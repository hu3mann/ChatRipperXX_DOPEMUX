# Architecture

## Context
- Privacy‑first CLI that ingests chat exports and runs an offline pipeline.
- Non‑Functional Requirements: local processing only, predictable runtime, strong redaction guarantees, and observable behavior.

## Module Boundaries
- **cli/** — argument parsing, commands
- **core/** — business logic (pure functions where possible)
- **adapters/** — external integrations (HTTP, files, models)
- **tests/** — unit + integration tests

## Data & Flows (sketch)
- **Extract → Transform → Redact → Enrich → Analyze**.
- Extractors pull platform data into canonical JSON.
- Transformers normalize fields and validate against schemas.
- Redaction removes PII before any optional cloud work.
- Enrichment augments messages with LLM‑generated metadata.
- Analysis modules generate reports from enriched artifacts.

## Observability
- Structured JSON logs at INFO level by default, DEBUG for troubleshooting.
- Hook points for metrics backends to track pipeline duration and message counts.

> Update this file when boundaries or flows change. Record critical decisions in ADRs.
