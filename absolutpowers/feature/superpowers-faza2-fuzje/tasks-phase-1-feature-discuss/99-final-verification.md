# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Wszystkie phase files 01-06.

## Objective
Uruchom weryfikację całościową zintegrowanej zmiany `skills/feature-discuss/SKILL.md`: frontmatter poprawny, brak regresji Routera/formatów doców, wszystkie AC pokryte grepem, dwujęzyczność zachowana. Wykonywane przez orchestratora po przejściu wszystkich faz implementacyjnych.

## Tasks

### Task 1: Final Verification
**Status:** pending
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15

**Create:** None
**Modify:** None

**Description:**
Uruchom kanoniczne komendy walidacyjne repo + grep-verifiable checki wszystkich AC na zintegrowanym SKILL.md. Potwierdza brak regresji frontmatter/Routera/formatów i pokrycie każdego AC.

**Requirements:**
- **Frontmatter (AC-12):**
  - `python3 -c "import yaml; d=yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); assert d['name']=='feature-discuss'; assert d.get('argument-hint'); assert 'brainstorm' in d['allowed-tools'] and 'companion-scripts' in d['allowed-tools']; print('FM OK')"`
  - `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done` → brak outputu.
- **Router + formaty doców nietknięte (AC-12):**
  - `grep -cE "### Tryb A|### Tryb B|### Tryb C" skills/feature-discuss/SKILL.md` → `3`.
  - `grep -cE "## Format: standardowy planning doc|## Format: epic main doc|## Format: phase doc" skills/feature-discuss/SKILL.md` → `3`.
- **Grafty obecne (AC-1..AC-11):**
  - HARD-GATE + „too simple": `grep -n "HARD-GATE" skills/feature-discuss/SKILL.md` (AC-1); `grep -niE "zbyt proste|za proste" ...` (AC-2).
  - Rekoncyliacja ≥2 miejsca: `grep -c -iE "spełnia gate|nie obchodz|nie jest obejściem" skills/feature-discuss/SKILL.md` → ≥ 2 (AC-9).
  - Scope-check + brak duplikacji epica: obecny scope-check w Fazie 1 (AC-5); `grep -c "to nie jeden feature, to epic" ...` → `1` (AC-8).
  - Prezentacja sekcjami + skalowanie: `grep -niE "po każdej sekcji|akceptacj.*sekcj"` (AC-3); `grep -niE "skaluj|złożon"` (AC-4).
  - Faza 5A między 5 a 5B: `grep -nE "### Faza 5:|### Faza 5A|### Faza 5B" ...` numery rosnące (AC-6); wykluczenia micro/main/stuby obecne (AC-11).
  - Companion: `grep -c "Visual Companion" ...` → ≥ 4; `grep -c "visual-companion.md" ...` → ≥ 1 (AC-7); fallback no-Node (AC-10); statyczny render / no-code-exec (AC-13); niedostępność ≠ akceptacja (AC-14); gnhf brak-odpowiedzi = rezygnacja (AC-15).
- **Manifesty JSON:** `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done` → brak outputu.
- **Dwujęzyczność:** wyrywkowo potwierdź, że nowe prompty user-facing są PL (nie surowy EN z donora); companion mechanika-szczegóły zostają w `visual-companion.md`.
- **Rozdęcie pliku:** `wc -l skills/feature-discuss/SKILL.md` — odnotuj długość; potwierdź że rewrite konsolidował (nie tylko dokleił) — miękkie „NIE PISZ KODU" zredukowane na rzecz jawnego gate.
- Zapisz wszystkie wykonane komendy i wyniki w Implementation Decisions.
- NIE oznaczaj tej fazy `completed` jeśli którakolwiek komenda zgłasza regresję lub brak pokrycia AC.

**Tests:**
- Frontmatter YAML parsuje, `name`/`argument-hint` nietknięte, `allowed-tools` zawiera granty companion.
- Router (3 tryby) i formaty doców (3) obecne pod tymi samymi nagłówkami.
- Każdy z AC-1..AC-15 ma zielony grep-check.
- Wszystkie manifesty JSON walidne.

**Implementation decisions / remarks:**
- Komendy wykonane: frontmatter YAML parse (AC-12), for-loop FM presence, Router `grep -cE "### Tryb A|B|C"`, formaty doców `grep -cE "## Format:..."`, greps AC-1..AC-15, JSON manifest walidacja, `grep -nE "### Faza 5:|5A|5B"`, `wc -l`, `grep -nE "Bash\(\*"`.
- Wyniki (wszystkie zielone):
  - AC-12: `FM OK`; brak `NO FM`; Router = 3; formaty doców = 3.
  - AC-1 HARD-GATE = 6 trafień; AC-2 „zbyt proste" = 1.
  - AC-9 rekoncyliacja = 2 (≥2 OK); AC-8 epic msg = 1 (bez duplikacji).
  - AC-3 sekcje = 4; AC-4 skalowanie = 4.
  - AC-6 kolejność Faza 5 (L326) → 5A (L362) → 5B (L376) rosnąca; AC-11 wykluczenia = 12.
  - AC-7 „Visual Companion" = 4 (≥4 OK), „visual-companion.md" = 2 (≥1 OK).
  - AC-10 fallback no-Node = 2 (L49); AC-13 statyczny render = 1; AC-14 niedostępność≠akceptacja = 9; AC-15 gnhf rezygnacja obecny (L49, L55).
  - JSON manifesty: brak `BAD`.
  - Brak wiodącego wildcarda Bash (`grep -nE "Bash\(\*"` = puste) — potwierdza wąskie granty po poprawce Fazy 6.
- Dwujęzyczność: nowe prompty user-facing PL (spot-check L49/L55 — pełne zdania PL, brak surowego EN donora); mechanika serwera companion pozostała w `visual-companion.md`.
- Pominięte checki: none.
- `wc -l` SKILL.md przed/po: 583 → 653 (+70 na 6 graftów w całym pliku; rewrite-to-unify skonsolidował miękkie „NIE PISZ KODU" w jawny HARD-GATE zamiast doklejać — rozdęcie kontrolowane).

**Example:**
```bash
python3 -c "import yaml; d=yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK', d['name'])"
grep -cE "### Tryb A|### Tryb B|### Tryb C" skills/feature-discuss/SKILL.md   # 3
grep -c "Visual Companion" skills/feature-discuss/SKILL.md                    # >=4
```

## Completion Criteria
- Wszystkie komendy walidacyjne exit 0 / oczekiwany output.
- Każdy AC-1..AC-15 ma zielony check.
- Brak regresji Routera/formatów/frontmatter.
- Implementation Decisions wypełnione wynikami.
</content>
