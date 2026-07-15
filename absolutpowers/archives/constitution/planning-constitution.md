# constitution — pryncypia projektu jako pierwszorzędna ceremonia

## Status
Propozycja (do akceptacji). Inspiracja: `/speckit.constitution` z github/spec-kit. Wersja: część zbiorczego bumpu 3.8.0 → 3.9.0 (analyze + constitution + tasks-to-issues + debug-handoff w jednym wydaniu).

## Problem
W AbsolutPowers reguły projektu (`absolutpowers/rules.md`) powstają jako **Faza 3 skilla
`update-ai-context`** — efekt uboczny skanu kodu, "proponuję, nie narzucam". To dobre dla reguł
**mechanicznych** ("nie używaj X", "kontrolery dziedziczą po Y"), ale brakuje warstwy wyżej:
**pryncypiów** — niezmienników i heurystyk decyzyjnych, które rządzą feature-discuss, generate-tasks,
implement i review ("optymalizujemy czytelność ponad spryt", "zero breaking changes API bez ADR",
"multi-tenancy to granica bezpieczeństwa, nigdy obejście").

Dziś takie pryncypia żyją rozproszone: część w CLAUDE.md, część w rules.md, część w głowie
architekta. Nie ma jednego ratyfikowanego, wersjonowanego źródła, do którego pipeline się odnosi
jako do **kontraktu nadrzędnego**. spec-kit traktuje constitution jako pierwszy krok i first-class
artefakt; u nas reguły to derywat skanu.

## Użytkownicy
Architekt/tech-lead ustalający niezmienniki projektu raz, a potem egzekwujący je przez cały
pipeline. Wejście: dyskusja o wartościach/granicach projektu (lub skan istniejącego kodu jako
materiał wyjściowy). Oczekiwanie: ratyfikowany dokument-konstytucja, wersjonowany, do którego
generate-tasks/implement/review odnoszą się jako do twardego kontekstu.

## Oczekiwane zachowanie
- Dedykowany skill `constitution` — **świadoma ceremonia**, nie efekt uboczny skanu.
- Tworzy/aktualizuje `absolutpowers/constitution.md` jako zestaw **artykułów** (pryncypia),
  każdy z: nazwą, treścią normatywną (MUST/SHOULD/NEVER), uzasadnieniem, opcjonalnie przykładem.
- **Wersjonowanie + proces poprawek:** semver konstytucji, data ratyfikacji, changelog amendmentów.
  Zmiana = jawna ratyfikacja przez użytkownika (human approval), nigdy auto-nadpisanie.
- **Tier rozdzielny od rules.md:** constitution = pryncypia (WHY/wartości/granice), rules.md =
  mechaniczne constrainty review (lint-level). Konstytucja może *rodzić* reguły, ale to różne pliki.
- **Wpięcie jako kontekst wiążący:** generate-tasks i implement czytają konstytucję jako binding
  (obok patterns.md/rules.md/ADR); review egzekwuje pryncypia jako osobny check.
- Bootstrap (skan kodu → propozycja artykułów) vs Amend (audyt: czy kod systematycznie łamie
  artykuł → flaga, że artykuł martwy lub kod do naprawy).

### Struktura `constitution.md`
```markdown
# Konstytucja projektu — {nazwa}
> Wersja: 1.2.0 · Ratyfikowano: 2026-06-19 · Egzekwowana przez: generate-tasks, implement, review

## Artykuł I: {Nazwa pryncypium}
**Norma:** {MUST/SHOULD/NEVER ...}
**Dlaczego:** {uzasadnienie}
**Jak stosować:** {konkret w kontekście pipeline}
**Przykład:** {opcjonalnie kod / sytuacja}

## Artykuł II: ...

## Changelog
- 1.2.0 (2026-06-19): dodano Artykuł V (granice multi-tenancy)
- 1.1.0 (2026-05-02): ...
```

## Wybrane rozwiązanie
Nowy skill `constitution` w obu drzewach + nowy plik `absolutpowers/constitution.md`, **odrębny**
od rules.md.

**Kluczowa decyzja — dwa pliki, nie jeden:**
- `constitution.md` = pryncypia/wartości/granice (tier strategiczny, ratyfikowany, rzadko zmieniany).
- `rules.md` = mechaniczne constrainty review (tier taktyczny, derywat kodu, częściej odświeżany).

Rozdzielenie, bo mieszają się dwie prędkości i dwie natury: "optymalizujemy X ponad Y" (osąd) vs
"kontrolery rozszerzają BaseController" (mechanika). Scalanie ich rozmywałoby ceremonię ratyfikacji.

`update-ai-context` Faza 3 (rules) zostaje, ale dostaje notkę: reguły mechaniczne tu, pryncypia
w `constitution` (i może odnosić proponowane reguły do istniejących artykułów).

### Uzasadnienie
- Promuje pryncypia z efektu ubocznego do świadomej, wersjonowanej ceremonii.
- Daje pipeline'owi jeden nadrzędny kontrakt zamiast wiedzy rozproszonej w CLAUDE.md/głowie.
- Rozdział constitution/rules trzyma dwie natury (osąd vs mechanika) rozłączne i czytelne.

### Rozważane alternatywy
- **Elevacja `rules.md` do konstytucji (jeden plik)** — odrzucone: miesza pryncypia (osąd, rzadka
  zmiana, ratyfikacja) z regułami mechanicznymi (derywat kodu, częsta zmiana). Jeden plik = jedna
  prędkość zmian, a tu są dwie.
- **Faza w `update-ai-context`** — odrzucone: pryncypia to nie efekt skanu kodu; ich źródłem jest
  decyzja architekta. Ceremonia ratyfikacji nie pasuje do "auto-odśwież docs".
- **Sekcja w root CLAUDE.md** — odrzucone: brak wersjonowania, brak procesu poprawek, miesza się
  z dokumentacją techniczną dla agenta.

## Zakres
### In scope
- `claude/skills/constitution/SKILL.md` + `codex/skills/constitution/SKILL.md`
- Nowy plik wynikowy `absolutpowers/constitution.md` (tworzony przez skill)
- MOD: `generate-tasks`, `implement` — czytają `constitution.md` jako binding context (oba drzewa)
- MOD: `review` — Faza "zgodność z pryncypiami" odnosi się do konstytucji (oba drzewa)
- MOD: `update-ai-context` — notka rozgraniczająca rules.md ↔ constitution.md (oba drzewa)
- Aktualizacja README.md, CLAUDE.md
- Bump wersji (oba manifesty)

### Out of scope
- Auto-generowanie reguł mechanicznych z artykułów (na razie ręczne; możliwe później).
- Wymuszanie konstytucji jako twardej bramki blokującej (review *raportuje* naruszenia, nie blokuje
  builda; egzekucja = przez istniejące gate'y review).
- Migracja istniejących rules.md → constitution.md (skill proponuje, nie przenosi automatycznie).

## Decyzje do zatwierdzenia
1. **Dwa pliki (constitution + rules) czy jeden** — rekomendacja: dwa (uzasadnienie wyżej).
2. **Wersjonowanie konstytucji** semverem — akceptowalne, czy wystarczy data + changelog?
3. **Egzekucja w review** — pryncypia jako osobna faza review czy rozszerzenie istniejącej Fazy 3
   (rules check)? Rekomendacja: rozszerzyć Fazę 3 o sekcję "Pryncypia (constitution)".
4. **Wersja pluginu:** jeden zbiorczy bump 3.8.0 → 3.9.0 dla wszystkich czterech feature'ów (decyzja: bundle).

## Pliki do zmodyfikowania / utworzenia
- NEW `claude/skills/constitution/SKILL.md`
- NEW `codex/skills/constitution/SKILL.md`
- NEW `absolutpowers/feature/planning-constitution.md` (ten plik)
- MOD `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
- MOD `claude/skills/implement/SKILL.md`, `codex/skills/implement/SKILL.md`
- MOD `claude/skills/review/SKILL.md`, `codex/skills/review/SKILL.md`
- MOD `claude/skills/update-ai-context/SKILL.md`, `codex/skills/update-ai-context/SKILL.md`
- MOD `README.md`, `CLAUDE.md`
- MOD `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`

## Edge cases i ryzyka
- **Redundancja z rules.md** → mitygacja: ostry rozdział natur (osąd vs mechanika) + notka w obu
  skillach; skill `constitution` odsyła reguły mechaniczne do `update-ai-context`.
- **Konstytucja ignorowana przez pipeline** (martwy dokument) → wpięcie jako binding context w
  generate-tasks/implement + egzekucja w review; bez tego dokument byłby ozdobą.
- **Konflikt artykuł ↔ kod** w Amend mode → skill flaguje (artykuł martwy lub kod do naprawy),
  nie nadpisuje; decyzja człowieka.
- **Scope creep** (skill zaczyna pisać reguły mechaniczne) → twarda granica: pryncypia tu, mechanika
  w update-ai-context.
- **Trigger collision z `update-ai-context`** → wąski TRIGGER (pryncypia / konstytucja / ratyfikacja
  / niezmienniki) + notka "vs constitution".

## Pytania otwarte
- Czy `feature-discuss` powinien też czytać konstytucję (żeby projekt rozwiązania respektował
  pryncypia od początku)? Skłaniam się ku tak — dopisać jako lekki kontekst.
- Czy bootstrap konstytucji powinien proponować artykuły ze skanu kodu, czy czysto z dyskusji?
  Rekomendacja: hybryda — skan jako materiał, ale artykuły rodzą się z potwierdzenia architekta.

## Notatki z dyskusji
Z porównania do spec-kit: tam `constitution` to krok pierwszy i first-class artefakt rządzący
resztą. U nas reguły to derywat skanu w update-ai-context — brak warstwy pryncypiów i ceremonii
ratyfikacji. Kluczowe rozstrzygnięcie projektowe: rozdzielić pryncypia (osąd, rzadka zmiana) od
reguł mechanicznych (derywat kodu, częsta zmiana) — dwa pliki, dwie prędkości.
