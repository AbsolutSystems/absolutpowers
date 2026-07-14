# Phase 2: Grafty treści — No Placeholders + Self-Review + wzmocnienie kompletnego kodu

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/implementation-context.md`
- ADR `./docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md` (pkt 3 wiążący: dyscyplina, nie szablon)

## Context Contract

### Requires (from previous phases)
- Pola `**Produces:**`/`**Consumes:**` obecne w task templates `skills/generate-tasks/SKILL.md` (Phase 1 Provides) — Self-Review type-consistency check odwołuje się do nich.
- Sekcja `## Global Constraints` obecna (Phase 1 Provides) — Self-Review spec-coverage nie duplikuje jej roli.

### Provides (for later phases)
- Sekcja `## No Placeholders` (lista banowanych wzorców = plan failure) w `skills/generate-tasks/SKILL.md`, obok `## Task Guidelines` (~416); `**Bad:**` example (~558) skonsolidowany jako odsyłacz do niej.
- Sekcja `## Self-Review` PRZED `## Review Gate` (~592): spec coverage / placeholder scan / type consistency (Produces↔Consumes), bez severity.
- Proza w `## Task Guidelines`: `Example` musi zawierać realny kod/sygnatury (link do No Placeholders); szkielet Requirements/Tests/Example i Test-first marker nietknięte.
- Zapis w `implementation-context.md → Created / Changed API` verbatim nazw dodanych sekcji.

## Read Scope
- `docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md`
- `skills/generate-tasks/SKILL.md` (sekcje: `## Task Guidelines` ~416-453, `**Good:**`/`**Bad:**` examples ~516-564, `## Review Gate` ~592, Test-first marker ~418-423)

## Write Scope
- `skills/generate-tasks/SKILL.md`

## Objective
Wgraftować trzy mechanizmy treściowe: (1) `## No Placeholders` — jawną listę wzorców = plan failure, konsolidując istniejący `**Bad:**` example w jeden kanon; (2) `## Self-Review` — lekki pre-gate autora (spec coverage / placeholder scan / type consistency) umieszczony PRZED Review Gate, bez severity; (3) prozę wzmacniającą "kompletny kod" w Task Guidelines bez zmiany szkieletu i Test-first markera. Wszystko rewrite-to-unify.

## Tasks

### Task 1: Dodać sekcję No Placeholders i skonsolidować "Bad" example
**Status:** completed
**Test-first:** no (edycja szablonu promptu — weryfikacja structural grep)
**Produces:** sekcja `## No Placeholders`; skonsolidowany `**Bad:**` example (odsyłacz, nie duplikat)
**Consumes:** none

**Requirements:**
- Dodaj `## No Placeholders` obok `## Task Guidelines` (~416): lista banowanych wzorców — `...`/`// TODO`/`// rest of implementation` w Example, "write tests for the above", "handle errors properly", "add appropriate validation", vague requirement bez sygnatury/typu, "similar to X" bez konkretu. Obecność któregokolwiek = plan failure.
- Skonsoliduj `**Bad:**` example (~558-564): odwołaj go do kanonu No Placeholders (jedno źródło), usuń duplikację — NIE dodawaj drugiego przykładu (GC-1).
- Zachowaj `**Good:**` example (~516-556) bez zmian.
- Synergia grep-AC: zaznacz, że No Placeholders wymusza realne nazwy testów z tokenem `AC-N`, nie zastępuje grep-AC (GC-2).

**Tests:**
- `grep -c "No Placeholders" skills/generate-tasks/SKILL.md` ≥1.
- `grep -c "^\*\*Bad:\*\*" skills/generate-tasks/SKILL.md` = 1 (niezduplikowany), odsyła do No Placeholders.

### Task 2: Dodać sekcję Self-Review (pre-gate autora) PRZED Review Gate
**Status:** completed
**Test-first:** no (edycja szablonu promptu — weryfikacja structural grep)
**Produces:** sekcja `## Self-Review` (spec coverage / placeholder scan / type consistency, bez severity)
**Consumes:** `## No Placeholders` (Task 1 tej fazy — placeholder scan linkuje do niej); pola `Produces`/`Consumes` (Phase 1 — type consistency)

**Requirements:**
- Umieść `## Self-Review` PRZED nagłówkiem `## Review Gate — Automatyczna weryfikacja tasków` (~592).
- Trzy checki: (1) **Spec coverage** — każde wymaganie planning doc pokryte taskiem; (2) **Placeholder scan** — zero wzorców z `## No Placeholders`; (3) **Type consistency** — każdy `Consumes` ma pasujący `Produces` we wcześniejszym zadaniu (sygnatura zgodna).
- Jawnie: self-review NIE emituje severity `[BLOCKER]`/`[WARN]` (severity → Faza 3).
- Jawnie: to check autora PRZED dispatchem `review-tasks`, nie zastępuje bramki.
- Type-consistency: single-file = task↔task; orchestrated dochodzi walidacja rollup Produces→Provides (link do reguły anty-dup z Phase 1).

**Tests:**
- `grep -c "## Self-Review" skills/generate-tasks/SKILL.md` = 1, PRZED linią `## Review Gate` (porównaj numery linii).
- `grep -niE "type consistency|Produces.*Consumes" skills/generate-tasks/SKILL.md` potwierdza check.

### Task 3: Wzmocnić "kompletny kod" prozą (Example = realny kod) bez zmiany szkieletu
**Status:** completed
**Test-first:** no (edycja szablonu promptu — weryfikacja diff + grep)
**Produces:** proza w `## Task Guidelines` o realnym kodzie w Example (link do No Placeholders)
**Consumes:** `## No Placeholders` (Task 1); pola `Produces`/`Consumes` (Phase 1)

**Requirements:**
- W `## Task Guidelines` (`**Specificity:**`/`**What to include:**`, ~431-446) dodaj prozę: `Example` musi zawierać realny kod, sygnaturę lub konkretną konfigurację — nie szkic ani placeholder (link do `## No Placeholders`).
- Powiąż: sygnatury w Example muszą być spójne z polami `Produces`/`Consumes` zadania.
- NIE zmieniaj struktury `Requirements/Tests/Example`; NIE dodawaj 5-step TDD checkbox template (GC-5, ADR pkt 3).
- NIE zmieniaj sekcji Test-first marker (~418-423) ani jej semantyki (GC-2).
- Opcjonalna nota-komentarz: kod w planie jest niezweryfikowany (Opus nie uruchamia testów); implement (Sonnet) iteruje live — Example = kontrakt sygnatur, nie gotowa implementacja.

**Tests:**
- `grep -c "Test-first" skills/generate-tasks/SKILL.md` — niezmienione względem baseline (marker nietknięty).
- `grep -niE "5-step|checkbox template" skills/generate-tasks/SKILL.md` = brak trafień (nie wprowadzono szablonu obry).

## Phase Verification
Run:
- `grep -nE "No Placeholders|## Self-Review" skills/generate-tasks/SKILL.md`
- `grep -c "Test-first" skills/generate-tasks/SKILL.md` (marker nietknięty)
- `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done`

## Completion Criteria
- All phase tasks are completed.
- All changes within Write Scope (`skills/generate-tasks/SKILL.md`) unless explicitly justified.
- Phase verification commands pass; Test-first / grep-AC / Review Gate flow nienaruszone (GC-2); brak 5-step template (GC-5).
- `implementation-context.md → Created / Changed API` zaktualizowany verbatim nazwami dodanych sekcji.
- All items in `## Context Contract → Provides` fulfilled.

## Implementation Decisions / Remarks
- `## No Placeholders` landed right after "What to omit" and before `## Final Verification Task` (SKILL.md ~469), sibling to `## Task Guidelines`, not nested under it — matches "obok" wording in Objective.
- `**Bad:**` example kept as the single occurrence (`grep -c "^\*\*Bad:\*\*"` = 1); added one line after its code block pointing at `## No Placeholders` as the canon — no second example introduced.
- `## Self-Review` landed at SKILL.md line 620, immediately before `## Review Gate — Automatyczna weryfikacja tasków` (line 634); PL callout note + EN checklist body per GC-6 bilingual convention.
- Self-Review's type-consistency check explicitly references the Phase 1 "Produces/Consumes ↔ Context Contract aggregation rule" paragraph (anti-dup, single-file vs orchestrated) instead of restating it — no duplication.
- Task 3 prose added as one new bullet under `**Specificity:**` (Example = real code/signature, linked to No Placeholders and to the task's own Produces/Consumes) plus a small clarifying edit to the existing "Code examples for non-obvious implementations" bullet under `**What to include:**`. Test-first marker section (`**Approach — Test-first marker:**`) and the Requirements/Tests/Example skeleton were not touched.
- Verified no `5-step`/`checkbox template` strings were introduced (GC-5); `Test-first` occurrence count unchanged by diff (no + / - lines touching that string).
