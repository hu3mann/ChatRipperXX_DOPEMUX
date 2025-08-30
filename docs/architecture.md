# Architecture

## Context
- CLI entrypoint, core modules, adapters (I/O, API), and persistence (if any).
- Non‑Functional Requirements: performance, robustness, security, observability.

## Module Boundaries
- **cli/** — argument parsing, commands
- **core/** — business logic (pure functions where possible)
- **adapters/** — external integrations (HTTP, files, models)
- **tests/** — unit + integration tests

## Data & Flows (sketch)
- Describe request/response, error flows, and where side effects occur.

## Observability
- Logging levels and structure, metrics (if any).

> Update this file when boundaries or flows change. Record critical decisions in ADRs.
