# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-2-generate-tasks/implementation-context.md`

## Objective
Uruchomić repo-canonical checki (frontmatter, JSON lint, SessionStart hook) i structural grepy potwierdzające obecność wszystkich 5 graftów w SKILL.md, 3 kryteriów w review-tasks.md, oraz not w VENDORED.md / planning-main.md. Potwierdzić regresję GC-2 (sekcje NIE-do-dotykania nienaruszone). Brak buildu/testów runtime — walidacja to lint + structural grep. Wykonywane przez orchestratora po PASS wszystkich faz implementacyjnych.

## Verification

### Requirements
- Frontmatter: `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done` → brak outputu.
- JSON manifesty: `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done` → brak `BAD:`.
- SessionStart hook: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null` → exit 0.
- Structural grep — 5 graftów w `skills/generate-tasks/SKILL.md`: `Global Constraints`, `Produces:`, `Consumes:`, `No Placeholders`, `## Self-Review` — każdy ≥1 trafienie.
- GC-2 regresja: `grep -cE "AC Traceability|Test-first|HARD BUDGET|Review Gate|orchestrated" skills/generate-tasks/SKILL.md` — grep-AC / Test-first / budget / gate / mode zachowane.
- review-tasks.md: `grep -nE "GLOBAL_CONSTRAINTS|INTERFACES|PLACEHOLDER" agents/review-tasks.md` → 3 kategorie; `grep -c "^### [0-9]" agents/review-tasks.md` ≥7.
- Rejestr: `grep -n "writing-plans" VENDORED.md` i `grep -n "W toku" absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`.
- Nie oznaczaj `completed`, jeśli którakolwiek weryfikacja zawiedzie.

### Tests
- Frontmatter check: brak outputu.
- JSON lint: brak `BAD:`.
- Hook: exit 0.
- 5 graftów: 5/5 obecne.
- GC-2: sekcje NIE-do-dotykania obecne.
- review-tasks.md: 3 kategorie + ≥7 kryteriów.
- Rejestr: obie noty obecne.

## Completion Criteria
- Wszystkie komendy weryfikacyjne przechodzą.
- Zapisane w Remarks: komendy + wyniki + pominięte checki (lub `none`).

## Implementation Decisions / Remarks
- Commands executed: frontmatter check; JSON lint; SessionStart hook; 5-graft grep on `skills/generate-tasks/SKILL.md`; GC-2 regression grep; `review-tasks.md` categories + criteria-count grep; registry greps (`VENDORED.md`, `planning-main.md`).
- Results: frontmatter → no output (pass); JSON lint → no `BAD:` (pass); hook → exit 0 (pass); 5 grafts → 14 hits (all 5 present, ≥1 each); GC-2 → 27 hits (AC Traceability/Test-first/HARD BUDGET/Review Gate/orchestrated all intact); review-tasks → 3 categories (GLOBAL_CONSTRAINTS/INTERFACES/PLACEHOLDER) + 10 criteria (≥7, 1-7 preserved); registry → `writing-plans` donor note at VENDORED.md:77-79, Faza 2 `W toku` at planning-main.md:35.
- Skipped checks: none.

## Example
```bash
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null
grep -nE "Global Constraints|Produces:|Consumes:|No Placeholders|## Self-Review" skills/generate-tasks/SKILL.md
grep -nE "GLOBAL_CONSTRAINTS|INTERFACES|PLACEHOLDER" agents/review-tasks.md
```
