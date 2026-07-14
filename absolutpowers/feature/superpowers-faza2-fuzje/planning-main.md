# Epic: Fuzja mechaniki obry do skilli domenowych (Faza 2 migracji)

## Status
Zrobiona — 2026-07-13 (wszystkie 3 fuzje zaimplementowane, bramki review PASS)

## Problem
Faza 1 migracji zvendorowała skille obry do jednego drzewa `skills/vendored/` i zachowała warstwę domenową absolutpowers. Faza 2 wchłania **dojrzałą mechanikę** trzech skilli obry (brainstorming, writing-plans, subagent-driven-development) do trzech skilli domenowych (feature-discuss, generate-tasks, implement) — bez porzucania warstwy domenowej (ADR, grep-AC, project-memory, QA, orchestrated gates). Cel: połączyć sprawdzoną-przez-community mechanikę konwersacji/planowania/wykonania obry z unikalną warstwą procesową Absolut Systems.

## Użytkownicy
Deweloperzy Absolut Systems używający pipeline'u absolutpowers na Claude Code / Codex / Pi (dev + nocne runy headless).

## Oczekiwane zachowanie (high-level)
Po fuzji trzy skille pipeline'u zyskują mechanikę obry, zachowując interfejsy i warstwę domenową:
- **feature-discuss** — HARD-GATE przed implementacją, prezentacja designu sekcjami z akceptacją per sekcja, dekompozycja dużych projektów przed pytaniami szczegółowymi, spec self-review, aktywny visual companion.
- **generate-tasks** — blok Interfaces (Consumes/Produces z sygnaturami), Global Constraints w nagłówku, reguły No Placeholders, kompletny kod w krokach, self-review spójności typów.
- **implement** — protokół 4 statusów implementera, dobór modelu per rola, ledger recovery po kompakcji, file-handoff via task-brief/review-package.

## Wspólny kontekst architektoniczny
- Stack: Markdown (SKILL.md), agenci/komendy Claude-only, JSON manifesty, plugin wieloharnessowy (Claude/Codex/Pi) po Fazie 1.
- Materiał-dawca: `skills/vendored/{subagent-driven-development,executing-plans,...}` (już w repo, MIT) oraz `vendor/superpowers/skills/{brainstorming,writing-plans}` (NIE vendorowane — tylko dawcy sekcji do fuzji).
- Warstwa domenowa do zachowania w KAŻDEJ fuzji: ADR, grep-AC, project-memory, QA enrichment, orchestrated gates ([BLOCKER]/[WARN] + review-*).
- Inwentarz `superpowers:*` cross-refów do rozwiązania: patrz `VENDORED.md` (executing-plans, subagent-driven-development, systematic-debugging).

## Wspólne decyzje
- **Metoda fuzji: rewrite-to-unify** (nie append w żadną stronę). Nowa, zunifikowana treść zawierająca oba światy; baza (czyj szkielet) wybierana **per fuzja na podstawie analizy**, nie z góry. Robocza hipoteza: treść obry często silniejsza (przetestowana przez community) → częściej szkielet obry + wszczepiona warstwa domenowa; ale weryfikujemy case-by-case w każdej fazie. → ADR: `./docs/adr/2026-07-13-rewrite-to-unify-fuzja-obry.md`
- **Dwujęzyczność zachowana** (zgodnie z CLAUDE.md): prompty user-facing po polsku, treść techniczna po angielsku. Materiał obry (EN) przekładamy/adaptujemy do tej konwencji, nie wklejamy surowo.
- **implement: NIE deprecjacja.** Wstrzykujemy 4 mechanizmy sdd w istniejący orchestrated implement; vendored subagent-driven-development zostaje jako źródło szablonów/skryptów (task-brief, review-package, sdd-workspace).
- **Walidacja jakości:** każdy zmodyfikowany skill przechodzi test metodą `writing-skills` (baseline RED bez mechaniki → GREEN z mechaniką) — Faza 5 planu migracji.

## Mapa faz

| Faza | Nazwa | Cel | Status | Plan |
|------|-------|-----|--------|------|
| 1 | feature-discuss ← brainstorming | Wchłonąć HARD-GATE, prezentację sekcjami, dekompozycję, spec self-review + wpiąć visual companion | Zrobiona | `planning-phase-1-feature-discuss.md` · [onboarding](../../../docs/onboarding/faza1-feature-discuss-brainstorming-2026-07-13.html) · [ADR](../../../docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md) |
| 2 | generate-tasks ← writing-plans | Przejąć blok Interfaces, Global Constraints, No Placeholders, kompletny kod w krokach, self-review typów | Zrobiona | `planning-phase-2-generate-tasks.md` · [ADR](../../../docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md) |
| 3 | implement ← subagent-driven | Wstrzyknąć 4 mechanizmy (statusy, model-per-rola, ledger, file-handoff) bez deprecjacji orchestrated | Zrobiona | `planning-phase-3-implement.md` · tasks: `tasks-phase-3-implement.md` |

> Statusy: `Do zaplanowania` → `Zaplanowana` → `W toku` → `Zrobiona`

## Zależności między fazami
- Fuzje są **edycyjnie niezależne** (różne pliki skilli) — można je implementować w dowolnej kolejności bez konfliktów.
- Ale **pipeline'owo sekwencyjne**: Faza 2 (generate-tasks) konsumuje output Fazy 1 (spec z feature-discuss); Faza 3 (implement) konsumuje output Fazy 2 (taski). Planowanie i walidację end-to-end prowadzimy wg tej kolejności.

## Out of scope (całość)
- Pełne ujednolicenie języka repo (dwujęzyczność zostaje — nie bug).
- Vendoring nowych skilli obry (zamknięte w Fazie 1).
- Zmiany w skillach spoza trójki (review, debug, harvest, itd.) — chyba że fuzja wymusi drobny touch (np. severity taksonomia).
- Faza 4/5 planu migracji (headless integration, walidacja produkcyjna) — osobno.

## Pytania otwarte (przekrojowe)
- Mapowanie `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor obry — zrobić w Fazie 2/3 czy osobno? (do rozstrzygnięcia przy planowaniu fazy, która pierwsza dotknie severity).
- Companion na Codex/Pi (Node dependency) — graceful fallback do terminala; szczegóły w Fazie 1.

## Notatki z dyskusji
- Kolejność planowania: naturalna (pipeline).
- Metoda: rewrite-to-unify, baza per fuzja z analizy (hipoteza: obra częściej szkielet, bo community-tested).
- Companion: wchłaniany w Fazie 1 (nie osobna faza).
- Język: dwujęzyczność zachowana (PL user-facing + EN technical) — świadoma konwencja, nie bug.
