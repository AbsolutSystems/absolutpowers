# Feature: Orchestrated Implementation Phases

## Status
Draft — 2026-05-09

## Problem
Obecny workflow `generate-tasks -> implement` produkuje jeden duży plik `tasks-*.md`, a skill `implement` wykonuje kolejne taski w tej samej sesji. Dla większych feature'ów powoduje to narastanie kontekstu: agent pamięta szczegóły wcześniejszych tasków, miesza lokalne decyzje z kolejną fazą i coraz częściej eksploruje lub modyfikuje zbyt szeroki zakres.

Potrzebny jest workflow, w którym główny agent implementacyjny działa jako orkiestrator, a właściwa implementacja jest delegowana do małych subagentów uruchamianych per faza. Każdy subagent dostaje świeższy kontekst, ograniczony write scope i krótki handoff z wcześniejszych faz.

## Użytkownicy
- Autorzy korzystający z AbsolutPowers w Claude Code przy większych feature'ach.
- AI agent wykonujący `implement`, który potrzebuje mniejszego i bardziej kontrolowanego kontekstu.
- Reviewerzy zmian, którzy chcą widzieć jasny audit trail po fazach.

## Oczekiwane zachowanie
`generate-tasks` dla większych feature'ów tworzy:
- główny plik `tasks-{slug}.md` jako index/orchestrator plan,
- katalog `tasks-{slug}/` z plikami faz,
- `tasks-{slug}/implementation-context.md` jako krótki shared handoff między fazami.

`implement` w Claude Code:
- czyta główny plik tasków,
- znajduje pierwszą fazę `pending`,
- odpala subagenta implementacyjnego z własnym kontekstem dla konkretnego phase file,
- po fazie uruchamia lekki `phase-review`,
- dopiero po PASS oznacza fazę w głównym pliku jako `completed`,
- przechodzi do kolejnej fazy,
- na końcu uruchamia final verification i pełny `review-implementation`.

Codex zachowuje kompatybilność z obecnym workflow bez plugin-level subagentów.

## Wybrane rozwiązanie
Wprowadzić tryb **orchestrated tasks** dla większych feature'ów. Jednostką delegacji jest faza implementacji: 1-3 logicznie powiązane taski, dodatkowo ograniczone modułowym write scope.

### Uzasadnienie
Faza po 1-3 taski daje lepszy balans niż subagent per pojedynczy task. Redukuje zapychanie kontekstu, ale nie generuje nadmiernego narzutu koordynacyjnego. Write scope per faza ogranicza ryzyko, że worker zacznie naprawiać lub refaktorować obszary spoza zadania.

### Rozważane alternatywy
- **Jeden subagent per pojedynczy task:** odrzucone, bo narzut rediscovery i koordynacji będzie zbyt duży dla drobnych tasków.
- **Jeden subagent per moduł/warstwa:** odrzucone jako główny podział, bo fazy typu "service layer" mogą urosnąć do zbyt dużego zakresu. Moduł/warstwa pozostaje dobrym write scope, ale nie jedyną jednostką delegacji.
- **Pełny review po każdej fazie:** odrzucone jako domyślne, bo powtarza ciężką analizę całego diffu. Zamiast tego używany jest lekki `phase-review`, a pełny `review-implementation` dopiero na końcu.

## Zakres

### In scope
- Zmiana formatu outputu `generate-tasks` dla większych feature'ów.
- Nowy format głównego `tasks-{slug}.md`.
- Nowy format phase files w katalogu `tasks-{slug}/`.
- Nowy plik `implementation-context.md` jako shared handoff.
- Zmiana Claude `implement` w orchestratora faz.
- Dodanie Claude subagenta `implementation-worker`.
- Dodanie Claude subagenta `phase-review`.
- Zachowanie finalnego `review-implementation` po wszystkich fazach.
- Backward compatibility dla istniejących pojedynczych `tasks-*.md`.
- Dokumentacja różnic Claude vs Codex.

### Out of scope
- Równoległe wykonywanie faz.
- Automatyczne rozwiązywanie konfliktów między subagentami.
- Zmiana runtime Claude Code.
- Wymuszanie orchestrated mode dla małych zmian.
- Plugin-level subagenci w Codex, dopóki platforma ich nie wspiera.

## Proponowana struktura plików

```text
absolutpowers/feature/
├── tasks-{slug}.md
└── tasks-{slug}/
    ├── 01-{phase-slug}.md
    ├── 02-{phase-slug}.md
    ├── 03-{phase-slug}.md
    ├── 99-final-verification.md
    └── implementation-context.md
```

## Format głównego pliku `tasks-{slug}.md`

Główny plik jest kontrolerem pracy, nie pełną instrukcją implementacji.

```markdown
# Tasks: [Feature Name]

## Status
pending

## Source
- Planning doc: `./absolutpowers/feature/planning-{slug}.md`

## Mode
orchestrated

## Project Context
**Stack:** [...]
**Verification commands:** [...]
**Shared implementation context:** `./absolutpowers/feature/tasks-{slug}/implementation-context.md`

## Phase Overview

### Phase 1: [Title]
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/01-{phase-slug}.md`
**Depends on:** none
**Write scope:** `src/domain/**`, `src/domain/**/*Test.*`
**Risk:** low | medium | high

### Phase 2: [Title]
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/02-{phase-slug}.md`
**Depends on:** Phase 1
**Write scope:** `src/service/**`, `src/service/**/*Test.*`
**Risk:** medium

## Final Verification
**Status:** pending
**File:** `./absolutpowers/feature/tasks-{slug}/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file.
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase tests and `phase-review` pass.
```

## Format phase file

Każdy phase file ma być mały i wykonawczy. Docelowo 1-3 taski, wspólny write scope i konkretne testy.

```markdown
# Phase 1: [Title]

## Status
pending

## Parent
`./absolutpowers/feature/tasks-{slug}.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-{slug}/implementation-context.md`

## Read Scope
- `src/domain/ExistingPattern.java`
- `src/test/...`

## Write Scope
- `src/domain/NewThing.java`
- `src/domain/NewThingTest.java`

## Objective
[2-4 sentences: what this phase must produce.]

## Tasks

### Task 1: [Action]
**Status:** pending
**Requirements:**
- [...]
**Tests:**
- [...]

### Task 2: [Action]
**Status:** pending
**Requirements:**
- [...]
**Tests:**
- [...]

## Phase Verification
Run:
- `[specific focused test command]`

## Completion Criteria
- All phase tasks are completed.
- All files modified are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.

## Implementation Decisions / Remarks
- [filled by worker]
```

## Format `implementation-context.md`

Ten plik jest kontraktem między agentami, nie dziennikiem pracy.

```markdown
# Implementation Context: [Feature Name]

## Purpose
Short handoff for phase workers. Keep this file concise. Add only facts that future phases need.

## Completed Phases
- None yet.

## Created / Changed API
- None yet.

## Decisions Made
- None yet.

## Test Utilities / Fixtures
- None yet.

## Constraints For Next Phases
- None yet.

## Verification History
- None yet.
```

Zasady:
- Dodawać tylko informacje potrzebne kolejnym fazom.
- Nie kopiować pełnego diffa.
- Nie zapisywać tymczasowych hipotez debugowania.
- Nie duplikować rzeczy oczywistych z phase file.
- Wpisy powinny być krótkie, konkretne i linkować realne pliki lub symbole.

## Kontrakt `implementation-worker`

Nowy Claude agent: `claude/agents/implementation-worker.md`.

Rola:
- Implementuje wyłącznie jeden phase file.
- Czyta parent tasks file, phase file, `implementation-context.md`, `patterns.md`, `rules.md` i niezbędne reference files.
- Przestrzega Write Scope.
- Uruchamia phase verification.
- Aktualizuje statusy tasków w phase file.
- Dopisuje krótki handoff do `implementation-context.md`.
- Nie aktualizuje statusu fazy w głównym `tasks-{slug}.md`.
- Nie uruchamia pełnego `review-implementation`.

Wymagany output:

```text
PHASE_RESULT: COMPLETED | BLOCKED | FAILED

Phase: [phase file]
Files changed:
- [...]

Tests run:
- [command] -> pass/fail

Context updated:
- yes/no, summary

Notes for orchestrator:
- [...]
```

## Kontrakt `phase-review`

Nowy Claude agent: `claude/agents/phase-review.md`.

Rola:
- Lekko sprawdza jedną zakończoną fazę.
- Nie naprawia kodu.
- Nie robi pełnego code review całego feature'a.
- Sprawdza, czy worker spełnił kontrakt fazy.

Input:
- main tasks file,
- phase file,
- `implementation-context.md`,
- git diff,
- `patterns.md` i `rules.md`, jeśli istnieją.

Kryteria:
- phase file ma wszystkie taski oznaczone jako completed,
- zmiany mieszczą się w Write Scope albo mają jawne uzasadnienie,
- phase verification commands zostały uruchomione i przeszły,
- handoff w `implementation-context.md` jest krótki i użyteczny,
- brak oczywistych debug artifacts, martwego kodu, TODO/FIXME dodanych przez agenta,
- zmiany nie łamią constraints z main tasks file.

Output:

```text
VERDICT: PASS

[1-2 sentence summary]
```

albo:

```text
VERDICT: REJECTED

Issues to address:
1. [CATEGORY] `path:line` — [specific issue and required fix]
```

Kategorie:
- SCOPE
- COMPLETENESS
- TESTS
- HANDOFF
- CORRECTNESS
- GARBAGE
- RULES

## Zmiany w `generate-tasks`

Plik: `claude/skills/generate-tasks/SKILL.md`

Wymagane zmiany:
- Dodać decyzję trybu:
  - `single-file` dla micro/small changes,
  - `orchestrated` dla większych feature'ów.
- Dla `orchestrated` generować main tasks file oraz katalog faz.
- Grupować taski w fazy po 1-3 logicznie powiązane zadania.
- Każdej fazie przypisać Read Scope, Write Scope, Phase Verification i Completion Criteria.
- Utworzyć `implementation-context.md`.
- Final verification zapisać jako osobny phase file `99-final-verification.md`.

Heurystyka trybu `orchestrated`:
- więcej niż 3-4 taski,
- wiele warstw aplikacji,
- migracje danych,
- public API,
- security/multi-tenancy,
- shared core,
- integracje zewnętrzne,
- spodziewany diff większy niż mały feature.

Codex:
- Może generować ten sam format jako dokumentację faz,
- ale nie powinien obiecywać plugin-level subagentów.

## Zmiany w `implement`

Plik: `claude/skills/implement/SKILL.md`

Wymagane zmiany:
- Rozpoznawać `## Mode orchestrated`.
- Dla legacy `single-file` działać jak dotychczas.
- Dla `orchestrated` działać jako orchestrator:
  1. read main tasks file,
  2. find first pending phase,
  3. spawn `implementation-worker` for phase file,
  4. inspect worker result,
  5. spawn `phase-review`,
  6. if rejected: send fix instructions to worker or spawn fix worker for same phase,
  7. after PASS update phase status in main tasks file,
  8. continue until final verification,
  9. run full `review-implementation`.
- Maksymalnie 3 review/fix iterations per phase.
- Nie przechodzić do następnej fazy, jeśli obecna faza nie ma PASS.

## Zmiany w dokumentacji

Pliki:
- `README.md`
- `docs/getting-started.md`
- `docs/review-gates.md`
- `docs/contributing.md`

Dodać:
- opis orchestrated mode,
- strukturę plików,
- różnice Claude vs Codex,
- opis `implementation-worker` i `phase-review`,
- zasady używania `implementation-context.md`.

## Plan implementacji
1. Zaktualizować `claude/skills/generate-tasks/SKILL.md` o orchestrated output mode.
2. Dodać `claude/agents/implementation-worker.md`.
3. Dodać `claude/agents/phase-review.md`.
4. Zaktualizować `claude/skills/implement/SKILL.md` o orchestrator mode.
5. Zaktualizować `claude/skills/review/SKILL.md` lub `review-implementation`, jeśli trzeba uwzględnić phase files w finalnym review.
6. Zaktualizować `codex/skills/generate-tasks/SKILL.md` o phase file format bez obietnicy subagentów.
7. Zaktualizować `codex/skills/implement/SKILL.md` o fallback: wykonać fazy sekwencyjnie w tej samej sesji, ale respektować phase files i context file.
8. Zaktualizować README i docs.
9. Uruchomić `./scripts/diff-skills.sh --diff` i świadomie zaakceptować różnice Claude/Codex.
10. Przetestować na przykładowym planning doc z większym feature'em.

## Pliki do zmodyfikowania / utworzenia
- `claude/skills/generate-tasks/SKILL.md` — orchestrated output format.
- `claude/skills/implement/SKILL.md` — orchestrator execution.
- `claude/agents/implementation-worker.md` — nowy worker phase agent.
- `claude/agents/phase-review.md` — nowy lekki review gate per faza.
- `codex/skills/generate-tasks/SKILL.md` — kompatybilny phase file format.
- `codex/skills/implement/SKILL.md` — sekwencyjny fallback bez subagentów.
- `README.md` — dokumentacja workflow.
- `docs/getting-started.md` — aktualizacja pierwszego użycia.
- `docs/review-gates.md` — opis phase-review.
- `docs/contributing.md` — opis nowych agentów i driftu.

## Edge cases i ryzyka
- Worker przekroczy Write Scope, bo potrzebuje dopisać import/export w pliku spoza zakresu.
- `implementation-context.md` urośnie do długiego dziennika, jeśli prompt nie będzie rygorystyczny.
- Phase files mogą być zbyt duże, jeśli `generate-tasks` nie będzie miał jasnej heurystyki cięcia.
- Orchestrator może oznaczyć fazę jako completed mimo niepełnego handoffu.
- Codex i Claude zaczną driftować bardziej niż dotychczas.
- Final verification może wykryć integracyjne błędy dopiero po kilku fazach.
- Review gate po fazie może blokować na drobiazgach, jeśli będzie zbyt podobny do pełnego review.

## Pytania otwarte
- Czy orchestrated mode ma być domyślny zawsze po przekroczeniu progu liczby tasków, czy tylko gdy użytkownik poprosi?
- Czy `phase-review` ma być osobnym agentem, czy częścią istniejącego `review-implementation` z trybem phase?
- Czy phase worker może modyfikować `CLAUDE.md` / `AGENTS.md`, czy to zostawić tylko orchestratorowi po fazie?
- Czy dla high-risk phase wymagać szerszego test command niż phase-local tests?

## Notatki z dyskusji
- Preferowany unit delegacji: faza implementacji po 1-3 powiązane taski.
- Faza powinna mieć modułowy Write Scope.
- `implementation-context.md` ma być krótkim kontraktem między agentami, nie pamiętnikiem.
- Worker aktualizuje phase file i shared context.
- Orchestrator aktualizuje main tasks file.
- Po każdej fazie rekomendowany jest lekki `phase-review`.
- Pełny `review-implementation` powinien zostać dopiero na koniec.
