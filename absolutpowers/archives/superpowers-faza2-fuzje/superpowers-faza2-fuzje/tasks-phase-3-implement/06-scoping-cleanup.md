# Phase 6: Ograniczenie zasięgu do orchestrated + czystka task-brief

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Z Phase 1: protokół 4 statusów (`DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED`) obecny w SKILL.md (O3) i worker.
- Z Phase 2: tabela routingu modelu per rola w O2.
- Z Phase 3: sekcja Durable Progress (ledger) w SKILL.md.
- Z Phase 5: wpięcie review-package w O4/O6 oraz zmiany w `agents/{phase-review,review-implementation}.md`.

### Provides (for later phases)
- `skills/implement/SKILL.md`: jawne ograniczenie 4-statusowego protokołu, tabeli routingu i ledgera do trybu orchestrated; sekcja Single-File Process nie używa słownictwa `DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED` ani nie wymaga ledgera do wznowienia.
- Wszystkie 4 zmodyfikowane pliki pluginu wolne od dispatchu/odwołań do `task-brief`.

## Read Scope
- `skills/implement/SKILL.md` (Mode Detection, Single-File Process, sekcje z Phase 1–3/5)
- `agents/implementation-worker.md`, `agents/phase-review.md`, `agents/review-implementation.md`

## Write Scope
- `skills/implement/SKILL.md` (Mode Detection / Single-File Process; dopiski scope-guard w sekcjach orchestrated)

## Objective
Jawnie ograniczyć nowe mechanizmy (4 statusy, model-per-rola, ledger) do trybu orchestrated i zapewnić że Single-File Process ich nie forsuje; potwierdzić że decyzja "task-brief pominięty" jest odzwierciedlona w treści (nie tylko w planie).

## Tasks

### Task 1: Scope-guard — mechanizmy orchestrated-only
**Status:** completed
**Traces to:** AC-10

**Modify:**
- `skills/implement/SKILL.md` (sekcje orchestrated: dopisz zasięg; Single-File Process / Mode Detection)

**Description:**
Dodaj jawne stwierdzenia że protokół 4 statusów, tabela routingu modelu per rola i ledger dotyczą wyłącznie trybu orchestrated (dispatch subagentów). Upewnij się że Single-File Process nie używa słownictwa statusów ani nie wymaga ledgera do resume.

**Requirements:**
- W sekcji orchestrated (lub Durable Progress / O2 / O3) dodaj notę: "Mechanizmy: protokół 4 statusów, model routing per rola, ledger — dotyczą wyłącznie trybu orchestrated. Single-file nie dispatchuje subagentów → status protokół go nie dotyczy, ledger opcjonalny." (spójne z edge case planning doc, linia 120).
- Zweryfikuj i w razie potrzeby popraw Single-File Process: NIE używa `DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED` jako statusów zadań (single-file używa `pending`/`in-progress`/`completed`), NIE wymaga `progress.md` do wznowienia (single-file resume = marker `in-progress` w tasks file, jak obecnie).
- Nie usuwaj istniejącej mechaniki single-file — tylko zapewnij rozłączność słownictwa i jawny scope.

**Tests:**
- `grep -Eiq 'orchestrated' skills/implement/SKILL.md` w kontekście scope-guard; ręczny odczyt: nota o zasięgu obecna (AC-10)
- Weryfikacja rozłączności — sekcja Single-File Process nie zawiera nowych statusów. Komenda pomocnicza (ekstrakcja sekcji Single-File i grep):
  ```bash
  awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -Eq 'DONE_WITH_CONCERNS|NEEDS_CONTEXT' && echo "LEAK" || echo "OK"
  ```
  Oczekiwane: `OK` (AC-10)
- Single-File Process nie wymaga ledgera: `awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -q 'progress.md' && echo "LEAK" || echo "OK"` → `OK` (AC-10)

**Implementation decisions / remarks:**
- Placed the scope-guard note as a blockquote in `## Orchestrated Process`, right after the existing "Path note" blockquote and before `### Durable Progress (ledger)` — this is the natural home since the ledger section is where all three mechanisms (4-status protocol, model-routing table, ledger) converge, and it stays outside the `Single-File Process`/`Rules` awk window used by the regression test.
- Verified (before editing) that Single-File Process already used only `pending`/`in-progress`/`completed` and never mentioned `progress.md` — no cleanup was needed there, only the explicit disclaimer was missing.

### Task 2: Weryfikacja nieobecności task-brief w zmodyfikowanych plikach
**Status:** completed
**Traces to:** AC-15

**Modify:**
- (żaden — task weryfikacyjny; usuń ewentualne odwołanie tylko jeśli grep coś znajdzie)

**Description:**
Potwierdź że żaden ze zmodyfikowanych plików pluginu nie zawiera dispatchu ani odwołania do `task-brief` (decyzja "task-brief pominięty" odzwierciedlona w treści). Jeśli grep znajdzie odwołanie — usuń je.

**Requirements:**
- Grep 4 plików pod kątem `task-brief`. Oczekiwany wynik: brak trafień.
- Jeśli którekolwiek trafienie istnieje — usuń odwołanie/dispatch (poza scope byłoby dodawanie task-brief; ma go NIE być).
- Uwaga: dotyczy plików pluginu z Write Scope tej fazy — NIE dotyczy `skills/vendored/...` (tam task-brief zostaje jako vendored, poza scope).

**Tests:**
- ```bash
  ! grep -l 'task-brief' skills/implement/SKILL.md agents/implementation-worker.md agents/phase-review.md agents/review-implementation.md
  ```
  → brak trafień, exit 0 (AC-15)

**Implementation decisions / remarks:**
- Grep confirmed zero hits for `task-brief` across all 4 plugin files (`skills/implement/SKILL.md`, `agents/implementation-worker.md`, `agents/phase-review.md`, `agents/review-implementation.md`) before any edit in this phase — nothing to remove. This is consistent with Phase 4's decision (recorded in `implementation-context.md`) that `task-brief` was intentionally not forked.

## Phase Verification
Run:
```bash
awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -Eq 'DONE_WITH_CONCERNS|NEEDS_CONTEXT' && echo "LEAK-STATUS" || echo "OK-STATUS"
awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -q 'progress.md' && echo "LEAK-LEDGER" || echo "OK-LEDGER"
! grep -l 'task-brief' skills/implement/SKILL.md agents/implementation-worker.md agents/phase-review.md agents/review-implementation.md
```
Oczekiwane: `OK-STATUS`, `OK-LEDGER`, grep bez trafień (exit 0).

## Completion Criteria
- Nota scope-guard (orchestrated-only) obecna; Single-File Process rozłączny ze słownictwem statusów i nie wymaga ledgera.
- Żaden z 4 plików pluginu nie zawiera `task-brief`.
- Wcześniejsze zmiany (Phase 1–3/5) nienaruszone.
- `implementation-context.md` zaktualizowany.
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- Added a single scope-guard blockquote in `skills/implement/SKILL.md` under `## Orchestrated Process`, between the existing "Path note" blockquote and `### Durable Progress (ledger)`. It names all three mechanisms (4-status protocol, model-routing-per-role table, ledger) as orchestrated-only and states Single-File Process does not dispatch subagents so none apply there, keeping its own `pending`/`in-progress`/`completed` statuses and resuming from the in-file `in-progress` marker (no ledger needed).
- Task 2 required no edits: grep of the 4 plugin files for `task-brief` returned zero hits both before and after the Task 1 edit — the "task-brief pominięty" decision from Phase 4 was already fully reflected; this phase only confirms it in writing.
- No prior phase content (O2/O3/O4/O6/Durable Progress) was touched — `git diff` shows exactly one new hunk (the scope-guard paragraph) plus the previously-completed Phase 1/2/3/5 hunks.
