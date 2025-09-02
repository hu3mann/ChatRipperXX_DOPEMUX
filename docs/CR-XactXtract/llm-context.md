# LLM Context (Design & Development)
Status: Draft | Owner: <<Name>> | Last Updated: 2025-08-30 PT

## 1. Purpose
This document anchors how Large Language Models (LLMs) are used in the **design and development** of ChatX/XtractXtract.
It is **not** a runtime prompt for RAG/querying; it defines guardrails, workflows, and policies for collaboration with the LLM during architecture, spec writing, and code generation.

## 2. Core Principles
- **Grounded in project files only.** LLM responses MUST cite filenames/sections. If unknown, write “Unknown — needs source” and add to NEXT.md.
- **Append-only policy.** Never delete or summarize existing content. New information MUST be appended.
- **Diff-first updates.** Existing files are only modified through minimal unified diffs.
- **TDD workflow.** Tests are written before code. Coverage ≥ 90%.
- **Determinism & safety.** No secrets in code. Emit `.env.example`. Schema-validate all JSON outputs.
- **Conventional Commits & SemVer.** All commits MUST follow `feat|fix|docs|refactor|test|chore`.

## 3. Files of Record
These are the authoritative sources of truth:
- **ARCHITECTURE.md** — C4 narrative, flows, security, ops.
- **ADRS.md** — Architecture Decision Records (Nygard style).
- **INTERFACES.md** — CLI/HTTP contracts, schemas, error models.
- **ACCEPTANCE_CRITERIA.md** — Gherkin user stories.
- **NON_FUNCTIONAL.md** — SLAs, performance, observability, compliance.
- **CI_ARCHITECTURE_GATES.md** — Quality gates enforced in CI.
- **NEXT.md** — Open questions, TODOs, decision backlog, change log.
- **schemas/** — JSON Schemas (Draft 2020-12) for messages, chunks, enrichment, redaction, metrics, errors, reports.
- **labels.yml** / **placeholders.yml** — Taxonomies for labeling and redaction.
- **REFERENCES.md** — Canonical references, requirement mapping.

## 4. Workflow for LLM Interaction
1. **Confirm objective** in one line.
2. **State assumptions & open questions.**
3. **Produce artifact/code** (tests first).
4. **Provide unified diffs** for edits to existing files.
5. **For new files**, output wrapped as:
   ```
   ===FILE: <path>===
   <content>
   ===END===
   ```
6. **List next actions** as a short, numbered plan.

## 5. Editing & Update Policy
- Only **append** to docs (ADRs, NEXT, REFERENCES, etc.). Never summarize, never remove.
- Only **diffs** for edits.
- Always **cite project docs**.
- Never overwrite history.

## 6. JSON Schema Guidance
- Always use **Draft 2020-12**.
- MUST include `$schema` and `$id`.
- Explicitly declare `required`.
- Use `additionalProperties: false` where possible.
- Modularize large schemas with `$ref`.
- Validate all produced JSON against schemas in tests.

## 7. Prompting Rules for Development
- Always cite project docs in reasoning.
- Always check schemas before emitting code.
- Use RFC 2119 terms (MUST, SHOULD, MAY).
- Only propose code in **CODEGEN mode**.
- Structured outputs for configs and API payloads.
- Reject or error if instructions violate append-only or diff-first policies.

## 8. Update Workflow (Local Dev)
- Upload current files or repo snapshot.
- LLM generates unified diffs.
- Apply with:
  ```zsh
  pbpaste > patch.diff && git apply --index --whitespace=fix patch.diff && git commit -m "chore: apply patch"
  ```
- If context drift, use `git apply --3way` to merge safely.
- `.gitattributes` MUST normalize line endings to LF to avoid patch errors.

## 9. Append-only Recordkeeping
- ADRs: add new ADR files sequentially.
- NEXT.md: append new questions/actions; never remove old ones.
- REFERENCES.md: add new mappings; never remove old ones.
- INTERFACES.md/ARCHITECTURE.md/etc.: modify only via diffs that preserve existing content.
