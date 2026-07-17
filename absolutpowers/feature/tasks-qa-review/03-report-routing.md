# Phase 3: Route QA Reports into Planning Workflows

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/qa-review/SKILL.md` with the stable `Actionable Findings` and ordered Next Actions report contract from Phase 1.
- `skills/qa-review/references/testing-rubric.md` with routes `INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS` from Phase 1.

### Provides (for later phases)
- Mapping `qa-review-{scope}-YYYY-MM-DD-HHmmss.md -> tasks-fix-qa-{scope}-YYYY-MM-DD-HHmmss.md` filtering `route == GENERATE_TASKS` in `skills/generate-tasks/SKILL.md` and `skills/generate-tasks/references/task-formats.md`.
- Planning handoff `QA finding IDs with route FEATURE_DISCUSS -> planning-{slug}.md source traceability` in `skills/feature-discuss/SKILL.md`.

## Read Scope
- `skills/qa-review/SKILL.md`
- `skills/qa-review/references/testing-rubric.md`
- `skills/generate-tasks/SKILL.md`
- `skills/generate-tasks/references/task-formats.md`
- `skills/feature-discuss/SKILL.md`
- `absolutpowers/archives/fix-major-v5-review/tasks-fix-major-v5-review.md`

## Write Scope
- `skills/generate-tasks/SKILL.md`
- `skills/generate-tasks/references/task-formats.md`
- `skills/feature-discuss/SKILL.md`

## Objective
Make the durable QA report a safe input to the two appropriate downstream workflows without turning mixed routing into implicit scope expansion. Ready findings become implementation tasks; unresolved product/design findings become a traced planning discussion.

## Tasks

### Task 1: Teach Generate-Tasks to Consume Ready QA Findings
**Status:** completed
**Traces to:** AC-6
**Test-first:** no (workflow routing prompt)
**Produces:** Mapping `qa-review-{scope}-YYYY-MM-DD-HHmmss.md -> tasks-fix-qa-{scope}-YYYY-MM-DD-HHmmss.md` filtering `route == GENERATE_TASKS`
**Consumes:** none

**Create:**
- None

**Modify:**
- `skills/generate-tasks/SKILL.md`
- `skills/generate-tasks/references/task-formats.md`

**Description:**
Add QA reports as a first-class input while preserving the report's scope and timestamp in the output filename. Ensure only findings already routed for task planning become tasks and make every omission visible to the user.

**Requirements:**
- Add `./absolutpowers/reviews/qa-review-{scope}-YYYY-MM-DD-HHmmss.md` as an input type and map it to `./absolutpowers/feature/tasks-fix-qa-{scope}-YYYY-MM-DD-HHmmss.md` by replacing `qa-review-` with `tasks-fix-qa-`.
- Parse the stable `Actionable Findings` section and generate tasks only for findings whose route is `GENERATE_TASKS`, preserving finding IDs, severity, evidence, operation, recommendation, report scope, and timestamp.
- List skipped `FEATURE_DISCUSS` and `INLINE_FIX` finding IDs with the reason and their correct next workflow; never silently include them in task scope.
- Extend the task-format Source doc variants and project context so the originating QA report and selected finding IDs remain traceable.
- Clarify that a report with no `GENERATE_TASKS` findings produces no tasks doc and instead returns the explicit skipped/routing summary.

**Tests:**
- Static scenario `mixedQaReportGeneratesOnlyReadyFindings_AC6` verifies filtering, omission lists, traceability, and output naming.

**Implementation decisions / remarks:**
- Added QA reports as a fifth input variant with basename-preserving `qa-review-` → `tasks-fix-qa-` naming.
- Task generation selects only exact `GENERATE_TASKS` routes, retains the full finding context and report provenance, and returns explicit per-ID routing for every skipped finding; an empty selected set writes no tasks doc.

**Example:**
```text
qa-review-auth-2026-07-15-101530.md -> tasks-fix-qa-auth-2026-07-15-101530.md
```

### Task 2: Teach Feature-Discuss to Resolve QA Design Findings
**Status:** completed
**Traces to:** AC-6
**Test-first:** no (workflow routing prompt)
**Produces:** Planning handoff `QA finding IDs with route FEATURE_DISCUSS -> planning-{slug}.md source traceability`
**Consumes:** none

**Create:**
- None

**Modify:**
- `skills/feature-discuss/SKILL.md`

**Description:**
Add an explicit entry path for selected QA findings whose expected behavior or test-level decision is unresolved. The discussion remains a design workflow and records its report/finding provenance in the resulting planning document.

**Requirements:**
- Accept a QA report path plus selected finding IDs and validate that each selected finding exists and has route `FEATURE_DISCUSS`.
- Load the report scope, intent sources, evidence, risk, recommendation, and limitations as starting context without treating the recommendation as an already accepted solution.
- Preserve normal feature-discuss acceptance/design gates and prevent `GENERATE_TASKS` or `INLINE_FIX` findings from silently joining this planning scope.
- Add source traceability in the resulting planning doc containing the QA report path and selected finding IDs.
- Route the accepted planning doc back to the standard `generate-tasks -> implement -> review` chain.

**Tests:**
- Static scenario `qaDesignFindingsEnterDiscussionWithTraceability_AC6` verifies route validation, provenance, normal design gates, and downstream handoff.

**Implementation decisions / remarks:**
- Added Tryb D for a QA report plus selected IDs; it validates exact `FEATURE_DISCUSS` routes before normal design work and rejects mixed-route scope explicitly.
- Planning provenance records only accepted QA IDs, while recommendations remain unaccepted hypotheses and the standard acceptance/review pipeline stays binding.

**Example:**
```text
Render the native `feature-discuss` command for `absolutpowers/reviews/qa-review-auth-2026-07-15-101530.md QA-003 QA-007` using `references/harness-command-contract.md`.
```

## Phase Verification
Run:
- `grep -Eq 'qa-review-.*tasks-fix-qa-' skills/generate-tasks/SKILL.md`
- `grep -Eq 'GENERATE_TASKS' skills/generate-tasks/SKILL.md`
- `grep -Eq 'INLINE_FIX' skills/generate-tasks/SKILL.md`
- `grep -Eq 'FEATURE_DISCUSS' skills/generate-tasks/SKILL.md skills/feature-discuss/SKILL.md`
- `grep -Eq 'qa-review' skills/generate-tasks/references/task-formats.md`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Kept routing logic in the two owning workflow skills and extended both single-file and orchestrated Source/Project Context templates for QA traceability.
- Verified both named static scenarios structurally, all five phase commands, and `git diff --check`.
