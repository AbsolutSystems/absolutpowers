# Phase 2: Extend Review-Plan with AC Quality Criterion

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1 completed: AC format defined (three categories: Happy path, Edge cases, Security; `AC-N:` numbering; behavioral, no implementation details)

### Provides (for later phases)
- Updated `claude/agents/review-plan.md` with criterion "5. AC Quality" and category `AC_QUALITY`
- `docs/review-gates.md` awareness that review-plan now checks AC (updated in Phase 7, but criterion name and categories established here)

## Read Scope
- `claude/agents/review-plan.md` — current file to modify
- `claude/agents/qa-enrichment.md` — to understand what AC format review-plan should validate
- `./absolutpowers/feature/planning-qa-enrichment.md` — AC format reference

## Write Scope
- `claude/agents/review-plan.md`

## Objective
Add a fifth review criterion "AC Quality" to the review-plan agent. This criterion validates that planning docs contain well-formed Acceptance Criteria: present, behavioral, verifiable, complete relative to scope, and free of implementation details.

## Tasks

### Task 1: Add AC Quality Criterion to Review-Plan
**Status:** completed

**Modify:**
- `claude/agents/review-plan.md`

**Requirements:**
- Add new section `### 5. AC Quality` after existing section `### 4. Actionability` (after line 60)
- Criterion checks:
  - `## Acceptance Criteria` section exists in the planning doc
  - AC covers all three categories: Happy path, Edge cases, Security
  - Each AC is behavioral and user-facing (not "file X exists", not "method Y returns Z")
  - Each AC contains zero implementation details (no file paths, no method signatures, no class names)
  - Each AC is verifiable as true/false
  - AC are numbered sequentially with `AC-N:` format
  - AC set is reasonably complete relative to the plan scope (not just happy path)
  - No trivial/vague AC like "system works correctly" or "feature is implemented"
- Add `AC_QUALITY` to the Categories line in Response Format section (after line 87, currently: `Categories: COMPLETENESS, FEASIBILITY, ARCHITECTURE, ACTIONABILITY`)
- Add `AC_QUALITY` to the categories table in `docs/review-gates.md` — but that's Phase 7's responsibility. Only update the agent file here.
- Handle graceful fallback: if planning doc has no `## Acceptance Criteria` section, flag as `AC_QUALITY` issue ("Acceptance Criteria section missing — QA enrichment may not have run")

**Example addition after line 60:**
```markdown
### 5. AC Quality
- Acceptance Criteria section exists with three categories (Happy path, Edge cases, Security)
- Each AC is behavioral and user-facing — no implementation details (file paths, method signatures, class names)
- Each AC is verifiable as true/false — not vague ("works correctly") or unbounded
- AC numbering is sequential (`AC-1:`, `AC-2:`, ...)
- AC coverage is reasonable relative to plan scope — not only happy path
- No trivial AC that would pass regardless of implementation quality
```

## Phase Verification
Run:
- Verify `claude/agents/review-plan.md` contains "AC Quality" section
- Verify `claude/agents/review-plan.md` contains "AC_QUALITY" in Categories line
- Verify the agent file still has valid frontmatter and all 5 criteria sections

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Added `### 5. AC Quality` section after `### 4. Actionability` in `claude/agents/review-plan.md`.
- Section contains 6 bullet checks plus a graceful fallback bullet for missing AC section ("Acceptance Criteria section missing — QA enrichment may not have run").
- `AC_QUALITY` appended to the existing Categories line (now: `COMPLETENESS, FEASIBILITY, ARCHITECTURE, ACTIONABILITY, AC_QUALITY`).
- No changes to any file outside Write Scope.
