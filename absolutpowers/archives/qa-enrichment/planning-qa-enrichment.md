# Feature: QA Enrichment — Acceptance Criteria w pipeline

## Status
Draft — 2026-06-05

## Problem
Pipeline AbsolutPowers nie ma mechanizmu definition of done. Planning doc opisuje CO budować, ale nie definiuje JAK ZWERYFIKOWAĆ że feature działa poprawnie. Konsekwencje:
- `generate-tasks` wymyśla testy ad-hoc, bez formalnego wymagania
- `review-implementation` ocenia kod bez behawioralnych kryteriów sukcesu
- Brak traceability: nie wiadomo czy wszystkie wymagania z planu mają pokrycie w taskach i implementacji
- Edge cases i security zależą od "pamięci" LLM, nie od jawnych wymagań

## Użytkownicy
- Deweloperzy korzystający z pipeline `feature-discuss → generate-tasks → implement → review`
- Na obu platformach: Claude Code (z subagentami) i Codex (inline)

## Oczekiwane zachowanie

### Perspektywa użytkownika
1. Użytkownik prowadzi dyskusję z feature-discuss jak dotąd
2. Po zapisie planning doc, QA-enrichment automatycznie analizuje plan i dopisuje sekcję `## Acceptance Criteria` z numerowanymi AC
3. Review-plan weryfikuje plan razem z jakością AC
4. W generate-tasks każdy task ma pole `Traces to: AC-1, AC-3`
5. W review-tasks weryfikowane jest pokrycie: każde AC-N ma min. 1 task
6. W review-implementation weryfikowane jest spełnienie: każde AC-N ma implementację + test
7. Użytkownik widzi pełną kaskadę: AC → task → kod → test

### Format AC w planning doc
```markdown
## Acceptance Criteria

### Happy path
- AC-1: [opis behawioralny — co musi być prawdą]
- AC-2: [opis behawioralny]

### Edge cases
- AC-3: [scenariusz brzegowy — co się dzieje gdy...]
- AC-4: [scenariusz brzegowy]

### Security
- AC-5: [wymaganie bezpieczeństwa]
```

Każde AC:
- Behawioralne, user-facing (nie "plik istnieje", nie "metoda zwraca X")
- Zero implementation details (zero file paths, zero method signatures, zero nazw klas)
- Weryfikowalne jako prawda/fałsz
- Numerowane `AC-N:` dla stabilnej referencji w pipeline

### Traceability w taskach
```markdown
### Task 3: Create ExportService
**Traces to:** AC-1, AC-4
...
**Verification:**
- [ ] Test covers: empty filter → all records (AC-1)
- [ ] Test covers: future date filter → empty list, 200 not 4xx (AC-4)
```

### AC fulfillment w review-implementation
Review-implementation po sprawdzeniu kodu raportuje:
```
AC Fulfillment:
- AC-1: FULFILLED (ExportController.spec.ts:45)
- AC-2: FULFILLED (ExportService.spec.ts:22)
- AC-3: NOT VERIFIED — no test found
```

## Wybrane rozwiązanie

### Architektura: QA jako wewnętrzny subagent feature-discuss

**Claude Code:**
- Nowy agent `claude/agents/qa-enrichment.md`
- Spawned przez feature-discuss po zapisie planning doc, przed review-plan gate
- Agent czyta planning doc + codebase (istniejące testy, CI config, test patterns)
- Dopisuje sekcję `## Acceptance Criteria` do planning doc
- Review-plan rozszerzony o kryterium "AC Quality"

**Codex:**
- Inline faza w `codex/skills/feature-discuss/SKILL.md`
- Ta sama logika QA, bez subagenta (Codex nie ma plugin-level agentów)
- Produkuje identyczny format AC

### Flow po zmianach

**Claude Code:**
```
feature-discuss:
  1. dyskusja z userem (bez zmian)
  2. zapis planning doc (bez zmian)
  3. qa-enrichment subagent → dopisuje AC do planning doc (NOWE)
  4. review-plan gate z kryterium AC Quality (ROZSZERZONE)
  5. ADR (bez zmian)
```

**Codex:**
```
feature-discuss:
  1. dyskusja z userem (bez zmian)
  2. zapis planning doc (bez zmian)
  3. inline QA enrichment → dopisuje AC do planning doc (NOWE)
  4. sugestia następnego kroku (bez zmian)
```

### Kaskada AC przez pipeline

| Skill/Agent | Co robi z AC |
|-------------|-------------|
| **feature-discuss** | QA-enrichment generuje AC w planning doc |
| **review-plan** | Weryfikuje jakość AC (nowe kryterium AC_QUALITY) |
| **generate-tasks** | Mapuje AC na taski, dodaje `Traces to: AC-N` |
| **review-tasks** | Sprawdza pokrycie: każde AC-N ma min. 1 task (nowe kryterium AC_COVERAGE) |
| **implement** | Czyta AC na starcie, raportuje fulfillment status |
| **review-implementation** | Weryfikuje AC fulfillment: każde AC-N spełnione (nowe kryterium AC_FULFILLMENT) |

### Uzasadnienie
- QA jako osobny mindset od planowania — planner myśli "co budować", QA myśli "co może się zepsuć"
- Niezależna weryfikacja: QA tworzy AC, review-plan ocenia ich jakość
- Minimalne 3 kategorie (happy path, edge cases, security) — wystarczające bez overengineering
- ID-based referencje (`AC-N`) — mechaniczne traceability, nie fuzzy text matching
- Codex inline — ta sama wartość bez dependency na plugin-level agentów

### Rozważane alternatywy

**A) QA jako osobny skill (user-invoked):**
Odrzucone — dodaje krok w pipeline użytkownika. User musiałby pamiętać o `/absolutpowers:qa-review` między feature-discuss a generate-tasks. Wbudowanie w feature-discuss jest transparentne.

**B) QA enrichment po review-plan (nie przed):**
Odrzucone — review-plan nie mógłby weryfikować jakości AC. Dwa osobne gate'y to zbędny narzut. Lepiej: QA dopisuje AC → review-plan sprawdza całość w jednym przebiegu.

**C) Adaptacyjne kategorie AC (6 kategorii, agent wybiera):**
Odrzucone — ryzyko niespójności między feature'ami. Stałe 3 kategorie (happy path, edge cases, security) prostsze i przewidywalne. Performance/accessibility/error handling to implementation concerns, nie AC.

**D) QA agent self-validates (bez rozszerzania review-plan):**
Odrzucone — ten sam LLM oceniałby swoją pracę. Review-plan jako osobny agent daje niezależną weryfikację.

## Zakres

### In scope
- Nowy agent `qa-enrichment` (Claude only)
- Inline QA faza w Codex feature-discuss
- Rozszerzenie review-plan o kryterium AC Quality
- Rozszerzenie generate-tasks o traceability AC → tasks
- Rozszerzenie review-tasks o kryterium AC Coverage
- Rozszerzenie implement o AC awareness
- Rozszerzenie review-implementation o AC Fulfillment
- Aktualizacja planning doc template w feature-discuss
- Aktualizacja dokumentacji (README, docs/)

### Out of scope
- Zmiana formatu orchestrated phase files (AC traceability jest na poziomie tasków, nie faz)
- Automatyczne wykonywanie AC (AC behawioralne, nie executable — mapowanie na testy robi generate-tasks)
- Zmiana review skill (standalone code review — nie jest częścią AC pipeline)
- Zmiana debug skill
- Zmiana update-ai-context skill
- Retroaktywne dodawanie AC do istniejących planning docs

## Plan implementacji

1. **Utwórz agent `qa-enrichment`** — definicja agenta z promptem QA, dostęp do Read/Glob/Grep/Bash + Edit planning doc
2. **Zmień feature-discuss (Claude)** — nowa Faza 5B między zapisem a review-plan, spawn qa-enrichment, rozszerzony template planning doc
3. **Zmień feature-discuss (Codex)** — nowa inline faza QA z identyczną logiką
4. **Zmień review-plan** — nowe kryterium "AC Quality", nowa kategoria AC_QUALITY
5. **Zmień generate-tasks (Claude + Codex)** — czytanie AC z planning doc, pole `Traces to:` w taskach, traceability w task template
6. **Zmień review-tasks** — nowe kryterium "AC Coverage", nowa kategoria AC_COVERAGE
7. **Zmień implement (Claude + Codex)** — czytanie AC na starcie, raportowanie fulfillment status
8. **Zmień review-implementation** — nowe kryterium "AC Fulfillment", nowa kategoria AC_FULFILLMENT
9. **Aktualizacja dokumentacji** — README, getting-started, review-gates

## Pliki do zmodyfikowania / utworzenia

- `claude/agents/qa-enrichment.md` — **UTWÓRZ** — nowy agent QA enrichment
- `claude/skills/feature-discuss/SKILL.md` — dodaj Fazę 5B (qa-enrichment spawn), rozszerz template planning doc o sekcję AC
- `codex/skills/feature-discuss/SKILL.md` — dodaj inline fazę QA enrichment, rozszerz template planning doc o sekcję AC
- `claude/agents/review-plan.md` — dodaj kryterium "5. AC Quality" w Review Criteria, dodaj kategorię AC_QUALITY
- `claude/skills/generate-tasks/SKILL.md` — dodaj czytanie AC z planning doc, dodaj `Traces to:` w task template, dodaj instrukcję traceability
- `codex/skills/generate-tasks/SKILL.md` — to samo co Claude wersja (bez agent-specific zmian)
- `claude/agents/review-tasks.md` — dodaj kryterium "AC Coverage" w Traceability, dodaj kategorię AC_COVERAGE
- `claude/skills/implement/SKILL.md` — dodaj czytanie AC z planning doc na starcie, dodaj raportowanie fulfillment status
- `codex/skills/implement/SKILL.md` — to samo co Claude wersja
- `claude/agents/review-implementation.md` — dodaj kryterium "AC Fulfillment", dodaj kategorię AC_FULFILLMENT
- `README.md` — aktualizuj opis pipeline o AC kaskadę, aktualizuj opis feature-discuss i review gates
- `docs/getting-started.md` — aktualizuj przykład workflow o AC
- `docs/review-gates.md` — dodaj opis qa-enrichment i nowych kryteriów w gate'ach

## Edge cases i ryzyka

- **QA generuje trywialne AC** ("system działa poprawnie") — mitygowane przez review-plan AC Quality gate który odrzuca vague AC
- **Za dużo AC** — agent może wygenerować 20+ AC dla dużego feature'a. Rozważyć limit (np. max 15) lub priorytetyzację
- **Micro-changes pomijają AC** — zamierzone. Micro-changes (Faza 5) pomijają planning doc → pomijają AC
- **Istniejące planning docs bez AC** — generate-tasks musi obsłużyć brak sekcji AC (graceful fallback, nie error). Traceability optional gdy brak AC
- **Drift Claude/Codex** — inline QA w Codex musi produkować identyczny format AC. Drift detection via `diff-skills.sh`
- **Token overhead** — dodatkowy subagent call. Szacunek: ~2-5k tokenów per QA enrichment. Akceptowalne vs koszt odrzuconej implementacji
- **AC format evolution** — jeśli format AC zmieni się w przyszłości, trzeba aktualizować: qa-enrichment, review-plan, generate-tasks, review-tasks, implement, review-implementation (6 plików). Coupling przez konwencję

## Pytania otwarte

- Czy limit AC (np. max 15) powinien być hardcoded w agencie, czy parametryzowalny?
- Czy phase-review (orchestrated) powinien też sprawdzać AC traceability per-phase, czy wystarczy końcowy review-implementation?

## Notatki z dyskusji

- Inicjalnie rozważano osobny skill QA — odrzucono na rzecz wbudowania w feature-discuss (mniej kroków dla użytkownika)
- Rozważano QA po review-plan — odrzucono bo review-plan nie mógłby weryfikować AC jakości
- Rozważano 6 kategorii AC (adaptacyjne) — odrzucono na rzecz stałych 3 (happy path, edge cases, security) dla prostoty
- Rozważano self-validation QA — odrzucono bo ten sam LLM oceniałby swoją pracę
- Rozważano pominięcie Codex — odrzucono, inline faza daje tę samą wartość bez agentów
- AC muszą być behawioralne (co musi być prawdą), nie techniczne (jaki plik/metoda). Planning nie powinien znać implementacji — to odpowiedzialność generate-tasks
