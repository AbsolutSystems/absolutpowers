# Phase 4: Wire lightweight context into feature-discuss (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-constitution/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `claude/skills/constitution/SKILL.md` exists (Phase 1) — defines `absolutpowers/constitution.md`.

### Provides (for later phases)
- `feature-discuss` (both trees) reads `absolutpowers/constitution.md` as lightweight context so proposed solutions respect ratified pryncypia from the start.

## Read Scope
- `claude/skills/feature-discuss/SKILL.md` (insertion point: context-loading step ~L48, where parent/ADR context is read)
- `codex/skills/feature-discuss/SKILL.md`

## Write Scope
- `claude/skills/feature-discuss/SKILL.md`
- `codex/skills/feature-discuss/SKILL.md`

## Objective
Add `absolutpowers/constitution.md` as **lightweight** (not binding) context in feature-discuss so the solution design honours pryncypia early. This is the open-question scope addition (confirmed yes). Single additive edit per tree — do not turn it into a hard gate.

## Tasks

### Task 1: Add constitution as lightweight context in feature-discuss (both trees)
**Status:** completed

**Modify:**
- `claude/skills/feature-discuss/SKILL.md`
- `codex/skills/feature-discuss/SKILL.md`

**Requirements:**
- In the context-loading step (near where ADR / parent main-doc context is read), add: read `./absolutpowers/constitution.md` if it exists; use ratified pryncypia as a soft guide for the proposed solution and flag any proposal that would conflict with an Artykuł.
- Explicitly mark it **lightweight** context, not a binding gate (distinct from generate-tasks/implement which treat it as binding).
- If the file does not exist, skip silently (no error).
- Mirror identically in both trees.

**Tests:**
- Manual: `grep -n "constitution.md" claude/skills/feature-discuss/SKILL.md codex/skills/feature-discuss/SKILL.md` — present in both.
- Manual: wording says lightweight/soft, not a gate; absent-file path is graceful.

## Phase Verification
Run:
- `grep -rn "constitution.md" claude/skills/feature-discuss/ codex/skills/feature-discuss/` — present in both.
- `./scripts/diff-skills.sh` — only pre-existing expected drift for `feature-discuss`.

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Phase verification commands pass.
- `implementation-context.md` updated (feature-discuss now reads constitution as lightweight context).
- All items in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Inserted a new "Wstępne wczytanie kontekstu projektu" sub-section directly before "Faza 0" in `## Proces rozmowy` in both trees. This positions the constitution read-step as a session preamble that runs for every invocation (Tryb A and Tryb B alike).
- Single sentence covers all three requirements: "lekki kontekst" (lightweight), "nie bramka" (not a gate, distinct from generate-tasks/implement binding treatment), "Brak pliku → pomiń cicho" (graceful absent-file skip).
- Bodies are identical between claude/ and codex/ trees. The `~` marker in diff-skills.sh for feature-discuss is pre-existing expected drift (allowed-tools + argument-hint frontmatter in Claude only).
