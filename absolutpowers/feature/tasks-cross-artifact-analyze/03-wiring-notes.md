# Phase 3: Wiring notes — `review` and `generate-tasks` (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-cross-artifact-analyze.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`
- `./absolutpowers/feature/planning-cross-artifact-analyze.md` (sections "Zakres -> In scope", "Rozważane alternatywy", "Edge cases -> Trigger collision")

## Context Contract

### Requires (from previous phases)
- `analyze` skill exists in both trees with settled behavior (Phase 2 Provides): report path `absolutpowers/reviews/analyze-{slug}.md`, on-demand, audit-only.

### Provides (for later phases)
- `review` (both trees) has a short "vs analyze" demarcation note (trace'owalność/kompletność ≠ jakość kodu).
- `generate-tasks` (both trees) suggests running `analyze` as an optional post-check before `implement` (soft nudge, no gate).

## Read Scope
- `claude/skills/review/SKILL.md`
- `codex/skills/review/SKILL.md`
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`
- `claude/skills/analyze/SKILL.md` (confirm the exact invocation string / slug arg shape to reference)

## Write Scope
- `claude/skills/review/SKILL.md`
- `codex/skills/review/SKILL.md`
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

## Objective
Cross-link the new `analyze` skill from its two neighbors without merging logic: a "vs analyze" demarcation note in `review`, and an optional `analyze` post-check suggestion in `generate-tasks`. Keep both notes byte-identical between Claude and Codex copies.

## Tasks

### Task 1: Add "vs analyze" demarcation note to `review` (both trees)
**Status:** completed

**Modify:**
- `claude/skills/review/SKILL.md`
- `codex/skills/review/SKILL.md`

**Description:**
`review` and `analyze` have adjacent triggers (both read the branch). Add a short note clarifying the boundary so triggers don't collide and users pick the right tool.

**Requirements:**
- Add a concise note (Polish) — in the `## Ważne` list or a small dedicated note near the top — stating: `review` ocenia JAKOŚĆ kodu na branchu (4 fazy); `analyze` ocenia KOMPLETNOŚĆ trace'owalności / spójność planning↔tasks↔kod przez artefakty. Inny wymiar — nie scalać; gdy pytanie brzmi "czy taski/kod pokrywają plan", użyj `analyze`.
- Identical text in both `claude/` and `codex/` files.
- Do not alter the 4-phase review flow or its report format.

**Tests:**
- `grep -ni "analyze" claude/skills/review/SKILL.md codex/skills/review/SKILL.md` returns the new note in both.
- The two notes are identical (diff of the paragraph is empty).

### Task 2: Add optional `analyze` post-check suggestion to `generate-tasks` (both trees)
**Status:** completed

**Modify:**
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

**Description:**
After tasks pass review, `analyze` is a useful optional pre-implement audit. Add a soft nudge (not a gate) so the user knows the option exists. In Claude this lives near the existing Review Gate "PASS" next-step message; in Codex (no gate) place it near the end-of-output next-steps area.

**Requirements:**
- Claude: in the `## Review Gate` "Jeśli VERDICT: PASS" branch, add an optional line: po PASS możesz (opcjonalnie, bez bramki) uruchomić `/absolutpowers:analyze {slug}` jako audyt spójności AC→task(→kod) przed `implement`. Keep the existing `implement` next-step as the primary suggestion.
- Codex: there is no Review Gate; add the equivalent optional suggestion near where the final tasks output / next steps are described, phrased as "opcjonalnie uruchom skill `analyze` dla sluga …".
- Frame as OPTIONAL and explicitly NOT a blocking step (consistent with `analyze` being on-demand).
- Keep the suggestion text identical between trees where the surrounding structure allows; where Claude/Codex structure differs (gate vs no-gate), the wording may differ minimally — note this in Implementation Decisions.

**Tests:**
- `grep -ni "analyze" claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md` returns the new suggestion in both.
- The suggestion is clearly marked optional / non-blocking in both files.

## Phase Verification
Run:
- `grep -cni "analyze" claude/skills/review/SKILL.md codex/skills/review/SKILL.md claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md`
- `./scripts/diff-skills.sh` (review + generate-tasks should show only expected/pre-existing drift)

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Task 1: identical blockquote "Review vs `analyze`" note added near the top of both `review` SKILL.md files (claude line 24, codex line 16). Byte-identical. 4-phase flow untouched.
- Task 2: Claude — optional non-blocking line added in the Review Gate "VERDICT: PASS" branch (line 587), keeping `implement` as primary next step. Codex (no Review Gate) — added a new `## Następny krok` section at end of file with the equivalent optional suggestion phrased "uruchom skill `analyze` dla sluga {slug}". Wording differs minimally between trees due to gate vs no-gate structure, as permitted.
- Phase interrupted by an API socket error after Task 1 (both trees) + Task 2 Claude landed; the orchestrator completed the remaining Codex generate-tasks edit and status updates. No duplicate edits.
- Verification: `grep -cni "analyze"` → review 1/1, generate-tasks 3/3 (2 pre-existing prose + 1 new each). `diff-skills.sh` shows review + generate-tasks differ only by expected/pre-existing drift.
