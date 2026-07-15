# Phase 5: Wpięcie review-package w O4/O6 + agenci przyjmują package path

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Z Phase 2: Step O2 zapisuje BASE commit przed dispatchem (review-package czyta `BASE HEAD`). Reguła jawnego modelu dla phase-review/review-implementation.
- Z Phase 3: ledger `progress.md` przechowuje BASE (źródło zakresu `BASE..HEAD` dla review-package); O4 zawiera już krok append-po-PASS.
- Z Phase 4: `skills/implement/scripts/review-package` + `sdd-workspace` istnieją; sposób podania katalogu faz (`AP_TASKS_DIR`/arg) ustalony w `implementation-context.md`.

### Provides (for later phases)
- `skills/implement/SKILL.md` Step O4: uruchamia `review-package BASE HEAD` przed dispatchem `phase-review`, przekazuje ścieżkę wygenerowanego pakietu w promptcie; nie instruuje reviewera do samodzielnego `git diff`. Model phase-review skalowany do diffa.
- `skills/implement/SKILL.md` Step O6: uruchamia `review-package` przed dispatchem `review-implementation`, przekazuje package path; final gate jawnie `opus`/most-capable.
- `agents/phase-review.md`, `agents/review-implementation.md`: przyjmują ścieżkę review package jako wejście, czytają diff z pliku jednym `Read`; sekcje Input/Required Checks nie zawierają już listy komend `git diff` do samodzielnego wykonania.

## Read Scope
- `skills/implement/SKILL.md` (Steps O4, O6)
- `agents/phase-review.md`
- `agents/review-implementation.md`
- `skills/implement/scripts/review-package` (interfejs)

## Write Scope
- `skills/implement/SKILL.md` (Steps O4, O6)
- `agents/phase-review.md`
- `agents/review-implementation.md`

## Objective
Zamienić ad-hoc `git diff` w kontekście orchestratora/reviewera na plik review package: orchestrator generuje pakiet przed dispatchem bramki i przekazuje ścieżkę; agenci czytają diff z pliku jednym `Read`. Model phase-review skalowany, final gate jawnie opus.

## Tasks

### Task 1: Step O4 + O6 generują review-package i przekazują ścieżkę
**Status:** completed
**Traces to:** AC-7

**Modify:**
- `skills/implement/SKILL.md` (Step O4, Step O6)

**Description:**
Przed dispatchem `phase-review` (O4) i `review-implementation` (O6) orchestrator uruchamia `review-package BASE HEAD` (BASE z ledgera/O2, HEAD = bieżący) i podaje ścieżkę pakietu w promptcie agenta zamiast instrukcji "read git diff".

**Requirements:**
- **O4:** przed `Agent(subagent_type="phase-review", ...)` dodaj krok uruchomienia `review-package <BASE> <HEAD>` (BASE zapisany w O2/ledgerze przed dispatchem workera). Zmień prompt dispatchu: dołóż `Review package: {package-path}` i usuń poleganie na samodzielnym git diff reviewera. Model phase-review podawany jawnie, skalowany do rozmiaru/ryzyka diffa (spójne z regułą O2 z Phase 2).
- **O6:** analogicznie przed `Agent(subagent_type="review-implementation", ...)`: uruchom `review-package <BASE-brancha> <HEAD>` dla całego zakresu gałęzi, przekaż package path w promptcie. Final gate jawnie `model="opus"`.
- Zachowaj istniejący protokół re-review (O6 przekazuje poprzedni werdykt + listę poprawek) — dołóż tylko package path.
- `AP_TASKS_DIR` (lub ustalony w Phase 4 sposób) ustawiany przy wywołaniu `review-package`, by scratch trafił pod katalog faz feature'a.

**Tests:**
- `grep -q 'review-package' skills/implement/SKILL.md` (AC-7)
- Ręczny odczyt O4/O6 → oba uruchamiają review-package przed dispatchem i przekazują ścieżkę pakietu; żaden nie instruuje reviewera do `git diff` na wejściu (AC-7)
- `grep -q 'model="opus"' skills/implement/SKILL.md` w kontekście O6 final gate (AC-7 / spójność z AC-5)

**Implementation decisions / remarks:**
- O4: `review-package` call inserted before the existing `phase-review` dispatch paragraph; BASE is the O2-recorded BASE for this phase (not `HEAD~1`), HEAD is current. `AP_TASKS_DIR` set to the phase directory from Path Resolution (same directory already used by `progress.md`/`implementation-context.md`) — no new path variable introduced. `phase-review` dispatch now carries `model="<scaled-to-diff>"` (placeholder token, per the already-documented O2 rule — Step O2's table is the single source of the tiering logic, O4 just enforces "always explicit").
- O6: `review-package` call covers the whole branch range; `<branch-BASE>` is defined as the earliest ledger line's `base7`, falling back to `git merge-base HEAD main` if the ledger is empty — this reuses the ledger format fixed by Phase 3 rather than inventing a new one. Final gate dispatch (both first-pass and re-review) now literally carries `model="opus"`.
- Ledger-append bullet from Phase 3 (directly under `If VERDICT: PASS:` in O4) left untouched, only the paragraph immediately above it (the dispatch call) changed.
- Phase-verification test 3 (`! grep -q 'git diff --cached'`) forced a stylistic choice in both agent files: the "do not run your own diff" instruction had to avoid echoing the literal substring `git diff --cached` (content-blind grep), so it is phrased as "do not run your own diff/status commands against the working tree (staged, unstaged, or untracked file listings)" instead of naming the three commands verbatim. Same trick already used in Phase 4 for `.superpowers/sdd`.

### Task 2: `phase-review.md` przyjmuje package path, czyta diff z pliku
**Status:** completed
**Traces to:** AC-8

**Modify:**
- `agents/phase-review.md`

**Description:**
Sekcja Input dostaje "review package path"; Required Checks pkt 5 (obecnie lista `git diff`/`git diff --cached`/`git ls-files`) zamieniona na "read the review package file (one Read)".

**Requirements:**
- W `## Input` dodaj pozycję: ścieżka do pliku review package.
- W `## Required Checks` usuń blok komend `git diff` / `git diff --cached` / `git ls-files --others --exclude-standard` (linie ~35–40) i zastąp instrukcją: przeczytaj diff z pliku review package jednym `Read` (plik zawiera commit list + `diff --stat` + `diff -U10` dla poprawnego zakresu BASE..HEAD).
- Zachowaj resztę kryteriów (SCOPE/COMPLETENESS/TESTS/HANDOFF/CONTRACT/CORRECTNESS/GARBAGE/RULES) i format werdyktu.

**Tests:**
- `grep -Eiq 'review package' agents/phase-review.md` (AC-8)
- `! grep -q 'git diff --cached' agents/phase-review.md` → lista git diff usunięta (AC-8)
- Frontmatter nienaruszony: `head -1 agents/phase-review.md | grep -q '^---$'`

**Implementation decisions / remarks:**
- Added "the path to a review package file" to `## Input`; Required Checks item 5 replaced the `git diff`/`git diff --cached`/`git ls-files --others --exclude-standard` block with an instruction to read the package with one `Read` call. All other criteria (SCOPE/COMPLETENESS/TESTS/HANDOFF/CONTRACT/CORRECTNESS/GARBAGE/RULES), Response Format, and Rules sections unchanged.

### Task 3: `review-implementation.md` przyjmuje package path, czyta diff z pliku
**Status:** completed
**Traces to:** AC-8

**Modify:**
- `agents/review-implementation.md`

**Description:**
Analogicznie do Task 2: Input dostaje review package path; blok `git diff` (linie ~31–36) zamieniony na czytanie diffu z pliku jednym `Read`.

**Requirements:**
- W `## Input` dodaj: ścieżka do pliku review package.
- Usuń blok komend `git diff` / `git diff --cached` / `git ls-files --others --exclude-standard` i zastąp instrukcją czytania diffu z pliku review package jednym `Read`.
- Zachowaj wszystkie kryteria review (Correctness…AC Fulfillment), severity `[BLOCKER]`/`[WARN]`, protokół re-review i format werdyktu.

**Tests:**
- `grep -Eiq 'review package' agents/review-implementation.md` (AC-8)
- `! grep -q 'git diff --cached' agents/review-implementation.md` (AC-8)
- `head -1 agents/review-implementation.md | grep -q '^---$'`

**Implementation decisions / remarks:**
- Same pattern as Task 2: `## Input` gained the review package path bullet; the diff block replaced with a one-`Read` instruction. All review criteria (1–7: Correctness…AC Fulfillment), severity rules `[BLOCKER]`/`[WARN]`, the Re-review Protocol section, and Response Format left byte-identical.

## Phase Verification
Run:
```bash
grep -q 'review-package' skills/implement/SKILL.md
grep -Eiq 'review package' agents/phase-review.md && grep -Eiq 'review package' agents/review-implementation.md
! grep -q 'git diff --cached' agents/phase-review.md && ! grep -q 'git diff --cached' agents/review-implementation.md
head -1 agents/phase-review.md | grep -q '^---$' && head -1 agents/review-implementation.md | grep -q '^---$'
```

## Completion Criteria
- O4/O6 generują review-package przed dispatchem bramek i przekazują ścieżkę; brak instrukcji "read git diff" na wejściu reviewera.
- Final gate w O6 jawnie opus; phase-review model skalowany.
- Oba agenty przyjmują package path i czytają diff z pliku; listy `git diff` usunięte.
- Protokół re-review i kryteria review zachowane; frontmattery nienaruszone.
- `implementation-context.md` zaktualizowany.
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- `AP_TASKS_DIR` reused verbatim from Phase 4's contract (the phase directory from Path Resolution) — no new variable name introduced at the O4/O6 call sites, keeping the fork's env-var contract stable across the SKILL.md text.
- Phase Verification block run and passed after fixing one grep collision: the negative-instruction prose in both agent files initially still contained the literal substring `git diff --cached` (inside "do not run..." wording), which the content-blind `! grep -q` test flags as if the old block were still present. Rephrased to avoid echoing the exact command strings, same technique Phase 4 used for `.superpowers/sdd`.
- No other in-flight SKILL.md sections (O1–O3, O5, O5.5, Durable Progress) touched; confirmed via file diff that only the O4/O6 hunks changed.
