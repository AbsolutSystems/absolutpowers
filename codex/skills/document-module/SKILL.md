---
name: document-module
description: >
  Generuje architektoniczną dokumentację ISTNIEJĄCEGO modułu ze skanu jego kodu:
  struktura, publiczne API, zależności, kluczowe przepływy + diagramy C4 (C1–C3) i sekwencyjne.
  Output: markdown (AI, źródło prawdy) w docs/modules/{slug}-architecture.md + self-contained HTML
  (człowiek) w docs/architecture/{slug}.html.
  TRIGGER when: "udokumentuj architekturę modułu", "architektura modułu X", "diagram modułu",
  "C4 modułu", "document module architecture", "narysuj jak działa moduł", "dokumentacja modułu
  ze skanu kodu", "zrób dokumentację modułu z diagramami".
  NIE wyzwalaj na: dokumentację z zakończonego feature'a (to `document-feature`) ani wyjaśnienie
  konkretnej zmiany/planu (to `explain`).
---

# Document Module — Architektura modułu ze skanu kodu

Jesteś inżynierem-architektem dokumentalistą. Bierzesz **istniejący moduł** i ze **skanu jego
kodu** budujesz dokumentację architektoniczną: jak jest zbudowany, co wystawia, od czego zależy,
jak płyną kluczowe operacje — z diagramami C4 (C1–C3) i sekwencyjnymi. Dwóch odbiorców: **człowiek**
(HTML) i **AI-jako-nowy-dev** (markdown).

**To NIE jest implementacja.** Nie piszesz kodu produktu. Zapisujesz tylko
`docs/modules/{slug}-architecture.md` i `docs/architecture/{slug}.html` w target-projekcie.

## Czym to NIE jest (granice)

- ≠ `document-feature` — tamten robi **prozę** "jak działa + dlaczego" z JEDNEGO feature'a (planning
  + diff), inkrementalnie, do `docs/modules/{slug}.md`. Tu: **struktura + diagramy** ze skanu CAŁEGO
  modułu, on-demand, do osobnego pliku `*-architecture.md`. Komplementarne — linkuj krzyżowo.
- ≠ `explain` — tamten to **ephemeralny** HTML jednej zmiany/planu (per-zmiana, snapshot). Tu:
  **durable** architektura modułu, regenerowalna.
- ≠ `update-ai-context` — tamten skanuje CAŁE repo → broad/shallow AGENTS.md. Tu: deep, jeden moduł, z diagramami.

## Wejście

`$ARGUMENTS` = nazwa modułu (np. `auth`) lub ścieżka (np. `src/billing`).

$ARGUMENTS

---

## KROK 1: Rozwiąż moduł → zbiór plików

Ustal granicę modułu i zbiór jego plików:

**Primary (źródło prawdy o strukturze):**
- `AGENTS.md` → `## Project Structure` (mapowanie katalogów na moduły/odpowiedzialności).
- `./absolutpowers/patterns.md` jeśli istnieje (struktura modułów).

**Gdy user podał ścieżkę wprost** (`src/billing`) — użyj jej jako granicy.

**Fallback (heurystyka ścieżek):** gdy brak mapy lub nie pokrywa — top-level katalog pod `src/`
albo pakiet/namespace: `auth` → `src/auth/**`, `billing` → `packages/billing/**`.

**Sanityzacja nazwy → slug pliku:** znaki specjalne (`@scope/pkg`, kropki, slashe) → kebab-case
(`@acme/auth-core` → `auth-core`). Pliki: `docs/modules/{slug}-architecture.md`, `docs/architecture/{slug}.html`.

**Echo granicy** (NIE twardy gate — user nazwał moduł, git diff = review):
```
Moduł `auth` → granica: src/auth/**
Pliki w zakresie (N): src/auth/login.ts, src/auth/session.ts, ...
Generuję dokumentację architektury.
```
Jeśli zakres pusty / moduł nie istnieje → zaraportuj i zakończ BEZ zapisu.

## KROK 2: Skan kodu (ŹRÓDŁO PRAWDY)

Czytaj/przeszukuj moduł. Skanuj kod, nie zgaduj z nazw. Wyciągnij:

- **Publiczne API / powierzchnia** — eksporty, publiczne klasy/metody, endpointy (HTTP/RPC),
  zdarzenia publikowane/konsumowane. Notuj `file:line`.
- **Komponenty wewnętrzne** — główne klasy/serwisy/warstwy modułu + ich odpowiedzialności.
- **Zależności in/out:**
  - **Out** (moduł zależy od) — importy modułu na zewnątrz (inne moduły, biblioteki, bazy, serwisy).
  - **In** (zależą od modułu) — kto importuje/woła moduł (grep po nazwie modułu/eksportach w repo).
- **Persystencja / integracje zewnętrzne** — bazy, kolejki, zewnętrzne API, pliki.
- **Kluczowe operacje / przepływy** — 1–3 najważniejsze ścieżki (np. „logowanie", „wystawienie faktury")
  od wejścia do efektu.

## KROK 3: Audytowalność (zweryfikowane vs wnioskowane)

Reguła naczelna (jak w `explain`): przy każdej istotnej relacji czytelnik musi wiedzieć, czy to
fakt z kodu czy wniosek.
- **Zweryfikowane** — „widać w kodzie", `file:line`.
- **Wnioskowane** — „zakładam", „prawdopodobnie". Oznacz wprost, NIE podawaj jako fakt.

Przekonująco brzmiąca konfabulacja architektury jest gorsza niż luka. Czego nie ustaliłeś z kodu →
oznacz jako założenie, nie wpisuj jako pewnik do diagramu.

## KROK 4: Diagramy Mermaid (C1–C3 + flow)

Generuj na podstawie skanu (nie szablonowo):
- **C1 Context** (`C4Context`) — moduł vs świat zewnętrzny (użytkownicy/systemy, z którymi gada).
- **C2 Container** (`C4Container`) — procesy/serwisy/bazy w obrębie i wokół modułu.
- **C3 Component** (`C4Component`) — główne komponenty/serwisy wewnątrz modułu i ich relacje.
- **Przepływy** (`sequenceDiagram`) — 1–3 kluczowe operacje z KROK 2.

Zasady (jak `explain`): każdy diagram prosty (max ~15 węzłów), rozbij molochy na kilka mniejszych.
Etykiety bez niedozwolonych znaków.

**Walidacja składni:** jeśli dostępne `npx @mermaid-js/mermaid-cli` — zwaliduj każdy diagram; jeśli
nie — przejdź składnię ręcznie (domknięte nawiasy, poprawne strzałki). Błędny diagram renderuje się
jako pusty prostokąt. **Fallback:** gdy `C4*` syntax ryzykowny/nie waliduje — użyj `graph TD`/
`flowchart` z tą samą treścią. Lepszy prosty działający diagram niż ambitny zepsuty.

## KROK 5: Zapis markdown (ŹRÓDŁO PRAWDY)

Zapisz `docs/modules/{slug}-architecture.md` wg szablonu niżej. Utwórz `docs/modules/` jeśli brak.
Stempluj `doc-meta` w ciele (nie frontmatter): `last-updated` (dzisiejsza data), `last-commit`
(`git rev-parse --short HEAD`), `source: code-scan`. Krzyżowy link do `docs/modules/{slug}.md`
(proza z `document-feature`), jeśli istnieje.

## KROK 6: Zapis HTML (REGENEROWALNY)

Zapisz `docs/architecture/{slug}.html`. Utwórz `docs/architecture/` jeśli brak.
- Self-contained `.html`, działa po otwarciu w przeglądarce bez serwera.
- Mermaid przez CDN: `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>`
  + `mermaid.initialize({startOnLoad:true})`. Te same diagramy co w markdown.
- Czysty CSS inline, karty sekcji, `prefers-color-scheme` (jasny i ciemny), max-width ~900px.
- Spis treści z kotwicami; legenda zweryfikowane vs wnioskowane (badge/kolor, konsekwentnie).
- Stopka: data generowania, moduł, `last-commit`.
- Język: polski.
- **NADPISUJ** istniejący plik (≠ `explain` z sufiksem `-v2`). HTML to regenerowalny artefakt
  build — zawsze odzwierciedla aktualny skan. Markdown jest źródłem prawdy; HTML się go nie trzyma kurczowo.

---

## Szablon markdown

```markdown
# Architektura modułu: {nazwa}

<!-- doc-meta
last-updated: YYYY-MM-DD
last-commit: <sha>
source: code-scan
-->

## Przegląd i granice
[Co to, za co odpowiada, gdzie się zaczyna/kończy]

## C1 — Context
\`\`\`mermaid
C4Context
...
\`\`\`

## C2 — Container
\`\`\`mermaid
C4Container
...
\`\`\`

## C3 — Component
\`\`\`mermaid
C4Component
...
\`\`\`

## Kluczowe przepływy
\`\`\`mermaid
sequenceDiagram
...
\`\`\`

## Publiczne API / kontrakty
[Eksporty, endpointy, sygnatury — z `file:line`. Oznacz zweryfikowane vs wnioskowane]

## Zależności
- **Out** (moduł zależy od): ...
- **In** (zależą od modułu): ...

## Mapa plików
- `ścieżka` — [rola]

## Pułapki / na co uważać
[Przy rozbudowie]

> Proza/decyzje: zob. `docs/modules/{slug}.md` (document-feature), jeśli istnieje.
```

### Reguła: `doc-meta` w CIELE, nie we frontmatter
`doc-meta` MUSI być komentarzem HTML w ciele docu (zaraz pod nagłówkiem), jednolicie z
`document-feature`/`try-learn-skill`. Pola: `last-updated`, `last-commit`, `source: code-scan`.

---

## Zasady

- **Markdown = źródło prawdy; HTML = regenerowalny** (zawsze nadpisuj ze skanu, nie edytuj ręcznie).
- **Źródło = skan kodu**, nie planning/diff (to `document-feature`).
- **Jednostka = MODUŁ.** Jeden moduł na wywołanie (kilka → pętla).
- **Audytowalność**: zweryfikowane vs wnioskowane, konsekwentnie.
- **C1–C3 + flow**; C4 code-level pomijamy (gnije, duplikuje kod).
- **Write tylko do `docs/modules/` i `docs/architecture/`** target-projektu, NIE do repo AbsolutPowers.
- **Brak materiału / pusty moduł → zakończ czysto** bez tworzenia plików.
