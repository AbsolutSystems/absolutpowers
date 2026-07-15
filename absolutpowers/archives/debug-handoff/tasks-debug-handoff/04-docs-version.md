# Phase 4: docs + version consistency

## Status
completed

## Parent
`./absolutpowers/feature/tasks-debug-handoff.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-debug-handoff/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1: `generate-tasks` accepts `planning-fix-{slug}.md`. Confirm via grep.
- Phase 2: `debug` `## Handoff Input` + Phase 4 size branch + Phase 4.5 escalation exist. Confirm via grep.
- Phase 3: `problem-discuss` Faza 5 nudge points to `problem-{slug}.md`. Confirm via grep.

### Provides (for later phases)
- `README.md` and `CLAUDE.md` pipeline descriptions show both debug handoffs (input: `problem-{slug}.md` → debug; output: large fix → `planning-fix-{slug}.md` → generate-tasks).
- Both `plugin.json` manifests carry the same version (3.9.0).

## Read Scope
- `README.md` (pipeline / debug / problem-discuss sections)
- `CLAUDE.md` (Pipeline Architecture, "Intake / triage front door" diagram)
- `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`
- `absolutpowers/feature/planning-debug-handoff.md` (Zakres → In scope)

## Write Scope
- `README.md`
- `CLAUDE.md`
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

## Objective
Document the two new debug handoffs in `README.md` and `CLAUDE.md`, and confirm the version is consistent across both manifests. The debug-handoff change is part of the collective 3.9.0 release; versions are already 3.9.0 — verify, only edit if mismatched.

## Tasks

### Task 1: Update pipeline docs in CLAUDE.md and README.md
**Status:** completed
**Traces to:** none (documentation task)

**Requirements:**
- In `CLAUDE.md` "Pipeline Architecture" (the `problem-discuss` front-door diagram and/or a short debug note): show debug's input handoff (reads `problem-{slug}.md` when routed from problem-discuss) and output handoff (large root-cause fix → `planning-fix-{slug}.md` → `generate-tasks`; small fix stays inline). Keep the existing `debug` "vs problem-discuss" framing intact.
- In `README.md`: mirror the same two handoffs wherever the pipeline/debug flow is described (the `feature-discuss → generate-tasks → implement → review` area and any debug/problem-discuss mention). Add the `planning-fix-{slug}.md` artefact to any artefact list.
- Keep wording consistent with the skill files written in Phases 1–3 (same artefact names/paths).
- Do not over-document — a few precise lines, not a rewrite.

**Tests:**
- `grep -n "planning-fix-" README.md CLAUDE.md` returns matches.
- `grep -n "problem-{slug}.md\|problem-discuss" CLAUDE.md` shows the debug input handoff is described.

### Task 2: Verify version consistency across manifests
**Status:** completed
**Traces to:** none (release-hygiene task)

**Requirements:**
- Run `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json`. Both must be `3.9.0` and equal.
- If already equal at 3.9.0 (expected): no edit; record "already 3.9.0, no bump" in remarks.
- If mismatched or below 3.9.0: set both to `3.9.0`.

**Tests:**
- Both manifests report identical `"version": "3.9.0"`.

## Phase Verification
Run:
- `grep -n "planning-fix-" README.md CLAUDE.md`
- `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json`

## Completion Criteria
- Both tasks completed; changes within Write Scope.
- Docs reference both debug handoffs and the `planning-fix-{slug}.md` artefact.
- Manifests carry matching version 3.9.0.
- `implementation-context.md` updated.
- `## Context Contract -> Provides` fulfilled.

## Implementation Decisions / Remarks
- Task 2 (version): Both manifests were already at 3.9.0 — no bump needed. Recorded "already 3.9.0, no edit".
- Task 1 (CLAUDE.md): Updated the `problem-discuss` front-door diagram to show `debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"` as the bug route. Added a paragraph after the existing note describing both handoffs: input (debug reads `problem-{slug}.md` from problem-discuss) and output (large fix → `planning-fix-{slug}.md` → generate-tasks nudge). Preserved the existing "vs problem-discuss" framing.
- Task 1 (README.md): Updated the `/absolutpowers:debug` section — expanded "What it does" with the size-branch (small → inline, large → planning-fix, Phase 4.5 escalation, and problem-discuss input); updated Input and Output fields. Added `planning-fix-{slug}.md` to the project structure tree under `absolutpowers/feature/`. Updated the "Quick bug fix" workflow snippet to show both paths. All wording consistent with Phase 1-3 skill files (same artefact names/paths).
- Edits are minimal and precise — no section rewrites. The debug "vs problem-discuss" note in CLAUDE.md is untouched.
