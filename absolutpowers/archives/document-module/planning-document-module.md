# document-module — architektura modułu ze skanu kodu (C4 + HTML)

## Status
Zaimplementowane (v3.8.0). Skill w obu drzewach (Claude + Codex).

## Problem
Repo ma cztery mechanizmy dokumentacji, ale żaden nie produkuje **architektonicznej dokumentacji
istniejącego modułu ze skanu kodu, z diagramami**:
- `document-feature` — proza per-moduł z JEDNEGO feature'a (planning + diff), inkrementalnie. Nie
  skanuje całego modułu, brak diagramów.
- `explain` — ephemeralny HTML jednej zmiany dla człowieka. Per-zmiana, nietrwały.
- `update-ai-context` — szeroki płytki skan repo → CLAUDE.md. Płytki, bez diagramów, nie per-moduł deep.

Brak odpowiedzi na: "zrób mi dokumentację modułu X — jak jest teraz, ze skanu kodu, z diagramami
C4 + Mermaid, HTML dla człowieka i markdown dla AI".

## Użytkownicy
Developer/architekt chcący na żądanie zrozumieć/przekazać architekturę modułu (człowiek przez HTML)
oraz AI-jako-nowy-dev czytający markdown przed rozbudową modułu.

## Oczekiwane zachowanie
- Wejście: nazwa modułu lub ścieżka.
- Skan kodu modułu: publiczne API, komponenty, zależności in/out, persystencja, kluczowe przepływy.
- Diagramy C4 (C1 Context / C2 Container / C3 Component) + sekwencyjne kluczowych operacji.
- Output: markdown (źródło prawdy, AI) `docs/modules/{slug}-architecture.md` + self-contained HTML
  (człowiek) `docs/architecture/{slug}.html`.
- Audytowalność: zweryfikowane (z kodu) vs wnioskowane.

## Wybrane rozwiązanie
Nowy skill `document-module`. Pożycza detekcję modułu + `doc-meta` z `document-feature`, a
generowanie HTML/Mermaid + zasadę audytowalności z `explain`.

### Decyzje (zatwierdzone w dyskusji)
1. **Osobny plik architektury** — `docs/modules/{slug}-architecture.md` + `docs/architecture/{slug}.html`.
   `document-feature` zostaje prozą `docs/modules/{slug}.md`. Zero kolizji merge, komplementarne,
   krzyżowo linkowane. (Odrzucono: tryb bootstrap tego samego pliku — ryzyko kolizji logiki merge;
   jeden łączony doc — miesza dwa cykle życia/źródła.)
2. **Oba formaty** — markdown z Mermaid (AI, durable, **źródło prawdy**) + HTML (człowiek).
   (Odrzucono: tylko markdown — gorzej dla człowieka; tylko HTML — gorszy kontekst dla AI, gnije.)
3. **Zakres C4: C1–C3 + flow.** C4 code-level pominięty — gnije najszybciej, duplikuje kod.
4. **HTML regenerowalny, nie edytowalny ręcznie** — zawsze nadpisywany ze skanu (artefakt build).
   Markdown = źródło prawdy. (Stąd różnica vs `explain`, który dodaje sufiks `-v2` jako snapshot.)

### Detekcja modułu
CLAUDE.md `## Project Structure` / `patterns.md` → ścieżka wprost od usera → fallback heurystyka
ścieżek → sanityzacja nazwy do slug (jak `document-feature` KROK 2). Echo granicy bez twardego gate
(user nazwał moduł, git diff = review).

## Zakres
### In scope
- `claude/skills/document-module/SKILL.md` + `codex/skills/document-module/SKILL.md`
- Notki "vs document-module" w `document-feature` i `explain` (oba drzewa)
- Nowe katalogi wyjściowe `docs/modules/{slug}-architecture.md`, `docs/architecture/{slug}.html`
- README + CLAUDE.md, bump 3.7.0 → 3.8.0

### Out of scope
- C4 code-level (poziom klas/metod).
- Auto-regeneracja przy zmianie kodu (na żądanie; drift wykrywalny przez `doc-meta last-commit`).
- Gate (echo granicy wystarcza; output do dedykowanych plików, niskie ryzyko, git diff = review).

## Pliki do zmodyfikowania / utworzenia
- NEW `claude/skills/document-module/SKILL.md`, `codex/skills/document-module/SKILL.md`
- NEW `absolutpowers/feature/planning-document-module.md` (ten plik)
- MOD `claude|codex/skills/document-feature/SKILL.md` (notka "vs")
- MOD `claude|codex/skills/explain/SKILL.md` (notka "vs")
- MOD `README.md`, `CLAUDE.md`
- MOD oba `plugin.json` (3.8.0)

## Edge cases i ryzyka
- Mermaid C4 syntax bywa kruchy → fallback na `graph/flowchart`, walidacja `mermaid-cli` jeśli dostępne.
- Wnioskowane relacje podane jako fakt → zasada audytowalności (oznaczanie).
- Trigger collision z `document-feature`/`explain` → wąski TRIGGER + notki "vs" w obu.
- HTML gnije → traktowany jako regenerowalny, markdown źródłem prawdy.

## Pytania otwarte
- (ROZSTRZYGNIĘTE) Spięte z harvest jako KROK 3: auto-odświeżanie/tworzenie architektury
  dotkniętego modułu, ale TYLKO przy zmianie architektury (nowy plik / nowy publiczny element /
  nowa zależność). Bootstrap NEW włączony. Bramka chroni przed churnem z niedeterministycznej
  generacji diagramów. Skill nadal dostępny on-demand.

## Notatki z dyskusji
Powstało z pytania "czego mi brakuje" — generowanie dokumentacji dla człowieka (HTML, Mermaid, C4).
Kluczowe było odróżnienie od trzech istniejących mechanizmów, by nie dublować (grzech główny repo =
dryf/overlap). Wszystkie trzy decyzje projektowe = rekomendacje (osobny plik / oba formaty / C1–C3).
