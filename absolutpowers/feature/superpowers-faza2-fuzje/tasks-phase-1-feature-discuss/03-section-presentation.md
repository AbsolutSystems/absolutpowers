# Phase 3: Prezentacja designu sekcjami + skalowanie długości

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: krok 3, Zachowanie #3, AC-3/AC-4

## Context Contract

### Requires (from previous phases)
- Scope-check na wejściu Fazy 1 obecny (Phase 2) — Faza 3 współpracuje z wcześniejszym flagowaniem epica; nie dubluj triggera.

### Provides (for later phases)
- Przepisany koniec **Faza 3**: po rekomendacji podejścia design prezentowany sekcjami (co najmniej: architektura, komponenty, data flow, obsługa błędów, testy), z osobnym pytaniem o akceptację po każdej sekcji.
- Jawna instrukcja skalowania długości każdej sekcji do złożoności (krótka dla prostych, rozwinięta ~200-300 słów dla niuansowych) — nie jednolita długość.

## Read Scope
- `skills/feature-discuss/SKILL.md` (Faza 3 L~221-258, w tym „Zaproponuj JEDNO rekomendowane podejście" i detekcja epica — NIE ruszaj detekcji epica)

## Write Scope
- `skills/feature-discuss/SKILL.md`

## Objective
Przepisz końcową część Fazy 3: obecnie daje jedną łączną rekomendację naraz. Po rekomendacji podejścia design ma być prezentowany rozbity na sekcje (architektura / komponenty / data flow / obsługa błędów / testy), długość każdej sekcji skalowana do złożoności tematu, z osobnym pytaniem o akceptację po każdej sekcji i powrotem/klaryfikacją gdy sekcja nie gra. Spójne z zasadą „jedno pytanie na turę".

## Tasks

### Task 1: Graft prezentacji sekcjami + skalowania długości w Fazie 3
**Status:** completed
**Traces to:** AC-3, AC-4

**Requirements:**
- Po bloku rekomendacji podejścia (i przed/obok detekcji epica) dodaj instrukcję: prezentuj design rozbity na sekcje — co najmniej **architektura, komponenty, data flow, obsługa błędów, testy** — nie jedną łączną rekomendacją.
- Po każdej sekcji zadaj **osobne pytanie o akceptację**; gdy sekcja nie gra — wróć i sklaruj zanim przejdziesz dalej. Utrzymaj „jedno pytanie na turę".
- Dodaj jawną instrukcję **skalowania długości**: krótka sekcja (kilka zdań) dla prostych elementów, rozwinięta (~200-300 słów) dla niuansowych — nie jednolita długość dla wszystkich.
- NIE ruszaj bloku detekcji epica w Fazie 3 (Phase 2/epic machinery zależą od niego); prezentacja sekcjami dotyczy ścieżki nie-epic (pojedynczy feature).
- Powiąż z HARD-GATE: akceptacja sekcji buduje akceptację całego designu (brama z Phase 1).
- Język PL user-facing.

**Tests (grep-verifiable):**
- Wszystkie pięć sekcji wymienione w rejonie Fazy 3: `grep -niE "architektur|komponent|data flow|obsług.*błęd|test" skills/feature-discuss/SKILL.md` (po edycji Fazy 3 — obecność łączna).
- Akceptacja per sekcja: `grep -niE "akceptacj.*sekcj|po każdej sekcji" skills/feature-discuss/SKILL.md`.
- Skalowanie długości: `grep -niE "skaluj|długość.*złożon|złożon.*długość" skills/feature-discuss/SKILL.md`.

## Phase Verification
Run:
- `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- `grep -niE "po każdej sekcji|akceptacj.*sekcj" skills/feature-discuss/SKILL.md` → ≥1 trafienie.
- `grep -niE "skaluj|złożon" skills/feature-discuss/SKILL.md` → ≥1 trafienie w rejonie Fazy 3.
- Ręcznie: pięć nazwanych sekcji (architektura/komponenty/data flow/obsługa błędów/testy) obecne jako lista prezentacji.

## Completion Criteria
- Wszystkie taski fazy `completed`.
- Zmiany w Write Scope; detekcja epica w Fazie 3 nietknięta.
- Phase verification przechodzi.
- `implementation-context.md` zaktualizowany.
- Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Nowa podsekcja `#### Prezentacja designu sekcjami (ścieżka nie-epic)` wstawiona w `### Faza 3: Propozycja rozwiązania`, między blokiem rekomendacji podejścia ("NIE prezentuj 3 równorzędnych opcji...") a `#### Detekcja Epica` — dokładnie zgodnie z Objective ("po bloku rekomendacji podejścia i przed/obok detekcji epica").
- Pięć nazwanych sekcji jako numerowana lista: Architektura, Komponenty, Data flow, Obsługa błędów, Testy — każda z jednozdaniowym opisem co obejmuje.
- Osobne pytanie o akceptację po każdej sekcji + powrót/klaryfikacja gdy sekcja nie gra, powiązane słownie z zasadą "jedno pytanie na turę" (odwołanie do Fazy 1) i z HARD-GATE ("to jest ta sama bramka co HARD-GATE wyżej, tylko rozłożona na kawałki") — spełnia wymóg powiązania z gate z Objective.
- Skalowanie długości: jawna instrukcja dwupoziomowa — "kilka zdań" dla prostych elementów, "~200-300 słów" dla niuansowanych, z przykładami obu.
- Blok kończy się jednozdaniowym rozgraniczeniem: prezentacja sekcjami dotyczy ścieżki nie-epic; gdy temat okaże się epikiem, przejść do Detekcji Epica zamiast prezentować sekcjami — utrzymuje separację od `#### Detekcja Epica`, który został NIETKNIĘTY (zweryfikowane grep — nagłówek i treść identyczne jak przed edycją).
- Język: PL user-facing, zgodnie z konwencją.
</content>
