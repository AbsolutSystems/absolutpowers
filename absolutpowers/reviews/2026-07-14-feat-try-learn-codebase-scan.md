# Full Review Report

> **Zakres:** branch `feat/try-learn-codebase-scan` vs `main` — 2 commity (tasks + implementacja),
> 11 plików, +550/−500. Feature: try-learn-skill → codebase-scan, harvest usunięty, archiwizacja → ship.
> Repo bez buildu — weryfikacja grep/strukturalna. Brak `rules.md`/`constitution.md` → Fazy 3 pominięte.

## 1. Semantic Review

### Co się zmieniło:
- `skills/try-learn-skill/SKILL.md` — pełny rewrite zachowania: źródło sygnału feature-artefakt → skan całego codebase; próg ≥3 wystąpień z `file:line`; batch approval; usunięty ledger/promocja/fast-track; dodana granica vs update-ai-context.
- `skills/ship/SKILL.md` — nowy KROK 4.5 (archiwizacja artefaktów, przeniesiony z harvest KROK 4); reconcile 5 ref harvest; allowed-tools +mkdir/mv/Write(archives).
- `skills/harvest/SKILL.md` — usunięty (skill nie istnieje).
- `skills/implement/SKILL.md`, `skills/document-feature/SKILL.md` — rewiring nudge/trigger → ship/ad-hoc.
- `CLAUDE.md`, `README.md`, `docs/getting-started.md` — usunięcie żywych ref harvest, poprawa liczników 15→14, grid ship↔harvest, changelog 5.1.0, bump wersji.

### Blast Radius:
- Usunięcie harvest → każdy kto wołał `/absolutpowers:harvest` (surface change, udokumentowane w changelog jako 5.1.0). Archiwizacja zachowana w ship — zero utraty funkcji.
- ship: nowy krok mutujący pliki (`git mv`) pod gate — powierzchnia review = `git diff` commita domykającego. Bezpieczne (hard boundary + human gate).
- try-learn: zmiana kontraktu wejścia (codebase zamiast tasks-doc) — ad-hoc, poza pipeline, brak zależnych konsumentów.

### Pytania do autora:
- Brak. Design zaakceptowany w feature-discuss, zaimplementowany zgodnie z planem.

## 2. Edge Cases

Prompty markdown — „edge cases" = sprzeczności/wiszące ref/luki proceduralne.

### WYSOKIE RYZYKO: brak.

### ŚREDNIE RYZYKO: brak.

### Sprawdzone, czyste:
- try-learn: ścieżka „0 kandydatów" jawna (KROK 5, koniec bez zapisu); human gate twardy; próg N tunable; dowód `file:line` wymagany.
- ship: warunki wstępne archiwizacji (taski completed / epic complete / brak artefaktów → skip); hard boundary (tylko artefakty feature'a); gate przed `mv`; allowed-tools kompletne (`git mv` przez Bash(git:*), mkdir, mv, Write archives).
- Zero martwych ref: `harvest` = 0 w skills/agents/hooks/references/docs*.md/CLAUDE.md (tylko changelog historyczny); `_candidates.md`/ledger = 0 w żywych promptach.

## 3. Rules Check
Brak pliku `./absolutpowers/rules.md`, pomijam sprawdzanie reguł.

### Pryncypia (constitution)
Brak pliku `./absolutpowers/constitution.md`, pomijam sprawdzanie pryncypiów.

## 4. Garbage Collection

### Do usunięcia: brak (zero TODO/FIXME/placeholder w zmienionych skillach).

### Naprawione w trakcie review (2 znaleziska — stale opisy starego try-learn, poza grepem `harvest` z Task 6):
- `README.md:347` (Key Concepts „Learned skills") — opis starego mechanizmu ledger/„promote on 2nd"/fast-track → przepisany na codebase-scan (≥3 + ≥2 nieoczywiste + batch approval).
- `README.md:353-354` (tabela Lifecycle/Source) — „Ledger candidate → promote on 2nd" i „One finished feature + git diff" → codebase-scan z progiem ≥3. Wiersz `patterns.md` doprecyzowany (structural convention vs procedure).

### Do sprawdzenia: brak.

## Podsumowanie
- Krytyczne problemy: 0
- Ryzyka do sprawdzenia: 0
- Śmieci do usunięcia: 0
- Złamane reguły: 0 (brak rules.md)
- Naruszone pryncypia: 0 (brak constitution.md)
- Weryfikacja końcowa: potwierdzona — 13/13 AC grep-verified, review-implementation PASS (2 rundy), JSON/hook/wersje OK, grep-sweep harvest/ledger czysty.
- Ogólna ocena: **Czysto. Gotowe do ship/merge.** Solo review złapał 2 żywe stale opisy try-learn w README, których grep `harvest` z Task 6 nie objął (dotyczyły ledgera, nie harvestu) — oba naprawione inline. Zero ryzyk semantycznych, spójny redesign.
