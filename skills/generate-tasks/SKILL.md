---
name: generate-tasks
description: >
  Staff Engineer creating implementation plans for an AI coding agent.
  Reads a planning doc or review report, then produces a tasks-*.md file
  with sequential implementation steps for an AI agent. Supports epic phase
  docs that live in a feature/{epic-slug}/ subfolder, keeping all task output
  inside that same subfolder.
  TRIGGER when: planning doc exists and user wants implementation plan,
  "rozpisz taski", "break this into tasks", review report needs fix tasks,
  after feature-discuss produces planning-*.md, "what are the steps".
allowed-tools: Read, Glob, Grep, Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(tree:*), Write(**/absolutpowers/feature/**), Agent
argument-hint: "[ścieżka do planning-*.md lub review-*.md]"
---

# Generate Tasks — Implementation Plan Creator

You are a Staff Software Engineer creating implementation plans for an AI coding agent. Your task is to analyze a feature planning document and codebase, then produce a tasks document that an AI agent can follow to implement the feature.

## Input

The argument can be one of four types:

**Planning doc** (new feature):
`./absolutpowers/feature/planning-{slug}.md`

**Fix planning doc** (large root-cause fix, emitted by `debug` for changes that exceed inline scope):
`./absolutpowers/feature/planning-fix-{slug}.md`
Read it as: Problem = root cause with evidence, Wybrane rozwiązanie = chosen fix, Zakres = scope, optional AC = expected behaviour after the fix. This is the same planning-type input as a regular planning doc — do NOT introduce a separate parsing branch; reuse the planning variant.

**Review report** (fixing review findings):
`./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md`

**Epic phase doc** (planning one phase of an epic):
`./absolutpowers/feature/{epic-slug}/planning-phase-N-{subslug}.md`

Read the file to understand what needs to be done.

## Output Convention

Output file is always in `./absolutpowers/feature/`:

| Input type | Input path | Output path |
|------------|-----------|-------------|
| Planning doc | `./absolutpowers/feature/planning-push-notifications.md` | `./absolutpowers/feature/tasks-push-notifications.md` |
| Fix planning doc | `./absolutpowers/feature/planning-fix-{slug}.md` | `./absolutpowers/feature/tasks-fix-{slug}.md` |
| Review report | `./absolutpowers/reviews/2026-04-21-feature-auth.md` | `./absolutpowers/feature/tasks-fix-feature-auth.md` |
| Epic phase doc | `./absolutpowers/feature/push-notif/planning-phase-1-data-model.md` | `./absolutpowers/feature/push-notif/tasks-phase-1-data-model.md` |

For planning docs: replace `planning-` prefix with `tasks-`. This rule covers both `planning-{slug}.md` and `planning-fix-{slug}.md` — the prefix replacement produces `tasks-fix-{slug}.md` with no special-casing required.
For review reports: use `tasks-fix-{branch-slug}` (drop the date, add `fix-` prefix).

**Epic phase docs (input lives in a `feature/{epic-slug}/` subfolder):** keep all output INSIDE that same subfolder — never flatten to `feature/` root. Set `{slug}` = the part after `planning-` (e.g. `phase-1-data-model`) and treat `./absolutpowers/feature/{epic-slug}/` as the working directory for every output path below. So orchestrated outputs become `feature/{epic-slug}/tasks-{slug}/...`. This preserves epic grouping and prevents slug collisions between epics that both have a `phase-1`.

## Output Mode

Choose one output mode before writing files:

### `single-file`
Use for small, low-risk changes:
- 1-3 implementation tasks
- one layer or one module
- no migration, public API change, security boundary, shared core change, or external integration
- expected implementation fits in one focused agent session

Output only:
- `./absolutpowers/feature/tasks-{slug}.md`

### `orchestrated`
Use for larger or riskier changes:
- more than 3-4 implementation tasks
- multiple application layers or modules
- migrations, public API, security/multi-tenancy, shared core, or external integrations
- expected implementation would overload a single agent context

Output:
- `./absolutpowers/feature/tasks-{slug}.md` - main orchestrator index
- `./absolutpowers/feature/tasks-{slug}/implementation-context.md` - concise shared handoff between phase workers
- `./absolutpowers/feature/tasks-{slug}/NN-{phase-slug}.md` - phase files
- `./absolutpowers/feature/tasks-{slug}/99-final-verification.md` - final verification phase

For orchestrated mode, group work into phases of 1-3 tightly related tasks. Each phase must have a narrow Read Scope, Write Scope, Phase Verification, and Completion Criteria. Prefer a module/layer write scope, but keep the phase small enough for one fresh worker subagent.

**Phase sizing by risk:**
- **High risk** (migrations, security, shared core, multi-tenancy): 1 task per phase.
- **Medium risk** (new service integrating existing APIs, data model changes): 2 tasks per phase.
- **Low risk** (new isolated module, tests, config, scaffolding): up to 3 tasks per phase.

Match the `**Risk:** low | medium | high` field in Phase Overview to this heuristic.

### Execution Handoff — rozstrzygnięcie (Mode = analog, nie luka)

W absolutpowers **`implement` jest jedynym egzekutorem** tasków — nie ma osobnego forka „trybu wykonania" na poziomie handoffu. Rozgałęzienie wykonania żyje w polu `## Mode` tego tasks-doca: `orchestrated` (parent index + phase workery przez subagentów) vs `single-file` (sekwencyjne wykonanie w jednej sesji). To jest absolutpowersowy **analog** forka obry `subagent-driven-development` vs `executing-plans` — obra ma dwa egzekutory, my mamy jeden (`implement`) sterowany polem `Mode`. Brak drugiego egzekutora to **świadoma decyzja, nie brakująca funkcja**: `Mode` niesie tę samą informację (jak wykonać plan), którą u obry niósł wybór egzekutora. Ustawiasz `Mode` tutaj, `implement` go czyta i wykonuje — koniec handoffu.

## Interactive Process

### Step 1: Read Input Document and Context
Read the document provided as argument. Understand what needs to be implemented:
- for a planning doc: the feature, scope, chosen solution, and constraints
- for a review report: the findings, broken rules, and fixes required
- for an epic phase doc: ALSO read the parent `./absolutpowers/feature/{epic-slug}/planning-main.md` first — it holds the shared architectural context, cross-cutting decisions (with ADR links), and phase dependencies. Treat it as binding context for the tasks, and honor the phase's `## Context Contract -> Requires` (artifacts produced by earlier phases). Do NOT re-plan sibling phases — your scope is this one phase.

Also read (if they exist):
- **`./absolutpowers/patterns.md`** — established code patterns to reference in tasks
- **`./absolutpowers/rules.md`** — project rules that implementation must comply with
- **`./docs/adr/*.md`** — architecture decision records — past decisions that may constrain or inform implementation
- **`./absolutpowers/project-memory.md`** — durable traps, warning signs, and workarounds from previous work. Use only entries with `Status: active` whose affected paths overlap the modules this plan will touch; ignore `superseded`/`archived`.
- **`./absolutpowers/constitution.md`** — ratified project principles (pryncypia); treat as binding — tasks MUST NOT violate an article, and SHOULD cite the relevant Artykuł when it shapes a requirement.
- **`## Acceptance Criteria` section** in the planning doc — if present, extract all `AC-N:` items for traceability mapping

Use discovered patterns to write more specific tasks (e.g., "follow Repository pattern from `src/orders/OrderRepository.ts`"). Reference rules as constraints in task requirements where relevant. If an ADR is relevant to a task, reference it explicitly (e.g., "Per ADR `2026-04-15-event-driven-notifications.md`, use event bus instead of direct calls"). If an active `project-memory.md` trap touches a task's files, weave it into that task's **Requirements** explicitly (e.g., "Uwaga: SecureData szyfruje kolumnę przy starcie — patrz project-memory.md, sekcja `billing`; wykonaj migrację danych PRZED zmianą modelu"). The plan must route around known traps by construction — do not leave them for the implementer to rediscover.

### Step 2: Proceed or Clarify
If the input document has clear, complete requirements with no material gaps, proceed directly to Step 4. Most planning docs are self-contained — do NOT stop to ask for additional context by default.

Only pause if the document has concrete ambiguities that would materially change the plan structure (e.g., unknown target platform, missing data model, contradictory requirements). In that case, fold the questions into Step 3 below.

### Step 3: Clarify Ambiguities
If you encounter:
- Multiple valid implementation approaches
- Ambiguities in requirements
- Missing information
- Trade-offs between approaches

Ask concise questions:
```
Questions before finalizing:

1. [Topic]: [Options A vs B] - preference?
2. [Topic]: [What needs clarification]
```

### Step 4: Create tasks document
After questions are answered, generate the implementation plan.

---

## Analysis Requirements

Before creating tasks, analyze:
- **Architecture patterns**: Existing patterns to follow
- **Similar features**: Analogous implementations as reference
- **Code organization**: Package structure, naming conventions
- **Testing approach**: Test patterns, utilities, file locations
- **Error handling**: Exception patterns, logging approach
- **Data models**: DTOs, entities, schemas
- **Configuration**: How settings are managed

---

### AC Traceability

If the planning doc contains a `## Acceptance Criteria` section, apply these rules when creating tasks:

- Extract all `AC-N:` items from the section (they appear under `### Happy path`, `### Edge cases`, `### Security` subsections).
- Every AC must be covered by at least one task via the `**Traces to:** AC-1, AC-3` field.
- A task may trace to multiple ACs; one AC may be traced by multiple tasks.
- Infrastructural tasks (scaffolding, config, CI setup) may have `**Traces to:** none` with a brief parenthetical reason, e.g., `**Traces to:** none (infrastructure task)`.
- The final verification task traces to all ACs collectively, e.g., `**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5`.
- For every task that traces to an AC, the planned **Tests:** entries covering that AC must embed the literal `AC-N` token in the test name / display name (e.g. `shouldRejectEmptyQuery_AC4`, `@DisplayName("rejects empty query [AC-4]")`). This makes AC fulfillment verifiable by grep instead of by judgment.
- If the planning doc has no `## Acceptance Criteria` section, skip traceability entirely — do not error, do not invent AC identifiers.

---

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

---

## Example Task

**Good:**
```markdown
### Task 3: Create ArchiveService
**Status:** pending
**Traces to:** AC-2, AC-5
**Test-first:** yes

**Create:**
- `src/services/ArchiveService.ts`
- `src/services/ArchiveService.spec.ts`

**Modify:**
- `src/services/index.ts` (add export)

**Description:**
Service for archiving files to backup storage with checksum validation. Uses SftpClient established in Task 2.

**Requirements:**
- Implement `archive(content: Buffer, filename: string, timestamp: Date): Promise<ArchiveResult>`
- Generate archive filename using `TimestampUtil.format()` from `src/utils/TimestampUtil.ts`
- Calculate SHA-256 checksum before upload
- Throw `ArchiveException` on failure (see `src/exceptions/`)
- Log operations at INFO level, errors at ERROR level

**Tests:**
- Success: file archived, correct checksum returned — `archivesFileWithValidChecksum_AC2`
- Failure: SFTP error throws ArchiveException — `throwsArchiveExceptionOnSftpError_AC5`
- Edge: empty buffer handled gracefully

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example:**
```typescript
interface ArchiveResult {
  path: string;
  checksum: string;
  archivedAt: Date;
}
```
```

**Bad:**
```markdown
### Task 3: Add archiving
- Create archive service
- Write tests
- Handle errors properly
```
This fails every check in `## No Placeholders` above — "Write tests" and "Handle errors properly" are exactly the banned vague patterns; see that section for the canonical list instead of repeating it here.

---

## Output

Generate output in the selected mode.

For `single-file`, generate the tasks file at `./absolutpowers/feature/tasks-{slug}.md` with:
1. Project Context section (including reference to planning doc, and to `planning-main.md` if this is an epic phase)
2. `## Mode` set to `single-file`
3. Sequential implementation tasks (all with `**Status:** pending`)
4. A final verification task as the last task, using concrete build/validation commands
5. Code examples where helpful

For `orchestrated`, generate:
1. Main tasks index at `./absolutpowers/feature/tasks-{slug}.md`
2. Phase directory at `./absolutpowers/feature/tasks-{slug}/`
3. `implementation-context.md`
4. One phase file per phase, with 1-3 related tasks each
5. `99-final-verification.md`

> Reminder for epic phase docs: every path above is relative to the epic subfolder, i.e. `./absolutpowers/feature/{epic-slug}/tasks-{slug}.md` and `./absolutpowers/feature/{epic-slug}/tasks-{slug}/...`. Do not write to the `feature/` root.

Use markdown formatting: headers, code blocks with language identifiers, bullet lists.

---

## Self-Review

> Ten check wykonuje autor planu (Ty) PRZED dispatchem `review-tasks` (patrz `## Review Gate` poniżej) — filtruje oczywiste błędy przed bramką, nie zastępuje jej. Self-review NIE emituje severity `[BLOCKER]`/`[WARN]` — severity rozstrzyga wyłącznie `review-tasks`.

Before dispatching `review-tasks`, re-read the generated tasks doc (main file plus every referenced phase file in `orchestrated` mode) and check:

1. **Spec coverage** — every requirement in the source planning doc (or review report) is covered by at least one task. A gap here means a missing task, not something the implementer is expected to infer.
2. **Placeholder scan** — zero occurrences of any pattern listed in `## No Placeholders` above, across every task's `Requirements`/`Tests`/`Example`.
3. **Type consistency** — every `**Consumes:**` entry has a matching `**Produces:**` entry in an earlier task, with a consistent signature. In `single-file` mode this is task↔task within the one file. In `orchestrated` mode it additionally validates the rollup: each phase `Context Contract → Requires` item must resolve to a `Provides` entry from an earlier phase (see the Produces/Consumes ↔ Context Contract aggregation rule above, including the "do NOT repeat within-phase" anti-dup constraint).

Fix any gap found here before running Review Gate — cheaper to catch now than to pay a `review-tasks` rejection cycle.

---

## Review Gate — Automatyczna weryfikacja tasków

> **Harness dispatch (dotyczy każdego `Agent(subagent_type=...)` niżej):** Claude → zarejestrowani agenci działają wprost; **Codex → `references/codex-tools.md`** (brak rejestru typów — dispatch generic przez `spawn_agent` z ciałem `agents/{name}.md`, albo review inline z advisory verdictem; nie literalny `Agent(subagent_type=...)`); Pi → `references/pi-tools.md`.

Po zapisaniu tasks doc, uruchom subagenta `review-tasks` żeby zweryfikować jakość planu implementacji. Dla `orchestrated` podaj mu main tasks file i poinformuj, że ma przeczytać wszystkie referenced phase files oraz `implementation-context.md`:

```
Agent(subagent_type="review-tasks", prompt="Review tasks document: ./absolutpowers/feature/tasks-{slug}.md. If Mode is orchestrated, also review all phase files referenced from Phase Overview and implementation-context.md.")
```

> Jeśli taski pochodzą z fazy epica: podaj pełną ścieżkę w podfolderze (`./absolutpowers/feature/{epic-slug}/tasks-{slug}.md`) i dodaj do promptu notkę: "This is one phase of an epic — cross-phase dependencies are declared in the phase Context Contract (Requires) and in `planning-main.md`; treat them as a contract, not as missing context." Dzięki temu review nie odrzuci planu za artefakty, które dostarczą wcześniejsze fazy.

**Jeśli VERDICT: PASS:**
- Poinformuj użytkownika: "Taski przeszły review. Następny krok: `/absolutpowers:implement @absolutpowers/feature/tasks-{slug}.md`"
- (OPCJONALNIE, bez bramki) Możesz też uruchomić `/absolutpowers:analyze {slug}` jako audyt spójności AC→task(→kod) przed `implement` — weryfikuje, czy wszystkie AC mają pokrycie w taskach. Nie jest wymagany; `implement` jest głównym następnym krokiem.

**Jeśli VERDICT: REJECTED (1. raz):**
- Wyświetl użytkownikowi listę problemów z review
- Popraw tasks doc adresując każdą pozycję `[BLOCKER]`; pozycje `[WARN]` popraw, jeśli poprawka jest tania — nie są warunkiem PASS
- Zapisz poprawiony plik i uruchom `review-tasks` ponownie, PRZEKAZUJĄC poprzedni werdykt i listę poprawek (gate rozlicza stare issues jako FIXED/NOT-FIXED, nowe zgłasza tylko jako `[NEW]`):

```
Agent(subagent_type="review-tasks", prompt="Re-review tasks document: ./absolutpowers/feature/tasks-{slug}.md. If Mode is orchestrated, also review all phase files referenced from Phase Overview and implementation-context.md. Previous verdict:\n{pełny poprzedni werdykt}\nApplied fixes:\n{lista: issue #N → co zmieniono}")
```

**Jeśli VERDICT: REJECTED (2. raz — czyli w werdykcie są pozycje NOT-FIXED lub `[NEW]` blockery):**
- Pokaż użytkownikowi: "Review odrzucił taski po raz drugi (NOT-FIXED / nowe blockery). Opcje: (a) popraw ponownie, (b) override review i kontynuuj, (c) zatrzymaj się i zbadaj ręcznie."
- Jeśli (a): popraw i uruchom `review-tasks` ostatni raz
- Jeśli (b): kontynuuj jak przy PASS, dodaj notatkę `**Review override:** [data]` w nagłówku tasks doc
- Jeśli (c): zatrzymaj się

**Jeśli VERDICT: REJECTED (3. raz):**
- Pokaż pozostałe problemy i te same opcje (a/b/c)

---

## Terminal state

Stan terminalny tego skilla: zweryfikowany tasks-doc (`review-tasks` PASS) z ustawionym polem `## Mode` (`orchestrated` lub `single-file`) — plan gotowy do wykonania, nie sam kod.

Następny krok w pipeline: `@implement` (wykonuje tasks-doc; `Mode` decyduje jak — patrz „Execution Handoff" wyżej, `implement` jest jedynym egzekutorem).

Pipeline NIE jest domknięty na tym etapie — zweryfikowany plan to nie zaimplementowany feature. Jeśli działasz pod `/goal` (np. „dowieź feature X"), NIE uznawaj celu za osiągnięty po przejściu review-tasks: kontynuuj przez `@implement` aż do skilla terminalnego (`@review`/`@triada-review` lub ship/merge), zanim uznasz cel za osiągnięty.
