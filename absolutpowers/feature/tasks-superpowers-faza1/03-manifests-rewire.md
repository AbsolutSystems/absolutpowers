# Phase 3: Top-level agents/commands + rewire manifestów i marketplace'ów

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/` istnieje z 16 skillami (Phase 2 Provides).
- `vendor/superpowers/` klon istnieje (Phase 1 Provides) — Read Scope czyta wzorzec top-level manifestów obry.

### Provides (for later phases)
- `agents/*.md` (9) i `commands/*.md` (1) na top-level.
- `.claude-plugin/plugin.json` na top-level, wskazujący `skills/`, `agents/`, `commands/`, `hooks/`.
- `.codex-plugin/plugin.json` na top-level, wskazujący `skills/`.
- `.claude-plugin/marketplace.json` i `.agents/plugins/marketplace.json` przekierowane na root (`.`) zamiast `claude/`/`codex/`.
- `AGENTS.md` → symlink do `CLAUDE.md` (bootstrap dyscypliny dla harnessów czytających AGENTS.md, wzorzec obry).

## Read Scope
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `vendor/superpowers/.claude-plugin/`, `vendor/superpowers/.codex-plugin/` (wzorzec top-level manifestów)

## Write Scope
- `agents/**`
- `commands/**`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `AGENTS.md` (symlink)

## Objective
Przenieść Claude-only artefakty (agents, commands) na top-level i przepiąć wszystkie manifesty/marketplace na jednodrzewową strukturę root. Po tej fazie plugin ładuje się z root, nie z `claude/`/`codex/`.

## Tasks

### Task 1: Przenieść agents/ i commands/ na top-level
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `git mv claude/agents agents`
- `git mv claude/commands commands`
- Zweryfikować że agenci referują skille/ścieżki, które nadal istnieją po kolapsie (grep w agents/*.md za `claude/skills` lub `codex/`)

**Tests:**
- `agents/` ma 9 plików `.md`, `commands/` ma 1 (`triada-review.md`)
- Żaden `agents/*.md` ani `commands/*.md` nie referuje ścieżki `claude/` ani `codex/`
- `git log --follow agents/review-tasks.md` pokazuje historię

### Task 2: Przenieść i przepiąć manifesty pluginów
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `git mv claude/.claude-plugin/plugin.json .claude-plugin/plugin.json` (root `.claude-plugin/` już istnieje — trzyma marketplace.json)
- `git mv codex/.codex-plugin .codex-plugin` (utworzyć na root)
- Zaktualizować ścieżki wewnątrz obu `plugin.json`, jeśli deklarują lokalizacje `skills`/`agents`/`commands`/`hooks` (dopasować do wzorca obry: relatywnie do root pluginu)
- `.claude-plugin/plugin.json` musi deklarować (jeśli schema wymaga) `hooks` wskazujące na `hooks/hooks.json` — pole doda/potwierdzi Phase 5; tu zostaw miejsce lub minimalny wpis
- Zachować `"version"` bez zmian w tej fazie (bump w P8)

**Tests:**
- `.claude-plugin/plugin.json` i `.codex-plugin/plugin.json` istnieją na root, są poprawnym JSON (`python3 -m json.tool`)
- Żadne pole ścieżkowe nie wskazuje `claude/` ani `codex/`
- `name` w obu manifestach zgodny z poprzednim (bez regresji identyfikatora pluginu)

### Task 3: Przepiąć marketplace'y na root
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `.claude-plugin/marketplace.json`: zmienić wskaźnik pluginu z `claude/` na `.` (root)
- `.agents/plugins/marketplace.json`: zmienić wskaźnik z `codex/` na `.` (root)
- Potwierdzić spójność `name`/`source` z manifestami

**Tests:**
- Oba marketplace.json to poprawny JSON
- `grep -r 'claude/\|codex/' .claude-plugin/marketplace.json .agents/plugins/marketplace.json` = brak trafień
- Wskaźniki źródła = root (`.` lub odpowiednik schematu)

### Task 4: AGENTS.md symlink → CLAUDE.md
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Utworzyć w root `AGENTS.md` jako symlink do `CLAUDE.md`: `ln -s CLAUDE.md AGENTS.md` (wzorzec obry — harnessy czytające AGENTS.md, np. Codex, bootstrapują dyscyplinę bez hooka)
- Potwierdzić że symlink jest relatywny (przenośny), nie absolutny
- Odnotować w context, że to kanał bootstrapu dla nie-Claude harnessów (hook Claude to tylko re-injekcja po kompakcji)

**Tests:**
- `test -L AGENTS.md && readlink AGENTS.md` == `CLAUDE.md`
- `cat AGENTS.md` zwraca treść CLAUDE.md (symlink działa)

## Phase Verification
Run:
- `for f in .claude-plugin/plugin.json .codex-plugin/plugin.json .claude-plugin/marketplace.json .agents/plugins/marketplace.json; do python3 -m json.tool "$f" >/dev/null && echo "OK $f" || echo "BAD $f"; done`
- `grep -rn 'claude/\|codex/' .claude-plugin/ .codex-plugin/ .agents/ | grep -v Binary || echo "no stale paths"`
- `test -d agents && test -d commands && echo "top-level dirs OK"`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany o docelowe lokalizacje manifestów.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- **Task 1:** `git mv claude/agents agents` + `git mv claude/commands commands` → 9 agents + 1 command (`triada-review.md`) na top-level. Git wykrył wszystkie jako R100 (100% rename, historia zachowana). Jedyne trafienia `claude/` w `commands/triada-review.md` to `.claude/triada-review.agents.json` — to per-project config path w target-projekcie (nie drzewo pluginu `claude/`), zostaje bez zmian. Żaden agent/command nie referuje ścieżek drzewa pluginu `claude/`/`codex/`.
- **Test `git log --follow agents/review-tasks.md`:** pre-commit zwraca pusto, bo top-level `agents/` nigdy nie istniał w zacommitowanej historii (agenci powstali od razu w `claude/agents/` w v2.0.0), a rename jest jeszcze niezacommitowany. `git status` pokazuje R100 → historia JEST zachowana i `--follow` przejdzie po commicie. (Dla `skills/` follow działa pre-commit tylko dlatego, że top-level `skills/` istniał przed v2.0.0.) Nie commituję — commit należy do orchestratora/usera.
- **Task 2:** `plugin.json` przeniesione na root przez `git mv`. `.claude-plugin/plugin.json` NIE ma pól ścieżkowych (skills/agents/commands/hooks auto-discovery Claude Code względem root pluginu — zgodne z wzorcem obry, którego claude `plugin.json` też ich nie ma). Pole `hooks` celowo NIEobecne — obra też polega na auto-discovery `hooks/hooks.json`; doda/potwierdzi Phase 5. `.codex-plugin/plugin.json` ma `"skills": "./skills/"` — poprawne po przeniesieniu na root. Wersja `3.13.0` bez zmian (bump w P8). `name` = `absolutpowers` w obu (bez regresji).
- **Task 3:** `.claude-plugin/marketplace.json` source `./claude` → `.`; `.agents/plugins/marketplace.json` path `./codex` → `.`. Zachowany istniejący kształt schematu (claude: `source` string; codex: `{source: local, path}`), zmieniony tylko wskaźnik na root. `name`/`source` spójne z manifestami.
- **Task 4:** `ln -s CLAUDE.md AGENTS.md` — symlink relatywny (readlink == `CLAUDE.md`, bez leading `/`), przenośny. Odczyt przez symlink zwraca treść CLAUDE.md. To kanał bootstrapu dyscypliny dla harnessów czytających AGENTS.md (Codex) — hook Claude to tylko re-injekcja po kompakcji. Dodany do git (`git add`).
