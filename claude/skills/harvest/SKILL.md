---
name: harvest
description: >
  Cienki orkiestrator fazy harvest na końcu cyklu implement (przed commit).
  Sekwencyjnie uruchamia try-learn-skill (reużywalna procedura) → document-feature
  (docs modułu) → document-module (architektura modułu, tylko gdy zmiana
  architektury), każde z własnym gate. Jeden punkt wejścia zamiast osobnych
  nudge'y. Gracefully pomija sub-skill nieobecny w projekcie.
  TRIGGER when: "harvest", "faza harvest", "zbierz wiedzę z feature'a",
  "harvest this feature", po zakończonej implementacji przed commitem.
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(npx @mermaid-js/mermaid-cli:*), Write(**/.claude/skills/learned/**/*.md), Write(**/docs/modules/**/*.md), Write(**/docs/architecture/**/*.html)
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

Kolejność: `try-learn-skill` → `document-feature` → `document-module`. Sub-kroki
są niezależne i low-stakes; kolejność ustalona dla determinizmu (nie ma między
nimi zależności danych).

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

### KROK 3: document-module (architektura modułu — TYLKO przy zmianie architektury)

Sprawdź dostępność skilla `document-module`. Jeśli dostępny — dla każdego
dotkniętego modułu (zbiór z KROKU 2 / z diffa feature'a) **zbadaj diff i odpal
document-module TYLKO gdy feature zmienił architekturę modułu**. Sygnały zmiany
architektury (wystarczy jeden, per moduł):

- **nowy plik** dodany pod ścieżką modułu (`+++ b/{moduł}/...` nowy),
- **nowy publiczny element** — dodany eksport / publiczna klasa-metoda / endpoint
  (HTTP/RPC) / publikowany-konsumowany event,
- **nowa zależność** — dodany import innego top-level modułu/pakietu w plikach modułu.

Jeśli feature tylko edytował wnętrze / poprawił copy / refaktor bez zmiany
powierzchni → **pomiń ten moduł** (architektura się nie zmieniła, regeneracja =
hałas w diffie).

Dla modułów przechodzących bramkę uruchom `document-module {nazwa-modułu}`:

> Zregeneruj architekturę modułu ze skanu kodu (NEW jeśli brak `*-architecture.md`,
> w innym wypadku odśwież). Diagramy C4 (C1–C3) + flow, markdown (źródło prawdy)
> + regenerowalny HTML.

document-module sam tworzy NEW lub nadpisuje (markdown = aktualny skan, HTML =
regenerowalny). Echo granicy modułu zostaje po stronie document-module.

**Dlaczego bramka:** generacja diagramów jest niedeterministyczna — regen przy
KAŻDYM dotknięciu modułu puchłby diff nawet bez realnej zmiany architektury.
Bramka „tylko gdy zmiana architektury" trzyma diffy znaczące.

### Graceful degradation

Przed każdym sub-krokiem sprawdź, czy sub-skill jest dostępny. Jeśli projekt
zrezygnował z jednego (np. nie chce learned-skilli) → **pomiń go i kontynuuj**,
nie wywalaj się. Brak sub-skilla to normalna sytuacja, nie błąd.

---

## Closeout

Po sekwencji podaj zwięzłe podsumowanie:
- które sub-kroki się wykonały, które pominięto (i dlaczego),
- co powstało/zmieniło się (learned-skill? docs modułu? architektura modułu?),
- przy document-module: które moduły przeszły bramkę „zmiana architektury", a które pominięto,
- **przypomnienie: przejrzyj wynik w `git diff` przed commitem** — to naturalna
  powierzchnia review dla wszystkich sub-skilli.
- **opcjonalnie: po harvest możesz zarchiwizować/usunąć `planning-{slug}.md` i
  `tasks-{slug}.md`** — durable wiedza jest już w `docs/modules/` (jak działa) i
  learned-skillach (procedura). Warunek: istotne decyzje (alternatywy, *dlaczego
  nie*) są w ADR (`docs/adr/`), bo tego harvest NIE utrwala. Preferuj przeniesienie
  do `absolutpowers/archives/` zamiast kasowania (czysty `feature/` + audit trail);
  git history i tak zachowa oryginał.

## Zasady

- **Cienki orkiestrator** — deleguj, nie reimplementuj sub-skilli.
- **Każdy sub-skill zachowuje własny gate** — nie obchodź ani try-learn-skill
  (human gate), ani document-feature (mapping confirm).
- **document-module tylko przy zmianie architektury** — bramka (nowy plik /
  nowy publiczny element / nowa zależność) chroni przed hałaśliwym churnem;
  NEW lub UPDATE rozstrzyga document-module.
- **Graceful skip** — brakujący sub-skill = pomiń, nie crashuj.
- **Kolejność stała**: try-learn-skill → document-feature → document-module.
- **Codex parity**: mirror w `codex/` ma identyczne ciało bez `allowed-tools` /
  `argument-hint`.
