# Plan migracji hybrydowej: Superpowers (obra) + absolutpowers

**Data:** 2026-07-13
**Analizowana wersja Superpowers:** 6.1.1 (MIT, obra/superpowers, stan repo z lipca 2026)
**Decyzja do podjęcia:** czy porzucić absolutpowers na rzecz Superpowers, czy zbudować hybrydę

---

## Część 1: Porównanie na podstawie źródeł

### 1.1. Architektura multi-harness

**Superpowers:** jeden katalog `skills/` (14 skilli, 3322 linie SKILL.md — zweryfikowane w źródle v6.1.1) plus cienkie manifesty per host: `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `.kimi-plugin/`, `.pi/`, `.agents/`, `gemini-extension.json`. Skille są host-agnostyczne; różnice per platforma trafiają do plików referencyjnych (`skills/using-superpowers/references/codex-tools.md` itd.), które dispatcher każe czytać warunkowo.

**Uściślenie (weryfikacja źródła):** obra **ma** skrypt `scripts/sync-to-codex-plugin.sh`, ale to **nie** jest wewnętrzny mirror-sync. `.codex-plugin/` zawiera wyłącznie `plugin.json` (zero kopii skilli); skrypt jednokierunkowo **publikuje** jedno drzewo `skills/` do zewnętrznego repo dystrybucyjnego (`prime-radiant-inc/openai-codex-plugins`) na marketplace Codex. Rdzeń przewagi trzyma się: obra ma **jedno wewnętrzne drzewo `skills/`**, absolutpowers ma dwa lustrzane.

**absolutpowers:** lustrzane drzewa `claude/` i `codex/` synchronizowane skryptem (którego duplikat był jednym z bugów z audytu v1).

**Werdykt:** architektura Superpowers jest strukturalnie lepsza — eliminuje całą klasę bugów synchronizacji. To wzorzec do adopcji niezależnie od decyzji o samych skillach. Koszt utrzymania mirrorów w absolutpowers to czysty dług techniczny wobec rozwiązania, które już istnieje.

### 1.2. Dispatcher: `using-superpowers` (brak odpowiednika w absolutpowers)

Hook `SessionStart` (matcher `startup|clear|compact` — czyli aktywny także po kompakcji kontekstu, co jest kluczowe dla długich sesji) wstrzykuje meta-skill wymuszający sprawdzenie skilli **przed jakąkolwiek odpowiedzią**, włącznie z pytaniami doprecyzowującymi. Zawiera tabelę "Red Flags" — 12 skatalogowanych racjonalizacji, którymi model wykręca się od użycia skilla ("to proste pytanie", "najpierw zbiorę kontekst", "pamiętam ten skill"), każda z kontrargumentem. Ma też regułę priorytetów: skille procesowe (brainstorming, systematic-debugging) przed implementacyjnymi, oraz `<SUBAGENT-STOP>` — subagenci wykonawczy ignorują dispatcher.

**Werdykt:** dispatcher rozwiązuje problem **automatycznego** triggerowania skilli — model ma sam wybrać skill na podstawie opisu, a dispatcher pilnuje, żeby tego wyboru nie zracjonalizował. Pipeline absolutpowers jest sterowany jawnie (`@feature-discuss` → `@generate-tasks` → `@implement` → `@review`/`@triada-review`), więc dla głównego przepływu dispatcher jest zbędny i tylko kosztowałby tokeny przy każdej wiadomości. Wartościowe są natomiast dwa jego elementy składowe: (a) **mechanizm hooka** z matcherem `startup|clear|compact` — re-injekcja instrukcji po kompakcji kontekstu, chroniąca długie sesje `@implement` i nocne runy przed dryfem do zachowań domyślnych; (b) idea **auto-triggeru dla skilli strażniczych** (`systematic-debugging`, `verification-before-completion`), których momentu użycia nie da się przewidzieć i wywołać jawnie. Adopcja: slim hook z własną treścią, bez pełnego dispatchera.

### 1.3. `brainstorming` vs `feature-discuss`

Wspólne: pytania doprecyzowujące, propozycje podejść z trade-offami, zapis dokumentu projektowego, gate zatwierdzenia przez użytkownika.

Przewagi `brainstorming`:
- `<HARD-GATE>` — zakaz jakiejkolwiek implementacji przed zatwierdzonym designem, z explicite zaadresowanym anty-wzorcem "to zbyt proste, żeby potrzebowało designu";
- jedna kwestia na wiadomość, preferencja pytań zamkniętych;
- prezentacja designu **sekcjami** z zatwierdzeniem po każdej sekcji (skalowanie długości sekcji do złożoności);
- wykrywanie projektów zbyt dużych na jeden spec i dekompozycja na sub-projekty **przed** zadawaniem pytań szczegółowych;
- spec self-review: skan placeholderów, spójność wewnętrzna, scope check, test dwuznaczności;
- twardo zdefiniowany stan terminalny: jedynym następnym skillem jest `writing-plans`.

Przewagi `feature-discuss`:
- spójność z ADR-ami (Superpowers w ogóle nie zna pojęcia ADR);
- tryb rewizji istniejącego designu;
- QA enrichment;
- Tryb C handoff;
- integracja z `project-memory.md` w dalszym pipeline.

**Werdykt:** funkcjonalnie się przecinają, ale nie pokrywają. `brainstorming` ma lepszą mechanikę konwersacji i gate'y; `feature-discuss` ma wiedzę domenową (ADR, rewizje, QA). Kandydat do **fuzji**: przejąć mechanikę obry (HARD-GATE, sekcyjna prezentacja, dekompozycja, self-review) do feature-discuss, zamiast utrzymywać dwa konkurujące skille discovery.

### 1.4. `writing-plans` vs `generate-tasks`

Przewagi `writing-plans`:
- założenie "inżynier zero-context o wątpliwym guście" — każdy krok zawiera kompletny kod, dokładne ścieżki plików (z zakresami linii przy modyfikacjach), dokładne komendy z oczekiwanym outputem;
- kroki 2–5 min z TDD wpisanym w strukturę zadania (krok 1 = failing test, krok 2 = weryfikacja że failuje, itd.) — czyli test-first jest egzekwowany **strukturą planu**, dokładnie w duchu Twojej decyzji o przeniesieniu TDD upstream;
- blok **Interfaces** (Consumes/Produces z dokładnymi sygnaturami) — implementer widzi tylko swoje zadanie, ten blok jest jedynym kanałem wiedzy o sąsiadach; to eleganckie rozwiązanie problemu spójności typów między zadaniami;
- sekcja **Global Constraints** w nagłówku planu — wymagania projektowe kopiowane verbatim ze speca, implicite obowiązujące każde zadanie;
- reguły "No Placeholders" z listą wzorców uznawanych za plan failure;
- self-review: pokrycie speca, skan placeholderów, spójność typów między zadaniami.

Przewagi `generate-tasks`:
- integracja `project-memory.md`;
- grep-owa weryfikacja spełnienia AC — Superpowers nie ma żadnego mechanicznego sprawdzenia, że kryteria akceptacji z designu mają odzwierciedlenie w kodzie/testach; ich odpowiednikiem jest tylko miękki "spec coverage skim" w self-review;
- upstream test-first decisions (u obry TDD w planie jest szablonowy; u Ciebie decyzja test-first jest podejmowana świadomie per zadanie).

**Werdykt:** znów fuzja, nie wybór. Struktura zadania z `writing-plans` (Interfaces, Global Constraints, No Placeholders, kompletny kod w krokach) jest dojrzalsza i warta przejęcia; grep-AC i project-memory to Twoja unikalna warstwa weryfikacji, której obra nie ma.

### 1.5. `subagent-driven-development` (brak pełnego odpowiednika)

Świeży subagent per zadanie + dwuetapowy review per zadanie (zgodność ze spec, potem jakość) + szeroki review całego brancha na końcu. Najciekawsze elementy:
- **protokół statusów implementera:** DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED, z zaleceniami obsługi każdego (m.in. re-dispatch na mocniejszym modelu, dekompozycja zadania, eskalacja do człowieka) — to dojrzalsza wersja Twojej konwencji BLOCKED.md/ANSWERS.md;
- **dobór modelu per rola:** transkrypcja kodu z planu → najtańszy model; integracja → standardowy; review finalny → najmocniejszy; z ostrzeżeniem, że liczba tur bije cenę tokena (najtańsze modele biorą 2–3× więcej tur na pracy wieloetapowej) — bezpośrednio przekłada się na koszt nocnych runów;
- **continuous execution:** zakaz "czy mam kontynuować?" między zadaniami — stop tylko przy BLOCKED, realnej dwuznaczności albo końcu planu;
- **pre-flight plan review:** jednorazowy skan planu pod kątem sprzeczności wewnętrznych i konfliktów z rubryką review, zgłaszany jako jedno zbiorcze pytanie przed startem;
- skrypt `review-package BASE HEAD` generujący paczkę diffa dla reviewera (z pułapką `HEAD~1` gubiącą commity wieloetapowych zadań — jawnie zaadresowaną).

**Werdykt:** adopcja w całości. To brakująca warstwa wykonawcza absolutpowers i naturalny partner dla gnhf — z tym że subagent-driven działa **wewnątrz** sesji, a gnhf orkiestruje **serią** wywołań `claude -p`; to komplementarne poziomy (gnhf = pętla zewnętrzna, subagenty = wykonanie pojedynczego planu wewnątrz jednego wywołania).

### 1.6. TDD, weryfikacja, review — porównanie filozofii gate'ów

`test-driven-development`: Iron Law ("NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"), kod napisany przed testem podlega usunięciu i implementacji od zera. Egzekwowanie w runtime.

`verification-before-completion`: "Evidence before claims" — zakaz twierdzenia, że coś działa, bez świeżego uruchomienia komendy weryfikacyjnej w bieżącej wiadomości; tabela typowych fałszywych dowodów ("agent zgłosił sukces" ≠ "diff w VCS pokazuje zmiany").

`requesting-code-review` / `receiving-code-review`: severity Critical / Important / Minor; Critical blokuje natychmiast, Important przed przejściem dalej, Minor odnotowywane. Reviewer dostaje precyzyjnie skonstruowany kontekst, nigdy historię sesji.

**Zestawienie z absolutpowers:** Twoje `[BLOCKER]`/`[WARN]` + Re-review Protocol to funkcjonalny odpowiednik severity obry; Twój verify.sh + pre-commit to **infrastrukturalna** wersja `verification-before-completion` (twardsza — hook nie da się zracjonalizować, skill teoretycznie tak). Systemy są komplementarne: behawioralny skill łapie przypadki między commitami, hook łapie wszystko przy commicie.

### 1.7. Pozostałe skille

| Skill Superpowers | Odpowiednik w absolutpowers | Ocena |
|---|---|---|
| `using-git-worktrees` | brak | Adopcja. Detekcja istniejącej izolacji, preferencja narzędzi natywnych harnessa, gate zgody użytkownika, guard na submoduły. Kluczowe dla równoległych nocnych runów gnhf. |
| `finishing-a-development-branch` | `ship` | Nakładają się. Obra: weryfikacja testów → detekcja środowiska → menu 4 opcji (merge/PR/kontynuuj/porzuć) → sprzątanie worktree. Do konsolidacji — patrz Faza 3. |
| `systematic-debugging` | brak | Adopcja bez zmian. Wymusza root-cause przed fixem. |
| `dispatching-parallel-agents` | brak | Adopcja. Równoległy dispatch niezależnych zadań. |
| `writing-skills` | `try-learn-skill` | **Różne cele, oba warto mieć.** Obra: TDD dla skilli — scenariusz presji z subagentem jako test, baseline RED bez skilla, GREEN ze skillem, refactor domyka luki. Twój ledger (observe n=1, promote n≥2) to promocja przez częstość użycia, nie test poprawności. Komplementarne: ledger decyduje *co* zeskillować, writing-skills *jak* to zweryfikować. |
| `executing-plans` | tryb inline w implement | Fallback bez subagentów; drugorzędny. |

### 1.8. Czego Superpowers nie ma (Twoja przewaga)

Zebrane w jednym miejscu, bo to jest sedno decyzji: ADR-y i spójność z nimi w discovery; tryb rewizji designu; QA enrichment; `project-memory.md`; grep-owa weryfikacja AC; budżet `implementation-context.md`; harvest (archiwizacja); ledger try-learn; konwencja verify.sh dla repo bez systemu budowania; integracja z gnhf i pętlą headless. Nic z tego nie pojawi się w generycznym frameworku, bo to jest proces Absolut Systems, nie proces uniwersalny.

### 1.9. Ryzyka zależności i mitygacje

Superpowers jest produktem Prime Radiant: telemetria wersji przy visual companion (opt-out: `SUPERPOWERS_DISABLE_TELEMETRY`), oferta enterprise, kierunek rozwoju poza Twoją kontrolą. Mitygacje: licencja **MIT** pozwala na vendoring/fork w każdej chwili; pinowanie wersji pluginu i świadome, testowane aktualizacje zamiast auto-update; warstwa domenowa absolutpowers jako jedyne miejsce, gdzie żyje Twoja wiedzosć procesowa — wymiana fundamentu pozostaje wtedy technicznie możliwa.

---

## Część 2: Plan migracji hybrydowej

**Cel końcowy:** absolutpowers v5 jako **samodzielny** system bez zależności od pluginu Superpowers — wybrane skille obry zvendorowane (skopiowane, przycięte i dostosowane) do wspólnego drzewa `skills/` absolutpowers, obok warstwy domenowej (ADR, project-memory, grep-AC, QA, gnhf). Jedna struktura `skills/` z cienkimi integracjami per harness zamiast mirrorów. Licencja MIT pozwala na kopiowanie i modyfikację pod warunkiem zachowania noty licencyjnej (copyright (c) 2025 Jesse Vincent).

**Architektura wieloharnessowa (przejęta od obry):** jedno host-agnostyczne drzewo `skills/` + różnice per harness w `references/{harness}-tools.md` (czytane warunkowo) + cienka integracja per harness (`.claude-plugin/`, `.codex-plugin/`, `.pi/extensions/`) + `AGENTS.md`→`CLAUDE.md` symlink dla harnessów czytających AGENTS.md. Dodanie kolejnego harnessu = nowa integracja + opcjonalny reference file, **zero edycji skilli**. Wspierane od startu v5: **Claude Code, Codex, Pi** (Pi używany lokalnie). Korekta faktograficzna względem wcześniejszych założeń: Codex i Pi NIE mają zarejestrowanych definicji agentów (bramki review = Claude-only), ale MAJĄ dispatch subagentów (Codex: `multi_agent=true`→`spawn_agent`; Pi: opcjonalny `pi-subagents`) — więc wykonawczy wzorzec subagentów jest przenośny, degraduje gracefully, nie znika.

**Strategia vendoringu zamiast dependency — uzasadnienie:** pełna kontrola nad treścią skilli (cięcie sekcji nieużywanych harnessów, dostrajanie pod proces Absolut Systems), brak ryzyka konfliktu priorytetów dwóch pluginów, brak zależności runtime od marketplace'u (istotne dla nocnych runów gnhf), możliwość natychmiastowego patchowania bez czekania na upstream. Koszt: ręczne śledzenie zmian upstreamu (mitygacja niżej, Faza 1.5).

### Faza 0: pominięta — od razu wchłanianie skilli (decyzja 2026-07-13)

Porównawczy pilot (równoległy przebieg feature'a przez absolutpowers i goły Superpowers) **pominięty**. Uzasadnienie: weryfikacja źródła v6.1.1 już potwierdziła dojrzałość mechaniki obry (HARD-GATE, blok Interfaces, No-Placeholders, protokół 4 statusów, ledger recovery, file-handoff via task-brief — wszystko potwierdzone w kodzie, Część 1). Pilot mierzyłby **obra as-is** = sufit fundamentu, a nie produkt końcowy, którym jest fuzja (mechanika obry + Twoja warstwa domenowa). Porównanie komponentu do produktu ma niską wartość decyzyjną przy wysokim koszcie (instalacja pluginu, przebieg równoległy, subiektywna ocena). Zamiast tego przechodzimy od razu do Fazy 1 (vendoring), a walidacja jakości spada na Fazę 5 (testy metodą `writing-skills` RED/GREEN na zfuzjowanych skillach + 2 tyg logu odchyleń) — twardszy, obiektywny net niż pilot.

**Tani baseline zamiast pilota (opcjonalny, 15 min, bez instalacji obry):** przed fuzją feature-discuss uruchom obecny feature-discuss na jednym realnym feature'rze i zapisz wygenerowany spec. Po fuzji powtórz na tym samym wejściu i porównaj. To baseline dla ryzyka regresji discovery — nie wymaga instalacji Superpowers.

### Faza 1: Vendoring i architektura repo (1–2 dni)

1. **Sklonować obra/superpowers (świeży `git clone`) i przypiąć commit źródłowy.** Wersja v6.1.1 potwierdzona w `package.json`, ale **SHA trzeba odczytać z klona** — analizowany katalog `~/Downloads/superpowers-main` to download bez `.git`, więc podany wcześniej `d884ae0` jest nieweryfikowalny i traktuj go jako placeholder do zastąpienia realnym `git rev-parse HEAD` po sklonowaniu. Zapisany SHA to punkt odniesienia dla przyszłych diffów upstreamu.
2. **Skopiować do `skills/` absolutpowers wybrane skille** (lista w Fazie 2): każdy z prefiksem lub w podkatalogu `vendored/`, z zachowaną notą MIT. Utworzyć `VENDORED.md`: skąd, jaki SHA, jaka wersja, jakie lokalne modyfikacje (per skill, jedna linia na zmianę) — bez tego pliku przyszłe diffowanie upstreamu będzie zgadywaniem.
3. **Przyciąć na starcie:** usunąć sekcje harnessów, których nie używasz (Cursor, Kimi, Antigravity, Gemini). Zostawić Claude Code + Codex + **Pi** (Pi używany lokalnie — pełny harness, nie cięty; integracja `.pi/extensions/` + `references/pi-tools.md`). Każde cięcie odnotowane w `VENDORED.md`.
   - **Visual companion — ZACHOWAĆ (nie wycinać).** Weryfikacja źródła: companion to realna infra (`skills/brainstorming/visual-companion.md` 291 linii + `scripts/server.cjs` Node HTTP+WS, `helper.js`, `frame-template.html`, `start-server.sh`/`stop-server.sh`, auth per-session key). Renderuje mockupy/diagramy w przeglądarce, użytkownik klika wybór, selekcje wracają przez pliki eventów. Wartościowe dla dyskusji feature'ów z warstwą UI. Przenieść razem z fuzją brainstorming→feature-discuss (patrz Faza 2, poddrzewo dowiązane jawnie).
   - **Telemetria — zneutralizować, nie usuwać całego companiona.** Weryfikacja: telemetria = wyłącznie zdalne logo Prime Radiant (`SUPERPOWERS_BRAND_IMAGE_URL = https://primeradiant.com/brand/…png?v=WERSJA`) na ekranie powitalnym; żadnych danych projektu, promptu ani kliknięć. `server.cjs` ma już przełącznik `SUPERPOWERS_TELEMETRY_DISABLED` (env `SUPERPOWERS_DISABLE_TELEMETRY`/`DISABLE_TELEMETRY`). Przy vendoringu: albo hardcode `SUPERPOWERS_TELEMETRY_DISABLED = true`, albo usunąć stałą `SUPERPOWERS_BRAND_IMAGE_URL` i gałąź logo (~linie 106, 244-251). Odnotować w `VENDORED.md`.
   - **Zależność runtime:** companion wymaga Node.js w target-projekcie. Twoje target-projekty to głównie Java/Spring (preboot) — Node zwykle jest na maszynie dev, ale to twarda zależność do udokumentowania; bez Node companion się nie odpali (feature-discuss musi mieć graceful fallback do trybu terminalowego).
4. **Slim hook zamiast dispatchera:** zvendorować sam mechanizm `hooks/session-start` (matcher `startup|clear|compact` + `run-hook.cmd`), ale z własną, chudą treścią zamiast `using-superpowers`. Treść hooka (~10–15 linii): (a) przypomnienie łańcucha pipeline'u absolutpowers i tego, że skille wywołuje się jawnie przez `@`; (b) jeśli sesja jest w trakcie skilla (aktywna checklista/todo) — wróć do jego checklisty; (c) reguły auto-triggeru **wyłącznie** dla skilli strażniczych: "przy debugowaniu użyj `systematic-debugging`; przed twierdzeniem, że coś działa/przechodzi — `verification-before-completion`". Kluczowa jest gałąź `compact`: po kompakcji kontekstu jawne wywołanie `@implement` z początku sesji już nie chroni, a hook przywraca dyscyplinę — istotne zwłaszcza dla nocnych runów gnhf.
5. **Restrukturyzacja absolutpowers na wzór obry:** jedno drzewo `skills/` + cienkie integracje per harness `.claude-plugin/`, `.codex-plugin/`, `.pi/extensions/` + `AGENTS.md`→`CLAUDE.md` symlink. Usunięcie drzew lustrzanych i skryptu sync. Różnice per harness → pliki referencyjne czytane warunkowo (`references/codex-tools.md`, `references/pi-tools.md`).
6. To jest zmiana formatu → **semver major: absolutpowers 5.0.0** (zgodnie z precedensem 4.0.0 przy poprzedniej zmianie formatu).
7. Migracja historii: harvest istniejących artefaktów, aktualizacja instrukcji instalacji (poprzednio zepsutej — okazja do naprawy na czysto).

#### Faza 1.5: Proces śledzenia upstreamu (ustawiany raz, potem kwartalnie)

Raz na kwartał: `git fetch` w klonie obry, `git diff <pinowany-SHA>..<nowy-tag> -- skills/` ograniczony do zvendorowanych skilli. Przegląd diffa ręcznie (skille to markdown — diffy są czytelne), selektywne przeniesienie wartościowych zmian, aktualizacja SHA w `VENDORED.md`. Świadomie akceptowany dryf: nie każda zmiana upstreamu musi trafić do Ciebie — kryterium jest wartość dla Twojego procesu, nie parytet wersji.

### Faza 2: Mapa dyspozycji skilli (decyzje, 0,5 dnia)

| Skill absolutpowers | Decyzja | Uzasadnienie |
|---|---|---|
| `feature-discuss` | **Zachować + wchłonąć mechanikę `brainstorming` (w tym visual companion)** | HARD-GATE, prezentacja sekcjami, dekompozycja dużych projektów, spec self-review — do przejęcia. **Plus visual companion** (`visual-companion.md` + `scripts/`): dowiązać jako poddrzewo feature-discuss, oferowany just-in-time przy pytaniach wymagających mockupu/diagramu, z fallbackiem do terminala. ADR/rewizje/QA zostają. `brainstorming` nie jest vendorowany osobno, więc nie ma konfliktu dwóch skilli discovery. |
| `generate-tasks` | **Zachować + przejąć strukturę zadań z `writing-plans`** | Bloki Interfaces, Global Constraints, No Placeholders, kompletny kod w krokach, self-review spójności typów. Grep-AC i project-memory zostają jako Twoja warstwa. |
| `implement` | **Nie deprecjonować — wstrzyknąć 4 mechanizmy sdd w istniejący orchestrated `implement`** | Masz już tę samą architekturę: `implementation-worker` (fresh subagent per faza) + `phase-review` (gate) + `99-final-verification`. Realna delta sdd nad Twoim to tylko: (1) protokół 4 statusów (DONE/DONE_WITH_CONCERNS/NEEDS_CONTEXT/BLOCKED), (2) dobór modelu per rola, (3) ledger recovery po kompakcji (`.superpowers/sdd/progress.md`), (4) file-handoff via `task-brief`/`review-package` (anty-context-pollution). To **ulepszenia**, nie zamiennik. Wstrzyknięcie ich w `implement` jest tańsze niż pełna deprecjacja i zachowuje grep-AC + budżet `implementation-context.md` już wszyte w workery. Pełną deprecjację rozważyć dopiero jeśli retro (Faza 5) pokaże, że nakładka domenowa na sdd jest prostsza niż utrzymanie własnego orchestratora. |
| review gates (`[BLOCKER]`/`[WARN]`) | **Zmapować na Critical/Important/Minor, zachować Re-review Protocol** | Jedna taksonomia severity w całym pipeline; Re-review Protocol jako rozszerzenie w warstwie domenowej. |
| `ship` | **Skonsolidować z `finishing-a-development-branch`** | Obra pokrywa weryfikację testów, menu i sprzątanie worktree; z `ship` zachować to, czego obra nie ma (konwencje commit/PR message specyficzne dla Twoich repo). Jeśli delta jest mała — pełna deprecjacja `ship`. |
| `try-learn-skill` | **Zachować, dodać krok walidacji z `writing-skills`** | Ledger decyduje o promocji; przy promocji (n≥2) nowy skill przechodzi baseline RED test metodą obry. |
| `harvest` | **Zachować bez zmian** | Brak odpowiednika. |
| skille infra (verify.sh, pre-commit, gnhf) | **Zachować bez zmian** | Warstwa infrastrukturalna, nie procesowa. |

Skille do zvendorowania (brak odpowiednika u Ciebie): `using-git-worktrees`, `systematic-debugging`, `verification-before-completion`, `dispatching-parallel-agents`, `subagent-driven-development` (wraz z szablonami `implementer-prompt.md`, `task-reviewer-prompt.md` **oraz kompletem skryptów `scripts/`: `review-package`, `task-brief`, `sdd-workspace`** — `task-brief` jest nośny, sekcja "File Handoffs" sdd wymusza go jako jedyny kanał przekazu wymagań implementerowi; vendorowanie sdd bez niego łamie mechanizm anty-context-pollution), `finishing-a-development-branch`, opcjonalnie `executing-plans` jako fallback bez subagentów. **Nie vendorujemy:** `using-superpowers` (dispatcher — zbędny przy jawnym sterowaniu `@skillami`; przejmujemy tylko mechanizm hooka, patrz Faza 1.4) oraz `brainstorming` i `writing-plans` w całości — te służą jako dawcy sekcji do fuzji z feature-discuss i generate-tasks (Faza 3). **Wyjątek:** z brainstormingu vendorujemy poddrzewo visual companion (`visual-companion.md` + `scripts/server.cjs`, `helper.js`, `frame-template.html`, `start-server.sh`, `stop-server.sh`) dowiązane do feature-discuss, z telemetrią zneutralizowaną (Faza 1.3).

### Faza 3: Integracja warstwy domenowej (2–3 dni)

1. **Deklaracja łańcucha pipeline'u:** zamiast dispatchera — jawny łańcuch w treści hooka i w dokumentacji: `@feature-discuss` → `@generate-tasks` (na podstawie pliku planning) → `@implement` (na podstawie tasks) → `@review`/`@triada-review`. Każdy skill deklaruje swój stan terminalny i wskazuje następny krok (przejęty od obry wzorzec "the terminal state is invoking X"), ale przejście wykonuje człowiek jawnym wywołaniem — z wyjątkiem trybu headless, gdzie łańcuch spina gnhf. Auto-triggering dotyczy wyłącznie skilli strażniczych (reguły w hooku, Faza 1.4).
2. **Punkty styku pipeline'u:** feature-discuss kończy się (jak brainstorming) twardym handoffem do generate-tasks; generate-tasks kończy się ofertą wyboru subagent-driven vs executing-plans (przejęty wzorzec Execution Handoff). Stan terminalny każdego skilla jest jawnie zadeklarowany — to była u obry jedna z lepszych decyzji projektowych.
3. **Wstrzyknięcie grep-AC:** krok "AC fulfillment verification" jako obowiązkowy element promptu task-reviewera (rozszerzenie szablonu `task-reviewer-prompt.md` w warstwie domenowej) oraz jako sekcja pre-flight w planie.
4. **project-memory.md:** czytany w feature-discuss i generate-tasks (jak dotąd); dodatkowo przekazywany implementerom przez blok kontekstu w prompcie dispatchu (obra podkreśla: subagent dostaje wyłącznie skonstruowany kontekst — project-memory musi być w nim jawnie).
5. Aktualizacja dokumentacji i planning docs (PL) absolutpowers.

### Faza 4: Integracja z natywnym `/goal` (headless / unattended) — RESCOPED (decyzja 2026-07-14)

> **Rescope gnhf → `/goal` (decyzja 2026-07-14, po Fazie 3 migracji).** Ta faza była pierwotnie napisana pod **gnhf** — założone narzędzie headless, którego NIE używamy. Właściwym, natywnym mechanizmem pętli headless/unattended w Claude Code jest **`/goal`** (v2.1.139+; „Set a completion condition… Claude keeps working across turns until the condition is met"). Faza przekierowana na `/goal`; założenia gnhf-specyficzne odrzucone jako martwe. Referencja: <https://code.claude.com/docs/en/goal>.
>
> **Mechanika `/goal` (istotna dla scope):** `/goal` to wrapper wokół session-scoped prompt-based Stop hooka. Po każdej turze warunek + dotychczasowa konwersacja idą do small-fast-model (domyślnie Haiku), który zwraca yes/no + powód. **Evaluator NIE wywołuje narzędzi — ocenia wyłącznie to, co model już „wysurfował" w konwersacji.** Działa też nieinteraktywnie: `claude -p "/goal …"` przepuszcza pętlę do końca w jednym wywołaniu.

**Rdzeń tej fazy DOSTARCZONY w Fazie 3** (terminal-state contract, `planning-faza3-integracja-pipeline.md`):
1. **Kontrakt terminal-state prozą** = właściwa dźwignia pod `/goal`. Skoro evaluator czyta konwersację (nie pliki), jawne „pipeline niedomknięty — kontynuuj do skilla terminalnego" w promptach skilli bezpośrednio steruje decyzją stop/continue. Format maszynowy (frontmatter `next:`) świadomie odrzucony — evaluator go nie parsuje. ✅ zrobione.
2. **Protokół eskalacji cross-invocation (gnhf BLOCKED.md/ANSWERS.md) — WYCIĘTY.** `/goal` trzyma jedną sesję przez wiele tur; nie ma wywołań między-procesowych do zszywania. Eskalacja zostaje in-session przez statusy `PHASE_RESULT` (`BLOCKED`/`NEEDS_CONTEXT`), już zaimplementowane w `implement`. ✅ moot.
3. **Dobór modeli per rola** — już w `implement` Step O2 (model routing table). Uwaga: to model głównej tury; evaluator `/goal` to osobny small-fast-model (Haiku), konfigurowany globalnie, poza absolutpowers. ✅ zrobione.

**Reszta do zrobienia (cienka, doc-only — opcjonalna):**
4. Krótki przewodnik „prowadzenie pipeline'u absolutpowers pod `/goal`": wzorce condition (np. „feature dowieziony = `review` PASS + zmergowane", z klauzulą `or stop after N turns`), parowanie z auto mode (unattended = zgoda na narzędzia), headless `claude -p … --output-format stream-json --verbose`. Miejsce: sekcja w README lub `docs/`. Nie jest bramką ani nową mechaniką — tylko udokumentowanie natywnego feature'a.
5. (opcjonalnie) `using-git-worktrees` jako izolacja równoległych runów `/goal` — natywny w harnessie, wspomnieć tylko jeśli pojawi się realny use-case wieloraveningu.

### Faza 5: Walidacja i domknięcie (1 dzień + obserwacja) — CZĘŚCIOWO ZAMKNIĘTA (stan 2026-07-14)

> **Stan:** release już wykonany (pkt 4 ✅) — migracja formalnie wydana: **5.0.0** (jednodrzewowa architektura + vendoring), **5.1.0** (fuzje Faza 2), **5.2.0** (terminal-state Faza 3). Pozostają punkty jakościowe/obserwacyjne (1–3), które wymagają czasu kalendarzowego, nie kodu — mają biec w tle na realnej pracy, nie blokują niczego.

1. ⏳ Każdy zmodyfikowany skill domenowy przechodzi test metodą `writing-skills`: baseline RED (agent bez skilla łamie regułę), GREEN (ze skillem przestrzega), domknięcie znalezionych racjonalizacji. — do zrobienia ad-hoc przy kolejnych dotknięciach skilli; repo bez buildu, więc „test" = RED/GREEN prozą, nie suite.
2. ⏳ Dwa tygodnie pracy produkcyjnej na hybrydzie z logiem odchyleń (skill nie zadziałał / zadziałał zły / konflikt priorytetów). — obserwacja w tle.
3. ⏳ Retro: czy `ship` ma jeszcze rację bytu, czy Re-review Protocol dubluje pętlę fix-subagent obry, czy coś z listy deprecjacji trzeba przywrócić. — po ~2 tyg obserwacji.
4. ✅ Release absolutpowers + changelog — wykonane (5.0.0 → 5.1.0 → 5.2.0).

### Ryzyka i mitygacje

| Ryzyko | Mitygacja |
|---|---|
| Dryf od upstreamu — obra naprawia bugi/domyka luki w racjonalizacjach, a Ty tego nie dostajesz | Kwartalny diff pinowany SHA→tag (Faza 1.5) z selektywnym przenoszeniem; `VENDORED.md` z listą lokalnych modyfikacji, żeby merge był świadomy. |
| Lokalne cięcia psują skill (usunięta sekcja była nośna) | Każde cięcie odnotowane w `VENDORED.md`; testy metodą `writing-skills` w Fazie 5 wykrywają regresję zachowania. |
| Regresja jakości discovery po fuzji feature-discuss | Tani baseline z Fazy 0 (spec przed/po fuzji na tym samym feature'rze, bez instalacji obry); testy `writing-skills` RED/GREEN w Fazie 5 wykrywają regresję zachowania. |
| Wzrost kosztu tokenów (hook wstrzykuje treść przy starcie/kompakcji) | Slim hook (~10–15 linii) zamiast pełnego dispatchera; koszt tylko przy startup/clear/compact, nie przy każdej wiadomości. Monitoring w Fazie 5. |
| Kwestie licencyjne | MIT: zachować `LICENSE` obry i noty copyright w zvendorowanych plikach; atrybucja w README absolutpowers. |
| Telemetria | Companion **zachowany**, telemetria zneutralizowana przy vendoringu (hardcode `SUPERPOWERS_TELEMETRY_DISABLED=true` lub usunięcie stałej `SUPERPOWERS_BRAND_IMAGE_URL` — to tylko zdalne logo, zero danych projektu). Do czasu neutralizacji (np. przy testach na klonie obry) `SUPERPOWERS_DISABLE_TELEMETRY=1`. |
| Zależność Node.js (visual companion) | Companion to Node server; target-projekty Java/Spring mogą nie mieć Node w środowisku. feature-discuss musi wykrywać brak Node i gracefully wracać do trybu terminalowego; companion czysto opcjonalny. |

### Szacunek całkowity

Około 5,5–8 dni roboczych rozłożonych na 3–4 tygodnie (Faza 5 wymaga czasu kalendarzowego na obserwację; pilot z Fazy 0 pominięty, stąd −0,5–1 dzień względem wcześniejszego szacunku). Punkt bezpiecznego wyjścia po Fazie 2 (decyzje odwracalne, repo już zrestrukturyzowane z jednodrzewową architekturą `skills/` — korzyść niezależna od reszty, wartościowa nawet gdyby fuzja skilli utknęła).
