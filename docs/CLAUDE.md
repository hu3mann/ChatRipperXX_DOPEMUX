# CLAUDE.md — Guardrails & Prompts for Agent Work

This file makes the development process **LLM-aware** so Claude follows it consistently.

## Operating Mode
- **Tooling:** Claude Code in VS Code, with **Claude Context (MCP)** for semantic code search and the **GitHub MCP server** for issue/PR automation.
- **Scope:** Implement changes only for the active issue/branch. Avoid repo-wide refactors unless explicitly requested.

## Required Process (per issue)
1. **Read the Issue:** Extract user story and acceptance criteria (Given/When/Then).
2. **Tests First:** Write or update `pytest` tests to reflect acceptance criteria. Do not implement code yet.
3. **Minimal Implementation:** Propose diffs that satisfy the tests without expanding scope.
4. **Refactor:** After green tests, propose small refactors with clear diffs.
5. **Docs & ADRs:** If the change affects architecture or behavior, update `docs/architecture.md` and/or add an ADR.
6. **Commit Rules:** Use **Conventional Commits** (`feat:`, `fix:`, `chore:`). Include short scope and rationale.
7. **PR & CI:** Open PR; ensure `pytest`, `ruff`, and `mypy` pass.

## Prompts
- **Implement from tests:**  
  “Using TDD, here is the failing test and error. Propose the minimal diff to make it pass. Show a unified diff only.”
- **Refactor request:**  
  “Now propose a safe refactor to improve readability without changing behavior. Show diff and rationale.”
- **Docs/ADR update:**  
  “Generate an ADR capturing this decision: context → decision → consequences. File under `docs/adr/` with next ID.”
- **Issue creation (via MCP GitHub):**  
  “Create a GitHub issue titled ‘<title>’ with body including user story and acceptance criteria. Label: `type:feature`.”

## MCP Usage
- **Claude Context:** Use to retrieve relevant code regions before proposing diffs for multi-file changes.
- **GitHub MCP:** Create/update issues, read CI logs, and open PRs when authorized.

## Safety & Boundaries
- Ask for permission before: large refactors, dependency changes, or modifying CI/release workflows.
- Never commit secrets. Respect `.gitignore` and repo policies.
