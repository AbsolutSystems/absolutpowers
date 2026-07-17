# Phase 4: Add the Conditional Post-Implementation Nudge

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/qa-review/SKILL.md` with public invocation `@qa-review feature [artifact]` from Phase 1.

### Provides (for later phases)
- Decision contract `shouldSuggestQAReview(signals) -> boolean` documented in `skills/implement/SKILL.md`.

## Read Scope
- `skills/qa-review/SKILL.md`
- `skills/implement/SKILL.md`
- `skills/implement/references/orchestrated-process.md`
- `agents/review-implementation.md`

## Write Scope
- `skills/implement/SKILL.md`

## Objective
Add one best-effort suggestion after successful implementation only when the completed change carries elevated test-risk signals. The suggestion must not run QA review, block completion, or change the established review/ship terminal chain.

## Tasks

### Task 1: Add the Risk-Gated QA Review Suggestion
**Status:** completed
**Traces to:** none (optional pipeline integration outside the audit behavior ACs)
**Test-first:** no (user-facing workflow nudge)
**Produces:** Decision contract `shouldSuggestQAReview(signals) -> boolean` documented in `skills/implement/SKILL.md`
**Consumes:** none

**Create:**
- None

**Modify:**
- `skills/implement/SKILL.md`

**Description:**
Place a single optional QA suggestion after implementation PASS and before the existing closeout guidance. Its conditions must be concrete enough to avoid unconditional noise and must preserve `review`/`triada-review` as the pipeline closure point.

**Requirements:**
- Define `shouldSuggestQAReview(signals) -> boolean` as true when at least one signal exists: orchestrated mode; security/public API/migration/integration/multi-module boundary; new critical flow; substantial test rewrite; test-related gate warning; or difficult-to-verify AC.
- When true, suggest one native `qa-review feature [optional planning/tasks artifact]` command once after PASS and explain that it statically evaluates test value without rerunning tests.
- When false, emit no QA nudge; do not make small routine changes noisier.
- State explicitly that the nudge never auto-invokes QA review, never gates completion, and never replaces `review`/`triada-review`.
- Preserve the existing terminal state and closeout ordering `review -> ship -> merge`.

**Tests:**
- Structural scenario `highRiskImplementationSuggestsQaReview` verifies each enumerated signal can trigger the nudge.
- Structural scenario `lowRiskImplementationDoesNotSuggestQaReview` verifies no unconditional suggestion.
- Structural scenario `qaReviewNudgeIsOptionalAndNonBlocking` verifies no automatic dispatch and unchanged terminal chain.

**Implementation decisions / remarks:**
- Documented one post-PASS decision point next to the existing closeout guidance. An explicit
  empty-signal branch suppresses the nudge for routine changes, while the true branch emits it once.

**Example:**
```text
QA review (optional): elevated test-risk signal `multi-module integration`; run `@qa-review feature absolutpowers/feature/planning-qa-review.md` to audit test value without rerunning tests.
```

## Phase Verification
Run:
- `grep -Eq 'qa-review' skills/implement/SKILL.md`
- `grep -Eq 'orchestrated|security|public API|migration|integration|multi-module' skills/implement/SKILL.md`
- `grep -Eq 'optional|opcjonal' skills/implement/SKILL.md`
- `grep -Eq 'never.*auto|nie uruchamiaj.*automaty' skills/implement/SKILL.md`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- `shouldSuggestQAReview(signals)` is prompt-level policy rather than executable code; named
  structural scenarios make its trigger, suppression, and non-blocking behavior reviewable.
