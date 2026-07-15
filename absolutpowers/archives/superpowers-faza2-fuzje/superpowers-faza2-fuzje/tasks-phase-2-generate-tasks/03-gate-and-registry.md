# Phase 3: Rubryka gate + rejestr — review-tasks.md + VENDORED.md + planning-main.md

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/implementation-context.md` (sekcja `Created / Changed API` — dokładne nazwy sekcji/pól z Phase 1+2, do dopasowania rubryki)
- ADR `./docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md`

## Context Contract

### Requires (from previous phases)
- Sekcje `## Global Constraints`, `## No Placeholders`, `## Self-Review` oraz pola `**Produces:**`/`**Consumes:**` obecne w `skills/generate-tasks/SKILL.md` (Phase 1 + Phase 2 Provides). Rubryka gate weryfikuje dokładnie te elementy — nazwy verbatim z `implementation-context.md → Created / Changed API`.

### Provides (for later phases)
- Trzy nowe checki w `agents/review-tasks.md`: Global Constraints (spec-derived + cytat-referencja constitution), Produces↔Consumes type-consistency, No-Placeholders scan; rozszerzona lista Categories.
- Nota w `VENDORED.md`: `writing-plans` = dawca sekcji (NIE vendorowany), 5 graftów wariant A do generate-tasks.
- Zaktualizowany status Fazy 2 w `planning-main.md`: `Zaplanowana` → `W toku`.

## Read Scope
- `agents/review-tasks.md` (całość — kryteria 1-7 ~50-108, Categories ~133, Severity ~140, Re-review ~150)
- `VENDORED.md` (tabela zvendorowanych ~36-44, nota subagent-driven-development ~44)
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md` (mapa faz ~35)
- `skills/generate-tasks/SKILL.md` (potwierdzenie dokładnych nazw dodanych sekcji/pól)

## Write Scope
- `agents/review-tasks.md`
- `VENDORED.md`
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`

## Objective
Domknąć fuzję po stronie gate i rejestru: rozszerzyć rubrykę `review-tasks.md` o trzy kryteria odpowiadające graftom Phase 1+2 (touch, nie przepisanie — kryteria 1-7 nietknięte), odnotować w `VENDORED.md` writing-plans jako dawcę sekcji (nie vendorowanego) i zaktualizować status Fazy 2 w mapie faz epica.

## Tasks

### Task 1: Rozszerzyć rubrykę agents/review-tasks.md o trzy kryteria (touch)
**Status:** completed
**Test-first:** no (edycja promptu agenta gate — weryfikacja structural grep)
**Produces:** trzy nowe checki + rozszerzone Categories w `agents/review-tasks.md`
**Consumes:** nazwy sekcji/pól z `skills/generate-tasks/SKILL.md` (Phase 1+2 Provides) — muszą się zgadzać verbatim

**Requirements:**
- Dodaj check **Global Constraints**: jeśli tasks doc ma `## Global Constraints`, zweryfikuj spec-derived i że wpisy `Per Artykuł N` to cytat-referencja, nie kopia treści constitution. Brak sekcji przy planie z cross-task wymaganiami → `[WARN]`.
- Dodaj check **Interfaces / type-consistency**: dla każdego `Consumes` istnieje pasujący `Produces` we wcześniejszym zadaniu (sygnatury zgodne); w orchestrated cross-phase Produces wchodzi w phase `Provides` bez duplikacji within-phase. Rozjazd sygnatur lub brakujący Produces → `[BLOCKER]`.
- Dodaj check **No-Placeholders scan**: obecność banowanego wzorca → `[BLOCKER]`.
- Rozszerz listę Categories (~133) o `GLOBAL_CONSTRAINTS`, `INTERFACES`, `PLACEHOLDER` — dodaj, nie zastępuj.
- NIE zmieniaj: semantyki kryteriów 1-7, sekcji Severity, Re-review Protocol, limitu 7 issues, epic phase dependency handling (GC-2). Format zadania rozszerzony → rubryka rozszerzona, nie przebudowana.

**Tests:**
- `grep -niE "Global Constraints|Produces|No-Placeholders|Placeholder" agents/review-tasks.md` potwierdza trzy checki.
- `grep -nE "GLOBAL_CONSTRAINTS|INTERFACES|PLACEHOLDER" agents/review-tasks.md` potwierdza kategorie.
- `grep -c "^### [0-9]" agents/review-tasks.md` ≥7 (kryteria 1-7 zachowane).

### Task 2: Odnotować graft w VENDORED.md i zaktualizować status fazy w planning-main.md
**Status:** completed
**Test-first:** no (edycja dokumentacji rejestru — brak testów wykonywalnych)
**Produces:** nota writing-plans w VENDORED.md; status `W toku` Fazy 2 w planning-main.md
**Consumes:** none

**Requirements:**
- W `VENDORED.md` dodaj notę (POZA tabelą zvendorowanych — writing-plans NIE jest vendorowany): `writing-plans` jako dawca sekcji dla `generate-tasks`, 5 graftów (Global Constraints, Produces/Consumes, No Placeholders, Self-Review, wzmocnienie kompletnego kodu), wariant A (wszczepienie w szkielet, zero osobnej kopii), metoda rewrite-to-unify, ADR `2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md`.
- Zaktualizuj notę o `subagent-driven-development` (~44) TYLKO jeśli graft dotyka jego cross-refów — jeśli nie (scope=generate-tasks, nie implement), zostaw as-is z notą, że integracja implement to Faza 3.
- W `planning-main.md` mapa faz (~35): zmień status Fazy 2 `Zaplanowana` → `W toku`.
- NIE zmieniaj przypiętego SHA, sekcji Źródło, ani not o innych skillach w VENDORED.md (GC-2).

**Tests:**
- `grep -n "writing-plans" VENDORED.md` potwierdza notę o dawcy sekcji.
- `grep -n "W toku" absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md` potwierdza status Fazy 2.

## Phase Verification
Run:
- `grep -nE "GLOBAL_CONSTRAINTS|INTERFACES|PLACEHOLDER" agents/review-tasks.md`
- `grep -c "^### [0-9]" agents/review-tasks.md` (≥7 kryteriów zachowanych)
- `grep -n "writing-plans" VENDORED.md`
- `grep -n "W toku" absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`

## Completion Criteria
- All phase tasks are completed.
- All changes within Write Scope (`agents/review-tasks.md`, `VENDORED.md`, `planning-main.md`) unless explicitly justified.
- Phase verification commands pass; kryteria 1-7 / Severity / Re-review Protocol nienaruszone (GC-2).
- Nowe checki referują dokładnie te nazwy sekcji/pól, które Phase 1+2 wprowadziły do SKILL.md.
- All items in `## Context Contract → Provides` fulfilled.

## Implementation Decisions / Remarks
- Added criteria as `### 8. Global Constraints`, `### 9. Interfaces / Type Consistency (Produces/Consumes)`, `### 10. No-Placeholders Scan`, placed after criterion 7 and before `## Response Format` — kept the existing 1-7 numbered list untouched (verified `grep -c "^### [0-9]"` = 10).
- Categories line extended in place (append, not replace): `..., TEST_FIRST, GLOBAL_CONSTRAINTS, INTERFACES, PLACEHOLDER`.
- Criterion #9 references the exact verbatim SKILL.md phrase `Do NOT repeat within-phase` (Phase 1+2 aggregation-rule paragraph, line ~381) so the rubric and the plan template stay in lockstep.
- VENDORED.md: added a new `## Dawcy sekcji (NIE vendorowani) — Faza 2 fuzji` subsection (after the Pi integration table, before the TS verification note) rather than touching the "Zvendorowane skille" table — `writing-plans` is explicitly not a vendored skill (no local copy, no SHA-drift tracking row). Left the `subagent-driven-development` note (~44) unmodified per Task 2 requirement (its cross-refs are Faza 3 scope, not touched by this graft).
- planning-main.md: only the Faza 2 status cell changed (`Zaplanowana` → `W toku`); phase table row text, ADR link, and all other rows/sections left untouched (GC-2).
- Phase Verification commands all pass; criteria 1-7, `## Severity`, `## Re-review Protocol`, and the "Maximum 7 issues" cap are byte-identical to before the edit (confirmed via grep line anchors).
