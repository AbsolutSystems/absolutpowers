# Phase 2: Wczesny scope-check (dekompozycja przed pytaniami)

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: krok 1, Zachowanie #4, AC-5/AC-8
- ADR lokalny: decyzja #2 (dekompozycja ROZSZERZA tryb epica — timing obry + machinery feature-discuss, zero duplikacji)

## Context Contract

### Requires (from previous phases)
- Blok `## HARD-GATE` obecny w `skills/feature-discuss/SKILL.md` (Phase 1) — by wstawić scope-check bez kolizji z nowym nagłówkiem.

### Provides (for later phases)
- Akapit wczesnego scope-checku na wejściu Fazy 1 (po Fazie 0 parafrazie, przed pierwszym pytaniem szczegółowym): trigger „wiele niezależnych podsystemów → nie drąż, flaguj i kieruj do detekcji epica (Faza 3)".
- Komunikat scope-checku jest KRÓTKI i KIERUJE do Fazy 3 (nie powiela komunikatu detekcji epica z Fazy 3).

## Read Scope
- `skills/feature-discuss/SKILL.md` (Faza 0 L~113, Faza 1 L~138, detekcja epica w Fazie 3 L~233 — wzorzec komunikatu, którego NIE dublujemy)

## Write Scope
- `skills/feature-discuss/SKILL.md`

## Objective
Dodaj na wejściu Fazy 1 (po potwierdzeniu kierunku w Fazie 0, przed pierwszym pytaniem szczegółowym) wczesny scope-check: gdy request opisuje wiele niezależnych podsystemów/warstw, feature-discuss NIE drąży szczegółów pytaniami — flaguje to od razu i kieruje do istniejącej detekcji/splitu epica (Faza 3). To rozszerzenie timingu, nie nowy mechanizm splitu — feeduje istniejącą maszynerię epica (main+stuby+Tryb B).

## Tasks

### Task 1: Wstaw akapit wczesnego scope-checku na wejściu Fazy 1
**Status:** completed
**Traces to:** AC-5, AC-8

**Requirements:**
- Wstaw 1-2 zdania na początku **Faza 1** (po Fazie 0, przed „ZASADA: JEDNO PYTANIE NA TURĘ" / pierwszym pytaniem szczegółowym).
- Trigger: gdy request opisuje wiele niezależnych podsystemów/warstw — zatrzymaj drążenie pytań, zaflaguj od razu i przejdź do detekcji epica (Faza 3) / splitu, zamiast marnować tury pytań na projekt do rozbicia.
- Komunikat scope-checku musi być **odrębny i krótszy** niż komunikat detekcji epica w Fazie 3 — ma *kierować* do Fazy 3 (wskaźnik), nie kopiować jej treści. Cel: epic nie jest flagowany dwukrotnie tym samym komunikatem w jednej sesji.
- NIE duplikuj mechanizmu splitu (main+stuby) — tylko wskaźnik do istniejącej maszynerii epica w Fazie 3.
- Język PL user-facing.

**Tests (grep-verifiable):**
- Scope-check obecny w rejonie Fazy 1: `grep -niE "niezależn.*podsystem|wiele podsystem|scope-check" skills/feature-discuss/SKILL.md`.
- Wskaźnik do Fazy 3 / epica z rejonu scope-checku (odwołanie „Faza 3" lub „epic" w akapicie wejścia Fazy 1).
- Brak zduplikowanego bloku komunikatu epica: `grep -c "to nie jeden feature, to epic" skills/feature-discuss/SKILL.md` → nadal 1 (tylko oryginał w Fazie 3).

## Phase Verification
Run:
- `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- `grep -c "to nie jeden feature, to epic" skills/feature-discuss/SKILL.md` → oczekiwane `1` (scope-check nie skopiował komunikatu epica).
- Ręcznie potwierdź: akapit scope-checku leży MIĘDZY końcem Fazy 0 a pierwszym pytaniem szczegółowym Fazy 1.

## Completion Criteria
- Wszystkie taski fazy `completed`.
- Wszystkie zmiany w Write Scope.
- Phase verification przechodzi; komunikat epica nie zdublowany.
- `implementation-context.md` zaktualizowany (gdzie osadzono scope-check, jak brzmi wskaźnik do Fazy 3).
- Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Akapit wstawiony bezpośrednio po nagłówku `### Faza 1: Zrozumienie potrzeby` (linia ~146-148 po edycji), przed dotychczasowym pierwszym zdaniem Fazy 1 ("Po potwierdzeniu kierunku...") i przed `**ZASADA: JEDNO PYTANIE NA TURĘ.**` (teraz linia 160).
- Treść (2 zdania PL): "**Scope-check na wejściu:** zanim zadasz pierwsze pytanie szczegółowe, oceń pobieżnie czy request opisuje wiele niezależnych podsystemów/warstw. Jeśli tak — NIE drąż pytaniami dalej; zaflaguj to od razu i przejdź do oceny epica (patrz Faza 3: Detekcja Epica) zamiast marnować tury pytań na projekt do rozbicia."
- Wskaźnik do Fazy 3 zrealizowany frazą "patrz Faza 3: Detekcja Epica" — krótki, nie kopiuje treści komunikatu epica z Fazy 3 ("Temat robi się spory — to nie jeden feature, to epic...").
- Zero duplikacji: `grep -c "to nie jeden feature, to epic"` nadal zwraca 1 (tylko oryginał w Fazie 3) — scope-check nie wprowadza równoległej normy, tylko wskaźnik.
- Nie ruszono: nagłówek Faza 1, treść bulletów CO/DLACZEGO, ZASADA jednego pytania, sekcja HARD-GATE z Fazy 1 (poprzednia faza).
</content>
