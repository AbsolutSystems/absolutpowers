# Phase 4: Add AC Coverage to Review-Tasks

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 3 completed: `**Traces to:** AC-N` field exists in generate-tasks task templates (both Claude and Codex)
- Phase 1 completed: AC format defined (`AC-N:` numbering)

### Provides (for later phases)
- Updated `claude/agents/review-tasks.md` with AC Coverage check in Traceability section and `AC_COVERAGE` category

## Read Scope
- `claude/agents/review-tasks.md` — current file to modify
- `claude/skills/generate-tasks/SKILL.md` — to understand `Traces to:` field format
- `./absolutpowers/feature/planning-qa-enrichment.md` — AC format reference

## Write Scope
- `claude/agents/review-tasks.md`

## Objective
Extend review-tasks agent to verify that every AC from the planning doc is covered by at least one task in the tasks document. Add graceful handling for planning docs without AC.

## Tasks

### Task 1: Add AC Coverage Check to Review-Tasks
**Status:** completed

**Modify:**
- `claude/agents/review-tasks.md`

**Requirements:**
- Extend existing section `### 1. Traceability` (line 38) with AC-specific checks:
  - If the source planning doc contains `## Acceptance Criteria`, extract all `AC-N:` items
  - Verify every `AC-N` is referenced by at least one task's `**Traces to:**` field
  - Flag tasks with `**Traces to:** none` that appear to cover an AC but don't reference it
  - If the source planning doc has no `## Acceptance Criteria` section, skip AC coverage check silently
- Add `AC_COVERAGE` to the Categories line in Response Format section (currently line 97: `Categories: TRACEABILITY, GRANULARITY, ORDERING, SPECIFICITY, VERIFICATION, CODE_REFERENCE`)
- AC_COVERAGE issues should be formatted as: `[AC_COVERAGE] General — AC-3 ("description...") not covered by any task`
- For orchestrated tasks: check traceability across all phase files, not just the main index

**Example addition to Traceability section:**
```markdown
- If the source planning doc contains `## Acceptance Criteria`:
  - Every `AC-N` item is referenced by at least one task's `**Traces to:**` field
  - No orphan AC (defined in plan but never traced by any task)
  - If planning doc has no AC section, skip this check
```

## Phase Verification
Run:
- Verify `claude/agents/review-tasks.md` contains "AC-N" and "Traces to" references in Traceability section
- Verify `claude/agents/review-tasks.md` contains "AC_COVERAGE" in Categories line
- Verify the agent file still has valid frontmatter and all 6 criteria sections

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Added AC coverage checks to `### 1. Traceability` section: extract `AC-N` items from planning doc if `## Acceptance Criteria` present, verify every AC-N is referenced by at least one task's `**Traces to:**` field, flag `**Traces to:** none` tasks that cover an AC, skip silently when no AC section.
- Added `AC_COVERAGE` to Categories line (now: `TRACEABILITY, GRANULARITY, ORDERING, SPECIFICITY, VERIFICATION, CODE_REFERENCE, AC_COVERAGE`).
- Added AC_COVERAGE issue format example directly after the Categories line: `[AC_COVERAGE] General — AC-3 ("description...") not covered by any task`.
- Added explicit note for orchestrated tasks: check AC traceability across all phase files, not just the main index.
- Graceful fallback is in the traceability bullet itself: "If planning doc has no `## Acceptance Criteria` section, skip this check" — no separate section needed.
