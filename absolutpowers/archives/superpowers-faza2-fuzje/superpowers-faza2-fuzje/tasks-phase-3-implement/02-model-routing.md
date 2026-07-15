# Phase 2: Model routing O2 + BASE commit tracking

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (edycyjnie niezależna od Phase 1).

### Provides (for later phases)
- `skills/implement/SKILL.md` Step O2: tabela/reguła routingu z ≥3 jawnie nazwanymi tierami implementera (transkrypcja/najtańszy, standard, most-capable), jawny model dla `phase-review` (skalowany) i jawnie `opus`/most-capable dla `review-implementation`.
- Reguła "always explicit": dispatch bez jawnego parametru modelu = błąd; dziedziczenie sesji NIE jest dopuszczalnym skrótem dla żadnej roli.
- Reguła fallback: phase file bez kompletnego kodu → tier standard (nie najtańszy).
- Step O2: orchestrator zapisuje BASE commit **przed** dispatchem workera (haczyk dla ledgera i review-package w Phase 3/5).

## Read Scope
- `skills/implement/SKILL.md` (Step O2, linie ~197–218)

## Write Scope
- `skills/implement/SKILL.md` (Step O2)

## Objective
Rozszerzyć routing modelu w Step O2 z obecnego (tylko implementer po Risk: high→opus / reszta→sonnet) na pełną tabelę per rola z regułą "always explicit" i fallbackiem tieru transkrypcji, oraz dodać zapis BASE commit przed dispatchem.

## Tasks

### Task 1: Rozszerzona tabela routingu modelu per rola + reguły
**Status:** completed
**Traces to:** AC-5, AC-11, AC-12

**Modify:**
- `skills/implement/SKILL.md` (sekcja "Model routing by risk" w Step O2)

**Description:**
Zastąp obecny dwuwierszowy routing pełną tabelą per rola, z jawnie nazwanymi tierami i regułami always-explicit + transcription-fallback.

**Requirements:**
- Implementer — ≥3 jawne tiery (AC-5):
  - **transkrypcja / najtańszy** (np. `haiku`) — gdy phase file zawiera **kompletny, gotowy do przepisania kod** (synergia z Fazą 2: generate-tasks produkuje kompletny kod w krokach → implementacja = transkrypcja + testy).
  - **standard** (`sonnet`) — integracja/wieloplikowość/pattern-matching, `Risk: low|medium`.
  - **most-capable** (`opus`) — `Risk: high` (security, migracje, shared core), design judgment.
- **phase-review** — model jawnie podany, skalowany do rozmiaru/ryzyka diffa (mały mechaniczny diff nie wymaga opus; subtelna współbieżność wymaga). (AC-5)
- **review-implementation** (final gate) — jawnie `opus`/most-capable, zawsze. (AC-5)
- Reguła fallback (AC-11): gdy phase file NIE zawiera kompletnego, gotowego do przepisania kodu (przypadek wątpliwy) → routing wskazuje tier **standard**, nie domyślnie najtańszy.
- Reguła always-explicit (AC-12): dispatch subagenta bez jawnie podanego parametru `model` jest **błędem** względem tej reguły; dziedziczenie modelu sesji NIE jest opisane jako dopuszczalny skrót dla żadnej z ról (implementer / phase-review / review-implementation). Dodaj notę "turn count beats token price" — mid-tier jako podłoga dla reviewerów i implementerów pracujących z prozą.
- Zachowaj spójność z dispatchami w O2 body (`Agent(subagent_type="implementation-worker", model=...)`) — każdy przykład dispatchu ma jawny `model=`.

**Tests:**
- `grep -Eiq 'transkrypc|transcription' skills/implement/SKILL.md` i obecność haiku/sonnet/opus w O2: `grep -q 'haiku' skills/implement/SKILL.md && grep -q 'opus' skills/implement/SKILL.md` (AC-5)
- `grep -q 'phase-review' skills/implement/SKILL.md && grep -Eiq 'skalowan|scaled' skills/implement/SKILL.md` (AC-5)
- `grep -Eiq 'always.?explicit|zawsze.*jawn|jawnie.*model' skills/implement/SKILL.md` (AC-12)
- Ręczny odczyt: fallback na standard przy wątpliwym kodzie jest jawnie sformułowany (AC-11), a pominięty `model` opisany jako błąd (AC-12).

**Implementation decisions / remarks:**
- Replaced the two-row "Model routing by risk" block with a "Model routing by role (always explicit)" section: a Markdown table (`implementation-worker` × 3 tiers, `phase-review`, `review-implementation`) plus a prose selection rule mirroring the table for the orchestrator to follow step-by-step. Added the always-explicit rule + "turn count beats token price" note at the top of the new section (covers AC-12). Added a third dispatch example block for the `haiku`/transcription tier so all three `implementation-worker` dispatch examples in O2 body now carry an explicit `model=`.
- `phase-review`/`review-implementation` dispatch calls themselves (in Step O4/O6) are NOT edited here — that is Phase 5's Write Scope (`Step O4, O6`). This phase only establishes the routing rule/table in O2; Phase 5 wires the explicit `model=` into the actual O4/O6 `Agent(...)` calls.

### Task 2: Zapis BASE commit przed dispatchem workera
**Status:** completed
**Traces to:** AC-6

**Modify:**
- `skills/implement/SKILL.md` (Step O2, sekcja "Before spawning the worker")

**Description:**
Orchestrator musi zapisać BASE commit (bieżący HEAD projektu docelowego) PRZED dispatchem workera, do wykorzystania przez review-package (Phase 5) i ledger (Phase 3). Bez tego review-package spadnie do `HEAD~1` i zgubi multi-commit fazy.

**Requirements:**
- Dodaj krok w O2 "before spawning the worker": zapisz BASE = `git rev-parse HEAD` przed dispatchem, zanotuj go (miejsce zapisu: linia ledgera — sformalizowane w Phase 3; tu wystarczy jawne polecenie "record BASE before dispatch").
- Sformułuj to jako twardy krok (MUST), nie opcjonalny — z jednozdaniowym uzasadnieniem (poprawny BASE dla review-package, nie `HEAD~1`).

**Tests:**
- `grep -Eiq 'BASE' skills/implement/SKILL.md && grep -Eiq 'przed dispatch|before .*dispatch|before spawning' skills/implement/SKILL.md` (AC-6)
- Ręczny odczyt: BASE zapisywany przed, nie po dispatchu.

**Implementation decisions / remarks:**
- Added "Record BASE commit (MUST, before dispatch)" as the first bullet under "Before spawning the worker" in O2, ahead of the existing context-budget-check and status-set bullets — so BASE is recorded before any other pre-dispatch step, satisfying "before dispatch" literally. Notes that the formal storage location (ledger line) is Phase 3's job; this phase only mandates the step and its justification (correct base for `review-package`, avoids silent `HEAD~1` fallback on multi-commit phases).

## Phase Verification
Run:
```bash
grep -q 'haiku' skills/implement/SKILL.md && grep -q 'opus' skills/implement/SKILL.md
grep -Eiq 'always.?explicit|jawnie.*model|zawsze.*jawn' skills/implement/SKILL.md
grep -Eiq 'BASE' skills/implement/SKILL.md
head -1 skills/implement/SKILL.md | grep -q '^---$'
```

## Completion Criteria
- Step O2 zawiera pełną tabelę routingu (≥3 tiery implementera + phase-review skalowany + review-implementation opus).
- Reguła always-explicit i fallback-na-standard obecne i jednoznaczne.
- BASE commit zapisywany przed dispatchem (twardy krok).
- Frontmatter i inne Steps SKILL.md nienaruszone.
- `implementation-context.md` zaktualizowany (BASE tracking istnieje w O2 — dla Phase 3/5).
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- Scope held strictly to Step O2 (`skills/implement/SKILL.md` lines ~197–236 after edit); Step O3/O4/O6 bodies and the worker file were left untouched — verified via `git diff` that only the O2 hunk changed and the rest of the pre-existing diff belongs to the already-completed Phase 1.
- Phase Verification grep suite (all 4 commands) passed against `skills/implement/SKILL.md`.
- Provides for later phases confirmed present in O2: full per-role table with ≥3 named implementer tiers, explicit `phase-review` (scaled) and `review-implementation` (opus, always) rows, always-explicit rule, standard-tier fallback rule, and a MUST-level "record BASE before dispatch" step — ready for Phase 3 (ledger) and Phase 5 (review-package wiring, O4/O6 dispatch calls) to build on.
