# Implementation Context: debug-handoff

## Purpose
Short handoff for phase workers. Keep concise. Add only facts future phases need.

## Completed Phases
- Phase 1: generate-tasks recognizes `planning-fix-` input — DONE.
- Phase 2: debug emits/consumes handoff artefacts — DONE.
- Phase 3: problem-discuss Faza 5 bug-route nudge updated to file-reference form — DONE.
- Phase 4: docs + version consistency — DONE.

## Phase 2 API / Anchors

- `debug` `## Handoff Input` section: anchor is `## Handoff Input`, placed after the `vs problem-discuss` blockquote, before `## Context Files`. Present in both trees.
- Phase 4 "Step 0" size classification: inserted at the top of `### Phase 4: Implementation`, before step 1 "Create Failing Test Case". Small = inline (1 file/layer, no migration/API/security/shared-core). Large = write `absolutpowers/feature/planning-fix-{slug}.md` + nudge to generate-tasks.
- `planning-fix-{slug}.md` template: defined inline in Phase 4 Step 0. Sections: Problem (root cause + file:line), Wybrane rozwiązanie, Zakres, optional AC. File path: `absolutpowers/feature/planning-fix-{slug}.md`.
- Phase 4.5 (`If 3+ Fixes Failed: Question Architecture`): now routes to `planning-fix-{slug}.md` + generate-tasks nudge after the user discussion. No longer dead-ends at conversation only.
- Iron Law text: unchanged.

## Created / Changed API
- `generate-tasks` `## Input`: `planning-fix-{slug}.md` documented as 4th input type, reusing planning variant. Exact anchor: `**Fix planning doc** (large root-cause fix, emitted by \`debug\` for changes that exceed inline scope):`.
- `generate-tasks` `## Output Convention` table: row `Fix planning doc | ./absolutpowers/feature/planning-fix-{slug}.md | ./absolutpowers/feature/tasks-fix-{slug}.md` added. "For planning docs" note confirms prefix replacement covers `planning-fix-` with no special-casing.
- Identical wording in both `claude/skills/generate-tasks/SKILL.md` and `codex/skills/generate-tasks/SKILL.md`.

## Decisions Made
- Input handoff: NO new file. `debug` reads existing `absolutpowers/problem/problem-{slug}.md` (reuse).
- Output handoff: `debug` emits `absolutpowers/feature/planning-fix-{slug}.md` for large fixes — a planning-variant input to `generate-tasks`.
- Output naming: `generate-tasks` already replaces `planning-` → `tasks-`, so `planning-fix-{slug}.md` → `tasks-fix-{slug}.md` falls out of the existing rule. No new output-naming logic needed.
- Size threshold for inline-vs-handoff = same heuristic as single-file vs orchestrated in `generate-tasks`.
- Versions already at 3.9.0 in both manifests — Phase 4 verifies match, does not bump.

## Test Utilities / Fixtures
- None (markdown-only repo). Verification = `./scripts/diff-skills.sh` + version grep.

## Constraints For Next Phases
- Every behavioral change must land in BOTH `claude/` and `codex/` skill copies (only expected drift differs).
- Do NOT change debug's Iron Law or the 4-phase core — handoff is input/output only.

## Phase 3 API / Anchors

- `problem-discuss` Faza 5 bug bullet (both trees): `/absolutpowers:debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"` (debug wczyta raport i skupi się na nazwanej sprawie).
- Old forms removed: Claude had `debug "{opis sprawy + dowód file:line}"`, Codex had `debug` ze sprawą + dowodem.
- Nudge shape matches `debug` `## Handoff Input` exactly: path arg + optional case-number string.

## Phase 4 Docs / Version

- Versions: both `claude/.claude-plugin/plugin.json` and `codex/.codex-plugin/plugin.json` confirmed at `"version": "3.9.0"` — no edit made.
- CLAUDE.md: `problem-discuss` diagram now shows `debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"` for the bug route. Added paragraph after the existing block describing both handoffs (input: reads `problem-{slug}.md`; output: large fix → `planning-fix-{slug}.md` → generate-tasks nudge).
- README.md: `/absolutpowers:debug` section updated (What it does / Input / Output). Project structure tree gained `planning-fix-{slug}.md` row. "Quick bug fix" workflow shows both paths.
- All artefact names/paths match skill files from Phases 1–3.

## Verification History
- Phase 1: `grep -Fn "planning-fix-"` returned 3 matches in each tree file (Input + table row + note). `grep -Fn "tasks-fix-{slug}"` returned 2 matches in each file (table row + note). `./scripts/diff-skills.sh` generate-tasks diff shows only pre-existing expected drift.
- Phase 2: `grep -n "Handoff Input\|planning-fix-"` returned 8 matches in each tree file (symmetric). `diff` after stripping frontmatter confirmed body is identical. Only drift = `allowed-tools` + `argument-hint` in Claude frontmatter (expected).
- Phase 3: `grep -n "debug @absolutpowers/problem/problem-"` returned 1 match in each file (lines 163 and 161). `./scripts/diff-skills.sh --diff` shows problem-discuss diff has only pre-existing expected drift (frontmatter, CLAUDE.md/AGENTS.md, minor Faza 1/2 wording). Behavioral bug bullet is identical in both trees.
