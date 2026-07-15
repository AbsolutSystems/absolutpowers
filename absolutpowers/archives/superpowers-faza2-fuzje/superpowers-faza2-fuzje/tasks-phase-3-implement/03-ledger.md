# Phase 3: Ledger — Durable Progress

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Z Phase 2: `skills/implement/SKILL.md` Step O2 zapisuje BASE commit przed dispatchem workera (sekcja "Before spawning the worker"). Ledger formalizuje MIEJSCE zapisu tego BASE.

### Provides (for later phases)
- `skills/implement/SKILL.md`: nowa, samodzielna sekcja "Durable Progress" (ledger) — ścieżka pliku ledgera obok katalogu faz, format jednej linii per faza z zakresem commitów (BASE..HEAD w skrócie), reguła zapisu BASE przed dispatchem (w O2).
- Reguła autorytatywności: przy rozjeździe ledger + `git log` autorytatywne na resume; status w tasks file = widok dla człowieka.
- Wpięcie: O1 (resume czyta ledger+git log PRZED statusami faz), O4 (append linii ledgera po phase-review PASS).

## Read Scope
- `skills/implement/SKILL.md` (Steps O1, O2, O4; miejsce na nową sekcję)

## Write Scope
- `skills/implement/SKILL.md` (nowa sekcja Durable Progress + edycje O1 i O4)

## Objective
Dodać do `implement` autorytatywny, git-kotwiczony ledger recovery: osobny plik `progress.md` obok katalogu faz, commitowany, jedno źródło prawdy do resume (przed statusami w tasks file). Wpiąć w resumption (O1) i w bookkeeping po PASS (O4).

## Tasks

### Task 1: Nowa sekcja "Durable Progress (ledger)"
**Status:** completed
**Traces to:** AC-6, AC-9

**Modify:**
- `skills/implement/SKILL.md` (dodaj samodzielną sekcję, np. między "Orchestrated Process" a Step O1, lub tuż po O6 — spójnie z układem dokumentu)

**Description:**
Samodzielna sekcja opisująca ledger jako autorytatywne, git-kotwiczone źródło recovery po kompakcji. Trzy pliki, trzy role (udokumentuj rozgraniczenie): phase file = pełny spec/kod; `implementation-context.md` = wąski handoff (≤10 linii/faza); ledger = mapa recovery (commity).

**Requirements:**
- **Ścieżka:** `{tasks-dir}/progress.md` — obok katalogu faz (dla epica: `absolutpowers/feature/{epic}/tasks-{slug}/progress.md`), zgodna z Path Resolution skilla. Konwencja absolutpowers, NIE `.superpowers/sdd/`.
- **Commitowany** — część artefaktów feature'a (przeżywa `git clean`, audytowalny), inaczej niż gitignored scratch review-package.
- **Format linii:** append jednej linii per faza po PASS, np. `Faza N: complete (commits <base7>..<head7>, review clean)`. Skrót commitów (7 znaków). Lżejsze i trudniejsze do pominięcia niż edycja tabeli statusów.
- **BASE:** orchestrator zapisuje BASE commit przed dispatchem (w Step O2 — Phase 2), a po PASS dopisuje HEAD → pełny zakres `base7..head7` w linii ledgera.
- **Reguła autorytatywności (AC-9):** przy rozjeździe między wpisem w ledgerze a statusem fazy w tasks file — **ledger + `git log` są autorytatywne przy resume**; status w tasks file jest jawnie opisany jako widok dla człowieka, nie źródło prawdy.
- Rozgraniczenie trzech plików (phase file / implementation-context.md / ledger) udokumentowane by się nie zlały.

**Tests:**
- `grep -Eiq 'Durable Progress|ledger' skills/implement/SKILL.md` (AC-6)
- `grep -q 'progress.md' skills/implement/SKILL.md` (AC-6)
- `grep -Eiq 'autorytatywn|authoritative' skills/implement/SKILL.md && grep -Eiq 'widok dla człowieka|human.?view|human-readable view' skills/implement/SKILL.md` (AC-9)
- `grep -Eiq 'base7|<base7>|base7\.\.head7|commits .*\.\.' skills/implement/SKILL.md` → format zakresu commitów (AC-6)

**Implementation decisions / remarks:**
- Placed the new section between the "Path note" paragraph and `### Step O1` (first suggested location in the task), as a self-contained `### Durable Progress (ledger)` subsection with a 3-row table drawing the phase-file / implementation-context.md / progress.md distinction, then Path, Committed, Format, and Authoritative-on-resume paragraphs.

### Task 2: Wpięcie ledgera w O1 (resume) i O4 (append po PASS)
**Status:** completed
**Traces to:** AC-6, AC-9

**Modify:**
- `skills/implement/SKILL.md` (Step O1 resumption detection; Step O4 po VERDICT: PASS)

**Description:**
Resume musi ufać ledgerowi + `git log` PRZED statusami faz w tasks file. Po phase-review PASS orchestrator dopisuje linię ledgera w tej samej wiadomości co reszta bookkeepingu.

**Requirements:**
- **O1:** w "Resumption detection" dodaj krok: NAJPIERW przeczytaj ledger `progress.md` + `git log`; fazy obecne w ledgerze = DONE, nie re-dispatchuj. Dopiero potem statusy faz w tasks file (jako widok pomocniczy). Przy rozjeździe — ledger wygrywa.
- **O4:** po `VERDICT: PASS` dodaj krok: append linii `Faza N: complete (commits base7..head7, review clean)` do `progress.md` (obok update statusu w tasks file). Nie zastępuje updatu statusu — dokłada autorytatywny wpis.
- Zachowaj istniejący mechanizm statusów faz w tasks file (nie usuwaj — staje się widokiem dla człowieka).

**Tests:**
- `grep -Eiq 'ledger.*git log|git log.*ledger' skills/implement/SKILL.md` lub ręczny odczyt O1 → resume czyta ledger+git log przed statusami (AC-9)
- Ręczny odczyt O4 → append linii ledgera po PASS (AC-6)
- `! grep -Eq 'BLOCKED (or|lub) FAILED' skills/implement/SKILL.md` (regresja Phase 1 nienaruszona)

**Implementation decisions / remarks:**
- O1: the resumption detection block now leads with a bullet that reads `progress.md` + `git log` before scanning `## Phase Overview`, explicitly stating the ledger wins on disagreement; the phase-status scan is relabeled "secondary, human-facing view". Existing sub-steps 1-6 (report/cross-reference/Requires check) untouched.
- O4: added one bullet before the existing PASS bookkeeping (status update, note, continue) — it does not replace or reorder them, only prepends the ledger append.
- Did not touch Step O2 body itself (out of this phase's Write Scope) — the BASE-recording MUST bullet from Phase 2 is referenced by name ("Step O2, 'Before spawning the worker'") rather than duplicated.

## Phase Verification
Run:
```bash
grep -Eiq 'Durable Progress|ledger' skills/implement/SKILL.md
grep -q 'progress.md' skills/implement/SKILL.md
grep -Eiq 'autorytatywn|authoritative' skills/implement/SKILL.md
head -1 skills/implement/SKILL.md | grep -q '^---$'
```

## Completion Criteria
- Samodzielna sekcja Durable Progress obecna: ścieżka, format linii z zakresem commitów, BASE-przed-dispatchem, reguła autorytatywności.
- O1 czyta ledger+git log przed statusami; O4 dopisuje linię po PASS.
- Rozgraniczenie trzech plików udokumentowane.
- Frontmatter i wcześniejsze edycje (O2 z Phase 2, O3 z Phase 1) nienaruszone.
- `implementation-context.md` zaktualizowany.
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- Verified Context Contract Requires before starting: Phase 2's Step O2 "Before spawning the worker" already contains the MUST bullet "Record BASE commit (MUST, before dispatch): run `git rev-parse HEAD` ... before dispatching the worker" — confirmed present, unmodified in this phase.
- All four grep tests (Task 1 x4, Task 2 x1 regex + 1 regression) and the Phase Verification block pass against the current `skills/implement/SKILL.md`.
- `git diff` confirms only the "Durable Progress" section (new, inserted before Step O1) and the two targeted additions inside O1's resumption bullets and O4's PASS branch changed; all Phase 1 (O3 4-status branches) and Phase 2 (O2 model-routing table + BASE bullet) hunks remain untouched in the working tree.
