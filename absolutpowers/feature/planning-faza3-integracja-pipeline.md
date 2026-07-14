# Feature: Integracja warstwy domenowej — jawne terminal-state kontrakty pipeline (Faza 3 migracji)

## Status
Draft — 2026-07-14

## Problem
Po Fazie 1 (hook deklaruje łańcuch `@feature-discuss→@generate-tasks→@implement→@review/@triada-review`) i Fazie 2 (fuzje) większość integracji z planu migracji Faza 3 jest już spełniona: grep-AC w reviewerach (v3.13.0 + Faza 2), project-memory czytane przez implementation-worker, handoffy jako linie „Następny krok". Zostaje jednak **niespójność i brak jawnego kontraktu terminal-state**: każdy skill kończy inaczej sformułowaną wzmianką o następnym kroku (albo wcale), a przejście nie jest zadeklarowane jako kontrakt.

To staje się realnym problemem przy użyciu **`/goal`** (feature Claude Code: „Set a goal Claude checks before stopping"). Model jadący do ustawionego celu (np. „dowieź feature X") sprawdza przed zatrzymaniem czy cel osiągnięty — ale bez jawnego kontraktu terminal-state może **zatrzymać się przedwcześnie po skillu pośrednim** (np. uznać robotę za skończoną po `generate-tasks`, bo nic explicite nie mówi „łańcuch niedomknięty dopóki `@review` nie przejdzie"). Jawne, spójne deklaracje terminal-state prozą — czytane przez model — domykają tę lukę.

> **Intencja (dla review-tasks Intent Fidelity):** ujednolicić i sformalizować deklaracje terminal-state w 4 skillach pipeline tak, aby (a) każdy skill jawnie deklarował swój stan terminalny i następny krok spójnym formatem, (b) model prowadzony przez `/goal` nie zatrzymywał się przedwcześnie w środku pipeline, rozumiejąc że łańcuch jest niedomknięty aż do skilla terminalnego (review/ship-merge). Plus: rozstrzygnąć mapowanie „Execution Handoff" obry na absolutpowers, potwierdzić przekaz project-memory do implementera, i wyczyścić martwe wzmianki o gnhf (narzędzie nieużywane). Cel to spójność i jawność kontraktu, NIE nowa maszyneria ani format maszynowy.

## Użytkownicy
Deweloperzy Absolut Systems prowadzący pipeline absolutpowers interaktywnie — w szczególności z ustawionym `/goal` (sesja jadąca do celu przez wiele skilli). Pośrednio: każda sesja pipeline zyskuje spójny, przewidywalny handoff między krokami.

## Oczekiwane zachowanie
1. **Spójny blok terminal-state:** każdy z 4 skilli (`feature-discuss`, `generate-tasks`, `implement`, `review`) kończy ujednoliconym blokiem deklarującym stan terminalny i następny krok — ten sam format/wording we wszystkich, zamiast dzisiejszych ad-hoc linii „Następny krok".
2. **Anty-przedwczesny-stop pod `/goal`:** blok terminal-state skilla pośredniego jawnie stwierdza, że pipeline jest niedomknięty — następny krok to wywołanie kolejnego `@skilla` — aby model sprawdzający `/goal` przed zatrzymaniem kontynuował łańcuch zamiast uznać cel za osiągnięty w połowie.
3. **Skill terminalny łańcucha jawnie oznaczony:** `review`/`triada-review` (albo `ship`/merge) deklaruje się jako punkt, w którym pipeline realnie się domyka — dopiero tam „dowieziony feature" jest prawdą.
4. **Execution Handoff rozstrzygnięty:** udokumentowane, że absolutpowers nie ma forka obry „subagent-driven vs executing-plans" — `generate-tasks` ustawia `Mode` (orchestrated/single-file), `implement` go czyta i wykonuje; to jest analog, nie brakująca funkcja.
5. **Zero regresji handoffów:** istniejące „Następny krok" linie zostają zunifikowane w nowy blok, nie zdublowane.

## Wybrane rozwiązanie
**Ujednolicony blok terminal-state prozą, wszczepiony na końcu każdego z 4 skilli**, spójny format. Bez formatu maszynowego (`/goal` czyta prozę — model, nie parser; nie ma konsumenta wymagającego struktury).

Zawartość bloku (wzorzec, adaptowany per skill):
```
## Terminal state
Stan terminalny tego skilla: <co jest dostarczone>.
Następny krok w pipeline: `@<next-skill>` (<warunek/kiedy>).
Pipeline NIE jest domknięty na tym etapie — jeśli działasz pod `/goal`,
kontynuuj do skilla terminalnego (`@review`/`@triada-review` lub ship/merge),
zanim uznasz cel za osiągnięty.
```
- **feature-discuss** → terminal: zapisany + zaakceptowany spec; next: `@generate-tasks`.
- **generate-tasks** → terminal: zweryfikowany tasks-doc (Mode ustawiony); next: `@implement`.
- **implement** → terminal: zaimplementowane + final gate PASS; next: `@review`/`@triada-review` (+ opcjonalnie harvest przed commitem).
- **review**/`triada-review` → terminal: raport review; to **punkt domknięcia** pipeline (dalej: fix-loop albo merge/ship). Tu `/goal` typu „dowieziony feature" może się realnie zatrzymać.

Execution Handoff, project-memory, gnhf — obsłużone jako decyzje/doc/cleanup (patrz Plan implementacji), nie nowa mechanika.

### Uzasadnienie
- **Proza, nie format maszynowy:** jedyny realny konsument to `/goal` (model czyta prozę). gnhf (który motywował format maszynowy w planie) jest nieużywany. Format maszynowy = spekulacja pod nieistniejący parser → YAGNI.
- **Ujednolicenie, nie dodanie:** handoffy już istnieją luźno; wartość jest w spójności + jawnym „pipeline niedomknięty", nie w nowej warstwie.
- **Execution Handoff jako doc, nie kod:** analog już działa (Mode). Udokumentowanie zapobiega przyszłemu „brakuje forka obry" — to była pozorna luka.

### Rozważane alternatywy
- **Format maszynowy terminal-state (`next:` w frontmatter)** — odrzucone: brak konsumenta (gnhf nieużywany, `/goal` czyta prozę). Rezerwa: jeśli w przyszłości pojawi się headless parser, dodać wtedy pod jego faktyczny format.
- **Zostawić jak jest (luźne „Następny krok")** — odrzucone: nie adresuje przedwczesnego stopu pod `/goal` i niespójności.
- **Dodać fork Execution Handoff obry do generate-tasks** — odrzucone: implement jest jedynym egzekutorem; fork subagent-driven-vs-executing-plans nie mapuje się (to był model obry z dwoma egzekutorami).

## Zakres

### In scope
- Ujednolicony blok terminal-state w `feature-discuss`, `generate-tasks`, `implement`, `review` SKILL.md.
- Udokumentowanie rozstrzygnięcia Execution Handoff (Mode = analog) w `generate-tasks` i/lub docs.
- **Dodanie brakującego filtra `Status: active`** przy odczycie project-memory do `agents/implementation-worker.md` (realna naprawa — worker jest jedynym z pipeline'u bez tego filtra).
- Cleanup gnhf: strip w archiwalnych planning-docach Fazy 2 (`superpowers-faza2-fuzje/`) + **relabel** w żywym `skills/feature-discuss/SKILL.md` (logika fallback zostaje, ginie tylko label).
- Sweep docs (CLAUDE.md/README) pod kątem opisu terminal-state, jeśli potrzeba.

### Out of scope
- Format maszynowy terminal-state (brak konsumenta).
- **Faza 4 planu migracji („gnhf/headless")** — do osobnego rescope'u/wycięcia (gnhf nieużywany); NIE w tym featurze.
- Integracja z `/goal` głębsza niż czytelny kontrakt prozą (nie budujemy nic pod `/goal`, tylko piszemy prozę którą on czyta).
- Zmiany w grep-AC (już spełnione) i w mechanizmie project-memory **poza** brakującym filtrem `Status: active` w `implementation-worker.md` (reszta mechanizmu czytania już działa — patrz In scope).

## Plan implementacji
1. **Terminal-state block — 4 skille.** Dodać/zunifikować sekcję `## Terminal state` na końcu `skills/{feature-discuss,generate-tasks,implement,review}/SKILL.md`. Zastąpić istniejące luźne linie „Następny krok" tym blokiem (unifikacja, nie duplikacja). Spójny wording + klauzula anty-przedwczesny-stop pod `/goal`. Oznaczyć `review`/`triada-review` jako punkt domknięcia.
2. **Execution Handoff — doc.** W `generate-tasks` (sekcja o Mode) dopisać krótką notę: absolutpowers wykonuje przez `implement` (Mode orchestrated/single-file); brak forka subagent-driven/executing-plans obry — to analog, nie luka. Ewentualnie wzmianka w CLAUDE.md pipeline section.
3. **project-memory — realna naprawa filtra w workerze.** `agents/implementation-worker.md` (linia 35) czyta `project-memory.md` „if they exist", ale — w przeciwieństwie do `implement`/`review`/`generate-tasks`/`debug`/`problem-discuss` — **NIE ma** instrukcji filtrowania `Status: active`. To realny latentny bug: orchestrated workery mogą traktować wpisy `superseded`/`archived` jako aktywne podpowiedzi. Dodać do `implementation-worker.md` linię filtra `Status: active` (spójną z brzmieniem w `implement/SKILL.md`). To realna zmiana, nie „tylko weryfikacja".
4. **gnhf cleanup — dwie klasy.** (a) **Archiwalne planning-doki** `absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md`: usunąć wzmianki „nocne runy gnhf" (martwa proza, strip OK). (b) **Żywy shipowany prompt** `skills/feature-discuss/SKILL.md` (linie ~49, 55: „nocne runy gnhf", „Tryb nieinteraktywny (gnhf)") — jedyny shipowany plik z gnhf, czytany co sesję: **relabel, nie strip.** Logika (fallback bez Node, tryb nieinteraktywny) jest ważna i zostaje — usuwamy tylko martwy label „gnhf" (np. „nocne runy gnhf" → „runy headless/nieinteraktywne", „Tryb nieinteraktywny (gnhf)" → „Tryb nieinteraktywny (headless)"). (c) Dodać w planie migracji notkę przy Fazie 4, że wymaga rescope'u (gnhf nieużywany) — bez przepisywania całej Fazy 4 tutaj.
5. **Docs sweep (PL).** Zaktualizować opis pipeline/terminal-state w CLAUDE.md/README jeśli potrzeba.

## Pliki do zmodyfikowania / utworzenia
- `skills/feature-discuss/SKILL.md` — blok terminal-state (unifikacja handoffu do generate-tasks) + relabel gnhf→headless (linie ~49, 55; logika zostaje)
- `agents/implementation-worker.md` — dodać filtr `Status: active` przy odczycie project-memory (linia ~35)
- `skills/generate-tasks/SKILL.md` — blok terminal-state + nota Execution Handoff/Mode
- `skills/implement/SKILL.md` — blok terminal-state (next: review, opcjonalnie harvest); opcjonalna 1 linia project-memory w dispatchu
- `skills/review/SKILL.md` — blok terminal-state (punkt domknięcia pipeline)
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md` — strip wzmianek gnhf (archiwalne)
- `plan-migracji-hybrydowej-superpowers.md` — notka rescope przy Fazie 4
- `CLAUDE.md` / `README.md` — sweep opisu pipeline (jeśli potrzeba)

## Edge cases i ryzyka
- **Duplikacja z istniejącymi liniami handoffu** — trzeba zastąpić, nie dodać obok (ryzyko dwóch sprzecznych „następny krok"). Wymaga przejrzenia każdego skilla przed wstawieniem.
- **`review` to gate, nie ogniwo łańcucha** — jego terminal-state jest inny (domknięcie/fix-loop/merge, nie „→ następny skill"). Blok musi to odróżnić, nie udawać że review woła kolejny skill.
- **`implement` ma już nudge do harvest** — terminal-state musi go objąć spójnie (harvest opcjonalny przed commitem, review to gate), nie zdublować.
- **`/goal` — nie nadprojektować** — piszemy tylko prozę którą model czyta; żadnej logiki pod `/goal` (to feature harnessa, nie nasz).
- **Dwujęzyczność** — blok terminal-state to treść user-facing/procesowa → polski, spójnie z resztą promptów.
- **gnhf w feature-discuss = relabel, NIE strip** — fallback bez Node i tryb nieinteraktywny to ważna logika (Codex/Pi/headless bez przeglądarki); usunąć tylko martwy label „gnhf", zachować zachowanie. Strip logiki byłby regresją companiona.
- **Filtr project-memory w workerze to realna zmiana zachowania** — nie kosmetyka: dziś worker może użyć `superseded`/`archived` wpisów jako aktywnych. Trzymać brzmienie spójne z `implement/SKILL.md` (jedno źródło konwencji), nie wymyślać nowego.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.
>
> Ten feature nie ma runtime'u ani build systemu (skille to pliki markdown/prompt). Weryfikacja AC jest grep/strukturalna — czytanie plików i sprawdzanie ich zawartości — a nie uruchamianie testów.

### Happy path
- AC-1: Każdy z 4 plików `skills/{feature-discuss,generate-tasks,implement,review}/SKILL.md` zawiera dokładnie jedną sekcję nagłówkową `## Terminal state`, umieszczoną na końcu pliku (po niej nie ma innej sekcji merytorycznej — dopuszczalne są tylko końcowe sekcje typu "Begin"/instrukcja startowa, jeśli już istniały).
- AC-2: Sekcja `## Terminal state` w `feature-discuss`, `generate-tasks` i `implement` zawiera jawne odwołanie do następnego skilla w łańcuchu w formacie `@<nazwa-skilla>` (odpowiednio `@generate-tasks`, `@implement`, `@review`/`@triada-review`), zgodne z realnym następnym krokiem opisanym w treści danego skilla.
- AC-3: Sekcja `## Terminal state` we wszystkich 4 plikach zawiera zdanie stwierdzające, co jest "dostarczone"/osiągnięte na tym etapie (np. zaakceptowany spec, zweryfikowany tasks-doc, zaimplementowane zadania z final gate PASS, raport review) — czytelnik rozumie stan bez czytania reszty pliku.
- AC-4: Sekcja `## Terminal state` w `feature-discuss`, `generate-tasks` i `implement` zawiera jawną klauzulę stwierdzającą, że pipeline NIE jest domknięty na tym etapie i że pod `/goal` należy kontynuować do skilla terminalnego zamiast uznawać cel za osiągnięty.
- AC-5: `generate-tasks/SKILL.md` zawiera notę dokumentującą rozstrzygnięcie "Execution Handoff" — że `implement` jest jedynym egzekutorem sterowanym przez pole `Mode` (orchestrated/single-file), a nie że brakuje osobnego forka trybu wykonania.

### Edge cases
- AC-6: Sekcja `## Terminal state` w `review/SKILL.md` jest treściowo odróżniona od pozostałych trzech — jawnie opisuje ten skill jako punkt domknięcia/gate pipeline'u (fix-loop albo merge/ship), a NIE jako "następny krok to `@<skill>`" wskazujący na kolejny etap w łańcuchu.
- AC-7: Żadna linia treści przed sekcją `## Terminal state` w żadnym z 4 plików nie duplikuje starą, zastąpioną wersję handoffu (np. luźną linię "Następny krok: ...") w sposób sprzeczny z nową sekcją — dopuszczalne są wyłącznie odwołania wewnątrz procesu (np. instrukcja Review Gate w `generate-tasks` mówiąca użytkownikowi co zrobić po PASS), nie osobny, konkurencyjny blok terminal-state.
- AC-8: Sekcja `## Terminal state` w `implement/SKILL.md` wspomina opcjonalny harvest przed commitem w sposób spójny z istniejącym nudge'em do harvest (nie tworzy drugiego, sprzecznego zalecenia co do kolejności harvest vs review).
- AC-9: Po cleanupie żaden **żywy shipowany** plik promptu nie zawiera literalnego tokenu "gnhf" — potwierdzalne przez `grep -rl "gnhf" skills/ agents/ hooks/` zwracające pusto, ORAZ `grep -rl "gnhf" absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md` zwracające pusto (strip archiwaliów). Obejmuje (a) strip w archiwalnych `superpowers-faza2-fuzje/planning-*.md` i (b) relabel w żywym `skills/feature-discuss/SKILL.md` (linie ~49, 55). **WYŁĄCZENIE:** `docs/onboarding/*.html` (generowane snapshoty onboardingowe dla człowieka — w tym raport tej fazy, który sam omawia gnhf) oraz `plan-migracji-hybrydowej-superpowers.md` (dokument historyczny + AC-10 dodaje tam notkę, nie strip) są POZA grepem AC-9 — edycja wygenerowanych/historycznych artefaktów = rewizjonizm, ta sama zasada co archiwum `absolutpowers/feature/`. Grep AC-9 celuje wyłącznie w żywy prompt czytany przez model co sesję.
- AC-9b: Relabel w `skills/feature-discuss/SKILL.md` jest RELABELEM, nie stripem — logika fallback pozostaje obecna: plik nadal zawiera (i) instrukcję graceful-fallback braku Node (kontynuuj w terminalu, nie zgłaszaj błędu przerywającego) oraz (ii) obsługę trybu nieinteraktywnego (brak odpowiedzi = rezygnacja z companion, sesja nie zawiesza się). Ginie tylko słowo "gnhf", nie zachowanie.
- AC-10: `plan-migracji-hybrydowej-superpowers.md` zawiera przy Fazie 4 jawną notatkę, że faza wymaga rescope'u/wycięcia (gnhf nieużywany), zamiast milczącego pozostawienia jej jako aktualnej do realizacji.

### Security
- AC-11: Sekcja `## Terminal state` nie wprowadza żadnego formatu maszynowego (np. frontmatter `next:`, YAML, JSON) parsowalnego przez zewnętrzny konsument — treść jest wyłącznie prozą, zgodnie z odrzuconą alternatywą "format maszynowy"; potwierdzalne brakiem nowych kluczy frontmatter w żadnym z 4 plików.
- AC-12: `agents/implementation-worker.md` PO tej zmianie zawiera jawną instrukcję, by przy odczycie `./absolutpowers/project-memory.md` używać wyłącznie wpisów `Status: active` jako podpowiedzi (i ignorować `superseded`/`archived`) — dziś tej instrukcji brak (stan wyjściowy: worker czyta bez filtra, w przeciwieństwie do `implement`/`review`/`generate-tasks`). Potwierdzalne przez `grep -i "Status: active" agents/implementation-worker.md` zwracające trafienie. `implement/SKILL.md` ten filtr już ma i pozostaje nietknięty.
- AC-13: Zmiany wprowadzone w tym feature (terminal-state, nota Execution Handoff, cleanup gnhf) nie modyfikują ani nie usuwają istniejącego wymogu jawnej zgody użytkownika przed promocją wpisu do `project-memory.md` (HARD-GATE promocji pozostaje nietknięty).

## Pytania otwarte
- Czy `ship` też dostaje blok terminal-state (jako realny punkt merge/PR po review)? Wstępnie: tak, ale `ship` nie był w pierwotnej czwórce — do potwierdzenia.
- Faza 4 planu migracji — rescope czy wyciąć całkiem? (poza tym featurem, do decyzji osobno).

## Notatki z dyskusji
- gnhf wjechał z planu migracji (Część 1.8 / Faza 4) — użytkownik go NIE używa; do wyczyszczenia jako martwe założenie.
- Realny konsument terminal-state to `/goal` (Claude Code: „Set a goal Claude checks before stopping") — interaktywny, model czyta prozę → format maszynowy zbędny.
- Większość Fazy 3 planu była już spełniona (hook chain z Fazy 1, grep-AC istniejący, project-memory czytane); ten feature to realny, mały delta: spójność terminal-state + rozstrzygnięcia/cleanup.
- Execution Handoff obry = N/A dla absolutpowers (jeden egzekutor: implement + Mode).
