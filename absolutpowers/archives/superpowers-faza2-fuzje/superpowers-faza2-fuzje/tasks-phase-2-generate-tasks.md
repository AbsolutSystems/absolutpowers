# Tasks: Faza 2 — generate-tasks ← writing-plans (fuzja mechaniki obry)

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-2-generate-tasks.md`
- Epic context: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
- ADR (binding): `./docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md`

## Mode
orchestrated

## Project Context
**Stack:** Markdown (`SKILL.md`, `agents/*.md`, docs), JSON manifests. Plugin wieloharnessowy (Claude/Codex/Pi), jednodrzewowa architektura (`skills/{name}/SKILL.md` = single source of truth). Brak kompilacji/testów runtime — walidacja = structural grep + JSON lint + frontmatter/hook check.

**Metoda:** rewrite-to-unify — wszczepiamy mechanikę w istniejącą strukturę, NIE dopisujemy na końcu; grafty konsolidują (nie tylko dodają).

**Shared core caveat:** `skills/generate-tasks/SKILL.md` i `agents/review-tasks.md` to najczęściej reużywane pliki promptów pluginu — każde przyszłe wywołanie generate-tasks/review-tasks od nich zależy. Stąd tryb orchestrated i faza-po-fazie z gate.

**Verification commands** (repo-canonical, z CLAUDE.md):
- Frontmatter: `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done`
- JSON manifesty: `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done`
- Hook: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null`

**Shared implementation context:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/implementation-context.md`

## Global Constraints
> Wymagania obowiązujące KAŻDĄ fazę tej fuzji (spec-derived verbatim z planning + ADR). Rozłączne z constitution.md (project pryncypia) i rules.md (lint).

- **GC-1 (rewrite-to-unify):** Osadzaj mechanikę w istniejącej strukturze SKILL.md; zakaz appendu na koniec pliku, gdy miejsce jest w istniejącej sekcji. Konsoliduj, nie duplikuj.
- **GC-2 (NIE dotykać):** Zero zmian semantyki w: grep-AC / `### AC Traceability` (tokeny `AC-N`), Mode `single-file`|`orchestrated`, `## Review Gate` flow, epic subfolder handling, Test-first marker, `implementation-context.md` budget (HARD BUDGET / size limits). Grafty ROZSZERZAJĄ format zadania, nie przebudowują.
- **GC-3 (rozłączne źródła):** Global Constraints (spec-scoped) ≠ constitution.md (project-scoped) ≠ rules.md (lint). GC CYTUJE artykuł constitution (`Per Artykuł N`), NIGDY nie kopiuje treści pryncypium. Per ADR pkt 4.
- **GC-4 (dwa poziomy Interfaces, zero duplikacji):** task-level `Produces`/`Consumes` + phase-level `Context Contract → Provides` (rollup). Twarda reguła anty-dup: NIE powtarzaj w Provides sygnatur nieprzekraczających granicy fazy. Per ADR pkt 2.
- **GC-5 (dyscyplina, nie szablon):** Wzmacniamy `Requirements/Tests/Example` + Test-first marker. NIE wprowadzamy rigid 5-step TDD checkbox template. Per ADR pkt 3 (split Opus-plan/Sonnet-implement).
- **GC-6 (dwujęzyczność):** Nowe sekcje merytoryczne EN; noty user-facing PL wg konwencji per sekcja.

## Phase Overview

### Phase 1: Grafty nagłówka — Global Constraints + Produces/Consumes format
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/01-header-grafts.md`
**Depends on:** none
**Write scope:** `skills/generate-tasks/SKILL.md`
**Risk:** medium

### Phase 2: Grafty treści — No Placeholders + Self-Review + wzmocnienie kompletnego kodu
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/02-body-grafts.md`
**Depends on:** Phase 1
**Write scope:** `skills/generate-tasks/SKILL.md`
**Risk:** low

### Phase 3: Rubryka gate + rejestr — review-tasks.md + VENDORED.md + planning-main.md
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/03-gate-and-registry.md`
**Depends on:** Phase 1, Phase 2
**Write scope:** `agents/review-tasks.md`, `VENDORED.md`, `absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file (`pending` → `in-progress` when a phase starts, → `completed` after phase verification and review).
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Phase 1 i Phase 2 edytują TEN SAM plik (`SKILL.md`) sekwencyjnie — brak konfliktu, bo fazy nie biegną równolegle; Phase 2 czyta stan po Phase 1 z `implementation-context.md`.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
