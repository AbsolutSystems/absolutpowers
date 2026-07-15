# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/tasks-debug-handoff.md`

## Objective
Confirm the integrated debug-handoff change is consistent across both plugin trees, both ends of the debug tree are wired, docs reflect it, and versions match. Run by the implement orchestrator after Phases 1–4 pass.

## Requirements
- Run drift check: `./scripts/diff-skills.sh` — only EXPECTED drift may appear (`allowed-tools`, `argument-hint`, `Agent` in allowed-tools, Claude-only agent gate sections). No behavioral divergence between trees for debug / problem-discuss / generate-tasks.
- Confirm input handoff wiring across trees:
  - `grep -rn "Handoff Input" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md`
  - `grep -rn "debug @absolutpowers/problem/problem-" claude/skills/problem-discuss/SKILL.md codex/skills/problem-discuss/SKILL.md`
- Confirm output handoff wiring across trees:
  - `grep -rn "planning-fix-" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md`
- Confirm docs: `grep -rn "planning-fix-" README.md CLAUDE.md`
- Confirm version match: `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json` → both `3.9.0`.
- Record any check intentionally skipped as `not applicable` with a reason.
- Do not mark completed if any check fails (other than expected drift).

## Tests
- `./scripts/diff-skills.sh` exits cleanly with only expected drift.
- All `grep` wiring checks above return matches in BOTH trees.
- Version grep shows identical 3.9.0 in both manifests.

## Implementation Decisions / Remarks
- Commands executed: `diff-skills.sh`; grep for `Handoff Input`, `debug @absolutpowers/problem/problem-`, `planning-fix-`; version grep.
- Results: PASS. `Handoff Input` in both debug trees. problem-discuss nudge identical in both trees. `planning-fix-` symmetric: debug 7/7, generate-tasks 3/3. Docs: CLAUDE.md 1, README.md 5. Versions both 3.9.0.
- Skipped checks: none. Note: `diff-skills.sh` reports per-skill "differs" at summary level (frontmatter drift, expected) and `tech-lead-advisor missing in claude` — pre-existing/unrelated to this change.

## Example
```bash
./scripts/diff-skills.sh
grep -rn "Handoff Input\|planning-fix-" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md
grep -rn "planning-fix-" claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md README.md CLAUDE.md
grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json
```
