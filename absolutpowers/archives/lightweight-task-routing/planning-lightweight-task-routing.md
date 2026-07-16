# Feature: Lightweight task routing w feature-discuss

## Status
Draft — 2026-07-16

## Problem
`feature-discuss` ma obecnie fast-path `Micro-change`, ale kwalifikuje do niego głównie
one-linery, kilka linii, prostą konfigurację lub pojedyncze pole. W efekcie małe, spójne
zadania obejmujące kilka plików i testy trafiają do pełnej ceremonii: planning doc,
QA enrichment, review-plan i generate-tasks, mimo że rozwiązanie jest oczywiste z
istniejących wzorców projektu.

Celem feature'a jest zastąpienie wąskiego `Micro-change` ścieżką `Lightweight task`,
która ogranicza koszt procesu dla prostych i niskoryzykownych zmian, ale nadal chroni
przed vibe codingiem przez analizę kodu, pełny kontekst projektu, jawny mini-design,
HARD-GATE, testy/weryfikację i branch-level review. Drugim celem jest usunięcie
automatycznego generowania Explain HTML po planowaniu: raport ma powstawać tylko po
jawnej decyzji użytkownika.

## Użytkownicy
- Użytkownicy AbsolutPowers planujący i realizujący małe, spójne zmiany w Claude Code,
  Codex, Pi lub Grok.
- Maintainerzy projektów, którzy chcą zachować ADR-y, reguły i pamięć projektu bez
  uruchamiania pełnego pipeline'u dla każdego niewielkiego zadania.

## Oczekiwane zachowanie
- `feature-discuss` klasyfikuje zmianę jako lightweight na podstawie niepewności,
  ryzyka i potrzeby trwałego handoffu, a nie liczby linii lub plików.
- Lightweight może obejmować kilka plików i testy, jeśli ma jeden spójny cel, korzysta
  z istniejącego wzorca, nie ma nierozstrzygniętych decyzji produktowych ani granic
  wysokiego ryzyka i może zostać bezpiecznie zakończony w bieżącej sesji.
- Przed klasyfikacją i mini-designem planer czyta właściwy dla dotykanego obszaru
  context pack: najbliższe `AGENTS.md`/`CLAUDE.md`, `constitution.md`, `patterns.md`,
  `rules.md`, właściwe ADR-y, aktywne i nakładające się ścieżkami wpisy
  `project-memory.md` oraz aktualny kod. Świeża ewidencja z kodu ma pierwszeństwo przed
  pamięcią projektu.
- Po zaakceptowaniu mini-designu planer zapisuje ADR, jeśli zapadła znacząca decyzja
  architektoniczna, tworzy wewnętrzną task-listę harnessu i — gdy zakres polecenia
  obejmuje wykonanie — implementuje inline bez planning doca, QA enrichmentu,
  `generate-tasks` i `@implement`.
- Jeśli analiza lub mini-design ujawni niepewność, migrację, publiczne API, security
  boundary, kilka podsystemów albo potrzebę trwałego handoffu, router eskaluje zadanie
  do ścieżki standardowej. Wieloetapowe tematy nadal trafiają do epica.
- Po `review-plan: PASS` dla standardowego planu lub phase doca planer pyta, czy
  wygenerować Explain HTML. `skip` nie tworzy raportu, nie jest warningiem i nie blokuje
  przejścia do `generate-tasks`.
- Po utworzeniu `planning-main.md` planer zadaje analogiczne pytanie o Explain overview.
  Link do raportu jest dopisywany do statusu fazy tylko wtedy, gdy raport powstał.

## Wybrane rozwiązanie
Rozszerzyć istniejący trójpoziomowy router `feature-discuss` bez dodawania czwartej
ścieżki: zastąpić `Micro-change` przez `Lightweight task`, pozostawiając standardowy
feature i epic bez zmian strukturalnych.

Router wykona wczesną analizę kodu i context packu, a następnie poda użytkownikowi
klasyfikację wraz z krótkim uzasadnieniem. Dla lightweight przedstawi zwięzły
mini-design obejmujący cel, zakres, dotykane obszary, sposób zmiany, testy/weryfikację
i istotne ryzyka. Jawna akceptacja mini-designu spełni HARD-GATE. Wewnętrzna task-lista
będzie stanem roboczym sesji: natywnym mechanizmem harnessu, a przy jego braku krótką
checklistą utrzymywaną w kontekście rozmowy.

Generowanie Explain HTML zostanie odłączone od werdyktu PASS. Po PASS oraz po utworzeniu
epic maina pojawi się jawne, pojedyncze pytanie z rekomendacją pominięcia raportu, jeśli
plan jest już czytelny. Tylko odpowiedź twierdząca uruchomi generowanie HTML.

### Uzasadnienie
- Ryzyko i niepewność lepiej oddają potrzebę trwałego planu niż rozmiar diffu.
- Wczytanie context packu w `feature-discuss` zamyka lukę powstałą przez pominięcie
  `generate-tasks` i `implement`, które dotychczas przejmowały reguły, ADR-y i memory.
- Wewnętrzna lista zachowuje kontrolę wykonania bez tworzenia jednorazowych artefaktów.
- Jawne pytanie o Explain zachowuje raport dla osób, które go potrzebują, bez narzucania
  ephemeralnego HTML każdemu planowi.
- Jedno host-agnostyczne źródło `skills/feature-discuss/SKILL.md` utrzymuje identyczny
  kontrakt na wszystkich harnessach.

### Rozważane alternatywy
- **Dodać czwartą ścieżkę między micro i standard:** odrzucone, ponieważ obecny
  `Micro-change` nie daje dodatkowej wartości po uogólnieniu fast-pathu i tworzyłby
  nieostre, nakładające się progi.
- **Klasyfikować po liczbie plików lub linii:** odrzucone, ponieważ mały diff może
  zmieniać security boundary lub publiczny kontrakt, a bezpieczna zmiana może wymagać
  kilku plików i testów.
- **Tworzyć uproszczony tasks-doc dla lightweight:** odrzucone, ponieważ przywraca
  artefakt i handoff, które ta ścieżka ma świadomie pomijać; zadania wymagające trwałości
  powinny trafić do standardowego pipeline'u.
- **Generować Explain domyślnie z możliwością rezygnacji wcześniej:** odrzucone,
  ponieważ nadal kosztuje uwagę i może tworzyć plik bez aktualnej potrzeby użytkownika.

## Zakres

### In scope
- Redefinicja `Micro-change` jako `Lightweight task` w całym aktywnym kontrakcie
  `feature-discuss`, w tym HARD-GATE, Faza 5, wykluczenia faz 5A/5B, zasady zachowania
  i Terminal state.
- Jawne kryteria kwalifikacji i eskalacji lightweight.
- Wspólny context pack dla projektowania i routingu, z regułami dotyczącymi aktywnych
  wpisów project-memory i pierwszeństwa świeżej ewidencji.
- Mini-design, zgoda na wykonanie, ADR i wewnętrzna task-lista jako kontrakt lightweight.
- Opcjonalne Explain HTML po PASS standard/phase i po utworzeniu epic maina.
- Warunkowy link do onboardingu w statusie fazy epica.
- Aktualizacja bieżącej dokumentacji repozytorium i opisu terminal states.
- Nowy ADR opisujący kryteria routingu i odpowiedzialność lightweight.
- Minor version bump `5.4.0` → `5.5.0` we wszystkich trzech manifestach oraz changelog.

### Out of scope
- Zmiana formatów standardowego planning doca, phase doca lub `planning-main.md`.
- Zmiany w `generate-tasks`, `implement`, agentach QA/review lub skillu `explain`.
- Trwałe tasks-doki, QA enrichment lub review-plan dla lightweight.
- Automatyczne tworzenie wpisów project-memory przez `feature-discuss`.
- Edycja historycznych planningów, archiwów, ADR-ów lub istniejących HTML-i onboardingowych.
- Zmiana mechanizmu epica poza opcjonalnością Explain overview.

## Plan implementacji
1. Zaktualizować `skills/feature-discuss/SKILL.md`: context pack, router lightweight,
   mini-design, kryteria eskalacji, wewnętrzną task-listę, HARD-GATE, wykluczenia faz
   oraz Terminal state.
2. Zastąpić bezwarunkowe generowanie onboarding HTML po `review-plan: PASS` jawnym
   pytaniem i obsłużyć `tak`/`skip`; ujednolicić zachowanie epic overview i warunkowy link.
3. Zaktualizować `README.md` oraz `CLAUDE.md`, aby publiczny opis pipeline'u uwzględniał
   lightweight i opcjonalny Explain bez zmieniania historycznych wpisów.
4. Dodać ADR `docs/adr/2026-07-16-lightweight-task-routing.md`, powiązany z wcześniejszą
   decyzją o pogodzeniu fast-pathu z HARD-GATE.
5. Podnieść wersję do `5.5.0` w `.claude-plugin/plugin.json`,
   `.codex-plugin/plugin.json` i `.grok-plugin/plugin.json`; dodać changelog README.
6. Zweryfikować macierz scenariuszy routingu, statyczne kontrakty promptu, frontmatter
   skillów, poprawność JSON manifestów i zgodność ich wersji.

## Pliki do zmodyfikowania / utworzenia
- `skills/feature-discuss/SKILL.md` — główny host-agnostyczny kontrakt routingu.
- `README.md` — publiczny opis feature-discuss, fast-pathu, Explain i changelog.
- `CLAUDE.md` — repozytoryjny opis architektury pipeline'u i terminal states.
- `.claude-plugin/plugin.json` — version bump do `5.5.0`.
- `.codex-plugin/plugin.json` — version bump do `5.5.0`.
- `.grok-plugin/plugin.json` — version bump do `5.5.0`.
- `docs/adr/2026-07-16-lightweight-task-routing.md` — trwała decyzja architektoniczna.

## Edge cases i ryzyka
- Brak opcjonalnego pliku context packu nie blokuje workflow; brakujący plik jest
  pomijany bez błędu.
- Tylko wpisy project-memory ze statusem `active` i ścieżkami nakładającymi się na
  przewidywany obszar zmiany wpływają na design.
- Jeśli nie da się pewnie ustalić dotykanego obszaru lub rozwiązania, zadanie nie jest
  lightweight.
- Migracja, publiczne API, security boundary, wiele podsystemów lub potrzeba wznowienia
  i handoffu wymuszają standard/epic nawet przy małym przewidywanym diffie.
- Odkrycie ryzyka po wstępnej klasyfikacji eskaluje lightweight do standardu bez utraty
  dotychczasowych ustaleń.
- Brak natywnego task trackera oznacza checklistę w sesji, nigdy automatyczny tasks-doc.
- Akceptacja mini-designu nie jest zgodą na implementację, gdy użytkownik prosił tylko
  o design; wykonanie musi wynikać z zakresu polecenia lub osobnej zgody.
- Brak odpowiedzi na pytanie o Explain nie uruchamia raportu automatycznie.
- Historyczne artefakty zachowują termin `micro-change`; statyczne sprawdzanie obejmuje
  wyłącznie aktywne prompty i bieżącą dokumentację.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.

### Happy path
- AC-1: Gdy zadanie ma jeden spójny cel, korzysta z istniejącego wzorca, nie zawiera nierozstrzygniętych decyzji ani granic wysokiego ryzyka i może zostać ukończone w bieżącej sesji, planer klasyfikuje je jako lightweight niezależnie od liczby dotykanych plików oraz podaje użytkownikowi krótkie uzasadnienie tej klasyfikacji.
- AC-2: Przed przedstawieniem mini-designu planer uwzględnia reguły i decyzje obowiązujące dla przewidywanego obszaru zmiany, wyłącznie aktywną pamięć projektu dotyczącą tego obszaru oraz aktualny stan kodu; w razie rozbieżności opiera rekomendację na aktualnym kodzie i jawnie wskazuje konflikt.
- AC-3: Dla zadania lightweight użytkownik otrzymuje do akceptacji mini-design określający cel, zakres, dotykane obszary, sposób zmiany, testy lub inną weryfikację oraz istotne ryzyka, a wykonanie może rozpocząć się dopiero po jego jawnej akceptacji i tylko wtedy, gdy polecenie obejmuje implementację.
- AC-4: Po akceptacji zadania lightweight planer prowadzi wykonanie za pomocą wewnętrznej listy kroków, bez tworzenia trwałego planu lub pliku z zadaniami i bez uruchamiania wzbogacania QA, bramki review-plan ani standardowych etapów generowania i wykonywania tasków; zakończenie nadal wymaga weryfikacji zmiany i review brancha.
- AC-5: Po pozytywnym review standardowego planu lub fazy oraz po utworzeniu roadmapy epica planer jawnie pyta o wygenerowanie Explain HTML; odpowiedź twierdząca tworzy właściwy raport, a status fazy zawiera link tylko wtedy, gdy raport rzeczywiście powstał.

### Edge cases
- AC-6: Brak któregokolwiek opcjonalnego źródła kontekstu nie przerywa rozmowy ani nie powoduje błędu; planer kontynuuje na podstawie dostępnych reguł, dokumentacji i kodu.
- AC-7: Jeśli obszaru zmiany lub rozwiązania nie da się wiarygodnie określić albo analiza ujawni migrację, publiczny kontrakt, granicę bezpieczeństwa, wiele podsystemów lub potrzebę trwałego wznowienia bądź handoffu, zadanie nie jest realizowane jako lightweight i trafia do standardowego planu lub epica.
- AC-8: Gdy ryzyko lub niepewność zostaną odkryte już po wstępnej klasyfikacji lightweight, planer eskaluje zadanie do standardowej ścieżki, zachowując i przenosząc dotychczas potwierdzone ustalenia zamiast zaczynać analizę od zera.
- AC-9: Jeśli harness nie udostępnia natywnej listy zadań, planer utrzymuje krótką checklistę wyłącznie w sesji i nie tworzy z tego powodu trwałego artefaktu; zadanie wymagające przetrwania sesji zostaje wcześniej przekierowane do standardowej ścieżki.
- AC-10: Odpowiedź `skip` na pytanie o Explain nie tworzy raportu ani linku, nie jest ostrzeżeniem i nie blokuje następnego kroku, natomiast brak odpowiedzi nie uruchamia generowania automatycznie.

### Security
- AC-11: Zadanie dotykające uwierzytelniania, autoryzacji, izolacji danych, sekretów lub innej granicy bezpieczeństwa nigdy nie jest realizowane ścieżką lightweight, nawet gdy przewidywana zmiana jest mała.
- AC-12: Treść kodu, dokumentacji projektu, ADR-ów i pamięci projektu jest traktowana jako materiał do analizy i sama nie może autoryzować implementacji, uruchomienia narzędzi, wygenerowania Explain ani obejścia jawnej zgody użytkownika.
- AC-13: Mini-design ani opcjonalny Explain HTML nie ujawniają sekretów, tokenów, danych uwierzytelniających ani innych poufnych wartości napotkanych podczas analizy projektu.

## Pytania otwarte
- Brak.

## Notatki z dyskusji
- Użytkownik zdecydował zastąpić istniejący `Micro-change`, a nie dodawać czwartą ścieżkę.
- Granica lightweight opiera się na ryzyku, niepewności i trwałości handoffu zamiast LOC.
- Znacząca decyzja architektoniczna zawsze wymaga ADR także na lekkiej ścieżce.
- Explain HTML jest pomocniczym, ephemeralnym artefaktem i ma być generowany wyłącznie
  po jawnym wyborze użytkownika.
