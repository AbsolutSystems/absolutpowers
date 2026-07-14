# Tasks: Faza 1 — feature-discuss ← brainstorming (fuzja mechaniki obry)

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-1-feature-discuss.md`
- Epic context: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
- ADR wspólny: `./docs/adr/2026-07-13-rewrite-to-unify-fuzja-obry.md`
- ADR lokalny: `./docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`

## Mode
orchestrated

## Project Context
**Stack:** Markdown (SKILL.md prompt), plugin wieloharnessowy (Claude/Codex/Pi), YAML frontmatter, host-agnostyczne drzewo `skills/`. Brak kodu wykonywalnego w scope — edycja czysto promptowa jednego pliku.

**Jedyny edytowany plik logiki:** `skills/feature-discuss/SKILL.md` (583 linie, host-agnostyczny, serwuje wszystkie harnessy). Metoda: **rewrite-to-unify** (nowa zunifikowana treść, nie append).

**Wszystkie fazy piszą TEN SAM plik** → łańcuch sekwencyjny (każda faza `Depends on` poprzednią), zero równoległości → brak konfliktów zapisu. Worker każdej fazy czyta bieżący stan SKILL.md + `implementation-context.md`.

**Assety companion (już w repo, MIT — bez zmian treści):**
- `skills/feature-discuss/visual-companion.md` — vendorowany guide EN (read-only w tej fazie, staje się tylko odwoływany).
- `skills/feature-discuss/companion-scripts/{start-server.sh,stop-server.sh,server.cjs,frame-template.html,helper.js}`.

**Kontekst już domknięty poza tym planem (NIE rób taska):**
- ADR lokalny fazy istnieje (`docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`).
- Status Fazy 1 w `planning-main.md` = już „Zaplanowana".

**Verification commands (markdown/prompt — brak build/test):**
- Frontmatter YAML poprawny: `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- Frontmatter obecny we wszystkich SKILL.md: `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done`
- Manifesty JSON poprawne: `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done`
- Grep-verifiable AC — komendy per faza (patrz Phase Verification każdej fazy).

**Shared implementation context:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`

**Convention:** dwujęzyczność (CLAUDE.md) — prompty user-facing PL, terminy techniczne EN. Materiał donora obry (EN) przekładamy/adaptujemy, nie wklejamy surowo.

## Phase Overview

### Phase 1: HARD-GATE + rekoncyliacja micro-change
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/01-hard-gate.md`
**Depends on:** none
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 2: Wczesny scope-check (dekompozycja przed pytaniami)
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/02-scope-check.md`
**Depends on:** Phase 1
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 3: Prezentacja designu sekcjami + skalowanie długości
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/03-section-presentation.md`
**Depends on:** Phase 2
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 4: Spec self-review — nowa Faza 5A
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/04-spec-self-review.md`
**Depends on:** Phase 3
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 5: Visual Companion — sekcja przekrojowa + wskaźniki z faz
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/05-visual-companion.md`
**Depends on:** Phase 4
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 6: Rozszerzenie `allowed-tools` (frontmatter — permission surface)
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/06-frontmatter-tools.md`
**Depends on:** Phase 5
**Write scope:** `skills/feature-discuss/SKILL.md`
**Risk:** high

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/99-final-verification.md`

## Orchestrator Notes
- Orchestrator aktualizuje statusy w tym pliku.
- Workers aktualizują tylko swój phase file i `implementation-context.md`.
- Nie oznaczaj fazy `completed` zanim Phase Verification i `phase-review` nie przejdą.
- Każdy phase file ma Context Contract. Worker waliduje Requires przed startem; `phase-review` sprawdza Provides na koniec.
- **Wszystkie fazy piszą ten sam plik SKILL.md** — muszą iść ściśle sekwencyjnie (Phase N po Phase N-1). Żadnej równoległości.
- Metoda rewrite-to-unify: konsoliduj przy okazji (miękkie „NIE PISZ KODU" → jawny gate), nie tylko doklejaj — mitygacja rozdęcia pliku.
</content>
</invoke>
