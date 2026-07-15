# debug-handoff — domknięcie artefaktów na wejściu i wyjściu drzewa debug

## Status
Propozycja (do akceptacji). Wersja: część zbiorczego bumpu 3.8.0 → 3.9.0
(analyze + constitution + tasks-to-issues + debug-handoff w jednym wydaniu).

## Problem
Cały pipeline AbsolutPowers przekazuje pracę przez **artefakty handoff** (planning → tasks →
implementacja, każdy krok czyta wyjście poprzedniego). Drzewo `debug` jest wyjątkiem — gubi
kontekst **na obu końcach**:

### Luka wejściowa (problem-discuss → debug)
`problem-discuss` zapisuje `absolutpowers/problem/problem-{slug}.md` z twardymi dowodami per
sprawa: reguła biznesowa, przejście flow, `file:line`, fakty wyciągnięte z załączników. Ale
Faza 5 routinguje do debug **stringiem w nudge'u** (`/absolutpowers:debug "{opis + dowód}"`).
`debug` startuje **czystym kontekstem** (subagentowo/świeżo) i **nie czyta** `problem-{slug}.md`.
Efekt: całe dochodzenie breadth z problem-discuss ginie poza tym, co zmieści się w stringu;
debug re-trace'uje Fazę 1 (Root Cause) od zera. Podwójna praca, ryzyko rozjazdu między tym co
problem-discuss ustalił a tym co debug odkrywa ponownie.

### Luka wyjściowa (debug → ???)
`debug` Faza 4 (Implementation) implementuje fix **inline, zawsze**, niezależnie od rozmiaru
zmiany. Dla jednolinijkowego root-cause fixa to słuszne — siła debug to ciasna pętla
hipoteza→test→fix, a przepychanie trywialnego fixa przez generate-tasks→implement→review to
zbędna ceremonia. ALE dla **dużej/architektonicznej/wielomodułowej** zmiany inline jest złe:
- Faza 4.5 wykrywa "massive refactoring / architectural problem" i każe "discuss with user" —
  ale **nie ma handoff-artefaktu**; ścieżka dead-enduje na rozmowie.
- Duży fix wpleciony inline omija bramki jakości (review-tasks, review-implementation), pod które
  podlega każda inna nietrywialna zmiana w projekcie.

Czyli debug połyka kontekst na wejściu i nie ma czystego wyjścia dla zmiany, która przerasta
"szybki fix".

## Użytkownicy
Developer prowadzący zgłoszenie przez triage→debug, oraz developer debugujący samodzielnie.
Oczekiwanie: (1) debug zaczyna od dowodów zebranych przez problem-discuss, nie od zera; (2) gdy
root-cause fix okazuje się duży, debug oddaje go do pipeline'u z artefaktem, zamiast albo pchać
inline bez bramek, albo utykać na "porozmawiaj z userem".

## Oczekiwane zachowanie

### Handoff wejściowy
- `problem-discuss` Faza 5: nudge do debug wskazuje **plik** + numer sprawy, nie tylko string:
  `/absolutpowers:debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"`.
- `debug` dostaje sekcję **Handoff Input**: jeśli wywołany ze ścieżką do `problem-{slug}.md`,
  czyta go PRZED Fazą 1 i traktuje dowody danej sprawy (reguła, flow, `file:line`, fakty z
  załączników) jako **punkt startowy** Fazy 1 — potwierdza/pogłębia, NIE re-derive'uje od zera.
- Iron Law bez zmian: nadal root cause przed fixem. Handoff daje przewagę startową, nie zwalnia
  z dochodzenia; debug może obalić wstępną hipotezę problem-discuss (z dowodem).

### Handoff wyjściowy (branch po rozmiarze fixa)
Po ustaleniu root cause (koniec Fazy 3), `debug` klasyfikuje rozmiar fixa:
- **Mały** (1 plik / 1 warstwa, brak migracji/API/security/shared-core) → **inline**, jak dziś
  (Faza 4: failing test → single fix → verify).
- **Duży** (wiele warstw/modułów, migracja, publiczne API, granica bezpieczeństwa, shared core,
  lub Faza 4.5 — 3+ fixy nieudane / problem architektoniczny) → **NIE implementuj inline**.
  Zapisz `absolutpowers/feature/planning-fix-{slug}.md` (root cause + wybrany fix + scope +
  ryzyko) i rutuj do `/absolutpowers:generate-tasks @absolutpowers/feature/planning-fix-{slug}.md`.
- Próg rozmiaru = ten sam heurystyk co single-file vs orchestrated w `generate-tasks`.

`planning-fix-{slug}.md` jest lekkim planning-doc, który `generate-tasks` rozumie jako wejście
typu planning (nowy, czwarty wariant obok planning/review-report/epic-phase — albo reuse wariantu
planning). Zawiera: Problem (= root cause z dowodem), Wybrane rozwiązanie (= fix), Zakres,
opcjonalnie AC dla zachowania po naprawie.

## Wybrane rozwiązanie
Reuse istniejących artefaktów, minimum nowych pojęć:
- **Wejście:** NIE dodajemy `problem-planning-{slug}.md` — `problem-{slug}.md` już istnieje i niesie
  dowody; wystarczy żeby debug go czytał. Mniej plików, zero duplikacji dochodzenia.
- **Wyjście:** debug emituje `planning-fix-{slug}.md` w `absolutpowers/feature/` — `generate-tasks`
  już konsumuje planning-doc; debug-big-fix to po prostu kolejny planning-doc. Analogiczne do tego,
  jak generate-tasks już przyjmuje review-report jako wejście fixowe.

### Uzasadnienie
- Domyka pipeline: artefakt handoff na obu końcach drzewa debug, spójnie z resztą.
- Zero utraty kontekstu na wejściu; zero omijania bramek przy dużym fixie na wyjściu.
- Inline zostaje dla małych fixów — nie zabijamy siły debug (ciasna pętla) ceremonią.
- Próg reuse'uje istniejący heurystyk generate-tasks — jeden model rozmiaru w całym pipeline.

### Rozważane alternatywy
- **Nowy `problem-planning-{slug}.md` z problem-discuss** — odrzucone: duplikuje `problem-{slug}.md`;
  problem-discuss ma twardą granicę "nie planuje", więc to musiałby być czysty handoff-evidence =
  to czym `problem-{slug}.md` już jest.
- **debug zawsze rutuje do generate-tasks (nigdy inline)** — odrzucone: trywialny root-cause fix
  przez 3 skille + 2 bramki to absurdalna ceremonia; zabija przewagę debug.
- **debug zawsze inline (status quo)** — odrzucone: duży fix omija bramki i dead-enduje na 4.5.
- **Nowy katalog `absolutpowers/debug/` na output** — odrzucone: `planning-fix-{slug}.md` w
  `feature/` wpina się w generate-tasks bez nowego wariantu wejścia.

## Zakres
### In scope
- MOD `claude/skills/problem-discuss/SKILL.md` + `codex/skills/problem-discuss/SKILL.md`
  (Faza 5 — nudge wskazuje plik `problem-{slug}.md` + sprawę)
- MOD `claude/skills/debug/SKILL.md` + `codex/skills/debug/SKILL.md`
  (sekcja Handoff Input; branch rozmiaru w Fazie 4; spójność z 4.5)
- MOD `claude/skills/generate-tasks/SKILL.md` + `codex/skills/generate-tasks/SKILL.md`
  (rozpoznaj `planning-fix-{slug}.md` jako wejście planning; output `tasks-fix-{slug}.md`)
- MOD `README.md`, `CLAUDE.md` (diagram pipeline — handoffy debug)
- Bump wersji w ramach zbiorczego 3.9.0

### Out of scope
- Gate dla `planning-fix-{slug}.md` osobny od istniejącego `review-plan` — jeśli generate-tasks
  traktuje go jak planning, `review-tasks` i tak go pokryje (downstream). Bez nowego gate'a.
- Automatyczne odpalanie generate-tasks po debug (nudge, nie automatyka — spójnie z resztą).
- Zmiana Iron Law / 4 faz debug — handoff to wejście/wyjście, rdzeń bez zmian.
- Per-sprawa handoff file z problem-discuss (reuse problem-{slug}.md + numer sprawy).

## Decyzje do zatwierdzenia
1. **Wejście:** debug czyta `problem-{slug}.md` (reuse) — OK, czy jednak osobny handoff file?
   Rekomendacja: reuse.
2. **Wyjście — nazwa/lokalizacja:** `absolutpowers/feature/planning-fix-{slug}.md` konsumowany
   przez generate-tasks jako planning. OK, czy nowy wariant wejścia w generate-tasks?
   Rekomendacja: reuse wariantu planning, prefiks `planning-fix-`.
3. **Próg inline vs handoff:** ten sam heurystyk co single-file/orchestrated. Zgoda?
4. **Faza 4.5 (3+ fixy nieudane):** zawsze eskaluje do `planning-fix-{slug}.md` + generate-tasks?
   Rekomendacja: tak — to definicja "za duże na inline".

## Pliki do zmodyfikowania / utworzenia
- NEW `absolutpowers/feature/planning-debug-handoff.md` (ten plik)
- MOD `claude/skills/problem-discuss/SKILL.md`, `codex/skills/problem-discuss/SKILL.md`
- MOD `claude/skills/debug/SKILL.md`, `codex/skills/debug/SKILL.md`
- MOD `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
- MOD `README.md`, `CLAUDE.md`
- MOD `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json` (zbiorczy 3.9.0)

## Edge cases i ryzyka
- **debug wywołany bez handoff file** (samodzielny bug) → Handoff Input opcjonalny; brak pliku =
  normalny start od Fazy 1. Zero regresji dla solo-debug.
- **problem-{slug}.md ma wiele spraw** → nudge wskazuje numer sprawy; debug czyta całość, skupia
  się na wskazanej. Bez numeru: debug pyta którą sprawę.
- **Dowód problem-discuss sprzeczny z głębszym dochodzeniem debug** → debug ufa świeżemu dowodowi
  (spójne z "memory to kontekst, nie dowód"), notuje rozjazd.
- **Fix na granicy małe/duże** → przy wątpliwości wybierz handoff (bramki > inline bez kontroli);
  jawnie uzasadnij wybór w odpowiedzi.
- **Eskalacja 4.5 w środku inline** → debug przerywa inline, zapisuje dotychczasowy root cause +
  nieudane hipotezy do `planning-fix-{slug}.md` (cenny kontekst dla generate-tasks), rutuje dalej.
- **generate-tasks nie rozpozna `planning-fix-`** → jawna notka w generate-tasks o prefiksie i
  mapowaniu output `tasks-fix-{slug}.md` (jak przy review-report).

## Pytania otwarte
- Czy `planning-fix-{slug}.md` powinien dziedziczyć sekcję AC (Acceptance Criteria), żeby downstream
  Intent Fidelity / AC Fulfillment działały? Rekomendacja: tak dla dużych fixów — root cause definiuje
  oczekiwane zachowanie po naprawie, naturalnie mapuje się na AC.
- Czy problem-discuss config/dane (fix bezpośredni) też zasługuje na handoff file? Na razie nie —
  to nie wchodzi w debug ani generate-tasks.

## Notatki z dyskusji
Pochodzi z obserwacji użytkownika: problem-discuss mówi "uruchom debug", ale kontekst (dowody)
nie przechodzi; oraz debug implementuje od razu, bez wyjścia do generate-tasks dla większej zmiany.
Rozstrzygnięcie: domknąć oba końce artefaktami, reuse istniejących (`problem-{slug}.md` na wejściu,
planning-doc na wyjściu), z branchem po rozmiarze fixa, żeby nie zabić inline dla małych bugów.
Spina drzewo debug z resztą pipeline'u, który już jest artefakt-driven.
