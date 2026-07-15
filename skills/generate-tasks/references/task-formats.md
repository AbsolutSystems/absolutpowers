# Tasks document structure (single-file + orchestrated)

_Extracted from `generate-tasks`. **Read this file** when writing the tasks doc (after Mode is chosen)._

## Tasks Document Structure

Always include `## Mode` near the top of the main tasks file with either `single-file` or `orchestrated`.

### `single-file` structure

Use the existing sequential task format below.

### Section 1: Project Context
Concise, factual overview for agent orientation:

```markdown
## Project Context

**Source doc:** `./absolutpowers/feature/planning-{slug}.md` or `./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md` or `./absolutpowers/feature/{epic-slug}/planning-phase-N-{subslug}.md`

**Epic context (if applicable):** `./absolutpowers/feature/{epic-slug}/planning-main.md`

**Stack:** [languages, frameworks, key libraries]

**Structure:**
- `src/controllers/` - HTTP handlers
- `src/services/` - Business logic
- `src/repos/` - Data access
- [other relevant paths]

**Patterns:**
- [Pattern name]: [one-line description]
- [Pattern name]: [one-line description]

**Conventions:**
- Files: [naming convention]
- Functions: [naming convention]
- Tests: [location pattern, naming]

**Global Constraints:**
- [cross-task requirement copied verbatim from the planning doc: exact versions, naming, copy rules that bind every task in this plan]
- Per Artykuł N: [one-line reference when a `constitution.md` article binds this feature — cite the article number only, never copy the article's text]

> Global Constraints (GC) are spec-derived and scoped to THIS plan — distinct from `constitution.md` (ratified project-wide pryncypia, loaded separately in Step 1 as binding context) and from `rules.md` (project lint/formatting rules). Copying constitution article text into GC instead of citing `Per Artykuł N` is a plan error.

**Verification commands:**
- Backend build/test: `[command]`
- Frontend build/typecheck: `[command]`
- Lint / formatter check: `[command]`

**Reference implementations:**
- `path/to/SimilarService.ts` - [what to reference]
- `path/to/SimilarController.ts` - [what to reference]
```

### Section 2: Implementation Tasks

Sequential tasks the agent executes in order. Each task:

```markdown
### Task [N]: [Action-Oriented Title]
**Status:** pending
**Traces to:** AC-N, AC-M
**Test-first:** yes | no ([short reason when no])
**Produces:** [exact symbol/signature this task exports for later tasks to consume, e.g. `ArchiveService.archive(content: Buffer, filename: string, timestamp: Date): Promise<ArchiveResult>`; `none` if nothing downstream depends on it]
**Consumes:** [exact symbol/signature from an earlier task this task depends on, e.g. `SftpClient` from Task 2; `none` if independent]

**Create:**
- `full/path/to/NewFile.ts`
- `full/path/to/NewFile.spec.ts`

**Modify:**
- `full/path/to/ExistingFile.ts`

**Description:**
[2-3 sentences: what to do and why it connects to previous/next task]

**Requirements:**
- Implement method `methodName(param: Type): ReturnType`
- Use pattern from `path/to/Reference.ts`
- Handle errors with [specific exception type]
- Log at [level] using [logger pattern]
- [other specific requirements]

**Tests:**
- Test success case: [description]
- Test failure case: [description]
- Test edge case: [description]

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example:**
```[language]
// Show key code snippet, signature, or config
```
```

**Status values:**
- `pending` - task not yet started
- `in-progress` - task started in a session; encountering it at session start means a previous session was interrupted mid-task
- `completed` - task finished and verified

The agent sets `pending` → `in-progress` when it STARTS a task, and `in-progress` → `completed` only after implementation and verification. A tasks doc fresh from generate-tasks contains only `pending`.

---

### `orchestrated` structure

The main `tasks-{slug}.md` file is an index for the orchestrator, not the full implementation prompt. It must point to every phase file.

```markdown
# Tasks: [Feature Name]

## Status
pending

## Source
- Planning doc: `./absolutpowers/feature/planning-{slug}.md`  <!-- for epic phases: ./absolutpowers/feature/{epic-slug}/planning-phase-N-{subslug}.md -->
- Epic context (if applicable): `./absolutpowers/feature/{epic-slug}/planning-main.md`

## Mode
orchestrated

## Project Context
**Stack:** [languages, frameworks, key libraries]
**Global Constraints:** [spec-derived requirements binding every phase/task in this plan — copied verbatim from the planning doc; cite binding `constitution.md` articles as `Per Artykuł N`, never copy article text. Distinct from `constitution.md` (project pryncypia) and `rules.md` (lint) — see the single-file `## Project Context` template above for the full demarcation note.]
**Verification commands:** [canonical commands]
**Shared implementation context:** `./absolutpowers/feature/tasks-{slug}/implementation-context.md`

## Phase Overview

### Phase 1: [Action-Oriented Title]
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/01-{phase-slug}.md`
**Depends on:** none
**Write scope:** `path/glob`, `path/File.ext`
**Risk:** low | medium | high

### Phase 2: [Action-Oriented Title]
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/02-{phase-slug}.md`
**Depends on:** Phase 1
**Write scope:** `path/glob`, `path/File.ext`
**Risk:** low | medium | high

## Final Verification
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file (`pending` → `in-progress` when a phase starts, → `completed` after phase verification and review).
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
```

Each phase file must follow this structure:

```markdown
# Phase N: [Action-Oriented Title]

## Status
pending

## Parent
`./absolutpowers/feature/tasks-{slug}.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-{slug}/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- [concrete item: file path, symbol, or `implementation-context.md` section that must exist before this phase starts]
- [for Phase 1: "None (first phase)."]

### Provides (for later phases)
- [concrete item this phase commits to producing]
- [e.g., "Service `OrderService` at `src/services/OrderService.ts` with method `create(dto): Order`"]

## Read Scope
- `path/to/reference/File.ext`

## Write Scope
- `path/to/change/File.ext`
- `path/to/change/**/*Test.ext`

## Objective
[2-4 concrete sentences describing what this phase must produce.]

## Tasks

### Task 1: [Action]
**Status:** pending
**Traces to:** AC-N, AC-M
**Test-first:** yes | no ([short reason when no])
**Produces:** [exact symbol/signature this task exports; `none` if nothing downstream depends on it]
**Consumes:** [exact symbol/signature from an earlier task in THIS phase; `none` if independent]

**Requirements:**
- [specific requirement]

**Tests:**
- [specific test]

## Phase Verification
Run:
- `[focused command for this phase]`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- [to be completed after phase completion]
```

Each Requires item must reference a concrete file, symbol, or `implementation-context.md` section — not vague descriptions. Each Provides item must be verifiable: a file path, a symbol name, or a specific section in `implementation-context.md`.

**Produces/Consumes ↔ Context Contract aggregation rule:** task-level `**Produces:**`/`**Consumes:**` and phase-level `Context Contract → Provides` are two levels of one mechanism, not a duplication. Phase `Provides` = the union of task `Produces` entries that cross the phase boundary (a later phase needs them) — nothing else. Do NOT repeat within-phase: when a `Produces` signature is consumed by another task inside the SAME phase, it stays in that task's `Consumes` field only and is never promoted to phase `Provides`. In `single-file` mode there are no phases: `Produces`/`Consumes` work task↔task with no rollup — do not look for a phase `Provides` section in single-file output. `Produces`/`Consumes` signatures are a separate field from the `AC-N` tokens embedded in test names (see AC Traceability above) — the two do not collide and both apply independently to the same task.

Create `implementation-context.md` with this structure:

```markdown
# Implementation Context: [Feature Name]

## Purpose
Short handoff for phase workers. Keep this file concise. Add only facts that future phases need.
HARD BUDGET: max 10 lines per phase entry across all sections combined; whole file target ≤150 lines.
Every later worker reads this file — its size is paid on every phase.

## Completed Phases
- None yet.

## Created / Changed API
- None yet.

## Decisions Made
- None yet.

## Test Utilities / Fixtures
- None yet.

## Constraints For Next Phases
- None yet.

## Verification History
- None yet.
```

Rules for `implementation-context.md`:
- It is a handoff contract, not a work log.
- Include only facts that later phases need.
- Do not paste full diffs, temporary debugging hypotheses, or obvious restatements of the phase file.
- Keep entries short and link concrete files, symbols, commands, or decisions.

**Size limits:**
- Maximum ~50 lines of content (excluding section headers and `## Purpose`).
- Each entry: max 2 lines. Longer entries belong in the phase file, not here.
- When a phase completes and its entries are not needed by remaining phases, compress to one-liners or remove.

**Staleness:**
- Before adding a new entry, check if existing entries became irrelevant given completed phases. Remove or compress stale ones.
- `## Completed Phases` entries are exempt — they serve as audit trail.

The final verification phase file `99-final-verification.md` must contain the same concrete project commands required by the main tasks file. It is completed by the implement orchestrator after all implementation phases pass.

## Task Guidelines

**Approach — Test-first marker:**
- Every implementation task gets a `**Test-first:**` field decided HERE, at generation time — the planner owns this decision, not the implementer mid-implementation.
- `Test-first: yes` for: business logic, data transformations, validation, pure functions, bug-fix regression tasks.
- `Test-first: no ([reason])` for: configuration, simple CRUD wiring, UI scaffolding, docs — the reason is mandatory, one short phrase.
- `implement` follows the marker; deviating requires a recorded justification in the task's remarks and is reviewable. The marker set here is the contract.

**Granularity:**
- One logical unit of work per task
- Tasks are sequential - each builds on previous
- Agent should verify completion and update status before proceeding
- Maximum 5 requirements per task. If a task accumulates more, split into two sequential tasks with clear scope boundaries.
- The final task should verify the integrated change across the whole project

**Specificity:**
- Exact file paths (create vs modify)
- Exact method signatures with types
- Exact exception/error types to use
- Reference files for patterns: "follow pattern in X"
- `**Example:**` shows real code, a concrete signature, or an actual configuration snippet — never a sketch, ellipsis, or placeholder (see `## No Placeholders` below); the signature shown must be consistent with the task's own `**Produces:**`/`**Consumes:**` fields. Note: code in the plan is unverified — the planner does not run it — it is a signature contract for the implementer, not a pre-tested implementation.

**What to include:**
- Status field (pending/completed)
- File paths (always full paths)
- Method signatures with types
- References to existing code patterns
- Required tests with descriptions
- Test-first marker (`yes` / `no` with reason) on every implementation task
- Code examples for non-obvious implementations — real code or signatures, per Specificity above
- Configuration changes
- A final verification task as the LAST task, with concrete project commands

**What to omit:**
- Time estimates
- Priority levels
- Business justifications
- Detailed onboarding explanations
- Rollback procedures

## No Placeholders

A task that contains any of the following patterns has failed the plan, regardless of how complete the rest of it looks:

- `...`, `// TODO`, or `// rest of implementation` (or any other elision) inside an `**Example:**` block
- "write tests for the above" instead of naming the actual tests
- "handle errors properly" instead of naming the concrete exception/error type
- "add appropriate validation" instead of naming the concrete validation rule
- a requirement with no signature or type (e.g. "update the service" instead of `update(id: string, dto: UpdateDto): Promise<Entity>`)
- "similar to X" with no concrete detail of what changes relative to X

Any of these in a generated task is a plan failure — fix it before writing the tasks doc; do not leave it for the implementer to resolve. This is a stricter, task-local check and does not replace grep-AC traceability (see `### AC Traceability` above): a task can be placeholder-free and still be missing an `AC-N` token in a test name — check both independently.

## Final Verification Task

Always add a final task at the end of the plan that verifies the integrated change across the project.

This final task should use concrete commands discovered in the project, for example:
- backend compilation or build
- backend tests relevant to the change
- frontend production build
- frontend typecheck
- lint
- formatter check such as `spotlessCheck` when used by the project

Prefer the project's canonical commands, wrappers, or documented scripts. Do not invent generic commands if the repo already exposes the right ones.

Suggested template:

```markdown
### Task [N]: Final Verification
**Status:** pending

**Create:**
- None

**Modify:**
- None

**Description:**
Run the project's final verification commands against the fully integrated change. This confirms that backend and frontend artifacts still build correctly and that project quality gates pass before review or merge.

**Requirements:**
- Run backend build/test command: `[exact command from project]`
- Run frontend build/typecheck command: `[exact command from project]`
- Run lint or formatter check command: `[exact command from project]`
- If the project uses formatter gates such as `spotlessCheck`, run them here instead of inventing a generic formatting command
- If the planning doc contains `## Acceptance Criteria`: for every `AC-N` traced by any task, grep the project's test sources for the literal token `AC-N` (scoped to the test locations from the project context section) — every traced AC must appear in at least one test name/annotation; a missing token means this verification fails
- Record any command that is intentionally skipped as `not applicable` with a short reason
- Do not mark this task as completed if any required verification command fails

**Tests:**
- Backend build/test exits with code 0
- Frontend build/typecheck exits with code 0
- Lint / formatter check exits with code 0
- Every traced `AC-N` token found in test sources (grep hit per token; skip when the planning doc has no AC section)

**Implementation decisions / remarks:**
- Commands executed: [fill after completion]
- Results: [fill after completion]
- Skipped checks: [fill after completion or `none`]

**Example:**
```bash
./mvnw test spotless:check
npm run build
npm run typecheck
```
```
