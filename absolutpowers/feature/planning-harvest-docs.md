# Feature: Harvest Phase — document-feature + harvest orchestrator

## Status
Draft — 2026-06-17

## Problem
Po zakończeniu implementacji feature'a wiedza o tym **jak moduł działa i dlaczego** ginie. Przy rozbudowie tego samego modułu pół roku później agent AI (traktowany jak nowy developer w zespole) rozumuje od zera — nie ma trwałej, czytelnej dokumentacji modułu do której można go odesłać ("przeczytaj docs modułu `auth` zanim go rozbudujesz").

Istniejące mechanizmy tej luki nie pokrywają:
- `update-ai-context` skanuje **kod** → CLAUDE.md (konwencje, broad/shallow, auto-injected). Gubi "dlaczego" (intencję/decyzje), które żyje w planning docs. Trigger: manual bootstrap/refresh całego projektu.
- `explain` → ephemeral raport HTML jednej zmiany (onboarding człowieka), nie trwała dokumentacja modułu.
- planning-*.md → intencja PRZED implementacją (draft), może rozjechać się z finalnym kodem.

Dodatkowo: ten feature oraz świeżo zaplanowany `try-learn-skill` (patrz `planning-learned-skills.md`) **oba** odpalają się na końcu `implement` przed commitem, z tych samych artefaktów. Potrzebny spójny punkt wejścia — **faza harvest**.

## Użytkownicy
- **Bezpośredni (czytelnik docs):** agent AI rozbudowujący istniejący moduł — czyta docs modułu jak nowy developer ("jak to działa, gdzie zacząć, na co uważać").
- **Operator:** deweloper kończący feature — odpala harvest przed commitem.
- **Pośrednio:** człowiek-maintainer, który też skorzysta z czytelnej dokumentacji modułu.

## Oczekiwane zachowanie

**Faza harvest (koniec `implement`, przed commit):**
1. `implement` na końcu **delikatnie sugeruje** odpalenie `harvest` (best-effort nudge; zapomnienie nie jest problemem).
2. Deweloper odpala `/absolutpowers:harvest @absolutpowers/feature/tasks-{slug}.md`.
3. `harvest` sekwencyjnie orkiestruje (każdy sub-krok zachowuje swój własny gate):
   - `try-learn-skill` → ekstrakcja reużywalnej procedury (human gate — patrz planning-learned-skills).
   - `document-feature` → aktualizacja/utworzenie docs modułu (auto-write + potwierdzenie mapowania modułu).
4. Deweloper przegląda wynik w git diff przed commitem.

**`document-feature` (wywoływany przez harvest lub samodzielnie):**
1. Czyta artefakty feature'a: `planning-{slug}.md` (intencja/decyzje) + `tasks-{slug}.md` (+ phase files) + **git diff** (prawda o kodzie).
2. Wykrywa które **moduły** feature dotknął (detekcja: CLAUDE.md/patterns.md → fallback heurystyka ze ścieżek).
3. **Pokazuje wykryte mapowanie plik→moduł** i czeka na potwierdzenie/korektę (jedyny twardy gate — zła detekcja = docs w złym pliku).
4. Dla każdego dotkniętego modułu: NEW (utwórz `docs/modules/{moduł}.md`) lub UPDATE (inteligentny merge w istniejący — przepisuje sekcje żeby odzwierciedlały AKTUALNY stan).
5. **Auto-write** treści (bez dodatkowego promptu — git diff przed commit = naturalny gate).
6. Stempluje doc: `last-updated` + `last-commit`.

## Wybrane rozwiązanie

Dwa nowe skille w obu drzewach (claude + codex):
- **`document-feature`** — generator/updater dokumentacji modułu z artefaktów feature'a. Mięso.
- **`harvest`** — cienki orkiestrator fazy harvest: `try-learn-skill` → `document-feature`.

Plus edit `implement` (nudge → harvest) i rekoncyliacja nudge'a w planning-learned-skills.

### Jednostka dokumentacji: per-MODUŁ
Jeden plik = jeden moduł: `docs/modules/{moduł}.md`. Feature dotykający 3 modułów → aktualizuje 3 docs. Uzasadnienie: use case = "przeczytaj docs **modułu** przed rozbudową" → jednostka to moduł, nie feature. Per-feature fragmentowałby wiedzę (AI musiałby zbierać "jak działa auth" z 5 plików feature). Per-moduł naturalnie kumuluje — każdy feature dokłada do żywego dokumentu modułu.

### Detekcja modułu (diff → moduł)
**Primary:** czytaj `CLAUDE.md` (`## Project Structure`) / `patterns.md` z update-ai-context — źródło prawdy o strukturze modułów (już istnieje w dojrzałym projekcie).
**Fallback:** heurystyka ze ścieżek diffa (top-level katalog pod `src/` lub pakiet/namespace; `src/auth/*` → moduł `auth`).
**Safety:** wykryte mapowanie plik→moduł zawsze **pokazywane do potwierdzenia** (nawet przy auto-write treści) — zła detekcja = docs w złym pliku, czego git diff nowego pliku nie wyłapie.

### NEW vs UPDATE: inteligentny merge
Gdy doc modułu istnieje, agent **przepisuje odpowiednie sekcje** żeby odzwierciedlały aktualny stan modułu po feature. Doc zostaje spójny "jak moduł działa teraz", nie stos changelogów. Append-changelog odrzucony (odtwarza fragmentację w jednym pliku; historia = od tego jest git + ADR). Ryzyko przekłamania mityguje: źródłem jest aktualny kod (diff), nie pamięć + git diff docu do wglądu przed commit.

### Gate: auto-write + diff review (różnicowany od learned-skills)
`document-feature` **pisze od razu** do `docs/modules/` — git diff przed commit (trigger = przed commit) jest naturalną powierzchnią review. Docs **nie wykonują się** (≠ learned-skills, gdzie zły skill auto-szkodzi → tam pełny human gate uzasadniony). Różnicowanie gate'ów = różne ryzyko (non-exec docs vs exec skill). Jedyne twarde potwierdzenie: **mapowanie plik→moduł**.

### Struktura docu modułu (proponowana)
```markdown
# Moduł: {nazwa}

<!-- doc-meta
last-updated: YYYY-MM-DD
last-commit: <sha>
-->

## Przegląd
[Co to jest, za co odpowiada, granice modułu]

## Jak działa
[Kluczowe komponenty + przepływ. Zorientowane na AI-jako-dev: gdzie zacząć]

## Kluczowe decyzje (dlaczego)
[Z planning rationale — czemu tak, nie inaczej; istotne tradeoffy]

## Punkty integracji
[Zależności, API/kontrakty, eventy, co woła / co woła ten moduł]

## Mapa plików
- `ścieżka` — [rola]

## Pułapki / edge cases
[Na co uważać przy rozbudowie]
```

### Stamp świeżości
`doc-meta` w ciele (komentarz HTML, jak w learned-skills — unik ryzyka loadera): `last-updated` + `last-commit`. Przyszłe tooling/AI wykryje drift (ile commitów w module od `last-commit` → docs mogą być nieaktualne).

### harvest — orkiestrator
Cienki skill. Argument = ścieżka do feature (tasks/planning). Sekwencja: `try-learn-skill` → `document-feature`, każdy zachowuje własny gate. Jeden nudge w `implement` (zamiast dwóch osobnych). W obu drzewach.

**Rekoncyliacja z planning-learned-skills:** nudge w `implement` opisany tam jako "→ try-learn-skill" zmienia się na "→ harvest". Do uwzględnienia przy implementacji (jeśli learned-skills wdrożone wcześniej — zaktualizować nudge; jeśli równolegle — od razu nudge → harvest).

### Uzasadnienie
- **Wypełnia realną lukę:** deep, per-moduł, z intencji (planning) + prawdy (diff), w cyklu implement. Żaden istniejący skill tego nie robi (update-ai-context = kod-scan/broad; explain = ephemeral; planning = pre-impl draft).
- **Spójność z platformą:** brak runtime loopa → nudge + manual harvest, jak learned-skills.
- **Świeżość przez cykl:** regeneracja na końcu każdego implement = docs nadążają za kodem (główne ryzyko doc-rot mitygowane).
- **Różnicowany gate:** docs non-exec → lżejszy gate niż exec learned-skills; mniej tarcia bez utraty bezpieczeństwa (git diff + module-mapping confirm).
- **MNIEJ=WIĘCEJ:** harvest cienki; brak hybryd/changelogów/sekcji historii (git je pokrywa).

### Rozważane alternatywy
- **Rozszerzenie update-ai-context zamiast nowego skilla:** inna oś (kod-scan/broad/auto-injected vs planning+diff/deep/on-demand), inny trigger i granularność → przeciążenie jednego skilla. Odrzucone — nowy `document-feature`.
- **Wzbogacony nested CLAUDE.md zamiast docs/:** auto-ładowany, ale deep docs zawsze injected = bloat kontekstu. Odrzucone — on-demand docs/.
- **Per-feature docs (docs/features/{slug}.md):** prosto, zero scope-detection, ale fragmentuje wiedzę o module. Odrzucone — per-moduł.
- **Append-changelog UPDATE:** bezpieczny, ale puchnie w stos logów = fragmentacja w pliku. Odrzucone — inteligentny merge.
- **Pełny human gate dla docs:** redundantny z pre-commit git diff; docs non-exec. Odrzucone — auto-write + mapping confirm.
- **Dwa nudge (try-learn + document osobno):** szum na końcu implement. Odrzucone — jeden harvest closeout.
- **Osobny planning dla harvest:** anemiczny (cienki orkiestrator bez wartości w oderwaniu). Odrzucone — wspólny planning z document-feature.

## Zakres

### In scope
- Nowy skill `document-feature` (claude + codex): input planning+tasks+diff → docs/modules/{moduł}.md, detekcja modułu (CLAUDE.md/patterns.md → fallback ścieżki), mapping confirm, NEW vs UPDATE (inteligentny merge), auto-write, stamp `doc-meta`.
- Nowy skill `harvest` (claude + codex): orkiestrator try-learn-skill → document-feature, każdy własny gate.
- Edit `implement/SKILL.md` (oba drzewa): nudge → harvest przy completion report.
- Rekoncyliacja nudge'a w planning-learned-skills (→ harvest zamiast → try-learn-skill).
- Struktura docu modułu (szablon w treści document-feature).
- Docs: README sekcja "Harvest phase" + rozróżnienie document-feature vs update-ai-context vs explain; pozycja w pipeline.
- Bump wersji (minor) w obu plugin.json (zgodne).

### Out of scope
- **Decay/archive docs** — docs żyją z modułem; nie wygasają jak learned-skills. (gdyby moduł usunięty → osobna kwestia, później).
- **Auto-detekcja drift / przypominanie o nieaktualnych docs** — `doc-meta` umożliwia, ale tooling wykrywający to osobny feature.
- **Renderowanie docs (HTML/site)** — docs to markdown w repo.
- **Migracja istniejących docs** — start od nowych/dotykanych modułów.
- harvest jako hook settings.json (to nudge prompt-level, nie hook).

## Plan implementacji
1. **`document-feature` (Claude)** — `claude/skills/document-feature/SKILL.md`: frontmatter (name, description+TRIGGER, allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/docs/modules/**), argument-hint), ciało: kroki input → detekcja modułu (CLAUDE.md/patterns.md→fallback) → mapping confirm → NEW/UPDATE inteligentny merge → auto-write → stamp.
2. **`document-feature` (Codex)** — `codex/skills/document-feature/SKILL.md`: bez allowed-tools/argument-hint.
3. **`harvest` (Claude)** — `claude/skills/harvest/SKILL.md`: orkiestrator, argument = feature path, sekwencja try-learn-skill → document-feature.
4. **`harvest` (Codex)** — `codex/skills/harvest/SKILL.md`.
5. **Edit `implement` (Claude + Codex)** — nudge → harvest przy completion report (po AC Fulfillment, przed Step 8/Begin — analogicznie do learned-skills).
6. **Rekoncyliacja** — update nudge w planning-learned-skills (i jego przyszłej implementacji) na → harvest.
7. **Szablon docu modułu** — udokumentuj w treści document-feature (sekcje + doc-meta).
8. **Docs** — README "Harvest phase"; rozróżnienie 3 mechanizmów dokumentacji.
9. **Wersja** — bump minor w obu plugin.json.
10. **Drift check** — `./scripts/diff-skills.sh` (różnice tylko oczekiwane: frontmatter Claude-only).

## Pliki do zmodyfikowania / utworzenia
- `claude/skills/document-feature/SKILL.md` — NOWY (pełny frontmatter; Write scope = TARGET project `docs/modules/`, nie repo).
- `codex/skills/document-feature/SKILL.md` — NOWY (bez allowed-tools/argument-hint).
- `claude/skills/harvest/SKILL.md` — NOWY.
- `codex/skills/harvest/SKILL.md` — NOWY.
- `claude/skills/implement/SKILL.md` — nudge → harvest (po AC Fulfillment Report, przed Step 8/`## Begin`).
- `codex/skills/implement/SKILL.md` — nudge → harvest (mirror).
- `absolutpowers/feature/planning-learned-skills.md` — rekoncyliacja nudge (→ harvest).
- `README.md` — sekcja Harvest phase + rozróżnienie document-feature/update-ai-context/explain + pipeline.
- `CLAUDE.md` (repo) — wzmianka o harvest phase w architekturze pipeline (opcjonalnie).
- `claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json` — bump wersji (identyczna).

## Edge cases i ryzyka
- **Feature dotyka wielu modułów:** mapping confirm pokazuje wszystkie; document-feature pętli po modułach (NEW/UPDATE każdy).
- **Płaska/nietypowa struktura projektu:** heurystyka ścieżek zgaduje słabo → mapping confirm ratuje (potwierdzasz/korygujesz).
- **Brak CLAUDE.md/patterns.md:** fallback na heurystykę ścieżek; działa, mniej precyzyjnie.
- **Brak `docs/modules/`:** document-feature tworzy katalog przy 1. zapisie.
- **Diff scommitowany/zmergowany przy późnym odpaleniu:** obsłuż `vs master` i diff konkretnego commita (jak w learned-skills).
- **Inteligentny merge gubi treść:** mityguje git diff docu (widzisz co zniknęło) + źródło = aktualny kod. Ostrzeżenie w treści skilla: "nie usuwaj wiedzy nieobjętej diffem, tylko aktualizuj dotknięte sekcje".
- **Zła detekcja modułu → docs w złym pliku:** główne ryzyko, dlatego mapping confirm jest twardym gate'em mimo auto-write reszty.
- **Codex parity:** oba skille działają w obu drzewach (skille, nie agenty/commands). `diff-skills.sh` pilnuje driftu.
- **Kolejność w harvest:** try-learn-skill → document-feature (niezależne, low-stakes; ustalona dla determinizmu).
- **harvest gdy jeden sub-skill nieobecny:** harvest powinien gracefully pominąć brakujący (np. projekt nie chce learned-skills) — sprawdź dostępność, nie wywalaj się.
- **Loader CC a doc-meta:** trzymamy w ciele (HTML comment), nie frontmatter docu (docs/ nie jest skillem, ale konsekwentnie i bezpiecznie).

## Pytania otwarte
- **Granularność "modułu" w monorepo / wielojęzycznym projekcie:** top-level pakiet wystarczy, czy potrzebne zagnieżdżone docs? (na start: płaskie docs/modules/{moduł}.md).
- **Drift tooling:** osobny skill/komenda czytający `doc-meta` i raportujący nieaktualne docs — przyszły feature?
- **harvest a samodzielne odpalenie sub-skilli:** czy document-feature/try-learn-skill mają być też wywoływalne solo (poza harvest)? Zakładam TAK (harvest = wygoda, nie jedyna droga).
- **Nazwa modułu vs nazwa pliku docu:** sanityzacja (slug) gdy nazwa pakietu ma znaki specjalne.
- **Promocja świeżości:** czy `last-commit` to HEAD przed commitem czy po? (prawdopodobnie agent stempluje bieżący HEAD; commit z docs nastąpi po — drobny rozjazd 1 commita, akceptowalny).

## Notatki z dyskusji
Decyzje zablokowane w sesji feature-discuss (2026-06-17):

| Decyzja | Wybór |
|---|---|
| Forma | nowy skill `document-feature` (nie rozszerzenie update-ai-context, nie nested CLAUDE.md) |
| Odbiorca | AI agent jak nowy developer ("czytaj docs modułu przed rozbudową") |
| Input | planning + tasks + git diff; NIE konwersacja (subagenci), NIE transcript (parity) |
| Jednostka docs | per-MODUŁ (`docs/modules/{moduł}.md`), nie per-feature |
| Detekcja modułu | CLAUDE.md/patterns.md (primary) → heurystyka ścieżek (fallback) → mapping confirm (safety) |
| NEW vs UPDATE | inteligentny merge (żywy "jak działa teraz"), nie append-changelog |
| Gate | auto-write + pre-commit git diff review; twardy gate tylko na mapping plik→moduł |
| Stamp | `doc-meta` w ciele: last-updated + last-commit |
| harvest | nowy cienki orkiestrator, try-learn-skill → document-feature, każdy własny gate; jeden nudge w implement |
| Organizacja | wspólny planning (harvest + document-feature); learned-skills osobno |
| Cross-tree | claude + codex |

Powiązane: `planning-learned-skills.md` (try-learn-skill — pierwszy element fazy harvest; PASS). Inspiracja całości: Nous Research Hermes learning loop, zaadaptowany do stateless platformy + filozofii jawnych gate AbsolutPowers.
