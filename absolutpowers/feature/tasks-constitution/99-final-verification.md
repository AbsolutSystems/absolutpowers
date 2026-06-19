# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Description
Run the project's verification commands against the fully integrated change. This is a markdown prompt-engineering plugin — there is no build/test/typecheck. The canonical gate is cross-tree drift detection plus manifest version match. Completed by the implement orchestrator after all implementation phases pass.

## Requirements
- Run drift check: `./scripts/diff-skills.sh` — every modified skill (`constitution`, `generate-tasks`, `implement`, `review`, `update-ai-context`, `feature-discuss`) shows ONLY expected Claude-only drift (`allowed-tools`, `argument-hint`, agent/gate sections). No unexpected procedural divergence.
- Confirm new skill present in both trees: `ls claude/skills/constitution/SKILL.md codex/skills/constitution/SKILL.md`.
- Confirm wiring landed everywhere: `grep -rln "constitution.md" claude/skills/ codex/skills/` lists generate-tasks, implement, review, feature-discuss in both trees (update-ai-context references constitution by name, not necessarily `.md`).
- Confirm manifest versions match and are `3.9.0`: `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json`.
- Confirm docs updated: `grep -n constitution README.md CLAUDE.md`.
- Record any command intentionally skipped as `not applicable` with a short reason (no backend/frontend build exists here).
- Do not mark this task completed if any required verification command fails or `diff-skills.sh` reports unexpected drift.

## Tests
- `./scripts/diff-skills.sh` exits 0 with only expected drift.
- Both constitution SKILL.md files exist.
- Both manifests report `3.9.0`.
- README.md + CLAUDE.md mention constitution.

## Implementation Decisions / Remarks
- Commands executed: `./scripts/diff-skills.sh`; `ls` both constitution files; `grep -rln constitution.md` both trees; `grep '"version"'` both manifests; `grep -c constitution README.md CLAUDE.md`.
- Results: PASS. `constitution` present both trees, reports `~ differs` (only allowed frontmatter drift). Wiring landed in generate-tasks/implement/review/feature-discuss/update-ai-context (both trees) + constitution itself = 12 files. Both manifests `3.9.0`. Docs: README 17 hits, CLAUDE.md 9 hits.
- Skipped checks: backend/frontend build, typecheck, lint — `not applicable` (markdown prompt-engineering plugin, no build system).
- Note: `! tech-lead-advisor (missing in claude)` in diff-skills is pre-existing codex-only drift (tech-lead is a claude *agent*, not a skill) — not introduced by this feature.

## Example
```bash
./scripts/diff-skills.sh
ls claude/skills/constitution/SKILL.md codex/skills/constitution/SKILL.md
grep -rln "constitution.md" claude/skills/ codex/skills/
grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json
grep -n constitution README.md CLAUDE.md
```
