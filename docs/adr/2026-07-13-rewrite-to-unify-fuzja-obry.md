# ADR: Metoda fuzji skilli — rewrite-to-unify z bazą wybieraną per fuzja

## Data
2026-07-13

## Status
Accepted

## Kontekst
Faza 2 migracji wchłania mechanikę trzech skilli obry (brainstorming, writing-plans, subagent-driven-development) do trzech skilli domenowych absolutpowers (feature-discuss, generate-tasks, implement). Trzeba zdecydować JAK łączyć treść: doklejać sekcje obry do naszych skilli, doklejać nasze rzeczy do skilli obry, czy przeredagować.

Doklejanie w którąkolwiek stronę produkuje niespójny, warstwowy dokument z dwoma tonami i możliwym dublowaniem mechanizmów (np. blok Interfaces obry vs Context Contract absolutpowers).

## Decyzja
**Rewrite-to-unify:** dla każdej fuzji powstaje nowa, zunifikowana treść zawierająca oba światy, przeredagowana — nie mechaniczny append. Który skill jest **szkieletem** (bazą redakcji) wybieramy **per fuzja na podstawie analizy gęstości warstwy do zachowania**, nie z góry jedną regułą.

Robocza hipoteza wyjściowa: treść obry jest często silniejsza (przetestowana przez community), więc domyślnie kandyduje na szkielet. ALE analiza per fuzja może to odwrócić tam, gdzie warstwa domenowa jest gęsta:
- **feature-discuss** (Faza 1): prawdopodobnie szkielet nasz (ADR/QA/Tryb B/tryb epica = dużo unikalnej warstwy) + wszczepiona mechanika obry (HARD-GATE/sekcje/self-review).
- **generate-tasks** (Faza 2): prawdopodobnie szkielet nasz (orchestrated/grep-AC/project-memory) + bloki writing-plans (Interfaces/Global Constraints/No-Placeholders).
- **implement** (Faza 3): szkielet nasz (orchestrated już dorównuje sdd architekturą) + 4 wstrzyknięte mechanizmy sdd.

Decyzja o bazie każdej fuzji zapada przy planowaniu tej fazy (Tryb B), z jawnym uzasadnieniem w phase docu.

Dwujęzyczność zachowana: materiał obry (EN) przekładany/adaptowany do konwencji PL user-facing + EN technical, nie wklejany surowo.

## Rozważane alternatywy
- **Append sekcji obry do naszych skilli:** — odrzucone, bo produkuje warstwowy dokument z dublami mechanizmów i dwoma tonami; trudny do utrzymania.
- **Append naszych rzeczy do skilli obry:** — odrzucone z tego samego powodu + traci spójność z resztą pipeline'u absolutpowers.
- **Jedna twarda reguła bazy (zawsze obra jako szkielet):** — odrzucone, bo tam gdzie warstwa domenowa jest gęsta (feature-discuss, generate-tasks, implement) obra-jako-szkielet zmusza do przepisania większości i grozi zgubieniem warstwy; wybór per fuzja jest bezpieczniejszy.

## Konsekwencje
- (+) Spójna, jednotonowa treść każdego skilla po fuzji; brak dubli mechanizmów.
- (+) Elastyczność: baza dobrana do tego, gdzie jest więcej do zachowania.
- (−) Więcej pracy redakcyjnej niż append; każda faza wymaga świadomej analizy bazy (nie mechaniczne).
- (Monitorować) Ryzyko zgubienia nośnej sekcji przy przepisaniu → mitygacja: test metodą `writing-skills` (baseline RED → GREEN) w Fazie 5 planu migracji wykrywa regresję zachowania.

## Powiązane
- Planning: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
- Plan migracji: `./plan-migracji-hybrydowej-superpowers.md` (Faza 2/3)
