---
name: harvest
description: >
  Cienki orkiestrator fazy harvest na końcu cyklu implement (przed commit).
  Sekwencyjnie uruchamia try-learn-skill (obserwacja do ledgera kandydatów;
  learned-skill dopiero przy 2. wystąpieniu klasy lub fast-tracku) →
  document-feature (docs modułu) → document-module (architektura modułu, tylko
  gdy zmiana architektury) → archiwizacja artefaktów feature'a ze streszczeniem
  (za zgodą), każde z własnym gate. Jeden punkt wejścia zamiast osobnych
  nudge'y. Gracefully pomija sub-skill nieobecny w projekcie.
  TRIGGER when: "harvest", "faza harvest", "zbierz wiedzę z feature'a",
  "harvest this feature", po zakończonej implementacji przed commitem.
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

Kolejność: `try-learn-skill` → `document-feature` → `document-module` →
`archiwizacja`. Pierwsze trzy sub-kroki są niezależne i low-stakes; kolejność
ustalona dla determinizmu. Archiwizacja MUSI być ostatnia — przenosi artefakty,
z których wcześniejsze kroki jeszcze czytają.

### KROK 1: try-learn-skill (ledger kandydatów / promocja do learned-skilla)

Sprawdź dostępność skilla `try-learn-skill` (czy projekt go ma). Jeśli dostępny —
uruchom go na `$ARGUMENTS`:

> Oceń, czy artefakty tego feature'a zawierają nieoczywistą, reużywalną
> procedurę. Domyślny wynik przy pierwszym wystąpieniu klasy to WPIS W LEDGERZE
> (`.claude/skills/learned/_candidates.md`), nie skill. Pełny learned-skill
> powstaje przy drugim wystąpieniu tej klasy (promocja) albo przy silnym
> statycznym dowodzie reużycia (fast-track) — i tylko po human gate.

Oczekiwane wyniki tego kroku (wszystkie są poprawne, nie forsuj ekstrakcji):
- **nic do utrwalenia** — brak procedury lub nie przeszła testu nieoczywistości,
- **wpis w ledgerze** — pierwsze wystąpienie klasy, zapis bez gate (raportowany),
- **learned-skill NEW/UPDATE** — promocja (n≥2) lub fast-track; TYLKO po
  akceptacji użytkownika,
- **gotchas → document-feature** — wiedza o jednym module trafi do KROKU 2.

Human gate try-learn-skill dotyczy wyłącznie zapisu `SKILL.md`. Nie obchodź go.

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

### KROK 4: Archiwizacja artefaktów feature'a (ZAWSZE OSTATNI, za zgodą)

Po zebraniu wiedzy artefakty procesu (`planning-*.md`, `tasks-*.md`) przestają
być potrzebne w aktywnym `feature/` — zalegając, zaśmiecają katalog i mylą
kolejne sesje. Przenieś je do archiwum ze streszczeniem.

**Warunki wstępne (sprawdź, przy niespełnieniu POMIŃ krok z komunikatem):**
- wszystkie taski/fazy w `tasks-{slug}.md` (i phase files, jeśli orchestrated)
  mają `Status: completed`,
- dla epica: przenoś cały folder `feature/{epic-slug}/` TYLKO gdy wszystkie
  fazy epica są ukończone; w innym wypadku pomiń (epic w toku).

**Procedura:**
1. Zbuduj listę do przeniesienia: `planning-{slug}.md`, `tasks-{slug}.md`,
   katalog `tasks-{slug}/` (jeśli istnieje). Cel: `absolutpowers/archives/{slug}/`.
2. Wygeneruj streszczenie `absolutpowers/archives/{slug}/summary.md` — to jest
   „pamięć na przyszłość", pisana dla kogoś, kto za pół roku zapyta „co i
   dlaczego tu zrobiliśmy":

   ```markdown
   # {Feature} — streszczenie (zarchiwizowano YYYY-MM-DD)

   ## Co zbudowano
   [2-4 zdania: efekt, nie proces]

   ## Dlaczego (intent)
   [z planning doca — problem i cel biznesowy]

   ## Kluczowe decyzje i odrzucone alternatywy
   [z planning doca — decyzja → dlaczego; alternatywa → dlaczego NIE;
    linki do ADR jeśli istnieją]

   ## Acceptance Criteria
   [lista AC-N z jednozdaniowym statusem pokrycia]

   ## Gdzie jest trwała wiedza
   - docs modułów: [ścieżki z KROKU 2]
   - architektura: [ścieżki z KROKU 3, jeśli powstały]
   - learned-skill / ledger: [wynik KROKU 1]
   - ADR: [ścieżki]
   ```
3. **Ostrzeżenie ADR:** jeśli planning doc zawiera istotne decyzje
   architektoniczne, a nie ma odpowiadającego ADR w `docs/adr/` — powiedz to
   wprost przed przeniesieniem (streszczenie utrwala esencję, ale ADR to
   właściwe miejsce na decyzje wiążące przyszłość).
4. **Gate:** pokaż listę plików do przeniesienia + pełne streszczenie. CZEKAJ
   na akceptację. User może pominąć archiwizację — to nadal krok opcjonalny.
5. Po akceptacji: `mkdir -p absolutpowers/archives/{slug}` → `git mv` każdego
   artefaktu (fallback na zwykłe `mv` dla plików untracked) → zapisz
   `summary.md`. NIE commituj — przeniesienie wejdzie do commita feature'a
   (naturalna powierzchnia review w `git diff`).

**Hard boundary:** archiwizacja przenosi i streszcza WYŁĄCZNIE artefakty tego
feature'a. Nie dotyka `reviews/`, `problem/`, `constitution.md`, `rules.md`,
`patterns.md` ani cudzych feature'ów.

### Graceful degradation

Przed każdym sub-krokiem sprawdź, czy sub-skill jest dostępny. Jeśli projekt
zrezygnował z jednego (np. nie chce learned-skilli) → **pomiń go i kontynuuj**,
nie wywalaj się. Brak sub-skilla to normalna sytuacja, nie błąd.

---

## Closeout

Po sekwencji podaj zwięzłe podsumowanie:
- które sub-kroki się wykonały, które pominięto (i dlaczego),
- co powstało/zmieniło się (wpis w ledgerze kandydatów? learned-skill?
  docs modułu? architektura modułu?),
- przy try-learn-skill: pokaż dodany wpis ledgera (jeśli powstał) i wynik GC
  ledgera (wpisy zaproponowane do usunięcia),
- przy document-module: które moduły przeszły bramkę „zmiana architektury", a które pominięto,
- przy archiwizacji: co przeniesiono do `archives/{slug}/` (albo dlaczego
  pominięto — np. taski niedokończone, brak zgody),
- **przypomnienie: przejrzyj wynik w `git diff` przed commitem** — to naturalna
  powierzchnia review dla wszystkich sub-kroków,
- **nudge: `/absolutpowers:ship`** — wygeneruje commit message i opis PR
  z artefaktów feature'a (jeden best-effort nudge, jak `implement` → `harvest`).

## Zasady

- **Cienki orkiestrator** — deleguj, nie reimplementuj sub-skilli.
- **Każdy sub-skill zachowuje własny gate** — nie obchodź ani try-learn-skill
  (human gate na SKILL.md), ani document-feature (mapping confirm), ani
  archiwizacji (akceptacja listy + streszczenia). Wpis do ledgera kandydatów
  jest bez gate — to zamierzone (niskie ryzyko, raportowany).
- **Nie forsuj ekstrakcji skilla** — „nic do utrwalenia" i „tylko wpis w
  ledgerze" to poprawne, oczekiwane wyniki KROKU 1 dla większości feature'ów.
- **Archiwizacja ZAWSZE ostatnia i tylko dla ukończonych feature'ów** —
  niedokończone taski / epic w toku = pomiń z komunikatem, nie przenoś połowicznie.
- **document-module tylko przy zmianie architektury** — bramka (nowy plik /
  nowy publiczny element / nowa zależność) chroni przed hałaśliwym churnem;
  NEW lub UPDATE rozstrzyga document-module.
- **Graceful skip** — brakujący sub-skill = pomiń, nie crashuj.
- **Kolejność stała**: try-learn-skill → document-feature → document-module → archiwizacja.
- **Codex parity**: mirror w `codex/` ma identyczne ciało bez `allowed-tools` /
  `argument-hint`.
