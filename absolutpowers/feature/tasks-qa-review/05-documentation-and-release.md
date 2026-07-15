# Phase 5: Document and Release QA Review

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Public workflow `@qa-review [feature [artifact] | codebase [path]]` with its three exact report-path rules in `skills/qa-review/SKILL.md`, plus `QAFinding` in `skills/qa-review/references/testing-rubric.md`, from Phase 1.
- Worker contract `QAWorkerResult { scope: string; intentSources: string[]; omittedScope: string[]; findings: QAFinding[]; strengths: string[]; limitations: string[] }` plus `dispatchQAReviewer(scopePackage) -> QAWorkerResult` mappings from Phase 2.
- Mapping `qa-review-{scope}-YYYY-MM-DD-HHmmss.md -> tasks-fix-qa-{scope}-YYYY-MM-DD-HHmmss.md` filtering `route == GENERATE_TASKS` and planning handoff `QA finding IDs with route FEATURE_DISCUSS -> planning-{slug}.md source traceability` from Phase 3.
- Decision contract `shouldSuggestQAReview(signals) -> boolean` documented in `skills/implement/SKILL.md` from Phase 4.

### Provides (for later phases)
- None (documentation and release metadata are terminal deliverables).

## Read Scope
- `skills/qa-review/SKILL.md`
- `skills/qa-review/references/testing-rubric.md`
- `agents/qa-reviewer.md`
- `references/harness-dispatch.md`
- `skills/generate-tasks/SKILL.md`
- `skills/feature-discuss/SKILL.md`
- `skills/implement/SKILL.md`
- `README.md`
- `hooks/session-context.md`
- `docs/contributing.md`
- `CLAUDE.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

## Write Scope
- `hooks/session-context.md`
- `README.md`
- `docs/contributing.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`
- `CLAUDE.md`

## Objective
Expose QA review consistently in user guidance, session routing, and maintainer architecture documentation, then publish the feature as release 5.4.0 across every manifest and descriptive version location.

## Tasks

### Task 1: Document Usage, Boundaries, Routing, and Maintenance
**Status:** completed
**Traces to:** AC-1, AC-3, AC-4, AC-6, AC-7
**Test-first:** no (documentation)
**Produces:** none
**Consumes:** none

**Create:**
- None

**Modify:**
- `hooks/session-context.md`
- `README.md`
- `docs/contributing.md`
- `CLAUDE.md`

**Description:**
Update user and maintainer documentation from the implemented contracts, positioning QA review as a specialist on-demand audit rather than another code-review gate. Include invocation examples, report routing, worker ownership, and per-harness degradation without duplicating the testing rubric.

**Requirements:**
- Add `@qa-review` to the session skill map and README on-demand tools with default feature, explicit feature artifact, whole-codebase, and module-path examples.
- Explain the boundary versus `review`, `triada-review`, and `analyze`: static test-value audit, no execution/coverage/code edits, never a mandatory pipeline gate.
- Document report naming, verdicts, stable `Actionable Findings`, the safe `FEATURE_DISCUSS -> INLINE_FIX approval -> GENERATE_TASKS -> re-audit` routing order, and the empty-feature stop behavior.
- Document `agents/qa-reviewer.md`, shared rubric ownership, module-wave dispatch, and explicit inline/sequential reduced-isolation fallback in `docs/contributing.md` and `CLAUDE.md`.
- Keep source-of-truth details linked to `skills/qa-review/references/testing-rubric.md`; do not copy the entire rubric into README or bootstrap context.

**Tests:**
- Documentation scenario `readmeShowsDefaultFeatureAudit_AC1` verifies default invocation and read-only/no-execution positioning.
- Documentation scenario `readmeShowsWholeCodebaseAudit_AC3` verifies logical-area synthesis is described.
- Documentation scenario `readmeShowsScopedModuleAudit_AC4` verifies module invocation and boundary advice distinction.
- Documentation scenario `docsExplainSafeFindingRouting_AC6` verifies mixed-routing order and consumers.
- Documentation scenario `docsExplainEmptyFeatureStop_AC7` verifies no accidental whole-project fallback.

**Implementation decisions / remarks:**
- Documented the four invocation examples, specialist-audit boundaries, exact immutable report
  names, safe finding routing, empty-feature stop, rubric ownership, worker ownership, module
  waves, and explicit reduced-isolation fallback without duplicating the canonical rubric.

**Example:**
```text
@qa-review
@qa-review feature absolutpowers/feature/planning-auth.md
@qa-review codebase skills/generate-tasks
```

### Task 2: Bump All Release Metadata to 5.4.0
**Status:** completed
**Traces to:** none (release metadata)
**Test-first:** no (JSON and prose version metadata)
**Produces:** none
**Consumes:** none

**Create:**
- None

**Modify:**
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`
- `CLAUDE.md`
- `README.md`

**Description:**
Publish the new skill and worker as a minor release. Keep every plugin manifest and the two descriptive current-version locations aligned at exactly 5.4.0.

**Requirements:**
- Set `.claude-plugin/plugin.json` field `version: "5.4.0"`.
- Set `.codex-plugin/plugin.json` field `version: "5.4.0"`.
- Set `.grok-plugin/plugin.json` field `version: "5.4.0"`.
- Update the current repository version in `CLAUDE.md` from `5.3.0` to `5.4.0` and describe QA review in the product capability summary.
- Update README's Current release to `5.4.0` and add a `5.4.0` release-note entry without rewriting historical `5.3.0` references.

**Tests:**
- Structural check `allPluginManifestsReportVersion540` parses all three JSON manifests and compares their `version` fields.
- Structural check `currentReleaseDocsReportVersion540` verifies current-version prose while preserving historical release notes.

**Implementation decisions / remarks:**
- Bumped exactly the three plugin manifests and the two current-version prose locations to
  5.4.0; added a new 5.4.0 changelog entry while preserving historical 5.3.0 release text.

**Example:**
```json
{
  "version": "5.4.0"
}
```

## Phase Verification
Run:
- `grep -l 'qa-review' hooks/session-context.md README.md docs/contributing.md CLAUDE.md`
- `python3 -c 'import json; paths=[".claude-plugin/plugin.json",".codex-plugin/plugin.json",".grok-plugin/plugin.json"]; values=[json.load(open(p))["version"] for p in paths]; assert values == ["5.4.0"] * 3, values'`
- `grep -Eq 'Current release: \*\*5\.4\.0\*\*' README.md`
- `grep -Eq 'Version 5\.4\.0' CLAUDE.md`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- QA-review guidance links to the canonical rubric and summarizes only public workflow,
  ownership, fallback, and routing contracts. Release metadata is aligned at 5.4.0.
