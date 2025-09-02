# ChatX — Project Overview

**Last updated:** 2025-09-02 UTC

## Vision (1‑pager)
- **Problem:** Manual chat forensics is slow, inconsistent, and often leaks sensitive data.
- **Audience:** Digital forensics investigators and privacy‑minded power users.
- **Non‑Goals:** Real‑time surveillance, cloud‑first processing, or vendor‑locked features.
- **Success Metrics:** Pipeline handles 100 messages in <2 s, test coverage ≥90%, zero P1 issues per release.

## MVP Scope
- Link to tracked **User Stories** in GitHub Issues (Now/Next/Later).
- Each story includes **acceptance criteria** written in Given/When/Then and mirrored in tests.

## Process (TDD + Agent-in-the-loop)
1. Write a **failing pytest** from the story’s acceptance criteria.
2. Use **Claude Code** with **Claude Context (MCP)** to implement only what’s needed.
3. Make tests **green**, then **refactor**.
4. Update docs + ADRs; commit with **Conventional Commits**.
5. Open PR; CI runs (**pytest**, **ruff**, **mypy**). Merge when green.

> See `CLAUDE.md` and `CONTRIBUTING.md` for exact prompts and guardrails.
