# Phase 2: Kolaps do jednego drzewa `skills/`

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (może startować równolegle z Phase 1).

### Provides (for later phases)
- Katalog `skills/{name}/` na top-level z 16 skillami przeniesionymi z `claude/skills/` (źródło prawdy), wraz z plikami pomocniczymi (np. `debug/root-cause-tracing.md`).
- Potwierdzona (lub obalona) decyzja: Codex toleruje frontmatter `allowed-tools`/`argument-hint` i traktuje sekcje gate jako zwykły tekst — zapisana w `implementation-context.md` → `## Decisions Made`.
- Ustalona konwencja host-agnostyczności: body skilli neutralne, różnice per harness → `references/{harness}-tools.md` (mechanizm rozszerzalności na nowe harnessy). Zapisana w context jako zasada wiążąca kolejne fazy.
- `claude/skills/` nadal istnieje (usunięcie w Phase 6) — tu tylko kopia/mv źródła.

## Read Scope
- `claude/skills/**` (źródło prawdy)
- `codex/skills/**` (do diffa: co Codex miał inaczej)
- `scripts/diff-skills.sh` (żeby zrozumieć oczekiwany drift)
- `vendor/superpowers/skills/using-superpowers/references/` (wzorzec references/ obry)

## Write Scope
- `skills/**`

## Objective
Utworzyć jedno kanoniczne drzewo `skills/` z zawartości `claude/skills/`. Rozstrzygnąć, jak Claude-only elementy (frontmatter, sekcje gate wywołujące agentów) współistnieją w jednym pliku serwowanym obu harnessom. Prescribed approach: pojedyncze body, Codex ignoruje to czego nie zna. Zwalidować to założenie PRZED masową przenosiną.

## Tasks

### Task 1: Pre-flight — walidacja tolerancji Codex (walidacja, nie hazard)
**Status:** completed
**Traces to:** none (infrastructure task)

**Precedens obry (obniża ryzyko):** obra/superpowers utrzymuje jedno drzewo `skills/` serwowane Claude + Codex + 6 innych harnessów. Body są host-agnostyczne; różnice per harness idą do `references/{harness}-tools.md` czytanych warunkowo. obra ma **zero** zarejestrowanych agentów — subagenty są generyczne (kontroler czyta szablon promptu i dispatchuje). Wasze review gates używają zarejestrowanych typów agentów (`Agent(subagent_type="absolutpowers:review-tasks")`) — to Claude-only; na Codex sekcje gate są inertną prozą, co dokładnie realizuje "Codex runs without gates" (już w CLAUDE.md). Czyli prescribed approach (jedno body, Claude-only sekcje martwe na Codex) to sprawdzony wzorzec obry, nie eksperyment. Pre-flight = potwierdzenie, nie odkrywanie.

**Requirements:**
- Zdiffować parę odpowiadających plików claude vs codex dla skilla z gate'em: `diff claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md`
- Skatalogować RÓŻNICE: które sekcje/frontmatter są Claude-only (spodziewane: `allowed-tools`, `argument-hint`, sekcja "Review Gate", wywołania `Agent(subagent_type=...)`)
- Potwierdzić, że Codex toleruje nieznany frontmatter (`allowed-tools`/`argument-hint`) i traktuje prozę wywołującą agentów jako zwykły tekst — porównać z tym, jak obra trzyma Claude-only treść w jednym body (`vendor/superpowers/skills/*/SKILL.md`) bez osobnej wersji Codex
- **Decyzja (spodziewana: potwierdzenie):** jeśli Codex toleruje → potwierdź jedno body. Mało prawdopodobny wyjątek: jeśli konkretny frontmatter CHOKE'uje parser Codeksa → przenieś tylko ten klucz do `references/`, nie porzucaj całego kolapsu
- Zapisać werdykt w `implementation-context.md` → `## Decisions Made`

**Tests:**
- Diff claude↔codex dla ≥2 skilli udokumentowany (lista Claude-only elementów)
- Werdykt tolerancji Codex zapisany w context z uzasadnieniem + odniesieniem do wzorca obry
- Jeśli jakiś klucz frontmatter wymaga przeniesienia do references/ → phase file zaktualizowany przed Task 2

### Task 2: Przenieść skille claude/skills → skills/
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Dla każdego z 16 skilli: `git mv claude/skills/{name} skills/{name}` (zachowanie historii)
- Przenieść WSZYSTKIE pliki pomocnicze (np. `debug/condition-based-waiting-example.ts`, `debug/root-cause-tracing.md`, `debug/defense-in-depth.md`)
- NIE modyfikować treści SKILL.md w tej fazie (fuzje to Faza 2/3 planu; tu czysta przenosina)
- Jeśli Task 1 wybrał wzorzec references/: wyekstrahować Claude-only sekcje do `skills/{name}/references/claude-gates.md` i wstawić warunkowy wskaźnik w body (tylko dla dotkniętych skilli)

**Tests:**
- `skills/` zawiera 16 katalogów skilli
- Każdy `skills/{name}/SKILL.md` istnieje i ma poprawny frontmatter (`head -1` == `---`)
- Pliki pomocnicze debug przeniesione (`ls skills/debug/` = 4 pliki + SKILL.md)
- `git log --follow skills/debug/SKILL.md` pokazuje historię sprzed przenosin

### Task 3: Weryfikacja parytetu treści z codex/
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Dla każdego skilla porównać nowe `skills/{name}/SKILL.md` z `codex/skills/{name}/SKILL.md` — potwierdzić, że jedyne różnice to spodziewany Claude-only drift z Task 1 (nic merytorycznego nie ginie dla Codex)
- Odnotować w context każdy przypadek, gdzie Codex miał treść NIEOBECNĄ w claude/ (jeśli istnieje — wtedy trzeba ją zmergować do jednego body, nie zgubić)
- codex/skills/tech-lead-advisor vs claude/agents/tech-lead-agent: odnotować rozjazd nazw (agent Claude-only; Codex miał to jako skill) — do rozstrzygnięcia w P3/P6

**Tests:**
- Dla każdego skilla: różnice claude↔codex sklasyfikowane jako "spodziewany drift" albo "treść do zmergowania"
- Żadna treść unikalna dla Codex nie zgubiona (lista w context lub potwierdzenie "brak")

## Phase Verification
Run:
- `ls skills/ | wc -l` (oczekiwane: 16)
- `for f in skills/*/SKILL.md; do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done` (brak outputu = OK)
- `git log --follow --oneline skills/feature-discuss/SKILL.md | head` (historia zachowana)

## Completion Criteria
- All phase tasks are completed.
- Decyzja tolerancji Codex zapisana; jeśli BLOCKED — faza zatrzymana, eskalacja.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany (decyzja + ewentualna treść do zmergowania).
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- **Task 1 werdykt: POTWIERDZONE — jedno body, `claude/` = źródło prawdy, brak przenoszenia frontmatter do `references/`.** Zdiffowano `generate-tasks` i `review` (oba z gate'em). Claude-only drift = dokładnie: (a) frontmatter `allowed-tools` + `argument-hint`; (b) cała sekcja `## Review Gate` z wywołaniami `Agent(subagent_type="review-tasks")`; (c) `review` — notka "To review vs triada-review". To pokrywa się z udokumentowanym oczekiwaniem `scripts/diff-skills.sh` ("Claude-specific frontmatter and agent-loop sections"). Wzorzec obry potwierdza tolerancję: `vendor/superpowers/skills/using-superpowers/SKILL.md` trzyma Claude-only treść w jednym host-agnostycznym body serwowanym 8 harnessom (Codex, Pi, antigravity, ...), różnice per harness w `references/{harness}-tools.md`. obra ma zero zarejestrowanych agentów; nasze gate'y używają zarejestrowanych typów → na Codex sekcje gate to inertna proza ("Codex runs without gates"). Żaden klucz frontmatter nie CHOKE'uje parsera → Task 2 to czysty `git mv` bez ekstrakcji do `references/`.
- **Task 2:** `git mv claude/skills/{name} skills/{name}` dla wszystkich 16 skilli. Git wykrył je jako rename (R) → historia zachowana (`git log --follow` sięga `4b02d79` initial release). Pliki pomocnicze `debug/` (4: condition-based-waiting.md, condition-based-waiting-example.ts, defense-in-depth.md, root-cause-tracing.md) przeniesione automatycznie wraz z katalogiem. Treść SKILL.md niezmieniona (fuzje = Faza 2/3 planu). `claude/skills/` pozostaje pustym katalogiem (git nie trackuje pustych dirów) — usuwany razem z `claude/` w Phase 6; diffing parytetu w kolejnych fazach odbywa się względem `codex/skills/` (istnieje do Phase 6).
- **Task 3 parytet:** przenosina to czyste `git mv`, więc `skills/{name}/SKILL.md` jest bajtowo identyczny z byłym `claude/skills/{name}/SKILL.md`. Parytet vs Codex sklasyfikowany jako spodziewany Claude-only drift (Task 1). Zeskanowano wszystkie 16 skilli: linie pozornie "codex-only" (implement, feature-discuss, problem-discuss) to relokowana/przeredagowana treść obecna w claude, NIE unikalna treść featurowa. Jedyny wyjątek: `implement` — Codex ma inline kroki "Read the referenced phase file completely" (adaptacja modelu sekwencyjnego zamiast delegacji do `implementation-worker`); semantycznie równoważne, nic nie ginie. **Żadna unikalna treść Codeksowa do zmergowania.** Rozjazd nazw: `codex/skills/tech-lead-advisor` (skill) vs `claude/agents/tech-lead-agent` (agent) — do rozstrzygnięcia w P3/P6.
