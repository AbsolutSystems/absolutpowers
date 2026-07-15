# tasks-to-issues — eksport tasków do issue trackera (most na zewnątrz)

## Status
Propozycja (do akceptacji). Inspiracja: `/speckit.taskstoissues` z github/spec-kit. Wersja: część zbiorczego bumpu 3.8.0 → 3.9.0 (analyze + constitution + tasks-to-issues + debug-handoff w jednym wydaniu).

## Problem
Cały pipeline AbsolutPowers jest **wsobny** — planning, tasks, implement, review żyją jako pliki
markdown w `absolutpowers/`. Nie ma mostu na zewnątrz: do issue trackera, gdzie pracuje reszta
zespołu/klient. Efekt: praca rozpisana w `tasks-{slug}.md` jest niewidoczna w GitHub Issues /
project board; status trzeba przepisywać ręcznie; brak linkowania commit/PR ↔ zadanie.

spec-kit ma `/taskstoissues` — konwersję `tasks.md` na GitHub Issues. To jedyny outward-facing
kanał, którego u nas nie ma, a daje realną wartość: zespół widzi plan w narzędziu, w którym
faktycznie pracuje.

## Użytkownicy
Developer/lead, który rozpisał taski (`generate-tasks`) i chce je wystawić zespołowi w trackerze
przed/podczas implementacji. Wejście: ścieżka do `tasks-{slug}.md` (single-file lub orchestrated).
Oczekiwanie: issues utworzone w repo (idempotentnie), z labelami, linkowaniem i mapą zwrotną
plik↔issue, bez duplikatów przy ponownym odpaleniu.

## Oczekiwane zachowanie
- Wejście: `tasks-{slug}.md`. Skill czyta strukturę (single-file: taski; orchestrated: fazy +
  taski z phase files + 99-final-verification).
- Tworzy issues przez `gh` CLI w bieżącym repo (autoryzacja = istniejące `gh auth`).
- **Idempotencja:** przy ponownym odpaleniu nie duplikuje — rozpoznaje już utworzone po markerze
  (np. tytuł z prefiksem sluga + numer, lub trwała mapa w pliku). Brakujące dotwarza, istniejące
  aktualizuje (tytuł/treść), zamknięte zostawia.
- **Granularność (decyzja):** rekomendacja — jedno **epic issue** na feature + **sub-issue na fazę**
  (orchestrated) lub na task (single-file). Taski wewnątrz fazy = checklista w body issue fazy.
- Labele: `absolutpowers`, `{slug}`, ryzyko fazy (`risk:low|medium|high`), status.
- Linkowanie: epic issue linkuje sub-issues; body każdego issue linkuje źródłowy plik tasków
  (ścieżka w repo) i AC, do których task trace'uje.
- Mapa zwrotna `absolutpowers/feature/tasks-{slug}.issues.md` (lub sekcja w tasks-doc):
  task/faza → numer issue + URL. To źródło idempotencji.
- **Twarda granica:** tworzy/aktualizuje issues i mapę; NIE zamyka issues automatycznie po implement,
  NIE pushuje kodu, NIE rusza statusów tasków w samym tasks-doc (to robi `implement`).

## Wybrane rozwiązanie
Nowy skill `tasks-to-issues`. **Tylko Claude na start** (Codex: out of scope w pierwszej iteracji),
bo wymaga `Bash(gh:*)` i interakcji z zewnętrznym API — w Claude pewniejsze; Codex można dołożyć,
gdy ustabilizuje się kontrakt.

Provider: **GitHub przez `gh`** w v1. Abstrakcja prowidera (GitLab `glab`) — out of scope, ale
struktura skilla ma to przewidzieć (sekcja "provider" łatwa do rozszerzenia).

### Uzasadnienie
- Jedyny brakujący kanał outward-facing; daje widoczność planu w narzędziu zespołu.
- `gh` jest już w środowisku (CLAUDE.md: operacje GitHub przez `gh`), zero nowej zależności.
- Idempotencja przez mapę zwrotną = bezpieczne wielokrotne odpalanie (re-run po edycji tasków).

### Rozważane alternatywy
- **Jedno issue na task (płasko, bez epica)** — odrzucone dla orchestrated: gubi strukturę faz
  i zalewa tracker; checklista tasków w issue fazy czytelniejsza.
- **Jedno wielkie issue na feature (bez sub-issues)** — odrzucone: za grube, brak granularnego
  trackowania postępu faz.
- **Integracja w `generate-tasks`** (auto-eksport po wygenerowaniu) — odrzucone: eksport to decyzja
  (nie każdy feature idzie do trackera); osobny skill on-demand. Możliwy późniejszy miękki nudge.
- **API GitHub bez `gh`** (REST + token) — odrzucone: `gh` załatwia auth i jest konwencją projektu.

## Zakres
### In scope
- `claude/skills/tasks-to-issues/SKILL.md`
- Output mapy zwrotnej: `absolutpowers/feature/tasks-{slug}.issues.md` (epic → fazy/taski → issue#/URL)
- Obsługa single-file i orchestrated tasks-doc (w tym epic subfolder `feature/{epic-slug}/`)
- Idempotencja przez mapę zwrotną
- Labele + linkowanie epic↔sub + link do pliku tasków i AC
- Aktualizacja README.md, CLAUDE.md
- Bump wersji (oba manifesty — wersja wspólna, mimo że skill Claude-only)

### Out of scope
- Codex (brak w v1; dołożyć po ustabilizowaniu kontraktu).
- Inne providery niż GitHub (`glab`/Jira) — tylko miejsce na rozszerzenie w strukturze.
- Auto-domknięcie issues po `implement`/merge (osobna, późniejsza decyzja).
- Dwukierunkowa synchronizacja status tracker → tasks-doc (na razie jednokierunkowo: tasks → issues).
- Tworzenie milestone'ów / przypisań / project board automation.

## Decyzje do zatwierdzenia
1. **Granularność:** epic + sub-issue na fazę (orchestrated) / na task (single-file) — OK?
   (alternatywa: sub-issue zawsze na task, faza tylko jako label).
2. **Mapa zwrotna:** osobny plik `tasks-{slug}.issues.md` czy sekcja `## Issues` w tasks-doc?
   Rekomendacja: osobny plik (nie zaśmieca tasks-doc, łatwy do gitignore jeśli trzeba).
3. **Claude-only v1** — akceptowalne, czy od razu próbować Codex?
4. **Idempotencja:** marker w tytule (`[{slug}]` + nr) vs wyłącznie mapa w pliku.
   Rekomendacja: mapa w pliku jako źródło prawdy + marker w tytule jako fallback.
5. **Wersja:** jeden zbiorczy bump 3.8.0 → 3.9.0 dla wszystkich czterech feature'ów (decyzja: bundle).

## Pliki do zmodyfikowania / utworzenia
- NEW `claude/skills/tasks-to-issues/SKILL.md`
- NEW `absolutpowers/feature/planning-tasks-to-issues.md` (ten plik)
- MOD `README.md`, `CLAUDE.md` (sekcja pipeline — eksport outward-facing, Claude-only)
- MOD `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json` (wersja wspólna)
- (opcjonalnie) MOD `claude/skills/generate-tasks/SKILL.md` — miękki nudge "możesz wyeksportować
  do issues" po PASS (bez automatyki)

## Edge cases i ryzyka
- **Ponowne odpalenie po edycji tasków** → idempotencja: dotwórz brakujące, zaktualizuj istniejące,
  nie duplikuj; usunięty task → issue **nie** kasowane automatycznie (flaga "orphaned" w raporcie).
- **`gh` niezalogowany / brak repo remote** → skill STOP z jasnym komunikatem (jak preboot przy
  braku docs), nie częściowy eksport.
- **Rate limit / błąd API w połowie** → zapis mapy po każdym utworzonym issue (resume-safe), raport
  co się udało / co zostało.
- **Brak uprawnień do tworzenia issues** → STOP, nie próbuj obejścia.
- **Slug collision** (dwa epiki, ta sama nazwa fazy) → marker zawiera pełny slug feature'a.
- **Wrażliwa treść w taskach** → przypomnienie: eksport publikuje treść do trackera (może być
  publiczny repo); potwierdzić przed pierwszym pushem issues.

## Pytania otwarte
- Czy domknąć pętlę później: po `implement` faza `completed` → komentarz/zamknięcie issue?
  (osobny feature, dwukierunkowość). Na razie jednokierunkowo.
- Czy dołożyć `glab` (GitLab) w iteracji 2 — zależne od potrzeb zespołu.

## Notatki z dyskusji
Z porównania do spec-kit: ich `/taskstoissues` to jedyny kanał outward-facing, którego brak w
AbsolutPowers (cały pipeline wsobny w plikach md). `gh` jest już konwencją projektu, więc most do
GitHub Issues jest tani. Kluczowe: idempotencja (mapa zwrotna) i granularność (epic + sub-issue na
fazę), żeby eksport był bezpiecznie powtarzalny i nie zalewał trackera. Świadomie outward-facing →
wymaga potwierdzenia przed pierwszą publikacją (publikacja treści na zewnątrz).
