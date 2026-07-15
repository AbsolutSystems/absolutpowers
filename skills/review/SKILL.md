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

> **To review vs `/absolutpowers:triada-review`:** to `review` = solo, pełne 4 fazy,
> audit trail do `./absolutpowers/reviews/`, integracja z `project-memory.md`,
> działa też na Codex. Dla równoległego, multi-agentowego review większych PR
> (3 agentów z rozłącznymi zakresami + synteza, Claude-only) użyj
> `/absolutpowers:triada-review`. Nie konkurują — to dwa różne narzędzia.

> **Review vs `analyze`:** `review` ocenia **JAKOŚĆ kodu** na branchu (4 fazy: semantyka, edge cases, reguły, garbage). `analyze` ocenia **KOMPLETNOŚĆ trace'owalności / spójność** planning↔tasks↔kod przez artefakty — zupełnie inny wymiar. Nie scalać: gdy pytanie brzmi „czy taski/kod pokrywają plan i AC", użyj `analyze`; gdy pytanie brzmi „czy kod jest poprawny i bezpieczny", użyj `review`.

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

**Read** `references/project-memory.md`. Use active entries as review hints only.
Create candidates only for durable operational traps (not one-off style nits).
Source label: `review / {branch} vs {base}`.

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

### Pryncypia (constitution)

Przeczytaj plik `./absolutpowers/constitution.md` z roota projektu.

**Jeśli plik nie istnieje** — napisz: "Brak pliku ./absolutpowers/constitution.md, pomijam sprawdzanie pryncypiów." i kontynuuj.

**Jeśli istnieje** — dla każdego Artykułu oceń, czy diff narusza jego Normę. Cytuj `Artykuł N` przy każdym znalezisku.

**Ważne:** Review RAPORTUJE naruszenia pryncypiów (binarnie: naruszone / nie), ale ich NIE blokuje — decyzja o merge należy do autora. Pryncypia to osąd i wartości, nie twarde reguły lintera.

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
### Naruszone pryncypia (constitution): [lista z Artykuł N lub "brak"]

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
- Naruszone pryncypia: [liczba]
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
Drobne fixy — napraw ręcznie, potem @ship (commit/archiwizacja) i merge.
Opcjonalnie: @analyze {slug} jeśli feature ma planning/tasks (traceability).
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

---

## Terminal state

Stan terminalny tego skilla: zapisany raport review (`./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md`) z werdyktem jakościowym zmian na branchu.

Ten skill jest **punktem domknięcia pipeline**, nie ogniwem łańcucha — NIE wskazuje kolejnego skilla „do przodu". Z review wychodzą dwie ścieżki, obie zamykające cykl:
- **Fix-loop** — jeśli review znalazł problemy: napraw drobne ręcznie, a przy 3+ problemach zawróć do `generate-tasks` na raporcie review (pętla naprawcza, patrz „Następne kroki" wyżej), potem ponów review. To pętla domykająca jakość, nie krok naprzód w łańcuchu.
- **Merge/ship** — jeśli review czysty (albo problemy naprawione): zmiana jest gotowa do zmergowania/wysłania. To jest realny koniec pipeline.

To **jedyne miejsce, w którym sesja pod `/goal` typu „dowieziony feature" może uznać cel za osiągnięty** — dopiero po czystym review i merge/ship „feature dowieziony" jest prawdą. W przeciwieństwie do `feature-discuss`/`generate-tasks`/`implement` (skille pośrednie, które jawnie mówią „pipeline niedomknięty, kontynuuj"), tutaj łańcuch realnie się domyka.
