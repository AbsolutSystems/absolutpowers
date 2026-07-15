# Phase 3: Wire review enforcement + update-ai-context demarcation (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-constitution/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `claude/skills/constitution/SKILL.md` exists (Phase 1) — defines `absolutpowers/constitution.md` and the verbatim demarcation sentence (recorded in `implementation-context.md`) reused here.

### Provides (for later phases)
- `review` (both trees) Faza 3 checks compliance with constitution pryncypia (reports violations, does not block).
- `update-ai-context` (both trees) Phase 3 carries a demarcation note: pryncypia → `constitution`, mechanika → here.

## Read Scope
- `claude/skills/review/SKILL.md` (insertion point: FAZA 3 RULES CHECK, ~L190–198, and report format ~L238–240)
- `claude/skills/update-ai-context/SKILL.md` (insertion point: PHASE 3 Rules, ~L234–264)
- `codex/skills/review/SKILL.md`
- `codex/skills/update-ai-context/SKILL.md`

## Write Scope
- `claude/skills/review/SKILL.md`
- `codex/skills/review/SKILL.md`
- `claude/skills/update-ai-context/SKILL.md`
- `codex/skills/update-ai-context/SKILL.md`

## Objective
Extend review Faza 3 with a "Pryncypia (constitution)" sub-check (decyzja #3 — extend, not a new phase), and add a demarcation note to update-ai-context Phase 3 so mechanical rules and ratified pryncypia stay in separate files. Constitution violations are *reported*, never block the build (out of scope: hard gate).

## Tasks

### Task 1: Extend review Faza 3 with constitution sub-check (both trees)
**Status:** completed

**Modify:**
- `claude/skills/review/SKILL.md`
- `codex/skills/review/SKILL.md`

**Requirements:**
- In FAZA 3, after the existing rules.md check, add a "Pryncypia (constitution)" sub-section: read `./absolutpowers/constitution.md`; if absent, write "Brak pliku ./absolutpowers/constitution.md, pomijam sprawdzanie pryncypiów." and continue. If present, for each Artykuł assess whether the diff violates its Norma; cite `Artykuł N` per finding.
- Make explicit it REPORTS violations (binary per article) but does NOT block — phrase consistently with the existing "review raportuje, nie blokuje" stance.
- Add a line to the report format (Faza 3 section, ~L238): `### Naruszone pryncypia (constitution): [lista z Artykuł N]`.
- Update the `## Podsumowanie` block to include a `Naruszone pryncypia: [liczba]` counter line.
- Mirror identically in both trees.

**Tests:**
- Manual: `grep -n "constitution\|Pryncypia" claude/skills/review/SKILL.md codex/skills/review/SKILL.md` — present in both.
- Manual: absent-file fallback text present; "reports, not blocks" wording present.

### Task 2: Add demarcation note to update-ai-context Phase 3 (both trees)
**Status:** completed

**Modify:**
- `claude/skills/update-ai-context/SKILL.md`
- `codex/skills/update-ai-context/SKILL.md`

**Requirements:**
- In PHASE 3 (Rules), add a short note: this phase produces only **mechanical** lint-level rules in `rules.md`; **pryncypia** (osąd/wartości/granice) belong in `absolutpowers/constitution.md` via the `constitution` skill. When a proposed rule is really a principle, redirect it there. Reuse the verbatim demarcation sentence from Phase 1 (`implementation-context.md`).
- Optionally note that a proposed mechanical rule MAY reference an existing Artykuł it derives from (per planning doc), but do NOT add auto-generation of rules from articles (out of scope).
- Mirror identically in both trees.

**Tests:**
- Manual: `grep -n "constitution\|pryncypia\|principle" claude/skills/update-ai-context/SKILL.md codex/skills/update-ai-context/SKILL.md` — note present in both.
- Manual: no auto-generation logic added.

## Phase Verification
Run:
- `grep -rn "constitution" claude/skills/review/ codex/skills/review/ claude/skills/update-ai-context/ codex/skills/update-ai-context/` — present in all four.
- `./scripts/diff-skills.sh` — only pre-existing expected drift for `review` / `update-ai-context`.

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Phase verification commands pass.
- `implementation-context.md` updated (review enforces, update-ai-context demarcates).
- All items in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- review FAZA 3 extended with "Pryncypia (constitution)" sub-section inserted after the existing rules.md check. Absent-file fallback text: "Brak pliku ./absolutpowers/constitution.md, pomijam sprawdzanie pryncypiów." Reports violations (cites Artykuł N), explicitly does NOT block via "Review RAPORTUJE … ale ich NIE blokuje".
- Report format updated: added `### Naruszone pryncypia (constitution): [lista z Artykuł N lub "brak"]` after `### Spełnione: [lista]`. Podsumowanie block extended with `- Naruszone pryncypia: [liczba]` counter.
- update-ai-context PHASE 3 extended with `### Demarcation: rules.md vs constitution.md` sub-section. Contains the verbatim demarcation sentence from implementation-context.md, redirects principles to `constitution` skill, permits optional Artykuł back-reference, explicitly bans auto-generation.
- Both claude/ and codex/ trees updated identically. Only pre-existing expected drift: allowed-tools + argument-hint frontmatter (Claude-only) and triada-review blurb (review, Claude-only). Verified with `diff-skills.sh` and direct file diff.
