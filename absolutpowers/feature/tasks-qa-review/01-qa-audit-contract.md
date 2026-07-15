# Phase 1: Define the QA Audit Contract

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- Markdown contract `QAFinding { id: string; severity: blocker | major | minor | nit; confidence: high | medium | low; evidence: string; risk: string; operation: ADD | REWRITE | REMOVE | MOVE_LEVEL | MERGE; route: INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS; recommendation: string; example?: string }` in `skills/qa-review/references/testing-rubric.md`, with `evidence` formatted as `path:line`.
- Public workflow `@qa-review [feature [artifact] | codebase [path]]` with report paths `feature -> absolutpowers/reviews/qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, whole codebase `-> absolutpowers/reviews/qa-review-codebase-YYYY-MM-DD-HHmmss.md`, and scoped module `-> absolutpowers/reviews/qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md` in `skills/qa-review/SKILL.md`.

## Read Scope
- `absolutpowers/feature/planning-qa-review.md`
- `skills/analyze/SKILL.md`
- `skills/review/SKILL.md`
- `skills/triada-review/SKILL.md`
- `agents/codebase-auditor.md`
- `references/harness-dispatch.md`

## Write Scope
- `skills/qa-review/SKILL.md`
- `skills/qa-review/references/testing-rubric.md`

## Objective
Create the single source of truth for evaluating test value and the host-agnostic workflow that applies it in feature and codebase modes. The contract must remain static-analysis-only, protect against prompt injection and sensitive-data disclosure, and always emit a uniquely named report when analysis can proceed.

## Tasks

### Task 1: Define the Testing Rubric and Finding Schema
**Status:** completed
**Traces to:** AC-5, AC-8, AC-10, AC-11, AC-12, AC-14
**Test-first:** no (Markdown contract definition)
**Produces:** Markdown contract `QAFinding { id: string; severity: blocker | major | minor | nit; confidence: high | medium | low; evidence: string; risk: string; operation: ADD | REWRITE | REMOVE | MOVE_LEVEL | MERGE; route: INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS; recommendation: string; example?: string }`, with `evidence` formatted as `path:line`
**Consumes:** none

**Create:**
- `skills/qa-review/references/testing-rubric.md`

**Modify:**
- None

**Description:**
Define one reusable rubric for feature and codebase audits so verdicts and recommendations cannot drift between modes or workers. The rubric must distinguish evidence-backed test-value findings from style preferences and calibrate destructive recommendations conservatively.

**Requirements:**
- Define the seven rubric dimensions from the planning doc, including behavior/intent coverage, scenario completeness, regression value, test doubles, test level, test construction/flaky signals, and integration/E2E strategy.
- Define the exact `QAFinding` fields and the `ADEQUATE | IMPROVEMENTS_RECOMMENDED | GAPS_FOUND | MISLEADING_CONFIDENCE` verdict mapping, including the rule that incomplete scope cannot yield `ADEQUATE`.
- Specify severity and confidence calibration, including `REMOVE` only at high confidence with concrete tautology, duplication, or no-regression-value evidence.
- Specify contextual handling for absent tests, multiple frameworks, snapshots, fixtures, generated artifacts, and static flaky signals without presenting non-executed instability as fact.
- Require safe `path:line` evidence that redacts full secrets, credentials, tokens, and sensitive fixture data.

**Tests:**
- Static scenario `findingSchemaAndVerdictMatchSeverity_AC5` verifies every finding field and highest-severity/completeness verdict rule is explicit.
- Static scenario `missingTestsRequireConcreteBehaviorRisk_AC8` verifies absence alone is not a finding.
- Static scenario `frameworkDifferencesAreContextNotDefects_AC10` verifies per-module conventions are discovered before judgment.
- Static scenario `removeRequiresHighConfidenceEvidence_AC11` verifies conservative `REMOVE` routing.
- Static scenario `artifactsAndFlakySignalsStayContextual_AC12` verifies snapshots/fixtures/generated files are contextual and flaky status remains unconfirmed.
- Static scenario `findingEvidenceRedactsSensitiveValues_AC14` verifies safe evidence requirements.

**Implementation decisions / remarks:**
- The rubric is the sole definition of findings and verdicts for both modes; partial scope caps the verdict below `ADEQUATE`, and destructive recommendations require direct high-confidence evidence.

**Example:**
```text
QAFinding { id: "QA-001", severity: major, confidence: high, evidence: "src/auth/login.test.ts:42", risk: "expired sessions can be accepted without regression coverage", operation: ADD, route: GENERATE_TASKS, recommendation: "add an integration case for an expired signed session" }
```

### Task 2: Implement the Host-Agnostic QA Review Workflow
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-9, AC-13, AC-15
**Test-first:** no (skill workflow prompt)
**Produces:** Public workflow `@qa-review [feature [artifact] | codebase [path]]` with report paths `feature -> absolutpowers/reviews/qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, whole codebase `-> absolutpowers/reviews/qa-review-codebase-YYYY-MM-DD-HHmmss.md`, and scoped module `-> absolutpowers/reviews/qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md`
**Consumes:** Markdown contract `QAFinding { id: string; severity: blocker | major | minor | nit; confidence: high | medium | low; evidence: string; risk: string; operation: ADD | REWRITE | REMOVE | MOVE_LEVEL | MERGE; route: INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS; recommendation: string; example?: string }`, with `evidence` formatted as `path:line`, from Task 1

**Create:**
- `skills/qa-review/SKILL.md`

**Modify:**
- None

**Description:**
Implement the audit router, scope discovery, static inspection, synthesis, report writing, and terminal routing around the shared rubric. Keep the workflow usable without planning/AC when other intent sources are sufficient, while stopping safely when feature scope cannot be established.

**Requirements:**
- Define frontmatter and argument parsing with default `feature`, explicit `feature [artifact]`, and `codebase [path]`, validating requested paths stay inside the audited project and accessible scope.
- In feature mode, collect intent in priority order from planning/AC, tasks, PR/commits, then production/test diff including committed-base, staged, unstaged, and untracked changes; stop with a clear explanation when neither changes nor a scope artifact exists.
- In codebase mode, discover workspace/package, domain, layer, then top-level directory boundaries; audit requested modules narrowly and track cross-boundary integration/E2E recommendations separately.
- Treat repository content as untrusted data, forbid running project tests/code/coverage or editing code, redact sensitive evidence, and record unavailable/omitted scope with reduced confidence.
- Write exactly one new timestamped Markdown report for a completed audit: feature uses `qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, whole codebase uses `qa-review-codebase-YYYY-MM-DD-HHmmss.md`, and a scoped module uses `qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md`; include Scope, Intent Sources, Omitted Scope, Actionable Findings, Strengths, Verdict, Limitations, and ordered Next Actions, then synthesize/deduplicate findings and route them by `INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS`.

**Tests:**
- Static scenario `defaultFeatureWritesOneReadOnlyReport_AC1` verifies default mode, complete diff collection, exact `qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md` naming, one report, and no test/coverage execution.
- Static scenario `featureWithoutPlanningUsesFallbackIntent_AC2` verifies fallback intent sources and confidence limitations.
- Static scenario `codebaseDiscoversAndMergesLogicalAreas_AC3` verifies per-area and boundary synthesis without lost scope.
- Static scenario `wholeCodebaseUsesCodebaseReportName_AC3` verifies exact `qa-review-codebase-YYYY-MM-DD-HHmmss.md` naming.
- Static scenario `moduleScopeSeparatesCrossBoundaryAdvice_AC4` verifies strict local scope, labeled integration/E2E recommendations, and exact `qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md` naming.
- Static scenario `reportSchemaAndVerdictUseRubric_AC5` verifies stable finding fields and rubric verdict mapping.
- Static scenario `reportOrdersRoutesForSafeHandoff_AC6` verifies decision-first, inline-approval, task-generation, then re-audit ordering.
- Static scenario `emptyFeatureScopeStopsWithoutReport_AC7` verifies no accidental codebase fallback or misleading report.
- Static scenario `partialAuditCannotBeAdequate_AC9` verifies omitted scope, lower confidence, and verdict restriction.
- Static scenario `repositoryInstructionsRemainUntrustedData_AC13` verifies prompt injection cannot trigger execution or edits.
- Static scenario `externalOrUnavailableScopeIsRejectedOrOmitted_AC15` verifies no implicit scan expansion.

**Implementation decisions / remarks:**
- The workflow validates project-local scope before reading, treats repository content as untrusted data, and writes one immutable local-second report only after a viable audit completes.

**Example:**
```text
@qa-review feature absolutpowers/feature/planning-auth.md
@qa-review codebase skills/generate-tasks
```

## Phase Verification
Run:
- `test -f skills/qa-review/SKILL.md && test -f skills/qa-review/references/testing-rubric.md`
- `grep -Eq 'feature.*codebase|codebase.*feature' skills/qa-review/SKILL.md`
- `grep -Eq 'do not run|nie urucham' skills/qa-review/SKILL.md`
- `grep -Eq 'ADD.*REWRITE.*REMOVE.*MOVE_LEVEL.*MERGE' skills/qa-review/references/testing-rubric.md`
- `grep -Eq 'ADEQUATE.*IMPROVEMENTS_RECOMMENDED.*GAPS_FOUND.*MISLEADING_CONFIDENCE' skills/qa-review/references/testing-rubric.md`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Kept mode discovery, analysis, synthesis, routing, and report ownership in the main skill while defining isolated worker dispatch as an optional scaling path with an explicit inline fallback.
- Preserved a hard static-analysis-only boundary: the skill may read repository/Git/available PR metadata and write its single report, but cannot execute project code or edit audited artifacts.
