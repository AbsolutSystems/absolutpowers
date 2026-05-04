#!/bin/bash
# Compare Claude and Codex SKILL.md files to detect drift.
# Expected drift: Claude-specific frontmatter (allowed-tools, argument-hint)
# and agent-loop sections added to Claude skills over time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$REPO_ROOT/claude/skills"
CODEX_DIR="$REPO_ROOT/codex/skills"

identical=0
different=0
missing_codex=0
missing_claude=0

for skill in "$CLAUDE_DIR"/*/SKILL.md; do
  name=$(basename "$(dirname "$skill")")
  codex="$CODEX_DIR/$name/SKILL.md"
  if [ -f "$codex" ]; then
    if diff -q "$skill" "$codex" > /dev/null 2>&1; then
      echo "  = $name"
      identical=$((identical + 1))
    else
      echo "  ~ $name (differs)"
      if [ "${1:-}" = "--diff" ]; then
        diff -u "$skill" "$codex" || true
        echo ""
      fi
      different=$((different + 1))
    fi
  else
    echo "  ! $name (missing in codex)"
    missing_codex=$((missing_codex + 1))
  fi
done

for skill in "$CODEX_DIR"/*/SKILL.md; do
  name=$(basename "$(dirname "$skill")")
  claude="$CLAUDE_DIR/$name/SKILL.md"
  if [ ! -f "$claude" ]; then
    echo "  ! $name (missing in claude)"
    missing_claude=$((missing_claude + 1))
  fi
done

echo ""
echo "Summary: $identical identical, $different differ, $missing_codex claude-only, $missing_claude codex-only"
