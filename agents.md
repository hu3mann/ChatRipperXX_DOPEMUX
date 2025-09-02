# Repository Guidelines

This guide helps contributors work effectively in this repository. It summarizes structure, tooling, and expectations for code, tests, and reviews.

## Project Structure & Module Organization
- `src/chatx/`: Python package (Python 3.11+).
  - `cli/` (Typer CLI), `extractors/`, `schemas/` (Pydantic), `transformers/`, `redaction/`, `enrichment/`, `utils/`.
- `tests/`: Pytest suite (`unit/`, `integration/`, `fixtures/`).
- `schemas/`: JSON Schemas; `docs/`: MkDocs site; `scripts/`: helper and git hook scripts.

## Build, Test, and Development Commands
- Setup: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
- Run CLI: `chatx --help`
  - Examples: `chatx extract ~/Library/Messages/chat.db -p imessage -o ./output`
              `chatx pipeline <source> ./output --provider local`
- Tests: `pytest` (coverage HTML in `htmlcov/`).
- Lint: `ruff check` (auto-fix: `ruff check --fix`).
- Types: `mypy src tests`.
- Docs: `mkdocs serve` (dev) | `mkdocs build` (static site).

## Coding Style & Naming Conventions
- Language: Python ≥ 3.11, 4‑space indent, max line length 100.
- Linting: Ruff with pycodestyle/pyflakes/isort/bugbear/pyupgrade rules; pydocstyle (Google style).
- Types: Prefer full typing; repository enforces strict mypy settings.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_CASE`.

## Testing Guidelines
- Framework: Pytest with coverage (threshold 60% via config).
- Naming: files `test_*.py` or `*_test.py`; classes `Test*`; functions `test_*`.
- Structure: unit tests in `tests/unit/`, integration in `tests/integration/`; reuse data in `tests/fixtures/`.
- Run locally before opening a PR: `pytest -q` then `pytest --cov=src/chatx`.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (Commitizen configured).
  - Example: `feat(extractors): add iMessage timestamp converter`
  - Subject ≤ 72 chars; keep focused; include rationale in body when useful.
- PRs: clear description, linked issues (e.g., `Closes #123`), test updates, and docs where applicable. Include example CLI command/output when relevant.
- Pre‑submit: run `ruff check --fix && mypy src tests && pytest`.
- Optional: install AI commit hook `bash scripts/install-git-hooks.sh`.

## Security & Configuration Tips
- Do not commit real datasets or secrets. Use `.env` (ignored) and sanitize samples.
- Review `SECURITY.md` and threat model docs under `docs/` for guidance.

## Agent‑Specific Instructions (if using AI agents)
- Read `CLAUDE.md` and `repo_prompt.md` at session start.
- Operate within role scope; request human confirmation before destructive actions.
