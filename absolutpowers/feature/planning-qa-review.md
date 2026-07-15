# Feature: QA Review

## Status
Draft — 2026-07-15

## Problem
Obecne przeglądy jakości w AbsolutPowers potwierdzają poprawność implementacji, zgodność z regułami i ogólną obecność testów, ale nie wykonują specjalistycznego audytu tego, czy zielony zestaw testów daje rzeczywiste zaufanie do produktu. `review` sprawdza cały branch, a rola `codebase-auditor` w `triada-review` ma jedynie skrócone kryterium jakości testów obok security i correctness. Brakuje narzędzia, które koncentruje się na wartości testów: brakujących scenariuszach, niepotrzebnych testach, testowaniu mocków zamiast zachowania, złym poziomie testu oraz lukach integracyjnych i E2E.

Celem feature'a jest dostarczenie ręcznie uruchamianego, read-only audytu QA, który odpowiada na pytanie „czy te testy rzeczywiście zabezpieczają istotne zachowanie?” i zapisuje konkretne rekomendacje w raporcie nadającym się do dalszego routingu. Skill nie uruchamia testów, nie mierzy coverage i nie modyfikuje kodu. Nawet oczywisty one-liner pozostaje rekomendacją wymagającą osobnej zgody przed zastosowaniem.

## Użytkownicy
- Developer po implementacji feature'a, który chce sprawdzić wartość i kompletność testów przed końcowym review.
- Tech lead lub QA engineer audytujący strategię testowania modułu albo całego codebase'u.
- Agent planujący poprawki na podstawie trwałego raportu QA przez `feature-discuss` lub `generate-tasks`.

## Oczekiwane zachowanie
- `@qa-review` oraz `@qa-review feature [opcjonalny artefakt]` audytują bieżący feature. Planning i Acceptance Criteria są preferowanym źródłem intencji, ale ich brak nie blokuje analizy opartej na tasks, opisie PR/commitach, diffie, kodzie produkcyjnym i testach.
- `@qa-review codebase [opcjonalna ścieżka]` audytuje wskazany moduł albo automatycznie odkrywa logiczne obszary całego projektu, analizuje je osobno i scala wynik.
- Skill analizuje kod testów statycznie. Zakłada, że testy przeszły podczas implementacji; nie uruchamia testów, E2E ani coverage.
- Audyt ocenia pokrycie intencji, brakujące scenariusze, wartość testu, użycie test doubles, dobrany poziom testowania, konstrukcję testów oraz strategię integracyjną/E2E.
- Każde znalezisko ma severity, confidence, dowód `plik:linia`, ryzyko, rekomendowaną operację i routing do dalszego działania.
- Skill zapisuje jeden raport Markdown w `absolutpowers/reviews/`, nawet gdy nie znajduje problemów.
- Skill nigdy nie edytuje testów ani kodu. Raport może pokazać konkretny przykład lepszego testu, ale jest to wyłącznie rekomendacja.
- `implement` może zasugerować uruchomienie audytu po zmianach o podwyższonym ryzyku testowym, lecz nigdy nie uruchamia go automatycznie i nie czyni z niego bramki pipeline'u.

## Wybrane rozwiązanie
Powstanie jeden host-agnostyczny skill `qa-review` z dwoma trybami: `feature` i `codebase`. Wspólna metodyka oceny będzie pojedynczym źródłem prawdy w `skills/qa-review/references/testing-rubric.md`. Główny skill odpowiada za wykrycie trybu i zakresu, zebranie kontekstu, podział dużego codebase'u, dispatch analiz per moduł, syntezę, deduplikację i zapis raportu.

Dla małego zakresu analiza może odbyć się inline. Dla wielu niezależnych modułów skill preferuje równoległy dispatch workerów QA: Claude użyje zarejestrowanego promptu `agents/qa-reviewer.md`, a Codex, Pi i Grok użyją generycznych subagentów z tym samym pełnym promptem. Przy braku dispatchu analiza działa sekwencyjnie i jawnie oznacza ograniczoną izolację.

Tryb `feature` zbiera pełny obraz zmian: commitowany diff względem automatycznie wykrytej bazy, staged, unstaged i untracked. Priorytet źródeł intencji to planning/AC, tasks, opis PR i commity, następnie diff z kodem produkcyjnym. Tryb `codebase` odkrywa moduły kolejno przez granice workspace/package, domeny, warstwy, a na końcu katalogi najwyższego poziomu.

Wspólny rubric obejmuje:
1. Pokrycie intencji i zachowania.
2. Happy path, błędy, granice, stan, retry, współbieżność i regresje.
3. Wartość regresyjną testu oraz tautologie i duplikaty.
4. Zasadność mocków, fake'ów, stubów i spy.
5. Dobór poziomu unit/integration/contract/component/E2E.
6. Asercje, setup, fixtures, coupling, czytelność i statyczne symptomy flaky tests.
7. Krytyczne przepływy, granice modułów i strategię E2E.

Każde finding zawiera:
- severity: `blocker | major | minor | nit`;
- confidence: `high | medium | low`;
- evidence: `plik:linia`;
- operation: `ADD | REWRITE | REMOVE | MOVE_LEVEL | MERGE`;
- route: `INLINE_FIX | GENERATE_TASKS | FEATURE_DISCUSS`;
- opis ryzyka i konkretną rekomendację, opcjonalnie przykładowy kształt testu.

Werdykt raportu to:
- `ADEQUATE` — brak istotnych luk i pełny zadeklarowany zakres został przeanalizowany;
- `IMPROVEMENTS_RECOMMENDED` — wyłącznie `minor`/`nit`;
- `GAPS_FOUND` — co najmniej jeden `major`;
- `MISLEADING_CONFIDENCE` — co najmniej jeden `blocker`, np. krytyczny przepływ wygląda na pokryty, lecz test sprawdza wyłącznie zachowanie mocka.

Raport ma stabilną sekcję `Actionable Findings`, konsumowalną przez `generate-tasks`. Generator domyślnie tworzy taski wyłącznie z findings oznaczonych `GENERATE_TASKS`. Findings `FEATURE_DISCUSS` pomija jako nierozstrzygnięte decyzje, a `INLINE_FIX` pomija jako zmiany wymagające osobnej, jawnej zgody i wykonania poza generatorem; oba pominięcia wymienia użytkownikowi wraz z identyfikatorami findings. Dzięki temu przekazanie mieszanego raportu nie rozszerza po cichu zakresu tasków. Output generatora zachowuje scope i timestamp raportu, zamieniając prefiks `qa-review-` na `tasks-fix-qa-`, np. `qa-review-auth-2026-07-15-101530.md` → `tasks-fix-qa-auth-2026-07-15-101530.md`. Routing rekomenduje kolejno: rozstrzygnąć kwestie projektowe, zaakceptować ewentualne inline fixes, wygenerować taski dla gotowych poprawek, a następnie ponowić audyt.

Każde uruchomienie tworzy nowy, niemodyfikujący poprzednich wyników raport z lokalnym timestampem sekundowym: `qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, `qa-review-codebase-YYYY-MM-DD-HHmmss.md` albo `qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md`. Ponowiony audyt ma dzięki temu osobny audit trail i może wskazać wcześniejszy raport jako poprzednią wersję oceny.

### Uzasadnienie
Jeden skill z dwoma trybami utrzymuje identyczną definicję wartościowego testu dla audytu feature'a i codebase'u. Wspólny rubric ogranicza drift promptów, a opcjonalny dispatch per moduł skaluje analizę bez uzależniania działania od rejestru agentów konkretnego harnessu. Read-only kontrakt zachowuje wiarygodność audytu i zapobiega zmianie badanego materiału w trakcie review. Trwały raport pasuje do istniejącego modelu `review → generate-tasks` i daje audit trail.

### Rozważane alternatywy
- **Dwa niezależne skille `qa-review` i `qa-code-review`:** odrzucone, ponieważ szybko rozjechałyby kryteria jakości i format raportów; różnica dotyczy zakresu wejścia, nie kompetencji QA.
- **Obowiązkowa bramka po `implement`:** odrzucona, ponieważ większość małych zmian nie potrzebuje specjalistycznego audytu, a pipeline ma już `review-implementation` i końcowe review. Pozostaje warunkowy, nieblokujący nudge.
- **Uruchamianie testów i coverage:** odrzucone jako duplikacja implementacji/CI; celem jest ocena znaczenia zielonych testów, nie ponowne ustalenie ich wyniku.
- **Automatyczne poprawianie prostych testów:** odrzucone, ponieważ miesza audyt z implementacją. One-liner jest oznaczany `INLINE_FIX`, ale wymaga osobnej zgody i wykonania poza skillem.
- **Rozszerzenie wyłącznie kryterium testowego w `triada-review`:** odrzucone, bo nie zapewnia codebase-wide analizy, własnego raportu, routingu ani głębokości specjalisty QA.

## Zakres

### In scope
- Nowy host-agnostyczny skill `qa-review` z trybami `feature` i `codebase`.
- Wspólny testing rubric i stabilny format raportu.
- Worker QA używany do izolowanej analizy modułów oraz fallback inline/sekwencyjny.
- Automatyczne wykrywanie artefaktów feature'a, pełnego diffu i logicznych modułów codebase'u.
- Read-only analiza testów i kodu produkcyjnego bez uruchamiania testów.
- Raport z unikalnym timestampem, werdyktem, findings, dobrymi praktykami, zakresem, ograniczeniami i routingiem.
- Jawna obsługa raportów QA przez `generate-tasks` i `feature-discuss`.
- Warunkowy, opcjonalny nudge w `implement` po zmianach o podwyższonym ryzyku testowym.
- Dokumentacja skilla, macierzy wyboru i zachowania per harness.
- Podbicie wersji minor we wszystkich manifestach pluginu oraz aktualizacja wersji opisowej repozytorium.

### Out of scope
- Uruchamianie testów, E2E, coverage, mutation testing lub CI.
- Edycja kodu produkcyjnego i testów przez `qa-review`.
- Automatyczne wdrażanie nawet jednoliniowych rekomendacji.
- Zastąpienie `review`, `triada-review`, `review-implementation` albo `analyze`.
- Obowiązkowa bramka QA w liniowym pipeline.
- Narzucenie jednej piramidy testów lub frameworka wszystkim projektom.
- Osobny automatyczny harness oceniający jakość promptów.

## Plan implementacji
1. Utworzyć `skills/qa-review/SKILL.md` z routerem trybu, kontraktem read-only, zbieraniem kontekstu, podziałem zakresu, syntezą, formatem raportu i stanem terminalnym.
2. Utworzyć `skills/qa-review/references/testing-rubric.md` jako wspólne źródło kryteriów, kalibracji severity/confidence, operacji i zasad rekomendowania poziomów testów/E2E.
3. Utworzyć `agents/qa-reviewer.md` z wąskim kontraktem analizy jednej paczki/modułu i ustrukturyzowanym outputem do syntezy.
4. Rozszerzyć kontrakty dispatchu dla Claude, Codex, Pi i Grok o workera `qa-reviewer` oraz zachować sekwencyjny fallback z jawnym disclaimerem.
5. Rozszerzyć `skills/generate-tasks/SKILL.md` i format kontekstu tasków o raporty `qa-review-*`, mapowanie nazwy outputu oraz kontrakt: konsumuj domyślnie tylko `GENERATE_TASKS`, jawnie pomiń i wypisz `INLINE_FIX` oraz `FEATURE_DISCUSS`.
6. Rozszerzyć router `skills/feature-discuss/SKILL.md` o wejście z raportu QA dla wybranych findings `FEATURE_DISCUSS`, z traceability źródło → planning.
7. Dodać do `skills/implement/SKILL.md` warunkowy, nieblokujący nudge po PASS, gdy występuje co najmniej jeden sygnał ryzyka: tryb orchestrated, granica security/public API/migracja/integracja/wiele modułów, nowy krytyczny flow, istotna przebudowa testów, warning testowy z gate'a albo trudne do zweryfikowania AC.
8. Zaktualizować README, session context i contributing docs: pozycjonowanie względem `review`/`triada-review`/`analyze`, przykłady wywołania, raporty, routing oraz worker QA.
9. Podbić wersję z `5.3.0` do `5.4.0` w `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.grok-plugin/plugin.json` oraz opisach wersji w `CLAUDE.md` i `README.md`.
10. Wykonać walidacje strukturalne i scenariuszowe, sprawdzić spójność dokumentacji oraz brak instrukcji uruchamiania testów lub modyfikowania kodu w kontrakcie audytowym.

## Pliki do zmodyfikowania / utworzenia
- `skills/qa-review/SKILL.md` — publiczny workflow obu trybów, synteza i zapis raportu.
- `skills/qa-review/references/testing-rubric.md` — szczegółowe kryteria i kalibracja rekomendacji.
- `agents/qa-reviewer.md` — izolowany worker jednej paczki QA.
- `references/harness-dispatch.md` — rejestr roli QA i ogólna ścieżka dispatchu.
- `references/codex-tools.md` — generic-agent i sekwencyjny fallback dla audytu modułów.
- `references/pi-tools.md` — mapping `pi-subagents` i fallback QA.
- `references/grok-tools.md` — mapping `spawn_subagent` i fallback QA.
- `skills/generate-tasks/SKILL.md` — nowy typ inputu raportowego, naming i filtrowanie routingu.
- `skills/generate-tasks/references/task-formats.md` — dopuszczenie raportu QA w `Source doc`.
- `skills/feature-discuss/SKILL.md` — tryb handoffu z raportu QA.
- `skills/implement/SKILL.md` — warunkowy, opcjonalny nudge QA.
- `hooks/session-context.md` — wybór `qa-review` i pozycja jako narzędzia on-demand.
- `README.md` — opis, tabela skilli, przykłady i granice odpowiedzialności.
- `docs/contributing.md` — worker QA i wskazówki utrzymania skilla/rubric.
- `.claude-plugin/plugin.json` — wersja `5.4.0`.
- `.codex-plugin/plugin.json` — wersja `5.4.0`.
- `.grok-plugin/plugin.json` — wersja `5.4.0`.
- `CLAUDE.md` — wersja i opis nowego elementu architektury pipeline'u.

## Edge cases i ryzyka
- Brak testów nie oznacza automatycznie defektu: skill musi najpierw ustalić, czy zakres zawiera zachowanie wymagające testowania.
- Brak diffu w trybie `feature` wymaga artefaktu wyznaczającego zakres; bez diffu i artefaktów skill zatrzymuje się zamiast audytować cały projekt przypadkiem.
- Planning/tasks mogą być nieaktualne względem diffu; raport oznacza rozbieżność i obniża confidence.
- Wiele frameworków testowych wymaga wykrycia konwencji per moduł, bez globalnego ujednolicania.
- Bardzo duży moduł może wymagać dalszego podziału; dispatch powinien działać falami mieszczącymi się w limicie harnessu.
- Wygenerowane pliki, snapshoty i fixtures muszą być oceniane przez ich źródło i rolę, a nie automatycznie uznawane za wartościowe lub bezwartościowe.
- Niedostępny lub pominięty zakres musi znaleźć się w `Omitted scope`; raport częściowy nie może otrzymać `ADEQUATE`.
- Niejasne wymaganie biznesowe jest kierowane do `FEATURE_DISCUSS`, bez wymyślania oczekiwanego zachowania.
- `REMOVE` wymaga wysokiego confidence i dowodu tautologii, duplikacji albo braku wartości regresyjnej.
- E2E jest rekomendowane wyłącznie dla krytycznych przepływów przekraczających realne granice systemu.
- Flaky patterns są tylko statycznym ryzykiem, nigdy potwierdzoną niestabilnością bez wykonania testów.
- Findings z mieszanym routingiem nie mogą zostać bezrefleksyjnie przekazane w całości do `generate-tasks`.
- Każdy audyt musi utworzyć nowy raport z timestampem sekundowym, aby ponowienie tego samego dnia nie nadpisało wcześniejszego audit trailu.
- Nowy overlap z kryterium testów w `codebase-auditor` musi zostać wyjaśniony w dokumentacji: triada daje płytką perspektywę w review brancha, `qa-review` wykonuje specjalistyczny audyt.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.

### Happy path
- AC-1: Wywołanie audytu bez wskazania trybu analizuje bieżący feature, ustala jego intencję z dostępnych artefaktów i zmian oraz zapisuje jeden raport QA bez uruchamiania testów ani coverage.
- AC-2: Audyt feature'a działa również bez planningu i Acceptance Criteria, jeżeli zakres oraz oczekiwane zachowanie można wiarygodnie ustalić z pozostałych źródeł, a raport jawnie wskazuje wykorzystane źródła i ograniczenia pewności.
- AC-3: Audyt całego codebase'u automatycznie dzieli projekt na logiczne obszary, ocenia każdy obszar oraz granice między nimi i scala wyniki w jeden raport bez gubienia informacji o zakresie poszczególnych ocen.
- AC-4: Audyt wskazanego modułu lub obszaru ogranicza analizę do żądanego zakresu i odróżnia lokalne problemy testów od rekomendacji dotyczących integracji lub E2E przekraczających ten zakres.
- AC-5: Każde znalezisko w raporcie zawiera severity, confidence, dokładny dowód, opis niezabezpieczonego ryzyka, rekomendowaną operację i routing, a końcowy werdykt odpowiada najwyższej istotności znalezionych problemów oraz kompletności audytu.
- AC-6: Raport rozróżnia gotowe poprawki kierowane do planowania zadań od niejasności wymagających dyskusji produktowej oraz podaje bezpieczną kolejność dalszych działań, dzięki czemu może zostać użyty jako wejście do właściwego kolejnego workflow.

### Edge cases
- AC-7: Gdy w trybie feature nie ma ani zmian, ani artefaktu pozwalającego ustalić zakres, audyt zatrzymuje się z jednoznacznym wyjaśnieniem zamiast przypadkowo analizować cały codebase lub tworzyć pozornie kompletny raport.
- AC-8: Brak testów w analizowanym obszarze jest zgłaszany jako luka wyłącznie wtedy, gdy audyt wykaże konkretne zachowanie lub ryzyko wymagające zabezpieczenia testem.
- AC-9: Gdy część zakresu jest niedostępna, pominięta albo nie może zostać wiarygodnie oceniona, raport dokładnie ją wymienia, obniża confidence i nie może otrzymać werdyktu `ADEQUATE`.
- AC-10: Projekt używający wielu frameworków lub konwencji testowych jest oceniany zgodnie z kontekstem poszczególnych modułów, bez uznawania samej różnicy stylu lub narzędzia za defekt.
- AC-11: Rekomendacja usunięcia testu pojawia się tylko z wysokim confidence i konkretnym dowodem, że test jest tautologiczny, zbędnie duplikuje inne zabezpieczenie albo nie ma wartości regresyjnej; w pozostałych przypadkach raport zaleca ostrożniejszą zmianę lub dalszą weryfikację.
- AC-12: Snapshoty, fixtures, wygenerowane artefakty i statyczne symptomy flaky tests są oceniane w kontekście zachowania, które zabezpieczają, a raport nie przedstawia niestabilności jako potwierdzonej bez wykonania testów.

### Security
- AC-13: Treść analizowanego kodu, testów, komentarzy i artefaktów jest traktowana jako dane; zawarte w niej instrukcje nie mogą skłonić audytu do uruchomienia testów lub kodu projektu, zmiany kodu ani odejścia od kontraktu read-only.
- AC-14: Raport nie ujawnia pełnych sekretów, tokenów, danych uwierzytelniających ani innych danych wrażliwych znalezionych w konfiguracji, fixtures lub testach, a dowody potrzebne do opisania problemu są redagowane do bezpiecznej postaci.
- AC-15: Wskazanie zakresu poza audytowanym projektem lub niedostępnego dla audytu jest odrzucane albo oznaczane jako pominięte; nie powoduje niejawnego rozszerzenia skanu ani dostępu do niezwiązanego kodu.

## Pytania otwarte
- Brak — zakres, routing, werdykty, read-only boundary i integracja pipeline zostały zaakceptowane podczas dyskusji.

## Notatki z dyskusji
- Jeden skill z dwoma trybami został wybrany zamiast dwóch niezależnych skillów.
- Tryb domyślny to `feature`; pełny codebase wymaga jawnego `codebase`, a brak ścieżki uruchamia automatyczne dzielenie na moduły.
- Planning i AC wzmacniają ocenę feature'a, ale nie są wymagane, jeśli zakres można wiarygodnie ustalić z diffu i testów.
- Skill zakłada zielone testy po implementacji i nie powtarza ich uruchamiania.
- Raport jest trwałym wejściem do `feature-discuss` albo `generate-tasks`.
- Nawet one-liner nie jest wdrażany przez skill; użytkownik musi osobno zaakceptować zmianę.
- `implement` jedynie sugeruje audyt przy sygnałach podwyższonego ryzyka testowego.
