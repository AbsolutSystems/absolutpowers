# Faza 3: implement ← subagent-driven-development  (epic: fuzja mechaniki obry)

## Kontekst nadrzędny
> ZACZNIJ od przeczytania `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`.
- Epic: `planning-main.md`
- Zależności: edycyjnie niezależna; pipeline'owo konsumuje taski z Fazy 2.

## Status
Zaplanowana — 2026-07-13

## Cel fazy
Wstrzyknąć 4 mechanizmy `subagent-driven-development` w istniejący orchestrated `implement` — BEZ deprecjacji. Zachować orchestrated architecture (implementation-worker + phase-review + 99-final-verification), grep-AC, implementation-context.md budget.

## Zakres

### In scope
- **Protokół 4 statusów implementera:** DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED, z obsługą każdego (re-dispatch mocniejszym modelem, dekompozycja, eskalacja do człowieka) — dojrzalsza wersja obecnego BLOCKED handling.
- **Dobór modelu per rola:** transkrypcja z planu → tani model; integracja → standard; review finalny → najmocniejszy; z notą o turach vs cena tokena.
- **Ledger recovery po kompakcji:** `.superpowers/sdd/progress.md`-equivalent — odzysk stanu po kompakcji zamiast re-dispatchu ukończonych faz.
- **File-handoff:** task-brief / review-package jako kanał przekazu (anty-context-pollution) — vendored skrypty już w `skills/vendored/subagent-driven-development/scripts/`.

### Out of scope
- feature-discuss / generate-tasks (Fazy 1/2).
- Pełna deprecjacja implement (świadomie odrzucona — patrz main).
- Zmiana grep-AC / implementation-context.md budget (zostają).

## Wybrane rozwiązanie

**Szkielet = implement, nie sdd.** Analiza bazy potwierdzona: implement MA już orchestrated (implementation-worker + phase-review + 99-final-verification + resumption przez statusy faz i `implementation-context.md`) = ta sama architektura co sdd. Więc odwrotność hipotezy epica (obra-jako-szkielet) — tu implement dorównuje sdd architekturą. Delta = **4 mechanizmy wszczepione w istniejący orchestrated flow**, plus jeden forkowany skrypt file-handoff. Grep-AC, `implementation-context.md` budget (10 linii/faza, ~150 total), Context Contract Requires/Provides, [BLOCKER]/[WARN] gate — zostają nietknięte.

Cztery wszczepy (decyzje domknięte w sesji planowania 2026-07-13):

### Wszczep 1 — Protokół statusów 3 → 4 (czyste 4, FAILED złożony)
Obecny `PHASE_RESULT: COMPLETED | BLOCKED | FAILED` → sdd-owy zestaw **czterech**: `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`.

Mapowanie:
- `COMPLETED` → `DONE` (rename, semantyka bez zmian)
- **`DONE_WITH_CONCERNS`** (nowy) — praca skończona + zweryfikowana, ale worker flaguje wątpliwości (correctness/scope → orchestrator adresuje przed phase-review; obserwacja typu "plik rośnie" → notuje i idzie do review)
- **`NEEDS_CONTEXT`** (nowy) — worker potrzebuje info, którego nie dostał. Wyodrębniony z obecnego "BLOCKED due to unsatisfied Requires" (O3): to nie eskalacja, tylko re-dispatch z dostarczonym kontekstem
- `BLOCKED` — zostaje, ale wzbogacony o **drabinę 4-way** z sdd (obecnie O3 tylko "stop and report"):
  1. problem kontekstu → dostarcz kontekst, re-dispatch **ten sam** model
  2. wymaga więcej rozumowania → re-dispatch **mocniejszy** model
  3. task za duży → **dekompozycja** na mniejsze
  4. plan sam jest zły → **eskalacja do człowieka**
  Reguła twarda: nigdy nie ignoruj eskalacji ani nie zmuszaj tego samego modelu do retry bez zmiany.
- `FAILED` — **złożony w BLOCKED** (czyste 4). Uzasadnienie w sekcji niżej.

### Wszczep 2 — Dobór modelu per rola
Obecnie O2 routuje tylko implementera po `**Risk:**` (high→opus, reszta→sonnet). phase-review i final `review-implementation` **dziedziczą model sesji** (drogo, sprzeczne z sdd).

Rozszerzona tabela routingu:
- **Implementer, tier transkrypcji** (najtańszy, np. haiku) — gdy phase file zawiera **kompletny kod** do przepisania. **Synergia z Fazą 2**: generate-tasks po fuzji produkuje kompletny kod w krokach → implementacja = transkrypcja + testy, najtańszy tier wystarcza.
- **Implementer, standard** (sonnet) — integracja/wielopliki/pattern-matching, `Risk: low|medium`.
- **Implementer, most capable** (opus) — `Risk: high` (security, migracje, shared core), design judgment.
- **phase-review** — skalowany do rozmiaru/ryzyka diffa (mały mechaniczny diff nie wymaga opus; subtelna zmiana współbieżności — wymaga).
- **final `review-implementation`** — **jawnie most capable** (sdd: final whole-branch review = most capable, zawsze explicit).
- Reguła: **zawsze specyfikuj model jawnie przy dispatchu** (pominięty = dziedziczy sesję = zwykle najdroższy, cicho psuje sekcję). Nota "turn count beats token price" — mid-tier jako podłoga dla reviewerów i implementerów pracujących z prozą.

### Wszczep 3 — Ledger recovery (git-anchored, autorytatywny)
Obecny resumption (statusy faz w parent tasks file + `## Completed Phases` w `implementation-context.md`) jest na dysku i przeżywa kompakcję, ALE: (a) nie zapisuje zakresu commitów per faza, (b) obserwacja z użycia — status w tasks file bywa nie-aktualizowany, więc poleganie na nim przy resume jest kruche.

Rozwiązanie: **osobny ledger `progress.md`, autorytatywny i git-kotwiczony — jedno źródło do resume**, nie dwa konkurujące.
- Path: `absolutpowers/feature/{epic}/tasks-{slug}/progress.md` (obok phase dir; convention absolutpowers, NIE `.superpowers/sdd/` z obry).
- **Commitowany** (część artefaktów feature'a — przeżywa `git clean`, audytowalny) — inaczej niż gitignored scratch obry.
- Zapis: append jednej linii w tej samej wiadomości co reszta bookkeepingu, np. `Faza N: complete (commits <base7>..<head7>, review clean)`. Lżejsze i trudniejsze do pominięcia niż edycja tabeli statusów.
- Na resume: **ufaj ledger + `git log` PRZED statusami w tasks file** (reguła sdd). Fazy w ledgerze = DONE, nie re-dispatchuj. Statusy faz w tasks file zostają jako widok dla człowieka; przy rozjeździe ledger wygrywa.

### Wszczep 4 — File-handoff (review-package; task-brief pominięty)
Obecnie phase-review i final gate czytają git diff ad-hoc w kontekście orchestratora (pollution, ryzyko `HEAD~1` gubiącego multi-commit).

- **review-package — adoptowany (forkowany)** w Step O4 (phase-review) i O6 (final gate): jeden plik = commit list + `diff --stat` + `diff -U10` dla zakresu, reviewer czyta w jednym Read, diff nie wchodzi w kontekst orchestratora, poprawny BASE (nie `HEAD~1`).
  - Orchestrator **zapisuje BASE commit przed dispatchem** workera (np. do ledgera), potem `review-package BASE HEAD`.
  - **Fork na absolutpowers/**: skopiuj `scripts/review-package` (+ `sdd-workspace` helper) i zmień `dir=` z `.superpowers/sdd` na scratch pod tasks dir feature'a (gitignored scratch). Utrata prostego "reuse vendored" świadoma — cena spójnej konwencji repo.
- **task-brief — pominięty.** Działa per-Task N; orchestrated dispatchuje per-FAZA (phase file to już osobny plik, wiele tasków, worker bierze całą fazę wg Write Scope + Context Contract fazowego). Adopcja = re-split już-splitowanego pliku i złamanie modelu kontraktu. Zero wartości w orchestrated.

### Uzasadnienie
- **implement jako szkielet** — dodawanie orchestrated od zera na szkielecie sdd zdublowałoby to, co implement już ma (worker/review/context/resumption/gate). Delta jest mała i chirurgiczna; rewrite-to-unify tu = wszczepienie, nie przepisanie szkieletu.
- **Czyste 4 (FAILED złożony)** — obecny O3 traktuje BLOCKED i FAILED **identycznie** ("stop and report"), więc FAILED nie ma osobnej obsługi do utraty. BLOCKED z drabiną 4-way pokrywa twarde awarie (verification/build fail = worker nie może ukończyć → krok drabiny). DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED pokrywają trzy ortogonalne przypadki; FAILED nie dodaje czwartego. Zestaw 1:1 z community-tested obrą, mniejsza powierzchnia mapowania.
- **Ledger autorytatywny git-anchored** — rozwiązuje realny problem (nie-aktualizowany status) przez oparcie recovery na commitach istniejących w git niezależnie od stanu markdown. Jedno źródło prawdy zamiast dwóch konkurujących (edge-case w main ostrzegał o duplikacji — tu unikniętej przez autorytatywność, nie przez dodanie równoległego).
- **review-package tak, task-brief nie** — granularność: review-package pasuje do per-faza dispatchu (BASE..HEAD fazy), task-brief operuje na granularności taska poniżej dispatchu → redundantny z pre-splitem faz.

### Rozważane alternatywy
- **Pełna deprecjacja implement na rzecz sdd** — odrzucona w `planning-main.md` (utrata warstwy domenowej: grep-AC, ADR, project-memory, orchestrated gates, epic path resolution).
- **4+1 (zachowaj FAILED)** — twardo odróżnić "test/build fail" od "utknąłem". Odrzucone: więcej niuansu bez osobnej obsługi, rozjazd z obrą.
- **Wzbogacenie istniejącego resumption zamiast osobnego ledgera** — rozważone; odrzucone bo nie adresuje obserwowanego nie-aktualizowania statusu (patrz Uzasadnienie).
- **Reuse skryptów vendored as-is (`.superpowers/sdd/`)** — zero edycji, ale wprowadza drugą ścieżkę scratch (`.superpowers/`) obok `absolutpowers/`. Odrzucone na rzecz forka dla spójności repo.
- **Adopcja task-brief** — odrzucona (analiza granularności powyżej).
- **Portowanie mechanizmów na Codex/Pi** (multi_agent / pi-subagents) — poza zakresem tej fazy; patrz `references/{harness}-tools.md`. Skill body zostaje host-agnostyczny; routing modelu i dispatch to Claude-only sekcje, inertne gdzie indziej.

## Plan implementacji

Kolejność wszczepów niezależna edycyjnie w obrębie `implement`, ale grupuję wg pliku:

1. **`agents/implementation-worker.md`** — Output Format: `PHASE_RESULT` 3 → 4 statusy (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`). Sekcja Process: worker zgłasza `NEEDS_CONTEXT` przy niespełnionym Requires (zamiast BLOCKED), `DONE_WITH_CONCERNS` gdy skończył ale flaguje wątpliwość. Zaktualizować regułę "Use COMPLETED only when…" → DONE.
2. **`skills/implement/SKILL.md` — Step O2** — rozszerzona tabela routingu modelu (tier transkrypcji dla kompletnego-kodu faz + reguła "always explicit"). Orchestrator zapisuje BASE commit przed dispatchem.
3. **`skills/implement/SKILL.md` — Step O3** — obsługa 4 statusów: DONE→review, DONE_WITH_CONCERNS→czytaj concerns przed review, NEEDS_CONTEXT→dostarcz kontekst+re-dispatch, BLOCKED→drabina 4-way.
4. **`skills/implement/SKILL.md` — Step O4 + O6** — dispatch review-package przed phase-review i final gate; przekaż package path zamiast "read git diff". Model phase-review skalowany do diffa; final gate jawnie opus.
5. **`skills/implement/SKILL.md` — ledger** — nowa sekcja "Durable Progress (ledger)": path, format linii, commit BASE tracking, reguła resume (ledger+git log przed statusami). Wpiąć w O1 (resumption) i O4 (append po PASS).
6. **`agents/phase-review.md` + `agents/review-implementation.md`** — przyjmij `review package path` jako wejście, czytaj diff z pliku zamiast uruchamiać git.
7. **Fork skryptu** — skopiuj `review-package` (+ `sdd-workspace`) do lokalizacji absolutpowers (np. `skills/implement/scripts/`), zmień `dir=` na scratch pod tasks dir; gitignored scratch.
8. **Doc sync** (CLAUDE.md rule): zaktualizować opisy w `CLAUDE.md`, `README.md`, `docs/` gdzie opisany PHASE_RESULT / model routing / resumption.
9. **Walidacja jakości** (Faza 5 planu migracji): test metodą `writing-skills` — baseline RED (implement bez wszczepów gubi stan po kompakcji / dziedziczy drogi model / diff pollution) → GREEN (z wszczepami).

## Pliki do zmodyfikowania / utworzenia
- `skills/implement/SKILL.md` — O2 routing, O3 statusy+drabina, O4/O6 review-package, nowa sekcja ledger (MODYFIKACJA)
- `agents/implementation-worker.md` — output format 3→4 statusy (MODYFIKACJA)
- `agents/phase-review.md` — przyjmij package path (MODYFIKACJA)
- `agents/review-implementation.md` — przyjmij package path (MODYFIKACJA)
- `skills/implement/scripts/review-package` + `sdd-workspace` — fork z vendored, path absolutpowers (UTWORZENIE)
- `CLAUDE.md`, `README.md`, `docs/` — sync opisów (MODYFIKACJA wg potrzeby)
- runtime (per-feature, nie w repo pluginu): `absolutpowers/feature/{epic}/tasks-{slug}/progress.md` (ledger, tworzony przez implement w target-projekcie)

## Edge cases i ryzyka
- **Ledger vs statusy faz rozjazd** — reguła twarda: ledger + `git log` autorytatywne na resume, statusy tasks file to widok dla człowieka. Dokumentować wprost w sekcji Durable Progress, inaczej wraca dwuźródłowa konfuzja.
- **BASE commit tracking** — orchestrator MUSI zapisać BASE przed dispatchem (do ledgera). Bez tego review-package spadnie do `HEAD~1` i zgubi multi-commit fazy. Krok O2 twardy.
- **Tier transkrypcji fałszywie tani** — jeśli phase file NIE ma kompletnego kodu (tylko prozę), haiki weźmie 2-3× tur → drożej. Sygnał doboru: "kompletny kod w krokach" musi być realnie w phase file (zależność od jakości outputu Fazy 2). Gdy wątpliwe → sonnet.
- **Fork skryptu a MIT** — review-package/sdd-workspace pochodzą z obra/superpowers (MIT). Fork musi zachować atrybucję (nagłówek + wpis w `VENDORED.md`), tak jak vendored skille.
- **Scratch gitignored a `git clean -fdx`** — scratch (review packages) ginie przy clean; to OK (efemeryczne). Ledger commitowany → przeżywa. Nie mylić dwóch lokalizacji.
- **Kompletny kod faz vs implementation-context.md budget** — rozgraniczenie ról: phase file = pełny spec/kod fazy; implementation-context.md = wąski handoff między fazami (10 linii); ledger = mapa recovery (commity). Trzy pliki, trzy role — udokumentować by nie zlały się.
- **Single-file mode** — wszczepy 2/3/4 dotyczą orchestrated (dispatch subagentów). Single-file nie dispatchuje → status protokół (1) go nie dotyczy, ledger opcjonalny. Nie forsować sdd-mechaniki na single-file.

## Pytania otwarte
Rozstrzygnięte w sesji planowania 2026-07-13:
- ~~Ledger: reuse resumption czy osobny ledger obry?~~ → **osobny, git-anchored, autorytatywny; jedno źródło do resume** (rozwiązuje obserwowane nie-aktualizowanie statusu).
- ~~Protokół 4 statusów vs PHASE_RESULT (COMPLETED/BLOCKED/FAILED)~~ → **czyste 4** (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED), FAILED złożony w BLOCKED.
- ~~task-brief adoptować?~~ → **pominąć** (redundantny z per-faza dispatchem).
- ~~Scratch path~~ → **fork na absolutpowers/**.

Pozostałe (do Fazy 2/3 planowania severity — przekrojowe z main):
- Mapowanie `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor obry — czy dotknąć przy tej fazie (review-package niesie findings reviewera)? Wstępnie: NIE w tej fazie, taksonomia severity zostaje absolutpowers ([BLOCKER]/[WARN]); tylko kanał przekazu (plik) się zmienia.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.

Uwaga metodologiczna: ta faza fuzuje mechanikę skilla (nie feature aplikacyjny). "Zachowanie" = treść plików pluginu (`skills/implement/SKILL.md`, `agents/*.md`, forkowany skrypt). AC są więc grep-weryfikowalne względem tych plików, nie względem runtime aplikacji.

### Happy path
- AC-1: `agents/implementation-worker.md` w sekcji Output Format wylicza dokładnie cztery wartości `PHASE_RESULT`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED` — linia statusu nie zawiera już `COMPLETED` ani `FAILED`.
- AC-2: `agents/implementation-worker.md` przenosi regułę "Use COMPLETED only when…" na `DONE` (ten sam warunek, nowa nazwa), dodaje osobny, jawny warunek zgłoszenia `DONE_WITH_CONCERNS`, oraz instruuje worker aby przy niespełnionym `Context Contract -> Requires` zgłaszał `NEEDS_CONTEXT` zamiast `BLOCKED`.
- AC-3: Step O3 w `skills/implement/SKILL.md` opisuje cztery odrębne ścieżki obsługi — jedną na status: `DONE` → phase-review, `DONE_WITH_CONCERNS` → orchestrator czyta zgłoszone wątpliwości przed phase-review, `NEEDS_CONTEXT` → orchestrator dostarcza brakujący kontekst i re-dispatchuje tę samą fazę, `BLOCKED` → drabina eskalacji — a nie jedną wspólną gałąź "BLOCKED lub FAILED, zatrzymaj się i raportuj".
- AC-4: Obsługa statusu `BLOCKED` w Step O3 zawiera udokumentowaną drabinę czterech kroków, w tej kolejności: (1) dostarcz brakujący kontekst i re-dispatchuj **ten sam** model, (2) re-dispatchuj **mocniejszy** model, (3) **dekomponuj** fazę na mniejsze zadania, (4) **eskaluj do człowieka** — wraz z regułą, że eskalacji nigdy się nie ignoruje i ten sam model nie jest ponownie wywoływany bez zmiany wejścia.
- AC-5: Step O2 w `skills/implement/SKILL.md` zawiera tabelę/regułę routingu modelu z co najmniej trzema jawnie nazwanymi tierami implementera (tier transkrypcji/najtańszy dla faz z kompletnym kodem, standard, most-capable dla `Risk: high`), oraz jawnie podanym (nie odziedziczonym po sesji) modelem dla `phase-review` skalowanym do ryzyka/rozmiaru diffa i jawnie `opus`/most-capable dla `review-implementation`.
- AC-6: `skills/implement/SKILL.md` zawiera nową, samodzielną sekcję o ledgerze ("Durable Progress" lub równoważny nagłówek) opisującą: ścieżkę pliku ledgera obok katalogu faz, format jednej linii dziennika per faza z zakresem commitów (BASE..HEAD w skrócie), oraz regułę że orchestrator zapisuje BASE commit **przed** dispatchem workera (w Step O2, nie po fakcie).
- AC-7: Step O4 i Step O6 w `skills/implement/SKILL.md` uruchamiają skrypt review-package przed dispatchem odpowiednio `phase-review` i `review-implementation`, i przekazują w promptcie ścieżkę wygenerowanego pliku pakietu — żaden z tych kroków nie instruuje już reviewera do samodzielnego uruchomienia `git diff` / `git diff --cached` na wejściu.
- AC-8: `agents/phase-review.md` oraz `agents/review-implementation.md` przyjmują ścieżkę pliku review package jako część wejścia i czytają diff z tego pliku (jednym `Read`), a sekcja "Required Checks"/"Input" tych agentów nie zawiera już listy komend `git diff` do samodzielnego wykonania.

### Edge cases
- AC-9: Sekcja ledgera w `skills/implement/SKILL.md` jawnie stwierdza, że przy rozjeździe między wpisem w ledgerze a statusem fazy w tasks file, **ledger + `git log` są autorytatywne przy resume** — status w tasks file jest opisany jako widok dla człowieka, nie źródło prawdy.
- AC-10: `skills/implement/SKILL.md` jawnie ogranicza zasięg czterostatusowego protokołu, tabeli routingu modelu per rola i ledgera do trybu orchestrated — sekcja Single-File Process nie używa słownictwa `DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED` ani nie wymaga pliku ledgera do wznowienia.
- AC-11: Reguła doboru tieru transkrypcji w Step O2 zawiera jawny warunek fallback: gdy phase file nie zawiera kompletnego, gotowego do przepisania kodu (przypadek wątpliwy), routing wskazuje tier standard — nie domyślnie najtańszy tier.
- AC-12: Step O2 (lub sąsiadująca reguła routingu) jawnie stwierdza, że dispatch subagenta bez jawnie podanego parametru modelu jest błędem względem reguły "always explicit" (domyślne dziedziczenie modelu sesji nie jest opisane jako dopuszczalny skrót dla żadnej z ról: implementer/phase-review/review-implementation).

### Security / integralność
- AC-13: Forkowany skrypt review-package (i `sdd-workspace`, jeśli forkowany razem z nim) pod ścieżką absolutpowers zachowuje notę atrybucji MIT w nagłówku pliku, a zmienna/ścieżka katalogu wyjściowego w forku nie wskazuje już na `.superpowers/sdd` — wskazuje na scratch pod katalogiem faz danego feature'a.
- AC-14: `VENDORED.md` zawiera nowy lub zaktualizowany wpis w tabeli zvendorowanych elementów dokumentujący fork review-package/`sdd-workspace`: źródłową ścieżkę, docelową ścieżkę absolutpowers, oraz deltę wobec oryginału (zmiana lokalizacji katalogu scratch) — analogicznie do istniejących wpisów w tym pliku.
- AC-15: Żaden ze zmodyfikowanych plików pluginu (`skills/implement/SKILL.md`, `agents/implementation-worker.md`, `agents/phase-review.md`, `agents/review-implementation.md`) nie zawiera dispatchu ani odwołania do `task-brief` — treść odzwierciedla decyzję "task-brief pominięty", nie tylko plan.

## Pytania otwarte
- Ledger recovery: użyć istniejącego mechanizmu resumption orchestrated implement (statusy w parent tasks file) czy dodać osobny ledger obry? Możliwe że orchestrated już to pokrywa — zweryfikować przy planowaniu.
- Protokół 4 statusów vs obecny PHASE_RESULT (COMPLETED/BLOCKED/FAILED) — zmapować na wspólny zestaw.

## Notatki z dyskusji
- 2026-07-13: sesja planowania. Potwierdzono szkielet = implement (nie sdd) — implement już dorównuje architekturą orchestrated.
- Cztery decyzje domknięte: (1) czyste 4 statusy, FAILED złożony; (2) ledger osobny git-anchored autorytatywny; (3) fork skryptów na absolutpowers/; (4) task-brief pominięty, review-package adoptowany.
- Driver decyzji o ledgerze: obserwacja z użycia, że status w tasks file bywa nie-aktualizowany → recovery oparty na commitach w git, niezależny od markdown.
- Synergia z Fazą 2: tier transkrypcji modelu opiera się o kompletny-kod-w-krokach z outputu generate-tasks po fuzji.
