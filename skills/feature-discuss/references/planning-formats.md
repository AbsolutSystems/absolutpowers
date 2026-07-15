# Planning document formats

_Extracted from `feature-discuss`. **Read this file** before writing planning / epic main / phase docs._

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

## Plan implementacji
1. [Krok 1 — co i gdzie]
2. [Krok 2 — co i gdzie]
...

## Pliki do zmodyfikowania / utworzenia
- `ścieżka/plik` — [co trzeba zrobić]

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
