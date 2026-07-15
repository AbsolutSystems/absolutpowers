# Phase 3: problem-discuss Faza 5 nudge points to file

## Status
completed

## Parent
`./absolutpowers/feature/tasks-debug-handoff.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-debug-handoff/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 2: `debug` has a `## Handoff Input` section that accepts a path to `problem-{slug}.md` (+ optional case number). The nudge written here must match that exact invocation shape. Confirm via `grep "Handoff Input" claude/skills/debug/SKILL.md`.

### Provides (for later phases)
- `problem-discuss` Faza 5 (both trees): the "potwierdzony bug → debug" nudge points to the FILE plus case number, not just a description string:
  `/absolutpowers:debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"`.
- Same wording in both `claude/skills/problem-discuss/SKILL.md` and `codex/skills/problem-discuss/SKILL.md`.

## Read Scope
- `claude/skills/problem-discuss/SKILL.md` (Faza 5: Routing / handoff — line ~158-169)
- `codex/skills/problem-discuss/SKILL.md` (same section)
- `absolutpowers/feature/planning-debug-handoff.md` ("Handoff wejściowy")

## Write Scope
- `claude/skills/problem-discuss/SKILL.md`
- `codex/skills/problem-discuss/SKILL.md`

## Objective
Make problem-discuss's bug-route nudge carry the evidence file instead of dropping it into a free-text string, so debug's new Handoff Input can pick it up. Single-line change to one bullet in Faza 5, mirrored in both trees.

## Tasks

### Task 1: Update Faza 5 bug-route nudge to reference the report file (both trees)
**Status:** completed
**Traces to:** none (no AC section in planning doc)

**Requirements:**
- In `## Faza 5: Routing / handoff (fan-out)`, change the bug bullet from:
  `potwierdzony bug → /absolutpowers:debug "{opis sprawy + dowód file:line}"`
  to:
  `potwierdzony bug → /absolutpowers:debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"`
- Add a half-line note that debug reads the report and focuses on the named case (matches debug `## Handoff Input`). Keep other route bullets (gap/config/dane/nieporozumienie/brak danych) unchanged.
- Keep the surrounding "best-effort nudge, NIE wykonuj" / "wybór należy do użytkownika" framing intact.
- Identical wording in both trees.

**Tests:**
- `grep -n "problem-{slug}.md" claude/skills/problem-discuss/SKILL.md codex/skills/problem-discuss/SKILL.md` matches in the Faza 5 nudge of both files.
- The old string-only `debug "{opis...}"` form is gone from the bug bullet.

## Phase Verification
Run:
- `grep -n "debug @absolutpowers/problem/problem-" claude/skills/problem-discuss/SKILL.md codex/skills/problem-discuss/SKILL.md`
- `./scripts/diff-skills.sh` — problem-discuss diff shows only expected drift

## Completion Criteria
- Task completed; change within Write Scope.
- Nudge shape matches debug Handoff Input invocation exactly.
- Both trees identical (modulo expected frontmatter drift).
- `implementation-context.md` updated if the chosen invocation shape differs from the contract above.
- `## Context Contract -> Provides` fulfilled.

## Implementation Decisions / Remarks
- Claude tree Faza 5 changed from: `potwierdzony bug → /absolutpowers:debug "{opis sprawy + dowód file:line}"` to the file-reference form.
- Codex tree Faza 5 changed from: `potwierdzony bug → \`debug\` ze sprawą + dowodem \`file:line\`` to the same file-reference form.
- Both trees now read: `potwierdzony bug → /absolutpowers:debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"` (debug wczyta raport i skupi się na nazwanej sprawie).
- Invocation shape matches debug `## Handoff Input` exactly (path + optional case number string).
- Remaining diffs in diff-skills.sh for problem-discuss are all pre-existing expected drift (frontmatter, CLAUDE.md vs AGENTS.md reference, minor Faza 1/2 wording). No new unexpected drift introduced.
