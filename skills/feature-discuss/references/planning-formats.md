# Planning document formats

_Extracted from `feature-discuss`. **Read this file** before writing planning / epic main / phase docs._

> Identify code by symbol name (class/method/field/constant) in every section below, not by line
> number — see `references/code-reference-style.md`.

## Format: standardowy planning doc

```markdown
# Feature: [Nazwa]

## Status
Draft — [data]

## Problem
[Co chcemy rozwiązać i dlaczego]

> **Ważne:** Cel i intencja feature'a MUSZĄ być zapisane tu explicite. Bramka `review-tasks`
> (kryterium Intent Fidelity) odpala się ze świeżym kontekstem i widzi wyłącznie to, co jest
> w tym dokumencie — intencja, która żyje tylko w rozmowie, jest dla niej niewidoczna.

## Użytkownicy
[Kto skorzysta z tego feature'a]

## Oczekiwane zachowanie
[Jak feature ma działać z perspektywy użytkownika]

## Wybrane rozwiązanie
[Opis wybranego podejścia technicznego]

### Uzasadnienie
[Dlaczego to podejście, a nie inne]

### Rozważane alternatywy
[Krótki opis odrzuconych podejść i powodów]

## Zakres

### In scope
- [Co wchodzi w zakres]

### Out of scope
- [Co świadomie wykluczamy]

### Deliberately not doing
- [Kusząca funkcja, abstrakcja, konfiguracja lub refaktor wykluczony z tego planu — dlaczego]

## Założenia i decyzje

### Założenia
- [Minimalne założenie przyjęte dla nieistotnej luki — oraz dlaczego nie wymaga osobnej decyzji]

### Decyzje wymagające potwierdzenia
- [Tylko nierozstrzygnięte kwestie, które zmieniają kontrakt, dane, bezpieczeństwo, migrację, zakres lub koszt; przed statusem Gotowy muszą zostać rozstrzygnięte]

## Plan implementacji
1. [Krok 1 — co i gdzie]
2. [Krok 2 — co i gdzie]
...

## Pliki do zmodyfikowania / utworzenia

> Przy każdym pliku podaj zmieniane metody, konstruktory, pola lub regiony — nie samą nazwę
> pliku; identyfikuj je nazwą, nigdy numerem linii (patrz reguła na górze tego dokumentu i
> `references/code-reference-style.md`). Gdy zmiana nie dotyczy żadnego nazwanego symbolu (nowy
> plik tworzony w całości, blok konfiguracji, adnotacja na poziomie klasy) — napisz to wprost
> zamiast zmyślać nazwę. Gdy nie ustalono jeszcze, który symbol się zmieni — też napisz to
> wprost, zamiast zgadywać. Przed nadaniem dokumentowi statusu Gotowy sprawdź, że każdy plik
> wymieniony w prozie (Wybrane rozwiązanie, Plan implementacji, Edge cases i ryzyka, Acceptance
> Criteria) pojawia się też w tej sekcji.
- `ścieżka/plik` — `NazwaKlasy.metoda()`, `NazwaKlasy.pole`: [co trzeba zrobić]
- `ścieżka/nowy-plik` — cały plik, nowy (brak symbolu)

## Edge cases i ryzyka
- [Edge case 1]
- [Ryzyko 1]

## Acceptance Criteria

> Sekcja generowana automatycznie przez qa-enrichment agent — nie wypełniaj ręcznie.

### Happy path
- AC-1: [opis behawioralny]

### Edge cases
- AC-N: [scenariusz brzegowy]

### Security
- AC-N: [wymaganie bezpieczeństwa]

## Pytania otwarte
- [Kwestie do rozstrzygnięcia później]

## Notatki z dyskusji
[Kluczowe ustalenia z rozmowy]
```

## Format: główny planning epica (domyślnie `planning-main.md`)

> LEKKI, kontekstowy. BEZ szczegółowego planu implementacji, BEZ Acceptance Criteria
> (te mieszkają w phase docach). Main to "mapa" epica i wspólny kontekst.

```markdown
# Epic: [Nazwa]

## Status
Draft — [data]

## Problem
[Co chcemy rozwiązać i dlaczego — na poziomie całości]

## Użytkownicy
[Kto skorzysta]

## Oczekiwane zachowanie (high-level)
[Jak całość ma działać — bez schodzenia w szczegóły faz]

## Wspólny kontekst architektoniczny
[Stack, kluczowe moduły, wzorce, ograniczenia wspólne dla wszystkich faz]

## Wspólne decyzje
- [Decyzja] → ADR: `./docs/adr/YYYY-MM-DD-{slug}.md`

## Mapa faz

| Faza | Nazwa | Cel | Status | Plan |
|------|-------|-----|--------|------|
| 1 | [nazwa] | [cel jednym zdaniem] | Do zaplanowania | `planning-phase-1-{subslug}.md` |
| 2 | [nazwa] | [cel] | Do zaplanowania | `planning-phase-2-{subslug}.md` |
| 3 | [nazwa] | [cel] | Do zaplanowania | `planning-phase-3-{subslug}.md` |

> Statusy są trwałym stanem między sesjami:
> `Do zaplanowania` → `Zaplanowana` (ustawia `feature-discuss`) → `W toku`
> (ustawia `implement` przed pierwszą zmianą kodu/dispatch) → opcjonalnie
> `Do akceptacji decyzji` (niepuste Implementation Decisions / Remarks) → `Zrobiona`
> (dopiero po final verification, PASS bramki implementacyjnej lub jawnym override oraz
> wymaganym human decision review). `Zrobiona` nie zastępuje osobnego branch-level
> `review`/`triada-review`.

## Zależności między fazami
- Faza 2 zależy od Fazy 1 ([dlaczego])
- [...]

## Out of scope (całość)
- [Co świadomie wykluczamy z całego epica]

## Pytania otwarte (przekrojowe)
- [Kwestie dotyczące całości]

## Notatki z dyskusji
[Kluczowe ustalenia o podziale na fazy]
```

## Format: phase doc (`planning-phase-N-{subslug}.md`)

> Pełny format = standardowy planning doc + sekcja kontekstu nadrzędnego na górze.
> Jako STUB (przy tworzeniu epica) wypełnij tylko: nagłówek, kontekst, cel, zgrubny
> scope, zależności, status. Resztę zostaw jako `TODO — do zaplanowania w osobnej sesji`.

```markdown
# Faza [N]: [Nazwa]  (epic: [nazwa epica])

## Kontekst nadrzędny
> ZACZNIJ od przeczytania `{dokładna ścieżka do głównego planning doca epica}`.
- Epic planning: `{dokładna ścieżka; nie odtwarzaj jej później z konwencji nazwy}`
- Zależności od innych faz: [np. wymaga Fazy 1 — modelu danych]

## Status
Do zaplanowania — [data]   <!-- → Draft → Gotowy po zaplanowaniu fazy -->

## Cel fazy
[Co ta faza dostarcza — jeden, dwa akapity]

## Zakres

### In scope
- [...]

### Out of scope
- [Co należy do innych faz / poza epic]

### Deliberately not doing
- [Kusząca funkcja, abstrakcja, konfiguracja lub refaktor wykluczony z fazy — dlaczego]

## Założenia i decyzje

### Założenia
- [Minimalne założenie przyjęte dla nieistotnej luki]

### Decyzje wymagające potwierdzenia
- [Istotne nierozstrzygnięte kwestie; przed statusem Gotowy muszą zostać rozstrzygnięte]

## Wybrane rozwiązanie
TODO — do zaplanowania w osobnej sesji (Tryb B)

### Uzasadnienie
TODO

### Rozważane alternatywy
TODO

## Plan implementacji
TODO — do zaplanowania w osobnej sesji

## Pliki do zmodyfikowania / utworzenia
TODO

## Edge cases i ryzyka
TODO

## Acceptance Criteria
> Generowane przez qa-enrichment po zaplanowaniu fazy. Nie wypełniaj ręcznie.

## Pytania otwarte
- [Znane już teraz pytania dot. tej fazy]

## Notatki z dyskusji
[Uzupełniane w sesji planowania tej fazy]
```
