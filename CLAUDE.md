# CLAUDE.md — Guardrails & Prompts for Agent Work

See `docs/index.md` for the process overview. This file captures LLM rules for day-to-day development.

---

## Chat & IDE/CLI Operating Rules

### When in a ChatGPT-style chat
1. **Request the project ZIP first.**
2. After analysis, **return a single unified `diff`** in a fenced diff block, plus a **one-liner** for local apply, e.g.:
   ```bash
   git apply -p0 <<'PATCH'
   *** your unified diff here ***
   PATCH
   ```
3. The diff must be minimal, self-contained, and pass CI locally (`pytest`, `ruff`, `mypy`).

### When in CLI or VS Code
- Write/update **docs as you plan or code** (no PR without docs).
- **Open a GitHub Issue** for each user story using the templates; link the PR.
- Use **aicommits** to generate **Conventional Commits** automatically.

### Always use the latest upstream docs
Before proposing code that uses a framework or library, **read the most recent official docs** and adapt examples accordingly. Prefer vendor docs and changelogs over stale blog posts.

### Code quality guarantees
- Code must compile, run, and **tests must pass on first try**.
- Use descriptive names; write docstrings (Google style); keep diffs small.
