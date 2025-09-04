# CLAUDE.md — ChatX/ChatRipper MCP Playbook
Status: Compact | Owner: <TBD> | Last Updated: 2025-09-03

## Purpose
Produce **small, correct patches** that build and pass first run, leveraging **MCP** for persistent memory, context injection, search, and integrations. Auto-loaded as project memory; see `docs/` for full architectural specs.

## Editing Policy
- **Terminal sessions**: Edit files directly or return unified diff (apply with `git apply`)
- **Web/chat sessions**: Return Repo Prompt XML edits document

---

## MCP User Configuration
**User = default_user**
1. On every interaction, retrieve all relevant memory
2. Store new facts (identity, behavior, preferences, goals, relationships)
3. Use **openmemory (Mem0)** for decisions/caveats; **server-memory** for short-lived notes; **memory-bank** for curated patterns
4. Use **sequential_thinking** for multi-step reasoning
5. Keep queries concise

## MCP Servers Available
**Persistence**: OpenMemory (cross-session), Server-Memory (scratch), Memory-Bank (patterns/runbooks)  
**Context & Planning**: Context7 (API docs), Sequential Thinking (reasoning), Claude-Context (semantic code search)  
**Search**: Exa (high-signal dev search), DuckDuckGo (broad fallback)  
**Integration**: GitHub (issues/PRs/code), Filesystem (local file ops), Conport (services/ports)

> Manage: `claude mcp list|add-json|get|remove`

---

## Development Workflow (Slice-based)
**/bootstrap** → preflight: summarize task (≤5 bullets), fetch hot files, get API docs, query memory, confirm constraints, propose tiny test-first plan  

**Research** → `/research` pulls **context7** (APIs) + **exa** sources → synthesize requirements + risks  
**Story** → `/story` converts research → user story + AC + non-functional constraints → **memory-bank**  
**Plan** → `/plan` uses **sequential_thinking** → ≤5 steps mapping to files + tests  
**Implement** → `/implement` writes tests first, minimal edits via **local_files**, runs checks, loops until green  
**Debug** → `/debug` narrows repro, instruments, proposes smallest fix + cites **context7** API behavior  
**Ship** → `/ship` updates docs + ADR stubs + **Mem0** decisions + small commit  
**Switch** → `/switch` compacts slice state → **Mem0** + **memory-bank**, clears transient memory

---

## Permissions & Safety (Least Privilege)
**Rules (`.claude/settings.json` + hooks):**
- ✅ **Allowed**: read, edits in `src/**` + `tests/**`, specific tools: `python`, `pip`, `pytest`, `ruff`, `mypy`, `git status/diff/add/commit`
- ❓ **Ask**: `git push`
- ❌ **Deny**: `rm`, `sudo`, generic network (`curl`/`wget`), reading `.env` or `secrets/**`
- **Prefer explicit** allow entries (e.g., `Bash(pytest:*)` not `Bash(*)`)
- **Hooks** run Pre/PostToolUse to enforce lint/type/test gates

---

## Core Project Constraints
- **Privacy**: Policy Shield ≥99.5% coverage (≥99.9% strict), attachments NEVER cloud, local-first processing with optional cloud via `--allow-cloud`
- **Quality**: lint + mypy clean + pytest (≥60% coverage), RFC-7807 problem+json errors, JSON schema validation
- **Models**: Local Gemma-2-9B (temp≤0.3, streaming off, fixed seed) default; cloud escalation requires explicit consent
- **TDD**: tests → minimal code → pass → refactor → docs → ADR
- **Diffs**: unified diffs, smallest viable hunks, separate config changes with rationale

---

## Slash Commands
**Core Workflow**:
- `/bootstrap` — session preflight (context gather + constraints + tiny plan)
- `/research` — API/doc ingest (context7 + exa) → risks + unknowns → memory-bank
- `/story` — user story + AC + test checklist → memory-bank  
- `/plan` — sequential plan with explicit file list + test ordering
- `/implement` — tests-first loop; minimal diffs; cite docs used
- `/debug` — repro → isolate → fix; add guard tests
- `/ship` — docs + ADR stub + PR body + small commit
- `/switch` — compact state → Mem0 + memory-bank; clear transient memory
- `/retrospect` — post-run: what worked/failed + follow-ups → Mem0 + backlog

**Memory Helpers**:
- `/decision` — add decision to OpenMemory (Mem0) with tags
- `/caveat` — add caveat/constraint to OpenMemory (Mem0) with tags  
- `/followup` — add follow-up/todo to OpenMemory (Mem0) with tags
- `/mem-search` — query OpenMemory by project/slice/tag
- `/pattern` — save reusable pattern/snippet in Memory-Bank
- `/runbook-update` — append steps/lessons to Memory-Bank runbook
- `/scratch` — jot short-lived notes in server-memory (cleared by /switch)

---

## TDD Loop ("Good" Looks Like)
1. Read **AC** + **Interfaces** (reference `docs/` on-demand)
2. Generate failing tests (unit + schema validation + **RFC-7807** negative paths)
3. **Local checks**:
```bash
python -m pip install -e .[dev]
ruff check .
mypy src  
pytest --cov=src/chatx --cov-fail-under=60
```
4. Minimal code → pass tests → refactor → docs → ADR

---

## Model Selection (Router-aware)
- **Local Gemma via Ollama** — default for routine coding/testing
- **Claude Sonnet** — when local confidence low or slice spans many files
- **Claude Opus** — heavy reasoning (architecture/design tradeoffs)

---

## Definition of Done
✅ Lint, types, tests **green**; coverage **≥ 60%** for changed code  
✅ JSON/HTTP **schemas valid**; errors are **RFC-7807** problem+json  
✅ Behavior documented; ADR stub if design shifted; clear commit message

---

## Memory Automation Rules
**OpenMemory (Mem0)**: Log decisions, caveats, preferences as atomic items with tags: `project`, `slice`, `decision|caveat|followup`  
**Memory-Bank**: Store reusable patterns, runbooks, prompts under `docs/patterns/**` and `docs/runbooks/**`  
**Server-Memory**: Scratch notes for current slice; cleared by `/switch`

**Session lifecycle**:
- **Start**: retrieve "open decisions", "recent caveats", "today's TODO"  
- **End**: append "decisions made", "follow-ups", "snippets added", "risks accepted"

---

## Updating This File  
Keep MCP server entries sync'd with `scripts/setup_mcp_servers.sh`. Add new servers only with explicit approval.
