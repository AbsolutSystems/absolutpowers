# Phase 1: HARD-GATE + rekoncyliacja micro-change

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-1-feature-discuss.md` (kroki 2, Zachowanie #1-2, AC-1/2/9)
- ADR lokalny: `./docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md` (decyzja #3 — gate rządzi akceptacją)

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- Nowy blok `## HARD-GATE — akceptacja designu przed implementacją` w `skills/feature-discuss/SKILL.md`, umieszczony PO nagłówku roli (po „## Temat feature'a" / przed „## Router trybu"), zawierający: (a) regułę „żaden kod/scaffolding/skill implementacyjny przed zaakceptowanym designem — KAŻDY projekt", (b) akapit anty-wzorca „To zbyt proste, by projektować", (c) zdanie rekoncyliacji micro-change.
- Zdanie rekoncyliacji „micro-change spełnia gate (akceptacja CO+GDZIE), nie obchodzi go" obecne w DWÓCH miejscach: w bloku HARD-GATE oraz w opisie Fazy 5 (micro-change).
- Zaktualizowana Zasada zachowania #1 (odwołuje HARD-GATE zamiast samego „NIE PISZ KODU").

## Read Scope
- `skills/feature-discuss/SKILL.md` (cały — orientacja w strukturze)

## Write Scope
- `skills/feature-discuss/SKILL.md`

## Objective
Wstaw jawny, samodzielny blok HARD-GATE po nagłówku roli, przed Routerem trybu. Blok stwierdza wprost, że żadna implementacja nie następuje przed zaakceptowanym przez użytkownika designem — dla każdego projektu niezależnie od rozmiaru — i jawnie adresuje anty-wzorzec „to zbyt proste". Zrekoncyliuj z micro-change: gate = akceptacja, nie ciężar doca. Skonsoliduj istniejące miękkie „NIE PISZ KODU" (nagłówek roli + Zasada #1) tak, by nie dublować przekazu (rewrite-to-unify, nie append).

## Tasks

### Task 1: Wstaw blok HARD-GATE + anty-wzorzec „too simple"
**Status:** completed
**Traces to:** AC-1, AC-2, AC-9

**Requirements:**
- Dodaj nowy blok `## HARD-GATE — akceptacja designu przed implementacją` (lub równoważny jednoznaczny nagłówek PL) między nagłówkiem roli (`## Temat feature'a`) a `## Router trybu`.
- Blok stwierdza wprost PL: żadna implementacja — kod, scaffolding, wywołanie skilla implementacyjnego — nie następuje przed **zaakceptowanym przez użytkownika** designem; dotyczy KAŻDEGO projektu niezależnie od rozmiaru.
- Dodaj akapit anty-wzorca: „To zbyt proste, by projektować" — stwierdź wprost, że prostota NIE zwalnia z wymogu akceptacji (adaptacja intencji obry: „proste projekty = najwięcej nieprzemyślanych założeń"). Nie wklejaj surowego EN.
- Umieść w bloku zdanie rekoncyliacji: micro-change to lekka ścieżka *pod* gate — akceptacja opisu CO+GDZIE spełnia gate, nie obchodzi go.
- Skonsoliduj miękkie „NIE PISZ KODU" z nagłówka roli tak, by nie było sprzecznej/zdublowanej normy — nagłówek roli może zostać krótki, twarda norma żyje w bloku HARD-GATE (rewrite-to-unify).

**Tests (grep-verifiable):**
- `grep -n "HARD-GATE" skills/feature-discuss/SKILL.md` → blok obecny, przed „## Router trybu".
- Blok zawiera frazę o akceptacji dla każdego projektu (np. „każd" + „projekt" + „akcept").
- Anty-wzorzec obecny: `grep -niE "zbyt proste|za proste" skills/feature-discuss/SKILL.md`.

### Task 2: Rekoncyliacja w Fazie 5 (micro-change) + update Zasady #1
**Status:** completed
**Traces to:** AC-9

**Requirements:**
- W opisie **Faza 5 → Micro-change** dopisz jedno zdanie: micro-change wymaga akceptacji CO+GDZIE zanim implementacja ruszy — to spełnia HARD-GATE, nie jest jego obejściem. (Micro-change nadal pomija generate-tasks/planning-doc, ale nie pomija akceptacji.)
- Zaktualizuj **Zasadę zachowania #1** tak, by odwoływała HARD-GATE (implementacja dopiero po akceptacji designu) zamiast samego „NIE PISZ KODU" — spójnie z nowym blokiem, bez sprzeczności.
- Nie zmieniaj mechaniki micro-change poza dodaniem zdania rekoncyliacji (fast-path do zatwierdzonego designu zostaje).

**Tests (grep-verifiable):**
- Zdanie rekoncyliacji w rejonie micro-change: `grep -niE "spełnia gate|nie obchodz|nie jest obejściem" skills/feature-discuss/SKILL.md` → ≥1 trafienie poza blokiem HARD-GATE (łącznie ≥2 w pliku).
- Zasada #1 wciąż istnieje w „## Zasady zachowania" i wspomina akceptację/gate.

## Phase Verification
Run:
- `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- `grep -c -iE "spełnia gate|nie obchodz|nie jest obejściem" skills/feature-discuss/SKILL.md` → oczekiwane ≥ 2 (blok gate + Faza 5).
- `grep -n "HARD-GATE" skills/feature-discuss/SKILL.md` → blok przed „## Router trybu" (porównaj numery linii z `grep -n "## Router trybu"`).

## Completion Criteria
- Wszystkie taski fazy `completed`.
- Wszystkie zmiany w Write Scope.
- Phase verification przechodzi.
- `implementation-context.md` zaktualizowany o kanoniczny nagłówek bloku HARD-GATE i decyzję o brzmieniu rekoncyliacji.
- Wszystkie pozycje Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Kanoniczny nagłówek bloku (do cytowania przez dalsze fazy): `## HARD-GATE — akceptacja designu przed implementacją`, wstawiony zaraz po `## Temat feature'a` / `$ARGUMENTS`, przed `## Router trybu` (linia ~33 w baseline po tej fazie).
- Blok ma 3 akapity: (1) twarda reguła "żadna implementacja przed akceptacją, KAŻDY projekt", (2) anty-wzorzec "to zbyt proste, by projektować", (3) rekoncyliacja z micro-change ("akceptacja opisu CO+GDZIE spełnia gate").
- Kanoniczne brzmienie rekoncyliacji (użyte w DWÓCH miejscach — blok HARD-GATE i Faza 5 micro-change): "akceptacja ... spełnia gate ... nie obchodzi [wymogu akceptacji]". Grep-verifiable pattern: `spełnia gate|nie obchodz|nie jest obejściem`.
- Nagłówek roli skrócony (jedno zdanie), skonsolidowany z jawnym blokiem HARD-GATE zamiast dublować "NIE PISZ KODU" — miękka norma usunięta z nagłówka, twarda norma żyje wyłącznie w bloku HARD-GATE + Zasadzie #1.
- Zasada zachowania #1 przeformułowana: teraz odwołuje sekcję HARD-GATE i wspomina akceptację/gate zamiast gołego "NIE PISZ KODU".
- Weryfikacja: frontmatter YAML OK, `grep -c` rekoncyliacji = 2 (linia bloku HARD-GATE + linia w Fazie 5), blok HARD-GATE (linia 33) jest przed „## Router trybu" (linia 41).
</content>
