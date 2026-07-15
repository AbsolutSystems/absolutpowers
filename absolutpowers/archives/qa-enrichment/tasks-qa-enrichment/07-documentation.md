# Phase 7: Update Documentation

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1 completed: `qa-enrichment` agent exists, feature-discuss updated on both platforms
- Phase 2 completed: review-plan has AC_QUALITY criterion
- Phase 3 completed: generate-tasks has AC traceability
- Phase 4 completed: review-tasks has AC_COVERAGE criterion
- Phase 5 completed: implement has AC fulfillment reporting
- Phase 6 completed: review-implementation has AC_FULFILLMENT criterion

### Provides (for later phases)
- Updated `README.md` with QA enrichment in pipeline description, feature-discuss skill reference, and agents table
- Updated `docs/getting-started.md` with AC workflow example
- Updated `docs/review-gates.md` with qa-enrichment description, AC_QUALITY in review-plan, AC_COVERAGE in review-tasks, AC_FULFILLMENT in review-implementation
- Updated `docs/contributing.md` with qa-enrichment agent in cross-file update rules

## Read Scope
- `README.md` — current readme to modify
- `docs/getting-started.md` — current getting-started to modify
- `docs/review-gates.md` — current review-gates to modify
- `docs/contributing.md` — current contributing to modify
- `claude/agents/qa-enrichment.md` — to accurately describe the agent
- `claude/agents/review-plan.md` — to accurately describe AC_QUALITY criterion
- `claude/agents/review-tasks.md` — to accurately describe AC_COVERAGE criterion
- `claude/agents/review-implementation.md` — to accurately describe AC_FULFILLMENT criterion

## Write Scope
- `README.md`
- `docs/getting-started.md`
- `docs/review-gates.md`
- `docs/contributing.md`

## Objective
Update all user-facing documentation to reflect the QA enrichment feature: new agent, new AC section in planning docs, AC traceability through the pipeline, new review criteria.

## Tasks

### Task 1: Update README.md
**Status:** completed

**Modify:**
- `README.md`

**Requirements:**
- In "The Pipeline" section (around line 53), update the ASCII flow diagram to show qa-enrichment step inside feature-discuss:
```
feature-discuss (+ qa-enrichment) → generate-tasks → implement → review
```
- In `/absolutpowers:feature-discuss` section (around line 88), add bullet: "Runs QA enrichment to generate behavioral Acceptance Criteria (AC-1, AC-2, ...)"
- In `/absolutpowers:generate-tasks` section (around line 116), add bullet: "Maps Acceptance Criteria from planning doc to tasks with `Traces to: AC-N` traceability"
- In Agents table (around line 309), add row: `qa-enrichment | feature-discuss | Analyzes planning doc and codebase, generates behavioral Acceptance Criteria`
- In "Review agent criteria" section (around line 317):
  - Add to review-plan: "AC quality (behavioral, verifiable, complete coverage)"
  - Add to review-tasks: "AC coverage (every AC-N traced by at least one task)"
  - Add to review-implementation: "AC fulfillment (every AC-N has implementation and test)"
- In Platform Differences table (around line 430), no change needed (QA enrichment works on both platforms via agent/inline)

### Task 2: Update docs/getting-started.md
**Status:** completed

**Modify:**
- `docs/getting-started.md`

**Requirements:**
- In "Krok 2: Twój pierwszy feature" section, "Dyskusja" subsection (around line 96):
  - Add phase "3. QA Enrichment" to the numbered list: "QA enrichment analizuje plan i dopisuje Acceptance Criteria (AC-1, AC-2, ...)"
  - Renumber subsequent phases (review gate becomes phase 4)
- In "Generowanie tasków" subsection (around line 110):
  - Add note that each task now includes `Traces to: AC-N` linking back to planning doc AC
- In "Typowe pytania" section, add new Q&A:
  - Q: "Co jeśli planning doc nie ma Acceptance Criteria?"
  - A: "Pipeline działa normalnie — traceability AC jest opcjonalne. Starsze planning docs bez sekcji AC nie powodują błędów. Generate-tasks, review-tasks i implement gracefully pomijają AC checks."

### Task 3: Update docs/review-gates.md
**Status:** completed

**Modify:**
- `docs/review-gates.md`

**Requirements:**
- In "Przegląd" section (around line 7), update the ASCII flow to show qa-enrichment:
```
feature-discuss ──qa-enrichment──▶ planning doc (z AC) ──▶ review-plan ──▶ PASS / REJECTED
```
- In "review-plan" section (around line 47):
  - Add `### AC Quality` subsection with criteria: AC exists, behavioral, verifiable, no implementation details, complete coverage, no trivial AC
  - Add `AC_QUALITY` to the categories table for review-plan
- In "review-tasks" section (around line 79):
  - Add `### AC Coverage` subsection with criteria: every AC-N covered by at least one task's `Traces to:` field
  - Add `AC_COVERAGE` to the categories table for review-tasks
- In "review-implementation" section (around line 152):
  - Add `### AC Fulfillment` subsection with criteria: every AC-N has implementation + test, report FULFILLED/NOT VERIFIED/MISSING
  - Add `AC_FULFILLMENT` to the categories table for review-implementation
- In "Kategorie issues" table (around line 197):
  - Add `AC_QUALITY` to review-plan row
  - Add `AC_COVERAGE` to review-tasks row
  - Add `AC_FULFILLMENT` to review-implementation row
- Add new section "## qa-enrichment" before "## review-plan" section:
  - Not a gate (no PASS/REJECTED)
  - Enrichment agent spawned by feature-discuss after planning doc write
  - Reads planning doc + codebase (test patterns, CI config)
  - Appends `## Acceptance Criteria` with three categories
  - Claude: subagent. Codex: inline phase

### Task 4: Update docs/contributing.md
**Status:** completed

**Modify:**
- `docs/contributing.md`

**Requirements:**
- In "Zmiany w formacie tasków" section (around line 169), add `claude/agents/qa-enrichment.md` to the list of files to update together when changing task format
- In "Agenci orchestrated implementation" table (around line 148), add note that `qa-enrichment` is not an orchestrated implementation agent but a feature-discuss enrichment agent
- In the agent table, add row for `qa-enrichment`:
  - Rola: Dopisuje Acceptance Criteria do planning doc po zapisie przez feature-discuss

## Phase Verification
Run:
- Verify `README.md` contains "qa-enrichment" in agents table
- Verify `docs/getting-started.md` contains "Acceptance Criteria" in the workflow description
- Verify `docs/review-gates.md` contains "AC_QUALITY", "AC_COVERAGE", and "AC_FULFILLMENT"
- Verify `docs/contributing.md` contains "qa-enrichment"

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- `review-gates.md` gained a new `## qa-enrichment` section before `## review-plan`; each gate section now ends with an explicit **Kategorie:** line to make the category list locally discoverable without scrolling to the summary table.
- `contributing.md`: added a separate "Agenci feature-discuss" table so that `qa-enrichment` and `review-plan` are clearly separated from the orchestrated implementation agents (`implementation-worker`, `phase-review`). The note inline ("Uwaga: qa-enrichment nie jest agentem orchestrated implementation") guards against future contributors misclassifying it.
- `getting-started.md`: the QA Enrichment step was inserted as step 6 in the numbered list (Dyskusja fazy), renumbering the old step 6 "Review gate" to step 7. The `Traces to: AC-N` note was added to the generate-tasks subsection rather than creating a standalone section, which keeps the flow concise.
- All changes stay inside Write Scope. No agent or skill files were modified.
