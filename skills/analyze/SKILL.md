---
name: analyze
description: >
  Cross-artifact consistency audit — builds a consolidated AC→Task→code traceability
  matrix for a feature slug, detects six divergence classes (each with file:line /
  AC-N / Task N evidence), emits a report, and returns a CONSISTENT / INCONSISTENT
  verdict. On-demand, audit-only; never fixes, plans, or writes code.
  TRIGGER when: traceability audit, "spójność artefaktów", "pokrycie AC",
  "audyt cross-artifact", "czy taski pokrywają plan", "AC→task→kod",
  "spójność planning↔tasks↔kod", "czy wszystkie AC mają taski",
  "czy zaimplementowano wszystkie taski", "scope creep check", "trace coverage".
  NIE wyzwalaj na: code quality review → użyj `review`; architecture/security audit
  → użyj `triada-review`; planning a new feature → użyj `feature-discuss`.
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(find:*), Bash(mkdir:*), Bash(diff:*), Write(**/absolutpowers/reviews/*.md)
argument-hint: "[slug feature'a, np. push-notifications]"
---

# Analyze — Cross-Artifact Consistency Audit

Wykonaj PEŁNY audyt spójności artefaktów dla podanego feature sluga. Zbuduj macierz AC→Task→Plik, wykryj sześć klas rozjazdów i wyemituj raport z werdyktem.

> **Analyze vs `review` vs `triada-review`:** `analyze` sprawdza **trace'owalność i kompletność łańcucha** między artefaktami (planning ↔ tasks ↔ kod) — różny wymiar od jakości kodu czy architektury. `review` sprawdza jakość kodu w 4 fazach. `triada-review` sprawdza architekturę, bezpieczeństwo i UI. Nie są zamienne — każde narzędzie patrzy na inny wymiar tej samej zmiany.

---

## Krok 0: Przygotowanie i auto-detekcja artefaktów

Argument to slug feature'a (np. `push-notifications`). Użyjesz go jako `{slug}` w całym audycie.

Utwórz katalog `./absolutpowers/reviews/` jeśli nie istnieje:

```bash
mkdir -p ./absolutpowers/reviews
```

### Auto-detekcja artefaktów

Sprawdź, które artefakty dla danego sluga istnieją. Audytuj **tylko dostępne ogniwa łańcucha** — brakujący artefakt to degradacja, nie błąd.

**Planning doc** — sprawdź w kolejności:
```bash
# Single planning doc
find ./absolutpowers/feature -name "planning-{slug}.md" -maxdepth 2
# Epic variant (planning doc wewnątrz podkatalogu epic)
find ./absolutpowers/feature -name "planning-*.md" -path "*/{slug}/*" -maxdepth 3
# Epic main doc
find ./absolutpowers/feature -name "planning-main.md" -path "*/{slug}/*" -maxdepth 3
```

**Tasks** — sprawdź oba warianty:
```bash
# Single-file
find ./absolutpowers/feature -name "tasks-{slug}.md" -maxdepth 2
# Orchestrated — katalog z fazami
find ./absolutpowers/feature -type d -name "tasks-{slug}" -maxdepth 2
```

**Diff** (current branch vs main):
```bash
git rev-parse --verify main 2>/dev/null && echo "main" || echo "master"
git diff main...HEAD --name-only 2>/dev/null || git diff master...HEAD --name-only 2>/dev/null || git diff --name-only
```

Zapisz wyniki detekcji. Zrób listę dostępnych ogniw: `[planning, tasks, diff]`. Poinformuj użytkownika, które ogniwa znalazłeś i które pominiesz z powodu braku artefaktu.

**Przypadki degradacji — zachowanie:**
- Tylko planning istnieje (brak tasks, brak diff) → sekcja AC→Task będzie pusta. Napisz: "brak tasków do audytu — pominięto wymiar Task→Kod." Nie jest to błąd.
- Brak sekcji AC w planning → audytuj tylko Task↔Kod i napisz: "brak sekcji AC — pominięto wymiar AC→Task."
- Brak diff (branch bez zmian lub brak dostępu) → napisz: "brak diffu — pominięto wymiar Kod→Task."
- Orchestrated mapping: Write scope faz bywa szeroki (globs) → preferuj false-negative nad false-positive przy wykrywaniu scope creep; zanotuj ograniczenie w raporcie.

---

## Krok 1: Ekstrakcja AC z planning doca

Jeśli planning doc istnieje, przeczytaj go w całości. Szukaj sekcji `## Acceptance Criteria` (lub podobnych: `## AC`, `## Kryteria akceptacji`).

Wyekstrahuj wszystkie wpisy w formacie `AC-N:` ze wszystkich podsekcji (Happy path, Edge cases, Security itp.).

**Format ekstrakcji:**
```
AC-1: [treść wymagania]
AC-2: [treść wymagania]
...
```

Jeśli sekcji AC nie ma — zapisz: "brak sekcji AC w planning docu" i przejdź do Kroku 2 bez wymiaru AC.

---

## Krok 2: Ekstrakcja Traces-to z tasków

### Single-file tasks

Przeczytaj `./absolutpowers/feature/tasks-{slug}.md`. Dla każdego taska szukaj pola `**Traces to:**` i wyekstrahuj listę AC referencji (np. `AC-1, AC-3`).

Jeśli `Traces to: none` — odnotuj jako brak AC powiązania dla tego taska.

### Orchestrated tasks

Przeczytaj główny plik `./absolutpowers/feature/tasks-{slug}.md` (indeks faz). Dla każdej fazy wymienionej w `## Phase Overview` przeczytaj jej plik fazowy.

W każdym pliku fazowym:
- Wyekstrahuj `**Traces to:**` z każdego taska.
- Wyekstrahuj `## Write Scope` fazy (lista plików/globów — granica zmiany kodu tej fazy).
- Zanotuj status każdego taska (`completed` / `pending` / `in-progress`).

Przeczytaj też `implementation-context.md` jeśli istnieje — może zawierać dodatkowe informacje o zmienionych plikach.

**Format ekstrakcji:**
```
Faza/Task           | Traces to        | Write Scope              | Status
--------------------|------------------|--------------------------|----------
Phase 1 / Task 1    | AC-1, AC-2       | src/auth/*.ts            | completed
Phase 2 / Task 1    | AC-3             | src/notifications/*.ts   | completed
Phase 2 / Task 2    | none             | (brak)                   | pending
```

---

## Krok 3: Budowa macierzy AC × Task × Plik

To jest rdzeń raportu. Zbuduj skonsolidowaną macierz łączącą wszystkie trzy wymiary.

### Pobierz listę zmienionych plików z diffu

```bash
git diff main...HEAD --name-only 2>/dev/null || git diff --name-only
```

Dla każdego pliku z diffu ustal: czy mapuje się na task/fazę przez Write Scope lub przez bezpośrednią wzmiankę w treści taska?

### Macierz

```
| AC     | Task(i)              | Plik(i) w diffie                      | Status   |
|--------|----------------------|---------------------------------------|----------|
| AC-1   | Phase 1 / Task 1     | src/auth/login.ts, src/auth/guard.ts  | COVERED  |
| AC-2   | Phase 2 / Task 1     | src/notifications/push.ts             | COVERED  |
| AC-3   | (brak taska)         | -                                     | GAP      |
| -      | Phase 2 / Task 2     | -                                     | NO CODE  |
| -      | -                    | src/utils/helper.ts                   | ORPHAN   |
```

**Legenda:**
- `COVERED` — AC ma taska, task ma powiązany plik w diffie
- `GAP` — AC bez żadnego taska (klasa 1)
- `NO CODE` — task `completed` bez zmian w diffie (klasa 3)
- `ORPHAN` — plik w diffie poza wszystkimi Write Scope (klasa 4)
- `NO TEST` — AC pokryte taskiem, ale brak testu referencjonującego AC (klasa 5)
- `ORPHAN TASK` — task bez AC (klasa 2, ostrzeżenie)

---

## Krok 4: Wykrycie sześciu klas rozjazdów

Dla każdej klasy zbierz dowody w formacie `file:line`, `AC-N`, lub `Task N`. Każde znalezisko musi mieć konkretny dowód — nie zgłaszaj przypuszczeń.

### Klasa 1: AC bez taska — **(BLOKUJE)**
**Definicja:** AC-N istnieje w planning docu, ale żaden task (w żadnej fazie) nie ma `Traces to: AC-N`.

Dla każdego AC-N z Kroku 1: sprawdź czy pojawia się w jakimkolwiek `Traces to:` z Kroku 2. Jeśli nie — to klasa 1.

**Dowód:** `planning-{slug}.md:{linia} AC-N` + "brak Traces to w żadnym tasku"

**Routing:** → `generate-tasks` (dopisz task pokrywający brakujące AC)

### Klasa 2: Task bez AC — **(OSTRZEŻENIE)**
**Definicja:** Task istnieje z `Traces to: none` bez wyraźnego uzasadnienia infrastrukturalnego (np. scaffolding, CI, testy integracyjne bez konkretnego AC).

**Uwaga:** zadania techniczne bez AC są dopuszczalne (np. "skonfiguruj CI", "dodaj migrację"), ale muszą mieć w treści wyraźne uzasadnienie dlaczego brak AC-N.

**Dowód:** `tasks-{slug}.md:{linia} Task N` + "`Traces to: none` bez uzasadnienia"

### Klasa 3: Task bez kodu — **(BLOKUJE)**
**Definicja:** Task ma status `completed`, ale w diffie nie ma żadnej zmiany pliku odpowiadającej Write Scope tego taska lub plikiem bezpośrednio wzmiankowanym w treści.

**Dowód:** `tasks-{slug}/{faza}.md:{linia} Task N` + "brak zmian w: [Write Scope]"

**Routing:** → `implement` (uzupełnij brakującą implementację)

### Klasa 4: Kod bez taska — **(BLOKUJE)**
**Definicja:** Plik zmieniony w diffie nie mieści się w Write Scope żadnej fazy/taska ANI nie jest wzmiankowany w treści żadnego taska.

**Ważna mitygacja:** jeśli plik pasuje do szerokiego globa (np. `src/**/*.ts`) jakiejkolwiek fazy — NIE flaguj go jako scope creep. Flaguj tylko gdy plik jest **poza WSZYSTKIMI** Write Scope i **poza** każdą wzmianką w taskach.

**Dowód:** `{plik w diffie}` + "poza Write Scope wszystkich tasków/faz"

**Routing:** → wróć do `generate-tasks` lub do autora tasków (czy to celowe?)

### Klasa 5: AC bez weryfikacji — **(OSTRZEŻENIE)**
**Definicja:** AC-N jest pokryte taskiem (klasa 1 nie dotyczy), ale żaden plik testowy w diffie nie referencjonuje tego AC (szukaj `AC-N` w treści testów, w komentarzach, w nazwach testów).

```bash
# Szukaj referencji do AC-N w plikach testowych z diffu
grep -r "AC-{N}" ./src/test ./tests ./**/*.test.* ./**/*.spec.* 2>/dev/null || true
```

**Dowód:** `AC-N` + "brak referencji w plikach testowych w diffie"

### Klasa 6: Sprzeczność — **(BLOKUJE)**
**Definicja:** Planning mówi X (np. określony kontrakt API, określona reguła biznesowa), a task lub kod robi non-X (inny endpoint, inna walidacja, inna wartość domyślna).

To wymaga oceny semantycznej — porównaj:
- Kontrakty API (endpointy, schematy, metody HTTP) wymienione w planning vs zaimplementowane w kodzie
- Reguły biznesowe w planning vs logikę w kodzie
- Wymagania bezpieczeństwa w planning vs implementację

**Dowód:** `planning-{slug}.md:{linia}` + `{plik kodu}:{linia}` + opis sprzeczności

**Routing:** → wróć do właściciela artefaktu (planning albo tasks), uzgodnij który jest autorytatywny

---

## Krok 5: Werdykt

Na podstawie zebranych rozjazdów:

**CONSISTENT** — łańcuch domknięty dla wszystkich dostępnych ogniw, zero rozjazdów klasy 1, 3, 4, 6.
Klasy 2 i 5 (ostrzeżenia) nie blokują same z siebie.

**INCONSISTENT** — co najmniej jeden rozjazd blokujący (klasa 1, 3, 4 lub 6).

---

## Krok 6: Zapis raportu

Zapisz pełny raport do:

```
./absolutpowers/reviews/analyze-{slug}.md
```

---

## Format raportu

```markdown
# Analyze Report: {slug}

**Data audytu:** YYYY-MM-DD
**Slug:** {slug}
**Dostępne artefakty:** [planning / tasks / diff — lista co znaleziono]

---

## Macierz AC × Task × Plik

| AC     | Task(i)              | Plik(i) w diffie | Status   |
|--------|----------------------|------------------|----------|
| AC-1   | Phase 1 / Task 1     | src/auth/login.ts | COVERED |
| ...    | ...                  | ...              | ...      |

---

## Rozjazdy

### Klasa 1: AC bez taska (BLOKUJE)
[lista znalezisk z dowodem, lub "brak"]

### Klasa 2: Task bez AC (ostrzeżenie)
[lista znalezisk z dowodem, lub "brak"]

### Klasa 3: Task bez kodu (BLOKUJE)
[lista znalezisk z dowodem, lub "brak"]

### Klasa 4: Kod bez taska (BLOKUJE)
[lista znalezisk z dowodem, lub "brak"]

### Klasa 5: AC bez weryfikacji (ostrzeżenie)
[lista znalezisk z dowodem, lub "brak"]

### Klasa 6: Sprzeczność (BLOKUJE)
[lista znalezisk z dowodem, lub "brak"]

---

## Werdykt

**CONSISTENT** / **INCONSISTENT**

[Uzasadnienie 1-3 zdania.]

---

## Routing rozjazdów

| Znalezisko          | Klasa | Routing                    |
|---------------------|-------|----------------------------|
| AC-3 bez taska      | 1     | → generate-tasks           |
| Task 2 bez kodu     | 3     | → implement                |
| src/util.ts orphan  | 4     | → review z autorem tasków  |
| Sprzeczność API     | 6     | → właściciel planning-doca |

---

## Ograniczenia audytu

[Zanotuj tu wszelkie degradacje: brak sekcji AC, brak diffu, orkiestrowany mapping nieprecyzyjny, itd.]
```

---

## Red Flags — STOP

Jeśli w trakcie audytu zauważysz, że masz zamiar:
- **edytować plik kodu** → STOP. Nie masz uprawnień do edycji kodu. Zaraportuj znalezisko, zasugeruj routing do `implement`.
- **dopisywać nowe taski** do pliku tasków → STOP. Zaraportuj brakujące pokrycie jako klasa 1, routing do `generate-tasks`.
- **modyfikować planning doc** → STOP. Zaraportuj sprzeczność jako klasa 6, routing do właściciela artefaktu.
- **usuwać lub zmieniać AC** → STOP. `analyze` jest tylko obserwatorem — nie zmienia artefaktów wejściowych.

**Twarda granica:** `analyze` audytuje i raportuje. Wszystkie decyzje o naprawie należą do człowieka lub do odpowiedniego narzędzia (generate-tasks / implement).

---

## Ważne

- Audytuj tylko dostępne ogniwa łańcucha — brakujące artefakty to degradacja, nie błąd.
- Każde znalezisko musi mieć konkretny dowód (`file:line`, `AC-N`, lub `Task N`) — nie zgłaszaj przypuszczeń.
- Przy orchestrated mapping: preferuj false-negative nad false-positive dla klasy 4 (scope creep). Szeroki glob nie jest dowodem scope creep.
- ZAWSZE zapisuj raport do pliku — nawet jeśli jest CONSISTENT (audit trail).
- Nie wymyślaj rozjazdów na siłę — jeśli łańcuch jest domknięty, napisz CONSISTENT.

<!-- CLAUDE-ONLY: Opcjonalna delegacja do subagenta -->
> **Claude-only (opcjonalne):** Budowę macierzy (Kroki 1–3) można zdelegować do subagenta dla czystego, izolowanego odczytu artefaktów — szczególnie przy dużych orchestrated tasks z wieloma fazami. Rdzeń logiki (klasy rozjazdów, werdykt, zapis raportu) zawsze wykonuje główna sesja. Skill działa w pełni bez delegacji i działa też na Codex.
<!-- /CLAUDE-ONLY -->

## Terminal state

Stan terminalny: raport `absolutpowers/reviews/analyze-{slug}.md` z werdyktem
**CONSISTENT** lub **INCONSISTENT**. Skill audytuje i routuje — nie fixuje.

Jeśli routing wymaga dalszego skilla, wypisz jedną pełną, copy-paste'owalną komendę w składni
aktywnego harnessu, z właściwym planning docem, tasks-docem lub identyfikatorem audytu. Stosuj
`references/harness-command-contract.md`; nie wypisuj samej nazwy skilla ani opisu typu „uruchom
generate-tasks”.

| Werdykt | Typowy następny krok |
|---------|----------------------|
| CONSISTENT | kontynuuj merge / wypisz pełną natywną komendę `ship` / close |
| INCONSISTENT (brak tasków) | wypisz pełną natywną komendę `generate-tasks` na właściwym planning docu |
| INCONSISTENT (brak kodu) | wypisz pełną natywną komendę `implement` na właściwym tasks-docu |
| INCONSISTENT (jakość kodu) | nie ten skill — wypisz pełną natywną komendę `review` |

On-demand: nie jest ogniwem łańcucha gate'ów.
