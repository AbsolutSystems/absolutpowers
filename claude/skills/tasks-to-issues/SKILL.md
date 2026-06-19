---
name: tasks-to-issues
description: >
  Eksport tasków (tasks-{slug}.md, single-file lub orchestrated) do GitHub Issues
  przez `gh` CLI — idempotentnie, z mapą zwrotną. Jedyny most outward-facing
  pipeline'u AbsolutPowers: rozpisany plan staje się widoczny w trackerze, w którym
  pracuje zespół. Tworzy epic issue na feature + sub-issue na fazę (orchestrated)
  lub na task (single-file), z labelami, linkowaniem i trwałą mapą plik↔issue.
  TRIGGER when: "eksportuj taski", "wystaw taski", "wystaw issues", "tasks to issues",
  "export tasks to GitHub", "utwórz issues z tasków", "rozpisz to na GitHub Issues",
  "pokaż plan zespołowi w trackerze".
  Claude-only (wymaga `gh`); brak odpowiednika w Codex. Provider: GitHub przez `gh`.
  NIE wyzwalaj na: implementację planu → użyj `implement`; generowanie tasków →
  użyj `generate-tasks`; audyt spójności → użyj `analyze`. Ten skill NIE pisze kodu,
  NIE zamyka issues, NIE rusza statusów w tasks-doc.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: "[ścieżka do tasks-{slug}.md]"
---

# Tasks → Issues — most do issue trackera

Wyeksportuj plan implementacji (`tasks-{slug}.md`) do GitHub Issues. Most outward-facing:
plan żyjący w plikach markdown staje się widoczny w narzędziu, w którym pracuje reszta zespołu.
Eksport jest **idempotentny** — wielokrotne odpalenie nie duplikuje, tylko dotwarza brakujące
i aktualizuje istniejące. Źródłem prawdy o tym, co już istnieje, jest **mapa zwrotna**
`tasks-{slug}.issues.md`.

> **tasks-to-issues vs `implement` vs `analyze`:** `tasks-to-issues` przenosi plan na zewnątrz
> (do trackera) — nie czyta kodu, nie zmienia tasks-doca. `implement` wykonuje taski i aktualizuje
> ich statusy w tasks-docu. `analyze` audytuje spójność AC↔task↔kod. Każde patrzy na inny wymiar
> tej samej zmiany — nie są zamienne.

---

## Twarda granica (przeczytaj najpierw)

Ten skill **tworzy i aktualizuje issues + mapę zwrotną — i nic więcej.**

- ❌ NIE zamyka issues automatycznie po `implement`/merge (osobna, późniejsza decyzja).
- ❌ NIE pushuje kodu, NIE tworzy commitów/PR-ów.
- ❌ NIE rusza statusów tasków w samym `tasks-{slug}.md` (to robota `implement`).
- ❌ NIE tworzy milestone'ów, przypisań (assignees) ani automatyki project board.
- ❌ NIE synchronizuje zwrotnie tracker → tasks-doc (kierunek jest jednostronny: tasks → issues).

Jeśli w trakcie zauważysz, że masz zamiar zrobić którąkolwiek z powyższych rzeczy → **STOP**
i zaraportuj to użytkownikowi zamiast wykonać.

---

## Provider: GitHub (przez `gh`)

> **Punkt rozszerzenia:** v1 obsługuje **wyłącznie GitHub przez `gh` CLI**. Cała logika specyficzna
> dla providera (komendy CLI, format `search`, tworzenie labeli) żyje w tej sekcji oraz w krokach
> oznaczonych `[provider:github]`. Dodanie GitLab (`glab`) lub Jira w przyszłości = nowa sekcja
> providera + mapowanie tych samych operacji (create issue, update issue, search by marker,
> ensure label), bez przepisywania reszty skilla. Reszta kroków (parsowanie tasków, mapa zwrotna,
> idempotencja, granularność) jest provider-agnostyczna.

Operacje providera GitHub (`[provider:github]`):
- Utworzenie issue: `gh issue create --title ... --body-file ... --label ...`
- Aktualizacja issue: `gh issue edit <nr> --title ... --body-file ... --add-label ...`
- Wyszukanie po markerze (fallback): `gh issue list --search "<marker> in:title" --state all --json number,title,url,state`
- Utworzenie labela (tolerancyjne na istniejący): `gh label create <name> --color <hex> 2>/dev/null || true`
- Sprawdzenie repo/uprawnień: `gh repo view --json nameWithOwner,viewerPermission`

---

## Krok 0: Preconditions — STOP zanim cokolwiek zapiszesz

Wzorzec jak w `preboot`: jeśli brakuje warunku wstępnego — **STOP z jasnym komunikatem**, NIE rób
częściowego eksportu.

Sprawdź po kolei (zanim utworzysz JAKIEKOLWIEK issue):

1. **`gh` zalogowany:**
   ```bash
   gh auth status
   ```
   Jeśli błąd → STOP: „`gh` nie jest zalogowany. Uruchom `gh auth login` i odpal skill ponownie. Nie utworzyłem żadnego issue."

2. **Repo GitHub z remote istnieje:**
   ```bash
   gh repo view --json nameWithOwner,viewerPermission
   ```
   Jeśli brak repo / brak remote → STOP: „Brak repozytorium GitHub (remote). Skonfiguruj remote i odpal ponownie. Nie utworzyłem żadnego issue."

3. **Uprawnienia do tworzenia issues:** sprawdź `viewerPermission` z poprzedniej komendy
   (`WRITE`, `MAINTAIN` lub `ADMIN` = OK; `READ`/`TRIAGE` = za mało).
   Jeśli za mało uprawnień → STOP: „Brak uprawnień do tworzenia issues w tym repo (`viewerPermission`: <X>). Nie próbuję obejścia. Nie utworzyłem żadnego issue."

Dopiero gdy wszystkie trzy przejdą — kontynuuj.

---

## Krok 1: Parsowanie tasks-doca

Argument to ścieżka do `tasks-{slug}.md`. Ustal `{slug}` z nazwy pliku (część po `tasks-` przed `.md`).

> **Epic subfolder:** jeśli plik leży w `feature/{epic-slug}/tasks-{slug}.md`, wszystkie ścieżki
> pochodne (w tym mapa zwrotna) rozwiązuj **względem katalogu tego pliku**, nie względem
> `feature/`. Mapa wtedy: `feature/{epic-slug}/tasks-{slug}.issues.md`.

Przeczytaj plik i wykryj `## Mode`:

### single-file
- Przeczytaj wszystkie `### Task N:` z sekcji `## Implementation Tasks`.
- Jednostka granularności = **task**. Każdy task → jedno sub-issue.

### orchestrated
- Przeczytaj `## Phase Overview` z głównego pliku: dla każdej fazy weź `**File:**`, `**Risk:**`,
  `**Write scope:**`, `**Depends on:**`.
- Przeczytaj każdy referenced plik fazowy (po `**File:**`) oraz `99-final-verification.md`.
- Jednostka granularności = **faza**. Każda faza → jedno sub-issue. Taski wewnątrz fazy renderuj
  jako **checklistę** w body issue fazy (`- [ ] Task N: ...`).

Z każdego taska/fazy wyłuskaj też (jeśli są): `**Traces to:**` (lista AC) — do linkowania w body.

---

## Krok 2: Model granularności

Niezależnie od trybu — zawsze jedno **epic issue** na cały feature:

```
epic issue  (feature {slug})
  ├─ sub-issue: Phase 1   (orchestrated)   ── body: checklista tasków fazy
  ├─ sub-issue: Phase 2
  └─ ...
```
lub
```
epic issue  (feature {slug})
  ├─ sub-issue: Task 1    (single-file)
  ├─ sub-issue: Task 2
  └─ ...
```

- **Epic issue body:** opis feature'a (krótki), link do źródłowego `tasks-{slug}.md` (ścieżka w repo),
  oraz checklista linków do wszystkich sub-issues (`- [ ] #NN Phase 1: ...`). Aktualizowana po
  utworzeniu sub-issues.
- **Sub-issue body:** opis fazy/taska, link zwrotny do epic issue (`Epic: #NN`), link do źródłowego
  pliku tasków, lista AC z `**Traces to:**` (jeśli są), a dla fazy — checklista jej tasków.

---

## Krok 3: Marker tytułu i mapa zwrotna (idempotencja)

**Marker tytułu** (fallback idempotencji): każdy tytuł zawiera pełny slug feature'a w nawiasie
kwadratowym, żeby uniknąć kolizji między epikami:
- Epic: `[{slug}] Epic: {Nazwa feature'a}`
- Faza:  `[{slug}] Phase N: {Tytuł fazy}`
- Task:  `[{slug}] Task N: {Tytuł taska}`

> **Slug collision:** dwa epiki z fazą o tej samej nazwie nie kolidują, bo marker zawiera PEŁNY
> slug feature'a, nie samą nazwę fazy.

**Mapa zwrotna** (źródło prawdy idempotencji): `tasks-{slug}.issues.md` obok tasks-doca.

Format:
```markdown
<!-- Wygenerowane przez tasks-to-issues. Źródło idempotencji — nie edytuj ręcznie. -->
# Issues map: {slug}

**Repo:** owner/repo
**Źródłowy tasks-doc:** `./absolutpowers/feature/tasks-{slug}.md`
**Ostatni eksport:** YYYY-MM-DD

| Artefakt          | Typ   | Issue | URL                                  | Status |
|-------------------|-------|-------|--------------------------------------|--------|
| (feature)         | epic  | #41   | https://github.com/owner/repo/issues/41 | open    |
| Phase 1: Data     | phase | #42   | https://github.com/owner/repo/issues/42 | open    |
| Phase 2: API      | phase | #43   | https://github.com/owner/repo/issues/43 | open    |
```

Kolumna `Typ`: `epic` | `phase` | `task`. Kolumna `Status`: `open` | `closed` | `orphaned`.

---

## Krok 4: Potwierdzenie publikacji (tylko przy pierwszym eksporcie sluga)

Eksport **publikuje treść tasków na zewnątrz** (tracker może być w repo publicznym). Dlatego:

- Jeśli mapa `tasks-{slug}.issues.md` **nie istnieje** (pierwszy eksport tego sluga) → POKAŻ
  użytkownikowi, ile issues zostanie utworzonych (1 epic + N sub-issues) i w jakim repo, i poproś
  o **wyraźne potwierdzenie** przed pierwszym pushem. Przypomnij: „Eksport opublikuje treść tasków
  do GitHub Issues w repo owner/repo. Kontynuować?"
- Jeśli mapa **istnieje** (re-run) → NIE pytaj ponownie; przejdź do idempotentnej aktualizacji.

Jeśli użytkownik nie potwierdzi → STOP, nic nie twórz.

---

## Krok 5: Eksport idempotentny

Dla każdego artefaktu (epic, potem każda faza/task) wykonaj w kolejności:

1. **Rozpoznanie istniejącego** (mapa = źródło prawdy):
   - Jeśli artefakt ma wpis w mapie → użyj zapisanego numeru issue.
   - Jeśli brak w mapie → fallback: wyszukaj po markerze tytułu
     `[provider:github] gh issue list --search "[{slug}] <część tytułu> in:title" --state all --json number,title,url,state`.
   - Jeśli nadal brak → to nowy artefakt (utwórz).

2. **Akcja wg stanu:**
   - **Brak** → utwórz issue (`gh issue create`). Zapisz nr/URL do mapy.
   - **Istnieje, `open`** → zaktualizuj tytuł/body/labele (`gh issue edit`). Nie duplikuj.
   - **Istnieje, `closed`** → **zostaw nietknięte** (nie reopenuj, nie edytuj). Zanotuj jako
     `skipped (closed)` w raporcie.

3. **Labele** (utwórz jeśli brak, tolerancyjnie):
   - `absolutpowers` (stały),
   - `{slug}` (identyfikator feature'a),
   - dla faz: `risk:low` | `risk:medium` | `risk:high` (z `**Risk:**` w Phase Overview),
   - status (np. `status:planned`).
   ```bash
   gh label create absolutpowers --color 1F4B99 2>/dev/null || true
   gh label create "{slug}" --color ededed 2>/dev/null || true
   gh label create "risk:high" --color d73a4a 2>/dev/null || true
   ```

4. **Linkowanie:** sub-issue body → `Epic: #<nr epica>`; epic body → checklista `- [ ] #<nr> ...`
   wszystkich sub-issues (zaktualizuj epic po utworzeniu sub-issues).

5. **Resume-safe:** **przepisz mapę po KAŻDYM utworzonym/zaktualizowanym issue.** Dzięki temu
   rate-limit lub błąd API w połowie zostawia spójną mapę częściową — ponowne odpalenie dotworzy
   resztę bez duplikatów.

**Kolejność:** najpierw epic (żeby sub-issues miały do czego linkować), potem fazy/taski, na końcu
aktualizacja body epica o pełną checklistę sub-issues.

---

## Krok 6: Sieroty (orphaned) — bez auto-kasowania

Jeśli mapa zawiera artefakt, którego **nie ma już** w tasks-docu (task/faza usunięte po edycji):
- **NIE kasuj i NIE zamykaj** issue automatycznie.
- Oznacz wpis w mapie jako `orphaned`.
- Zgłoś w raporcie z numerem issue i sugestią: „rozważ ręczne zamknięcie #NN, jeśli już nieaktualne".

---

## Krok 7: Raport końcowy

Po zakończeniu pokaż zwięzły raport:

```
Eksport tasks-to-issues: {slug} → owner/repo

- Utworzone:   #41 (epic), #42, #43
- Zaktualizowane: #40
- Pominięte (closed): #38
- Sieroty (orphaned): #35 — brak w tasks-docu, rozważ ręczne zamknięcie
- Błędy: brak

Mapa: ./absolutpowers/feature/tasks-{slug}.issues.md
```

Jeśli coś się nie powiodło w połowie (rate limit / błąd API): pokaż, co się udało, a co zostało,
i przypomnij, że ponowne odpalenie jest bezpieczne (idempotentne, dotworzy brakujące).

---

## Edge cases — ściąga

| Sytuacja | Zachowanie |
|----------|------------|
| `gh` niezalogowany / brak repo / brak uprawnień | STOP w Kroku 0, zero issues |
| Ponowne odpalenie po edycji tasków | dotwórz brakujące, zaktualizuj istniejące, nie duplikuj |
| Task/faza usunięte z tasks-doca | issue → `orphaned` w raporcie, NIE kasuj |
| Issue ręcznie zamknięte | zostaw, `skipped (closed)` |
| Rate limit / błąd API w połowie | mapa zapisana po każdym issue → resume-safe |
| Slug collision (dwa epiki) | marker zawiera pełny slug feature'a |
| Wrażliwa treść w taskach | potwierdzenie publikacji w Kroku 4 (pierwszy eksport) |
| Epic subfolder | mapa i ścieżki względem katalogu tasks-doca |

---

## Ważne

- Mapa zwrotna jest źródłem prawdy idempotencji; marker tytułu to tylko fallback.
- Zawsze przepisuj mapę po każdym issue (resume-safe), nie dopiero na końcu.
- Trzymaj się twardej granicy: tylko issues + mapa. Reszta (kod, status tasków, zamykanie) należy
  do innych narzędzi lub do człowieka.
- Claude-only: skill wymaga `gh` i interakcji z zewnętrznym API. Brak odpowiednika w Codex
  (out of scope w v1) — to celowa asymetria, nie drift do wyrównania.
