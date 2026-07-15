# Phase 5: Add AC Awareness to Implement

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 3 completed: `**Traces to:** AC-N` field exists in task templates
- Phase 1 completed: AC format defined (`AC-N:` numbering, behavioral)

### Provides (for later phases)
- Updated `claude/skills/implement/SKILL.md` with AC reading on startup and AC fulfillment status reporting at completion
- Updated `codex/skills/implement/SKILL.md` with same changes (minus agent-specific content)
- Implement output format includes AC Fulfillment section that Phase 6 (review-implementation) will verify

## Read Scope
- `claude/skills/implement/SKILL.md` — current Claude implement to modify
- `codex/skills/implement/SKILL.md` — current Codex implement to modify
- `./absolutpowers/feature/planning-qa-enrichment.md` — AC format reference

## Write Scope
- `claude/skills/implement/SKILL.md`
- `codex/skills/implement/SKILL.md`

## Objective
Make implement AC-aware: read AC from the source planning doc at startup, and report AC fulfillment status after all tasks complete (before review-implementation gate on Claude, before completion summary on Codex).

## Tasks

### Task 1: Add AC Awareness to Implement (Claude)
**Status:** completed

**Modify:**
- `claude/skills/implement/SKILL.md`

**Requirements:**
- In "Context Files" section (after line 28), add instruction to read `## Acceptance Criteria` from the source planning doc referenced in the tasks file's `**Source doc:**` field. Extract all `AC-N:` items. If no AC section exists, note that AC traceability is not available for this tasks file and proceed normally.
- After Step 7 (Continue or Stop) and before Step 8 (Review Gate), add new step "Step 7B: AC Fulfillment Report":
  - For each `AC-N` from the planning doc, determine fulfillment status:
    - `FULFILLED` — task(s) tracing to this AC are completed and tests pass
    - `NOT VERIFIED` — no task traces to this AC, or tracing task has no tests for it
    - `PARTIAL` — task traces to this AC but implementation is incomplete
  - Print AC fulfillment summary in output
  - This step is informational — it does not block proceeding to review gate
  - Skip entirely if no AC were found in planning doc
- Add AC Fulfillment section to the completion output format (around line 418):
```
AC Fulfillment:
- AC-1: FULFILLED
- AC-2: FULFILLED
- AC-3: NOT VERIFIED — no test found
```
- In orchestrated mode: AC fulfillment report runs once after all phases complete and final verification passes, before the `review-implementation` gate (Step O6)

### Task 2: Add AC Awareness to Implement (Codex)
**Status:** completed

**Modify:**
- `codex/skills/implement/SKILL.md`

**Requirements:**
- Apply same AC reading and fulfillment reporting changes as Task 1
- No agent-specific content (no `Agent()` calls, no `subagent_type` references, no review-implementation gate)
- AC fulfillment report is the last step before completion summary
- Codex orchestrated mode: AC fulfillment report runs once after all phases and final verification

## Phase Verification
Run:
- Verify `claude/skills/implement/SKILL.md` contains "Acceptance Criteria" reading instruction
- Verify `claude/skills/implement/SKILL.md` contains "AC Fulfillment" in output format
- Verify `codex/skills/implement/SKILL.md` contains "Acceptance Criteria" reading instruction
- Verify `codex/skills/implement/SKILL.md` contains "AC Fulfillment" in output format
- Run `./scripts/diff-skills.sh` to check expected drift

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- AC reading instruction placed as a subsection `### Acceptance Criteria` inside the `## Context Files` section (after existing memory instructions) — consistent with "read before starting" intent.
- Step 7B inserted between Step 7 and Step 8 in Claude; between Step 7 and the Rules/Output section in Codex (Codex has no Step 8 review gate).
- Claude Step 7B explicitly notes orchestrated mode behavior (runs after all phases + final verification, before Step O6). Codex Step 7B notes orchestrated mode as "before completion summary" with no agent gate reference.
- AC Fulfillment output format added to Output Format section in both files as a conditional block ("if ACs were found").
- `diff-skills.sh` reports `implement (differs)` — expected by design: Claude has `allowed-tools`, `argument-hint`, agent review gate (Step 8, Step O6 references), Codex has none.
- Graceful fallback preserved in both versions: if no `## Acceptance Criteria` section, step is skipped entirely.
