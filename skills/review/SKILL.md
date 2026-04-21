---
name: review
description: >
  Full code review of current branch changes — 4 phases: semantic analysis,
  edge case hunting, project rules compliance, and garbage collection.
  Always runs all phases, no partial reviews.
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(find:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(mkdir:*), Write(**/absolut-ai/reviews/*.md)
argument-hint: "[branch bazowy, default: main]"
---

# Review — Full Code Review

Wykonaj PEŁNY review zmian w bieżącym BRANCHU (w porównaniu do main/master). Przejdź przez WSZYSTKIE 4 fazy po kolei.

## Krok 0: Przygotowanie

Ustal nazwę aktualnego brancha:
```bash
git branch --show-current
```
Zamień na slug (kebab-case): `feature/auth-tokens` → `feature-auth-tokens`. Użyjesz go do nazwy pliku review.

Utwórz katalog `./absolut-ai/reviews/` jeśli nie istnieje.

Ustal branch bazowy (użyj argumentu jeśli podany, inaczej auto-detect):

```bash
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
```

Pobierz PEŁNY diff (commitowane zmiany vs baza + lokalne nieskomitowane):

```bash
# Zmiany commitowane na branchu vs main
git diff main...HEAD
# Zmiany staged (dodane przez git add, jeszcze nieskomitowane)
git diff --cached
# Zmiany unstaged (edytowane ale jeszcze nie git add)
git diff
```

Połącz wyniki wszystkich trzech — to jest Twój PEŁNY obraz zmian.

Pobierz listę WSZYSTKICH zmienionych/nowych plików:

```bash
# Pliki zmienione na branchu vs main
git diff main...HEAD --name-only
# Pliki staged
git diff --cached --name-only
# Pliki unstaged
git diff --name-only
# Pliki nowe, nieśledzone (untracked)
git ls-files --others --exclude-standard
```

Połącz i zdeduplikuj tę listę.

Przeczytaj plik `./absolut-ai/rules.md` z roota projektu (jeśli istnieje).

Jeśli jesteś NA BRANCHU main/master i nie ma diff vs HEAD — to znaczy że zmiany są tylko lokalne. Użyj `git diff` i `git diff --cached` jako jedyne źródło.

**WAŻNE:** Nowe pliki (untracked) nie pojawią się w żadnym `git diff`. Dla każdego pliku z `git ls-files --others --exclude-standard` przeczytaj CAŁY plik i traktuj go jako 100% nowy kod do review.

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

Przeczytaj plik `./absolut-ai/rules.md` z roota projektu.

**Jeśli plik nie istnieje** — napisz: "Brak pliku ./absolut-ai/rules.md, pomijam sprawdzanie reguł." i przejdź do Fazy 4.

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
- Ogólna ocena: [1-2 zdania — czy ten diff jest gotowy do merge'a]
```

## Zapis do pliku

Po zakończeniu wszystkich 4 faz, ZAWSZE zapisz pełny raport do:

```
./absolut-ai/reviews/YYYY-MM-DD-{branch-slug}.md
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
/absolut-ai:generate-tasks @absolut-ai/reviews/YYYY-MM-DD-{branch-slug}.md
```

## Ważne

- Przejdź przez WSZYSTKIE 4 fazy — nie pomijaj żadnej
- Bądź konkretny — podawaj pliki i linie
- Nie wymyślaj problemów na siłę — jeśli jest czysto, napisz że jest czysto
- Jeśli diff jest duży (>500 linii), skup się na najważniejszych zmianach i zaznacz co pominąłeś
- ZAWSZE zapisuj raport do pliku — nawet jeśli review jest czysty (audit trail)
