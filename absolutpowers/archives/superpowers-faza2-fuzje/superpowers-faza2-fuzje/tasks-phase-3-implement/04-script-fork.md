# Phase 4: Fork skryptu review-package + sdd-workspace + VENDORED.md

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (edycyjnie niezależna).
- Referencyjnie (read-only): `skills/vendored/subagent-driven-development/scripts/review-package` i `scripts/sdd-workspace` — źródła forka. Istniejące wpisy w `VENDORED.md` — wzór atrybucji.

### Provides (for later phases)
- `skills/implement/scripts/review-package` — forkowany skrypt (executable, `bash -n` czysty, nagłówek MIT, dir NIE `.superpowers/sdd`).
- `skills/implement/scripts/sdd-workspace` — forkowany helper (executable, `bash -n` czysty, nagłówek MIT, `dir` wskazuje scratch pod katalogiem faz feature'a, NIE `.superpowers/sdd`).
- `VENDORED.md` — wpis dokumentujący fork (ścieżka źródłowa, docelowa, delta = zmiana katalogu scratch).

## Read Scope
- `skills/vendored/subagent-driven-development/scripts/review-package`
- `skills/vendored/subagent-driven-development/scripts/sdd-workspace`
- `VENDORED.md`
- `LICENSE-VENDORED` (dla treści noty MIT)

## Write Scope
- `skills/implement/scripts/review-package` (UTWORZENIE)
- `skills/implement/scripts/sdd-workspace` (UTWORZENIE)
- `VENDORED.md`

## Objective
Sforkować dwa skrypty vendored do lokalizacji absolutpowers, zachowując atrybucję MIT i mechanizm, zmieniając wyłącznie katalog scratch z `.superpowers/sdd` na scratch pod katalogiem faz danego feature'a; udokumentować fork w `VENDORED.md`. `task-brief` świadomie NIE forkowany.

## Tasks

### Task 1: Fork `sdd-workspace` — zmiana katalogu scratch + nagłówek MIT
**Status:** completed
**Traces to:** AC-13
**Test-first:** no (skrypt bash, weryfikacja przez `bash -n` + grep; brak sensownego testu-first dla forka)

**Create:**
- `skills/implement/scripts/sdd-workspace`

**Description:**
Skopiuj `skills/vendored/subagent-driven-development/scripts/sdd-workspace`, zachowaj mechanizm (self-ignoring `.gitignore`, `pwd`), zmień `dir` z `.superpowers/sdd` na scratch pod katalogiem faz feature'a przekazany przez orchestrator.

**Requirements:**
- Zachowaj mechanizm: `mkdir -p`, `printf '*\n' > "$dir/.gitignore"` (self-ignoring), `cd "$dir" && pwd`.
- Zmień źródło `dir`: NIE `"$root/.superpowers/sdd"`. Ma wskazywać scratch pod katalogiem faz feature'a. Rozwiązanie: przyjmij katalog faz jako argument lub zmienną środowiskową, np. `dir="${AP_TASKS_DIR:?AP_TASKS_DIR required}/.scratch"`. (Katalog faz zna orchestrator z Path Resolution i podaje przy wywołaniu.)
- Dodaj na górze notę atrybucji MIT (nagłówek komentarza): pochodzenie `obra/superpowers` (MIT, Copyright (c) 2025 Jesse Vincent), plik forkowany, delta = zmiana katalogu scratch. Wzoruj się na tekście `LICENSE-VENDORED` i notach w innych vendored plikach.
- Ustaw bit wykonywalności: `chmod +x`.

**Tests:**
- `bash -n skills/implement/scripts/sdd-workspace` → exit 0
- `test -x skills/implement/scripts/sdd-workspace` → executable
- `! grep -q '.superpowers/sdd' skills/implement/scripts/sdd-workspace` → dir zmieniony (AC-13)
- `grep -Eiq 'MIT|obra/superpowers|Jesse Vincent' skills/implement/scripts/sdd-workspace` → atrybucja (AC-13)

**Implementation decisions / remarks:**
- `dir="${AP_TASKS_DIR:?AP_TASKS_DIR required}/.scratch"` — zmienna env `AP_TASKS_DIR` wymagana (bash `:?` fails fast z czytelnym komunikatem, jeśli caller jej nie ustawi), scratch to podkatalog `.scratch` pod katalogiem faz feature'a. Mechanizm `mkdir -p` / self-ignoring `.gitignore` / `cd "$dir" && pwd` skopiowany 1:1.
- Uwaga do notatki atrybucji: unikaj literalnego stringa `.superpowers/sdd` nawet w komentarzach nagłówka — Phase Verification grep (`! grep -q '.superpowers/sdd' ...`) jest ślepy na kontekst (komentarz vs kod) i złapałby też opisową wzmiankę starej ścieżki w prozie. Nagłówek opisuje deltę peryfrastycznie ("previous repo-root-relative scratch location, see VENDORED.md") zamiast cytować starą ścieżkę wprost.

### Task 2: Fork `review-package` + wpis w `VENDORED.md`
**Status:** completed
**Traces to:** AC-13, AC-14
**Test-first:** no (skrypt bash + dokumentacja; weryfikacja przez `bash -n` + grep)

**Create:**
- `skills/implement/scripts/review-package`

**Modify:**
- `VENDORED.md`

**Description:**
Skopiuj `review-package`, zachowaj mechanizm (commit list + `diff --stat` + `diff -U10`, OUTFILE per range), zmień default OUTFILE by korzystał z forkowanego `sdd-workspace` (nie `.superpowers/sdd`), dodaj notę MIT. Udokumentuj oba forki w `VENDORED.md`.

**Requirements:**
- Zachowaj mechanizm i interfejs: `review-package BASE HEAD [OUTFILE]`, walidacja `git rev-parse`, sekcje `## Commits` / `## Files changed` / `## Diff`, `git diff -U10 BASE..HEAD`.
- Domyślny OUTFILE: wywołuj forkowany `sdd-workspace` z tego samego katalogu (`skills/implement/scripts/sdd-workspace`), NIE vendored. Komentarz usage zaktualizuj: default OUTFILE pod scratch katalogu faz feature'a (nie `.superpowers/sdd`).
- Nagłówek atrybucji MIT jak w Task 1.
- `chmod +x`.
- **`VENDORED.md`** (AC-14): dodaj nowy wpis (nowa tabela lub wiersz w istniejącej sekcji dawców/forków) dokumentujący fork obu skryptów: ścieżka źródłowa (`skills/vendored/subagent-driven-development/scripts/{review-package,sdd-workspace}`), ścieżka docelowa (`skills/implement/scripts/{review-package,sdd-workspace}`), SHA `d884ae0`, delta wobec oryginału = **zmiana lokalizacji katalogu scratch** z `.superpowers/sdd` na scratch pod katalogiem faz feature'a. Analogicznie do istniejących wpisów. Zaznacz że `task-brief` świadomie NIE forkowany.

**Tests:**
- `bash -n skills/implement/scripts/review-package` → exit 0
- `test -x skills/implement/scripts/review-package`
- `! grep -q '.superpowers/sdd' skills/implement/scripts/review-package` (AC-13)
- `grep -Eiq 'MIT|Jesse Vincent' skills/implement/scripts/review-package` (AC-13)
- `grep -q 'skills/implement/scripts' VENDORED.md && grep -Eiq 'review-package' VENDORED.md` (AC-14)
- `grep -Eiq 'scratch|.superpowers/sdd' VENDORED.md` → delta katalogu opisana (AC-14)

**Implementation decisions / remarks:**
- `review-package` skopiowany bez zmian mechanizmu/interfejsu (`BASE HEAD [OUTFILE]`, walidacja `git rev-parse`, sekcje `## Commits`/`## Files changed`/`## Diff`, `git diff -U10`); domyślny OUTFILE nadal woła `"$(cd "$(dirname "$0")" && pwd)/sdd-workspace"` — nie zmieniony w treści skryptu, bo relatywne wywołanie już wskazuje na forkowaną wersję obok (`skills/implement/scripts/sdd-workspace`), która sama dziedziczy nową lokalizację scratch przez `AP_TASKS_DIR`.
- Nowa sekcja `## Forkowane skrypty (Faza 3 fuzji: implement ← subagent-driven-development)` dodana w `VENDORED.md` (tabela, wzorowana na istniejących), plus notka że `task-brief` świadomie NIE forkowany w tej fazie (poza scope — nie jest jeszcze wpięty w `implement`).

## Phase Verification
Run:
```bash
bash -n skills/implement/scripts/review-package && bash -n skills/implement/scripts/sdd-workspace
test -x skills/implement/scripts/review-package && test -x skills/implement/scripts/sdd-workspace
! grep -q '.superpowers/sdd' skills/implement/scripts/review-package
! grep -q '.superpowers/sdd' skills/implement/scripts/sdd-workspace
grep -Eiq 'MIT|Jesse Vincent' skills/implement/scripts/review-package
grep -q 'skills/implement/scripts' VENDORED.md
```

## Completion Criteria
- Oba skrypty utworzone, wykonywalne, `bash -n` czyste, z notą MIT, bez `.superpowers/sdd`.
- `review-package` używa forkowanego `sdd-workspace` dla default OUTFILE.
- `VENDORED.md` ma wpis forka (źródło, cel, delta katalogu, task-brief pominięty).
- `implementation-context.md` zaktualizowany o ścieżki skryptów i sposób podania katalogu faz (`AP_TASKS_DIR`/arg) — dla Phase 5.
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- Both scripts created at `skills/implement/scripts/{sdd-workspace,review-package}`, executable (`chmod +x`), `bash -n` clean, MIT-attributed header, no literal `.superpowers/sdd` string anywhere in either file.
- Scratch dir contract for Phase 5: caller MUST export `AP_TASKS_DIR` (absolute path to the feature's tasks directory, e.g. `./absolutpowers/feature/tasks-{slug}` or the epic-nested equivalent) before invoking `sdd-workspace` or the default-OUTFILE branch of `review-package`. Resolved scratch dir = `"$AP_TASKS_DIR/.scratch"`. Missing `AP_TASKS_DIR` fails fast via bash `:?` with a clear stderr message — no silent fallback.
- `review-package`'s explicit-OUTFILE 3-arg form is unaffected by `AP_TASKS_DIR` (caller can bypass the workspace resolver entirely by passing OUTFILE directly) — Phase 5 can choose either calling convention when wiring into O4/O6.
- `VENDORED.md` gained a new `## Forkowane skrypty (Faza 3 fuzji: implement ← subagent-driven-development)` section with a 2-row table (`sdd-workspace`, `review-package`) plus an explicit note that `task-brief` is intentionally not forked in this phase.
- Phase Verification's `! grep -q '.superpowers/sdd' ...` tests are content-blind (match comments same as code) — kept header prose peryfrastyczna (describes the old location without quoting it) to satisfy both the "documented delta" requirement and the negative grep test simultaneously.
