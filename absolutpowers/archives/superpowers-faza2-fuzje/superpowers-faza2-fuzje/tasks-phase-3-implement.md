# Tasks: Faza 3 — implement ← subagent-driven-development (4 wszczepy)

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-3-implement.md`
- Epic context: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`

## Mode
orchestrated

## Project Context

**Stack:** Markdown skill/agent prompts (`skills/*/SKILL.md`, `agents/*.md`), Bash scripts, JSON manifests. Multi-harness plugin (Claude/Codex/Pi). No compiled runtime.

**Struktura dotknięta:**
- `skills/implement/SKILL.md` — orchestrator skill (Steps O1–O6, Single-File Process)
- `agents/implementation-worker.md` — worker subagent (PHASE_RESULT output)
- `agents/phase-review.md`, `agents/review-implementation.md` — review gate subagents
- `skills/implement/scripts/` — forked `review-package` + `sdd-workspace` (nowe)
- `VENDORED.md` — atrybucja MIT forka
- `CLAUDE.md`, `README.md`, `docs/` — sync opisów

**Weryfikacja — grep-against-artifact (KLUCZOWE):**
Ta faza fuzuje mechanikę skilla, nie feature aplikacyjny. Zgodnie z notą metodologiczną planning doc (linia 136), "zachowanie" = treść plików pluginu, więc **wszystkie AC są grep-weryfikowalne względem tych plików, nie względem runtime**. Konsekwencje wiążące dla `implement`/`review`:
- Konwencja tokenu `AC-N` w źródłach testów **NIE obowiązuje** — nie ma runtime test suite ani plików testowych. Nie twórz sztucznych testów jednostkowych dla tych zmian.
- "Tests" w każdym tasku = konkretna komenda `grep`/`bash -n` weryfikująca obecność (lub nieobecność) treści w pliku docelowym.
- Final verification = zestaw grepów + walidacja manifestów/hooka/frontmatteru.

**Verification commands (kanoniczne, z CLAUDE.md):**
```bash
# manifesty JSON
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
# hook SessionStart emituje poprawny JSON
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null
# każdy SKILL.md ma frontmatter
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done
# skrypty parsują się i są wykonywalne
bash -n skills/implement/scripts/review-package && bash -n skills/implement/scripts/sdd-workspace
```

**Shared implementation context:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

**Reference implementations:**
- `skills/vendored/subagent-driven-development/scripts/review-package` + `sdd-workspace` — źródło forka (MIT)
- `skills/vendored/subagent-driven-development/SKILL.md` — dawca mechaniki 4 statusów / drabiny / ledgera
- Istniejące wpisy w `VENDORED.md` (tabele) — wzór wpisu atrybucji

## Phase Overview

### Phase 1: Protokół 4 statusów (worker + O3 handling)
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/01-status-protocol.md`
**Depends on:** none
**Write scope:** `agents/implementation-worker.md`, `skills/implement/SKILL.md` (Step O3, O4 nagłówek dispatchu)
**Risk:** medium

### Phase 2: Model routing O2 + BASE commit tracking
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/02-model-routing.md`
**Depends on:** none
**Write scope:** `skills/implement/SKILL.md` (Step O2)
**Risk:** medium

### Phase 3: Ledger — Durable Progress
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/03-ledger.md`
**Depends on:** Phase 2
**Write scope:** `skills/implement/SKILL.md` (nowa sekcja Durable Progress + wpięcie w O1, O4)
**Risk:** medium

### Phase 4: Fork skryptu review-package + sdd-workspace + VENDORED.md
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/04-script-fork.md`
**Depends on:** none
**Write scope:** `skills/implement/scripts/review-package`, `skills/implement/scripts/sdd-workspace`, `VENDORED.md`
**Risk:** medium

### Phase 5: Wpięcie review-package w O4/O6 + agenci przyjmują package path
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/05-review-package-wiring.md`
**Depends on:** Phase 2, Phase 3, Phase 4
**Write scope:** `skills/implement/SKILL.md` (Step O4, O6), `agents/phase-review.md`, `agents/review-implementation.md`
**Risk:** medium

### Phase 6: Ograniczenie zasięgu do orchestrated + czystka task-brief
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/06-scoping-cleanup.md`
**Depends on:** Phase 1, Phase 2, Phase 3, Phase 5
**Write scope:** `skills/implement/SKILL.md` (Single-File Process, Mode Detection)
**Risk:** low

### Phase 7: Doc sync + bump wersji
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/07-doc-sync.md`
**Depends on:** Phase 1, Phase 2, Phase 3, Phase 5
**Write scope:** `CLAUDE.md`, `README.md`, `docs/`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/99-final-verification.md`

## Orchestrator Notes
- Orchestrator aktualizuje statusy w tym pliku.
- Workerzy aktualizują tylko swój phase file i `implementation-context.md`.
- Nie oznaczaj fazy `completed` zanim phase verification i `phase-review` przejdą.
- Każdy phase file ma Context Contract. Worker waliduje Requires przed startem; `phase-review` sprawdza Provides na końcu.
- **Kolejność edycji `skills/implement/SKILL.md`:** wiele faz edytuje ten sam plik w rozłącznych sekcjach (O2 → Phase 2, O3 → Phase 1, ledger/O1/O4-append → Phase 3, O4/O6 → Phase 5, Single-File → Phase 6). Faz nie uruchamiaj równolegle — sekwencyjnie, każda po `phase-review` PASS poprzedniej z jej `Depends on`.
- **Ta faza jest częścią epica** — cross-phase dependencies są w Context Contract (Requires) każdej fazy oraz w `planning-main.md`; traktuj je jako kontrakt, nie brakujący kontekst.
