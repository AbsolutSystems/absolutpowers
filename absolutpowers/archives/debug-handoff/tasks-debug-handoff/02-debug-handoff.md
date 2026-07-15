# Phase 2: debug emits/consumes handoff artefacts

## Status
completed

## Parent
`./absolutpowers/feature/tasks-debug-handoff.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-debug-handoff/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1: `generate-tasks` recognizes `planning-fix-{slug}.md` as planning input and emits `tasks-fix-{slug}.md` — so debug's output route has a live consumer. Confirm via `grep "planning-fix-" claude/skills/generate-tasks/SKILL.md`.

### Provides (for later phases)
- `debug` SKILL.md (both trees) has a `## Handoff Input` section: if invoked with a path to `problem-{slug}.md`, read it before Phase 1 and use the named case's evidence (reguła, flow, `file:line`, fakty z załączników) as Phase 1 starting point — confirm/deepen, not re-derive. Iron Law unchanged.
- `debug` Phase 4 has a size-classification branch (after Phase 3 / root cause established): small → inline (as today); large → write `absolutpowers/feature/planning-fix-{slug}.md` and route to `generate-tasks` instead of fixing inline. Threshold = generate-tasks single-file-vs-orchestrated heuristic.
- Phase 4.5 (3+ failed fixes / architectural) escalates by writing `planning-fix-{slug}.md` (current root cause + failed hypotheses) and routing to `generate-tasks` — no longer dead-ends at "discuss with user".
- A `planning-fix-{slug}.md` content template is specified in the debug skill (Problem = root cause+dowód, Wybrane rozwiązanie = fix, Zakres, optional AC).
- All of the above present identically in BOTH `claude/skills/debug/SKILL.md` and `codex/skills/debug/SKILL.md` (modulo expected frontmatter drift).

## Read Scope
- `claude/skills/debug/SKILL.md`
- `codex/skills/debug/SKILL.md`
- `claude/skills/problem-discuss/SKILL.md` (Faza 4 report shape — to know what `problem-{slug}.md` contains)
- `absolutpowers/feature/planning-debug-handoff.md` ("Oczekiwane zachowanie", edge cases)

## Write Scope
- `claude/skills/debug/SKILL.md`
- `codex/skills/debug/SKILL.md`

## Objective
Close both ends of the debug tree. Add a `## Handoff Input` section so debug starts from problem-discuss evidence when given a `problem-{slug}.md` path. Add a fix-size branch after root cause is established: small stays inline, large is written out as `planning-fix-{slug}.md` and routed to `generate-tasks`. Make Phase 4.5 escalate through the same artefact. Iron Law and 4-phase core stay intact. Both trees identical.

## Tasks

### Task 1: Add `## Handoff Input` section (both trees)
**Status:** completed
**Traces to:** none (no AC section in planning doc)

**Requirements:**
- Add a `## Handoff Input` section near the top (after the `vs problem-discuss` note / before `## The Four Phases`, alongside `## Context Files`).
- Behavior: if invoked with a path to `absolutpowers/problem/problem-{slug}.md` (optionally plus a case number, e.g. `"Sprawa 2"`), read it BEFORE Phase 1. Treat the named case's evidence (reguła biznesowa, flow, `file:line`, fakty z załączników) as the Phase 1 starting point — confirm/deepen, do NOT re-derive from zero.
- State explicitly: section is OPTIONAL — no path = normal start from Phase 1 (zero regression for solo debug).
- Edge cases (from planning doc): multi-case file + no case number → ask which case; problem-discuss evidence contradicted by deeper investigation → trust fresh evidence, note the divergence (consistent with "memory is context, not proof").
- Reaffirm Iron Law: handoff gives a head start, does not waive root-cause investigation; debug may refute problem-discuss's preliminary hypothesis with evidence.
- Identical in both trees.

**Tests:**
- `grep -n "Handoff Input" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md` matches in both.
- Section references `problem-{slug}.md` and the optional/no-path fallback.

### Task 2: Add fix-size branch in Phase 4 + escalate Phase 4.5 (both trees)
**Status:** completed
**Traces to:** none (no AC section in planning doc)

**Requirements:**
- In Phase 4 (Implementation), before "Implement Single Fix", insert a size-classification step run after root cause is established (end of Phase 3):
  - **Small** (1 file / 1 layer, no migration/API/security/shared-core) → inline, exactly as today (failing test → single fix → verify).
  - **Large** (multiple layers/modules, migration, public API, security boundary, shared core, OR Phase 4.5 escalation) → do NOT implement inline. Write `absolutpowers/feature/planning-fix-{slug}.md` and route to `/absolutpowers:generate-tasks @absolutpowers/feature/planning-fix-{slug}.md` (nudge, not auto-run).
  - Threshold = the same heuristic as single-file vs orchestrated in `generate-tasks` (state this explicitly; one size model across the pipeline).
  - Borderline small/large → choose handoff (gates > ungated inline); justify the choice explicitly in the response.
- Update Phase 4.5 ("If 3+ Fixes Failed: Question Architecture"): instead of dead-ending at "discuss with user", escalate by writing `planning-fix-{slug}.md` capturing current root cause + failed hypotheses (valuable context for generate-tasks) and routing onward. Keep the architectural-pause discussion, but give it an artefact exit.
- Add a `planning-fix-{slug}.md` template block: Problem (= root cause z dowodem `file:line`), Wybrane rozwiązanie (= chosen fix), Zakres, optional `## Acceptance Criteria` (recommended for large fixes — root cause defines expected post-fix behavior; enables downstream Intent Fidelity / AC checks).
- Update the Quick Reference / Red Flags only as needed to stay consistent (do not contradict the new branch). Do NOT change the Iron Law text.
- Identical in both trees.

**Tests:**
- `grep -n "planning-fix-" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md` matches in both.
- Phase 4 contains both the small→inline and large→generate-tasks branches.
- Phase 4.5 references writing `planning-fix-{slug}.md` (no longer ends at conversation only).

## Phase Verification
Run:
- `grep -n "Handoff Input\|planning-fix-" claude/skills/debug/SKILL.md codex/skills/debug/SKILL.md`
- `./scripts/diff-skills.sh` — debug diff shows only expected drift (`Agent` in `allowed-tools`, `argument-hint`), no behavioral divergence

## Completion Criteria
- All phase tasks are completed.
- All changes within Write Scope.
- Iron Law and 4-phase core unchanged; only input/output handoff added.
- Both trees identical (modulo expected frontmatter drift).
- `implementation-context.md` updated: note final section name/anchor and the `planning-fix-` template location.
- All `## Context Contract -> Provides` items fulfilled.

## Implementation Decisions / Remarks
- `## Handoff Input` section inserted after the `vs problem-discuss` blockquote, before `## Context Files`, in both trees.
- Section is marked OPTIONAL; no-path case falls through to normal Phase 1 (zero regression).
- Edge cases covered inline: multi-case file + no case number → ask; contradicted evidence → trust fresh, note divergence.
- Iron Law reaffirmation included at end of section.
- Phase 4 Step 0 (size classification) inserted before existing step 1 "Create Failing Test Case". Small/large threshold explicitly equated to generate-tasks single-file vs orchestrated heuristic.
- `planning-fix-{slug}.md` template block included in Phase 4, with AC marked optional but recommended for large fixes.
- Phase 4.5 updated: discussion with user retained, but artefact exit (`planning-fix-{slug}.md` + generate-tasks nudge) added. 3+ failures automatically = Large scope.
- Quick Reference Phase 4 row updated to mention the size branch.
- Iron Law text is unchanged.
- Body content verified identical between both trees via `diff` after stripping frontmatter. Only expected drift: `allowed-tools` + `argument-hint` in Claude frontmatter.
- Grep verification: 8 matches for `Handoff Input\|planning-fix-` in each tree file, symmetric.
