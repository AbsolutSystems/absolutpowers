---
name: harvest
description: >
  Cienki orkiestrator fazy harvest na końcu cyklu implement (przed commit).
  Sekwencyjnie uruchamia try-learn-skill (reużywalna procedura) → document-feature
  (docs modułu), każde z własnym gate. Jeden punkt wejścia zamiast dwóch
  osobnych nudge'y. Gracefully pomija sub-skill nieobecny w projekcie.
  TRIGGER when: "harvest", "faza harvest", "zbierz wiedzę z feature'a",
  "harvest this feature", po zakończonej implementacji przed commitem.
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md), Write(**/docs/modules/**/*.md)
argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"
---

# Harvest — Orkiestrator fazy harvest

Jesteś orkiestratorem zbioru wiedzy po zakończonym feature. Twoje zadanie to
**cienko** poprowadzić dwa sub-skille po artefaktach feature'a, każdy z jego
WŁASNYM gate. Sam nie implementujesz logiki sub-skilli — delegujesz.

**MNIEJ = WIĘCEJ.** Brak changelogów, brak sekcji historii, brak duplikowania
logiki sub-skilli. Harvest to tylko deterministyczna sekwencja + closeout.

## Wejście

Argument `$ARGUMENTS` = ścieżka do artefaktu feature'a (zwykle `tasks-{slug}.md`
lub `planning-{slug}.md`). Przekazujesz ją do każdego sub-skilla bez zmian.

$ARGUMENTS

---

## Sekwencja (kolejność deterministyczna)

Kolejność: `try-learn-skill` → `document-feature`. Sub-kroki są niezależne i
low-stakes; kolejność ustalona dla determinizmu (nie ma między nimi zależności
danych).

### KROK 1: try-learn-skill (reużywalna procedura)

Sprawdź dostępność skilla `try-learn-skill` (czy projekt go ma). Jeśli dostępny —
uruchom go na `$ARGUMENTS`:

> Wyodrębnij reużywalną procedurę z artefaktów tego feature'a.
> (Skill ma własny human gate — czeka na akceptację przed zapisem learned-skilla.)

Skill zachowuje swój własny gate (propose → akceptacja → zapis do
`.claude/skills/learned/`). Nie obchodź go.

### KROK 2: document-feature (docs modułu)

Sprawdź dostępność skilla `document-feature`. Jeśli dostępny — uruchom go na
`$ARGUMENTS`:

> Zaktualizuj/utwórz dokumentację dotkniętych modułów.
> (Skill ma własny twardy gate — potwierdzenie mapowania plik→moduł przed zapisem.)

Skill zachowuje swój własny gate (mapping confirm; treść = auto-write do
`docs/modules/`). Nie obchodź go.

### Graceful degradation

Przed każdym sub-krokiem sprawdź, czy sub-skill jest dostępny. Jeśli projekt
zrezygnował z jednego (np. nie chce learned-skilli) → **pomiń go i kontynuuj**,
nie wywalaj się. Brak sub-skilla to normalna sytuacja, nie błąd.

---

## Closeout

Po sekwencji podaj zwięzłe podsumowanie:
- które sub-kroki się wykonały, które pominięto (i dlaczego),
- co powstało/zmieniło się (learned-skill? docs modułu?),
- **przypomnienie: przejrzyj wynik w `git diff` przed commitem** — to naturalna
  powierzchnia review dla obu sub-skilli.
- **opcjonalnie: po harvest możesz zarchiwizować/usunąć `planning-{slug}.md` i
  `tasks-{slug}.md`** — durable wiedza jest już w `docs/modules/` (jak działa) i
  learned-skillach (procedura). Warunek: istotne decyzje (alternatywy, *dlaczego
  nie*) są w ADR (`docs/adr/`), bo tego harvest NIE utrwala. Preferuj przeniesienie
  do `absolutpowers/archiwa/` zamiast kasowania (czysty `feature/` + audit trail);
  git history i tak zachowa oryginał.

## Zasady

- **Cienki orkiestrator** — deleguj, nie reimplementuj sub-skilli.
- **Każdy sub-skill zachowuje własny gate** — nie obchodź ani try-learn-skill
  (human gate), ani document-feature (mapping confirm).
- **Graceful skip** — brakujący sub-skill = pomiń, nie crashuj.
- **Kolejność stała**: try-learn-skill → document-feature.
- **Codex parity**: mirror w `codex/` ma identyczne ciało bez `allowed-tools` /
  `argument-hint`.
