# Phase 1: Protokół 4 statusów (worker + O3 handling)

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (first phase).
- Referencyjnie (read-only): `skills/vendored/subagent-driven-development/SKILL.md` — źródłowa mechanika 4 statusów i drabiny 4-way.

### Provides (for later phases)
- `agents/implementation-worker.md`: sekcja Output Format wylicza dokładnie 4 wartości `PHASE_RESULT`: `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` (bez `COMPLETED`, bez `FAILED`).
- `agents/implementation-worker.md`: warunek `DONE` (dawny "Use COMPLETED only when…"), jawny warunek `DONE_WITH_CONCERNS`, reguła `NEEDS_CONTEXT` przy niespełnionym Requires.
- `skills/implement/SKILL.md` Step O3: cztery odrębne gałęzie obsługi (jedna per status) + drabina 4-way dla `BLOCKED`.
- Referencje "worker reports COMPLETED" w SKILL.md (O4) przepisane na `DONE`.

## Read Scope
- `agents/implementation-worker.md`
- `skills/implement/SKILL.md` (Steps O3, O4)
- `skills/vendored/subagent-driven-development/SKILL.md` (wzorzec drabiny)

## Write Scope
- `agents/implementation-worker.md`
- `skills/implement/SKILL.md` (Step O3 body; nagłówek dispatchu w O4 gdzie pada słowo "COMPLETED")

## Objective
Zmienić protokół raportowania workera z 3 statusów (`COMPLETED | BLOCKED | FAILED`) na czyste 4 (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`, `FAILED` złożony w `BLOCKED`) i wprowadzić w orchestratorze (Step O3) cztery odrębne ścieżki obsługi zamiast jednej wspólnej gałęzi "BLOCKED lub FAILED, stop and report", w tym drabinę eskalacji 4-way dla `BLOCKED`.

## Tasks

### Task 1: Przepisz Output Format i reguły statusów w `implementation-worker.md`
**Status:** completed
**Traces to:** AC-1, AC-2

**Modify:**
- `agents/implementation-worker.md`

**Description:**
Sekcja Output Format (obecnie linia ~84 `PHASE_RESULT: COMPLETED | BLOCKED | FAILED`) oraz reguła zamykająca (obecnie linia ~105 "Use `COMPLETED` only when…") i reguła Requires→BLOCKED (obecnie linia ~34) dostają nowy zestaw 4 statusów. To definicyjne źródło nazw statusów dla całej fazy.

**Requirements:**
- W linii statusu Output Format wylicz dokładnie: `PHASE_RESULT: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`. Usuń `COMPLETED` i `FAILED` z tej linii i z całego pliku (żadne odwołanie do `COMPLETED`/`FAILED` jako wartości PHASE_RESULT nie zostaje).
- Przepisz regułę zamykającą: "Use `DONE` only when all phase tasks are complete, phase verification passed, phase file statuses are updated, and the handoff is updated or explicitly not needed." (ten sam warunek co dawny COMPLETED, nowa nazwa).
- Dodaj osobny, jawny warunek `DONE_WITH_CONCERNS`: praca skończona i zweryfikowana, ale worker flaguje wątpliwość (correctness/scope do zaadresowania przed phase-review, albo obserwacja typu "plik rośnie" do zanotowania). Worker MUSI w `Notes for orchestrator` wypisać konkretne wątpliwości gdy zwraca ten status.
- Zmień regułę Requires (linia ~34): przy niespełnionym `## Context Contract -> Requires` worker zwraca `PHASE_RESULT: NEEDS_CONTEXT` (nie `BLOCKED`), z listą niespełnionych itemów — to sygnał re-dispatchu z kontekstem, nie twarda awaria.
- `BLOCKED` zostaje dla twardych awarii (verification/build fail, task nie do ukończenia w obecnym kształcie).

**Tests:**
- `grep -Eq 'PHASE_RESULT: *DONE *\| *DONE_WITH_CONCERNS *\| *NEEDS_CONTEXT *\| *BLOCKED' agents/implementation-worker.md` → exit 0 (AC-1)
- `! grep -Eq 'PHASE_RESULT.*COMPLETED|PHASE_RESULT.*FAILED' agents/implementation-worker.md` → brak COMPLETED/FAILED jako wartości (AC-1)
- `grep -q 'NEEDS_CONTEXT' agents/implementation-worker.md && grep -q 'DONE_WITH_CONCERNS' agents/implementation-worker.md` → exit 0 (AC-2)
- `grep -q 'Use `DONE` only when' agents/implementation-worker.md` → warunek DONE przeniesiony (AC-2)

**Implementation decisions / remarks:**
- Requires-check rule (line ~34) rewritten to return `NEEDS_CONTEXT` instead of `BLOCKED`, consistent with Task 2's O3 handling.
- Added explicit `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED` condition sentences after the old `DONE` (renamed from `COMPLETED`) rule, mirroring the vendored source's four-status semantics.

**Example:**
```text
PHASE_RESULT: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
...
Use `DONE` only when all phase tasks are complete, phase verification passed,
phase file statuses are updated, and the handoff is updated or explicitly not needed.
Return `DONE_WITH_CONCERNS` when the work is complete and verified but you must flag a
concern (correctness/scope doubt, or an observation like a file growing large); list
each concern under `Notes for orchestrator`.
Return `NEEDS_CONTEXT` (not BLOCKED) when a `Context Contract -> Requires` item is
unsatisfied; list the unsatisfied items so the orchestrator can supply context and re-dispatch.
```

### Task 2: Cztery gałęzie obsługi + drabina 4-way w Step O3
**Status:** completed
**Traces to:** AC-3, AC-4

**Modify:**
- `skills/implement/SKILL.md` (Step O3; nagłówek dispatchu w O4 gdzie pada "COMPLETED")

**Description:**
Obecny Step O3 (linie ~220–234) traktuje `BLOCKED`/`FAILED` jedną wspólną gałęzią "stop and report". Zastąp go czterema odrębnymi ścieżkami — jedną per status — oraz udokumentowaną drabiną eskalacji dla `BLOCKED`. Zaktualizuj też referencję w O4 (linia ~237 "After a worker reports `COMPLETED`") na `DONE`.

**Requirements:**
- Cztery odrębne gałęzie (AC-3):
  - `DONE` → przejdź do phase-review (Step O4).
  - `DONE_WITH_CONCERNS` → orchestrator NAJPIERW czyta zgłoszone wątpliwości; wątpliwości correctness/scope adresuje przed phase-review, obserwacje notuje i idzie do review.
  - `NEEDS_CONTEXT` → orchestrator dostarcza brakujący kontekst (z `implementation-context.md`/kodu/wcześniejszych faz) i re-dispatchuje TĘ SAMĄ fazę (nie eskalacja).
  - `BLOCKED` → drabina eskalacji (niżej).
- Usuń dawną wspólną gałąź "BLOCKED lub FAILED, stop and report" — nie może zostać jako fallback.
- Drabina 4-way dla `BLOCKED`, w tej kolejności (AC-4):
  1. problem kontekstu → dostarcz brakujący kontekst, re-dispatch **ten sam** model
  2. wymaga więcej rozumowania → re-dispatch **mocniejszy** model
  3. task za duży → **dekompozycja** fazy na mniejsze zadania
  4. plan sam jest zły → **eskalacja do człowieka**
- Reguła twarda w tekście: nigdy nie ignoruj eskalacji ani nie zmuszaj tego samego modelu do retry bez zmiany wejścia.
- W O4 zmień "After a worker reports `COMPLETED`" → "After a worker reports `DONE`" (i analogiczne wystąpienia słowa COMPLETED jako statusu workera w O3/O4).

**Tests:**
- `grep -q 'DONE_WITH_CONCERNS' skills/implement/SKILL.md && grep -q 'NEEDS_CONTEXT' skills/implement/SKILL.md` (AC-3)
- `! grep -q 'BLOCKED or FAILED' skills/implement/SKILL.md && ! grep -q 'BLOCKED lub FAILED' skills/implement/SKILL.md` → wspólna gałąź usunięta (AC-3)
- Ręczny grep drabiny: `grep -q 'mocniejszy' skills/implement/SKILL.md && grep -Eiq 'dekompoz' skills/implement/SKILL.md && grep -Eiq 'eskal' skills/implement/SKILL.md` (AC-4)
- `! grep -q 'reports `COMPLETED`' skills/implement/SKILL.md` → referencja przepisana na DONE (AC-3)

**Implementation decisions / remarks:**
- Old single "BLOCKED or FAILED, stop and report" branch replaced with 4 explicit bullets in Step O3 (`DONE` → O4; `DONE_WITH_CONCERNS` → address correctness/scope concerns first, note observations; `NEEDS_CONTEXT` → supply context + re-dispatch same phase, not an escalation; `BLOCKED` → 4-way ladder).
- The old "Requires unsatisfied → ask user to fix/skip" sub-case moved under `NEEDS_CONTEXT` (since the worker now reports `NEEDS_CONTEXT`, not `BLOCKED`, for unsatisfied Requires), keeping the ladder purely for hard-failure escalation.
- Ladder text mixes English/Polish (matching this file's existing bilingual style, e.g. Step O4's REJECTED handling) — written to satisfy the phase's literal grep tests (`mocniejszy`, `dekompoz`, `eskal`) while staying in the surrounding English prose.
- O4 dispatch header "After a worker reports `COMPLETED`" → "After a worker reports `DONE`".

## Phase Verification
Run:
```bash
grep -Eq 'PHASE_RESULT: *DONE *\| *DONE_WITH_CONCERNS *\| *NEEDS_CONTEXT *\| *BLOCKED' agents/implementation-worker.md
grep -q 'DONE_WITH_CONCERNS' skills/implement/SKILL.md && grep -q 'NEEDS_CONTEXT' skills/implement/SKILL.md
! grep -Eq 'BLOCKED (or|lub) FAILED' skills/implement/SKILL.md
head -1 skills/implement/SKILL.md | grep -q '^---$'
```

## Completion Criteria
- Oba pliki zaktualizowane, wszystkie greps z Tasks/Phase Verification przechodzą.
- Żaden `COMPLETED`/`FAILED` nie zostaje jako wartość PHASE_RESULT w obu plikach.
- Frontmatter obu plików nienaruszony.
- `implementation-context.md` zaktualizowany o potwierdzone nazwy 4 statusów.
- Wszystkie itemy z `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- 4-status protocol landed in both `agents/implementation-worker.md` (Output Format + closing rules + Requires-check step 4) and `skills/implement/SKILL.md` Step O3 (four separate branches, no shared fallback) + Step O4 dispatch header (`COMPLETED` → `DONE`).
- Ladder for `BLOCKED` uses mixed English/Polish text (matching this file's existing bilingual convention) to satisfy the phase's literal Polish-word grep tests (`mocniejszy`, `dekompoz`, `eskal`) while the surrounding Step O1–O5 prose stays English.
- All Task-level Tests and the Phase Verification block pass (see commands run below); no `COMPLETED`/`FAILED` remain as `PHASE_RESULT` values in either file; frontmatter of both files untouched.
