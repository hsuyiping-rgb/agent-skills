#!/usr/bin/env bash
# Install agent-workflow-kit skills into Claude Code, Codex and Antigravity (macOS / Linux).
# Usage: bash install.sh [--dry-run] [--force] [claude] [codex] [antigravity]
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)/skills"
SKILLS=(agent-kit project-init startup shutdown office-docs grilling)
DRY=0; FORCE=0; TARGETS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --force) FORCE=1 ;;
    claude|codex|antigravity) TARGETS+=("$a") ;;
    *) echo "unknown option: $a" >&2; exit 1 ;;
  esac
done

probe() { case "$1" in claude) echo "$HOME/.claude";; codex) echo "$HOME/.codex";; antigravity) echo "$HOME/.gemini/antigravity";; esac; }
if [ ${#TARGETS[@]} -eq 0 ]; then
  for t in claude codex antigravity; do [ -d "$(probe $t)" ] && TARGETS+=("$t"); done
fi
[ ${#TARGETS[@]} -gt 0 ] || { echo "No Claude Code / Codex / Antigravity config folder found." >&2; exit 1; }

BACKUP="$HOME/.agent-kit-backup/$(date +%Y%m%d-%H%M%S)"
for t in "${TARGETS[@]}"; do
  dest="$(probe "$t")/skills"
  echo "== $t -> $dest"
  [ $DRY -eq 1 ] || mkdir -p "$dest"
  for s in "${SKILLS[@]}"; do
    src="$KIT/$s"; target="$dest/$s"
    if [ -d "$target" ]; then
      if diff -rq "$src" "$target" >/dev/null 2>&1; then echo "   = $s (already identical)"; continue; fi
      if [ $FORCE -eq 0 ]; then echo "   ! $s exists and differs - skipped (use --force)"; continue; fi
      if [ $DRY -eq 1 ]; then echo "   ~ $s would replace"; continue; fi
      mkdir -p "$BACKUP/$t"; mv "$target" "$BACKUP/$t/$s"; echo "   backup: $BACKUP/$t/$s"
    elif [ $DRY -eq 1 ]; then echo "   ~ $s would install"; continue; fi
    cp -R "$src" "$target"; echo "   + $s"
  done
done
[ $DRY -eq 1 ] && echo "Dry run only - nothing was changed." || echo "Done. Restart each Agent so the new skills are loaded."
