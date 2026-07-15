# Phase 1: Infrastruktura vendoringu + atrybucja MIT

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- Klon roboczy obry w `vendor/superpowers/` (gitignorowany, poza drzewem pluginu) z przypiętym SHA.
- `VENDORED.md` w root repo z tabelą: skill → źródłowy SHA → wersja → lokalne modyfikacje.
- `LICENSE-VENDORED` w root z pełnym tekstem MIT obry (copyright (c) 2025 Jesse Vincent).
- Realny SHA klona wpisany w `implementation-context.md` → sekcja `## Vendored SHA`.

## Read Scope
- `./plan-migracji-hybrydowej-superpowers.md` (Faza 1 kroki 1-2, Faza 1.5)

## Write Scope
- `VENDORED.md`
- `LICENSE-VENDORED`
- `.gitignore` (dodać `vendor/`)
- `vendor/superpowers/` (klon — nie commitowany)

## Objective
Zbudować odtwarzalny punkt odniesienia do vendoringu i przyszłych diffów upstreamu. Sklonować obrę na świeżo (analizowany `~/Downloads/superpowers-main` NIE ma `.git`, więc SHA jest nieznany), odczytać realny SHA, zapisać atrybucję MIT i szkielet `VENDORED.md`.

## Tasks

### Task 1: Sklonować obrę i przypiąć SHA
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `git clone https://github.com/obra/superpowers vendor/superpowers`
- `cd vendor/superpowers && git checkout` na tagu odpowiadającym v6.1.1 (zweryfikować `cat package.json | grep version` == `6.1.1`)
- Odczytać `git rev-parse HEAD`, wpisać do `implementation-context.md` → `## Vendored SHA` (zastąpić placeholder)
- Dodać `vendor/` do `.gitignore` (klon nie wchodzi do repo pluginu)

**Tests:**
- `vendor/superpowers/package.json` ma `"version": "6.1.1"`
- `git rev-parse HEAD` w klonie zwraca 40-znakowy SHA, zapisany w context
- `git status` w repo pluginu NIE pokazuje `vendor/` (gitignore działa)

### Task 2: Atrybucja MIT
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Skopiować `vendor/superpowers/LICENSE` → `LICENSE-VENDORED` w root repo (zachować dosłownie: `MIT License`, `Copyright (c) 2025 Jesse Vincent`)
- Nie modyfikować treści licencji

**Tests:**
- `LICENSE-VENDORED` zawiera `Copyright (c) 2025 Jesse Vincent`
- `LICENSE-VENDORED` zawiera pełny tekst MIT (min. akapit "Permission is hereby granted")

### Task 3: Szkielet VENDORED.md
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Utworzyć `VENDORED.md` z nagłówkiem: źródło (`obra/superpowers`), przypięty SHA (z context), wersja (6.1.1), data, link do `LICENSE-VENDORED`
- Dodać sekcję "Proces śledzenia upstreamu" (streszczenie Fazy 1.5: kwartalny `git diff <SHA>..<tag> -- skills/` ograniczony do zvendorowanych skilli, selektywne przenoszenie, aktualizacja SHA)
- Dodać pustą tabelę: `| Skill | Źródłowa ścieżka | SHA | Lokalne modyfikacje |` — wypełni ją P4

**Tests:**
- `VENDORED.md` zawiera przypięty SHA (nie placeholder)
- `VENDORED.md` ma tabelę z nagłówkami kolumn
- `VENDORED.md` ma sekcję o kwartalnym śledzeniu upstreamu

## Phase Verification
Run:
- `test -f LICENSE-VENDORED && grep -q 'Jesse Vincent' LICENSE-VENDORED && echo OK`
- `test -f VENDORED.md && grep -qE '[0-9a-f]{7,40}' VENDORED.md && echo OK`
- `git check-ignore vendor/superpowers && echo "gitignore OK"`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany o realny SHA.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Fresh `git clone https://github.com/obra/superpowers vendor/superpowers`, then `git checkout v6.1.1` (detached HEAD). `package.json` confirms `"version": "6.1.1"`.
- Real pinned SHA: `d884ae04edebef577e82ff7c4e143debd0bbec99` (matches the short-form placeholder `d884ae0` from the planning doc, now verified/confirmed rather than assumed).
- `vendor/` added to `.gitignore` (single line, appended); `git check-ignore vendor/superpowers` confirms it is ignored and `git status --short` shows no `vendor/` entries.
- `LICENSE-VENDORED` is a verbatim copy of `vendor/superpowers/LICENSE` (MIT, Copyright (c) 2025 Jesse Vincent) — no modifications.
- `VENDORED.md` created at repo root with: source/version/SHA/date header, link to `LICENSE-VENDORED`, a "Proces śledzenia upstreamu" section (quarterly `git fetch` + `git diff <SHA>..<tag> -- skills/` scoped to vendored skills only), and an empty attribution table (`Skill | Źródłowa ścieżka | SHA | Lokalne modyfikacje`) to be filled by Phase 4.
- Noted for later phases: `vendor/superpowers/CLAUDE.md` carries obra's own contributor/PR guidelines — irrelevant to the vendoring/copy process here (we are not submitting upstream PRs), recorded in `implementation-context.md` to prevent confusion in Phase 4.
