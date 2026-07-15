# Faza 1: feature-discuss ← brainstorming  (epic: fuzja mechaniki obry)

## Kontekst nadrzędny
> ZACZNIJ od przeczytania `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`.
- Epic: `planning-main.md`
- Zależności od innych faz: brak edycyjnych (różne pliki); pipeline'owo dostarcza spec dla Fazy 2.
- ADR wspólny epica: `./docs/adr/2026-07-13-rewrite-to-unify-fuzja-obry.md` (metoda: rewrite-to-unify, baza per fuzja z analizy).
- ADR lokalny fazy: `./docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md` (szkielet + dwie rekoncyliacje).

## Status
Draft — 2026-07-13

## Problem
`feature-discuss` (583 linie) ma gęstą, unikalną warstwę domenową Absolut Systems (Tryb A/B/C, rozdział CO/JAK, Faza 0 parafraza, tryb epica z main+stuby, ADR, QA-enrichment, gates `[BLOCKER]`/`[WARN]` + review-plan) — ale słabszą, rozproszoną mechanikę bramkowania i prezentacji designu. `brainstorming` obry (160 linii) to przeciwnie: czysta, przetestowana-przez-community mechanika (HARD-GATE, prezentacja sekcjami z akceptacją per sekcja, dekompozycja przed pytaniami, spec self-review, visual companion just-in-time) bez warstwy domenowej.

Cel Fazy 1: wszczepić dojrzałą mechanikę `brainstorming` do `feature-discuss` metodą rewrite-to-unify, **zachowując w całości warstwę domenową** i **nie duplikując** istniejących mechanizmów. Dodatkowo: podpiąć visual companion, który jest już w repo (`companion-scripts/` + `visual-companion.md`) ale którego SKILL.md w ogóle nie odwołuje (martwy kod — `grep companion skills/feature-discuss/SKILL.md` = 0 trafień).

> **Intencja (dla review-tasks Intent Fidelity):** po fuzji feature-discuss ma egzekwować akceptację designu przed jakąkolwiek implementacją (HARD-GATE), prezentować design przyswajalnymi sekcjami z akceptacją per sekcja, flagować zbyt-duże projekty ZANIM zada pytania szczegółowe, robić self-review specu przed bramką QA, i oferować wizualny companion just-in-time — wszystko bez utraty Trybu A/B/C, ADR, epica, QA-enrichment i gate'ów. Fuzja mechaniki, nie porzucenie warstwy procesowej.

## Użytkownicy
Deweloperzy Absolut Systems prowadzący `feature-discuss` na Claude Code / Codex / Pi (dev interaktywny + nocne runy headless). Pośrednio: dalsze etapy pipeline'u (generate-tasks konsumuje spec o wyższej jakości — mniej placeholderów, jaśniejszy scope).

## Oczekiwane zachowanie
1. **HARD-GATE:** feature-discuss nie inicjuje żadnej implementacji (kod, scaffolding, wywołanie skilla implementacyjnego) zanim design nie zostanie **zaakceptowany** przez użytkownika. Anty-wzorzec "to zbyt proste" jest jawnie zaadresowany: prostota NIE zwalnia z akceptacji.
2. **Micro-change współistnieje z gate:** one-liner nadal idzie szybką ścieżką (opis CO+GDZIE → implementuj bez planning-doca), ale dopiero **po** akceptacji użytkownika. Micro-change = lekka ścieżka *do zatwierdzonego designu*, nie obejście gate.
3. **Prezentacja sekcjami:** po rekomendacji podejścia (Faza 3) design prezentowany jest sekcjami (architektura / komponenty / data flow / obsługa błędów / testy), długość każdej sekcji skalowana do złożoności, z pytaniem o akceptację po każdej sekcji.
4. **Dekompozycja przed pytaniami:** na wejściu Fazy 1 działa wczesny scope-check — gdy request opisuje wiele niezależnych podsystemów, feature-discuss flaguje to OD RAZU i przechodzi do istniejącej detekcji/splitu epica, zamiast marnować tury pytań na projekt do rozbicia.
5. **Spec self-review:** po zapisaniu planning/phase-doca, przed QA-enrichment, feature-discuss robi jednoprzebiegowy self-review (placeholdery/TODO, wewnętrzna sprzeczność, scope-fit, dwuznaczność) i naprawia inline.
6. **Visual companion:** oferta just-in-time (nie z góry, własna wiadomość), decyzja per-pytanie (browser dla treści wizualnej, terminal dla konceptualnej), graceful fallback brak-Node → terminal.

## Wybrane rozwiązanie
**Szkielet = `feature-discuss`; wszczepiamy mechanikę `brainstorming` jako grafty w istniejące fazy.** (Rewrite-to-unify z bazą feature-discuss — odwrotnie niż domyślna hipoteza epica, bo tu warstwa domenowa jest gęstsza i to ona ma więcej do stracenia.)

Mapa wszczepień:

| Mechanika obry | Stan w feature-discuss | Akcja | Gdzie |
|---|---|---|---|
| HARD-GATE + anty-wzorzec "too simple" | miękkie "NIE PISZ KODU" + micro-change fast-path, brak jawnego gate | **graft jawnego bloku**, zrekoncyliowany z micro-change (gate = akceptacja, nie doc) | nowy blok po nagłówku roli + zasada w Fazie 5 |
| Prezentacja sekcjami, akceptacja per sekcja, skalowanie długości | brak — Faza 3 daje jedną rekomendację naraz | **graft** | Faza 3 |
| Dekompozycja PRZED pytaniami | epic-detection istnieje, ale w Fazie 3 (PO pytaniach) | **graft wczesnego scope-checku** feedującego istniejącą maszynerię epica | wejście Fazy 1 |
| Spec self-review | brak zupełnie | **graft nowej fazy** | nowa Faza 5A (przed 5B QA) |
| Visual companion | pliki w repo, SKILL.md ich nie odwołuje (martwy kod) | **podpięcie** jako **cross-cutting sekcja** (jak HARD-GATE — samodzielny blok) + rozszerzenie `allowed-tools` | samodzielna sekcja "Visual Companion", odwoływana z faz pytających (1/3/4); + frontmatter |

### Uzasadnienie
- **Szkielet feature-discuss:** 583 linie unikalnej warstwy domenowej vs 160 linii czystej mechaniki obry. Przy odwrotnym wyborze (szkielet brainstorming) trzeba by odtworzyć Tryb A/B/C, epic main+stuby, ADR, gates — cały ciężar. Wszczepienie 4 mechanizmów + companion w gotowy szkielet jest tańsze i mniej ryzykowne.
- **Rekoncyliacja gate↔micro-change (ADR):** HARD-GATE semantycznie znaczy "brak implementacji przed **akceptacją**", nie "przed **docem**". To pozwala micro-change fast-path przeżyć jako lekka ścieżka pod tym samym gate. Anty-wzorzec "too simple" celuje w pomijanie akceptacji, nie w pomijanie ciężkiego doca — zgodne z intencją obry ("simple projects = najwięcej nieprzemyślanych założeń").
- **Rekoncyliacja dekompozycja↔epic (ADR):** obra dostarcza *timing* (flaguj przed pytaniami), feature-discuss dostarcza *machinery* (main+stuby+Tryb B). Rozszerzenie, nie zastąpienie — zero duplikacji mechanizmu splitu, zysk = wcześniejsze flagowanie.
- **Companion to podpięcie, nie budowa:** assety już są w repo z Fazy 1 migracji; brak tylko odwołania w SKILL.md.

### Rozważane alternatywy
- **Szkielet brainstorming + wszczepienie warstwy domenowej** — odrzucone: odtwarzanie 583 linii warstwy domenowej w 160-liniowym szkielecie to większy nakład i większe ryzyko regresji niż odwrotny kierunek.
- **HARD-GATE bezwzględny (wywalić micro-change)** — odrzucone: ciężar proceduralny na trywialnych zmianach, który feature-discuss świadomie usunął; sprzeczne z zasadą "MNIEJ = WIĘCEJ".
- **Dekompozycja obry zastępuje epic** — odrzucone: obra nie zna main-doca/Trybu B, utrata warstwy domenowej splitu.
- **Pominąć dekompozycję obry** — odrzucone: traci jedyną realną przewagę obry tutaj (wczesne flagowanie przed rundą pytań).

## Plan implementacji
> Edycja jednego pliku źródłowego: `skills/feature-discuss/SKILL.md` (host-agnostyczny, serwuje wszystkie harnessy). Plus odwołanie do istniejącego `visual-companion.md`. Metoda: rewrite-to-unify (nowa zunifikowana treść, nie append).

1. **Wczesny scope-check (dekompozycja) — wejście Fazy 1.** Dodaj na początku Fazy 1 (po Fazie 0 parafrazie, przed pierwszym pytaniem szczegółowym) akapit: gdy request opisuje wiele niezależnych podsystemów, NIE drąż szczegółów — flaguj od razu i skacz do detekcji epica (Faza 3) / splitu. Jedno-dwa zdania triggera + wskaźnik do istniejącej maszynerii epica. Nie duplikuj mechanizmu splitu.
2. **HARD-GATE — nowy blok + rekoncyliacja.** Po nagłówku roli (przed Routerem trybu) dodaj jawny blok HARD-GATE (żaden kod/scaffolding/skill implementacyjny przed zaakceptowanym designem, EVERY project) + akapit anty-wzorca "To zbyt proste by projektować". W Fazie 5 (Micro-change) dopisz jedno zdanie rekoncyliacji: micro-change wymaga akceptacji CO+GDZIE zanim implementacja ruszy — to spełnia gate, nie obchodzi go. Zaktualizuj Zasadę zachowania #1.
3. **Prezentacja sekcjami — Faza 3.** Przepisz koniec Fazy 3: po rekomendacji podejścia prezentuj design sekcjami (architektura / komponenty / data flow / obsługa błędów / testy), skaluj długość sekcji do złożoności (kilka zdań ↔ 200-300 słów dla niuansowych), pytaj o akceptację po każdej sekcji, wracaj i klaruj gdy sekcja nie gra. Spójne z "jedno pytanie na turę".
4. **Spec self-review — nowa Faza 5A.** Wstaw między Fazę 5 (zapis) a 5B (QA-enrichment) nową Fazę 5A: jednoprzebiegowy skan zapisanego doca (placeholdery/TODO, wewnętrzna sprzeczność, scope-fit, dwuznaczność → wybierz jedną interpretację i uczyń ją jawną), fix inline, bez re-review. Zaznacz: nie emituje severity (`[BLOCKER]`/`[WARN]`) — to zostaje bramce review-plan. Dotyczy standardowego feature'a i phase-doca (Tryb B); NIE micro-change/main/stubów.
5. **Visual companion — odwołanie + integracja (cross-cutting).** Dodaj **samodzielną sekcję "Visual Companion"** (analogicznie do bloku HARD-GATE — mechanizm przekrojowy, nie przyklejony do jednej fazy): oferta just-in-time (własna wiadomość, dopiero gdy pytanie zyska na pokazaniu), decyzja per-pytanie (browser dla wizualnej treści, terminal dla konceptualnej), graceful fallback brak-Node → terminal, odwołanie do `skills/feature-discuss/visual-companion.md` po szczegóły. Z faz zadających pytania użytkownikowi (Faza 1 Zrozumienie, Faza 3 Propozycja, Faza 4 Doprecyzowanie) dodaj jednozdaniowy wskaźnik do tej sekcji — NIE do Fazy 2 (Analiza kodu, brak pytań user-facing). Zaadaptuj język donora (EN) do konwencji PL user-facing.
5a. **Rozszerzenie `allowed-tools` pod companion (frontmatter).** Companion faktycznie działa tylko przy poszerzonym grancie narzędzi — obecny allowlist go nie pokrywa: (a) **Bash** — dodaj grant wykonania `companion-scripts/start-server.sh` i `stop-server.sh` (obecnie tylko `find/wc/cat/head/tail/tree/mkdir`); (b) **Write** — dodaj wzorzec na katalog ekranów companion `**/.superpowers/brainstorm/**/*.html` (obecnie tylko `absolutpowers/feature/**` + `docs/adr/**`). `Read` jest bez restrykcji → `server-info`/`events` OK. To rozszerzenie jest **wąskie i celowe** — nie luzuj pozostałych grantów. Dopisz przypomnienie o `.superpowers/` w `.gitignore` w treści sekcji companion.
6. **Dwujęzyczność + spójność.** Cała nowa treść: prompty user-facing PL, terminy techniczne EN — zgodnie z CLAUDE.md. Nie wklejaj surowego EN z donora; przełóż/zaadaptuj.
7. **Walidacja frontmatter + brak regresji formatu.** Po edycji: frontmatter syntaktycznie poprawny; `allowed-tools` rozszerzony **wyłącznie** o granty companion z kroku 5a (Bash companion-scripts + Write `.superpowers/brainstorm/**`), reszta grantów, `name`, `description`, `argument-hint` nietknięte; formaty doców (standard/main/phase) nietknięte; Router A/B/C zachowany.

## Pliki do zmodyfikowania / utworzenia
- `skills/feature-discuss/SKILL.md` — **modyfikacja** (rewrite-to-unify: 5 wszczepień wg planu + rozszerzenie `allowed-tools` w frontmatter o granty companion — krok 5a). Jedyny plik z realną zmianą logiki.
- `skills/feature-discuss/visual-companion.md` — **bez zmian treści**, tylko staje się odwoływany z SKILL.md (weryfikacja że ścieżka/nazwa zgadza się z donorem; ewentualna adaptacja PL nagłówka).
- `docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md` — **utworzenie** (szkielet=feature-discuss + rekoncyliacja gate↔micro-change + rekoncyliacja dekompozycja↔epic).
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md` — **aktualizacja statusu** Fazy 1 (Do zaplanowania → Zaplanowana) po PASS review-plan.
- (Poza scope edycji, do świadomości) `README.md` / `docs/` — wzmianka o wchłonięciu mechaniki: aktualizacja w Fazie implementacyjnej, nie tutaj.

## Edge cases i ryzyka
- **Kolizja tryb-epica-obry ↔ tryb-epica-feature-discuss.** Rozstrzygnięte: rozszerzenie (early scope-check → istniejąca maszyneria). Ryzyko rezydualne: podwójne flagowanie epica (raz na wejściu Fazy 1, raz w Fazie 3). Mitygacja: scope-check ma *kierować* do Fazy 3, nie *duplikować* jej komunikatu.
- **HARD-GATE vs micro-change fast-path.** Rozstrzygnięte: gate = akceptacja. Ryzyko rezydualne: użytkownik odczyta gate jako zakaz micro-change. Mitygacja: jawne zdanie rekoncyliacji w Fazie 5 + w bloku gate.
- **Companion bez Node (Codex/Pi, nocne runy headless).** Graceful fallback do terminala. Ryzyko: `start-server.sh` zakłada środowisko dev. Mitygacja: oferta companion NIGDY nie blokuje — brak Node = cicho kontynuuj w terminalu. (Przekrojowe pytanie maina — tu tylko fallback, pełne wsparcie Codex/Pi poza scope.)
- **Companion na nieinteraktywnym runie (headless).** Brak człowieka do kliknięcia w tab → companion nie może być gate'em. Mitygacja: oferta jest opcjonalna z definicji; brak odpowiedzi = terminal.
- **Rozdęcie SKILL.md.** 583 linie + 5 wszczepień → ryzyko przekroczenia rozsądnej długości/przepalenia kontekstu. Mitygacja: rewrite-to-unify (nie append) — konsoliduj przy okazji miękkie "NIE PISZ KODU" w jawny gate zamiast dokładać; companion szczegóły zostają w osobnym `visual-companion.md`.
- **Severity taksonomia `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor obry.** Spec self-review NIE emituje severity → Faza 1 nie wymusza tej decyzji. Świadomie **punktowane do Fazy 2/3** (tam gate emituje severity). Odnotowane, nie rozwiązywane tutaj.
- **Regresja formatów doców / Routera.** Rewrite dotyka faz procesu, nie formatów. Mitygacja: krok 7 walidacji — formaty i Router nietknięte.
- **Rozszerzenie `allowed-tools` = poszerzenie powierzchni uprawnień.** Companion wymaga grantu Bash-exec (`companion-scripts/*`) i Write do `.superpowers/brainstorm/**`. Ryzyko: zbyt szeroki wzorzec (np. `Bash(*)`) rozluźnia skill w trybie dyskusji. Mitygacja: granty maksymalnie wąskie (dokładne ścieżki skryptów + katalog ekranów), krok 7 weryfikuje że reszta grantów nietknięta. `.superpowers/` do `.gitignore` (przypomnienie w treści sekcji companion).
- **Walidacja jakości fuzji (Faza 5 planu migracji).** Zmodyfikowany skill przechodzi test metodą `writing-skills`: baseline RED (bez mechaniki) → GREEN (z mechaniką). Poza scope tej sesji planistycznej, odnotowane jako brama akceptacji implementacji.

## Acceptance Criteria

> Generated by qa-enrichment agent. Do not edit manually — re-run enrichment if the plan changes significantly.

### Happy path
- AC-1: SKILL.md zawiera jawny blok HARD-GATE umieszczony po nagłówku roli, a przed Routerem trybu, stwierdzający wprost że żadna implementacja (kod, scaffolding, wywołanie skilla implementacyjnego) nie następuje przed zaakceptowanym przez użytkownika designem — dla KAŻDEGO projektu, niezależnie od jego rozmiaru.
- AC-2: Blok HARD-GATE (lub sąsiadujący akapit) jawnie adresuje anty-wzorzec "to zbyt proste, by projektować" — stwierdza wprost, że prostota projektu nie zwalnia z wymogu akceptacji.
- AC-3: W Fazie 3, po rekomendacji podejścia, design jest prezentowany rozbity na sekcje (co najmniej: architektura, komponenty, data flow, obsługa błędów, testy), z osobnym pytaniem o akceptację po każdej sekcji — a nie jedną łączną rekomendacją naraz.
- AC-4: Faza 3 jawnie instruuje skalowanie długości każdej sekcji do złożoności tematu (krótka dla prostych elementów, rozwinięta dla niuansowych) — nie jednolita długość dla wszystkich sekcji.
- AC-5: Na wejściu Fazy 1, przed pierwszym pytaniem szczegółowym, działa scope-check: gdy request opisuje wiele niezależnych podsystemów, feature-discuss zatrzymuje drążenie pytań i kieruje do istniejącej detekcji/splitu epica (Faza 3) zamiast kontynuować rundę pytań.
- AC-6: Nowa Faza 5A jest wstawiona między zapisem doca (Faza 5) a QA-enrichment (Faza 5B) i wykonuje jednoprzebiegowy skan zapisanego doca pod kątem placeholderów/TODO, wewnętrznej sprzeczności, dopasowania zakresu i dwuznaczności, naprawiając problemy inline bez ponownego pełnego review.
- AC-7: SKILL.md jawnie odwołuje `visual-companion.md` i opisuje ofertę just-in-time (własna wiadomość, nie z góry), decyzję per-pytanie między trybem przeglądarkowym a terminalowym, oraz zaadaptowaną (nie surowo wklejoną z EN) treść user-facing po polsku.

### Edge cases
- AC-8: Komunikat wczesnego scope-checku (wejście Fazy 1) jest odrębny i krótszy niż komunikat detekcji epica w Fazie 3 — nie powiela jego treści, tylko kieruje do niego, tak by epic nie był flagowany dwukrotnie tym samym komunikatem w jednej sesji.
- AC-9: Zdanie rekoncyliacji "micro-change spełnia gate, nie obchodzi go" pojawia się w co najmniej dwóch miejscach SKILL.md — w bloku HARD-GATE oraz w opisie Fazy 5 (micro-change) — tak by kolejność czytania nie prowadziła do błędnej interpretacji gate jako zakazu micro-change.
- AC-10: Gdy środowisko nie ma dostępnego Node (Codex/Pi, run nocny headless), feature-discuss kontynuuje wyłącznie w trybie terminalowym bez próby uruchomienia companion i bez błędu przerywającego sesję.
- AC-11: Nowa Faza 5A (self-review) uruchamia się wyłącznie dla standardowego feature'a oraz phase doca w Trybie B — SKILL.md jawnie wyklucza jej uruchomienie dla micro-change, `planning-main.md` oraz stubów faz epica.
- AC-12: Po rewrite-to-unify frontmatter SKILL.md pozostaje syntaktycznie poprawny; jedyną dozwoloną zmianą znaczącą jest rozszerzenie `allowed-tools` o wąskie granty companion (Bash `companion-scripts/*` + Write `**/.superpowers/brainstorm/**/*.html`) — `name`, `description`, `argument-hint` oraz pozostałe granty niezmienione. Router trybu A/B/C oraz formaty doców (standard/main/phase) pozostają nienaruszone i rozpoznawalne pod tymi samymi nagłówkami co przed zmianą.

### Security
- AC-13: Visual companion nie wykonuje żadnego kodu pochodzącego z projektu ani z requestu użytkownika — serwuje wyłącznie statyczny render (diagram/HTML), niezależnie od treści pytania w dyskusji.
- AC-14: Niedostępność lub błąd companion (brak Node, zablokowany port, ograniczenia sandboxa) nigdy nie jest interpretowany jako domyślna akceptacja designu — HARD-GATE nadal wymaga jawnej, wprost wyrażonej akceptacji użytkownika.
- AC-15: W trybie nieinteraktywnym (headless, brak człowieka do odpowiedzi) sesja nie zawiesza się w oczekiwaniu na decyzję dot. companion — brak odpowiedzi jest traktowany jako rezygnacja z companion, a proces kontynuuje bez niego.

## Pytania otwarte
- Severity taksonomia `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor obry — **punktowane do Fazy 2/3** (spec self-review nie emituje severity). Decyzja przy fazie, która pierwsza dotknie gate emitującego severity.
- Pełne wsparcie companion na Codex/Pi (Node dependency) — poza scope Fazy 1; tu tylko graceful fallback do terminala. Przekrojowe pytanie maina.

## Notatki z dyskusji
- Companion wchłaniany tu (nie osobna faza) — decyzja z sesji epica.
- **Szkielet = feature-discuss** (analiza: 583 vs 160 linii; więcej warstwy domenowej do zachowania → odwrotnie niż domyślna hipoteza epica). Potwierdzone.
- **Fork 1 (dekompozycja↔epic): ROZSZERZA.** Obra = timing (flaguj przed pytaniami), feature-discuss = machinery (main+stuby+Tryb B). Zero duplikacji.
- **Fork 2 (gate↔micro-change): gate rządzi AKCEPTACJĄ, nie ciężarem doca.** Micro-change przeżywa jako lekka ścieżka pod gate; anty-wzorzec "too simple" celuje w pomijanie akceptacji.
- Visual companion = martwy kod w repo (SKILL.md nie odwołuje) → Faza 1 głównie podpina, nie buduje.
- Dwie decyzje-forki zapisane jako ADR lokalny fazy.
- review-plan (iter. 1) REJECTED → poprawki: (BLOCKER) companion wymaga rozszerzenia `allowed-tools` (Bash companion-scripts + Write `.superpowers/brainstorm/**`) — sprzeczność z "frontmatter nienaruszony" usunięta (krok 5a + 7 + AC-12); (WARN) companion przemodelowany na cross-cutting sekcję odwoływaną z faz pytających (1/3/4), nie przyklejony do Fazy 2/3.
