@docs/README.md
@docs/architecture.md
@docs/interfaces.md
@docs/acceptance-criteria.md
@docs/development/test-strategy.md
@docs/operations/non-functional-requirements.md

# CLAUDE.md — ChatX/ChatRipper + MCP Playbook
Status: Draft | Owner: <TBD> | Last Updated: 2025-09-02

## Purpose
Make Claude Code produce **small, correct patches** that build and pass on the first run, while leveraging **Model Context Protocol (MCP)** servers for persistent memory, context injection, search, and integrations. This file is auto-loaded as project memory at session start; the `@…` imports above bring key specs into context without copy-pasting.

## Editing policy
- In Claude Code sessions (terminal): you may edit files directly or return a unified diff (we'll apply with `git apply`).
- In web/chat sessions: return a Repo Prompt XML edits document (see `docs/repo-prompt-xml.md`) and we'll apply via Repo Prompt's Apply tab or MCP tool.

---

MCP: Open User Configuration
User = default_user

1. On every interaction, retrieve all relevant memory.
2. When new facts show up, store them (identity, behavior, preferences, goals, relationships).
3. Use the “memory” server to persist; use “sequentialthinking” when multi‑step reasoning is needed.
4. Keep queries concise and sexy as hell.


## 0) Session bootstrap (Claude, do this first)
1. **Summarize the task** in ≤5 bullets and list impacted files.
2. Enter **Plan Mode** and propose a minimal, **test-first** approach (no edits/exec yet).
3. Confirm constraints: language/runtime, lint/type/test gates (≥90% coverage), interfaces/SLA, schemas, **RFC-7807** errors.
4. Propose **tests under `tests/**`**; request permission to write tests only; run them and show failures.
5. Propose a **minimal patch** to `src/**` to make tests pass. Re-run ruff + mypy + pytest.
6. When green: **refactor → docs → ADR stub → small, titled commit**.

---

## 1) MCP servers & tools (what's available)
MCP provides a standard "USB-C for AI" to connect tools and data sources. Claude Code can add servers from JSON and use them in sessions.

**Categories & examples (installed via `scripts/setup_mcp_servers.sh`):**
- **Persistence**
  - *Memory Bank* — structured memory across slices (notes/decisions).
  - *Knowledge Graph Memory* — facts + relationships, semantic queries.
  - *Vector Memory* — Chroma/pgvector embeddings for recall.
- **Context & Planning**
  - *Context7* — up-to-date API/framework docs injection.
  - *Sequential Thinking* — structured multi-step reasoning to break down tasks.
- **Search**
  - *Exa* — web search with caching; **DuckDuckGo** as privacy fallback.
- **Integration**
  - *GitHub* — read/modify files, branches, PRs.
  - *Filesystem* — project file ops.
  - *Notion* — docs & DBs (project log, decisions).
  - *Pandoc* — convert docs (MD/HTML/PDF/Word).
  - *MCP Compass* — discover additional servers.

> Use `claude mcp list`, `claude mcp add-json <name> '<json>'`, `claude mcp get <name>` to manage servers.

---

## 2) Development workflow (slice-based with MCP)
**Plan** — Call **Sequential Thinking** to outline the slice; use **Context7** to fetch current API docs. Store AC and open questions in **Memory Bank**.  
**Persist** — Record user stories, decisions, and facts in Memory/Graph stores; retrieve at the start of each slice to avoid prompt repetition and token waste.  
**Implement & Test** — Use **Filesystem/GitHub** MCP servers to read/edit. **Write tests first**, implement minimal changes, run tests and iterate. For research, use **Exa** or **DuckDuckGo**. For schema conversions/export, call **Pandoc**.  
**Document** — Update repo docs and Notion; append decisions to Memory Bank/Graph.  
**Discover** — Use **MCP Compass** to find servers; install only with approval.  
**Manage Context** — Keep prompts short; refer to stored memories instead of pasting history.

---

## 3) Permissions & safety (least privilege)
Use project settings + hooks to control tools. Inspect and tweak permissions in `/permissions`; settings resolve user → project → local.

**Rules (enforced by `.claude/settings.json` + hooks):**
- Allowed: read, edits in `src/**` and `tests/**`, and specific Bash tools: `python`, `pip`, `pytest`, `ruff`, `mypy`, `git status/diff/add/commit`.
- Ask: `git push`.
- Deny: `rm`, `sudo`, generic network (`curl`/`wget`), reading `.env` or `secrets/**`.
- Prefer **explicit** allow entries (e.g., `Bash(pytest:*)`) rather than `Bash(*)`.
- Hooks run on **PreToolUse**/**PostToolUse** to block risky calls and enforce lint/type/test gates after edits.

---

## 4) Modes & flags that matter
- Start complex work in **Plan Mode** (read-only), then elevate when ready.  
- Resume work with `claude --continue` or `claude --resume <id>`.  
- Keep outputs token-efficient: summaries → minimal diffs (avoid whole-file dumps).

---

## 5) TDD loop (what "good" looks like)
1) Read **AC** + **Interfaces** (already imported above).  
2) Generate failing tests (unit + schema validation + **RFC-7807** negative paths).  
3) Local checks:
```bash
python -m pip install -e .[dev]
ruff check .
mypy src
pytest --cov=src --cov-fail-under=90
```
4) Minimal code → pass tests → refactor → docs → ADR.

---

## 6) Diff etiquette
- Propose **unified diffs**, smallest viable hunks.  
- Only touch files you list; separate config/CI changes into their own tiny patch with rationale.

---

## 7) Slash commands (kept in `.claude/commands/`)
- `/plan-slice` — 10-bullet technical plan + risks + test checklist.  
- `/tdd-loop` — tests → minimal patch → re-run checks (ruff/mypy/pytest ≥90%).  
- `/security-review` — check last diff for secrets/PII exfil/unsafe shell/network/schema drift.  
- `/hooks` — manage hooks; `/permissions` — view/adjust tool rules.

---

## 8) Model selection (router-aware)
- **Local Gemma via Ollama** — default for routine coding/testing.  
- **Claude Sonnet** — when local confidence is low or slice spans many files.  
- **Claude Opus** — heavy reasoning (architecture/design tradeoffs).  
- Optionally let a router select based on task complexity and context.

---

## 9) MCP quick reference
- List servers: `claude mcp list`  
- Add from JSON: `claude mcp add-json <name> '<json>'`  
- Inspect: `claude mcp get <name>`  
- Remove: `claude mcp remove <name>`

---

## 10) Definition of Done
- Lint, types, tests **green**; coverage **≥ 90%** for changed code.  
- JSON/HTTP **schemas valid**; errors are **RFC-7807** problem+json.  
- Behavior documented; ADR stub added if design shifted; commit message is clear and scoped.

---

## Updating this file
Keep MCP server entries and env requirements in sync with `scripts/setup_mcp_servers.sh`. Add new servers only with explicit approval.
