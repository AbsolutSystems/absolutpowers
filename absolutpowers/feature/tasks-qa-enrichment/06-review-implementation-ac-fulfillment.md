# Phase 6: Add AC Fulfillment to Review-Implementation

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 5 completed: implement skills report AC Fulfillment status (FULFILLED / NOT VERIFIED / PARTIAL)
- Phase 3 completed: tasks have `**Traces to:** AC-N` fields
- Phase 1 completed: AC format defined

### Provides (for later phases)
- Updated `claude/agents/review-implementation.md` with "7. AC Fulfillment" criterion and `AC_FULFILLMENT` category

## Read Scope
- `claude/agents/review-implementation.md` — current file to modify
- `claude/skills/implement/SKILL.md` — to understand AC fulfillment report format
- `./absolutpowers/feature/planning-qa-enrichment.md` — AC format reference

## Write Scope
- `claude/agents/review-implementation.md`

## Objective
Extend review-implementation agent to verify AC fulfillment: every AC from the planning doc should have corresponding implementation and tests. Add graceful handling for tasks without AC.

## Tasks

### Task 1: Add AC Fulfillment Criterion to Review-Implementation
**Status:** completed

**Modify:**
- `claude/agents/review-implementation.md`

**Requirements:**
- Add new section `### 7. AC Fulfillment` after existing section `### 6. Safety` (after line 73)
- Criterion checks:
  - Read `## Acceptance Criteria` from the source planning doc referenced in the tasks file
  - For each `AC-N`, verify:
    - At least one completed task traces to it (via `**Traces to:**` field)
    - The tracing task's implementation exists in the code changes
    - A test covers the behavioral expectation described in the AC
  - Report fulfillment status per AC:
    - `FULFILLED` — implementation and test exist
    - `NOT VERIFIED` — no test found for this AC
    - `MISSING` — no task traces to this AC or tracing task not implemented
  - `NOT VERIFIED` and `MISSING` are rejection reasons
  - If source planning doc has no `## Acceptance Criteria` section, skip this criterion silently
- Add `AC_FULFILLMENT` to the Categories line in Response Format section (currently line 100: `Categories: CORRECTNESS, PATTERNS, RULES, TESTS, COMPLETENESS, SAFETY`)
- For orchestrated tasks: read AC fulfillment across all phase files and the main tasks file
- Include AC fulfillment summary in PASS verdict as well (informational):
```
AC Fulfillment: 5/5 FULFILLED
```

**Example addition:**
```markdown
### 7. AC Fulfillment
- If source planning doc contains `## Acceptance Criteria`:
  - Every AC-N has at least one task tracing to it with completed implementation
  - Every AC-N has at least one test covering its behavioral expectation
  - Report: `AC-N: FULFILLED | NOT VERIFIED | MISSING`
  - NOT VERIFIED and MISSING are blocking issues
  - If no AC section exists in the planning doc, skip this criterion
```

## Phase Verification
Run:
- Verify `claude/agents/review-implementation.md` contains "AC Fulfillment" section
- Verify `claude/agents/review-implementation.md` contains "AC_FULFILLMENT" in Categories line
- Verify the agent file still has valid frontmatter and all 7 criteria sections

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Added `### 7. AC Fulfillment` section after `### 6. Safety` (lines 76-89)
- `AC_FULFILLMENT` appended to Categories line in Response Format section
- PASS verdict format extended with optional `AC Fulfillment: N/N FULFILLED` line; inclusion conditional on planning doc having `## Acceptance Criteria`; line-by-line AC listing recommended when any AC is NOT VERIFIED or MISSING
- Planning doc is located via `**Source doc:**` field or `## Source` section — consistent with how implement skill reads it
- Graceful fallback: criterion silently skipped when no `## Acceptance Criteria` section in planning doc
- `NOT VERIFIED` and `MISSING` are both blocking rejection reasons; `FULFILLED` is not listed as a blocking category
