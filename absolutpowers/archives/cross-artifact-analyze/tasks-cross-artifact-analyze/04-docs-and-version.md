# Phase 4: Docs + version sanity — README, CLAUDE.md, manifests

## Status
completed

## Parent
`./absolutpowers/feature/tasks-cross-artifact-analyze.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`
- `./absolutpowers/feature/planning-cross-artifact-analyze.md` (sections "Zakres -> In scope", "Decyzje do zatwierdzenia -> Wersja")

## Context Contract

### Requires (from previous phases)
- Phase 1 done: criterion #7 Intent Fidelity + feature-discuss nudge.
- Phase 2 done: `analyze` skill in both trees.
- Phase 3 done: review + generate-tasks wiring notes.

### Provides (for later phases)
- `README.md` and `CLAUDE.md` document `analyze` (cross-cutting audit) + the Intent Fidelity gate criterion.
- Both manifests confirmed at version `3.9.0` (no further bump — analyze ships under the existing 3.9.0 bundle).

## Read Scope
- `README.md`
- `CLAUDE.md`
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

## Write Scope
- `README.md`
- `CLAUDE.md`
- `claude/.claude-plugin/plugin.json` (only if a version correction is needed)
- `codex/.codex-plugin/plugin.json` (only if a version correction is needed)

## Objective
Document the new `analyze` skill and the Intent Fidelity gate criterion in the user-facing README and the agent-facing CLAUDE.md, and confirm both manifests are at the same `3.9.0` version. No re-bump unless a mismatch is found.

## Tasks

### Task 1: Document `analyze` + Intent Fidelity in README and CLAUDE.md
**Status:** completed

**Modify:**
- `README.md`
- `CLAUDE.md`

**Description:**
Add `analyze` to the skill catalog/pipeline description as an on-demand, cross-cutting consistency audit (not a pipeline gate), and note the new `review-tasks` Intent Fidelity criterion. Keep CLAUDE.md's existing pipeline-architecture style.

**Requirements:**
- `CLAUDE.md`: in the Pipeline Architecture area, add a short subsection (alongside the "Standalone Triada Review" / constitution notes) describing `analyze`: on-demand cross-artifact audit (AC→task→kod matrix + six divergence classes), output `absolutpowers/reviews/analyze-{slug}.md`, verdict CONSISTENT/INCONSISTENT, blocking classes 1/3/4/6 + warnings 2/5, hard boundary (audits + routes, never fixes), both trees. Also add a one-line note that `review-tasks` gained criterion #7 Intent Fidelity (`INTENT` verdict category, Claude-only gate).
- `CLAUDE.md`: if a "Cross-Platform Editing Rules" or skill-list area enumerates skills, add `analyze` there too.
- `README.md`: add `analyze` to the skill list / usage section with a one-line description and example invocation `/absolutpowers:analyze {slug}`; place it near `review`/`triada-review`, framed as on-demand (not a gate).
- Keep bilingual conventions consistent with each file's existing language.

**Tests:**
- `grep -ni "analyze" README.md CLAUDE.md` returns the new entries in both.
- `grep -ni "intent fidelity" CLAUDE.md` returns the gate note.

### Task 2: Confirm manifest versions match at 3.9.0
**Status:** completed

**Modify:**
- `claude/.claude-plugin/plugin.json` (only if mismatch)
- `codex/.codex-plugin/plugin.json` (only if mismatch)

**Description:**
The 3.9.0 bundle bump was already applied (analyze is part of that release). Verify both manifests read `3.9.0` and match; correct only if a drift is found. Do NOT bump further.

**Requirements:**
- Read both `"version"` fields; confirm both equal `3.9.0`.
- If they already match at `3.9.0` (expected): make NO change; record "no bump needed — already 3.9.0" in Implementation Decisions.
- If they mismatch: set both to `3.9.0` and note the correction.

**Tests:**
- `python3 -c "import json; a=json.load(open('claude/.claude-plugin/plugin.json'))['version']; b=json.load(open('codex/.codex-plugin/plugin.json'))['version']; print(a,b); assert a==b=='3.9.0'"` prints `3.9.0 3.9.0` and exits 0.

## Phase Verification
Run:
- `grep -ni "analyze" README.md CLAUDE.md`
- `python3 -m json.tool claude/.claude-plugin/plugin.json > /dev/null && python3 -m json.tool codex/.codex-plugin/plugin.json > /dev/null && echo "JSON OK"`
- `python3 -c "import json; a=json.load(open('claude/.claude-plugin/plugin.json'))['version']; b=json.load(open('codex/.codex-plugin/plugin.json'))['version']; assert a==b=='3.9.0'; print('versions OK', a)"`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Task 1: Added `analyze` documentation to CLAUDE.md (new "Cross-artifact Audit: `analyze`" subsection in Pipeline Architecture area, including Intent Fidelity criterion #7 note and INTENT category; `analyze` also added to Cross-Platform Editing Rules). Added `/absolutpowers:analyze` skill entry to README.md Skills Reference (placed after triada-review, before debug; includes six divergence classes, verdict, hard boundary, compare table vs review/triada-review). Added `analyze` on-demand audit note to README.md pipeline section diagram. Updated review-tasks criteria line to include Intent Fidelity. Added `analyze-{slug}.md` to project structure, updated skill count from 13 to 14, updated 3.9.0 changelog entry.
- Task 2: No bump needed — both manifests already at `3.9.0` (verified: `python3 -c "... assert a==b=='3.9.0'"` exits 0). No changes made to either manifest.
