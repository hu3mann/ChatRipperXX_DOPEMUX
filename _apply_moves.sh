#!/usr/bin/env bash
set -euo pipefail
# Recreate a clean Python project layout from the original "CR-XX" tree without changing file contents.
# Usage: run from the directory that contains the messy CR-XX/ folder. A new folder CR-XX_clean/ will be created.
SRC="CR-XX"
DEST="CR-XX_clean"
if [ ! -d "$SRC" ]; then
  echo "Expected $SRC/ next to this script." >&2
  exit 1
fi
rm -rf "$DEST"
mkdir -p "$DEST"
# Root files
cp -p "$SRC/.aicommitsrc" "$DEST/" 2>/dev/null || true
cp -p "$SRC/mkdocs.yml" "$DEST/" 2>/dev/null || true
cp -p "$SRC/PROJECT_INSTRUCTIONS.md" "$DEST/" 2>/dev/null || true
cp -p "$SRC/mypy.ini" "$DEST/" 2>/dev/null || true
cp -p "$SRC/CONTRIBUTING.md" "$DEST/" 2>/dev/null || true
cp -p "$SRC/.ruff.toml" "$DEST/" 2>/dev/null || true
cp -p "$SRC/.cz.toml" "$DEST/" 2>/dev/null || true
cp -p "$SRC/CLAUDE.md" "$DEST/" 2>/dev/null || true

# Directories
rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/.github/" "$DEST/.github/" 2>/dev/null || true
rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/scripts/" "$DEST/scripts/" 2>/dev/null || true
rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/docs/" "$DEST/docs/" 2>/dev/null || true

# Bring stray markdowns to docs/
shopt -s nullglob
for md in "$SRC"/*.md; do
  base="$(basename "$md")"
  case "$base" in
    CONTRIBUTING.md|CLAUDE.md|PROJECT_INSTRUCTIONS.md) ;;
    *) mkdir -p "$DEST/docs"; cp -p "$md" "$DEST/docs/$base" ;;
  esac
done
shopt -u nullglob

# CR-XactXtract subtree
if [ -d "$SRC/CR-XactXtract" ]; then
  rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/CR-XactXtract/config/" "$DEST/config/" 2>/dev/null || true
  rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/CR-XactXtract/SCHEMAS/" "$DEST/schemas/" 2>/dev/null || true
  rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/CR-XactXtract/PROJECT_DESIGN_FILES/" "$DEST/docs/PROJECT_DESIGN_FILES/" 2>/dev/null || true
  rsync -a --exclude '__MACOSX' --exclude '._*' --exclude '.DS_Store' "$SRC/CR-XactXtract/EXTRACTORS/" "$DEST/src/chatx/extractors/" 2>/dev/null || true
  if [ -d "$SRC/CR-XactXtract/.git" ]; then
    rsync -a "$SRC/CR-XactXtract/.git/" "$DEST/archive/CR-XactXtract_git/" 2>/dev/null || true
  fi
fi

# Remove macOS metadata
find "$DEST" -name '__MACOSX' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$DEST" -name '.DS_Store' -type f -delete 2>/dev/null || true
find "$DEST" -name '._*' -type f -delete 2>/dev/null || true

echo "Cleaned layout written to $DEST/"
