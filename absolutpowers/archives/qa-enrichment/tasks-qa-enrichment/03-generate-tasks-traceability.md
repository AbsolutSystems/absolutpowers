# Phase 3: Add AC Traceability to Generate-Tasks

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1 completed: AC format defined (three categories, `AC-N:` numbering, behavioral)

### Provides (for later phases)
- Updated `claude/skills/generate-tasks/SKILL.md` with AC reading instructions, `**Traces to:** AC-N` field in task template, traceability guidance
- Updated `codex/skills/generate-tasks/SKILL.md` with same changes (minus agent-specific content)
- Task template includes `**Traces to:**` field that Phase 4 (review-tasks) and Phase 5 (implement) will reference

## Read Scope
- `claude/skills/generate-tasks/SKILL.md` — current Claude generate-tasks to modify
- `codex/skills/generate-tasks/SKILL.md` — current Codex generate-tasks to modify
- `./absolutpowers/feature/planning-qa-enrichment.md` — AC format and traceability examples

## Write Scope
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

## Objective
Make generate-tasks AC-aware: read AC from planning doc, map each AC to tasks, add `Traces to: AC-N` field to task template. Ensure graceful fallback when planning doc has no AC section.

## Tasks

### Task 1: Add AC Reading to Generate-Tasks (Claude)
**Status:** completed

**Modify:**
- `claude/skills/generate-tasks/SKILL.md`

**Requirements:**
- In Step 1 (Read Input Document and Context, line 73), add instruction to read `## Acceptance Criteria` section from the planning doc if present
- Add new subsection `### AC Traceability` after the Analysis Requirements section (after line 123) with these rules:
  - If planning doc contains `## Acceptance Criteria`, extract all `AC-N:` items
  - Every AC must be covered by at least one task via `**Traces to:** AC-1, AC-3` field
  - Tasks may trace to multiple AC; one AC may be traced by multiple tasks
  - Infrastructural tasks (scaffolding, config) may have `**Traces to:** none` with reason
  - Final verification task traces to all AC collectively
  - If planning doc has no `## Acceptance Criteria` section, skip traceability — do not error, do not invent AC
- Add `**Traces to:** AC-N, AC-M` field to the single-file task template (after `**Status:** pending`, before `**Create:**`, around line 175)
- Add `**Traces to:**` field to the orchestrated phase task template (inside `### Task 1: [Action]` block, around line 295)
- In the example task (line 452, "Good" example), add `**Traces to:** AC-2, AC-5` to show the pattern

### Task 2: Add AC Reading to Generate-Tasks (Codex)
**Status:** completed

**Modify:**
- `codex/skills/generate-tasks/SKILL.md`

**Requirements:**
- Apply same changes as Task 1 to Codex version
- No agent-specific content (no `Agent()` calls, no `subagent_type` references)
- Same AC traceability rules, same `**Traces to:**` field in templates, same graceful fallback

## Phase Verification
Run:
- Verify `claude/skills/generate-tasks/SKILL.md` contains "AC Traceability" section
- Verify `claude/skills/generate-tasks/SKILL.md` task template contains `**Traces to:**`
- Verify `codex/skills/generate-tasks/SKILL.md` contains "AC Traceability" section
- Verify `codex/skills/generate-tasks/SKILL.md` task template contains `**Traces to:**`
- Run `./scripts/diff-skills.sh` to check expected drift (Claude has agent gates, Codex does not)

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Added `## Acceptance Criteria section` reading instruction to Step 1 in both Claude and Codex generate-tasks files.
- Added `### AC Traceability` section after `## Analysis Requirements` in both files; section is self-contained and explains graceful fallback when no AC section exists.
- Added `**Traces to:** AC-N, AC-M` field to the single-file task template (after `**Status:** pending`) in both files.
- Added `**Traces to:** AC-N, AC-M` field to the orchestrated phase task template (inside `### Task 1: [Action]` block) in both files.
- Added `**Traces to:** AC-2, AC-5` to the "Good" example task in both files.
- Codex version has no agent-specific content (no `Agent()` calls) — same traceability logic, same field, same fallback rule.
- `diff-skills.sh` output: `generate-tasks (differs)` — expected due to Claude-specific `allowed-tools`, `argument-hint`, Review Gate section, and orchestrator wording differences that pre-existed this phase.
