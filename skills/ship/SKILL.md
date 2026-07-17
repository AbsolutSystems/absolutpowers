---
name: ship
description: >
  Domknięcie feature'a: generuje conventional-commit message i opis PR
  z artefaktów pipeline'u (planning + tasks + AC + diff), za zgodą archiwizuje
  artefakty feature'a i wykonuje lokalny commit. NIE pushuje, NIE tworzy PR bez
  wyraźnego polecenia, NIE zmienia kodu. Naturalny krok po review.
  TRIGGER when: "ship", "commit tego feature'a", "przygotuj commit",
  "napisz commit message", "opis PR", "przygotuj PR", "domknij feature",
  gotowe do commita zmiany feature'a.
  NIE wyzwalaj na: eksport tasków do issue trackera (usunięte celowo w 3.10.0)
  ani na review kodu (to `review`).
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(gh auth:*), Bash(gh pr:*), Bash(mkdir:*), Bash(mv:*), Write(**/absolutpowers/archives/**/*.md)
argument-hint: "[ścieżka do tasks-*.md; puste = autodetekcja z brancha]"
---

# Ship — Commit i opis PR z artefaktów feature'a

Jesteś inżynierem domykającym feature. Cała historia zmiany już istnieje w
artefaktach pipeline'u — intent w planning docu, zakres w taskach, weryfikacja
w AC. Twoje zadanie to **przełożyć ją na commit message i opis PR**, których
nie trzeba pisać ręcznie ani zgadywać z diffa.

**Hard boundary (nie przekraczaj):**
- NIE zmieniasz kodu, NIE dotykasz statusów w tasks-docach (to `implement`).
- NIE pushujesz. Commit jest lokalny; push to decyzja i ruch użytkownika.
- NIE tworzysz PR z własnej inicjatywy — `gh pr create` wyłącznie gdy
  użytkownik wprost o to poprosi, i dopiero po `gh auth status` OK.
- NIE tworzysz issues (outward bridge usunięto świadomie w 3.10.0).

## Wejście

Argument `$ARGUMENTS` = ścieżka do `tasks-{slug}.md` (opcjonalnie).

$ARGUMENTS

---

## KROK 1: Ustal feature i wczytaj artefakty

**Slug:** z `$ARGUMENTS`, a gdy puste — autodetekcja: dopasuj nazwę bieżącego
brancha do slugów w `absolutpowers/feature/` (a także `absolutpowers/archives/`
na wypadek wcześniejszego, ręcznego archiwum). Przy wielu kandydatach — zapytaj,
nie zgaduj. Przy zerze kandydatów — pracuj na samym diffie i powiedz to wprost
(commit będzie uboższy o intent).

**Wczytaj co istnieje** (obsłuż brak każdego z osobna):
- `planning-{slug}.md` — intent, wybrane rozwiązanie, odrzucone alternatywy
- `tasks-{slug}.md` + phase files — zakres, `Traces to:`, decyzje implementacyjne
- sekcja `## Acceptance Criteria` — lista AC-N
- diff: `git diff <base>...HEAD` + `git status --short`
  (base auto-detect: `git rev-parse --verify main 2>/dev/null && echo main || echo master`)

**Sanity-check spójności:** diff jest źródłem prawdy o tym, co faktycznie
wchodzi do commita. Jeśli diff zawiera zmiany wykraczające poza zakres tasków
(pliki spoza feature'a) — wypunktuj je i zapytaj, czy mają wejść do tego commita.

## KROK 2: Pre-flight

- `git status` — jeśli brak jakichkolwiek zmian (staged + unstaged + untracked)
  → zaraportuj "nic do commitowania" i zakończ.
- Zbuduj proponowaną listę plików do `git add` (unstaged/untracked należące do
  feature'a, w tym przeniesienia artefaktów z własnego kroku archiwizacji ship
  — KROK 4.5 — i `archives/{slug}/summary.md`).
  **Niczego nie stage'uj przed akceptacją w KROKU 5.**
- Jeśli na branchu są już commity feature'a — zaznacz, że to commit domykający
  (nie squashuj, nie przepisuj historii; `rebase`/`squash` to decyzja usera
  poza tym skillem).

## KROK 3: Wygeneruj commit message

Format conventional commits:

```
{type}({scope}): {subject — imperatyw, ≤72 znaki, bez kropki}

{body: 2-5 zdań — CO i DLACZEGO z planning doca, nie JAK z diffa.
 Nieoczywiste decyzje implementacyjne z tasks-doca, jeśli wpływają
 na czytającego historię.}

Feature: {slug}
AC: {AC-1..AC-N pokryte | brak sekcji AC}
```

- `type`: `feat` (nowa funkcjonalność), `fix` (planning-fix-*), `refactor`,
  `chore` — wyprowadź z charakteru planning doca, nie zgaduj z diffa.
- `scope`: dominujący moduł z diffa (opcjonalny, gdy jednoznaczny).
- Subject opisuje efekt dla użytkownika/systemu, nie proces
  ("add CSV export with filtering", nie "implement tasks from planning doc").

## KROK 4: Wygeneruj opis PR

```markdown
## TL;DR
[1-2 zdania: co i po co]

## Kontekst i intent
[z planning doca: problem, cel, wybrane rozwiązanie; 1 zdanie o odrzuconych
 alternatywach z linkiem do ADR jeśli istnieje]

## Zakres zmian
[3-6 punktów po modułach/warstwach — z tasks-doca skonfrontowanego z diffem]

## Acceptance Criteria
- [ ] AC-1: [treść] — [gdzie zweryfikowane: test/plik]
- [ ] AC-N: ...
[checkboxy odhaczone tam, gdzie tasks-doc/final-verification potwierdza pokrycie]

## Jak testowane
[verification commands z tasks-doca + wynik 99-final-verification jeśli orchestrated]

## Ryzyka / rollback
[z planning doca i faz oznaczonych Risk: high; "brak istotnych" jeśli czysto]

## Artefakty
[ścieżki: planning/tasks albo archives/{slug}/, raport review jeśli istnieje]
```

Sekcje bez materiału pomiń w całości — nie zostawiaj pustych nagłówków ani
placeholderów.

## KROK 4.5: Archiwizacja artefaktów feature'a (za zgodą)

Ship jest teraz jedynym miejscem archiwizacji artefaktów procesu — po domknięciu
feature'a `planning-*.md`/`tasks-*.md` przestają być potrzebne w aktywnym
`feature/` (zalegając, zaśmiecają katalog i mylą kolejne sesje). Przenieś je do
archiwum ze streszczeniem. Przeniesienie wchodzi do commita domykającego (KROK 6),
więc jest widoczne w `git diff` jako naturalna powierzchnia review.

**Warunki wstępne (przy niespełnieniu POMIŃ ten krok z komunikatem):**
- wszystkie taski/fazy w `tasks-{slug}.md` (i phase files, jeśli orchestrated) mają `Status: completed`,
- dla epica: przenoś cały folder `feature/{epic-slug}/` TYLKO gdy wszystkie fazy epica ukończone; inaczej pomiń (epic w toku),
- gdy brak artefaktów feature'a (praca z samego diffa) → pomiń, nie ma czego archiwizować.

**Procedura (przygotowanie — sam `mv` w KROKU 6, po akceptacji):**
1. Zbuduj listę do przeniesienia: `planning-{slug}.md`, `tasks-{slug}.md`,
   katalog `tasks-{slug}/` (jeśli istnieje). Cel: `absolutpowers/archives/{slug}/`.
2. Wygeneruj treść `absolutpowers/archives/{slug}/summary.md` — „pamięć na
   przyszłość" dla kogoś, kto za pół roku zapyta „co i dlaczego tu zrobiliśmy":

   ```markdown
   # {Feature} — streszczenie (zarchiwizowano YYYY-MM-DD)

   ## Co zbudowano
   [2-4 zdania: efekt, nie proces]

   ## Dlaczego (intent)
   [z planning doca — problem i cel biznesowy]

   ## Kluczowe decyzje i odrzucone alternatywy
   [z planning doca — decyzja → dlaczego; alternatywa → dlaczego NIE; linki do ADR]

   ## Acceptance Criteria
   [lista AC-N z jednozdaniowym statusem pokrycia]

   ## Gdzie jest trwała wiedza
   - docs modułów / architektura / learned-skille / ADR: [ścieżki, jeśli istnieją]
   ```
3. **Ostrzeżenie ADR:** jeśli planning doc zawiera istotne decyzje
   architektoniczne, a nie ma odpowiadającego ADR w `docs/adr/` — powiedz to
   wprost przed przeniesieniem (streszczenie utrwala esencję, ale ADR to właściwe
   miejsce na decyzje wiążące przyszłość).

**Hard boundary:** archiwizacja przenosi i streszcza WYŁĄCZNIE artefakty tego
feature'a (`planning-{slug}.md`, `tasks-{slug}.md`, katalog fazowy). NIE dotyka
`reviews/`, `problem/`, `constitution.md`, `rules.md`, `patterns.md` ani cudzych
feature'ów.

## KROK 5: Human gate

Pokaż razem: (a) listę plików do `git add`, (b) pełny commit message,
(c) pełny opis PR, (d) **archiwizację** — listę plików do przeniesienia do
`archives/{slug}/` + pełne streszczenie `summary.md` (albo notę, że archiwizację
pominięto i dlaczego). **CZEKAJ NA AKCEPTACJĘ.** User może skorygować każdy
element — w tym zrezygnować z samej archiwizacji, zachowując resztę. Brak ścieżki
cichej archiwizacji: żaden `mv`/`git mv` nie wykonuje się przed tą akceptacją.

## KROK 6: Wykonanie (po akceptacji)

1. **Archiwizacja (jeśli zaakceptowana w KROKU 5):** `mkdir -p absolutpowers/archives/{slug}`
   → `git mv` każdego artefaktu (fallback na zwykłe `mv` dla plików untracked)
   → zapisz `summary.md`. Wykonaj PRZED `git add`, żeby przeniesienia weszły do
   tego samego commita domykającego.
2. `git add` — dokładnie uzgodniona lista (z przeniesieniami i `summary.md`), nigdy `git add -A` na ślepo.
3. `git commit` z zaakceptowanym message.
4. Opis PR wypisz w bloku do skopiowania. `gh pr create` TYLKO na wyraźne
   polecenie: najpierw `gh auth status`; przy braku autoryzacji STOP z czytelnym
   komunikatem, bez częściowych działań.
5. Zakończ podsumowaniem: hash commita, co w nim jest (w tym co zarchiwizowano),
   przypomnienie że push należy do użytkownika.

---

## Terminal state

Stan terminalny tego skilla: lokalny commit domykający feature (message + artefakty zarchiwizowane do `archives/{slug}/`), gotowy opis PR w bloku do skopiowania.

`ship` jest **mechanicznym closeoutem PO `review`**, nie ogniwem łańcucha gate'ów — NIE wskazuje kolejnego skilla. Za nim zostają już tylko ruchy użytkownika poza tym skillem: `git push` i merge/otwarcie PR (ship nie pushuje i nie tworzy PR z własnej inicjatywy). To realny, końcowy punkt pipeline po stronie narzędzia — dalej decyduje człowiek.

Jeśli działasz pod `/goal` typu „dowieziony feature": właściwym punktem, w którym cel może być uznany za osiągnięty, jest czysty `review` + merge (patrz `review` → Terminal state). `ship` domyka stronę commitową między nimi; sam commit lokalny to jeszcze nie zmergowany feature.

- **Intent z artefaktów, prawda z diffa** — planning/tasks dają "dlaczego",
  diff rozstrzyga "co". Przy rozjeździe pytaj, nie maskuj.
- **Nic bez gate** — żadnego `git add`/`git commit` przed akceptacją KROKU 5.
- **Lokalnie i tyle** — bez pusha, bez PR z inicjatywy skilla, bez issues.
- **Degraduj czysto** — brak planning/tasks = commit z samego diffa,
  z jawnym zastrzeżeniem; brak AC = pomiń sekcję, nie wymyślaj kryteriów.
- **Single-tree**: jedno `skills/ship/`; pola `allowed-tools`/`argument-hint` są Claude-only i inertne na Codex/Pi/Grok.
