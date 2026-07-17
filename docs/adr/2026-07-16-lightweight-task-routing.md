# ADR: Lightweight task routing i opt-in Explain w feature-discuss

## Data
2026-07-16

## Status
Accepted

## Kontekst
`feature-discuss` rozróżniał micro-change, standardowy feature i epic. Fast-path był
zdefiniowany głównie przez rozmiar zmiany: one-liner, kilka linii, prostą konfigurację
lub pojedyncze pole. Małe, spójne zadania obejmujące kilka plików i testy niepotrzebnie
przechodziły pełną ceremonię planningu, QA enrichmentu i task generation.

Fast-path pomija `generate-tasks` i `implement`, a to te skille wczytują `patterns.md`,
`rules.md`, ADR-y i aktywne wpisy `project-memory.md`. Poszerzenie fast-pathu bez
przeniesienia tego kontekstu do `feature-discuss` stworzyłoby boczne wejście do pracy
bez projektowych guardraili. Jednocześnie po `review-plan: PASS` standardowy workflow
automatycznie generował Explain HTML, choć jest to pomocniczy, ephemeralny artefakt.

Ta decyzja rozwija wcześniejszy ADR
`docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`, który ustalił, że
HARD-GATE rządzi akceptacją designu, a nie obecnością ciężkiego planning doca.

## Decyzja
1. Zastępujemy ścieżkę `Micro-change` ścieżką `Lightweight task`; nie dodajemy
   czwartego poziomu routingu.
2. Kwalifikacja lightweight opiera się na ryzyku, niepewności i potrzebie trwałego
   handoffu, nie na liczbie linii lub plików. Wymagane są: jeden spójny cel, istniejący
   wzorzec rozwiązania, brak nierozstrzygniętych decyzji produktowych, brak granic
   wysokiego ryzyka oraz możliwość bezpiecznego ukończenia w bieżącej sesji.
3. Przed routingiem i mini-designem `feature-discuss` czyta najbliższe
   `AGENTS.md`/`CLAUDE.md`, `constitution.md`, `patterns.md`, `rules.md`, właściwe ADR-y,
   aktywne i nakładające się ścieżkami wpisy `project-memory.md` oraz aktualny kod.
   Świeża ewidencja ma pierwszeństwo przed pamięcią. Brak opcjonalnego źródła kontekstu
   jest pomijany bez błędu i nie blokuje routingu.
4. Lightweight zachowuje HARD-GATE. Jawna akceptacja kompletnego mini-designu spełnia
   bramkę, ale nie autoryzuje implementacji, gdy zakres polecenia obejmował tylko design.
   Po zgodzie na wykonanie zapisuje ADR, jeśli
   zapadła znacząca decyzja architektoniczna, a pracę śledzi wewnętrzną task-listą
   harnessu lub checklistą sesji. Nie tworzy planning ani tasks doca i nie uruchamia
   QA enrichmentu, review-plan, `generate-tasks` ani `implement`; wykonuje pracę inline
   w bieżącej sesji, po czym obowiązkowo weryfikuje zmianę i przekazuje cały branch do
   `review` albo `triada-review` w składni aktywnego harnessu.
5. Każde odkryte ryzyko migracji, publicznego API lub kontraktu, security boundary,
   wielu podsystemów,
   niejasnego rozwiązania lub potrzeby trwałego wznowienia eskaluje zadanie do standardu
   albo epica.
6. Explain HTML po `review-plan: PASS` i Explain overview dla epic maina są opt-in.
   Planer generuje je wyłącznie po odpowiedzi twierdzącej. `skip` nie tworzy raportu
   ani linku, nie jest warningiem i nie blokuje pipeline'u; brak odpowiedzi nie uruchamia
   Explain automatycznie. Link do raportu w statusie fazy jest warunkowy.

## Rozważane alternatywy
- **Zachować micro-change i dodać osobny lightweight:** odrzucona, bo granice obu
  fast-pathów byłyby nieostre i dublowałyby odpowiedzialność.
- **Próg oparty na LOC/liczbie plików:** odrzucona, bo rozmiar diffu nie odzwierciedla
  ryzyka kontraktowego, migracyjnego ani bezpieczeństwa.
- **Uproszczony trwały tasks-doc:** odrzucona, bo trwałość i handoff są sygnałem do
  standardowego pipeline'u, a nie do drugiego formatu tasków.
- **Explain generowany domyślnie:** odrzucona, bo tworzy artefakt bez potwierdzonej
  potrzeby i zwiększa koszt każdego standardowego planowania.

## Konsekwencje
- (+) Małe, spójne zadania mogą zachować dyscyplinę projektową bez pełnej ceremonii.
- (+) Lightweight uwzględnia te same ADR-y, reguły, wzorce i aktywne pułapki pamięci,
  które dotąd pojawiały się dopiero downstream.
- (+) Jawne uzasadnienie routingu i możliwość eskalacji ograniczają arbitralność.
- (+) Repo nie otrzymuje niepotrzebnych planningów, tasks-doców i HTML-i.
- (−) Wewnętrzna lista lightweight nie przetrwa utraty kontekstu; zadania wymagające
  wznowienia muszą zostać eskalowane do standardowej ścieżki.
- (−) Router wymaga jakościowej oceny ryzyka zamiast prostego progu mechanicznego.
- (monitorować) Termin `micro-change` pozostaje w historycznych artefaktach; walidacja
  nie może traktować archiwów i onboardingów jako aktywnego kontraktu.

## Powiązane
- Planning: `./absolutpowers/feature/planning-lightweight-task-routing.md`
- Poprzedni ADR: `./docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`
