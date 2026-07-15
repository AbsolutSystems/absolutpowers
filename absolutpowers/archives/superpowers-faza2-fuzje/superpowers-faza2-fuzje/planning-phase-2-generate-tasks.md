# Faza 2: generate-tasks ← writing-plans  (epic: fuzja mechaniki obry)

## Kontekst nadrzędny
> ZACZNIJ od przeczytania `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`.
- Epic: `planning-main.md`
- Zależności: edycyjnie niezależna; pipeline'owo konsumuje spec z Fazy 1, dostarcza taski dla Fazy 3.
- ADR: `./docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md` (szkielet + rekoncyliacje).

## Status
Zaplanowana — 2026-07-13

## Cel fazy
Przejąć strukturę zadań `writing-plans` obry do `generate-tasks`, zachowując grep-AC, project-memory, tryb orchestrated/single-file i integrację z constitution/ADR.

## Zakres

### In scope
- Blok **Interfaces** (Consumes/Produces z dokładnymi sygnaturami) w strukturze zadania — kanał wiedzy o sąsiednich zadaniach.
- **Global Constraints** w nagłówku planu (wymagania projektowe verbatim ze speca, obowiązujące każde zadanie).
- Reguły **No Placeholders** (lista wzorców = plan failure).
- Kompletny kod w krokach (założenie "inżynier zero-context").
- Self-review: pokrycie speca + skan placeholderów + spójność typów między zadaniami.

### Out of scope
- feature-discuss / implement (Fazy 1/3).
- Zmiana grep-AC (zostaje jako warstwa domenowa; ewentualnie wzmocniona przez No-Placeholders).
- Severity taksonomia `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor — punktowana do Fazy 3 (self-review nie emituje severity; spójne z ADR Fazy 1).

## Wybrane rozwiązanie

**Metoda: rewrite-to-unify. Szkielet = generate-tasks** (624 linie gęstej warstwy domenowej: orchestrated, grep-AC, AC-traceability, epic subfolder, Test-first marker, review gate). `writing-plans` = 175 linii czystej mechaniki → dawca sekcji, NIE vendorowany osobno. Więcej do stracenia po stronie domeny → wszczepiamy mechanikę obry w szkielet generate-tasks. Odstępstwo od hipotezy epica ("obra częściej szkielet") uzasadnione gęstością domeny — tak samo jak Faza 1.

**5 graftów, wszystkie wariant A (zasada obry wszczepiona w szkielet, zero duplikacji):**

1. **Interfaces → task-level `Produces:`/`Consumes:` (dokładne sygnatury).** Dodane do formatu zadania w single-file (Section 2) i orchestrated (Task w phase file). Reguła agregacji: phase `Context Contract → Provides` = union `Produces` przekraczających granicę fazy; **nie powtarzaj** within-phase. W single-file (brak faz) działa task↔task bez rollupu. Zasila type-consistency w self-review — jedyny grep-owalny check spójności typów.

2. **Global Constraints → osobna sekcja nagłówka tasks doc**, spec-derived verbatim (wersje, naming, copy rules). Może **cytować** artykuły constitution wiążące ten feature (`Per Artykuł N: ...`), ale NIE kopiuje treści pryncypiów. Constitution.md nadal binding-context wczytywany osobno (Step 1). Trzy źródła rozłączne: GC (spec) / constitution (projekt) / rules (lint).

3. **No Placeholders → jawna lista wzorców = plan failure** w Task Guidelines. Konsoliduje rozproszone uwagi "kompletny kod" + istniejący "Bad" example w jeden kanon. Synergia z grep-AC: banuje "write tests for above" → wymusza realne nazwy testów z tokenem `AC-N`.

4. **Kompletny kod: dyscyplina, nie szablon.** Zostaje format `Requirements/Tests/Example` + `Test-first` marker. Wzmocnienie: dokładne sygnatury (przez `Produces/Consumes`), realny kod w `Example`, zero vague (przez No-Placeholders). **NIE** przejmujemy rigid 5-step TDD checkbox template. Powód rozstrzygający: podział modeli **Opus planuje / Sonnet implementuje** — implement zostaje autonomicznym inżynierem, nie transkryptorem. 5-step template zakłada najtańszy model-transkryptor (którego w implement nie ma) i front-loaduje niezweryfikowany kod (Opus w planie nie uruchamia testów; Sonnet pisze live z feedbackiem failów).

5. **Self-Review → lekki check autora PRZED bramką review-tasks:** spec coverage / placeholder scan / type consistency (`Produces` ↔ `Consumes`). Tnie iteracje bramki. Bez severity.

### Uzasadnienie
- **Szkielet per gęstość domeny** — jak ADR Fazy 1; graft mechaniki w domenę tańszy i mniej ryzykowny niż odwrotnie.
- **P1→A rozstrzygnięty modelem** (Opus-plan / Sonnet-implement): plan = kontrakt + decyzje (osąd Opusa), implement = autonomiczne wykonanie TDD z feedbackiem testów (zdolność Sonneta). B marnowałby oba: Opus klepie mechaniczny kod, Sonnet transkrybuje. Kod pisany w planie jest niezweryfikowany (model nie uruchamia) — Sonnet live iteruje przeciw realnym failom.
- **P2→A**: Interfaces to najelegantszy element writing-plans; task-level + rollup unika duplikacji z Context Contract i działa też w single-file (gdzie faz nie ma).
- **P3→A**: rozłączne zakresy zapobiegają dryfowi — pryncypium zmienia się w constitution, kopie w starych tasks docs nie gniją.
- **Severity → Faza 3**: self-review nie emituje severity; miejsce styku severity to sdd/implement (DONE_WITH_CONCERNS + review).

### Rozważane alternatywy
- **P1-B: pełny 5-step TDD checkbox template** — odrzucone. Sprzęga Fazę 2 ↔ Fazę 3 (wymusza implement→transkryptor), marnuje split Opus/Sonnet, front-loaduje niezweryfikowany kod, ~2× tokeny na zadanie (drogie dla nocnych runów headless), blast radius na review-tasks/phase-review/analyze rubryki.
- **P1-C: hybryda per marker** (`yes`→5-step, `no`→lekki) — odrzucone na teraz. Dwa formaty zadania w jednym pliku → koszt parsowania w gate/implement; enforcement zbędny skoro Sonnet autonomiczny. Rezerwa gdyby Faza 5 pokazała drift od test-first.
- **P2-B: tylko Context Contract** — odrzucone: single-file traci type-consistency całkowicie; sygnatury cross-phase opisane prozą.
- **P2-C: dwa równoległe mechanizmy** — odrzucone: duplikacja Provides/Produces → rozjazd przy aktualizacji jednego; rozdęcie phase file.
- **P3-B: jedna sekcja GC absorbująca constitution** — odrzucone: miesza zakresy feature vs projekt → dryf pryncypiów w kopiach; dublowanie binding-context.

## Plan implementacji
Edycje w `skills/generate-tasks/SKILL.md`, osadzone w istniejącej strukturze (rewrite-to-unify, nie append):

1. **Global Constraints** — dodać sekcję do nagłówka: single-file `## Project Context` oraz orchestrated main index. Instrukcja: kopiuj cross-task wymagania ze speca verbatim; cytuj wiążące artykuły constitution jako referencję (`Per Artykuł N`), nie treść.
2. **Produces/Consumes** — rozszerzyć format zadania (single-file Section 2 Task + orchestrated phase Task) o dwa pola z dokładnymi sygnaturami. Dodać regułę agregacji do sekcji orchestrated: phase `Context Contract → Provides` = union `Produces` przekraczających granicę fazy; nie powtarzaj within-phase. Doprecyzować: single-file = task↔task bez rollupu.
3. **No Placeholders** — dodać sekcję listy wzorców = plan failure obok Task Guidelines; skonsolidować z istniejącym "Bad" example (jeden kanon).
4. **Self-Review** — dodać sekcję pre-gate (autor): spec coverage / placeholder scan / type consistency (Produces↔Consumes). Umieścić PRZED sekcją Review Gate.
5. **Wzmocnienie "kompletny kod"** — proza: `Example` musi zawierać realny kod/sygnatury (link do No-Placeholders). BEZ zmiany szkieletu Requirements/Tests/Example. Marker Test-first bez zmian.
6. **NIE dotykać:** grep-AC / AC-traceability / Mode single-file|orchestrated / review gate flow / epic subfolder handling / Test-first marker / implementation-context.md budget.

## Pliki do zmodyfikowania / utworzenia
- `skills/generate-tasks/SKILL.md` — główna edycja (5 graftów).
- `agents/review-tasks.md` — drobny touch (nie przepisanie): dodać kryteria (a) Global Constraints obecne i spec-derived, (b) Produces↔Consumes type-consistency, (c) No-Placeholders scan. Format zadania rozszerzony, nie zmieniony → rubryka rozszerzona, nie przebudowana.
- `docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md` — ADR (szkielet + 3 rekoncyliacje). [utworzony]
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md` — mapa faz: link ADR + status Zaplanowana.
- `VENDORED.md` — odnotować: writing-plans = dawca sekcji (nie vendorowany), grafty do generate-tasks.

## Edge cases i ryzyka
- **Produces/Consumes vs Context Contract** — reguła anty-dup wymaga osądu plannera; self-review type-consistency + kryterium review-tasks łapią rozjazd.
- **Global Constraints vs constitution** — ryzyko skopiowania pół-constitution do GC → instrukcja twarda: GC = spec-derived, constitution TYLKO przez cytat-referencję (Artykuł N).
- **single-file bez faz** — Produces/Consumes działa task↔task; brak rollupu (nie ma Context Contract). Doprecyzować w SKILL, żeby nie szukać phase Provides w single-file.
- **No-Placeholders vs istniejący "Bad" example** — skonsolidować w jeden kanon, nie dublować.
- **Rozdęcie SKILL.md** (624 linie + 5 graftów) → mitygacja rewrite-to-unify: No-Placeholders zastępuje rozproszone uwagi "complete code"; grafty konsolidują, nie tylko dopisują.
- **Grep-AC × Produces** — sygnatury w Produces nie kolidują z tokenami `AC-N` w nazwach testów (osobne pola). Potwierdzić przy edycji.

## Acceptance Criteria
> Generowane przez qa-enrichment po zaplanowaniu fazy. Nie wypełniaj ręcznie.

## Pytania otwarte
- ~~Blok Interfaces vs Context Contract Requires/Provides — zunifikować czy współistnieją?~~ **Rozstrzygnięte [P2→A]:** współistnieją na dwóch poziomach — task `Produces`/`Consumes` + phase `Provides` jako rollup, reguła anty-dup (nie powtarzaj within-phase).
- ~~Global Constraints vs constitution.md — jedna sekcja czy dwie?~~ **Rozstrzygnięte [P3→A]:** dwie sekcje, GC (spec-derived) cytuje wiążące artykuły constitution.

## Notatki z dyskusji
- **P1→A rozstrzygnięty podziałem modeli** (2026-07-13): Opus planuje / Sonnet implementuje → implement zostaje autonomicznym inżynierem, nie transkryptorem. B (5-step template) odrzucony: sprzęga z Fazą 3, marnuje split, front-loaduje niezweryfikowany kod z modelu, który nie testuje.
- P2→A, P3→A: wariant "zasada obry wszczepiona w szkielet, zero duplikacji" — spójny z rewrite-to-unify (ADR Fazy 1).
- Severity ([BLOCKER]/[WARN] ↔ Critical/Important/Minor) → Faza 3.
- Metoda: rewrite-to-unify, szkielet = generate-tasks (gęstość domeny, jak Faza 1).
