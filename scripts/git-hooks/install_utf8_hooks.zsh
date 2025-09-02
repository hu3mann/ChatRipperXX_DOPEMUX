#!/usr/bin/env zsh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" ]]; then
  print -u2 "Error: run inside a Git repository."
  exit 1
fi

mkdir -p "$ROOT/.git/hooks"

timestamp() { date +"%Y%m%d-%H%M%S"; }

install_hook() {
  local src_rel="$1"     # e.g., hooks/pre-commit
  local name="$2"        # e.g., pre-commit

  local src_abs="$ROOT/$src_rel"
  local dst="$ROOT/.git/hooks/$name"

  if [[ ! -f "$src_abs" ]]; then
    print -u2 "Error: missing source $src_abs"
    exit 1
  fi

  # Backup existing non-symlink hooks
  if [[ -e "$dst" && ! -L "$dst" ]]; then
    mv "$dst" "$dst.backup-$(timestamp)"
  fi

  # Create absolute symlink (portable on macOS). If that fails, copy.
  if ln -sfn "$src_abs" "$dst" 2>/dev/null; then
    :
  else
    cp "$src_abs" "$dst"
  fi

  chmod +x "$src_abs" "$dst" 2>/dev/null || true
  echo "Installed $name -> $src_rel"
}

install_hook "hooks/pre-commit" "pre-commit"
install_hook "hooks/pre-applypatch" "pre-applypatch"

echo "Done. Hooks installed."
