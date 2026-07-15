# analyze — audyt spójności cross-artifact (planning ↔ tasks ↔ kod)

## Status
Propozycja (do akceptacji). Inspiracja: `/speckit.analyze` z github/spec-kit. Wersja: część zbiorczego bumpu 3.8.0 → 3.9.0 (analyze + constitution + tasks-to-issues + debug-handoff w jednym wydaniu).

**Decyzja architektoniczna (Opcja C, zatwierdzona):** luka #1 (wierność intencji) idzie do
bramki `review-tasks` — tam najtaniej i w pipeline. Luki #2 (skonsolidowana macierz) i #3
(scope-creep) idą do nowego skilla `analyze` jako audyt on-demand. Czysty rozdział: bramka
pilnuje **w locie**, analyze robi **audyt zbiorczy** przed merge. `review-plan` zostaje bez
zmian — jest pierwszy, nie ma downstream do ciągnięcia.

## Problem
**Korekta wcześniejszej przesłanki:** bramki NIE są w izolacji. `review-tasks` już czyta source
planning-doc i ma kryterium Traceability (każde wymaganie pokryte, AC coverage, brak scope poza
planem). `review-implementation` już czyta AC z planning i ma kryterium AC Fulfillment
(per-AC FULFILLED/NOT VERIFIED/MISSING). Kontekst "co robimy" jest więc obecny na poziomie
**mechanicznym** w obu bramkach.

To, czego naprawdę brakuje, jest subtelniejsze — trzy luki, których obecne bramki nie łapią:

1. **Wierność intencji ≠ pokrycie mechaniczne.** Gate sprawdza "wymaganie X → istnieje task"
   (checkbox), nie "czy te taski realizują CEL planu". Można pokryć każde wymaganie co do litery
   i minąć sedno. review-tasks dziś tego nie ocenia.
2. **Brak skonsolidowanej macierzy 3-stronnej naraz.** Trace rozbity między bramki: review-tasks
   robi planning↔tasks, review-implementation robi tasks↔kod. Nikt nie widzi pełnego
   AC→task→kod w jednym miejscu, po fakcie, jako audyt na żądanie.
3. **Scope creep (kod bez taska).** review-implementation czyta "ALL changed files", ale nie
   mapuje ich twardo z powrotem na taski/AC — kod, którego nikt nie zamawiał, przechodzi.

QA-enrichment dodał `AC-N:` w planning + `Traces to: AC-N` w taskach — infrastruktura
trace'owalności istnieje i bramki jej cząstkowo używają. `analyze` jej NIE wprowadza od nowa;
dokłada **skonsolidowany audyt end-to-end + warstwę intencji + wykrycie scope-creep**, czego
żadna pojedyncza bramka nie robi.

Realny scenariusz: planning ma 7 AC, generate-tasks pokrywa 6 (jeden wypadł — to złapie już
review-tasks), implement robi 6 tasków + dokłada walidację spoza planu (klasa 4, dziś przechodzi),
a całość technicznie pokrywa AC, ale mija cel feature'a (klasa intencji, dziś nie oceniana).

## Użytkownicy
Developer/architekt prowadzący feature przez pipeline. Wejście: slug feature'a, który ma już
co najmniej planning-doc (opcjonalnie tasks-doc i/lub zaimplementowany kod na branchu).
Oczekiwanie: macierz trace'owalności + lista rozjazdów, **zanim** przejdzie dalej / zmerge'uje.

## Oczekiwane zachowanie
- Auto-wykrycie, które artefakty dla danego sluga istnieją (planning / tasks / diff) i audyt
  tylko dostępnych ogniw łańcucha (degradacja, nie błąd).
- Ekstrakcja `AC-N:` z planning-doca i `Traces to:` z tasków (single-file i orchestrated —
  z phase files).
- Zbudowanie macierzy: **AC → Task(i) → Plik(i)/symbol(e) w diffie**.
- Wykrycie sześciu klas rozjazdów (patrz niżej), każdy z dowodem `file:line` / `AC-N` / `Task N`.
- Raport `absolutpowers/reviews/analyze-{slug}.md` + werdykt CONSISTENT / INCONSISTENT.
- **Twarda granica:** audytuje i raportuje, NIE naprawia, NIE dopisuje tasków, NIE pisze kodu.
  Rozjazdy klasy "brakujący task" rutuje do `generate-tasks`; "brakujący kod" do `implement`.

### Sześć klas rozjazdów
1. **AC bez taska** — wymaganie w planie, brak `Traces to` w jakimkolwiek tasku → gap pokrycia.
2. **Task bez AC** — task istnieje, `Traces to: none` bez uzasadnienia infra → osierocona praca.
3. **Task bez kodu** — task `completed`, brak odpowiadającej zmiany w diffie → status kłamie.
4. **Kod bez taska** — zmiana w diffie nie mapuje się na żaden task → scope creep.
5. **AC bez weryfikacji** — AC pokryte taskiem, ale żaden test nie odnosi się do tego AC.
6. **Sprzeczność** — planning mówi X, task/kod robi non-X (np. inny kontrakt API, inna reguła).

### Werdykt
- **CONSISTENT** — łańcuch domknięty dla wszystkich dostępnych ogniw, zero rozjazdów klasy 1/3/4/6.
- **INCONSISTENT** — co najmniej jeden rozjazd blokujący; raport listuje każdy z dowodem i routingiem.
  Klasy 2/5 są ostrzeżeniami (nie blokują same z siebie), 1/3/4/6 blokują.

## Wybrane rozwiązanie (Opcja C — dwa komplementarne ruchy)

### Ruch 1: kryterium "Intent Fidelity" w bramce `review-tasks` (luka #1)
Dokładamy do istniejącego agenta `review-tasks` jedno kryterium — **semantyczne**, nie
mechaniczne. Obok obecnego Traceability (czy wymaganie pokryte taskiem) gate ma ocenić, czy
zestaw tasków **realizuje cel/intencję planu**, a nie tylko literę wymagań.

Proponowana treść kryterium (do wklejenia w `claude/agents/review-tasks.md`, sekcja Review Criteria):

```markdown
### 7. Intent Fidelity
- The task set as a whole achieves the GOAL/intent of the planning doc, not just literal
  per-requirement coverage. Read the planning doc's problem statement and chosen solution,
  then judge: if an agent executed exactly these tasks, would the feature's intent be met?
- Flag when tasks technically cover each requirement but collectively miss the point
  (e.g. plan wants "users self-serve password reset"; tasks build the endpoint but no email
  delivery — every requirement "checked", intent unmet).
- This is a judgment criterion, not a checklist. Only flag a CLEAR intent gap, not stylistic
  preference. When the intent is genuinely met, do not invent gaps.
```

Nowa kategoria werdyktu: `INTENT`. Tylko Claude (bramki są Claude-only; Codex bez gate'ów).

### Ruch 2: nowy skill on-demand `analyze` (luki #2 i #3)
Nowy **skill on-demand** `analyze` (nie agent-bramka), skupiony na skonsolidowanej macierzy
AC→task→kod i wykryciu scope-creep — czego bramka per-krok strukturalnie nie zrobi. Bo:
- Działa na żądanie w dowolnym punkcie (po generate-tasks, po implement, przed merge), nie jest
  przyspawany do jednego kroku jak istniejące gate'y.
- Wykorzystuje istniejącą infrastrukturę AC/Traces-to zamiast wprowadzać nowy format.
- Jest kuzynem `review` (oba czytają branch + rules), ale `review` patrzy na **jakość kodu**
  w czterech fazach, a `analyze` patrzy na **kompletność trace'owalności** przez artefakty.

Implementacja jako skill w obu drzewach. W Claude dodatkowo może delegować budowę macierzy do
subagenta (czyste, izolowane czytanie), ale rdzeń logiki = prompt skilla — działa też w Codex.

### Uzasadnienie
- Domyka realną dziurę: bramki per-artefakt nie widzą urwanego łańcucha.
- Zero nowego formatu — pasożytuje na `AC-N:` / `Traces to:` z QA-enrichment.
- Twarda granica (audyt, nie fix) trzyma go rozłącznym z generate-tasks/implement/review.

### Rozważane alternatywy
- **Rozszerzenie `review-implementation`** — odrzucone: bramka jest per-krok i per-artefakt;
  trace cross-artifact wymaga czytania planning+tasks+diff razem, co rozdmuchuje bramkę i miesza
  "jakość kodu" z "kompletność łańcucha".
- **Rozszerzenie `review`** — odrzucone: `review` to 4 fazy jakości kodu na branchu; trace'owalność
  to inny wymiar (kompletność vs poprawność). Notka "vs analyze" w `review` zamiast scalania.
- **Dodanie do każdego gate'a po kawałku** — odrzucone: rozproszyłoby logikę macierzy w trzech
  agentach i wymusiło duplikację ekstrakcji AC/Traces-to.

## Zakres
### In scope
- **Ruch 1:** MOD `claude/agents/review-tasks.md` — kryterium #7 Intent Fidelity + kategoria `INTENT`
  (Claude-only; Codex bez bramek)
- **Ruch 1 (źródło):** MOD `claude/skills/feature-discuss/SKILL.md` + `codex/skills/feature-discuss/SKILL.md`
  — przypomnienie, że cel/intencja musi trafić do planning-doca explicite (inaczej gate ślepy)
- **Ruch 2:** `claude/skills/analyze/SKILL.md` + `codex/skills/analyze/SKILL.md`
- Reużycie istniejącego katalogu `absolutpowers/reviews/` na output `analyze-{slug}.md`
- Notka "vs analyze" w `review` (oba drzewa), notka w `generate-tasks` (analyze jako post-check)
- Aktualizacja README.md, CLAUDE.md (sekcja pipeline — analyze jako cross-cutting audyt)
- Bump wersji (oba manifesty)

### Out of scope
- Auto-fix rozjazdów (skill rutuje do generate-tasks/implement, nie naprawia).
- Nowy format AC/Traces-to (używa istniejącego z QA-enrichment).
- Audyt jakości kodu (to `review`) ani architektury (to `triada-review`).
- Bramka blokująca w pipeline — `analyze` jest on-demand, użytkownik decyduje kiedy odpalić.

## Decyzje do zatwierdzenia
1. **Output dir:** reużyć `absolutpowers/reviews/` (`analyze-{slug}.md`) czy nowy `absolutpowers/analyze/`?
   Rekomendacja: reużyć `reviews/` — to artefakt audytowy bliski review.
2. **Klasy blokujące:** 1/3/4/6 blokują, 2/5 ostrzegają — czy zgadza się z intuicją?
3. **Orchestrated diff:** mapowanie kod↔task po `Write scope` faz + ścieżkach z tasków —
   wystarczające czy potrzebny dokładniejszy mechanizm?
4. **Wersja:** jeden zbiorczy bump 3.8.0 → 3.9.0 dla wszystkich czterech feature'ów (decyzja: bundle).

## Pliki do zmodyfikowania / utworzenia
- MOD `claude/agents/review-tasks.md` (Ruch 1 — kryterium #7 Intent Fidelity + kategoria `INTENT`)
- NEW `claude/skills/analyze/SKILL.md`
- NEW `codex/skills/analyze/SKILL.md`
- NEW `absolutpowers/feature/planning-cross-artifact-analyze.md` (ten plik)
- MOD `claude/skills/review/SKILL.md`, `codex/skills/review/SKILL.md` (notka "vs analyze")
- MOD `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
  (sugestia: po PASS uruchom `analyze` przed implement)
- MOD `README.md`, `CLAUDE.md`
- MOD `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`

## Zależność: Intent Fidelity czyta z czystego kontekstu
Bramka `review-tasks` to subagent — odpala się ze **świeżym kontekstem**, nie dziedziczy sesji
feature-discuss/generate-tasks. Kryterium #7 ocenia intencję **wyłącznie z zapisanego
planning-doca** (sekcja Problem/Cel + wybrane rozwiązanie), nie z żywej dyskusji.

Konsekwencja: Intent Fidelity działa tylko gdy planning-doc **samowystarczalnie oddaje cel**.
Jeśli intencja żyje w rozmowie a nie jest spisana, gate jej nie zobaczy. To wzmacnia zasadę
z CLAUDE.md ("dokumentacja jako produkt — samodzielna"). Dlatego:
- Kryterium #7 jawnie każe czytać sekcję Problem/Cel, nie tylko listę wymagań (już ujęte w bloku).
- **MOD `feature-discuss` (oba drzewa):** dopisać przypomnienie, że cel/intencja MUSI trafić do
  planning-doca explicite (sekcja Problem/Cel), bo downstream gate Intent Fidelity jest ślepy na
  to, czego w docu nie ma. Bez tego Ruch 1 ma dziurę u źródła.

## Edge cases i ryzyka
- **Intencja nie spisana w planning-docu** → Intent Fidelity ślepy; mitygacja: nudge w
  feature-discuss (wyżej) + kryterium #7 czyta Problem/Cel jawnie.
- **Brak sekcji AC w planning** → skill audytuje tylko task↔kod (degradacja), informuje o braku AC.
- **Tylko planning istnieje** (brak tasks/diff) → audyt zatrzymuje się na AC→Task = pusty,
  raportuje "brak tasków do audytu", nie błąd.
- **Orchestrated mapowanie kod↔task** niedokładne (glob Write scope szeroki) → ryzyko false-positive
  scope creep; mitygacja: traktować Write scope jako granicę, flagować tylko poza nią.
- **Trigger collision z `review`** → wąski TRIGGER (trace'owalność / spójność / pokrycie AC) +
  notka "vs analyze" w `review`.
- **Scope creep skilla** (zaczyna naprawiać) → twarda granica + Red Flags STOP, routing zamiast fix.

## Pytania otwarte
- Czy w przyszłości spiąć `analyze` jako opcjonalny auto-step po `review-tasks` PASS (miękki nudge,
  bez bramki)? Na razie: czysto on-demand, spójne z `review`.
- Czy raport powinien zawierać wizualną macierz (tabela AC×Task×Plik) — tak, jako rdzeń raportu.

## Notatki z dyskusji
Pomysł wyłonił się z porównania do spec-kit: ich `/analyze` robi cross-artifact consistency +
coverage, a `/checklist` to "unit testy dla angielskiego". AbsolutPowers ma silniejsze bramki
adwersarialne, ale każda jest per-artefakt — brak audytu **łańcucha**. Ponieważ QA-enrichment
już dołożył `AC-N:`/`Traces to:`, `analyze` to tani dobudowany audytor istniejącej infrastruktury,
nie nowy format.
