# Tasks: try-learn-skill jako codebase-scan + usunięcie harvest

## Mode
single-file

## Project Context

**Source doc:** `./absolutpowers/feature/planning-learned-skills-codebase-scan.md`

**Stack:** Markdown (SKILL.md prompt files), plugin wieloharnessowy (Claude/Codex/Pi). Repo **bez systemu budowania** — weryfikacja AC jest grep/strukturalna (odczyt plików + grep), nie testy runtime.

**Struktura:**
- `skills/{name}/SKILL.md` — jedno drzewo, źródło prawdy (host-agnostyczne)
- `agents/*.md` — zarejestrowani agenci Claude-only
- `CLAUDE.md` / `README.md` — dokumentacja repo; `AGENTS.md` = symlink do CLAUDE.md (auto-mirror)

**Patterns/Konwencje:**
- Dwujęzyczność: prompty user-facing → **polski**; treść techniczna → angielski.
- Frontmatter SKILL.md: `name`, `description` (triggers), `allowed-tools` (Claude), `argument-hint`.
- Format learned-skilla: `.claude/skills/learned/{name}/SKILL.md` w target-projekcie.

**Verification commands (grep/strukturalne — repo bez buildu):**
- try-learn codebase-scan: `grep -ci 'codebase\|skan' skills/try-learn-skill/SKILL.md` (>0), brak `git diff <base>...HEAD` jako głównego wejścia
- próg 3 + dowód: `grep -n '3' skills/try-learn-skill/SKILL.md` (kontekst progu) + `grep -ci 'file:line\|plik:linia' skills/try-learn-skill/SKILL.md`
- ledger usunięty: `grep -ci '_candidates.md\|ledger\|drugim wystąpieniu\|promocj' skills/try-learn-skill/SKILL.md` = 0
- granica: `grep -c 'update-ai-context' skills/try-learn-skill/SKILL.md` (>0)
- harvest skasowany: `test -d skills/harvest` (brak)
- harvest w żywych promptach: `grep -rn 'harvest' skills/ agents/` (tylko opisowa wzmianka w ship, brak wywołań)
- ship archiwizacja: `grep -ci 'archives/\|archiwiz' skills/ship/SKILL.md` (>0)

**Reference:**
- `skills/harvest/SKILL.md` — KROK 4 (logika archiwizacji: hard boundary, gate, git mv, summary.md template) — źródło do przeniesienia w Task 2
- `skills/try-learn-skill/SKILL.md` — obecny stan (ledger/promocja) do zastąpienia
- `skills/ship/SKILL.md` — KROK 1 zakłada „harvest już zarchiwizował" — do reconcile

## Global Constraints
> Wymagania obowiązujące KAŻDE zadanie:
- **Dwujęzyczność:** treść user-facing → polski; nie zmieniać istniejącej konwencji per plik.
- **Archiwum = nie rewizjonizm:** NIE ruszać `absolutpowers/archives/`, `docs/onboarding/*.html`, historii changelog w README. Grep czyszczący harvest celuje tylko w żywe prompty `skills/`+`agents/` (+ opis w CLAUDE.md/README).
- **Human gate zachowany:** zapis learned-skilla i archiwizacja wymagają jawnej zgody użytkownika PRZED zapisem/`mv` (AC-11, AC-13). Nie osłabiać.
- **Hard boundary archiwizacji:** przenosić WYŁĄCZNIE artefakty bieżącego feature'a; NIE dotykać reviews/problem/constitution/rules/patterns/innych feature'ów (AC-12).

## Implementation Tasks

### Task 1: Rewrite try-learn-skill na codebase-scan
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-6, AC-7, AC-8, AC-11

**Modify:**
- `skills/try-learn-skill/SKILL.md`

**Description:**
Przepisać body i frontmatter `try-learn-skill` z trybu feature-artefakt (planning+tasks+git diff, ledger, promocja przy 2. wystąpieniu) na **codebase-scan**: skan kodu projektu pod kątem powtarzalnych procedur, próg ≥3 wystąpień z dowodem `file:line`, batch approval, zapis wybranych do `.claude/skills/learned/`. Dodać jawną sekcję granicy vs `update-ai-context`.

**Requirements:**
- **Wejście = codebase:** frontmatter `description` + body opisują skan całego codebase'u projektu; opcjonalny `argument-hint` = ścieżka zawężająca zakres (domyślnie cały codebase). Usunąć czytanie `git diff <base>...HEAD` / planning / tasks jako głównego źródła (AC-1).
- **Próg powtarzalności:** jawny liczbowy próg domyślnie **3** wystąpienia wzorca; wymóg dowodu `file:line` (lub `plik:linia`) per wystąpienie. Wzmianka że próg można podać w argumencie (AC-2).
- **Batch approval:** jeden przebieg — skan prezentuje CAŁĄ listę kandydatów (nazwa + procedura + dowód wystąpień), użytkownik zaznacza które zapisać, zapis WYŁĄCZNIE zaznaczonych do `.claude/skills/learned/{name}/SKILL.md`. Human gate PRZED zapisem zachowany (AC-3, AC-11).
- **Usunąć ledger:** zero wzmianek `_candidates.md`, `ledger`, „drugim wystąpieniu", „promocja"/„fast-track" (AC-6).
- **Sekcja granicy vs update-ai-context:** wyodrębniona treść — update-ai-context = pasywna dokumentacja (patterns/rules/CLAUDE.md, tło); try-learn = aktywne wywoływalne procedury (learned-skille). Token `update-ai-context` w kontekście porównania (AC-7).
- **Graceful brak kandydatów:** gdy nic nie spełnia progu ≥3 (albo wzorce bez proceduralności — sama duplikacja kodu ≠ procedura) → jawny raport braku + koniec BEZ zapisu (AC-8).
- Frontmatter `description`/triggers bez „odpalany przez harvest".
- Zachować: wysoki próg wybredności, pomijanie kolizji ze statycznymi skillami, format learned SKILL.md.
- Proza PL user-facing.

**Tests (grep/strukturalne):**
- `grep -ci 'codebase\|skan' skills/try-learn-skill/SKILL.md` >0; brak `git diff.*HEAD` jako głównego wejścia (AC-1)
- próg `3` obecny w kontekście wystąpień + `file:line`/`plik:linia` (AC-2)
- batch approval + zapis tylko zaznaczonych opisany (AC-3)
- `grep -ci '_candidates.md\|ledger\|drugim wystąpieniu\|promocj\|fast-track' ...` = 0 (AC-6)
- `grep -c 'update-ai-context' ...` >0 w sekcji granicy (AC-7)
- opisany brak-kandydatów bez zapisu (AC-8); human gate przed zapisem obecny (AC-11)

**Implementation decisions / remarks:**
- Pełny rewrite SKILL.md: wejście=codebase (opcjonalny scope + próg N w argumencie), KROK 1 skan wzorców, KROK 2 próg ≥3 z dowodem `file:line`, KROK 3 test nieoczywistości (zachowany z podmianą rzeczowników), KROK 4 collision-check + NEW/UPDATE, KROK 5 batch approval (cała lista naraz, zapis tylko zaznaczonych, human gate twardy).
- Usunięte: ledger `_candidates.md`, promocja przy 2. wystąpieniu, fast-track, GC ledgera, czytanie planning/tasks/git diff, „odpalany przez harvest" z triggerów.
- Dodana sekcja „Granica vs update-ai-context" (pasywna dokumentacja vs aktywne wywoływalne procedury) — na górze, przed KROK 1.
- Grep: codebase/skan=14, git-diff-HEAD-jako-wejście=0, ledger/promocja=0, update-ai-context=7, batch approval opisany, human gate obecny, harvest=0.

### Task 2: Przenieś archiwizację do ship + reconcile + allowed-tools
**Status:** completed
**Traces to:** AC-5, AC-9, AC-12, AC-13

**Modify:**
- `skills/ship/SKILL.md`

**Description:**
Wnieść do `ship` logikę archiwizacji artefaktów feature'a z harvest KROK 4 (przeniesienie `planning-{slug}.md`/`tasks-{slug}.md` + katalog fazowy do `absolutpowers/archives/{slug}/` + wygenerowany `summary.md`), jako krok closeout za jawną zgodą. Odwrócić obecne założenie ship „harvest już zarchiwizował". Rozszerzyć `allowed-tools`.

**Requirements:**
- **Krok archiwizacji obecny w treści** (nie TODO): przenieś `planning-{slug}.md`/`tasks-{slug}.md` (+ katalog fazowy jeśli orchestrated) → `absolutpowers/archives/{slug}/` + `summary.md` (co zbudowano, dlaczego, kluczowe decyzje, AC, gdzie trwała wiedza). Ostatni krok closeout — po commicie/przed lub po PR wg obecnej logiki ship (AC-5).
- **Usunąć WSZYSTKIE żywe odwołania do harvest jako aktywnego poprzedzającego kroku (5 miejsc, potwierdzone grepem)** — inaczej final gate AC-10 (`grep -rn harvest skills/`) fail:
  - l.7 frontmatter `description`: „Naturalny krok po review/harvest." → „Naturalny krok po review."
  - l.10 frontmatter `TRIGGER`: „po zakończonym harvest, gotowe do commita…" → usunąć „po zakończonym harvest" (np. „gdy zmiany feature'a gotowe do commita").
  - l.43 KROK 1: „(harvest mógł już przenieść artefakty)" → usunąć/przeformułować (ship sam zarządza artefaktami).
  - l.51 KROK 1: „`archives/{slug}/summary.md` — jeśli harvest już zarchiwizował" → odwrócić: ship archiwizuje sam jako ostatni krok; nie zakładać wcześniejszego archiwum (AC-9).
  - l.64 KROK 2: „w tym przeniesienia z harvestu i `archives/{slug}/summary.md`" → „w tym artefakty z własnego kroku archiwizacji ship".
- **Dozwolona pozostaje** co najwyżej opisowa/historyczna wzmianka, że ship PRZEJĄŁ funkcję archiwizacji (nie że harvest jest aktywnym krokiem) — zgodnie z AC-10.
- **Hard boundary (przeniesiona z harvestu):** archiwizuj WYŁĄCZNIE artefakty bieżącego feature'a; jawne zdanie że NIE dotyka `reviews/`, `problem/`, `constitution.md`, `rules.md`, `patterns.md`, innych feature'ów (AC-12).
- **Human gate:** pokaż listę plików + streszczenie, czekaj na potwierdzenie PRZED `git mv`/`mv`; brak ścieżki cichej archiwizacji (AC-13).
- **allowed-tools:** rozszerzyć frontmatter `ship` o `Bash(mkdir:*)`, `Write(**/absolutpowers/archives/**/*.md)` i `Bash(mv:*)` (albo `git mv` przez istniejące `Bash(git:*)`) — obecnie: `Read, Glob, Grep, Bash(git:*), Bash(gh auth:*), Bash(gh pr:*)`.
- Proza PL user-facing.

**Tests (grep/strukturalne):**
- `grep -ci 'archives/\|archiwiz\|summary.md' skills/ship/SKILL.md` >0, krok w treści nie jako TODO (AC-5)
- brak „harvest już zarchiwizował" jako warunku wstępnego; założenie odwrócone (AC-9)
- `grep -n -i 'harvest' skills/ship/SKILL.md` = zero odwołań do harvest jako aktywnego kroku (frontmatter description/TRIGGER + KROK1×2 + KROK2 wyczyszczone); dozwolona co najwyżej wzmianka „ship przejął archiwizację" (AC-10)
- zdanie hard boundary obecne (AC-12); gate przed `mv` obecny (AC-13)
- frontmatter ship zawiera `mkdir` + `Write(**/absolutpowers/archives/**/*.md)` (uprawnienia)

**Implementation decisions / remarks:**
- Dodano `## KROK 4.5: Archiwizacja artefaktów feature'a (za zgodą)` (po KROK 4 PR, przed human gate) — pełna logika z harvest KROK 4: warunki wstępne (taski completed, epic complete), procedura (lista + summary.md template + ostrzeżenie ADR), hard boundary (tylko artefakty feature'a).
- KROK 5 gate rozszerzony o (d) archiwizację (lista + summary); KROK 6 wykonuje `mkdir`+`git mv`+summary PRZED `git add`, żeby przeniesienia weszły do commita domykającego.
- Reconcile: usunięto wszystkie 5 żywych referencji harvest (description, TRIGGER, KROK1 ×2, KROK2) — ship nie zakłada już wcześniejszego archiwum, sam archiwizuje. `grep -i harvest ship` = 0.
- allowed-tools rozszerzone o `Bash(mkdir:*)`, `Bash(mv:*)`, `Write(**/absolutpowers/archives/**/*.md)`.

### Task 3: Usuń skill harvest
**Status:** completed
**Traces to:** AC-4

**Description:**
Skasować cały katalog `skills/harvest/` (wraz z `SKILL.md`). Wykonać PO Task 2 — ship musi już mieć przeniesioną logikę archiwizacji, zanim źródło zniknie.

**Requirements:**
- Usunąć `skills/harvest/` całościowo (`git rm -r skills/harvest`).
- Nie zostawić pustego katalogu.

**Tests (grep/strukturalne):**
- `test -d skills/harvest` → brak katalogu (AC-4)

**Implementation decisions / remarks:**
- `git rm -r skills/harvest` — katalog usunięty (KROK 4 archiwizacji przeniesiony do ship w Task 2 przed usunięciem źródła). `test -d skills/harvest` = brak.

### Task 4: Rewiring implement — nudge harvest → ship
**Status:** completed
**Traces to:** AC-10

**Modify:**
- `skills/implement/SKILL.md`

**Description:**
Zamienić best-effort nudge do harvest na nudge do `ship` jako closeout przed commitem. **Dwa miejsca w `skills/implement/SKILL.md`** odwołują się do harvest — oba trzeba poprawić, inaczej test `grep -ci harvest = 0` nie przejdzie:
1. Sekcja „Optional: faza harvest (best-effort)" (ok. l. 624-634) — nudge block.
2. Sekcja „Terminal state" (ok. l. 642) — zdanie „Opcjonalnie PRZED review możesz uruchomić fazę harvest… `@harvest` → try-learn-skill + document-feature… Kolejność: harvest (opcjonalnie) → review → merge/ship" (dodane w Fazie 3).

**Requirements:**
- Sekcja nudge (l. ~624-634) wskazuje `/absolutpowers:ship` (closeout: commit message + PR + archiwizacja), nie `/absolutpowers:harvest`.
- Terminal state (l. ~642): zamienić wzmiankę o harvest na `ship` — closeout to teraz ship (który archiwizuje); kolejność „→ review → ship" (ship archiwizuje). Nie zostawić `@harvest`/„fazę harvest".
- Zachować charakter best-effort/opcjonalny (pominięcie nie blokuje completion).
- Zero odwołań do `harvest` jako wywoływalnego skilla w implement (AC-10).
- Proza PL.

**Tests (grep/strukturalne):**
- `grep -ci 'harvest' skills/implement/SKILL.md` = 0
- nudge do `ship` obecny w miejscu dawnego harvest nudge

**Implementation decisions / remarks:**
- Miejsce 1 (nudge, „Optional: faza harvest" → „Optional: closeout"): teraz wskazuje `/absolutpowers:ship` (commit+PR+archiwizacja), z osobną wzmianką o `document-feature` ad-hoc.
- Miejsce 2 (Terminal state l.642): kolejność przepisana na „review → ship (commit/archiwizacja) → merge"; document-feature/try-learn odpalane ad-hoc, nie jako etap. Zero „harvest".
- Grep: `harvest` w implement = 0; nudge `absolutpowers:ship` = 1.

### Task 5: Rewiring document-feature — usuń odwołanie do harvest
**Status:** completed
**Traces to:** AC-10

**Modify:**
- `skills/document-feature/SKILL.md`

**Description:**
Usunąć wzmianki o byciu odpalanym przez harvest (frontmatter triggers + ew. body). document-feature zostaje samodzielnym commandem.

**Requirements:**
- Usunąć „odpalany przez harvest" / „przez harvest" z description/triggers i body.
- Nie zmieniać reszty logiki skilla (poza scope).
- Zero odwołań do `harvest` jako wywoływalnego kroku (AC-10).

**Tests (grep/strukturalne):**
- `grep -ci 'harvest' skills/document-feature/SKILL.md` = 0

**Implementation decisions / remarks:**
- Frontmatter TRIGGER: „harvest docs" → „docs modułu z feature'a", „odpalany przez harvest" → „odpalany ad-hoc". Reszta logiki skilla nietknięta. Grep harvest = 0.

### Task 6: Docs — CLAUDE.md + README (usuń Harvest Phase, zaktualizuj pipeline)
**Status:** completed
**Traces to:** AC-10, none (docs)

**Modify:**
- `CLAUDE.md`
- `README.md`

**Description:**
Usunąć wszystkie ŻYWE (nie-changelogowe) odwołania do harvest z CLAUDE.md i README, opisać nowy try-learn (codebase-scan, ad-hoc) i archiwizację w ship. README ma harvest w WIELU miejscach — wszystkie trzeba objąć, inaczej README instruuje odpalenie nieistniejącego skilla. AGENTS.md = symlink (auto-mirror, brak osobnej edycji).

**Requirements:**
- **CLAUDE.md:** usunąć „### Harvest Phase (closeout)"; zaktualizować opis pipeline/closeout — docs = osobne commandy (document-feature/document-module), learning = ad-hoc `try-learn-skill` codebase-scan, archiwizacja = w `ship`. Sprawdzić Repository Layout / inne wzmianki harvest.
- **README — WSZYSTKIE żywe miejsca (potwierdzone grepem):**
  - l. ~53: przykład Quick Start `/absolutpowers:harvest …` → usunąć/zamienić na ship
  - l. ~62: diagram pipeline `… → review → harvest → ship` → usunąć `harvest` z łańcucha (`… → review → ship`)
  - l. ~156: wiersz tabeli skilli `| harvest | Closeout… |` → usunąć wiersz; ew. zaktualizować wiersz try-learn na codebase-scan
  - l. ~242-266: cała sekcja `### /absolutpowers:harvest` (opis 4-step, when/in-out, przykład) → usunąć; opisać nowy try-learn (codebase-scan) tam gdzie stosowne
  - l. ~268, ~270: proza w sekcji `ship` — „Autodetects… (harvest may already have moved the artifacts)" i „When: after `review`/`harvest`" → reconcile: ship SAM archiwizuje; usunąć „harvest may already have moved" i „/harvest" z „when"
  - l. ~293: wiersz „Situation → skill" `| A finished feature, pre-commit | harvest | …` → zamienić na `ship`/try-learn wg nowej roli
  - l. ~440: komentarz w repo-tree `archives/{slug}/ … (from harvest)` → `(from ship)`
  - dodać wpis changelog (nowa wersja) opisujący zmianę
- **Grep-boundary:** NIE ruszać historii changelog opisującej stary harvest w kontekście wcześniejszych wersji (l. ~556, 562, 570-571, 595, 603-607 — rewizjonizm). Tylko bieżący opis pipeline/skills/tabele/tree.
- Zero odwołań do harvest jako aktywnego skilla w bieżącym opisie (AC-10).

**Tests (grep/strukturalne):**
- `grep -ci 'Harvest Phase' CLAUDE.md` = 0
- `grep -n -i 'harvest' README.md` = WYŁĄCZNIE trafienia w sekcji changelog (historyczne wersje); zero w Quick Start / diagramie pipeline / tabeli skilli / sekcji command / Situation→skill / repo-tree / sekcji ship
- CLAUDE.md/README opisują try-learn jako codebase-scan + archiwizację w ship
- `grep -rn 'harvest' skills/ agents/` = tylko opisowa wzmianka w ship (AC-10)

**Implementation decisions / remarks:**
- CLAUDE.md: sekcja „Harvest Phase (closeout)" → „Closeout and on-demand knowledge capture" (ship closeout + try-learn codebase-scan + granica vs update-ai-context + document-*). Fraza przeformułowana by nie łapać `grep -ci 'Harvest Phase'`. CLAUDE harvest = 0.
- README: Quick Start (usunięto linię harvest), diagram pipeline (harvest wypadł z łańcucha), tabela skilli (wiersz harvest usunięty, ship zaktualizowany o archiwizację, try-learn na codebase-scan), sekcja command harvest → nowa sekcja `### /absolutpowers:try-learn-skill` (codebase-scan), proza ship (usunięto „harvest may already have moved" + „after review/harvest"→„after review"), Situation table (harvest→ship+try-learn), repo-tree („from harvest"→„from ship"). Wpis changelog 5.1.0 dodany. Historia changelog (≤3.x) nietknięta.
- Wersja bump 5.0.1 → 5.1.0 (manifesty + CLAUDE.md). README harvest tylko w changelogu (≥l.513).

### Task 7: Final Verification
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13

**Create:**
- None

**Modify:**
- None

**Description:**
Uruchomić grep/strukturalne komendy weryfikacyjne przeciw zintegrowanej zmianie. Repo bez buildu — bramki to walidacja strukturalna. Nie oznaczać completed jeśli którakolwiek faili.

**Requirements:**
- try-learn codebase-scan (AC-1): `grep -ci 'codebase\|skan' skills/try-learn-skill/SKILL.md` >0
- próg 3 + dowód (AC-2): próg `3` w kontekście wystąpień + `file:line`/`plik:linia`
- batch approval (AC-3) + graceful brak-kandydatów (AC-8) + human gate (AC-11) — obecne w treści
- ledger usunięty (AC-6): `grep -ci '_candidates.md\|ledger\|drugim wystąpieniu\|promocj\|fast-track' skills/try-learn-skill/SKILL.md` = 0
- granica update-ai-context (AC-7): `grep -c 'update-ai-context' skills/try-learn-skill/SKILL.md` >0
- harvest skasowany (AC-4): `test -d skills/harvest` → brak
- ship archiwizacja (AC-5) + reconcile (AC-9) + hard boundary (AC-12) + gate (AC-13) + allowed-tools: obecne
- harvest w żywych promptach (AC-10): `grep -rn 'harvest' skills/ agents/` = co najwyżej opisowa wzmianka w ship; `grep -ci 'harvest' skills/implement/SKILL.md skills/document-feature/SKILL.md` = 0; `grep -ci 'Harvest Phase' CLAUDE.md` = 0
- harvest w README (AC-10, poza changelogiem): `grep -n -i 'harvest' README.md` = WYŁĄCZNIE trafienia w sekcji changelog (historyczne wersje); zero w Quick Start / diagramie pipeline / tabeli skilli / sekcji command / Situation→skill / repo-tree / sekcji ship
- Frontmatter ship zawiera nowe uprawnienia (`mkdir`, `Write(archives)`)
- Nie oznaczać completed jeśli którakolwiek faili.

**Tests:**
- Wszystkie powyższe grepy zwracają oczekiwane wartości (0 rozbieżności)
- Manifesty JSON walid (jeśli dotknięte): `python3 -m json.tool` OK
- Hook SessionStart emituje poprawny JSON

**Implementation decisions / remarks:**
- Komendy wykonane: grep/strukturalne AC-1..AC-13 + JSON/hook/wersje.
- Wyniki (0 rozbieżności):
  - AC-1: try-learn codebase/skan=14, git-diff-HEAD jako wejście=0.
  - AC-2: `file:line`=12, próg `3` obecny.
  - AC-3/8/11: batch approval, brak-kandydatów-bez-zapisu, human gate — obecne w treści.
  - AC-6: ledger/promocja/fast-track=0.
  - AC-7: update-ai-context=7 (sekcja granicy).
  - AC-4: `test -d skills/harvest` = brak.
  - AC-5/9/12/13: ship archives/archiwiz=19, reconcile (0 harvest), hard boundary, gate przed mv — obecne; allowed-tools mkdir+Write(archives)=1+1.
  - AC-10: `grep -rin harvest skills/ agents/`=0; implement=0; document-feature=0; CLAUDE „Harvest Phase"=0; README harvest tylko w changelogu.
  - JSON manifestów OK (oba 5.1.0), hook SessionStart OK.
- Pominięte: none.

**Example:**
```bash
test -d skills/harvest && echo "FAIL harvest exists" || echo "harvest removed OK"
grep -rn 'harvest' skills/ agents/
grep -ci '_candidates.md\|ledger\|drugim wystąpieniu\|promocj' skills/try-learn-skill/SKILL.md
grep -c 'update-ai-context' skills/try-learn-skill/SKILL.md
grep -ci 'archives/\|archiwiz' skills/ship/SKILL.md
```
