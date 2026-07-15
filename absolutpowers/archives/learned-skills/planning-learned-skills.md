# Feature: Learned Skills — Auto-Skill-Extraction (Hermes-inspired learning loop)

## Status
Draft — 2026-06-17

## Problem
AbsolutPowers ma tylko **statyczne, ręcznie pisane skille** (feature-discuss, implement, review…) opisujące *uniwersalny* lifecycle. Brakuje mechanizmu utrwalania **procedur specyficznych dla konkretnej aplikacji** nad którą agent pracuje — powtarzalnych sekwencji kroków typu "jak w TYM projekcie dodać nowy endpoint CRUD", "jak podpiąć nowy event handler". Dziś taka wiedza ginie po zakończeniu zadania; przy podobnym zadaniu agent rozumuje od zera.

Inspiracja: **Nous Research Hermes learning loop** — agent ekstrahuje udane wzorce pracy do reużywalnych "Skill" plików (Markdown) i ładuje je przy podobnych przyszłych zadaniach zamiast rozumować od zera. Chcemy ten compounding, ale dopasowany do realiów platformy (Claude Code / Codex są stateless per-sesja — brak runtime loopa) i do filozofii AbsolutPowers (jawne quality gates, nie ciche self-write).

## Użytkownicy
- **Bezpośredni:** deweloper używający AbsolutPowers w swoim projekcie (target project), który wielokrotnie wykonuje podobne zadania w tej samej aplikacji.
- **Pośredni:** agent (Claude Code / Codex) wykonujący kolejne zadania — ładuje learned-skille i wykonuje powtarzalne procedury szybciej/spójniej.

## Oczekiwane zachowanie
1. Deweloper kończy pracę nad feature'em (np. przez `implement`).
2. `implement` na końcu **delikatnie sugeruje** odpalenie `try-learn-skill` (best-effort nudge; zapomnienie nie jest problemem).
3. Deweloper odpala `/absolutpowers:try-learn-skill @absolutpowers/feature/tasks-{slug}.md`.
4. Skill czyta artefakty feature'a (planning + tasks + implementation-context.md) jako **proces** oraz git diff jako **weryfikację efektu**.
5. Wykrywa **generalizowalną procedurę** — sekwencję kroków powtarzalną na innym zadaniu tego typu (nie one-off specyficzny dla tego featue).
6. Czyta istniejące `.claude/skills/learned/*` i podejmuje decyzję **NEW vs UPDATE**; sprawdza kolizję ze skillami statycznymi.
7. **Proponuje** treść SKILL.md (NEW / UPDATE / SKIP z uzasadnieniem) i **czeka na akceptację** (human gate).
8. Po akceptacji zapisuje do `{target-project}/.claude/skills/learned/{name}/SKILL.md`.
9. Skill jest **natychmiast aktywny** — Claude Code auto-wykrywa go po `description` przy przyszłych zadaniach.

## Wybrane rozwiązanie

Nowy skill **`try-learn-skill`** (manual command, human-approve gate) + soft nudge w `implement`. Decay/archive jako osobna **Faza 2**.

### Rozróżnienie vs istniejący `patterns.md` (KLUCZOWE — nie duplikuj)

| | `patterns.md` (update-ai-context, istnieje) | learned skills (ten feature) |
|---|---|---|
| Co utrwala | wzorce **struktury kodu** (Repository, Service, Factory) | wzorce **procedury/pracy** agenta |
| Forma | opisowy dokument (reference, czytany przez generate-tasks/implement) | **wywoływalny** SKILL.md (auto-detekcja przez CC) |
| Oś | jak aplikacja jest **zbudowana** | jak **wykonać** powtarzalne zadanie |
| Próg | 3+ wystąpień + code reference (automat) | generalizowalność + human gate (manual) |

Learned skills uczą *czynności*, nie *struktury*. Uzupełniają patterns.md, nie zastępują.

### Input source (co czyta `try-learn-skill`)

Argument = ścieżka do feature (tasks/planning), spójnie z `generate-tasks` i `implement`.

```
try-learn-skill @absolutpowers/feature/tasks-{slug}.md
  proces:     tasks-{slug}.md (+ phase files w tasks-{slug}/)   ← zdekomponowany reasoning pattern
              planning-{slug}.md                                 ← intencja / decyzje (DLACZEGO)
              implementation-context.md                          ← decyzje/handoffy workerów
  weryfikacja: git diff (vs master/last commit)                 ← EFEKT (kod), grounding
```

**Dlaczego NIE konwersacja sesji:** orchestrated `implement` odpala subagentów (implementation-worker) w izolowanych kontekstach — główna sesja widzi tylko ich finalne podsumowania, nie kroki. Proces żyje w artefaktach AbsolutPowers, nie w konwersacji. Bonus: konwersacja może być dodatkowym sygnałem gdy praca była solo (bez subagentów), ale nigdy nie jest podstawą.

**Dlaczego NIE transcript JSONL:** parsowanie historii łamie cross-tree parity (Codex ma inny format/lokalizację), dodaje złożoność, zero zysku gdy artefakty już strukturyzują proces.

### Kwalifikacja (co warte utrwalenia)

**Generalizowalna procedura** — sekwencja kroków którą dałoby się powtórzyć na INNYM zadaniu tego typu. Odrzuca one-offy specyficzne dla tego featue. Ostateczny osąd należy do człowieka w gate.

Nie wymagamy "3+ wystąpień" w jednym runie (jeden feature = jedna instancja). Powtarzalność śledzona **przez katalog learned/ across runy**: 1. spotkanie → `confidence: candidate`; 2. spotkanie (UPDATE) → promocja do `established`. Collision-check = jednocześnie detektor powtórzeń.

### Confidence i staging

Świeży learned skill (1. spotkanie) ląduje **od razu aktywny** w `.claude/skills/learned/`. Uzasadnienie: przeszedł human gate (jest zweryfikowany, tylko nie "widziany 2x"). `confidence` to **pole metadanych (sygnał dojrzałości), nie blokada** — w Claude Code nie istnieje "draft skill którego CC ignoruje", każdy skill w `.claude/skills/` jest auto-wykrywany. Staging poza katalogiem odrzucony (duplikacja katalogów + opóźnia wartość; candidate byłby bezużyteczny do 2. spotkania, które może nie nadejść).

### Collision handling

Rozróżnij źródło kolizji:
- **vs skill STATYCZNY** (feature-discuss, implement, review…) → **SKIP**, nie twórz. Statyczne są kurowane, wygrywają. Zgłoś: "to już robi skill X, pomijam".
- **vs inny LEARNED skill** → ścieżka **UPDATE** (merge/refine istniejący + bump confidence), nie twórz duplikatu.

Podział: statyczne = nietykalne, learned = ewoluują. Gate i tak pokazuje NEW/UPDATE/SKIP do akceptacji.

### Format learned SKILL.md

Standardowa struktura skilla AbsolutPowers + blok metadanych w **ciele** (nie we frontmatter — unik ryzyka że loader CC zachłyśnie się nieznanymi kluczami; ciało jest parsowalne przez NEW-vs-UPDATE).

```markdown
---
name: learned-{descriptive-kebab}
description: >
  [co ten skill robi w tym projekcie] +
  TRIGGER when: [konkretne sygnały dla auto-detekcji CC]
allowed-tools: [...]        # Claude only — omit dla Codex
argument-hint: "[...]"      # Claude only — opcjonalnie
---

<!-- learned-meta
origin: learned
source-feature: {slug}
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
confidence: candidate | established
occurrences: N
-->

# {Tytuł} — Learned Skill

[Procedura: kroki, narzędzia, decyzje, odwołania do plików/wzorców projektu]
```

`name` z prefiksem `learned-` → namespace, brak kolizji nazw ze statycznymi.

### Soft nudge w `implement`

Tekst (nie hook settings.json) w `implement/SKILL.md`, przy finalnym raporcie completion (sekcja po "AC Fulfillment Report" / Step 7B), np.:

> Praca skończona. Rozważ `/absolutpowers:try-learn-skill @absolutpowers/feature/tasks-{slug}.md` — sprawdzę czy z tej pracy da się utrwalić reużywalny learned skill.

Best-effort, prompt-level. Brak konsekwencji jeśli agent zapomni.

> **Rekoncyliacja (2026-06-18):** ten nudge został zastąpiony przez fazę
> **harvest** (patrz `planning-harvest-docs.md`). `implement` nuduje teraz
> `/absolutpowers:harvest`, które uruchamia `try-learn-skill` → `document-feature`
> (każde z własnym gate). Oryginalne uzasadnienie nudge'a pozostaje aktualne —
> zmienił się tylko punkt wejścia (harvest zamiast bezpośrednio try-learn-skill).

### Uzasadnienie
- **Reuse istniejących prymitywów:** artefakty feature'a (tasks/planning/context) jako input — zero nowego parsowania, deterministyczne, działa identycznie w obu drzewach.
- **Spójność z filozofią:** human gate zamiast cichego self-write (główna słabość Hermesa = self-eval reward hacking → poisoning). AbsolutPowers = jawne gate.
- **Realizm platformy:** brak runtime loopa → manual command + nudge symuluje pętlę bez fikcji "działa w tle".
- **MNIEJ=WIĘCEJ:** jeden skill + edit w implemencie dla Fazy 1; decay odłożony.

### Rozważane alternatywy
- **Hook po sesji (auto-ekstrakcja):** najbliżej Hermesa, ale szum + koszt tokenów co sesję + brak kontroli. Odrzucone na rzecz manual+nudge.
- **Auto-write bez gate / pełna autonomia Hermes-style:** maks compounding, ale ryzyko skill-poisoning bez human eval. Odrzucone.
- **Transcript JSONL jako input:** najbogatszy proces, ale łamie parity + złożoność. Odrzucone.
- **Staging candidate poza .claude/skills/:** "prove before reuse", ale duplikacja katalogów + opóźnia wartość. Odrzucone.
- **Rozszerzenie update-ai-context zamiast nowego skilla:** inna oś (struktura vs procedura), pomieszanie odpowiedzialności. Odrzucone — osobny skill.

## Zakres

### In scope (Faza 1)
- Nowy skill `try-learn-skill` w obu drzewach (`claude/skills/`, `codex/skills/`).
- Input: planning + tasks + implementation-context.md + git diff (argument = ścieżka).
- Logika: detekcja generalizowalnej procedury → read `.claude/skills/learned/*` → NEW vs UPDATE → collision-check (statyczne SKIP / learned UPDATE) → propose → human gate → zapis.
- Format learned SKILL.md z blokiem `learned-meta` (confidence/occurrences/source/dates).
- Soft nudge w `implement/SKILL.md` (oba drzewa).
- Dokumentacja: README + docs, rozróżnienie vs patterns.md.
- Bump wersji (minor) w obu plugin.json.

### Out of scope (Faza 2 — osobny planning)
- **Decay/archive** nieużywanych learned-skilli (~7d) — wymaga ledgera użycia.
- **Ledger użycia** (tracking wywołań) — CC nie liczy natywnie.
- Auto-refinement skilli w runtime (Hermes self-improve) — wymaga sygnału użycia.
- Metryki/analytics learned-skilli.

### Out of scope (całkowicie)
- Runtime background loop (platforma nie wspiera).
- Auto-write bez human gate.
- Embeddingowe podobieństwo (na start: heurystyka + osąd agenta w gate).

## Plan implementacji
1. **`try-learn-skill` SKILL.md (Claude)** — `claude/skills/try-learn-skill/SKILL.md`: frontmatter (name, description+TRIGGER, allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**), argument-hint), ciało: kroki 1-9 (input → detekcja → read learned → NEW/UPDATE/collision → propose → gate → write).
2. **`try-learn-skill` SKILL.md (Codex)** — `codex/skills/try-learn-skill/SKILL.md`: to samo bez `allowed-tools`/`argument-hint`.
3. **Edit `implement` (Claude)** — dodaj soft nudge przy finalnym completion report.
4. **Edit `implement` (Codex)** — to samo.
5. **Format learned SKILL.md** — udokumentuj szablon + blok `learned-meta` w treści `try-learn-skill` (jako wzorzec który skill generuje).
6. **Docs** — README sekcja "Learned Skills", rozróżnienie vs patterns.md; `docs/` jeśli pasuje.
7. **Wersja** — bump minor w `claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json` (zgodne).
8. **Drift check** — `./scripts/diff-skills.sh` potwierdza że różnice claude/codex to tylko oczekiwane (frontmatter Claude-only).

## Pliki do zmodyfikowania / utworzenia
- `claude/skills/try-learn-skill/SKILL.md` — NOWY (skill, pełny frontmatter).
- `codex/skills/try-learn-skill/SKILL.md` — NOWY (skill, bez allowed-tools/argument-hint).
- `claude/skills/implement/SKILL.md` — soft nudge przy completion report.
- `codex/skills/implement/SKILL.md` — soft nudge (mirror).
- `README.md` — sekcja Learned Skills + rozróżnienie vs patterns.md + pozycja w pipeline.
- `docs/getting-started.md` (lub nowy) — jak używać try-learn-skill (opcjonalnie).
- `claude/.claude-plugin/plugin.json` — bump wersji.
- `codex/.codex-plugin/plugin.json` — bump wersji (identyczna).
- `CLAUDE.md` (repo) — wzmianka o learned skills w architekturze pipeline (opcjonalnie).

## Edge cases i ryzyka
- **Pusty/słaby sygnał:** feature za mały / one-off → skill raportuje "nic generalizowalnego do utrwalenia" i kończy bez zapisu (nie wymuszaj skilla).
- **Kolizja nazw:** prefiks `learned-` + collision-check chronią; przy UPDATE zachowaj historię (`occurrences++`, `last-updated`).
- **Brak `.claude/skills/learned/`:** skill tworzy katalog przy 1. zapisie.
- **Loader CC a metadane:** trzymamy `learned-meta` w ciele (komentarz HTML), nie we frontmatter → zero ryzyka że CC odrzuci skill. (Do weryfikacji w implementacji: czy CC toleruje nadmiarowe klucze frontmatter — jeśli tak, można rozważyć przeniesienie; na start ciało = bezpiecznie.)
- **Codex parity:** `try-learn-skill` to skill (działa w obu drzewach, nie wymaga agenta/command). `diff-skills.sh` pilnuje driftu.
- **Skill-poisoning (główne ryzyko Hermesa):** mitygowane human gate + `confidence` + ścieżką UPDATE/SKIP. Zły learned skill → następny run go poprawi (UPDATE) lub Faza 2 (decay) zarchiwizuje przy braku użycia.
- **Retrieval collision z runtime:** learned-skille mogą nachodzić description'em na statyczne przy auto-detekcji CC → wymóg precyzyjnych, wąskich `TRIGGER when` w generowanym description (skill musi to egzekwować przy generacji).
- **Argument w nowej sesji:** gdy odpalasz później, artefakty feature'a wciąż na dysku → działa; git diff może być już scommitowany/zmergowany → skill obsłuży zarówno `vs master` jak i diff konkretnego commita.

## Pytania otwarte
- **Faza 2 — ledger źródło:** hook logujący wywołania (`.claude/skills-ledger.json`) vs parsowanie historii CC (jak `rtk discover`). Wpływa na parity.
- **Faza 2 — decay TTL:** flat 7d vs count-aware (skill z dużą historią użyć = dłuższy TTL, ratuje sezonowe procedury typu "deploy raz/mies").
- **Generowany description — egzekwowanie precyzji TRIGGER:** czy `try-learn-skill` ma walidować że nowy description nie nachodzi zbyt szeroko na istniejące (statyczne+learned) przed propozycją?
- **Confidence promote — próg:** czy 2. spotkanie = automatycznie `established`, czy potrzebne ≥N spotkań?
- **Scope learned skilli:** tylko project-local (`.claude/skills/learned/`) — potwierdzone. Czy kiedyś global/user-level? (poza zakresem teraz).

## Uwagi implementacyjne (z review-plan gate)
Nieblokujące, do uwzględnienia przy generate-tasks:
1. **`Write` permission celuje w TARGET project, nie repo:** `allowed-tools` Claude musi mieć `Write(**/.claude/skills/learned/**)` wskazujący na `.claude/` *konsumującego* projektu, nie `{absolutpowers-repo}/.claude/`. Analogicznie do `feature-discuss` które scope'uje `Write(**/absolutpowers/feature/**/*.md)`, ale inny wzorzec.
2. **Brakujący katalog learned/:** w świeżym projekcie `.claude/skills/learned/` nie istnieje. Ciało SKILL.md musi obsłużyć Glob na nieistniejącej ścieżce bez zatrzymania (traktuj brak jako "zero learned skilli" → zawsze NEW).
3. **Dokładny punkt wstawienia nudge:** w `implement/SKILL.md` wstaw po bloku AC Fulfillment Report, przed Step 8 (review gate) / `## Begin`. Task ma przypiąć dokładne miejsce, zero dwuznaczności.

## Notatki z dyskusji
Decyzje zablokowane w sesji feature-discuss (2026-06-17):

| Decyzja | Wybór |
|---|---|
| Trigger | manual command `try-learn-skill` + soft nudge w `implement` (best-effort) |
| Gate | human approve (propose → akceptacja → zapis) |
| Input source | planning + tasks + implementation-context.md + git diff; NIE konwersacja (subagenci), NIE transcript (parity) |
| Kwalifikacja | generalizowalna procedura (nie one-off), osąd człowieka w gate |
| Powtarzalność | śledzona across runy przez katalog learned/ (candidate → established przy UPDATE), nie 3+ w jednym runie |
| Staging | od razu aktywny w `.claude/skills/learned/`; confidence = pole metadanych, nie blokada |
| Collision | statyczny → SKIP (nietykalne); learned → UPDATE (ewoluują) |
| Decay | Faza 2, wymaga ledgera — odłożone |
| Cross-tree | claude + codex (skill w obu, nudge w obu) |

Inspiracja: Nous Research Hermes learning loop (Task Execution → Outcome Evaluation → Skill Extraction → Skill Retrieval & Refinement). Świadomie odeszliśmy od auto-self-write (ryzyko poisoning) na rzecz human gate, i od runtime loopa (platforma stateless) na rzecz manual+nudge.
