# Tasks: Superpowers vendoring — Faza 1 (restrukturyzacja repo + wektor vendoringu)

## Status
completed

## Source
- Planning doc: `./plan-migracji-hybrydowej-superpowers.md` (Faza 1 + Faza 1.5)

## Mode
orchestrated

## Project Context

**Co to jest:** AbsolutPowers — plugin skilli dla Claude Code + Codex + Pi. Repo trzyma dziś DWA lustrzane drzewa (`claude/`, `codex/`) synchronizowane skryptami. Faza 1 zamienia to na **jedno drzewo `skills/`** + cienkie manifesty/integracje per harness (wzorzec obra/superpowers) i buduje infrastrukturę vendoringu wybranych skilli obry. To zmiana formatu → **semver major 5.0.0**.

**Cel architektoniczny — wieloharnessowość:** przejmujemy architekturę obry (jedno host-agnostyczne drzewo + różnice per harness w `references/{harness}-tools.md` czytanych warunkowo + cienka integracja per harness). Efekt: dodanie kolejnego harnessu = nowa integracja/manifest + opcjonalny reference file, **zero edycji skilli**. Wspierane od razu: Claude Code, Codex, **Pi** (Pi używany lokalnie). Bramki review (zarejestrowane agenty) i hook to Claude-only; na Codex/Pi degradują gracefully (sekcje inertne / natywne prymitywy).

**Stack:** Markdown (SKILL.md + agent/command .md), JSON (manifesty pluginów + marketplace), Bash (hook), Python (skrypty sync — do usunięcia).

**Obecna struktura (przed):**
- `claude/skills/{name}/SKILL.md` (16 skilli) + `claude/agents/*.md` (9) + `claude/commands/*.md` (1) + `claude/.claude-plugin/plugin.json`
- `codex/skills/{name}/SKILL.md` (16) + `codex/scripts/sync_claude_to_agents.py` + `codex/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json` → wskazuje `claude/`
- `.agents/plugins/marketplace.json` → wskazuje `codex/`
- `scripts/diff-skills.sh` (detekcja driftu), `scripts/sync_claude_to_agents.py` (duplikat kopii w codex/)
- brak jakichkolwiek hooków

**Docelowa struktura (po Fazie 1):**
- `skills/{name}/SKILL.md` — jedno drzewo, źródło prawdy (host-agnostyczne body + Claude-only sekcje tolerowane/inertne na Codex/Pi)
- `skills/vendored/{name}/` — zvendorowane skille obry z notą MIT
- `references/{harness}-tools.md` — mapowanie akcji skilli na prymitywy harnessu (codex-tools.md, pi-tools.md); czytane warunkowo
- `agents/*.md`, `commands/*.md` — na top-level (Claude-only, inne harnessy ignorują)
- `hooks/` — slim hook Claude (session-start + run-hook.cmd + hooks.json) + `hooks/session-context.md` (wspólna treść wstrzykiwana, współdzielona z Pi)
- `.pi/extensions/absolutpowers.ts` — integracja Pi (rejestruje skills/, re-injekcja treści na session_start/compact)
- `AGENTS.md` → symlink do `CLAUDE.md` (bootstrap dla harnessów czytających AGENTS.md — Codex; wzorzec obry)
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` — manifesty per harness na top-level
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json` — przekierowane na root
- `VENDORED.md`, `LICENSE-VENDORED` — atrybucja MIT obry
- USUNIĘTE: `claude/`, `codex/`, oba `sync_claude_to_agents.py`, `scripts/diff-skills.sh`

**Kluczowa decyzja projektowa (P2):** przy kolapsie do jednego drzewa `claude/` jest źródłem prawdy (bogatszy — ma frontmatter `allowed-tools`/`argument-hint` i sekcje gate). Codex dostaje TEN SAM plik; sekcje gate wywołujące agentów są dla Codex no-opem ("Codex runs without gates" — już zapisane w CLAUDE.md). Założenie do walidacji w P2 pre-flight: Codex toleruje nieznany frontmatter i traktuje prozę wywołującą agentów jako zwykły tekst. Jeśli nie — BLOCKED, eskalacja do feature-discuss.

**Shared implementation context:** `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

**Verification commands (repo bez systemu budowania — bramki to walidacja strukturalna):**
- Manifesty to poprawny JSON: `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done`
- Hook emituje poprawny JSON: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null`
- Każdy SKILL.md ma frontmatter: `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done`
- Brak wiszących referencji do usuniętych ścieżek: `grep -rn 'claude/skills\|codex/skills\|sync_claude_to_agents\|diff-skills' --include='*.md' --include='*.json' . | grep -v tasks-superpowers-faza1`
- Wersje w obu manifestach zgodne: patrz Task w P8

## Phase Overview

### Phase 1: Infrastruktura vendoringu + atrybucja MIT
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/01-vendoring-infra.md`
**Depends on:** none
**Write scope:** `VENDORED.md`, `LICENSE-VENDORED`, `vendor/` (klon roboczy poza repo)
**Risk:** low

### Phase 2: Kolaps do jednego drzewa `skills/`
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/02-single-tree-skills.md`
**Depends on:** none
**Write scope:** `skills/`, `claude/skills/` (źródło mv)
**Risk:** high

### Phase 3: Top-level agents/commands + rewire manifestów i marketplace'ów
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/03-manifests-rewire.md`
**Depends on:** Phase 1, Phase 2
**Write scope:** `agents/`, `commands/`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`
**Risk:** high

### Phase 4: Kopiowanie + przycinanie zvendorowanych skilli obry
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/04-copy-vendored-skills.md`
**Depends on:** Phase 1, Phase 2
**Write scope:** `skills/vendored/`, `skills/feature-discuss/visual-companion.md`, `skills/feature-discuss/companion-scripts/`, `VENDORED.md`
**Risk:** medium

### Phase 5: Slim hook (session-start)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/05-slim-hook.md`
**Depends on:** Phase 1, Phase 3
**Write scope:** `hooks/`, `.claude-plugin/plugin.json`
**Risk:** medium

### Phase 6: Usunięcie luster i skryptów sync
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/06-remove-mirrors.md`
**Depends on:** Phase 2, Phase 3
**Write scope:** `claude/`, `codex/`, `scripts/`
**Risk:** high

### Phase 7: Wsparcie harnessu Pi
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/07-pi-harness.md`
**Depends on:** Phase 1, Phase 2, Phase 5
**Write scope:** `.pi/extensions/`, `references/pi-tools.md`, skille dispatchujące subagenty (wskaźnik warunkowy)
**Risk:** medium

### Phase 8: Bump 5.0.0 + README/docs/install
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/08-version-docs.md`
**Depends on:** Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7
**Write scope:** `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `README.md`, `CLAUDE.md`, `docs/`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/tasks-superpowers-faza1/99-final-verification.md`

## Orchestrator Notes
- Orchestrator aktualizuje statusy w tym pliku.
- Workery aktualizują tylko swój phase file i `implementation-context.md`.
- Nie oznaczaj fazy jako completed przed przejściem phase verification i `phase-review`.
- Każdy phase file ma Context Contract. Workery walidują Requires przed startem; `phase-review` sprawdza Provides na końcu.
- **Praca na plikach repo pluginu (dogfooding)** — zmiany dotyczą samego AbsolutPowers, nie target-projektu. Używaj `git mv` żeby zachować historię.
- P2 pre-flight to walidacja (nie hazard): obra utrzymuje jedno drzewo dla 8 harnessów tym samym wzorcem, więc kolaps jest odtworzeniem sprawdzonego podejścia. Jeśli konkretny klucz frontmatter CHOKE'uje Codex — przenieś ten klucz do `references/`, nie porzucaj kolapsu.
