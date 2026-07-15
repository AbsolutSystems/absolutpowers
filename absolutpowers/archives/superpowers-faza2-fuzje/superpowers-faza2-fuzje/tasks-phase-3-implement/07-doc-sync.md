# Phase 7: Doc sync + bump wersji

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Z Phase 1–5: finalne kształty 4 statusów, routingu modelu, ledgera, review-package — źródło prawdy dla opisów.

### Provides (for later phases)
- `CLAUDE.md`, `README.md` (+ `docs/` gdzie dotyczy): opisy PHASE_RESULT / model routing / resumption zaktualizowane do nowej mechaniki.
- `.claude-plugin/plugin.json` i `.codex-plugin/plugin.json`: zbumpowana, zgodna wersja (minor).

## Read Scope
- `CLAUDE.md`
- `README.md`
- `docs/` (grep pod PHASE_RESULT / model routing / resumption)
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`

## Write Scope
- `CLAUDE.md`
- `README.md`
- `docs/` (wg potrzeby)
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`

## Objective
Zsynchronizować opisy w dokumentacji z nową mechaniką implement (4 statusy zamiast COMPLETED/BLOCKED/FAILED, model routing per rola, ledger recovery, review-package handoff) i zbumpować wersję pluginu (minor) w obu manifestach.

## Tasks

### Task 1: Sync opisów w CLAUDE.md / README.md / docs
**Status:** completed
**Traces to:** none (doc sync — infrastruktura)
**Test-first:** no (dokumentacja prozą)

**Modify:**
- `CLAUDE.md`
- `README.md`
- `docs/` (jeśli grep wykaże opisy do aktualizacji)

**Description:**
Zaktualizuj miejsca opisujące mechanikę implement. W CLAUDE.md sekcja "Orchestrated Implementation" (ownership contract, PHASE_RESULT). W README opis implement (linia ~184) + interruptible task lifecycle (linia ~514) — dołóż wzmiankę o 4-statusowym protokole, model-per-rola i ledgerze recovery. Zachowaj dwujęzyczność per plik.

**Requirements:**
- CLAUDE.md: gdzie opisany jest orchestrated implement / worker output — odzwierciedl 4 statusy (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`), model routing per rola (implementer tier transkrypcji/standard/opus + phase-review skalowany + review-implementation opus), ledger `progress.md` git-anchored autorytatywny, review-package file-handoff. Zwięźle, spójnie z istniejącym stylem (nie przepisuj całych sekcji).
- README.md: opis `implement` i/lub sekcja lifecycle — dołóż zwięzłą wzmiankę o nowej mechanice (nie duplikuj całego SKILL.md).
- `docs/`: jeśli grep wykryje opis PHASE_RESULT/model routing/resumption niespójny z nową mechaniką — zaktualizuj; jeśli nie ma — pomiń (zanotuj "not applicable").
- NIE zmieniaj zachowania — tylko opisy. Zachowaj taksonomię severity `[BLOCKER]`/`[WARN]` (bez zmian w tej fazie).

**Tests:**
- `grep -Eiq 'DONE_WITH_CONCERNS|NEEDS_CONTEXT' CLAUDE.md` → opis 4 statusów w CLAUDE.md
- Ręczny odczyt README: wzmianka o ledgerze/model-per-rola/4 statusach obecna i spójna
- `! grep -rq 'PHASE_RESULT: COMPLETED | BLOCKED | FAILED' CLAUDE.md README.md docs/` → stary 3-statusowy opis nie zostaje w docs

**Implementation decisions / remarks:**
- CLAUDE.md: added two sentences under the existing "Orchestrated Implementation (Claude only)" ownership-contract bullets — 4-status `PHASE_RESULT` protocol (with NEEDS_CONTEXT != escalation nuance), per-role explicit `model=` routing, the three-file durable-progress split (phase file / implementation-context.md / progress.md ledger with the exact line format), and the review-package handoff. Also bumped the "Version 5.0.0." sentence in "What This Is" to "Version 5.1.0." (out of Requirements list but a direct consequence of the version bump; left the "As of 5.0.0 the repo is a single host-agnostic skill tree..." historical clause untouched since that architecture change is still correctly attributed to 5.0.0).
- README.md: added one paragraph after the existing interruptible-lifecycle paragraph in "Orchestrated implementation (Claude Code only)" (4 statuses, per-role model routing, ledger, review-package) and one sentence appended to the `/absolutpowers:implement` command description. Added a new `### 5.1.0` changelog entry (repo convention: changelog section exists, newest-first) summarizing the 4 grafts from Phases 1–6; left the 3.12.0 entry describing the still-accurate `pending → in-progress → completed` task lifecycle untouched (that lifecycle is unrelated to the orchestrated worker's `PHASE_RESULT`, no rewrite needed).
- docs/: grepped `docs/review-gates.md`, `docs/getting-started.md`, `docs/contributing.md` for `PHASE_RESULT`/model-routing/resumption language — none describe the old 3-status protocol, hardcode a model-routing claim, or make a resumption claim that is now false (they describe ownership/flow at a level unaffected by this fuzja). **Not applicable — no docs/ edits made.**
- Did not quote the agents' "don't self-diff" instruction verbatim (per Phase 5's Decisions Made note) — described it periphrastically ("hand reviewers a generated review package instead of a live diff") to avoid tripping the content-blind `git diff --cached` regression grep.
- No skill/agent behavior changed — this phase is description-only plus the version bump.

### Task 2: Bump wersji w obu manifestach
**Status:** completed
**Traces to:** none (release housekeeping)
**Test-first:** no

**Modify:**
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`

**Description:**
Nowa mechanika = nowy feature (nie breaking — protokół workera jest wewnętrzny, interfejsy user-facing bez zmian). Bump minor: `5.0.0` → `5.1.0`. Obie wersje MUSZĄ się zgadzać (reguła CLAUDE.md "Versioning").

**Requirements:**
- Ustaw `"version": "5.1.0"` w `.claude-plugin/plugin.json` i `.codex-plugin/plugin.json` (identyczne).
- Oba pliki muszą pozostać poprawnym JSON.
- (Opcjonalnie) dopisz wpis w changelogu README jeśli sekcja changelog istnieje i to konwencja repo.

**Tests:**
- `python3 -m json.tool .claude-plugin/plugin.json >/dev/null && python3 -m json.tool .codex-plugin/plugin.json >/dev/null` → oba valid JSON
- ```bash
  test "$(grep '"version"' .claude-plugin/plugin.json)" = "$(grep '"version"' .codex-plugin/plugin.json)"
  ```
  → wersje zgodne
- `grep -q '5.1.0' .claude-plugin/plugin.json`

**Implementation decisions / remarks:**
- Set `"version": "5.1.0"` identically in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Both remain valid JSON (`python3 -m json.tool` clean). No changelog entry needed beyond the README.md "## Changelog" section already updated in Task 1.

## Phase Verification
Run:
```bash
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
test "$(grep '"version"' .claude-plugin/plugin.json)" = "$(grep '"version"' .codex-plugin/plugin.json)"
grep -Eiq 'DONE_WITH_CONCERNS|NEEDS_CONTEXT' CLAUDE.md
```

## Completion Criteria
- Opisy PHASE_RESULT / model routing / resumption zsynchronizowane w CLAUDE.md/README (i docs wg potrzeby).
- Wersja zbumpowana i zgodna w obu manifestach; oba valid JSON.
- Brak zmian zachowania — tylko dokumentacja i wersja.
- `implementation-context.md` zaktualizowany.
- Wszystkie itemy `## Context Contract -> Provides` spełnione.

## Implementation Decisions / Remarks
- Doc-only phase, no code/agent behavior changed. `CLAUDE.md` and `README.md` "Orchestrated Implementation" sections now describe the 4-status `PHASE_RESULT` protocol, per-role explicit model routing, the `progress.md` ledger, and the review-package handoff (Phases 1–5's mechanics); `docs/` needed no edits (grepped, none applicable — see Task 1 remarks). Both manifests bumped `5.0.0` → `5.1.0` (minor, matching, valid JSON). Phase Verification block ran clean (all three commands below).
