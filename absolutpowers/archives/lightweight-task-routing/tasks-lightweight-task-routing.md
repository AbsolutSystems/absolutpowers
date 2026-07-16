# Tasks: Lightweight task routing w feature-discuss

## Status
completed

## Source
- Source doc: `./absolutpowers/feature/planning-lightweight-task-routing.md`

## Mode
orchestrated

## Project Context
**Stack:** host-agnostic Markdown skill prompts, Python 3 standard library contract tests, JSON plugin manifests

**Testing approach:**
- `tests/test_lightweight_task_routing.py` is added as the dependency-free implementation of planning step 6 (static prompt/documentation/manifest contracts); its unittest method docstrings carry literal `AC-N` markers for grep-based traceability.

**Global Constraints:**
- Rozszerzyć istniejący trójpoziomowy router bez dodawania czwartej ścieżki: zastąpić `Micro-change` przez `Lightweight task`, pozostawiając standardowy feature i epic bez zmian strukturalnych.
- Brak opcjonalnego pliku context packu nie blokuje workflow; brakujący plik jest pomijany bez błędu.
- Historyczne artefakty zachowują termin `micro-change`; statyczne sprawdzanie obejmuje wyłącznie aktywne prompty i bieżącą dokumentację.
- Jedno host-agnostyczne źródło `skills/feature-discuss/SKILL.md` utrzymuje identyczny kontrakt na wszystkich harnessach.
- Explain HTML jest generowany wyłącznie po jawnym wyborze użytkownika; `skip` ani brak odpowiedzi nie uruchamiają raportu.

**Verification commands:**
- Contract tests: `rtk proxy python3 -m unittest discover -s tests -p 'test_lightweight_task_routing.py'`
- JSON manifests: `rtk proxy bash -lc 'for f in $(git ls-files "*.json"); do python3 -m json.tool "$f" >/dev/null || exit 1; done'`
- Skill frontmatter: `rtk proxy bash -lc 'for f in $(git ls-files "skills/**/SKILL.md"); do test "$(head -n 1 "$f")" = "---" || { echo "NO FM: $f"; exit 1; }; done'`
- Session hook JSON: `rtk proxy bash -lc 'CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null'`
- AC token coverage: `rtk proxy bash -lc 'for n in $(seq 1 13); do rg -q "AC-$n" tests/test_lightweight_task_routing.py || { echo "MISSING: AC-$n"; exit 1; }; done'`

**Shared implementation context:** `./absolutpowers/feature/tasks-lightweight-task-routing/implementation-context.md`

**Reference implementations:**
- `skills/feature-discuss/SKILL.md` — current router, HARD-GATE, Phase 5/5A/5B/6, behavior rules, and terminal-state contract.
- `docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md` — prior decision reconciling fast-path execution with HARD-GATE.
- `docs/adr/2026-07-16-lightweight-task-routing.md` — accepted decision to implement and keep synchronized.
- `README.md` — public skill card, pipeline guidance, and release changelog conventions.
- `CLAUDE.md` — repository architecture and terminal-state documentation.

## Phase Overview

### Phase 1: Implement the lightweight routing contract
**Status:** completed
**File:** `./absolutpowers/feature/tasks-lightweight-task-routing/01-routing-contract.md`
**Depends on:** none
**Write scope:** `skills/feature-discuss/SKILL.md`, `tests/test_lightweight_task_routing.py`
**Risk:** medium

### Phase 2: Synchronize durable documentation and release metadata
**Status:** completed
**File:** `./absolutpowers/feature/tasks-lightweight-task-routing/02-docs-and-release.md`
**Depends on:** Phase 1
**Write scope:** `tests/test_lightweight_task_routing.py`, `README.md`, `CLAUDE.md`, `docs/adr/2026-07-16-lightweight-task-routing.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.grok-plugin/plugin.json`
**Risk:** low

## Final Verification
**Status:** completed

## Decision Review
- Report: `docs/onboarding/implementation-decisions-lightweight-task-routing-2026-07-16.html`
- Decisions: DEC-001, DEC-002, DEC-003, DEC-004, DEC-005, DEC-006, DEC-007, DEC-008, DEC-009
- Status: accepted
- Reviewed: 2026-07-16
- Notes: Użytkownik zaakceptował wszystkie zapisane decyzje implementacyjne oraz korekty po final review.
**File:** `./absolutpowers/feature/tasks-lightweight-task-routing/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file (`pending` → `in-progress` when a phase starts, → `completed` after phase verification and review).
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
