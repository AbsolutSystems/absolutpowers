---
name: review
description: >
  Full code review of current branch changes — 4 phases: semantic analysis,
  edge case hunting, project rules compliance, and garbage collection.
  Always runs all phases, no partial reviews.
  TRIGGER when: "review my code", "sprawdz kod", "przejrzyj zmiany", before merge,
  PR ready, "is this ready", code quality check, "what did I miss",
  branch ready for review.
allowed-tools: Read, Glob, Grep, Edit(**/absolutpowers/project-memory.md), Bash(git:*), Bash(find:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(mkdir:*), Bash(rm:*), Write(**/absolutpowers/reviews/*.md), Write(**/absolutpowers/project-memory.md), Write(**/absolutpowers/memory-candidates/*.md)
argument-hint: "[branch bazowy, default: main]"
---

# Review — Full Code Review

Wykonaj PEŁNY review zmian w bieżącym BRANCHU (w porównaniu do main/master). Przejdź przez WSZYSTKIE 4 fazy po kolei.

## Krok 0: Przygotowanie

Ustal branch bazowy i używaj go konsekwentnie jako `<base>` w dalszych komendach.

Ustal nazwę aktualnego brancha:
```bash
git branch --show-current
```
Zamień na slug (kebab-case): `feature/auth-tokens` → `feature-auth-tokens`. Użyjesz go do nazwy pliku review.

Utwórz katalog `./absolutpowers/reviews/` jeśli nie istnieje.

Ustal branch bazowy (użyj argumentu jeśli podany, inaczej auto-detect):

```bash
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
```

Pobierz PEŁNY diff (commitowane zmiany vs baza + lokalne nieskomitowane):

```bash
# Zmiany commitowane na branchu vs <base>
git diff <base>...HEAD
# Zmiany staged (dodane przez git add, jeszcze nieskomitowane)
git diff --cached
# Zmiany unstaged (edytowane ale jeszcze nie git add)
git diff
```

Połącz wyniki wszystkich trzech — to jest Twój PEŁNY obraz zmian.

Pobierz listę WSZYSTKICH zmienionych/nowych plików:

```bash
# Pliki zmienione na branchu vs <base>
git diff <base>...HEAD --name-only
# Pliki staged
git diff --cached --name-only
# Pliki unstaged
git diff --name-only
# Pliki nowe, nieśledzone (untracked)
git ls-files --others --exclude-standard
```

Połącz i zdeduplikuj tę listę.

Przeczytaj plik `./absolutpowers/rules.md` z roota projektu (jeśli istnieje).
Przeczytaj plik `./absolutpowers/project-memory.md` z roota projektu (jeśli istnieje).

Jeśli jesteś NA BRANCHU main/master i nie ma diff vs HEAD — to znaczy że zmiany są tylko lokalne. Użyj `git diff` i `git diff --cached` jako jedyne źródło.

**WAŻNE:** Nowe pliki (untracked) nie pojawią się w żadnym `git diff`. Dla każdego pliku z `git ls-files --others --exclude-standard` przeczytaj CAŁY plik i traktuj go jako 100% nowy kod do review.

## Project Memory

Use `./absolutpowers/project-memory.md` as prior context for recurring traps and warning signs that might make the review sharper.
Do not treat it as proof that a new diff is wrong; it is only a hint to inspect relevant areas more carefully.
When reading `project-memory.md`, use only entries with `Status: active` as review hints. Ignore `superseded` and `archived` entries.

Create a memory candidate only when ALL of these are true:
- the review surfaced a recurring trap, workaround, or warning sign
- the lesson is likely to matter again in future implementation/debugging/review work
- the content is more operational than architectural, so it belongs in memory instead of ADRs or `rules.md`

Do NOT create memory entries for:
- one-off review comments tied only to this diff
- subjective style preferences
- findings that should instead become project rules

When a durable lesson is worth capturing, use:
- candidate path: `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md`
- permanent memory path: `./absolutpowers/project-memory.md`

`project-memory.md` should be grouped by module, with explicit affected paths in every entry:

```markdown
## src/payments

### Retry helper swallows the first provider error
- Added: 2026-03-10
- Source: review / feature/payment-retry branch
- Last verified: 2026-03-10
- Status: active
- Problem: wrapper retries correctly but loses the original failure context
- Symptoms: logs show generic timeout, root provider exception disappears
- Root cause: helper overwrites the first caught error on each retry
- Resolution: keep the first provider failure and attach later retry metadata separately
- Warning signs:
  - retries appear in logs without original provider message
  - final exception is generic despite provider-specific failures
- Affected paths:
  - `src/payments/provider-retry.ts`
  - `src/payments/provider-client.ts`
```

Candidate file template:

```markdown
# Memory Candidate: [Short title]

## Status
Candidate — YYYY-MM-DD

## Metadata
- Added: YYYY-MM-DD
- Source: review / `branch-name` vs `base`
- Status: candidate

## Module
`path/to/module`

## Problem
...

## Symptoms
...

## Root Cause
...

## Resolution
...

## Warning Signs
- ...

## Affected Paths
- `path/to/file`

## Why This May Matter Again
...
```

---

## FAZA 1: SEMANTIC REVIEW

Dla KAŻDEJ zmienionej funkcji/metody/komponentu napisz:
- **Co się zmieniło w zachowaniu** (nie "zmieniono linię 42", tylko "dodano walidację wieku")
- **Dlaczego to może być ryzykowne**
- **Blast radius** — jakie moduły/pliki mogą być dotknięte
- Lista kluczowych decyzji architektonicznych i pytania do autora

---

## FAZA 2: EDGE CASE HUNT

Dla każdej zmienionej funkcji sprawdź:
- Co się stanie dla: null, undefined, pusty string, pusta lista, -1, 0, MAX_INT, duplikaty?
- Off-by-one (> vs >=)?
- Brak obsługi błędów?
- Race conditions?
- Czy zmiana usuwa istniejące zabezpieczenia?

Dla każdego problemu podaj: scenariusz, problematyczna linia, fix w pseudokodzie.

---

## FAZA 3: RULES CHECK

Przeczytaj plik `./absolutpowers/rules.md` z roota projektu.

**Jeśli plik nie istnieje** — napisz: "Brak pliku ./absolutpowers/rules.md, pomijam sprawdzanie reguł." i przejdź do Fazy 4.

**Jeśli istnieje** — dla KAŻDEJ reguły sprawdź czy diff ją łamie. Bądź binarny: złamana albo nie.

---

## FAZA 4: GARBAGE COLLECTION

Sprawdź CAŁY plik (nie tylko diff) dla każdego zmienionego pliku:
- Nieużywane importy, zmienne, funkcje
- `console.log` / `debugger` / `print()` (poza testami)
- Zakomentowany kod (nie komentarze dokumentacyjne)
- TODO/FIXME dodane przez agenta
- Stare nazwy w komentarzach po refaktorze
- Puste bloki catch

---

## Format odpowiedzi

```
# Full Review Report

## 1. Semantic Review
### Co się zmieniło:
- [plik:funkcja] — [opis zmiany w logice]

### Blast Radius:
- [zmiana → wpływ na inne moduły]

### Pytania do autora:
- [pytania]

---

## 2. Edge Cases
### WYSOKIE RYZYKO:
1. [plik:linia] — Scenariusz: ... / Problem: ... / Fix: ...

### ŚREDNIE RYZYKO:
1. [plik:linia] — ...

---

## 3. Rules Check
### Złamane: [lista]
### Spełnione: [lista]

---

## 4. Garbage Collection
### Do usunięcia: [lista z plik:linia]
### Do sprawdzenia: [lista]

---

## Podsumowanie
- Krytyczne problemy: [liczba]
- Ryzyka do sprawdzenia: [liczba]
- Śmieci do usunięcia: [liczba]
- Złamane reguły: [liczba]
- Weryfikacja końcowa: [potwierdzona / brak dowodu / nie dotyczy]
- Ogólna ocena: [1-2 zdania — czy ten diff jest gotowy do merge'a]
```

## Zapis do pliku

Po zakończeniu wszystkich 4 faz, ZAWSZE zapisz pełny raport do:

```
./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md
```

Plik zawiera dokładnie ten sam raport co output do konsoli.

## Następne kroki

Na końcu raportu (zarówno w konsoli jak i w pliku), zaproponuj następne kroki w zależności od wyników:

**0-2 problemy (drobne):**
```
Drobne fixy — napraw ręcznie i merguj.
```

**3+ problemy:**
```
Dużo do poprawki. Sugeruję wygenerować taski:
/absolutpowers:generate-tasks @absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md
```

## Ważne

- Przejdź przez WSZYSTKIE 4 fazy — nie pomijaj żadnej
- Bądź konkretny — podawaj pliki i linie
- Nie wymyślaj problemów na siłę — jeśli jest czysto, napisz że jest czysto
- Jeśli diff jest duży (>500 linii), skup się na najważniejszych zmianach i zaznacz co pominąłeś
- Jeśli zmiana dotyczy kodu wykonywalnego, sprawdź czy istnieje dowód końcowej weryfikacji (np. build backendu, build frontendu, typecheck, `spotlessCheck`). Jeśli nie ma dowodu, zaznacz to jako ryzyko procesowe
- ZAWSZE zapisuj raport do pliku — nawet jeśli review jest czysty (audit trail)
- Jeśli review ujawni trwałą lekcję dla przyszłych tasków, utwórz candidate file na końcu i zapytaj użytkownika, czy promować go do `./absolutpowers/project-memory.md`
- Promocja wymaga jawnej zgody użytkownika; przy promocji aktualizuj istniejący wpis zamiast duplikować, a po sukcesie usuń candidate file
