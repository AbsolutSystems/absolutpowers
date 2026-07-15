# Phase 4: Kopiowanie + przycinanie zvendorowanych skilli obry

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `vendor/superpowers/` klon z przypiętym SHA (Phase 1 Provides).
- `skills/` istnieje jako drzewo docelowe (Phase 2 Provides).

### Provides (for later phases)
- `skills/vendored/{name}/` dla skilli bez fuzji: `using-git-worktrees`, `systematic-debugging`, `verification-before-completion`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `executing-plans`, `subagent-driven-development` (+ `implementer-prompt.md`, `task-reviewer-prompt.md`, `scripts/review-package`, `scripts/task-brief`, `scripts/sdd-workspace`).
- Poddrzewo visual companion pod feature-discuss: `visual-companion.md` + `scripts/{server.cjs,helper.js,frame-template.html,start-server.sh,stop-server.sh}` z telemetrią zneutralizowaną.
- `VENDORED.md` tabela wypełniona (per skill: ścieżka, SHA, lokalne modyfikacje).

### NIE w tej fazie
- `brainstorming` i `writing-plans` (dawcy sekcji do fuzji — Faza 2/3 planu, osobny feature-discuss).
- Integracja mechanizmów sdd w `implement` (Faza 2 planu).
- `using-superpowers` dispatcher (nie vendorowany — tylko mechanizm hooka, Phase 5).

## Read Scope
- `vendor/superpowers/skills/**`
- `vendor/superpowers/skills/subagent-driven-development/scripts/**`
- `vendor/superpowers/skills/brainstorming/{visual-companion.md,scripts/**}`
- `plan-migracji-hybrydowej-superpowers.md` (Faza 2 lista + Faza 1.3 neutralizacja telemetrii)

## Write Scope
- `skills/vendored/**`
- `skills/feature-discuss/visual-companion.md`, `skills/feature-discuss/companion-scripts/**` (poddrzewo companiona)
- `VENDORED.md`

## Objective
Skopiować 7 skilli obry bez fuzji + poddrzewo companiona do drzewa `skills/`, przyciąć nieużywane harnessy, zneutralizować telemetrię companiona, zachować notę MIT. Każde cięcie odnotowane w `VENDORED.md`.

## Tasks

### Task 1: Skopiować skille bez fuzji + przyciąć harnessy
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Skopiować z `vendor/superpowers/skills/` do `skills/vendored/{name}/`: `using-git-worktrees`, `systematic-debugging`, `verification-before-completion`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `executing-plans`, `subagent-driven-development`
- Dla `subagent-driven-development` skopiować też: `implementer-prompt.md`, `task-reviewer-prompt.md`, `scripts/review-package`, `scripts/task-brief`, `scripts/sdd-workspace`
- Przyciąć sekcje harnessów nieużywanych (Cursor, Kimi, Antigravity, Gemini) z SKILL.md i references/ — zostawić Claude Code + Codex + **Pi** (Pi jest wspieranym harnessem, Phase 7; NIE przycinać sekcji/references Pi ze zvendorowanych skilli)
- Dodać notkę MIT na górze każdego zvendorowanego SKILL.md (jedna linia: źródło + `LICENSE-VENDORED`)
- Odnotować w `VENDORED.md` każde cięcie (per skill, jedna linia na modyfikację)

**Tests:**
- `skills/vendored/` ma 7 katalogów
- `skills/vendored/subagent-driven-development/scripts/` ma `review-package`, `task-brief`, `sdd-workspace`
- Żaden zvendorowany SKILL.md nie zawiera sekcji Cursor/Kimi/Antigravity/Gemini (sekcje Pi/Codex ZOSTAJĄ)
- Każdy zvendorowany SKILL.md ma notkę MIT
- `VENDORED.md` tabela ma wiersz per zvendorowany skill z listą modyfikacji

### Task 2: Vendorować poddrzewo visual companion (telemetria zneutralizowana)
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Skopiować `vendor/superpowers/skills/brainstorming/visual-companion.md` → `skills/feature-discuss/visual-companion.md`
- Skopiować `scripts/{server.cjs,helper.js,frame-template.html,start-server.sh,stop-server.sh}` → `skills/feature-discuss/companion-scripts/`
- **Zneutralizować telemetrię** w `server.cjs`: albo hardcode `SUPERPOWERS_TELEMETRY_DISABLED = true`, albo usunąć stałą `SUPERPOWERS_BRAND_IMAGE_URL` i gałąź logo (ok. linie 106, 244-251 w źródle) — logo staje się lokalnym tekstem, żaden zewnętrzny GET
- Zaktualizować ścieżki w `visual-companion.md` odnoszące się do `scripts/` → `companion-scripts/`
- Dodać notkę MIT; odnotować w `VENDORED.md`
- NIE wire'ować companiona do feature-discuss SKILL.md w tej fazie (to fuzja — Faza 2/3 planu); tu tylko złożyć pliki obok

**Tests:**
- `grep -n 'primeradiant.com' skills/feature-discuss/companion-scripts/server.cjs` = brak trafień (albo za martwą flagą)
- `skills/feature-discuss/companion-scripts/` ma 5 plików
- `visual-companion.md` nie referuje ścieżki `scripts/` (tylko `companion-scripts/`)
- `VENDORED.md` ma wiersz companiona z notatką "telemetria zneutralizowana"

## Phase Verification
Run:
- `ls skills/vendored/ | wc -l` (oczekiwane: 7)
- `test -x skills/vendored/subagent-driven-development/scripts/task-brief || echo "task-brief missing"`
- `grep -rl 'primeradiant.com' skills/feature-discuss/ && echo "TELEMETRY LEFT" || echo "telemetry clean"`
- `grep -c '|' VENDORED.md` (tabela wypełniona — >8 wierszy)

## Completion Criteria
- All phase tasks are completed.
- Wszystkie zvendorowane pliki mają notę MIT; cięcia w VENDORED.md.
- Telemetria companiona zneutralizowana.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany o listę zvendorowanych skilli.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- **Nic do przycięcia (harnessy):** grep-em zweryfikowano, że żaden z 7 zvendorowanych skilli (i ich helper-plików) nie zawiera sekcji Cursor/Kimi/Antigravity/Gemini w źródle — te sekcje istnieją wyłącznie w `using-superpowers/` (dispatcher, świadomie niewendorowany). Task 1 "przycinania" polegał więc na weryfikacji nieobecności, nie na realnym cięciu. Odnotowane w `VENDORED.md` jedną zbiorczą uwagą.
- **MIT nota:** dodana jako linia po frontmatterze każdego zvendorowanego `SKILL.md` (i na górze `visual-companion.md`, który nie ma frontmatteru) — format: źródło + SHA (skrócone 7 znaków) + link do `LICENSE-VENDORED` (ścieżka relatywna, policzona per głębokość pliku).
- **Cross-referencje `superpowers:*` pozostawione as-is** w `executing-plans`, `subagent-driven-development` **i `systematic-debugging`** (np. `superpowers:writing-plans`, `superpowers:finishing-a-development-branch`, `../using-superpowers/references/`, `superpowers:test-driven-development`, `superpowers:verification-before-completion`) — część dawców (writing-plans, using-superpowers, test-driven-development) nie jest vendorowana w tej fazie; przepisanie tych odniesień to integracja z `implement`/`generate-tasks`, czyli Faza 2/3 planu migracji, poza scope tej fazy. Odnotowane per-skill w `VENDORED.md` (pełny inwentarz po korekcie post-phase-review). **Uwaga o kolizji nazw:** `superpowers:verification-before-completion` w `systematic-debugging/SKILL.md` odwołuje się do nieistniejącego namespace `superpowers:`, mimo że lokalny `skills/vendored/verification-before-completion/` już istnieje — nie zostało to automatycznie zaaliasowane, wymaga jawnej decyzji w fazie fuzji.
- **Telemetria companiona — usunięcie, nie tylko env-gate:** w `server.cjs` usunięto stałą `SUPERPOWERS_BRAND_IMAGE_URL` i gałąź `<img>` w `brandMarkup()` (zamiast tylko hardkodować flagę) — silniejsza gwarancja niż "opt-out": żaden kod path nie może wykonać zewnętrznego GET, niezależnie od zmiennych środowiskowych. `SUPERPOWERS_TELEMETRY_DISABLED` zahardkodowana na `true` dla przejrzystości (funkcja `isTruthyEnv()` i tablica `TELEMETRY_DISABLE_ENV_VARS` usunięte jako martwy kod tego samego cięcia). Branding uproszczony do lokalnego tekstu `AbsolutPowers (vendored companion) v{version}` bez linku/obrazka.
- **Ścieżki companiona:** `scripts/` → `companion-scripts/` w `visual-companion.md` (wszystkie 8 wystąpień); `server.cjs` czyta `../../..` względem `__dirname` dla wersji z manifestu — głębokość niezmieniona (3 poziomy) mimo przenosin, bo `skills/brainstorming/scripts/` i `skills/feature-discuss/companion-scripts/` mają tę samą głębokość względem roota.
- **NIE wpięte:** companion pozostaje nieodwołany z `feature-discuss/SKILL.md` (zgodnie z "NIE w tej fazie") — świadomie zaznaczone notką w `visual-companion.md`.
