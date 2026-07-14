# Phase 1: Grafty nagłówka — Global Constraints + Produces/Consumes format

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/implementation-context.md`
- ADR `./docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md` (pkt 2 + pkt 4 wiążące dla tej fazy)

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- Sekcja `## Global Constraints` w szablonach `## Project Context` (single-file, ~linie 173-204) ORAZ orchestrated main index (~linie 273-276) `skills/generate-tasks/SKILL.md`.
- Pola `**Produces:**` i `**Consumes:**` w single-file task template (~linie 210-245) i orchestrated phase task template (~linie 342-351).
- Reguła agregacji: phase `Context Contract → Provides` = union `Produces` przekraczających granicę fazy; anty-dup within-phase.
- Zapis w `implementation-context.md → Created / Changed API` verbatim nazw dodanych pól/sekcji (dla dopasowania rubryki Phase 3).

## Read Scope
- `docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md`
- `skills/generate-tasks/SKILL.md` (sekcje: `### Step 1` ~104 constitution load, `### AC Traceability` ~147, `## Project Context` template, task templates, `## Context Contract` ~320-368)

## Write Scope
- `skills/generate-tasks/SKILL.md`

## Objective
Wgraftować dwa mechanizmy nagłówkowe writing-plans w istniejący szkielet generate-tasks: (1) sekcję `## Global Constraints` (spec-derived, cytuje constitution, nie kopiuje) w obu trybach, (2) pola `Produces`/`Consumes` z dokładnymi sygnaturami w formacie zadania obu trybów plus regułę agregacji do phase Provides bez duplikacji. Osadzenie w istniejących sekcjach (rewrite-to-unify), zero appendu.

## Tasks

### Task 1: Dodać sekcję Global Constraints do nagłówka planu (oba tryby)
**Status:** completed
**Test-first:** no (edycja szablonu promptu — brak testów wykonywalnych; weryfikacja structural grep)
**Produces:** sekcja `## Global Constraints` w single-file `## Project Context` i w orchestrated main index
**Consumes:** none

**Requirements:**
- W single-file `## Project Context` (SKILL.md ~173-204) dodaj podsekcję `**Global Constraints:**`: kopiuj cross-task wymagania ze speca **verbatim** (wersje, naming, copy rules); cytuj wiążące artykuły constitution jako `Per Artykuł N: ...`, NIE kopiuj treści pryncypium.
- W orchestrated main index `## Project Context` (SKILL.md ~273-276) dodaj tę samą sekcję.
- Dodaj zdanie demarkacji: GC (spec-derived, ten feature) / constitution.md (project pryncypia, wczytywana osobno w Step 1) / rules.md (lint) — rozłączne (GC-3, ADR pkt 4).
- Instrukcja twarda: skopiowanie treści constitution do GC zamiast cytatu = błąd (ryzyko z planning "Edge cases").
- NIE zmieniaj kroku wczytywania constitution.md w `### Step 1` (~104) (GC-2).

**Tests:**
- `grep -c "Global Constraints" skills/generate-tasks/SKILL.md` ≥2 (single-file + orchestrated).
- `grep -n "Per Artykuł" skills/generate-tasks/SKILL.md` potwierdza wzorzec cytatu.

### Task 2: Dodać pola Produces/Consumes do formatu zadania (oba tryby) + reguła agregacji
**Status:** completed
**Test-first:** no (edycja szablonu promptu — weryfikacja structural grep)
**Produces:** pola `**Produces:**`/`**Consumes:**` w obu task templates; reguła agregacji Produces→Provides
**Consumes:** none (niezależne od Task 1)

**Requirements:**
- W single-file task template (SKILL.md ~210-245) dodaj pod `**Test-first:**` pola `**Produces:**` (symbole/sygnatury eksportowane przez zadanie) i `**Consumes:**` (symbole z wcześniejszych zadań używane tutaj), z dokładnymi sygnaturami.
- W orchestrated phase task template (SKILL.md ~342-351) dodaj te same dwa pola.
- Dodaj regułę agregacji w sekcji orchestrated: phase `Context Contract → Provides` = union `Produces` **przekraczających granicę fazy**; twarde "NIE powtarzaj within-phase" (sygnatury task↔task w jednej fazie zostają tylko w Produces/Consumes).
- Dodaj notę single-file: brak faz → Produces/Consumes task↔task BEZ rollupu; nie szukaj phase Provides w single-file.
- Dodaj jedno zdanie: Produces (sygnatury) to osobne pole od tokenów `AC-N` w nazwach testów — nie kolidują (GC-2/GC-4, ryzyko z planning "Grep-AC × Produces").

**Tests:**
- `grep -c "Produces:" skills/generate-tasks/SKILL.md` ≥2; `grep -c "Consumes:" skills/generate-tasks/SKILL.md` ≥2.
- `grep -niE "nie powtarzaj|do not repeat" skills/generate-tasks/SKILL.md` potwierdza regułę anty-dup within-phase.

## Phase Verification
Run:
- `grep -nE "Global Constraints|Produces:|Consumes:|Per Artykuł" skills/generate-tasks/SKILL.md`
- `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done` (frontmatter nietknięty)
- `grep -c "AC Traceability\|Test-first\|HARD BUDGET" skills/generate-tasks/SKILL.md` (GC-2: sekcje NIE-do-dotykania obecne)

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope (`skills/generate-tasks/SKILL.md`) unless explicitly justified.
- Phase verification commands pass; grep-AC / Test-first / budget sekcje nienaruszone (GC-2).
- `implementation-context.md → Created / Changed API` zaktualizowany verbatim nazwami dodanych sekcji/pól.
- All items in `## Context Contract → Provides` fulfilled.

## Implementation Decisions / Remarks
- Task 1: added `**Global Constraints:**` subsection in the single-file `## Project Context` template (between `**Conventions:**` and `**Verification commands:**`, SKILL.md ~196-201) and in the orchestrated main index `## Project Context` template (SKILL.md ~283) — the orchestrated version is a one-line cross-reference to the single-file demarcation note (no duplication of the full note text, per rewrite-to-unify).
- Task 1: demarcation note placed as a blockquote directly under the single-file GC bullets: GC (spec-derived, this feature) is distinct from `constitution.md` (project pryncypia, loaded separately in Step 1) and `rules.md` (lint); hard instruction that copying constitution article text into GC (instead of citing `Per Artykuł N`) is a plan error.
- Task 2: added `**Produces:**`/`**Consumes:**` fields directly under `**Test-first:**` in both the single-file task template (SKILL.md ~215-216) and the orchestrated phase task template (SKILL.md ~349-350).
- Task 2: aggregation rule + single-file no-rollup note + AC-N/Produces non-collision note added as one paragraph right after "Each Requires item must reference..." (SKILL.md ~381), immediately before the `implementation-context.md` template — this is the natural home for Context-Contract-adjacent meta-rules and keeps the phase-file template block itself unchanged (GC-1/GC-4).
- Did not touch Step 1 constitution load, AC Traceability, Mode section, Review Gate flow, epic subfolder handling, Test-first marker semantics, or implementation-context.md size/budget rules (GC-2 verified via phase verification grep count = 11, matching pre-existing occurrences).
- Frontmatter of `skills/generate-tasks/SKILL.md` untouched (verified by repo-canonical frontmatter check).
