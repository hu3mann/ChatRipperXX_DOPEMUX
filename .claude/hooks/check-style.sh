#!/usr/bin/env bash
set -euo pipefail
echo "[hooks] Running style & test checks..."
ruff check .
mypy src
pytest --cov=src --cov-fail-under=90 -q || { echo "Tests/coverage failed; blocking further edits." >&2; exit 2; }
echo "[hooks] All checks passed."
