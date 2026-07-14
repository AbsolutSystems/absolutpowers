# Implementation Context: Faza 1 — feature-discuss ← brainstorming

## Purpose
Handoff dla workerów faz. Wszystkie fazy edytują JEDEN plik `skills/feature-discuss/SKILL.md` sekwencyjnie. Trzymaj tu tylko fakty, których potrzebują kolejne fazy (gdzie co wstawiono, jakie nagłówki są kanoniczne, decyzje o brzmieniu rekoncyliacji). Krótko.

## Completed Phases
- **Phase 1 (HARD-GATE + rekoncyliacja micro-change):** completed. Patrz `01-hard-gate.md` → Implementation Decisions dla pełnych detali.
- **Phase 2 (Wczesny scope-check):** completed. Patrz `02-scope-check.md` → Implementation Decisions dla pełnych detali.
- **Phase 3 (Prezentacja sekcjami + skalowanie długości):** completed. Patrz `03-section-presentation.md` → Implementation Decisions dla pełnych detali.
- **Phase 4 (Spec self-review — nowa Faza 5A):** completed. Patrz `04-spec-self-review.md` → Implementation Decisions dla pełnych detali.
- **Phase 5 (Visual Companion — sekcja przekrojowa + wskaźniki):** completed. Patrz `05-visual-companion.md` → Implementation Decisions dla pełnych detali.
- **Phase 6 (Rozszerzenie `allowed-tools`):** completed. Patrz `06-frontmatter-tools.md` → Implementation Decisions dla pełnych detali.

## Struktura SKILL.md (aktualna, PO Fazie 1)
- L1-16: frontmatter (`name`, `description`, `allowed-tools`, `argument-hint`). **Faza 6 rozszerzyła TYLKO `allowed-tools` (L14)** o 3 granty companion; reszta frontmatter nietknięta. Finalna wartość `allowed-tools`: `Read, Glob, Grep, Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(tree:*), Bash(mkdir:*), Bash(companion-scripts/start-server.sh:*), Bash(companion-scripts/stop-server.sh:*), Write(**/absolutpowers/feature/**/*.md), Write(**/docs/adr/*.md), Write(**/.superpowers/brainstorm/**/*.html), Agent`. Granty Bash companion używają literalnego prefiksu (bez wiodącego wildcarda — Bash-granty są prefiksowe, nie glob) równego dokumentowanemu poleceniu w `visual-companion.md` (poprawka po phase-review #1).
- L18-22: nagłówek roli, SKRÓCONY (jedno zdanie roli + wskaźnik do sekcji HARD-GATE; usunięto zdublowane „NIE PISZ KODU").
- L24-31: „## Temat feature'a" ($ARGUMENTS).
- **L33-39: NOWY blok `## HARD-GATE — akceptacja designu przed implementacją`** (3 akapity: reguła KAŻDY projekt / anty-wzorzec „zbyt proste" / rekoncyliacja micro-change).
- L41+: „## Router trybu" (Tryb A / B / C) — dalsze offsety w SKILL.md przesunięte o ok. +15 linii względem starego baseline z powodu nowego bloku; kolejne fazy niech lokalizują po nagłówkach, nie numerach.
- „## Proces rozmowy" → Faza 0, Faza 1 (teraz z nowym akapitem scope-checku od razu po nagłówku, przed resztą treści Fazy 1), Faza 2, **Faza 3 ma teraz dwie podsekcje w tej kolejności: `#### Prezentacja designu sekcjami (ścieżka nie-epic)` (NOWA, Faza 3 tego planu), potem `#### Detekcja Epica`** (nietknięta), Faza 4, **Faza 5 micro-change ma teraz dodatkowy punkt rekoncyliacji z HARD-GATE** (ostatni bullet sekcji Micro-change), Faza 5B QA, Faza 6 review, Faza 7 ADR.
- Sekcje „## Format:" (standard / epic main / phase doc) — nietknięte.
- „## Zasady zachowania" — **Zasada #1 przeformułowana**: teraz "HARD-GATE — implementacja dopiero po akceptacji", odwołuje sekcję HARD-GATE zamiast gołego „NIE PISZ KODU". Pozostałe 10 zasad nietknięte.
- **Faza 5 (zapis)** ma teraz zaraz po sobie **nową `### Faza 5A: Spec self-review`** (Faza 4 tego planu), a dopiero potem `### Faza 5B: QA Enrichment` (nietknięta, treściowo identyczna sprzed Fazy 4). Kolejność w pliku: Faza 5 → Faza 5A → Faza 5B → Faza 6 → Faza 7.
- **NOWA sekcja `## Visual Companion — wizualne wspomaganie dyskusji`** (Faza 5 tego planu) wstawiona MIĘDZY blokiem HARD-GATE a `## Router trybu` (czyli zaraz po akapicie rekoncyliacji micro-change z HARD-GATE). Jednozdaniowe wskaźniki-frazowanie „patrz sekcja **Visual Companion**" dodane w: `### Faza 1: Zrozumienie potrzeby` (przed `ZASADA: JEDNO PYTANIE NA TURĘ`), `### Faza 3: Propozycja rozwiązania` (przed `#### Prezentacja designu sekcjami`), `### Faza 4: Doprecyzowanie` (przed `Pamiętaj: jedno pytanie na turę...`). `### Faza 2: Analiza kodu` celowo BEZ wskaźnika.

## Created / Changed API
- Nowy kanoniczny nagłówek sekcji w `skills/feature-discuss/SKILL.md`: `## HARD-GATE — akceptacja designu przed implementacją`, umieszczony między `## Temat feature'a` a `## Router trybu`. **Kolejne fazy odwołujące się do gate (np. Faza 3 prezentacja sekcjami, Faza 5A self-review, companion) mogą linkować do tej sekcji po nagłówku.**
- Kanoniczne brzmienie rekoncyliacji gate↔micro-change (grep-verifiable, użyte w 2 miejscach — blok HARD-GATE + Faza 5 micro-change): zawiera frazę `spełnia gate` i/lub `nie obchodz`. Jeśli kolejna faza dodaje kolejne odwołanie do rekoncyliacji, użyj tego samego wzorca słownego dla spójności (nie wprowadzaj nowej alternatywnej frazy).
- Nowy kanoniczny nagłówek podsekcji (Faza 3 tego planu) w `### Faza 3: Propozycja rozwiązania`: `#### Prezentacja designu sekcjami (ścieżka nie-epic)`, wstawiony przed `#### Detekcja Epica` (który pozostaje NIETKNIĘTY — treść identyczna sprzed Fazy 3). Zawiera: 5 nazwanych sekcji (Architektura/Komponenty/Data flow/Obsługa błędów/Testy) jako numerowana lista, instrukcję "osobne pytanie o akceptację po KAŻDEJ sekcji" powiązaną z HARD-GATE i z zasadą jedno-pytanie-na-turę (Faza 1), oraz instrukcję skalowania długości (kilka zdań ↔ ~200-300 słów). **Faza 4 (spec self-review) i Faza 5 (visual companion), jeśli odwołują się do prezentacji sekcjami, powinny linkować do tego nagłówka po nazwie, nie duplikować treści.**

## Decisions Made
- Baza rewrite = feature-discuss (ADR lokalny). Mechanika obry wszczepiana jako grafty.
- HARD-GATE = akceptacja designu, NIE ciężar doca. Micro-change przeżywa pod gate (Faza 1 zaimplementowała tę rekoncyliację dosłownie w SKILL.md).
- Rewrite-to-unify zastosowany od razu w Fazie 1: soft „NIE PISZ KODU" z nagłówka roli skonsolidowane w jawny blok HARD-GATE + Zasadę #1, zamiast zostawić dublujący się soft-tekst obok nowego bloku.

## Test Utilities / Fixtures
- Brak testów runtime. Weryfikacja = frontmatter YAML parse + grep markerów AC (patrz Verification History).

## Constraints For Next Phases
- Dwujęzyczność: user-facing PL, techniczne EN. Nie wklejaj surowego EN donora.
- NIE ruszaj: `name`, `description`, `argument-hint`, Router A/B/C, formaty doców, istniejących grantów `allowed-tools` (poza rozszerzeniem z Fazy 6).
- Rewrite-to-unify: konsoliduj miękkie normy zamiast dokładać kolejne — Faza 1 to zademonstrowała (nagłówek roli + Zasada #1 skonsolidowane z blokiem HARD-GATE).
- Numery linii w SKILL.md przesunęły się (+~15 linii od Fazy 1) i przesuną się dalej po każdej kolejnej fazie — lokalizuj po nagłówkach markdown, nie po numerach linii z tego pliku.
- Sekcja HARD-GATE jest teraz istniejącym punktem odwołania (anchor) — Faza 2 (scope-check), Faza 3 (prezentacja sekcjami), Faza 4 (spec self-review) i Faza 5 (visual companion) mogą/powinny odwoływać się do niej nazwą nagłówka zamiast tworzyć równoległą normę.
- Sekcja `## Visual Companion` jest teraz istniejącym punktem odwołania (anchor), analogicznie do HARD-GATE — Faza 6 (allowed-tools) powinna odwoływać się do niej po nazwie przy uzasadnianiu rozszerzenia frontmatter, nie duplikować opisu mechanizmu.
- Faza 6 (allowed-tools, następna) MUSI: (a) dodać Bash grant dla `companion-scripts/start-server.sh` i `stop-server.sh` (obecny allowlist ma tylko `find/wc/cat/head/tail/tree/mkdir`), (b) dodać Write grant `**/.superpowers/brainstorm/**/*.html` (obecny Write allowlist ma tylko `absolutpowers/feature/**` + `docs/adr/**`), (c) NIE ruszać `name`/`description`/`argument-hint`/pozostałych grantów, (d) potwierdzić że frontmatter nadal YAML-parsowalny po zmianie (AC-12).
- Nowy wzorzec komunikatu z Fazy 2: „patrz Faza 3: Detekcja Epica" — krótki wskaźnik-frazowanie do istniejącego nagłówka `#### Detekcja Epica` w Fazie 3, bez kopiowania jego treści. Jeśli kolejna faza (3, 4, 5) potrzebuje odwołać się do detekcji epica z innego miejsca, użyj tego samego wzorca wskaźnikowego ("patrz Faza 3: Detekcja Epica"), nie nowego alternatywnego sformułowania.
- Akapit scope-checku (Faza 2) leży bezpośrednio pod nagłówkiem `### Faza 1: Zrozumienie potrzeby`, przed resztą treści Fazy 1 i przed `**ZASADA: JEDNO PYTANIE NA TURĘ.**`. Faza 3 (prezentacja sekcjami) nie musi tego ruszać — to odrębny akapit na wejściu Fazy 1, nagłówek `#### Detekcja Epica` w Fazie 3 zostaje nietknięty jako cel wskaźnika.
- Faza 3 (ten plan) zaimplementowana: `#### Prezentacja designu sekcjami (ścieżka nie-epic)` żyje MIĘDZY blokiem rekomendacji podejścia a `#### Detekcja Epica`, zamknięta jednozdaniowym rozgraniczeniem "dotyczy ścieżki nie-epic; jeśli okaże się epikiem — patrz Detekcja Epica niżej". Kolejne fazy (4 self-review, 5 companion) mogą wskazywać na tę podsekcję po nazwie nagłówka — nie duplikuj listy 5 sekcji ani instrukcji skalowania długości gdziekolwiek indziej w pliku.
- Faza 4 (ten plan) zaimplementowana: nowy kanoniczny nagłówek `### Faza 5A: Spec self-review`, wstawiony między `### Faza 5: Ocena złożoności i zapis` i `### Faza 5B: QA Enrichment`. Zawiera przypis zakresu wzorowany dosłownie na `> Dotyczy: ...` z Fazy 5B (identyczna formuła wykluczenia: micro-change / `planning-main.md` / stuby faz), 4 kryteria skanu jako bullet listę (placeholdery/TODO, wewnętrzna sprzeczność, scope-fit, dwuznaczność → wybierz jedną interpretację i uczyń ją jawną), instrukcję "napraw inline, bez pełnego re-review", i jawne zdanie że Faza 5A **nie emituje** severity — `[BLOCKER]`/`[WARN]` pojawiają się tam WYŁĄCZNIE jako wskazanie-referencja do bramki review-plan (Faza 6), nigdy jako emitowany marker tej fazy. Kolejne fazy (5 companion, 6 allowed-tools) niech linkują do tego nagłówka po nazwie, nie duplikują treści skanu ani formuły wykluczenia.
- Faza 5 (ten plan) zaimplementowana: nowa sekcja `## Visual Companion — wizualne wspomaganie dyskusji` (7 akapitów pogrubionych leadów: just-in-time offer, decyzja per-pytanie, graceful fallback brak-Node, bezpieczeństwo/statyczny render, gate integrity, tryb nieinteraktywny gnhf, odwołanie do `visual-companion.md` + przypomnienie `.gitignore`). Kanoniczna fraza gate integrity (grep-verifiable, użyj tej samej jeśli kolejna faza się do niej odwołuje): "niedostępność ≠ akceptacja" + "HARD-GATE ... nadal wymaga jawnej, wprost wyrażonej akceptacji użytkownika". `visual-companion.md` pozostał NIEtknięty (read-only, potwierdzone `git diff --stat` pusty). **Frontmatter `allowed-tools` świadomie NIE rozszerzony w tej fazie** — companion opisany w SKILL.md odwołuje `companion-scripts/start-server.sh`/`stop-server.sh` i katalog `.superpowers/brainstorm/**`, ale odpowiadający grant Bash/Write przypisany jest wprost do **Fazy 6** (krok 5a planu). Faza 6 musi dodać: Bash grant na `companion-scripts/start-server.sh` i `stop-server.sh`, Write grant na `**/.superpowers/brainstorm/**/*.html` — wąsko, bez luzowania pozostałych grantów (AC-12).

## Verification History
- Phase 1: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"` → pass.
- Phase 1: `grep -c -iE "spełnia gate|nie obchodz|nie jest obejściem" skills/feature-discuss/SKILL.md` → 2 (oczekiwane ≥2) → pass.
- Phase 1: `grep -n "HARD-GATE"` (linia 33-ish) występuje przed `grep -n "## Router trybu"` (linia 41-ish) → pass.
- Phase 1: `grep -niE "zbyt proste|za proste"` → 1 trafienie → pass.
- Phase 2: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"` → pass.
- Phase 2: `grep -c "to nie jeden feature, to epic" skills/feature-discuss/SKILL.md` → 1 (bez duplikacji) → pass.
- Phase 2: `grep -niE "niezależn.*podsystem|wiele podsystem|scope-check"` → 1 trafienie (linia ~148) → pass.
- Phase 2: manualnie potwierdzono — akapit scope-checku leży między nagłówkiem Faza 1 (L146) i `ZASADA: JEDNO PYTANIE NA TURĘ` (L160), tj. przed pierwszym pytaniem szczegółowym.
- Phase 3: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"` → pass.
- Phase 3: `grep -niE "po każdej sekcji|akceptacj.*sekcj" skills/feature-discuss/SKILL.md` → 2 trafienia (L246 opis, L254 instrukcja) → pass.
- Phase 3: `grep -niE "skaluj|złożon" skills/feature-discuss/SKILL.md` → trafienia w L254/L256/L258 (rejon Fazy 3) → pass.
- Phase 3: manualnie potwierdzono — 5 sekcji (Architektura/Komponenty/Data flow/Obsługa błędów/Testy) obecne jako numerowana lista L248-252; `#### Detekcja Epica` (L262) treściowo identyczna jak przed edycją (tylko przesunięta w dół o nowy blok).
- Phase 4: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"` → pass.
- Phase 4: `grep -nE "### Faza 5:|### Faza 5A|### Faza 5B" skills/feature-discuss/SKILL.md` → L300 → L336 → L350, kolejność rosnąca → pass.
- Phase 4: `grep -niE "wyklucz|nie dotyczy|micro-change"` w rejonie 5A (L336-349) → dopasowanie na L338 (`> Dotyczy: ... NIE dotyczy: micro-changes, planning-main.md, ani stubów faz epica.`) → pass.
- Phase 4: manualnie potwierdzono — sekcja 5A (L336-349) zawiera 4 kryteria skanu, przypis zakresu, i jedyne wystąpienia `[BLOCKER]`/`[WARN]` w tym rejonie są referencją-wskazaniem do review-plan (dozwolony wyjątek), nie emitowanym markerem; treść Fazy 5B (teraz L350+) niezmieniona.
- Phase 5: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"` → pass.
- Phase 5: `grep -c "Visual Companion" skills/feature-discuss/SKILL.md` → 4 (1 nagłówek + 3 wskaźniki) → pass.
- Phase 5: `grep -c "visual-companion.md" skills/feature-discuss/SKILL.md` → 2 → pass.
- Phase 5: `grep -niE "brak.*Node|bez Node|Node.*niedostęp|fallback.*terminal"` → dopasowanie na linii "Graceful fallback — brak Node" → pass.
- Phase 5: `grep -niE "niedostępn.*nie.*akceptacj|nie.*domyśln.*akceptacj|nadal wymaga.*akceptacj"` → dopasowanie na linii "Gate integrity — niedostępność ≠ akceptacja..." → pass.
- Phase 5: `grep -n ".superpowers" skills/feature-discuss/SKILL.md` → 1 trafienie (przypomnienie gitignore w rejonie companion) → pass.
- Phase 5: manualnie potwierdzono (awk region check) — rejon `### Faza 2: Analiza kodu` do `### Faza 3` NIE zawiera frazy "Visual Companion" → pass.
- Phase 5: `git diff --stat skills/feature-discuss/visual-companion.md` → pusty (plik nietknięty, read-only zachowane) → pass.
- Phase 6: `python3 -c "...; assert d['name']=='feature-discuss'; assert 'brainstorm' in d['allowed-tools']; print('FM OK')"` → FM OK.
- Phase 6: `git diff skills/feature-discuss/SKILL.md | grep -E '^[+-]' | grep -iE 'name:|description:|argument-hint:'` → brak trafień (żadne z tych pól nie zmienione) → pass.
- Phase 6: `grep -nE "Bash\(\*\)|Bash\(:"` → brak trafień (brak szerokiego wildcarda) → pass.
- Phase 6: `grep "superpowers/brainstorm"` + `grep -iE "companion-scripts/(start|stop)-server"` → oba obecne w L14 → pass.
- Phase 6: global — FM presence we wszystkich SKILL.md OK; wszystkie `*.json` walidne → pass.
</content>
