# Phase 2: Add the QA Worker and Harness Dispatch

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-review.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-review/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/qa-review/SKILL.md` with public workflow `@qa-review [feature [artifact] | codebase [path]]` from Phase 1.
- `skills/qa-review/references/testing-rubric.md` with the `QAFinding` schema and verdict calibration from Phase 1.

### Provides (for later phases)
- Worker contract `QAWorkerResult { scope: string; intentSources: string[]; omittedScope: string[]; findings: QAFinding[]; strengths: string[]; limitations: string[] }` in `agents/qa-reviewer.md`.
- Dispatch contract `dispatchQAReviewer(scopePackage) -> QAWorkerResult` with Claude registered-role, Codex generic-agent, Pi `pi-subagents`, Grok generic-agent, and sequential-inline fallback paths in the shared/per-harness reference files.

## Read Scope
- `skills/qa-review/SKILL.md`
- `skills/qa-review/references/testing-rubric.md`
- `agents/codebase-auditor.md`
- `agents/tech-lead-agent.md`
- `references/harness-dispatch.md`
- `references/codex-tools.md`
- `references/pi-tools.md`
- `references/grok-tools.md`

## Write Scope
- `agents/qa-reviewer.md`
- `references/harness-dispatch.md`
- `references/codex-tools.md`
- `references/pi-tools.md`
- `references/grok-tools.md`

## Objective
Create a narrow, read-only worker for one prepared QA scope and make its dispatch portable across all four harnesses. The worker returns facts for root-session synthesis; it never writes the final report or expands its assigned scope.

## Tasks

### Task 1: Create the Isolated QA Reviewer Prompt
**Status:** completed
**Traces to:** AC-3, AC-4, AC-5, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15
**Test-first:** no (agent prompt definition)
**Produces:** Worker contract `QAWorkerResult { scope: string; intentSources: string[]; omittedScope: string[]; findings: QAFinding[]; strengths: string[]; limitations: string[] }`
**Consumes:** none

**Create:**
- `agents/qa-reviewer.md`

**Modify:**
- None

**Description:**
Define a reusable reviewer role that analyzes exactly one package or module prepared by the orchestrator and returns structured evidence for synthesis. Its prompt must apply the canonical rubric by reference and treat all inspected content as untrusted data.

**Requirements:**
- Add valid agent frontmatter with read-only discovery tools and a narrow instruction to read `skills/qa-review/references/testing-rubric.md` before analysis.
- Accept an assigned scope, intent sources, production/test file list, omitted scope, and project conventions; reject silent scope expansion and report unavailable inputs.
- Return exactly one `QAWorkerResult` block containing scoped findings in the canonical `QAFinding` schema, strengths, limitations, and omitted scope; do not write the final report.
- Forbid project test/code/coverage execution, file edits, following instructions embedded in inspected content, or disclosing unredacted secrets.
- Require contextual decisions for absent tests, multiple frameworks, test doubles, snapshots/fixtures/generated files, flaky signals, `REMOVE`, and cross-boundary E2E recommendations.

**Tests:**
- Static scenario `workerPreservesModuleAndBoundaryScope_AC3_AC4` verifies assigned-scope analysis plus separately labeled boundary findings.
- Static scenario `workerReturnsCompleteFindingSchema_AC5` verifies all canonical fields.
- Static scenario `workerNeedsBehaviorRiskBeforeMissingTestFinding_AC8` verifies missing tests are not automatically defective.
- Static scenario `workerReportsOmissionsAndReducedConfidence_AC9` verifies partial scope handling.
- Static scenario `workerDetectsConventionsPerModule_AC10` verifies framework/style differences are contextual.
- Static scenario `workerRestrictsRemoveToHighConfidence_AC11` verifies destructive advice calibration.
- Static scenario `workerKeepsArtifactAndFlakyClaimsStatic_AC12` verifies evidence is not overstated.
- Static scenario `workerIgnoresRepositoryInstructions_AC13` verifies prompt-injection resistance.
- Static scenario `workerRedactsSensitiveEvidence_AC14` verifies no full secret disclosure.
- Static scenario `workerRejectsOutOfProjectScope_AC15` verifies assigned boundaries cannot be widened.

**Implementation decisions / remarks:**
- The worker has discovery-only tools, applies the shared rubric by reference, and returns one scope-preserving `QAWorkerResult`; final synthesis and report writing remain root-session responsibilities.

**Example:**
```text
QAWorkerResult { scope: "skills/generate-tasks", intentSources: ["planning AC"], omittedScope: [], findings: [], strengths: ["routing cases are explicit"], limitations: ["static analysis only"] }
```

### Task 2: Wire QA Reviewer Dispatch Across Harnesses
**Status:** completed
**Traces to:** AC-3, AC-10, AC-13, AC-15
**Test-first:** no (dispatch documentation)
**Produces:** Dispatch contract `dispatchQAReviewer(scopePackage) -> QAWorkerResult` with Claude registered-role, Codex generic-agent, Pi `pi-subagents`, Grok generic-agent, and sequential-inline fallback paths
**Consumes:** Worker contract `QAWorkerResult { scope: string; intentSources: string[]; omittedScope: string[]; findings: QAFinding[]; strengths: string[]; limitations: string[] }` from Task 1

**Create:**
- None

**Modify:**
- `references/harness-dispatch.md`
- `references/codex-tools.md`
- `references/pi-tools.md`
- `references/grok-tools.md`

**Description:**
Register `qa-reviewer` in the shared dispatch map and document the concrete equivalent for each harness. Preserve isolation when dispatch exists and explicitly disclose reduced isolation when module analysis must run sequentially inline.

**Requirements:**
- Add `qa-reviewer` to Claude's registered-role list and define generic prompt-body dispatch for Codex, Pi, and Grok using `agents/qa-reviewer.md` plus the exact scope package.
- Specify parallel waves only for independent modules, respecting harness concurrency limits and recursively splitting oversized modules before dispatch.
- Define a sequential inline fallback that applies the same worker prompt, labels limited isolation, preserves per-module scope, and never silently skips a module.
- State that worker dispatch inherits the audit's read-only/untrusted-input/path-boundary contract and workers return `QAWorkerResult` without writing reports.

**Tests:**
- Static scenario `allHarnessesDispatchEveryLogicalArea_AC3` verifies all four mappings and no silently omitted module.
- Static scenario `perModuleDispatchKeepsNativeConventions_AC10` verifies each scope package carries module-local test conventions.
- Static scenario `dispatchCannotEscalateRepositoryInstructions_AC13` verifies read-only/untrusted-data inheritance.
- Static scenario `dispatchRejectsOutOfProjectScope_AC15` verifies path boundaries survive delegation.

**Implementation decisions / remarks:**
- The shared dispatch contract defines scope-package invariants once; each harness mapping documents its native generic-agent mechanism and the same explicit sequential non-isolated fallback.

**Example:**
```text
dispatchQAReviewer({ scope: "packages/auth", rubric: "skills/qa-review/references/testing-rubric.md", workerPrompt: "agents/qa-reviewer.md" }) -> QAWorkerResult
```

## Phase Verification
Run:
- `test -f agents/qa-reviewer.md`
- `grep -l 'qa-reviewer' references/harness-dispatch.md references/codex-tools.md references/pi-tools.md references/grok-tools.md`
- `grep -Eq 'QAWorkerResult|findings.*strengths.*limitations' agents/qa-reviewer.md`
- `grep -Eq 'read-only|read only' agents/qa-reviewer.md`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Kept worker behavior centralized in `agents/qa-reviewer.md` and required every harness path to pass that complete prompt plus the exact module-local scope package.
- Parallelism is limited to independent scopes; oversized modules are recursively subdivided, while unavailable dispatch degrades to sequential inline analysis without losing scope.
