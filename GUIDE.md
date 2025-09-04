
# MCP + Claude Code Playbook (Guide)

This pack gives you:
- A project-level **CLAUDE.md** that defines flows, rules, and tools.
- A set of **slash commands** under `.claude/commands/` to keep runs fast and consistent.
- Empty folders under `docs/` for patterns/runbooks/stories/plans/research`.

## Quick Start

1) Ensure your MCP servers are added (Mem0 hosted, context7, claude-context, exa, etc.).  
2) Open your project terminal and run:
   ```bash
   claude
   ```
3) Start with:
   ```
   /bootstrap
   ```
   Approve the tiny test-first plan or adjust it.

## Core Flow

**research → story → plan → implement → debug → ship → retrospect → switch**

- **/research**: Pulls authoritative docs (context7), optional web sources (exa), writes `docs/research/<topic>.md`.
- **/story**: Converts research into a user story + AC; writes `docs/stories/<id>.md`.
- **/plan**: Uses sequential_thinking to make ≤5 executable steps; writes `docs/plans/<id>.md`.
- **/implement**: Test-first loop, minimal diffs, cite docs.
- **/debug**: Repro, isolate, smallest fix, guard tests; postmortem note.
- **/ship**: Docs + ADR stub + PR body + small commit; logs Mem0 decisions.
- **/retrospect**: 3 bullets on what worked/failed + improvements.
- **/switch**: Compact state, push decisions (Mem0) and patterns (Memory-Bank), clear scratch.

## Memory Automation

- **Mem0 (OpenMemory, hosted):** add decisions/caveats/follow-ups with tags:
  - `project:<name>`, `slice:<name>`, `decision|caveat|followup`.
  - Use `/decision`, `/caveat`, `/followup`, `/mem-search` commands as shortcuts.
- **Memory-Bank:** reusable patterns and runbooks:
  - `/pattern` to add a pattern (e.g., edge streaming).
  - `/runbook-update` to append lessons to a runbook.
- **Server-Memory:** short-lived notes (`/scratch`), cleared by `/switch`.

**Start of session**
- Run `/bootstrap`; it fetches hot files, API docs, and open decisions.

**End of session**
- Run `/ship` then `/retrospect`. If changing tasks, run `/switch` to compress context and store it.

## Conventions

- Keep patches small (≤200 lines).  
- Always cite doc sections (from context7) you relied on.  
- Never store secrets in Mem0/Memory-Bank.  
- Prefer Exa for technical sources; use DuckDuckGo when you need broader recall.

## Troubleshooting

- If a command can't access a tool, run `claude mcp list` and re-add as needed.
- If Mem0 search is noisy, add more specific tags: `project:chatx`, `slice:auth`, `decision`.
- If context feels stale, re-run `/bootstrap` to refresh hot files + docs.

---

Happy shipping. Keep it tiny, tested, and traceable.


## Namespace defaults & PR helpers
- Source `scripts/ns_defaults.zsh` after installing aliases to auto-tag Mem0 items with `project:` and `slice:`.
- Use `cc-dec+`, `cc-cav+`, `cc-fu+` to log with defaults; `cc-mem+` searches with defaults.
- `cc-compact` runs the `/switch` flow.
- `cc-pr` writes a PR body to `docs/pr/<branch>.md` using `git_local`, `openmemory`, and `memory_bank`.
- `cc-commit` drafts a conventional commit using `git_local` and asks for confirmation before committing.
