# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/tasks-cross-artifact-analyze.md`

## Shared Context
- `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`

## Objective
Run the project's verification commands against the fully integrated change. This repo has no compiled code or test suite — verification = cross-tree drift check, JSON manifest validity, version parity, and targeted presence greps. Completed by the implement orchestrator after all implementation phases pass.

## Tasks

### Task 1: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- None

**Description:**
Confirm both plugin trees are consistent, manifests are valid and version-matched, and every required edit landed.

**Requirements:**
- Run drift detection: `./scripts/diff-skills.sh` — `analyze`, `feature-discuss`, `review`, `generate-tasks` show ONLY expected drift (Claude-only `allowed-tools`/`argument-hint` + the Claude-only delegation paragraph in `analyze`). No unexpected logic divergence; no `! analyze (missing ...)`.
- Validate manifests: `python3 -m json.tool claude/.claude-plugin/plugin.json > /dev/null && python3 -m json.tool codex/.codex-plugin/plugin.json > /dev/null`.
- Confirm version parity: both manifests `"version": "3.9.0"`.
- Presence greps (all must hit):
  - `grep -q "### 7. Intent Fidelity" claude/agents/review-tasks.md`
  - `grep -q "INTENT" claude/agents/review-tasks.md`
  - `test -f claude/skills/analyze/SKILL.md && test -f codex/skills/analyze/SKILL.md`
  - `grep -qi "analyze" claude/skills/review/SKILL.md && grep -qi "analyze" codex/skills/review/SKILL.md`
  - `grep -qi "analyze" claude/skills/generate-tasks/SKILL.md && grep -qi "analyze" codex/skills/generate-tasks/SKILL.md`
  - `grep -qi "analyze" README.md && grep -qi "analyze" CLAUDE.md`
  - `grep -qi "review-tasks\|intent" claude/skills/feature-discuss/SKILL.md && grep -qi "review-tasks\|intent" codex/skills/feature-discuss/SKILL.md`
- Record any command intentionally skipped as `not applicable` with a short reason.
- Do not mark this task completed if any required verification command fails.

**Tests:**
- `./scripts/diff-skills.sh` exits 0 and shows only expected drift.
- Both `python3 -m json.tool` invocations exit 0.
- All presence greps exit 0.

**Implementation decisions / remarks:**
- Commands executed: `./scripts/diff-skills.sh`; `python3 -m json.tool` on both manifests; version-parity python check; 7 presence greps (crit7, INTENT, analyze both trees, review notes, generate-tasks, README+CLAUDE docs, feature-discuss nudge).
- Results: ALL PASS. diff-skills → analyze/feature-discuss/review/generate-tasks show only expected drift; JSON OK; versions OK 3.9.0; all 7 greps ok.
- Skipped checks: none. (No build/test suite — this is a Markdown plugin repo.)
- Note: diff-skills summary "1 codex-only" = pre-existing `tech-lead-advisor` (Codex skill mirrored as a Claude agent), unrelated to this feature.

## Phase Verification
Run all commands listed in Task 1 Requirements.

## Completion Criteria
- All verification commands pass (or are justified as not applicable).
- Both plugin trees consistent; manifests valid and at matching 3.9.0.

## Implementation Decisions / Remarks
- Run by the orchestrator after all four phases passed phase-review. All verification commands pass; both plugin trees consistent, manifests valid and at matching 3.9.0.
