# Phase 1: generate-tasks recognizes `planning-fix-` input

## Status
completed

## Parent
`./absolutpowers/feature/tasks-debug-handoff.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-debug-handoff/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- `generate-tasks` `## Input` section documents `planning-fix-{slug}.md` as a recognized planning-type input (the 4th variant, mapped onto the existing planning path).
- `generate-tasks` `## Output Convention` confirms `planning-fix-{slug}.md` → `tasks-fix-{slug}.md` via the existing `planning-` → `tasks-` prefix replacement.
- Same wording present in BOTH `claude/skills/generate-tasks/SKILL.md` and `codex/skills/generate-tasks/SKILL.md`.

## Read Scope
- `claude/skills/generate-tasks/SKILL.md` (sections `## Input`, `## Output Convention`)
- `codex/skills/generate-tasks/SKILL.md` (same sections)
- `absolutpowers/feature/planning-debug-handoff.md` (decyzja 2, edge case "generate-tasks nie rozpozna planning-fix-")

## Write Scope
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

## Objective
Teach `generate-tasks` to recognize a `planning-fix-{slug}.md` file (emitted by `debug` for large root-cause fixes) as a planning-type input. No new variant logic — fold it into the existing planning path. Confirm the output name `tasks-fix-{slug}.md` falls out of the current prefix-replacement rule. Apply identically to both trees.

## Tasks

### Task 1: Document `planning-fix-` in the Input section (both trees)
**Status:** completed
**Traces to:** none (no AC section in planning doc)

**Requirements:**
- In `## Input`, under the **Planning doc** entry, add a short note that a `planning-fix-{slug}.md` (root cause + chosen fix, emitted by `debug` for large fixes) is the same planning-type input — read it as Problem (= root cause z dowodem), Wybrane rozwiązanie (= fix), Zakres, optional AC.
- Do NOT introduce a separate 4th input branch with its own parsing — explicitly state it reuses the planning variant.
- Keep wording bilingual-consistent with the surrounding file (English technical prose is fine here).
- Land identical wording in both `claude/` and `codex/` copies.

**Tests:**
- `grep -n "planning-fix-" claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md` returns matches in the Input section of both files.

### Task 2: Confirm output naming in Output Convention (both trees)
**Status:** completed
**Traces to:** none (no AC section in planning doc)

**Requirements:**
- In `## Output Convention`, add one row or note: input `./absolutpowers/feature/planning-fix-{slug}.md` → output `./absolutpowers/feature/tasks-fix-{slug}.md`.
- State that this follows the existing rule ("replace `planning-` prefix with `tasks-`") — no special-casing.
- Land identical wording in both trees.

**Tests:**
- `grep -n "tasks-fix-{slug}" claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md` returns matches in both.

## Phase Verification
Run:
- `grep -n "planning-fix-" claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md`
- `./scripts/diff-skills.sh` — generate-tasks diff shows only expected drift (no behavioral divergence between trees for the new note)

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Both trees carry identical `planning-fix-` wording (only expected drift elsewhere).
- `implementation-context.md` updated with the exact phrasing/anchor used (so Phase 2 can reference it).
- All `## Context Contract -> Provides` items fulfilled.

## Implementation Decisions / Remarks
- Added `planning-fix-{slug}.md` as the 4th input type in `## Input`, directly after the planning doc entry. Described it as a reuse of the planning variant (no separate parsing branch). The description maps Problem/Wybrane rozwiązanie/Zakres/AC to the debug handoff structure.
- Added a `Fix planning doc` row to the `## Output Convention` table showing `planning-fix-{slug}.md` → `tasks-fix-{slug}.md`. Extended the "For planning docs" note below the table to explicitly cover the `planning-fix-` prefix, confirming no special-casing is required.
- Wording is byte-for-byte identical between claude and codex trees (verified with grep). Only expected frontmatter drift (`allowed-tools`, `argument-hint`) separates the two files.
