# Review Gates — Automatyczne weryfikacje jakości

Review gates to subagenty, które automatycznie sprawdzają output każdego kroku pipeline'u. Działają jak quality gate w CI/CD — nie przepuszczają artefaktu jeśli nie spełnia kryteriów.

## Przegląd

```
feature-discuss ──zapisuje──▶ planning doc ──▶ review-plan ──▶ PASS / REJECTED
                                                                    │
generate-tasks ──zapisuje──▶ tasks doc ────▶ review-tasks ──▶ PASS / REJECTED
                                                                    │
implement ──kończy taski──▶ kod + testy ──▶ review-implementation ──▶ PASS / REJECTED
```

Dla większych tasków w Claude Code `implement` może działać w trybie orchestrated:

```
main tasks file ──▶ implementation-worker ──▶ phase-review ──▶ PASS / REJECTED
                         │                       │
                         └──── next phase ◀──────┘

all phases + final verification ──▶ review-implementation ──▶ PASS / REJECTED
```

`phase-review` jest lekkim gate'em jednej fazy. Pełny `review-implementation` nadal działa dopiero po zakończeniu wszystkich faz i final verification.

## Mechanizm działania

1. Skill kończy swoją pracę i zapisuje output (planning doc / tasks doc / kod)
2. Skill automatycznie uruchamia odpowiedni subagent review
3. Subagent czyta output + kontekst projektu (patterns.md, rules.md, CLAUDE.md)
4. Subagent zwraca jedno z dwóch:
   - `VERDICT: PASS` — output jest gotowy
   - `VERDICT: REJECTED` + lista konkretnych problemów
5. Jeśli REJECTED — skill adresuje problemy, poprawia output, uruchamia review ponownie
6. Maksymalnie 3 iteracje. Po 3 odrzuceniach — skill pyta użytkownika o decyzję

## Dostępność

| Platforma | Review gates |
|-----------|-------------|
| Claude Code | Tak (subagenty w `claude/agents/`, w tym `phase-review` dla orchestrated implementation) |
| Codex | Nie (brak wsparcia dla plugin-level agentów) |

## review-plan

**Uruchamiany przez:** `feature-discuss` (po zapisie planning doc)

**Sprawdza:**

### Completeness
- Problem statement jasny i konkretny
- Użytkownicy/odbiorcy zidentyfikowani
- Oczekiwane zachowanie opisane konkretnie
- Zakres (in/out) zdefiniowany bez niejasności
- Edge cases i ryzyka zidentyfikowane
- Pliki do modyfikacji/utworzenia wymienione z konkretnymi akcjami

### Feasibility
- Wybrane rozwiązanie technicznie wykonalne w tym codebase
- Referencje do plików, wzorców i API faktycznie istnieją
- Brak założeń o nieistniejącej infrastrukturze
- Złożoność realistyczna wobec opisanego zakresu

### Architectural Soundness
- Rozwiązanie zgodne z istniejącą architekturą (lub jawnie uzasadnia odchylenie)
- Brak niepotrzebnego couplingu
- Zgodność z patterns.md i rules.md
- Bezpieczeństwo, wydajność, integralność danych rozważone

### Actionability
- Plan wystarczająco szczegółowy żeby `generate-tasks` mógł z niego stworzyć konkretne taski
- Kroki implementacji uporządkowane logicznie
- Brak vague kroków typu "obsłuż błędy prawidłowo"
- Alternatywy udokumentowane z jasnymi powodami odrzucenia

**Maksymalnie 7 issues per review.**

## review-tasks

**Uruchamiany przez:** `generate-tasks` (po zapisie tasks doc)

Dla orchestrated tasks czyta główny `tasks-{slug}.md`, wszystkie referenced phase files, `99-final-verification.md` i `implementation-context.md`.

**Sprawdza:**

### Traceability
- Każde wymaganie z planning doc pokryte przez co najmniej jeden task
- Brak tasków wykraczających poza zakres planning doc bez uzasadnienia

### Granularity
- Każdy task to jedna logiczna jednostka pracy
- Brak zbyt dużych tasków (wiele feature'ów w jednym) ani zbyt małych (rename zmiennej)

### Ordering & Dependencies
- Kolejność poprawna — żaden task nie zależy od czegoś jeszcze niezbudowanego
- Fundamenty (modele, typy, interfejsy) przed konsumentami (serwisy, kontrolery)
- Testy co-located z implementacją, nie odłożone na osobny task

### Specificity
- Ścieżki plików dokładne i istniejące (lub oznaczone jako nowe do utworzenia)
- Sygnatury metod z typami
- Referencje do wzorców wskazują na realne pliki
- Typy błędów, klasy wyjątków, poziomy logowania określone
- Brak vague instrukcji

### Verification
- Finalny task weryfikacyjny istnieje jako ostatni
- Używa konkretnych komend projektu (nie generycznych `npm test`)

### Code References
- Referencje do plików faktycznie istnieją w codebase
- Wzorce w tych plikach odpowiadają opisowi
- Sygnatury metod zgodne z rzeczywistymi interfejsami

**Weryfikuje minimum 3 referencje do plików sprawdzając codebase.**

**Maksymalnie 7 issues per review.**

## phase-review

**Uruchamiany przez:** `implement` po zakończeniu jednej fazy orchestrated implementation

**Sprawdza:**

### Scope
- Zmienione pliki mieszczą się w Write Scope fazy
- Każde wyjście poza Write Scope jest jawnie uzasadnione

### Completeness
- Wszystkie taski w phase file są oznaczone jako completed
- Wymagania fazy mają odpowiadającą implementację
- Parent tasks file nie jest oznaczany jako completed przez workera

### Tests
- Phase verification commands zostały uruchomione
- Wynik weryfikacji jest zapisany w phase file albo handoffie

### Handoff
- `implementation-context.md` zawiera tylko krótkie fakty potrzebne kolejnym fazom
- Brak pełnych diffów, debug notes i generycznej narracji

### Correctness / Garbage / Rules
- Brak oczywistych bugów w zakresie fazy
- Brak debug logs, martwego kodu, stale TODO/FIXME
- Brak jasnych naruszeń `rules.md`

**Nie zastępuje `review-implementation`.** Ma łapać problemy lokalne przed przejściem do następnej fazy.

**Maksymalnie 7 issues per review.**

## review-implementation

**Uruchamiany przez:** `implement` (po zakończeniu wszystkich tasków)

Dla orchestrated tasks czyta main tasks file, wszystkie phase files, `implementation-context.md` i `99-final-verification.md`.

**Sprawdza:**

### Correctness
- Implementacja zgodna z wymaganiami tasków
- Logika poprawna — brak oczywistych bugów, off-by-one, null dereferences
- Error handling pokrywa failure paths opisane w taskach
- Brak martwego kodu, nieużywanych importów, artefaktów debugowania

### Patterns Compliance
- Kod zgodny z patterns.md
- Konwencje nazewnictwa zgodne ze standardami projektu
- Lokalizacja plików zgodna ze strukturą projektu

### Rules Compliance
- Brak naruszeń rules.md
- Brak zabronionych wzorców
- Wymagane biblioteki użyte gdzie wskazano

### Test Coverage
- Testy istnieją dla każdego tasku który je wymagał
- Testy pokrywają success, failure i edge cases
- Testy asertują sensowne zachowanie (nie tylko "nie rzuca wyjątku")

### Completeness
- Wszystkie taski oznaczone jako completed mają odpowiadające zmiany w kodzie
- Brak częściowych implementacji
- Final verification task wykonany i przeszedł

### Safety
- Brak zahardkodowanych sekretów, credentials, tokenów
- Brak SQL injection, XSS, command injection
- Brak niezwalidowanego zewnętrznego inputu w wrażliwych operacjach

**Sprawdza WSZYSTKIE zmienione pliki, nie tylko te wymienione w taskach.**

**Maksymalnie 10 issues per review.**

## Kategorie issues

Każdy issue w REJECTED verdict ma kategorię:

| Gate | Kategorie |
|------|-----------|
| review-plan | COMPLETENESS, FEASIBILITY, ARCHITECTURE, ACTIONABILITY |
| review-tasks | TRACEABILITY, GRANULARITY, ORDERING, SPECIFICITY, VERIFICATION, CODE_REFERENCE |
| phase-review | SCOPE, COMPLETENESS, TESTS, HANDOFF, CORRECTNESS, GARBAGE, RULES |
| review-implementation | CORRECTNESS, PATTERNS, RULES, TESTS, COMPLETENESS, SAFETY |

## Co jeśli gate ciągle odrzuca?

Po 3 nieudanych iteracjach skill pokazuje pozostałe issues i pyta co robić. Opcje:

1. **Napraw ręcznie** — popraw plik/kod i uruchom skill ponownie
2. **Kontynuuj mimo problemów** — zaakceptuj znane issues i idź dalej
3. **Wróć do poprzedniego kroku** — np. z generate-tasks wróć do feature-discuss

Gate'y nie blokują na stałe. Są narzędziem do wyłapywania problemów, nie biurokracją.
