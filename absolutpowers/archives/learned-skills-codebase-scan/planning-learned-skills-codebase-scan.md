# Feature: try-learn-skill jako codebase-scan + usunięcie harvest

## Status
Draft — 2026-07-14

## Problem
Obecny `try-learn-skill` uczy się z artefaktów **jednego** zakończonego feature'a (planning + tasks + git diff) — obserwuje *jak akurat ten feature był robiony* i próbuje z tego wydestylować reużywalną procedurę. To generalizacja z **n=1**: skille wychodzą jednorazowe, przywiązane do konkretnego feature'a, bezużyteczne później. Mechanizm candidate-ledger (3.12.0, „learned-skill dopiero przy 2. wystąpieniu klasy") miał to łagodzić, ale nie działa w praktyce — sesje feature'ów są izolowane, więc „2. wystąpienie" rzadko jest łapane, a punkt obserwacji (pojedynczy diff) jest z definicji za wąski.

Dodatkowo `harvest` (cienki orkiestrator: try-learn-skill → document-feature → document-module → archiwizacja) stał się pustą skorupą: document-feature i document-module są już samodzielnymi commandami wywoływalnymi ad-hoc, a try-learn zostaje wyprowadzony na zewnątrz. Jedyną unikalną funkcją harvestu jest archiwizacja artefaktów feature'a — którą można przenieść do `ship` (closeout).

> **Intencja (dla review-tasks Intent Fidelity):** odwrócić źródło sygnału uczenia się — z „ucz się z tego jednego feature'a" (n=1, jednorazowce) na „przeskanuj cały codebase projektu i wyciągnij powtarzalne, generyczne procedury tego projektu" (n≥próg, dowód w kodzie). Przy okazji usunąć zbędny orkiestrator `harvest`, przenosząc jego jedyną unikalną funkcję (archiwizacja) do `ship`. Cel to trafniejsze, reużywalne learned-skille + prostszy zestaw skilli, NIE nowa maszyneria.

## Użytkownicy
Deweloperzy Absolut Systems prowadzący pipeline absolutpowers, którzy chcą zbudować bibliotekę project-specyficznych, wywoływalnych learned-skilli odzwierciedlających realne powtarzalne procedury ich codebase'u — odpalane świadomie, ad-hoc, kiedy uznają że warto.

## Oczekiwane zachowanie
1. **`try-learn-skill` skanuje codebase, nie feature:** odpalany ad-hoc (`/absolutpowers:try-learn-skill`, opcjonalny arg = ścieżka zawężająca skan; domyślnie cały codebase). Analizuje kod projektu, nie artefakty pojedynczego feature'a.
2. **Próg powtarzalności:** proceduralny wzorzec kwalifikuje się na learned-skilla tylko gdy występuje w kodzie **≥3 razy** (N=3, tunable), z pokazaniem miejsc (`file:line`) jako dowodu. To wprost zabija problem jednorazowców.
3. **Batch approval:** skan prezentuje listę kandydatów (nazwa + procedura + dowód wystąpień); użytkownik zaznacza które zapisać; zapisywane są tylko wybrane, do `.claude/skills/learned/{name}/SKILL.md`.
4. **Bez ledgera:** candidate-ledger (`_candidates.md`) i promocja „przy 2. wystąpieniu" znikają — skan daje dowód powtórzenia w jednym przebiegu.
5. **`harvest` usunięty całkowicie;** archiwizacja artefaktów feature'a (`planning/tasks-{slug}.md` → `absolutpowers/archives/{slug}/` + `summary.md`) przeniesiona do `ship`.
6. **Zero regresji uczenia się w pipeline:** implement nie nudguje już harvestu; zamiast tego nudguje `ship` jako closeout. document-feature/document-module pozostają samodzielne.

## Wybrane rozwiązanie
Przepisać body `skills/try-learn-skill/SKILL.md` z trybu feature-artefakt na **codebase-scan z progiem powtarzalności i batch approval**; usunąć `skills/harvest/`; przenieść archiwizację do `skills/ship/SKILL.md`; poprawić wiring (implement nudge, document-feature ref, CLAUDE.md/README).

**Granica vs `update-ai-context` (zapisana wprost w try-learn-skill):**
- `update-ai-context` → **pasywna dokumentacja**: `patterns.md`/`rules.md`/`CLAUDE.md` — „tak wygląda ten projekt", czytane biernie jako tło dla AI.
- `try-learn-skill` → **aktywne, wywoływalne procedury**: „tak SIĘ ROBI powtarzalną procedurę X w tym projekcie" — learned-skille, które agent odpala. Inny cel, inny artefakt.

Zachowane z obecnego try-learn: wysoki próg wybredności, kolizja ze statycznymi skillami (pomiń), człowiek decyduje o zapisie (teraz batch), format learned SKILL.md.

### Uzasadnienie
- **Codebase-scan > feature-artefakt:** powtarzalność w całym kodzie to twardy, weryfikowalny sygnał reużywalności; pojedynczy diff to zgadywanie z n=1. Zmiana źródła rozwiązuje problem u korzenia.
- **Ledger zbędny po zmianie źródła:** istniał tylko po to, by łapać „2. wystąpienie" między izolowanymi sesjami; skan widzi wszystkie wystąpienia naraz.
- **Usunięcie harvest = mniej maszynerii:** wrapper bez wartości (sub-skille standalone); jedyna unikalna funkcja (archiwizacja) ma naturalny dom w `ship`.
- **Batch approval:** „procedura" jest fuzzy — próg ≥N zawęża, człowiek tnie ostatecznie; batch jest szybszy niż gate-per-skill przy bootstrapie wielu naraz.

### Rozważane alternatywy
- **Zostawić try-learn na feature-artefaktach, tylko podkręcić próg** — odrzucone: nie adresuje korzenia (n=1 zostaje n=1).
- **Zostawić harvest jako orkiestrator** — odrzucone: pusta skorupa po wyprowadzeniu try-learn; document-* i tak standalone.
- **Archiwizacja jako osobny mikro-command `archive-feature`** — odrzucone: kolejny command do pamiętania; `ship` to naturalny closeout.
- **Human gate per-skill (zamiast batch)** — odrzucone jako domyślne: wolne przy bootstrapie wielu skilli; batch approval daje tę samą kontrolę.

## Zakres

### In scope
- Przepisanie `skills/try-learn-skill/SKILL.md`: codebase-scan, próg ≥3, batch approval, granica vs update-ai-context, usunięcie ledgera i trybu feature-artefakt. Aktualizacja frontmatter description/triggers (usunąć „odpalany przez harvest").
- Usunięcie `skills/harvest/` (cały katalog skilla).
- Przeniesienie archiwizacji artefaktów feature'a do `skills/ship/SKILL.md` (logika KROK 4 harvestu) + reconcile obecnego założenia ship „harvest już zarchiwizował".
- `skills/implement/SKILL.md`: nudge harvest → nudge ship.
- `skills/document-feature/SKILL.md`: usunąć odwołanie do harvest (zostaje standalone).
- `CLAUDE.md` / `README.md`: usunąć sekcję „Harvest Phase", zaktualizować opis pipeline (docs = osobne commandy, learning = ad-hoc codebase-scan, archiwizacja = w ship).

### Out of scope
- Nowy wrapper w `commands/` dla try-learn — niepotrzebny, skill jest wywoływalny jako `/absolutpowers:try-learn-skill`.
- Zmiana `update-ai-context`, `document-feature`, `document-module` poza usunięciem odwołań do harvest.
- Automatyczna detekcja „procedury" ML/AST — zostajemy przy heurystyce grep/wzorzec + osąd modelu.
- Migracja istniejących learned-skilli / `_candidates.md` w target-projektach (jeśli jakieś powstały) — poza tym featurem.

## Plan implementacji
1. **Rewrite `try-learn-skill`:** nowe body — wejście=codebase (opcjonalny scope arg), skan powtarzalnych procedur ≥N (N=3), lista kandydatów z dowodem `file:line`, batch approval, zapis wybranych do `.claude/skills/learned/`. Sekcja „Granica vs update-ai-context". Usunąć ledger, promocję 2-wystąpienia, czytanie planning/tasks/diff. Frontmatter: description + triggers bez „harvest".
2. **Przenieś archiwizację do `ship`:** wnieś logikę KROK 4 harvestu (przenieś planning/tasks do `archives/{slug}/` + `summary.md`, za zgodą, ostatni krok). Reconcile: ship przestaje zakładać „harvest już zarchiwizował" — teraz sam archiwizuje. **Rozszerz `allowed-tools` ship** o `Bash(mkdir:*)` i `Write(**/absolutpowers/archives/**/*.md)` (obecnie ma tylko `Read, Glob, Grep, Bash(git:*), Bash(gh auth:*), Bash(gh pr:*)`) — bez tego krok archiwizacji nie ma uprawnień pod tool-gatingiem Claude'a. Rozważ `Bash(mv:*)`/`git mv` zgodnie z tym jak harvest przenosił pliki.
3. **Usuń `harvest`:** skasuj `skills/harvest/` całościowo.
4. **Rewiring implement:** zamień best-effort nudge harvest na nudge ship (closeout przed commitem).
5. **Rewiring document-feature:** usuń wzmiankę o byciu odpalanym przez harvest.
6. **Docs:** CLAUDE.md (usuń „Harvest Phase (closeout)", zaktualizuj pipeline + Repository Layout jeśli wspomina harvest), README (usuń harvest z pipeline/Skills Reference, opisz nowy try-learn + archiwizację w ship), AGENTS.md mirror (symlink — auto).

## Pliki do zmodyfikowania / utworzenia
- `skills/try-learn-skill/SKILL.md` — rewrite na codebase-scan
- `skills/harvest/SKILL.md` (+ katalog) — usunięcie
- `skills/ship/SKILL.md` — wchłonięcie archiwizacji + reconcile + rozszerzenie `allowed-tools` (`mkdir`, `Write(archives)`, ew. `mv`)
- `skills/implement/SKILL.md` — nudge harvest → ship
- `skills/document-feature/SKILL.md` — usunięcie odwołania do harvest
- `CLAUDE.md` — usunięcie sekcji Harvest Phase, aktualizacja pipeline
- `README.md` — aktualizacja pipeline / Skills Reference / changelog

## Edge cases i ryzyka
- **Osierocona archiwizacja** — jeśli przeniesienie do ship jest niepełne, artefakty feature'ów przestają być sprzątane. Task musi przenieść pełną logikę KROK 4 + gate, nie jej skrót.
- **Ship zakłada dziś „harvest już zarchiwizował"** — trzeba usunąć/odwrócić to założenie, inaczej ship będzie szukał archiwum, którego nikt już nie tworzy przed nim.
- **„Procedura" jest fuzzy** — skan może produkować szum (false-positive wzorce). Próg ≥N + batch approval to filtry; skill musi wymagać dowodu `file:line` i odrzucać wzorce bez realnej proceduralności (sama duplikacja kodu ≠ procedura).
- **Skan dużego repo drogi** — opcjonalny scope-arg + próg ograniczają koszt; skill powinien pozwolić zawęzić zakres.
- **Kolizja z granicą update-ai-context** — bez jawnej sekcji demarkacji feature odtworzy niejasność „dwa narzędzia skanujące codebase". Sekcja granicy jest wymagana, nie opcjonalna.
- **Dwujęzyczność** — prompty user-facing → polski, spójnie z resztą skilli.
- **Referencje do harvest w archiwaliach/docs onboardingowych** — NIE ruszać (rewizjonizm); grep czyszczący celuje tylko w żywe prompty `skills/`+`CLAUDE.md`+`README.md`.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.
>
> Ten feature nie ma runtime'u ani build systemu (skille to pliki markdown/prompt). Weryfikacja AC jest grep/strukturalna — czytanie plików i sprawdzanie ich zawartości — a nie uruchamianie testów.

### Happy path
- AC-1: `skills/try-learn-skill/SKILL.md` (frontmatter `description` + body) opisuje wejście jako skan całego codebase'u projektu (z opcjonalnym argumentem zawężającym zakres, domyślnie cały codebase), nie jako artefakty jednego zakończonego feature'a. Potwierdzalne brakiem `git diff <base>...HEAD` jako głównego źródła wejścia i obecnością instrukcji przeszukania kodu projektu pod kątem powtarzających się wzorców.
- AC-2: `skills/try-learn-skill/SKILL.md` zawiera jawny, liczbowy próg powtarzalności ustawiony domyślnie na **3** wystąpienia wzorca w kodzie, wraz z wymogiem pokazania dowodu w formacie `file:line` dla każdego wystąpienia. Potwierdzalne przez `grep -n "3" skills/try-learn-skill/SKILL.md` zwracające trafienie w kontekście progu wystąpień oraz obecnością `file:line` (lub `plik:linia`) jako wymaganego formatu dowodu.
- AC-3: `skills/try-learn-skill/SKILL.md` opisuje jednoprzebiegowy tryb batch approval: skan prezentuje całą listę kandydatów (nazwa + procedura + dowód wystąpień) naraz, użytkownik zaznacza które zapisać, a zapisywane są WYŁĄCZNIE zaznaczone pozycje, do `.claude/skills/learned/{name}/SKILL.md` w projekcie docelowym.
- AC-4: Katalog `skills/harvest/` (wraz z `skills/harvest/SKILL.md`) nie istnieje. Potwierdzalne przez `test -d skills/harvest` zwracające brak katalogu / kod błędu.
- AC-5: `skills/ship/SKILL.md` zawiera krok archiwizacji artefaktów feature'a — przenoszenie `planning-{slug}.md`/`tasks-{slug}.md` (+ katalog fazowy, jeśli orchestrated) do `absolutpowers/archives/{slug}/` wraz z wygenerowanym `summary.md` (co zbudowano, dlaczego, kluczowe decyzje, AC, gdzie jest trwała wiedza) — logika jest obecna w treści `ship`, nie tylko wzmiankowana jako TODO.

### Edge cases
- AC-6: `skills/try-learn-skill/SKILL.md` nie zawiera już żadnego odwołania do ledgera kandydatów: `grep -i "_candidates.md" skills/try-learn-skill/SKILL.md` oraz `grep -i "ledger" skills/try-learn-skill/SKILL.md` zwracają pusto. Brak też mechanizmu "promocja przy drugim wystąpieniu" (`grep -i "drugim wystąpieniu\|promocj" skills/try-learn-skill/SKILL.md` zwraca pusto).
- AC-7: `skills/try-learn-skill/SKILL.md` zawiera jawną, wyodrębnioną treść granicy względem `update-ai-context` — rozróżniającą "pasywna dokumentacja" (update-ai-context: patterns.md/rules.md/CLAUDE.md, czytane biernie jako tło) od "aktywne, wywoływalne procedury" (learned-skille, które agent odpala). Potwierdzalne obecnością tokenu `update-ai-context` w treści pliku w kontekście jawnego porównania/rozróżnienia, nie tylko pojedynczej wzmianki w opisie.
- AC-8: Gdy skan nie znajduje żadnego wzorca spełniającego próg ≥3 wystąpień (albo znajduje wzorce bez realnej proceduralności — sama duplikacja kodu ≠ procedura), skill jawnie raportuje brak kandydatów / odrzucenie wzorca i kończy BEZ zapisu jakiegokolwiek pliku — nie forsuje ekstrakcji przy niewystarczającym dowodzie.
- AC-9: `skills/ship/SKILL.md` NIE zawiera już założenia "harvest już zarchiwizował" jako milczącego warunku wstępnego swojego działania — to zdanie albo zniknęło, albo zostało jawnie odwrócone na "ship sam archiwizuje jako ostatni krok". Potwierdzalne przeglądem sekcji dotyczącej odczytu artefaktów/archiwum w `ship/SKILL.md` zestawionej z krokiem wczytania artefaktów.
- AC-10: Żaden żywy shipowany plik promptu (`skills/`, `agents/`) nie odwołuje się do `harvest` jako istniejącego, wywoływalnego skilla (np. `TRIGGER when: ... odpalany przez harvest`, nudge `/absolutpowers:harvest`). Potwierdzalne przez `grep -rn "harvest" skills/ agents/` zwracające co najwyżej wzmianki opisowe/historyczne w `skills/ship/SKILL.md` (np. że ship przejął funkcję archiwizacji), a nie odwołania do harvestu jako aktywnego, wywoływalnego kroku pipeline'u. Archiwalne dokumenty (`absolutpowers/archives/`, `docs/onboarding/*.html`, historia zmian/changelog w `README.md`) są POZA tym grepem — edycja wygenerowanych/historycznych artefaktów byłaby rewizjonizmem.

### Security
- AC-11: Zapis learned-skilla (`.claude/skills/learned/{name}/SKILL.md`) w `try-learn-skill` nadal wymaga jawnej, wyraźnej akceptacji użytkownika PRZED zapisem (human gate zachowany mimo przejścia na batch approval) — potwierdzalne obecnością instrukcji typu "czekaj na akceptację" w sekcji zapisu i brakiem ścieżki wykonania zapisu bez gate.
- AC-12: Krok archiwizacji w `skills/ship/SKILL.md` respektuje twardą granicę przeniesioną z harvestu: przenosi i streszcza WYŁĄCZNIE artefakty bieżącego feature'a (`planning-{slug}.md`, `tasks-{slug}.md`, katalog fazowy) i jawnie NIE dotyka `reviews/`, `problem/`, `constitution.md`, `rules.md`, `patterns.md` ani artefaktów innych feature'ów. Potwierdzalne obecnością równoważnego zdania "hard boundary" w `ship/SKILL.md`.
- AC-13: Krok archiwizacji w `skills/ship/SKILL.md` wymaga jawnej akceptacji użytkownika (pokazanie listy plików + streszczenia, oczekiwanie na potwierdzenie) PRZED wykonaniem jakiegokolwiek `git mv`/`mv` — brak ścieżki cichej/automatycznej archiwizacji bez gate.

## Pytania otwarte
- Czy N=3 zostaje na stałe, czy ma być parametrem odpalenia (`/absolutpowers:try-learn-skill --min=N`)? Wstępnie: stała domyślna 3, wzmianka że można podać inną w argumencie.
- Czy istniejące learned-skille / `_candidates.md` w target-projektach wymagają migracji? Wstępnie: poza scope, ewentualnie osobno.

## Notatki z dyskusji
- Trigger ustalony: ad-hoc, gdy użytkownik uzna (nie okresowo, nie w pipeline).
- update-ai-context = dokumentacja (inny cel) — potwierdzone przez użytkownika; granica pasywne-docs vs aktywne-skille.
- Los harvest: usunąć całkowicie (dokumentacja ma osobne commandy) — decyzja użytkownika.
- Archiwizacja → ship (opcja a): jeden closeout-command.
- Próg ekstrakcji: a+c — twardy próg ≥N znajduje kandydatów, potem batch approval zaznacza które zapisać. Ledger wywalony.
