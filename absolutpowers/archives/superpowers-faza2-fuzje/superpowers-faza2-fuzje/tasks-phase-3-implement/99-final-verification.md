# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-3-implement.md`

## Objective
Zweryfikować zintegrowaną zmianę w całym repo pluginu. Ponieważ ta faza fuzuje mechanikę skilla (nie feature aplikacyjny), weryfikacja = **grep-against-artifact** + walidacja manifestów/hooka/frontmatteru/skryptów. Brak runtime test suite; konwencja tokenu `AC-N` w testach NIE obowiązuje. Wykonuje orchestrator po PASS wszystkich faz.

## Verification Commands

### 1. Manifesty JSON + zgodność wersji
```bash
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
test "$(grep '"version"' .claude-plugin/plugin.json)" = "$(grep '"version"' .codex-plugin/plugin.json)" && echo "VERSION OK"
```

### 2. Hook SessionStart emituje poprawny JSON
```bash
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null && echo "HOOK OK"
```

### 3. Frontmatter każdego SKILL.md
```bash
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done
```

### 4. Forkowane skrypty parsują się, są wykonywalne, bez `.superpowers/sdd`, z notą MIT
```bash
bash -n skills/implement/scripts/review-package && bash -n skills/implement/scripts/sdd-workspace && echo "BASH OK"
test -x skills/implement/scripts/review-package && test -x skills/implement/scripts/sdd-workspace && echo "EXEC OK"
! grep -q '.superpowers/sdd' skills/implement/scripts/review-package && ! grep -q '.superpowers/sdd' skills/implement/scripts/sdd-workspace && echo "DIR OK"
grep -Eiq 'MIT|Jesse Vincent' skills/implement/scripts/review-package && grep -Eiq 'MIT|Jesse Vincent' skills/implement/scripts/sdd-workspace && echo "ATTRIB OK"
```

### 5. AC grep-checklist (wszystkie AC-1..AC-15)
```bash
# AC-1: worker wylicza dokładnie 4 statusy, bez COMPLETED/FAILED jako wartości
grep -Eq 'PHASE_RESULT: *DONE *\| *DONE_WITH_CONCERNS *\| *NEEDS_CONTEXT *\| *BLOCKED' agents/implementation-worker.md && echo "AC-1 a"
! grep -Eq 'PHASE_RESULT.*COMPLETED|PHASE_RESULT.*FAILED' agents/implementation-worker.md && echo "AC-1 b"
# AC-2: DONE (dawny COMPLETED), DONE_WITH_CONCERNS, NEEDS_CONTEXT przy Requires
grep -q 'Use `DONE` only when' agents/implementation-worker.md && grep -q 'DONE_WITH_CONCERNS' agents/implementation-worker.md && grep -q 'NEEDS_CONTEXT' agents/implementation-worker.md && echo "AC-2"
# AC-3: cztery gałęzie w O3, brak wspólnej "BLOCKED lub FAILED"
grep -q 'DONE_WITH_CONCERNS' skills/implement/SKILL.md && grep -q 'NEEDS_CONTEXT' skills/implement/SKILL.md && ! grep -Eq 'BLOCKED (or|lub) FAILED' skills/implement/SKILL.md && echo "AC-3"
# AC-4: drabina 4-way (kontekst→ten sam model, mocniejszy model, dekompozycja, eskalacja)
grep -Eiq 'mocniejszy|stronger' skills/implement/SKILL.md && grep -Eiq 'dekompoz|decompos' skills/implement/SKILL.md && grep -Eiq 'eskal|escalat' skills/implement/SKILL.md && echo "AC-4 (potwierdź kolejność ręcznie)"
# AC-5: routing ≥3 tiery + phase-review skalowany + review-implementation opus
grep -q 'haiku' skills/implement/SKILL.md && grep -q 'opus' skills/implement/SKILL.md && grep -q 'phase-review' skills/implement/SKILL.md && echo "AC-5 (potwierdź tabelę ręcznie)"
# AC-6: sekcja Durable Progress, progress.md, format zakresu commitów, BASE przed dispatchem
grep -Eiq 'Durable Progress|ledger' skills/implement/SKILL.md && grep -q 'progress.md' skills/implement/SKILL.md && grep -Eiq 'BASE' skills/implement/SKILL.md && echo "AC-6"
# AC-7: review-package w O4/O6, brak "read git diff" na wejściu reviewera
grep -q 'review-package' skills/implement/SKILL.md && echo "AC-7 (potwierdź O4/O6 ręcznie)"
# AC-8: agenci przyjmują package path, bez listy git diff
grep -Eiq 'review package' agents/phase-review.md && grep -Eiq 'review package' agents/review-implementation.md && ! grep -q 'git diff --cached' agents/phase-review.md && ! grep -q 'git diff --cached' agents/review-implementation.md && echo "AC-8"
# AC-9: ledger + git log autorytatywne, tasks file = widok dla człowieka
grep -Eiq 'autorytatywn|authoritative' skills/implement/SKILL.md && grep -Eiq 'widok dla człowieka|human.?view|human-readable view' skills/implement/SKILL.md && echo "AC-9"
# AC-10: Single-File Process bez nowych statusów i bez wymogu ledgera
awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -Eq 'DONE_WITH_CONCERNS|NEEDS_CONTEXT' && echo "AC-10 STATUS LEAK" || echo "AC-10 status OK"
awk '/## Single-File Process/,/^## Rules$/' skills/implement/SKILL.md | grep -q 'progress.md' && echo "AC-10 LEDGER LEAK" || echo "AC-10 ledger OK"
# AC-11 / AC-12: fallback na standard + always-explicit (potwierdź ręcznie)
grep -Eiq 'always.?explicit|jawnie.*model|zawsze.*jawn' skills/implement/SKILL.md && echo "AC-12 (potwierdź AC-11 fallback ręcznie)"
# AC-13: fork bez .superpowers/sdd + MIT (patrz sekcja 4)
# AC-14: VENDORED.md wpis forka
grep -q 'skills/implement/scripts' VENDORED.md && grep -Eiq 'review-package' VENDORED.md && echo "AC-14"
# AC-15: brak task-brief w 4 plikach pluginu
! grep -l 'task-brief' skills/implement/SKILL.md agents/implementation-worker.md agents/phase-review.md agents/review-implementation.md && echo "AC-15"
```

## Completion Criteria
- Sekcje 1–4 zwracają OK (JSON valid, wersje zgodne, hook OK, frontmattery OK, skrypty OK).
- Sekcja 5: wszystkie AC-1..AC-15 potwierdzone (grep + ręczne potwierdzenia AC-4 kolejność drabiny, AC-5 tabela, AC-7 O4/O6, AC-11 fallback).
- Żadna komenda wymagana nie kończy się błędem.
- Nie oznaczaj jako completed jeśli którakolwiek weryfikacja wymagana zawiedzie.

## Implementation Decisions / Remarks
- Commands executed: sections 1–4 (JSON manifests + version match, SessionStart hook, SKILL.md frontmatter scan, script `bash -n`/`test -x`/no-`.superpowers/sdd`/MIT) + section 5 AC-1..AC-15 grep checklist, run by orchestrator 2026-07-13.
- Results: all PASS. Sections 1–4 → VERSION OK (5.1.0), HOOK OK, FM scan clean, BASH OK / EXEC OK / DIR OK / ATTRIB OK. Section 5 → AC-1..AC-15 all `ok`. Manual confirmations: AC-4 ladder order (context→same model → stronger model → decomposition → human escalation + hard rule) ✓; AC-5 role table (haiku/sonnet/opus implementer tiers + phase-review scaled + review-implementation opus) ✓; AC-7 O4/O6 run review-package before dispatch and pass package path, no self-diff ✓; AC-11 sonnet-as-doubt-fallback ✓.
- Skipped checks: none.
