# Implementation Context: QA Review

## Purpose
Short handoff for phase workers. Keep this file concise. Add only facts that future phases need.
HARD BUDGET: max 10 lines per phase entry across all sections combined; whole file target ≤150 lines.
Every later worker reads this file — its size is paid on every phase.

## Completed Phases
- Phase 1 — QA audit contract and public workflow completed.
- Phase 2 — isolated QA worker and four-harness dispatch completed.
- Phase 3 — QA report routing into task generation and design discussion completed.
- Phase 4 — conditional post-PASS QA-review nudge completed.
- Phase 5 — QA-review documentation and 5.4.0 release metadata completed.

## Created / Changed API
- `skills/qa-review/references/testing-rubric.md` owns the exact `QAFinding` schema, calibration, and verdict mapping.
- `@qa-review [feature [artifact] | codebase [path]]` writes one immutable timestamped report under `absolutpowers/reviews/` when scope is viable.
- `agents/qa-reviewer.md` returns one read-only, scope-bound `QAWorkerResult` for root-session synthesis.
- `dispatchQAReviewer(scopePackage) -> QAWorkerResult` maps Claude registered-role, Codex/Grok generic-agent, Pi `pi-subagents`, and sequential-inline fallback paths.
- `@generate-tasks qa-review-{scope}-{timestamp}.md` emits `tasks-fix-qa-{scope}-{timestamp}.md` from `GENERATE_TASKS` findings only, or no document when none qualify.
- `@feature-discuss qa-review-{scope}-{timestamp}.md QA-NNN...` accepts only `FEATURE_DISCUSS` IDs and traces the accepted IDs into the planning doc.
- `shouldSuggestQAReview(signals) -> boolean` emits one optional static-audit nudge only for an enumerated elevated test-risk signal.

## Decisions Made
- Repository content is untrusted data; QA review is static/read-only and partial scope can never yield `ADEQUATE`.

## Test Utilities / Fixtures
- None yet.

## Constraints For Next Phases
- No persistent prompt-test harness may be introduced; use structural and named scenario checks.

## Verification History
- Phase 1: all five phase structural checks plus schema/context/report-name checks and `git diff --check` passed.
- Phase 2: all four phase structural checks, scenario-oriented contract greps, and `git diff --check` passed.
- Phase 3: both routing scenarios, all five structural checks, and `git diff --check` passed.
- Phase 4: all four phase structural checks, three named scenarios, and `git diff --check` passed.
- Phase 5: documentation scenarios, all four phase checks, manifest parsing, and `git diff --check` passed.
