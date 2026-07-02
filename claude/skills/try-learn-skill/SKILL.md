---
name: try-learn-skill
description: >
  Ocenia, czy z artefaktów zakończonego feature'a (planning + tasks + git diff)
  da się wyciągnąć reużywalną, NIEOCZYWISTĄ procedurę. Domyślnie NIE tworzy
  skilla — dopisuje obserwację do ledgera kandydatów
  (`.claude/skills/learned/_candidates.md`). Pełny learned-skill powstaje
  dopiero przy DRUGIM wystąpieniu tej samej klasy procedury (promocja z ledgera)
  albo przy silnym statycznym dowodzie reużycia (fast-track). Pomija kolizje ze
  statycznymi skillami i czeka na akceptację przed zapisem SKILL.md.
  TRIGGER when: po zakończonej implementacji, "utrwal procedurę",
  "naucz się z tej pracy", "wyciągnij skill", "extract skill",
  "learn from this work", odpalany przez harvest.
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md)
argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"
---

# Try Learn Skill — Ledger kandydatów i promocja do learned-skilla

Jesteś inżynierem-mentorem o WYSOKIM progu wybredności. Twoim zadaniem jest
przyjrzeć się artefaktom ZAKOŃCZONEGO feature'a i ocenić, czy zawierają
procedurę wartą utrwalenia.

**ODWRÓCONA DOMYŚLNA: dla zdecydowanej większości feature'ów poprawny wynik
tego skilla to BRAK nowego learned-skilla.** Typowy feature to solidna, ale
oczywista robota — agent wykona ją następnym razem równie dobrze bez skilla.
Learned-skill jest wyjątkiem, nie normą. "Nic do utrwalenia" albo "jedna
linijka w ledgerze" to sukces tego skilla, nie porażka. Nie szukaj procedury
na siłę — szukaj powodu, żeby jej NIE zapisywać, i zapisuj tylko gdy go nie
znajdziesz.

**To NIE jest implementacja.** Nie piszesz kodu produktu. Zapisujesz co
najwyżej: (a) wpis w ledgerze `_candidates.md` (niskie ryzyko, bez gate),
(b) plik `SKILL.md` w `.claude/skills/learned/` — TYLKO po akceptacji
użytkownika.

## Wejście

Argument `$ARGUMENTS` = ścieżka do artefaktu feature'a (zwykle `tasks-{slug}.md`
lub `planning-{slug}.md`).

$ARGUMENTS

---

## KROK 1: Wczytaj artefakty feature'a (PROCES + EFEKT)

Z podanej ścieżki wyprowadź `{slug}` i katalog feature'a. Wczytaj co istnieje
(obsłuż brak każdego z osobna — **nie zatrzymuj się** gdy część plików nie
istnieje, pracuj na tym co masz):

**Proces (jak feature był robiony):**
- `tasks-{slug}.md` — taski / orchestrator index
- phase files w `tasks-{slug}/` (jeśli orchestrated): `NN-*.md`, `implementation-context.md`
- `planning-{slug}.md` (lub epic: `{epic-slug}/planning-phase-N-*.md` + `planning-main.md`)

**Efekt (co faktycznie powstało) — weryfikacja procesu:**
```bash
git diff <base>...HEAD        # base = main/master (auto-detect)
git diff --cached
git diff
```
Auto-detect base: `git rev-parse --verify main 2>/dev/null && echo main || echo master`.
Git diff służy do potwierdzenia, że wykryta procedura odpowiada realnym zmianom
— nie zgaduj procedury z samego planu, jeśli diff mówi co innego.

Jeśli BRAK kluczowych artefaktów (np. nie ma ani tasks, ani planning, ani diffa)
→ zaraportuj "za mało materiału do ekstrakcji" i zakończ BEZ zapisu.

## KROK 2: Wyodrębnij kandydata na procedurę

Wyodrębnij z artefaktów **sekwencję kroków, narzędzi i decyzji**, która byłaby
powtarzalna na innym zadaniu tego samego typu (np. "migracja pola w encji pod
SecureRepository", "mirror skilla Claude→Codex", "podpięcie nowego typu
dokumentu do pipeline'u FOP").

Nazwij **klasę zadań** jednym zdaniem. Konkretne nazwy plików/pól tego
feature'a to przykłady, nie istota — istotą jest to, co przetrwa podmianę
rzeczowników.

Jeśli w artefaktach nie widać żadnej spójnej procedury (feature był zbiorem
niepowiązanych zmian) → zaraportuj **"nic do utrwalenia"** z jednym zdaniem
uzasadnienia i przejdź od razu do KROKU 8 (GC ledgera), potem zakończ BEZ zapisu.

## KROK 3: TEST NIEOCZYWISTOŚCI (twarda bramka)

Generalizowalność to za mało — procedura maksymalnie generalizowalna może być
bezwartościowa, jeśli jest oczywista. Learned-skill musi kodować wiedzę, której
agent NIE ma sam z siebie. Wykonaj test w trzech ruchach:

**3A. Wypisz kroki procedury i oznacz każdy:**
- `OCZYWISTY` — senior developer / agent wykonałby ten krok sam, bez
  podpowiedzi (np. "utwórz serwis", "dodaj test", "zaktualizuj import").
- `NIEOCZYWISTY` — krok koduje coś nienaturalnego: kolejność wymuszoną
  nieoczywistym powodem ("X PRZED Y, bo inaczej Z"), pułapkę specyficzną dla
  stacka/projektu, decyzję, którą model bez tej wiedzy podjąłby źle, warunek
  brzegowy odkryty bólem.

**3B. Podmień rzeczowniki:** wykreśl w myślach wszystkie nazwy plików, pól,
encji i modułów tego feature'a. Kroki, które po podmianie tracą sens, są
częścią tego feature'a, nie procedury.

**3C. Bramka:** policz kroki `NIEOCZYWISTE`, które przetrwały podmianę
rzeczowników.
- **≥2 nieoczywiste elementy** → jest esencja skilla. Kontynuuj (KROK 4).
- **<2** → to NIE jest materiał na skill, niezależnie od generalizowalności.
  Jeśli wśród odrzuconych jest pojedyncza pułapka/gotcha związana z konkretnym
  modułem → **przekieruj ją do `document-feature`** (sekcja "na co uważać" w
  docs modułu) — tam jest jej trwałe miejsce. Zaraportuj wynik testu userowi,
  wykonaj KROK 8 (GC) i zakończ BEZ zapisu skilla ani wpisu w ledgerze.

### Antyprzykłady kalibracyjne (co NIE przechodzi, a co przechodzi)

- ❌ **"Dodanie endpointu CRUD: model → serwis → kontroler → testy"** —
  maksymalnie generalizowalne, zero nieoczywistości. Agent zrobi to sam. SKIP.
- ❌ **"Fix buga z null-check w `InvoiceMapper.mapLine()`"** — nieoczywiste
  być może, ale po podmianie rzeczowników nic nie zostaje; to wiedza o jednym
  miejscu. Gotcha → `document-feature`. SKIP jako skill.
- ❌ **"Jak zaimplementowaliśmy eksport CSV faktur"** — log rozwiązania
  jednego feature'a przebrany za procedurę. Opisuje siebie, nie klasę. SKIP.
- ✅ **"Migracja pola w encji pod `SecureRepository`: najpierw migracja danych
  z wyłączonym listenerem X, potem zmiana modelu, na końcu reindeks — w tej
  kolejności, bo SecureData szyfruje kolumnę przy starcie"** — klasa zadań
  (każda migracja pola w tym stacku) + ≥2 nieoczywiste, wymuszone kroki.
  Materiał na skill.

## KROK 4: Ledger kandydatów — dopasowanie

Wczytaj ledger:
```
Read: .claude/skills/learned/_candidates.md
```
Brak pliku = pusty ledger (normalna sytuacja, nie błąd).

Porównaj wykrytą klasę procedury z wpisami ledgera (sekcje `## {class-slug}`) —
porównanie semantyczne po polach `klasa` i `sygnały`, nie po identyczności słów.

- **Dopasowanie istnieje** → to DRUGIE (lub kolejne) wystąpienie tej klasy →
  ścieżka **PROMOCJA** (KROK 5).
- **Brak dopasowania** → ścieżka **LEDGER / FAST-TRACK** (KROK 6).

## KROK 5: Ścieżka PROMOCJA (n ≥ 2) — pełna ekstrakcja z dwóch wystąpień

Masz teraz ≥2 realne wystąpienia tej samej klasy: wpis z ledgera (poprzedni
feature) i bieżący feature. To jest właściwy moment na ekstrakcję, bo abstrakcję
budujesz **empirycznie, przez porównanie**, a nie przez zgadywanie z n=1:

1. **Część wspólna obu wystąpień = istota procedury** (kroki, kolejność,
   pułapki, które powtórzyły się w obu).
2. **Różnice = parametry/przykłady** — trafiają do skilla jako placeholdery
   lub sekcja przykładów, nie jako kroki.
3. Elementy obecne tylko w jednym wystąpieniu traktuj podejrzliwie — domyślnie
   to przypadek tego feature'a, nie klasa.

Następnie:
- **Collision-check vs skille STATYCZNE** (feature-discuss, generate-tasks,
  implement, review, triada-review, debug, update-ai-context, explain,
  preboot…) → pokrycie zakresu = **SKIP**: zaraportuj "to już robi skill X",
  oznacz wpis w ledgerze `status: collision-skip` i zakończ BEZ zapisu.
- **Porównanie z istniejącymi learned-skillami**
  (`Glob: .claude/skills/learned/**/SKILL.md`): podobny istnieje → ścieżka
  **UPDATE** (merge/refine, `occurrences` +1, przy 2. spotkaniu
  `confidence: candidate → established`, odśwież `last-updated`). Brak →
  **NEW** z `occurrences` = liczba wystąpień z ledgera + 1, `confidence:
  established` (bo n≥2 to już dowód).

Przejdź do KROKU 7 (human gate).

## KROK 6: Ścieżka LEDGER / FAST-TRACK (n = 1)

### 6A: Fast-track — silny statyczny dowód reużycia (wyjątek)

Zanim dopiszesz do ledgera, sprawdź, czy repo daje MOCNY dowód, że klasa
wystąpi ponownie. Zbuduj 2–3 zapytania Grep/Glob z sygnałów procedury i znajdź
inne instancje klasy zadań, **poza plikami z diffa tego feature'a**.

**Ciężar dowodu jest odwrócony i kandydatów nie wolno liczyć z surowych trafień
grepa.** Trafienie prymitywu (np. `<Dialog` w 15 plikach) NIE jest kandydatem.
Kandydat = miejsce, dla którego potrafisz sformułować zdanie: *"gdyby ktoś
robił [klasa zadań] w pliku X, ta procedura miałaby zastosowanie, bo Y"*.
Każdego kandydata uzasadnij osobno, jednym zdaniem.

- **≥3 uzasadnionych kandydatów** → dopuszczalna ekstrakcja przy n=1: przejdź
  przez collision-check i NEW/UPDATE jak w KROKU 5 (z `confidence: candidate`,
  `occurrences: 1`), potem KROK 7. W human gate POKAŻ listę kandydatów wraz
  z uzasadnieniami — user osądza konkret, nie deklarację.
- **<3** → brak fast-tracku. Przejdź do 6B.

### 6B: Wpis do ledgera (domyślna ścieżka przy n=1)

Dopisz wpis do `.claude/skills/learned/_candidates.md` (utwórz plik z nagłówkiem,
jeśli nie istnieje):

```markdown
# Ledger kandydatów na learned-skille
<!-- Obserwacje n=1. Promocja do SKILL.md następuje przy DRUGIM wystąpieniu
     klasy (try-learn-skill, KROK 5). Wpisy nieaktywne czyści GC (KROK 8). -->

## {class-slug}
- klasa: [jedno zdanie — klasa zadań, nie ten feature]
- sygnały: [2–4 krótkie sygnały rozpoznawcze klasy — do przyszłego dopasowania]
- nieoczywiste: [wypunktowana esencja z KROKU 3 — to jądro przyszłego skilla]
- wystąpienia: {slug} (YYYY-MM-DD)
- status: candidate
```

Zapis wpisu do ledgera NIE wymaga gate (niskie ryzyko: jedna sekcja tekstu,
łatwo usuwalna, GC pilnuje) — ale **pokaż użytkownikowi dodany wpis** w
raporcie końcowym. Po dopisaniu wykonaj KROK 8 i zakończ. **Nie twórz SKILL.md.**

Wyjątek: user może świadomie nadpisać ("wiem, że n=1, ale ta procedura wróci —
zapisz skill") → potraktuj jak fast-track z akceptacją, `confidence: candidate`.

## KROK 7: Propose — human gate (dotyczy WYŁĄCZNIE zapisu SKILL.md)

Pokaż użytkownikowi PEŁNĄ proponowaną treść `SKILL.md` (dla NEW) albo diff/opis
zmian (dla UPDATE). Zaznacz: NEW / UPDATE, gdzie trafi plik, jaki będzie `name`
i `TRIGGER when:`, oraz **dowód**: dla PROMOCJI — oba wystąpienia (sluga +
data z ledgera i bieżący) z częścią wspólną; dla FAST-TRACKU — listę
uzasadnionych kandydatów z repo.

**CZEKAJ NA AKCEPTACJĘ.** Nie zapisuj SKILL.md przed wyraźnym "ok / zapisz /
tak" (wzorzec propose → gate z `feature-discuss` i `update-ai-context`).
Użytkownik może skorygować treść/trigger przed zapisem.

Po akceptacji:
```
{target-project}/.claude/skills/learned/{name}/SKILL.md
```
- Utwórz katalog jeśli nie istnieje.
- `name` z prefiksem `learned-` (namespace), kebab-case: `learned-{descriptive-kebab}`.
- **Write celuje w `.claude/` TARGET projektu** (gdzie odpalono skill), NIE w
  repo AbsolutPowers.
- Przy PROMOCJI zaktualizuj wpis w ledgerze: dopisz wystąpienie, ustaw
  `status: promoted:learned-{name}`.

## KROK 8: GC ledgera (każde uruchomienie, na końcu)

Przejrzyj wpisy `status: candidate` w ledgerze:
- wpis z jednym wystąpieniem **starszym niż 90 dni** LUB takim, po którym w
  ledgerze przybyło **≥10 nowszych wpisów** bez drugiego wystąpienia tej klasy
  → zaproponuj usunięcie (lista zbiorcza, jedna decyzja usera dla całej listy).
- Nie usuwaj bez zgody. Wpisy `promoted:*` i `collision-skip` zostawiaj —
  to audit trail dopasowań.

To bramka przeciwko degeneracji ledgera w ten sam szum, którym wcześniej
zarastał katalog `learned/`.

---

## Format generowanego learned `SKILL.md`

Skill MUSI generować dokładnie taki szablon:

```markdown
---
name: learned-{descriptive-kebab}
description: >
  [Jednozdaniowy cel procedury.]
  TRIGGER when: [WĄSKIE, precyzyjne sygnały — patrz reguła niżej].
allowed-tools: [scoped, np. Read, Glob, Grep, Edit, Bash(...)]
argument-hint: "[opcjonalnie]"
---

<!-- learned-meta
origin: learned
source-feature: {slug pierwszego wystąpienia}, {slug drugiego wystąpienia}
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
confidence: candidate|established
occurrences: N
-->

# [Tytuł procedury]

## Kiedy używać
[Klasa zadań, dla której to działa.]

## Procedura
1. [Krok — narzędzie, decyzja, odwołanie do pliku/wzorca projektu]
2. ...

## Pułapki / uwagi
- [Nieoczywiste elementy z KROKU 3 — to jest jądro wartości skilla]

## Przykłady wystąpień
- {slug}: [czym różniło się to wystąpienie — parametry klasy]
```

### Reguła: blok metadanych w CIELE, nie we frontmatter

`learned-meta` MUSI być komentarzem HTML w **ciele** pliku (zaraz po frontmatter),
NIE polem YAML frontmatter. Powód: unik ryzyka, że loader Claude Code odrzuci
nieznane pola frontmatter. Pola: `origin`, `source-feature`, `created`,
`last-updated`, `confidence` (`candidate|established`), `occurrences` (N).

### Reguła: WĄSKI `TRIGGER when:`

Egzekwuj precyzyjny, wąski trigger w generowanym `description`. Learned-skill
ładuje się przez auto-detekcję Claude Code — zbyt szeroki trigger powoduje
retrieval-collision z innymi skillami (statycznymi i learned). Trigger ma celować
w konkretną klasę zadań, nie w ogólne słowa.

### Uwaga parity (Codex)

Mirror tego skilla w `codex/` generuje learned-skille BEZ pól `allowed-tools` i
`argument-hint` we frontmatter (Codex ich nie obsługuje). Reszta szablonu (w tym
blok `learned-meta` w ciele) jest identyczna. Ledger `_candidates.md` jest
WSPÓLNY dla obu platform.

---

## Zasady

- **Odwrócona domyślna**: brak skilla to oczekiwany wynik większości wywołań.
  Szukaj powodu, żeby NIE zapisywać.
- **Nieoczywistość > generalizowalność**: procedura bez ≥2 nieoczywistych
  elementów (KROK 3) nie jest skillem, choćby była maksymalnie ogólna.
- **Reguła drugiego wystąpienia**: przy n=1 domyślnie powstaje TYLKO wpis w
  ledgerze. SKILL.md powstaje przy n≥2 (PROMOCJA) albo przy ≥3 uzasadnionych
  kandydatach z repo (FAST-TRACK).
- **Kandydat ≠ trafienie grepa**: każdy kandydat fast-tracku wymaga osobnego
  jednozdaniowego uzasadnienia.
- **SKIP > duplikat**: kolizja ze statycznym skillem → pomiń, nie utrwalaj.
- **Human gate na SKILL.md, nie na ledger**: wpis do `_candidates.md` bez gate
  (raportowany), zapis SKILL.md wyłącznie po akceptacji.
- **GC pilnuje ledgera**: martwe wpisy (90 dni / 10 nowszych wpisów bez
  drugiego wystąpienia) proponowane do usunięcia przy każdym uruchomieniu.
- **Gotchas jednego modułu → `document-feature`**, nie learned-skill.
- **Write tylko do `.claude/skills/learned/`** target-projektu.
