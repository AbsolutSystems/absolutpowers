# Tasks: Learned Skills — Auto-Skill-Extraction (try-learn-skill)

## Mode
single-file

## Project Context

**Source doc:** `./absolutpowers/feature/planning-learned-skills.md`

**Stack:** Brak kodu wykonywalnego. Plugin AbsolutPowers = pliki Markdown (SKILL.md) z YAML frontmatter, dwa równoległe drzewa: `claude/` (pełny: skills/agents/commands) i `codex/` (skills only). Treść dwujęzyczna: polski user-facing, angielski techniczny.

**Structure:**
- `claude/skills/{name}/SKILL.md` — skille Claude Code (mają `allowed-tools`, `argument-hint`)
- `codex/skills/{name}/SKILL.md` — skille Codex (BEZ `allowed-tools`, BEZ `argument-hint`)
- `claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json` — manifesty, wersja MUSI być zgodna
- `scripts/diff-skills.sh` — wykrywanie driftu claude vs codex
- `README.md`, `docs/` — dokumentacja

**Patterns:**
- Skill frontmatter: `name` (kebab-case), `description` (`>` blok z triggerami + "TRIGGER when:"), Claude dodaje `allowed-tools` i `argument-hint`
- Body po frontmatter = prompt w Markdown; `$ARGUMENTS` = argument użytkownika
- Propose → human gate → write: wzorzec z `feature-discuss` (pyta, czeka na akceptację) i `update-ai-context` (proponuje rules, czeka na potwierdzenie przed zapisem)
- Multi-faza z numerowanymi krokami: wzorzec z `update-ai-context` (PHASE 1/2/...) i `review`

**Conventions:**
- Skille: kebab-case nazwa katalogu = `name` we frontmatter
- Expected drift claude vs codex: TYLKO `allowed-tools` + `argument-hint` we frontmatter (+ ewentualne sekcje agent-loop). Reszta treści identyczna.
- Wersjonowanie SemVer: minor = nowy skill/feature. Obie wersje muszą się zgadzać.

**Verification commands:**
- Drift check: `./scripts/diff-skills.sh` (oraz `./scripts/diff-skills.sh --diff` dla pełnego diffa)
- Walidacja YAML frontmatter (każdy nowy/zmieniony SKILL.md):
  `python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" <plik>`
- Zgodność wersji: porównaj `version` w obu plugin.json (muszą być identyczne)

**Reference implementations:**
- `claude/skills/feature-discuss/SKILL.md` — wzorzec interaktywnego propose → gate (jak pytać, jak czekać na akceptację)
- `claude/skills/update-ai-context/SKILL.md` — wzorzec multi-faza + "propose draft, ask confirmation before saving" + reguła "pattern 3+ użyć z code reference"
- `claude/skills/review/SKILL.md` — wzorzec frontmatter z bogatym `allowed-tools` (scoped Write/Bash) i `argument-hint`
- `codex/skills/review/SKILL.md` — ten sam skill bez `allowed-tools`/`argument-hint` (wzorzec mirrora Codex)
- `claude/skills/implement/SKILL.md` — gdzie wstawić nudge (sekcja completion report, po "AC Fulfillment")

---

## Implementation Tasks

### Task 1: Utwórz `claude/skills/try-learn-skill/SKILL.md` (rdzeń)
**Status:** completed

**Create:**
- `claude/skills/try-learn-skill/SKILL.md`

**Modify:**
- None

**Description:**
Główny artefakt feature'a — skill ekstrahujący reużywalną procedurę z artefaktów zakończonego feature'a do wywoływalnego learned-skilla w target-project. To rdzeń; Task 2 to jego mirror dla Codex. Implementuje 9-krokowy flow z planning doc z human gate przed zapisem.

**Requirements:**
- **Frontmatter:**
  - `name: try-learn-skill`
  - `description:` blok `>` opisujący cel + `TRIGGER when:` z sygnałami PL/EN (np. "po zakończonej implementacji", "utrwal procedurę", "naucz się z tej pracy", "extract skill", "learn from this work", odpalany przez `harvest`)
  - `allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md)`
  - `argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"`
- **Body (prompt PL user-facing, terminy techniczne EN), kroki:**
  1. **Input:** czytaj `$ARGUMENTS` (ścieżka do feature). Wczytaj: `tasks-{slug}.md` (+ phase files w `tasks-{slug}/` jeśli orchestrated), `planning-{slug}.md`, `implementation-context.md` (jeśli istnieje). To PROCES. Dodatkowo `git diff` (vs master/main lub last commit) jako weryfikacja EFEKTU. Obsłuż brak części artefaktów gracefully.
  2. **Detekcja:** wykryj GENERALIZOWALNĄ procedurę — sekwencję kroków powtarzalną na INNYM zadaniu tego typu (nie one-off specyficzny dla tego featue). Jeśli nic generalizowalnego → zaraportuj "nic do utrwalenia" i zakończ BEZ zapisu.
  3. **Read existing:** `Glob` `.claude/skills/learned/**/SKILL.md` w target-project. **Obsłuż brak katalogu** (zero learned skilli → zawsze NEW, nie zatrzymuj się na pustym Glob).
  4. **NEW vs UPDATE:** porównaj wykrytą procedurę z istniejącymi learned-skillami. Podobny istnieje → ścieżka UPDATE (merge/refine + bump `occurrences`, `confidence: candidate→established` przy 2. spotkaniu). Brak → NEW (`confidence: candidate`).
  5. **Collision-check vs statyczne:** jeśli procedura nachodzi na skill STATYCZNY (feature-discuss, implement, review, generate-tasks, debug, update-ai-context, preboot...) → **SKIP**, zaraportuj "to już robi skill X, pomijam". Kolizja z innym LEARNED → ścieżka UPDATE (nie duplikuj).
  6. **Propose:** pokaż użytkownikowi proponowaną treść SKILL.md (NEW / UPDATE / SKIP z uzasadnieniem). **Czekaj na akceptację (human gate)** — wzorzec z feature-discuss.
  7. **Write (po akceptacji):** zapisz do `{target-project}/.claude/skills/learned/{name}/SKILL.md`. Utwórz katalog jeśli nie istnieje. `name` z prefiksem `learned-` (namespace).
- **Format generowanego learned SKILL.md** (skill MUSI generować dokładnie taki szablon):
  - Frontmatter: `name: learned-{descriptive-kebab}`, `description:` z wąskim, precyzyjnym `TRIGGER when:` (egzekwuj precyzję — nie może nachodzić szeroko na statyczne/inne learned), `allowed-tools` (Claude) / pominięte (gdy generujesz dla Codex — patrz uwaga parity), opcjonalnie `argument-hint`
  - Blok metadanych w **ciele** (komentarz HTML, NIE frontmatter — unik ryzyka loadera CC): `<!-- learned-meta\norigin: learned\nsource-feature: {slug}\ncreated: YYYY-MM-DD\nlast-updated: YYYY-MM-DD\nconfidence: candidate|established\noccurrences: N\n-->`
  - Body: procedura (kroki, narzędzia, decyzje, odwołania do plików/wzorców projektu)
- Egzekwuj wąskie `TRIGGER when:` w generowanym description (ryzyko retrieval-collision z auto-detekcją CC).
- **Uwaga write scope:** `Write` celuje w `.claude/` TARGET projektu (gdzie odpalany skill), nie w repo AbsolutPowers.

**Tests:**
- Frontmatter parsuje się jako YAML (`python3 -c ...` jw.) — `name`, `description`, `allowed-tools`, `argument-hint` obecne
- Body zawiera wszystkie 7 kroków flow + szablon learned SKILL.md z blokiem `learned-meta` w ciele
- Body explicytnie obsługuje: brak katalogu learned/, brak części artefaktów, SKIP przy kolizji ze statycznym, ścieżkę UPDATE z bump confidence
- Body zawiera human gate (czeka na akceptację przed Write)

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example:**
```yaml
---
name: try-learn-skill
description: >
  Ekstrahuje reużywalną procedurę z artefaktów zakończonego feature'a
  (planning + tasks + git diff) do wywoływalnego learned-skilla.
  TRIGGER when: po zakończonej implementacji, "utrwal procedurę",
  "naucz się z tej pracy", "extract skill", odpalany przez harvest.
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md)
argument-hint: "[ścieżka do tasks-*.md lub planning-*.md]"
---
```
Szablon generowanego learned skilla (fragment ciała):
```markdown
<!-- learned-meta
origin: learned
source-feature: csv-export
created: 2026-06-17
last-updated: 2026-06-17
confidence: candidate
occurrences: 1
-->
```

---

### Task 2: Utwórz `codex/skills/try-learn-skill/SKILL.md` (mirror Codex)
**Status:** completed

**Create:**
- `codex/skills/try-learn-skill/SKILL.md`

**Modify:**
- None

**Description:**
Mirror skilla z Task 1 dla drzewa Codex. Identyczny w treści POZA frontmatter: BEZ `allowed-tools` i BEZ `argument-hint` (Codex ich nie obsługuje). To jedyny oczekiwany drift wykrywany przez `diff-skills.sh`.

**Requirements:**
- Skopiuj treść z `claude/skills/try-learn-skill/SKILL.md`
- Usuń z frontmatter linie `allowed-tools:` i `argument-hint:`
- Zostaw `name` i `description` identyczne
- Body identyczny (włącznie z generowanym szablonem learned SKILL.md — uwaga: w opisie generacji wspomnij że dla Codex generowany learned skill też pomija `allowed-tools`/`argument-hint`)
- Żadnych innych różnic w treści

**Tests:**
- Frontmatter parsuje się jako YAML, zawiera `name` + `description`, NIE zawiera `allowed-tools` ani `argument-hint`
- `./scripts/diff-skills.sh --diff try-learn-skill` (lub pełny) pokazuje TYLKO różnicę frontmatter (allowed-tools/argument-hint), reszta identyczna

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 3: Dodaj nudge → try-learn-skill w `implement` (oba drzewa)
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/implement/SKILL.md`
- `codex/skills/implement/SKILL.md`

**Description:**
Soft, prompt-level nudge na końcu implementacji sugerujący utrwalenie procedury. Best-effort — brak konsekwencji gdy agent zapomni. NIE hook settings.json. Wstawiony przy finalnym completion report, po sekcji "AC Fulfillment", przed `## Begin` / Step 8 (review gate).

**Requirements:**
- W obu plikach znajdź sekcję finalnego completion report (po bloku "AC Fulfillment")
- Dodaj krótki tekst sugerujący: po zakończeniu wszystkich tasków rozważ `/absolutpowers:try-learn-skill @absolutpowers/feature/tasks-{slug}.md` — sprawdzi czy z tej pracy da się utrwalić reużywalny learned skill
- Zaznacz że to opcjonalne (best-effort), zapomnienie nie jest błędem
- **Identyczna treść w obu drzewach** (nudge nie zależy od platformy)
- **UWAGA rekoncyliacja:** ten nudge celuje w `try-learn-skill`. Feature `harvest` (planning-harvest-docs.md) PÓŹNIEJ zmieni go na `→ harvest`. Zostaw komentarz/notkę nie jest wymagany w pliku, ale w remarks zaznacz świadomość.

**Tests:**
- Oba `implement/SKILL.md` zawierają nudge w sekcji completion (po AC Fulfillment, przed Begin)
- Treść nudge identyczna w claude i codex
- `./scripts/diff-skills.sh` na `implement` — drift bez zmian (był differs z powodu allowed-tools; nudge identyczny nie dokłada nowego driftu)

**Implementation decisions / remarks:**
- Nudge wstawiony jako sekcja `### Optional: utrwal procedurę (best-effort)` w `## Output Format`, po bloku AC Fulfillment, przed `## Begin`. Identyczny w obu drzewach (potwierdzone `diff` → "Files are identical").
- ŚWIADOMOŚĆ rekoncyliacji: nudge celuje w `/absolutpowers:try-learn-skill`. Feature `harvest` (planning-harvest-docs.md) zmieni go później na `→ harvest`. Brak komentarza w pliku (zbędny), notka tylko tu.

---

### Task 4: Dokumentacja README + bump wersji
**Status:** completed

**Create:**
- None

**Modify:**
- `README.md`
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

**Description:**
Udokumentuj learned skills w README (sekcja + rozróżnienie vs patterns.md + pozycja w pipeline) i podbij wersję minor w obu manifestach (nowy skill = minor).

**Requirements:**
- README: dodaj sekcję "Learned Skills" opisującą `try-learn-skill` (manual command, human gate, .claude/skills/learned/, confidence/UPDATE)
- README: tabela/akapit rozróżnienia learned skills (procedura, wywoływalna) vs `patterns.md` (struktura kodu, opisowa) — przeciw duplikacji
- README: zaznacz pozycję w pipeline (po implement, opcjonalny krok utrwalania)
- Bump wersji: odczytaj bieżącą z `claude/.claude-plugin/plugin.json` (3.4.0) → podnieś minor → `3.5.0`
- Ustaw IDENTYCZNĄ wersję w obu plugin.json
- Sprawdź czy README ma listę skilli / pipeline diagram do zaktualizowania o try-learn-skill

**Tests:**
- README zawiera sekcję Learned Skills + rozróżnienie vs patterns.md
- `version` w obu plugin.json identyczna i = `3.5.0`
- JSON w obu plugin.json poprawny (`python3 -m json.tool <plik>`)

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 5: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- None

**Description:**
Uruchom weryfikację zintegrowanej zmiany: drift claude vs codex tylko oczekiwany, frontmatter/JSON poprawne, wersje zgodne.

**Requirements:**
- Drift check: `./scripts/diff-skills.sh` — `try-learn-skill` i `implement` różnią się TYLKO oczekiwanym driftem (allowed-tools/argument-hint w claude); nowy `try-learn-skill` obecny w obu drzewach (zero `missing in codex`/`missing in claude`)
- Walidacja YAML frontmatter nowych/zmienionych SKILL.md (try-learn-skill claude+codex, implement claude+codex):
  `python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1]).read().split('---')[1]); print('OK')" <plik>`
- Walidacja JSON: `python3 -m json.tool claude/.claude-plugin/plugin.json >/dev/null && python3 -m json.tool codex/.codex-plugin/plugin.json >/dev/null`
- Zgodność wersji: `version` identyczna w obu plugin.json
- Każdy intencjonalnie pominięty check zapisz jako `not applicable` z powodem
- NIE oznaczaj completed jeśli którykolwiek check pada

**Tests:**
- `./scripts/diff-skills.sh` — tylko oczekiwany drift, brak missing
- Wszystkie frontmattery parsują się jako YAML
- Oba plugin.json: poprawny JSON + zgodna wersja 3.5.0

**Implementation decisions / remarks:**
- Commands executed: `./scripts/diff-skills.sh`; YAML frontmatter parse na 4 plikach (try-learn-skill + implement, oba drzewa); `python3 -m json.tool` na obu plugin.json; porównanie `version`.
- Results:
  - Drift: `try-learn-skill (differs)` + `implement (differs)` — TYLKO oczekiwany drift (allowed-tools/argument-hint w claude). Body try-learn-skill byte-identyczny (potwierdzone `diff <(tail...)` → "BODY IDENTICAL"). Nudge w implement identyczny w obu drzewach. Zero `missing in codex` dla try-learn-skill.
  - `tech-lead-advisor (missing in claude)` — PRE-EXISTING codex-only skill, niezwiązany z tym feature'em (nie wprowadzony tu).
  - YAML: 4/4 OK. JSON: oba OK. Wersje: 3.5.0 == 3.5.0.
- Skipped checks: none. (Uwaga: `diff-skills.sh` nie przyjmuje argumentu nazwy skilla — Task 2 test sugerował `--diff try-learn-skill`; użyto pełnego `--diff` + bezpośredniego `diff` na plikach, równoważnie.)
- Setup: `pyyaml` nie był zainstalowany w env → `pip3 install pyyaml` przed walidacją YAML.

**Example:**
```bash
./scripts/diff-skills.sh
python3 -c "import sys,yaml; yaml.safe_load(open('claude/skills/try-learn-skill/SKILL.md').read().split('---')[1]); print('OK')"
python3 -m json.tool claude/.claude-plugin/plugin.json >/dev/null && echo "claude json OK"
python3 -m json.tool codex/.codex-plugin/plugin.json >/dev/null && echo "codex json OK"
```
