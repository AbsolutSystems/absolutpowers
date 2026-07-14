# ADR: Fuzja generate-tasks ← writing-plans — szkielet i rekoncyliacje (Faza 2)

## Data
2026-07-13

## Status
Accepted

## Kontekst
Faza 2 epica "fuzja mechaniki obry" wszczepia mechanikę `writing-plans` obry do `generate-tasks` metodą rewrite-to-unify (ADR wspólny: `2026-07-13-rewrite-to-unify-fuzja-obry.md`). writing-plans dostarcza 5 mechanizmów; trzy są tanie (No-Placeholders, Self-Review, Global Constraints), dwa kolidują z istniejącymi mechanizmami generate-tasks i wymagają rozstrzygnięcia zanim powstaną taski:

1. Który skill jest szkieletem fuzji (baza rewrite'u)?
2. Blok Interfaces (Consumes/Produces per-TASK, dokładne sygnatury) vs istniejący Context Contract (Requires/Provides per-PHASE).
3. Struktura zadania: rigid 5-step TDD checkbox template obry (kompletny kod w każdym kroku) vs istniejący Requirements/Tests/Example + Test-first marker.
4. Global Constraints (spec-derived) vs constitution.md (binding-context) — jedna sekcja czy dwie.

## Decyzja

**1. Szkielet = generate-tasks.** Wszczepiamy mechanikę writing-plans w gotowy szkielet generate-tasks, nie odwrotnie. Powód: generate-tasks ma 624 linie gęstej warstwy domenowej (orchestrated/single-file, grep-AC, AC-traceability, epic subfolder, Test-first marker, review gate, constitution/ADR/project-memory), writing-plans 175 linii czystej mechaniki. Więcej do stracenia po stronie domeny → mniejsze ryzyko przy grafcie mechaniki w domenę. Świadome odstępstwo od domyślnej hipotezy epica ("obra częściej szkielet, bo community-tested") — uzasadnione gęstością domeny tego skilla, identycznie jak w Fazie 1.

**2. Interfaces WSPÓŁISTNIEJĄ z Context Contract na dwóch poziomach (nie unifikacja, nie duplikacja).** Task dostaje pola `Produces:`/`Consumes:` z dokładnymi sygnaturami. Phase `Context Contract → Provides` = rollup `Produces` przekraczających granicę fazy, z twardą regułą: **nie powtarzaj within-phase**. W single-file (brak faz) Interfaces działa task↔task bez rollupu. Type-consistency między zadaniami staje się grep-owalne w self-review. Zero równoległej duplikacji: jeden mechanizm, dwa poziomy granularności.

**3. Struktura zadania: DYSCYPLINA obry, nie SZABLON.** Zostaje format Requirements/Tests/Example + Test-first marker. Przejmujemy dyscyplinę writing-plans (dokładne sygnatury via Produces/Consumes, realny kod w Example, zero vague via No-Placeholders), ale NIE rigid 5-step TDD checkbox template. Powód rozstrzygający: podział modeli **Opus planuje / Sonnet implementuje**. 5-step template zakłada najtańszy model-transkryptor (obra: tani model przepisuje kroki) — którego w implement nie ma; Sonnet to zdolny model wykonawczy. Kod pisany wewnątrz planu jest niezweryfikowany (Opus nie uruchamia testów w trakcie planowania); Sonnet piszący kod live iteruje przeciw realnym failom. Plan = kontrakt + decyzje; implement = autonomiczne wykonanie. Test-first marker (decyzja per-zadanie) zostaje właścicielem decyzji TDD; implement ją honoruje.

**4. Global Constraints i constitution.md = DWIE sekcje, GC cytuje constitution.** Global Constraints = osobna sekcja nagłówka tasks doc, spec-derived verbatim (cross-task wymagania TEGO feature'a). Może cytować wiążące artykuły constitution jako referencję (`Per Artykuł N`), ale nie kopiuje treści pryncypiów. Constitution.md nadal wczytywany osobno jako binding-context. Rozłączne zakresy: GC (spec-scoped) / constitution (project-scoped) / rules (lint).

## Rozważane alternatywy
- **Szkielet = writing-plans + wszczepienie domeny** — odrzucone: odtwarzanie 624 linii domeny w 175-liniowym szkielecie = większy nakład i ryzyko regresji.
- **Interfaces zastępuje Context Contract (unifikacja w jeden poziom)** — odrzucone: gubi rozdział task↔phase; single-file straciłby type-consistency albo orchestrated straciłby handoff fazowy.
- **Dwa równoległe mechanizmy (dosłowna kopia obry)** — odrzucone: duplikacja Provides/Produces → rozjazd przy aktualizacji jednego; rozdęcie phase file.
- **Pełny 5-step TDD template (P1-B)** — odrzucone: sprzęga Fazę 2 ↔ Fazę 3 (wymusza implement→transkryptor), marnuje split Opus/Sonnet, front-loaduje niezweryfikowany kod, ~2× tokeny na zadanie, blast radius na rubryki gate.
- **Hybryda per marker (P1-C)** — odrzucone na teraz: dwa formaty zadania w pliku → koszt parsowania; enforcement zbędny przy autonomicznym Sonnecie. Rezerwa gdyby Faza 5 pokazała drift od test-first.
- **GC absorbuje constitution (jedna sekcja)** — odrzucone: miesza zakresy → dryf pryncypiów w kopiach starych tasks docs; dublowanie binding-context.

## Konsekwencje
- (+) Warstwa domenowa generate-tasks zachowana w całości; mechanika obry wzmacnia strukturę zadania i self-review.
- (+) Type-consistency między zadaniami staje się sprawdzalny (Produces↔Consumes), także w single-file.
- (+) Podział Opus-plan/Sonnet-implement zachowany — plan kontraktem, implement autonomicznym wykonawcą.
- (+) Rozłączne źródła constraintów (GC/constitution/rules) bez dryfu.
- (−/monitorować) Reguła anty-dup Produces↔Provides wymaga osądu plannera — self-review + kryterium review-tasks łapią rozjazd.
- (−/monitorować) Ryzyko skopiowania treści constitution do GC zamiast cytatu — instrukcja twarda w SKILL.md.
- (−/monitorować) Rozdęcie SKILL.md (624 + 5 graftów) — mitygacja rewrite-to-unify (konsolidacja rozproszonych uwag "complete code" w No-Placeholders).
- Severity taksonomia `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor NIE rozstrzygana tutaj (self-review nie emituje severity) — punktowana do Fazy 3.

## Powiązane
- Planning: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-2-generate-tasks.md`
- Epic: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
- ADR wspólny: `./docs/adr/2026-07-13-rewrite-to-unify-fuzja-obry.md`
- ADR Fazy 1 (precedens szkielet-per-gęstość): `./docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`
