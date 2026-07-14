# Implementation Context: Faza 2 — generate-tasks ← writing-plans

## Purpose
Short handoff for phase workers. Keep concise. Add only facts later phases need.
HARD BUDGET: max 10 lines per phase entry across all sections combined; whole file target ≤150 lines.

## Completed Phases
- Phase 1 (header grafts): `skills/generate-tasks/SKILL.md` edited, verification passed.
- Phase 2 (body grafts): `skills/generate-tasks/SKILL.md` edited, verification passed.
- Phase 3 (gate + registry): `agents/review-tasks.md`, `VENDORED.md`, `planning-main.md` edited, verification passed.

## Created / Changed API
- Exact new labels in `skills/generate-tasks/SKILL.md`: `**Global Constraints:**` (single-file `## Project Context` ~196-201, full demarcation note; orchestrated main index ~283, one-line cross-ref, no dup), `**Produces:**`/`**Consumes:**` (under `**Test-first:**` in single-file task template ~215-216 and orchestrated phase task template ~349-350).
- Aggregation-rule paragraph at ~381 (after "Each Requires item must reference…", before `implementation-context.md` template): phase Provides = union of task Produces crossing phase boundary; anti-dup phrase "Do NOT repeat within-phase"; single-file = no rollup; Produces/Consumes ≠ AC-N tokens.
- New top-level `## No Placeholders` (SKILL.md ~469, sibling to `## Task Guidelines`, before `## Final Verification Task`): canon list of banned patterns; `**Bad:**` example (~585) now has one trailing line referencing it, still exactly one `**Bad:**` occurrence.
- New top-level `## Self-Review` (SKILL.md ~620, immediately before `## Review Gate — Automatyczna weryfikacja tasków` ~634): 3 checks (spec coverage / placeholder scan / type consistency), explicitly no severity.
- `**Specificity:**` bullet list (~444) gained one bullet: Example must be real code/signature consistent with Produces/Consumes, links to No Placeholders.

## Decisions Made
- GC full note lives once (single-file); orchestrated cross-references it. Produces/Consumes always sit right after `**Test-first:**`, before Create/Requirements — fixed position for Phase 3 grep.

## Test Utilities / Fixtures
- None. (No runtime tests — verification is structural grep + JSON/frontmatter/hook lint.)

## Constraints For Next Phases
- Phase 3 rubric (`agents/review-tasks.md`) must grep exact labels: `**Global Constraints:**`, `**Produces:**`, `**Consumes:**`, `Per Artykuł`, `Do NOT repeat within-phase` (case-insensitive), plus Phase 2 labels: `## No Placeholders`, `## Self-Review`, and confirm zero `5-step`/`checkbox template` hits.
- `## Self-Review` deliberately omits `[BLOCKER]`/`[WARN]` severity — Phase 3's `review-tasks` rubric owns severity taxonomy; do not add severity to Self-Review retroactively.

## Verification History
- Phase 1: header-grafts greps + frontmatter check + GC-2 section-count check (11) all pass — see `01-header-grafts.md` Phase Verification for exact commands.
- Phase 2: `grep -nE "No Placeholders|## Self-Review"` (5 hits, Self-Review line 620 < Review Gate line 634), `grep -c "Test-first"` = 8 unchanged, `grep -c "^\*\*Bad:\*\*"` = 1, `grep -niE "5-step|checkbox template"` = no hits, frontmatter check pass — all green.
- Phase 3: `grep -c "^### [0-9]" agents/review-tasks.md` = 10 (7 original + 3 new: `### 8. Global Constraints`, `### 9. Interfaces / Type Consistency`, `### 10. No-Placeholders Scan`, all before `## Response Format`); Categories line appended (not replaced); `grep -n "writing-plans" VENDORED.md` and `grep -n "W toku" planning-main.md` both hit — all green.

## Faza 2 Epic Status
- All 3 phases of `tasks-phase-2-generate-tasks.md` are content-complete; only `99-final-verification.md` remains for this tasks set. Epic-level `planning-main.md` Faza 2 row now reads `W toku` (orchestrator/human still needs to flip to `Zrobiona` once 99-final-verification + phase-review pass).
