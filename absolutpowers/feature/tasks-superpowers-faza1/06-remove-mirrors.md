# Phase 6: Usunięcie luster i skryptów sync

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/` kompletne z zawartością claude/skills (Phase 2 Provides).
- `agents/`, `commands/`, manifesty na root, marketplace'y przepięte (Phase 3 Provides).

### Provides (for later phases)
- Usunięte `claude/`, `codex/`, oba `sync_claude_to_agents.py`, `scripts/diff-skills.sh`.
- Repo bez luster i bez martwej infrastruktury sync.

## Read Scope
- `claude/**`, `codex/**` (potwierdzenie, że nic unikalnego nie zostało)
- `scripts/**`
- Wynik Phase 2 Task 3 (lista treści unikalnej dla Codex, jeśli była)

## Write Scope
- `claude/**` (usunięcie)
- `codex/**` (usunięcie)
- `scripts/**` (usunięcie sync + diff)
- `CLAUDE.md` (minimalne odkłamanie martwych ścieżek w Task 3; pełny przepis w Phase 8)

## Objective
Usunąć lustrzane drzewa i skrypty synchronizacji — teraz redundantne wobec jednego drzewa `skills/`. To nieodwracalny krok (git zachowa historię), więc dopiero po potwierdzeniu, że P2/P3 przeniosły wszystko.

## Tasks

### Task 1: Potwierdzić brak sierot przed usunięciem
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Potwierdzić z contextu Phase 2 Task 3: żadna treść unikalna dla `codex/skills/` nie zostanie zgubiona (albo już zmergowana do `skills/`)
- Rozstrzygnąć `codex/skills/tech-lead-advisor`: odpowiednik to `agents/tech-lead-agent.md` (Claude) — potwierdzić że funkcja żyje w drzewie po kolapsie (agent Claude-only; Codex traci ten skill, co jest OK jeśli był tylko cieniem agenta — udokumentować decyzję)
- `grep -rn` w `skills/`, `agents/`, `commands/`, manifestach za ścieżkami `claude/` i `codex/` — muszą być czyste PRZED usunięciem

**Tests:**
- Brak referencji `claude/`/`codex/` w przeniesionych plikach
- Decyzja o `tech-lead-advisor` udokumentowana w context
- Potwierdzenie "brak sierot" zapisane w context

### Task 2: Usunąć lustra i skrypty
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `git rm -r claude/ codex/`
- `git rm scripts/sync_claude_to_agents.py scripts/diff-skills.sh`
- (codex/scripts/sync_claude_to_agents.py znika razem z `codex/`)
- Jeśli `scripts/` staje się pusty — usunąć katalog; jeśli zostają inne skrypty — zostawić
- NIE ruszać `scripts/sync_claude_to_agents.py` funkcjonalności w target-projektach: to był helper CLAUDE.md→AGENTS.md — jeśli nadal potrzebny jako narzędzie, przenieść do dokumentacji zamiast kasować (rozstrzygnąć w Task 1)

**Tests:**
- `test ! -d claude && test ! -d codex && echo "mirrors gone"`
- `test ! -f scripts/diff-skills.sh && echo "diff-skills gone"`
- `git status` pokazuje usunięcia jako staged

### Task 3: Wyczyścić referencje w dokumentacji projektu
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Zaktualizować `CLAUDE.md` sekcje opisujące dwudrzewową strukturę i skrypty sync (Repository Layout, Cross-Platform Editing Rules, Key Development Commands) — dopasować do jednego drzewa (pełny przepis README/CLAUDE w P8; tu minimalne odkłamanie martwych ścieżek żeby verification przeszło)
- `grep -rn 'diff-skills\|sync_claude_to_agents\|claude/skills\|codex/skills'` w `*.md`/`*.json` (poza tasks-superpowers-faza1) = brak trafień

**Tests:**
- `grep -rn 'diff-skills\|sync_claude_to_agents' --include='*.md' --include='*.json' . | grep -v tasks-superpowers-faza1` = brak trafień
- `grep -rn 'claude/skills\|codex/skills' --include='*.md' --include='*.json' . | grep -v tasks-superpowers-faza1` = brak trafień

## Phase Verification
Run:
- `test ! -d claude && test ! -d codex && echo "mirrors removed"`
- `grep -rn 'claude/skills\|codex/skills\|sync_claude_to_agents\|diff-skills' --include='*.md' --include='*.json' . | grep -v 'tasks-superpowers-faza1' || echo "no stale refs"`
- `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD $f"; done`

## Completion Criteria
- All phase tasks are completed.
- Żadna treść unikalna dla Codex nie zgubiona (potwierdzone przed usunięciem).
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany o decyzję tech-lead-advisor + potwierdzenie braku sierot.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks

**tech-lead-advisor / tech-lead-agent — rozstrzygnięte:** tech-lead zostaje jako
**agent Claude-only** (`agents/tech-lead-agent.md`, top-level po P3). Codeksowy skill
`codex/skills/tech-lead-advisor` był cieniem tego agenta (Codex nie ma subagentów, więc
funkcję "tech lead advisor" eksponował jako skill). Porównanie treści: obie formy dostarczają
tę samą funkcję (strategiczne doradztwo architektoniczne). Kolaps usuwa cień — spójne z
architekturą "agenty/bramki są Claude-only i degradują gracefully na Codex/Pi" (P2/P3).
**Nazwa NIE zmieniona** → `commands/triada-review.md` (`absolutpowers:tech-lead-agent`) nie
wymaga aktualizacji. Codex traci samodzielny trigger skilla — akceptowalne per kryterium fazy
(był tylko cieniem agenta). Ewentualna promocja do skilla wieloharnessowego to osobna decyzja
projektowa poza scope Fazy 1.

**Brak sierot potwierdzony:** `git ls-files claude/` = pusty (Phase 2 przeniósł całe drzewo,
został tylko nietrackowany `.DS_Store` — usunięty `rm -rf`). Grep `claude/skills|codex/skills`
w przeniesionych plikach live (`skills/`, `agents/`, `commands/`, manifesty) = tylko legit
`.claude/skills/learned/` (ścieżka target-projektu w `skills/harvest` + `skills/try-learn-skill`,
NIE lustro). Żadna unikalna treść Codeksowa nie zaginęła (potwierdzone w P2 context + tu re-grep).

**sync_claude_to_agents.py — usunięty, nie zarchiwizowany:** helper CLAUDE.md→AGENTS.md jest
obsoletny — `AGENTS.md` to teraz symlink → `CLAUDE.md` (P3, wzorzec obry), więc sync generujący
plik jest zbędny. Żaden skill go nie wywołuje (grep: występował tylko w CLAUDE.md/README/docs jako
dokumentacja). Oba kopie (`scripts/` + `codex/scripts/`, identyczne) usunięte. `scripts/` stał się
pusty i zniknął.

**Usunięto:** `git rm -r codex/` (18 plików) + `git rm scripts/sync_claude_to_agents.py
scripts/diff-skills.sh` = 20 staged deletions. `claude/` nie miał trackowanych plików (empty po
P2 git mv) — usunięty fizycznie.

**CLAUDE.md — minimalne odkłamanie (pełny przepis w P8):** przepisano Repository Layout
(jedno drzewo `skills/` + top-level manifesty + symlink AGENTS.md), Key Development Commands
(usunięto blok `diff-skills.sh`), Cross-Platform → **Cross-Harness Editing Rules** (brak luster
do sync; różnice per harness → `references/{harness}-tools.md`), Versioning (ścieżki manifestów
na root). Pozostała stara fraza "Both skills live in both trees" / "synchronized between Claude
and Codex" w innych sekcjach — nie łamie verification-grepa, do pełnego przepisu w P8.

**Verification-grep — istotny caveat dla P8 i final-verification:** literalny broad grep
`claude/skills|codex/skills|sync_claude_to_agents|diff-skills` NIGDY nie zwróci pustego, bo trafia
w (a) legit `.claude/skills/learned/` (ścieżki target-projektu w CLAUDE.md + harvest +
try-learn-skill — poprawna treść, MUSI zostać) oraz (b) archiwum historycznych dokumentów
`absolutpowers/feature/*.md` (zapisy zamkniętych ficzerów — przepisywanie = rewizjonizm, poza scope).
Po wykluczeniu tych dwóch klas jedyne pozostałe trafienia to `README.md` + `docs/contributing.md`
— **Write Scope Phase 8** (Task 3 tej fazy jawnie deleguje pełny przepis README/docs do P8).
Realny sens bramki: brak wiszących referencji w plikach LIVE. Phase 6 owned surface (delecje +
CLAUDE.md + config + skills/agents/commands) = czysty (modulo legit `.claude/skills/learned`).
