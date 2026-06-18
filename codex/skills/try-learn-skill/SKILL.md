---
name: try-learn-skill
description: >
  Ekstrahuje reużywalną procedurę z artefaktów zakończonego feature'a
  (planning + tasks + git diff) do wywoływalnego learned-skilla zapisanego
  w target-projekcie pod `.claude/skills/learned/`. Wykrywa procedurę
  generalizowalną, porównuje z istniejącymi learned-skillami (NEW vs UPDATE),
  pomija kolizje ze statycznymi skillami i czeka na akceptację przed zapisem.
  TRIGGER when: po zakończonej implementacji, "utrwal procedurę",
  "naucz się z tej pracy", "wyciągnij skill", "extract skill",
  "learn from this work", odpalany przez harvest.
---

# Try Learn Skill — Auto-ekstrakcja learned-skilla

Jesteś inżynierem-mentorem. Twoim zadaniem jest przyjrzeć się artefaktom
ZAKOŃCZONEGO feature'a i ocenić, czy da się z nich wyciągnąć **reużywalną
procedurę** — sekwencję kroków, którą dałoby się powtórzyć na INNYM zadaniu
tego samego typu. Jeśli tak, generujesz **learned-skill** zapisywany w
target-projekcie.

**To NIE jest implementacja.** Nie piszesz kodu produktu. Jedyne co zapisujesz
to plik `SKILL.md` w `.claude/skills/learned/` — i to dopiero po akceptacji
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

## KROK 2: Detekcja generalizowalnej procedury

Wyodrębnij z artefaktów **sekwencję kroków, narzędzi i decyzji**, która jest
powtarzalna na innym zadaniu tego samego typu (np. "dodanie nowego endpointu
CRUD z filtrowaniem", "mirror skilla Claude→Codex", "migracja pola w modelu").

Kryterium GENERALIZACJI (twarde):
- **Generalizowalne** = procedura działa dla klasy zadań, nie tylko dla tego
  konkretnego feature'a. Konkretne nazwy plików/pól tego feature'a to przykłady,
  nie istota procedury.
- **One-off** = czysto specyficzne dla tego feature'a, bez powtarzalnego wzorca.

Jeśli nic generalizowalnego → zaraportuj **"nic do utrwalenia"** z jednym
zdaniem uzasadnienia i zakończ BEZ zapisu.

## KROK 3: Wczytaj istniejące learned-skille

```
Glob: .claude/skills/learned/**/SKILL.md
```
w target-projekcie (katalog, z którego odpalono skill).

**Obsłuż brak katalogu**: zero learned-skilli (pusty wynik Glob lub brak
`.claude/skills/learned/`) → to normalna sytuacja, ścieżka domyślna = NEW.
**Nie zatrzymuj się** na pustym wyniku.

Dla każdego znalezionego learned-skilla odczytaj `description` (TRIGGER) i blok
`learned-meta` z ciała (origin, confidence, occurrences).

## KROK 4: NEW vs UPDATE

Porównaj wykrytą procedurę z istniejącymi learned-skillami:
- **Podobny learned-skill istnieje** (ta sama klasa procedury) → ścieżka **UPDATE**:
  merge/refine treści, podbij `occurrences` o 1, przy 2. spotkaniu podnieś
  `confidence: candidate → established`. Aktualizuj `last-updated`.
- **Brak podobnego** → ścieżka **NEW**: `confidence: candidate`, `occurrences: 1`.

## KROK 5: Collision-check vs skille STATYCZNE

Jeśli wykryta procedura pokrywa się z zakresem skilla STATYCZNEGO
(feature-discuss, generate-tasks, implement, review, triada-review, debug,
update-ai-context, explain, preboot…) → **SKIP**: zaraportuj
"to już robi skill X, pomijam" i zakończ BEZ zapisu. Nie duplikuj wbudowanej
funkcjonalności jako learned-skill.

Kolizja z innym **learned**-skillem → to nie SKIP, to ścieżka **UPDATE** (Krok 4).

## KROK 6: Propose — human gate

Pokaż użytkownikowi PEŁNĄ proponowaną treść `SKILL.md` (dla NEW) albo diff/opis
zmian (dla UPDATE), albo uzasadnienie SKIP. Zaznacz: NEW / UPDATE / SKIP, gdzie
trafi plik, jaki będzie `name` i `TRIGGER when:`.

**CZEKAJ NA AKCEPTACJĘ.** Nie zapisuj nic przed wyraźnym "ok / zapisz / tak"
(wzorzec propose → gate z `feature-discuss` i `update-ai-context`). Użytkownik
może skorygować treść/trigger przed zapisem.

## KROK 7: Write (po akceptacji)

Zapisz do target-projektu:
```
{target-project}/.claude/skills/learned/{name}/SKILL.md
```
- Utwórz katalog jeśli nie istnieje.
- `name` z prefiksem `learned-` (namespace), kebab-case: `learned-{descriptive-kebab}`.
- **Write celuje w `.claude/` TARGET projektu** (gdzie odpalono skill), NIE w repo
  AbsolutPowers.

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
source-feature: {slug}
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
confidence: candidate
occurrences: 1
-->

# [Tytuł procedury]

## Kiedy używać
[Klasa zadań, dla której to działa.]

## Procedura
1. [Krok — narzędzie, decyzja, odwołanie do pliku/wzorca projektu]
2. ...

## Pułapki / uwagi
- [Co poszło nie tak / na co uważać — z artefaktów feature'a]
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
blok `learned-meta` w ciele) jest identyczna.

---

## Zasady

- **Nie zapisuj bez akceptacji** (Krok 6 = twarda brama).
- **SKIP > duplikat**: kolizja ze statycznym skillem → pomiń, nie utrwalaj.
- **Brak materiału / brak generalizacji → zakończ czysto** bez tworzenia plików.
- **Write tylko do `.claude/skills/learned/`** target-projektu.
- Najpierw pokaż, potem pisz — użytkownik widzi cały plik przed zapisem.
