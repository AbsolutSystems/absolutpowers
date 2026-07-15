# Phase 4: Spec self-review — nowa Faza 5A

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: krok 4, Zachowanie #5, AC-6/AC-11
- Edge case planningu: self-review NIE emituje severity (`[BLOCKER]`/`[WARN]`) — to zostaje bramce review-plan (Faza 6)

## Context Contract

### Requires (from previous phases)
- Struktura procesu z Faz 1-3 spójna (Phase 1-3) — Faza 5A wstawiana jest w istniejącą sekwencję między Fazę 5 (zapis) a 5B (QA).

### Provides (for later phases)
- Nowa sekcja `### Faza 5A: Spec self-review` wstawiona MIĘDZY „### Faza 5: Ocena złożoności i zapis" a „### Faza 5B: QA Enrichment".
- Jednoprzebiegowy skan: placeholdery/TODO, wewnętrzna sprzeczność, scope-fit, dwuznaczność (→ wybierz jedną interpretację i uczyń ją jawną); fix inline, bez re-review; NIE emituje severity.
- Jawne wykluczenie: Faza 5A dotyczy tylko standardowego feature'a + phase doca (Tryb B); NIE micro-change, NIE `planning-main.md`, NIE stubów faz.

## Read Scope
- `skills/feature-discuss/SKILL.md` (Faza 5 L~271-304, Faza 5B L~306-318 — punkty wstawienia i wzorzec „> Dotyczy: ..." z Fazy 5B)

## Write Scope
- `skills/feature-discuss/SKILL.md`

## Objective
Wstaw nową Fazę 5A między zapis doca (Faza 5) a QA-enrichment (Faza 5B). Faza 5A robi jednoprzebiegowy self-review zapisanego planning/phase-doca (placeholdery/TODO, wewnętrzna sprzeczność, dopasowanie zakresu, dwuznaczność), naprawia inline i nie robi pełnego re-review. Nie emituje severity — to zostaje bramce review-plan. Jawnie ogranicz zakres uruchomienia (standard feature + phase doc Trybu B; wyklucz micro-change/main/stuby).

## Tasks

### Task 1: Wstaw Fazę 5A (spec self-review) z jawnym zakresem uruchomienia
**Status:** completed
**Traces to:** AC-6, AC-11

**Requirements:**
- Wstaw `### Faza 5A: Spec self-review` bezpośrednio po `### Faza 5` a przed `### Faza 5B: QA Enrichment`.
- Treść: jednoprzebiegowy skan zapisanego doca pod kątem — (a) placeholdery/TODO, (b) wewnętrzna sprzeczność, (c) scope-fit (dopasowanie zakresu), (d) dwuznaczność → wybierz JEDNĄ interpretację i uczyń ją jawną. Napraw problemy inline, bez ponownego pełnego review.
- Zaznacz jawnie: Faza 5A **nie emituje** severity (`[BLOCKER]`/`[WARN]`) — decyzja o severity zostaje bramce review-plan (Faza 6).
- Dodaj przypis zakresu (wzoruj na `> Dotyczy: ...` z Fazy 5B): Faza 5A uruchamia się WYŁĄCZNIE dla standardowego feature'a oraz phase doca w Trybie B; jawnie wyklucz micro-change, `planning-main.md` oraz stuby faz epica.
- Język PL user-facing; terminy techniczne EN.

**Tests (grep-verifiable):**
- `grep -nE "Faza 5A" skills/feature-discuss/SKILL.md` → obecna, między „Faza 5:" a „Faza 5B".
- Kryteria skanu obecne: `grep -niE "placeholder|TODO|sprzeczn|dwuznaczn|scope" skills/feature-discuss/SKILL.md` w rejonie 5A.
- Wykluczenia obecne: `grep -niE "micro-change.*main|main.*stub|nie dotyczy|wyklucz" skills/feature-discuss/SKILL.md` w rejonie 5A (micro-change/main/stuby).
- Brak emisji severity w 5A: sekcja 5A NIE zawiera `[BLOCKER]`/`[WARN]` jako emitowanych markerów (dozwolone tylko jako wskazanie „to zostaje review-plan").

## Phase Verification
Run:
- `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- Kolejność sekcji: `grep -nE "### Faza 5:|### Faza 5A|### Faza 5B" skills/feature-discuss/SKILL.md` → numery linii rosnące w kolejności 5 → 5A → 5B.
- `grep -niE "wyklucz|nie dotyczy|micro-change" skills/feature-discuss/SKILL.md` → wykluczenia obecne w rejonie 5A.

## Completion Criteria
- Wszystkie taski fazy `completed`.
- Zmiany w Write Scope.
- Phase verification przechodzi; kolejność 5 → 5A → 5B zachowana.
- `implementation-context.md` zaktualizowany.
- Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Nowa sekcja `### Faza 5A: Spec self-review` wstawiona w `skills/feature-discuss/SKILL.md` między `### Faza 5: Ocena złożoności i zapis` (L300) a `### Faza 5B: QA Enrichment` (teraz L350; było L336 przed wstawieniem). Faza 5A zajmuje L336-349.
- Wzorowano się dosłownie na przypisie zakresu Fazy 5B (`> Dotyczy: ...`) — powtórzono identyczną formułę wykluczenia (micro-change / `planning-main.md` / stuby faz), rozszerzoną o "faz epica" dla jednoznaczności.
- 4 kryteria skanu (placeholdery/TODO, wewnętrzna sprzeczność, scope-fit, dwuznaczność) wypisane jako osobne bullet pointy z pogrubioną nazwą kryterium — dwuznaczność jawnie instruuje "wybierz JEDNĄ interpretację i uczyń ją jawną w tekście dokumentu" (dosłowne odwzorowanie planningu, nie parafraza).
- Jawnie zaznaczono "Ty sam, bez subagenta" — odróżnia to od Fazy 5B (QA-enrichment), która odpala subagenta; Faza 5A to self-review wykonywany przez główną sesję.
- Zdanie o braku emisji severity używa `[BLOCKER]`/`[WARN]` wyłącznie jako wskazanie-referencja do bramki review-plan (Faza 6) — zgodnie z dozwolonym wyjątkiem z testu fazy ("dozwolone tylko jako wskazanie 'to zostaje review-plan'"), nie jako emitowany marker.
- Nie ruszono treści Fazy 5B ani żadnej innej sekcji — czysta insercja, zero zmian w istniejącym tekście.
</content>
