# Final Verification: QA Review

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Public workflow `@qa-review [feature [artifact] | codebase [path]]` with report paths `feature -> absolutpowers/reviews/qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, whole codebase `-> absolutpowers/reviews/qa-review-codebase-YYYY-MM-DD-HHmmss.md`, and scoped module `-> absolutpowers/reviews/qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md`, plus the `QAFinding` contract, from Phase 1.
- Worker contract `QAWorkerResult { scope: string; intentSources: string[]; omittedScope: string[]; findings: QAFinding[]; strengths: string[]; limitations: string[] }` plus dispatch contract `dispatchQAReviewer(scopePackage) -> QAWorkerResult` from Phase 2.
- Mapping `qa-review-{scope}-YYYY-MM-DD-HHmmss.md -> tasks-fix-qa-{scope}-YYYY-MM-DD-HHmmss.md` filtering `route == GENERATE_TASKS` and planning handoff `QA finding IDs with route FEATURE_DISCUSS -> planning-{slug}.md source traceability` from Phase 3.
- Decision contract `shouldSuggestQAReview(signals) -> boolean` from Phase 4 and release `5.4.0` metadata in all three plugin manifests, `README.md`, and `CLAUDE.md` from Phase 5.

### Provides (for later phases)
- None (terminal verification).

## Read Scope
- `absolutpowers/feature/planning-qa-review.md`
- `absolutpowers/feature/tasks-qa-review.md`
- `absolutpowers/feature/tasks-qa-review/*.md`
- `skills/qa-review/SKILL.md`
- `skills/qa-review/references/testing-rubric.md`
- `agents/qa-reviewer.md`
- `references/harness-dispatch.md`
- `references/codex-tools.md`
- `references/pi-tools.md`
- `references/grok-tools.md`
- `skills/generate-tasks/SKILL.md`
- `skills/generate-tasks/references/task-formats.md`
- `skills/feature-discuss/SKILL.md`
- `skills/implement/SKILL.md`
- `hooks/session-context.md`
- `README.md`
- `docs/contributing.md`
- `CLAUDE.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

## Write Scope
- None

## Objective
Verify the integrated prompt, routing, documentation, and release contracts without executing audited project tests/code or introducing the explicitly out-of-scope prompt-test harness. Every command must pass before this phase and the parent plan can be marked completed.

## Tasks

### Task 1: Run Integrated Structural and Scenario Verification
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15
**Test-first:** no (verification-only task)
**Produces:** none
**Consumes:** none

**Create:**
- None

**Modify:**
- None

**Description:**
Run repository-canonical structural checks plus targeted contract inspections across every touched artifact. Record command outputs and any intentionally inapplicable check; do not mark complete if a required command or scenario fails.

**Requirements:**
- Run JSON manifest validation, session-hook JSON validation, all-skill frontmatter validation, and `git diff --check` using the commands from the parent Project Context.
- Verify the new skill/rubric/worker exist; all four harness mappings mention `qa-reviewer`; downstream workflows contain all three routes; the implement nudge is optional/nonblocking; and current release metadata is consistently 5.4.0.
- Inspect the final diff against `planning-qa-review.md` and confirm the audit never runs tests/code/coverage, never edits audited files, never follows repository instructions, and redacts sensitive evidence.
- Confirm every AC-1 through AC-15 has at least one literal token-bearing named check in the phase task `Tests:` sections; record persistent test-source grep as `not applicable` because this prompt-only repo has no test tree and the accepted scope forbids a new automatic prompt-quality harness.
- Record skipped checks with reasons and leave this task pending on any unexplained omission or failed validation.

**Tests:**
- Integrated scenario `defaultAndFallbackFeatureIntent_AC1_AC2` validates default feature behavior and fallback intent sources.
- Integrated scenario `codebaseAndModuleScopeSynthesis_AC3_AC4` validates area discovery, per-module analysis, and boundary labeling.
- Integrated scenario `findingVerdictAndRoutingContract_AC5_AC6` validates report schema, verdicts, and safe mixed-route handoff.
- Integrated scenario `emptyAndMissingTestsAreNotMisrepresented_AC7_AC8` validates stop and behavior-risk rules.
- Integrated scenario `partialAndMultiFrameworkAuditsStayHonest_AC9_AC10` validates omissions/confidence and local conventions.
- Integrated scenario `removeArtifactsAndFlakyClaimsAreConservative_AC11_AC12` validates destructive recommendations and static-evidence limits.
- Integrated scenario `untrustedContentCannotBreakReadOnlyBoundary_AC13` validates prompt-injection resistance.
- Integrated scenario `sensitiveEvidenceIsRedacted_AC14` validates secret handling.
- Integrated scenario `externalScopeCannotExpandAudit_AC15` validates project path boundaries.

**Implementation decisions / remarks:**
- Commands executed: all commands in `## Phase Verification`, direct frontmatter/whitespace checks for new untracked files, AC-1 through AC-15 named-scenario checks, safety-boundary greps, and current-version documentation checks.
- Results: all required structural, scenario, hook, JSON, routing, safety, whitespace, and release checks passed on 2026-07-15; final combined command exited `0`.
- Skipped checks: persistent test-source grep is not applicable because this prompt-only repository has no prompt test tree and the accepted scope explicitly forbids introducing an automatic prompt-quality harness. AC verification uses the literal token-bearing named structural scenarios in these phase task `Tests:` sections.

**Example:**
```bash
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done
git diff --check
```

## Phase Verification
Run:
- `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done`
- `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null`
- `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done`
- `git diff --check`
- `grep -l 'qa-reviewer' references/harness-dispatch.md references/codex-tools.md references/pi-tools.md references/grok-tools.md`
- `grep -Eq 'INLINE_FIX' skills/qa-review/SKILL.md skills/generate-tasks/SKILL.md`
- `grep -Eq 'GENERATE_TASKS' skills/qa-review/SKILL.md skills/generate-tasks/SKILL.md`
- `grep -Eq 'FEATURE_DISCUSS' skills/qa-review/SKILL.md skills/feature-discuss/SKILL.md`
- `python3 -c 'import json; paths=[".claude-plugin/plugin.json",".codex-plugin/plugin.json",".grok-plugin/plugin.json"]; values=[json.load(open(p))["version"] for p in paths]; assert values == ["5.4.0"] * 3, values'`

## Completion Criteria
- All implementation phases are completed and reviewed.
- All final verification commands pass with no unexplained omissions.
- Every AC has a named token-bearing scenario check in the task plan.
- No files are changed by this verification phase.
- Results and skipped checks are recorded in this file.

## Implementation Decisions / Remarks
- Verification remained static and did not execute audited project code, tests, coverage, or E2E.
- All AC-1 through AC-15 have literal token-bearing named scenario checks in the phase task specifications; persistent test-source token matching is inapplicable for the documented prompt-only/no-harness constraint.
