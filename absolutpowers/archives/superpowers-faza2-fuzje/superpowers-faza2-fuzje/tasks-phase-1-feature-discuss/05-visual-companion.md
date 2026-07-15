# Phase 5: Visual Companion — sekcja przekrojowa + wskaźniki z faz

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: krok 5, Zachowanie #6, AC-7/AC-10/AC-13/AC-14/AC-15
- **Read-only donor:** `skills/feature-discuss/visual-companion.md` (guide EN — pozostaje EN, tu tylko go odwołujemy; szczegóły mechaniki serwera/loop tam)

## Context Contract

### Requires (from previous phases)
- Blok `## HARD-GATE` obecny (Phase 1) — sekcja companion odwołuje się do niego (niedostępność companion ≠ akceptacja designu).

### Provides (for later phases)
- Samodzielna sekcja `## Visual Companion` w `skills/feature-discuss/SKILL.md` (analogicznie do bloku HARD-GATE — mechanizm przekrojowy), opisująca: ofertę just-in-time (własna wiadomość, nie z góry), decyzję per-pytanie (browser dla treści wizualnej, terminal dla konceptualnej), graceful fallback brak-Node → terminal, brak wykonywania kodu z projektu/requestu (statyczny render), niedostępność ≠ akceptacja, tryb nieinteraktywny (gnhf) = rezygnacja bez zawieszenia. Odwołuje `skills/feature-discuss/visual-companion.md` po szczegóły + przypomnienie o `.superpowers/` w `.gitignore`.
- Jednozdaniowe wskaźniki do tej sekcji z faz zadających pytania user-facing: Faza 1 (Zrozumienie), Faza 3 (Propozycja), Faza 4 (Doprecyzowanie). NIE z Fazy 2 (Analiza kodu — brak pytań user-facing).

## Read Scope
- `skills/feature-discuss/SKILL.md`
- `skills/feature-discuss/visual-companion.md` (read-only — sprawdź ścieżkę/nazwę skryptów: `companion-scripts/start-server.sh`, `stop-server.sh`; katalog ekranów `.superpowers/brainstorm/`)

## Write Scope
- `skills/feature-discuss/SKILL.md`

## Objective
Podepnij martwy companion (SKILL.md dziś 0 odwołań): dodaj samodzielną sekcję „Visual Companion" jako mechanizm przekrojowy i wstaw jednozdaniowe wskaźniki z faz pytających (1/3/4). Sekcja adaptuje treść donora do PL user-facing (nie wkleja surowego EN), oddelegowuje szczegóły do `visual-companion.md`, i twardo zabezpiecza edge case'y: brak Node → terminal bez błędu, statyczny render (żadnego kodu z projektu/requestu), niedostępność/brak odpowiedzi ≠ akceptacja designu.

## Tasks

### Task 1: Dodaj samodzielną sekcję „## Visual Companion"
**Status:** completed
**Traces to:** AC-7, AC-10, AC-13, AC-14, AC-15

**Requirements:**
- Dodaj sekcję `## Visual Companion` (mechanizm przekrojowy, samodzielny blok — jak HARD-GATE). Treść PL user-facing, terminy techniczne EN.
- Opisz: oferta **just-in-time** (własna wiadomość, dopiero gdy pytanie zyska na pokazaniu — nie z góry na starcie sesji); decyzja **per-pytanie** (browser dla treści wizualnej: mockup/diagram/porównanie; terminal dla konceptualnej: scope/tradeoff/API).
- **Graceful fallback:** brak dostępnego Node (Codex/Pi, nocny run gnhf) → kontynuuj wyłącznie w terminalu, bez próby uruchomienia companion i bez błędu przerywającego sesję. (AC-10)
- **Bezpieczeństwo:** companion serwuje wyłącznie statyczny render (diagram/HTML) — NIE wykonuje kodu pochodzącego z projektu ani z requestu użytkownika, niezależnie od treści pytania. (AC-13)
- **Gate integrity:** niedostępność/błąd companion (brak Node, zablokowany port, sandbox) NIGDY nie jest domyślną akceptacją designu — HARD-GATE nadal wymaga jawnej akceptacji użytkownika. (AC-14)
- **Tryb nieinteraktywny (gnhf):** brak człowieka do kliknięcia/odpowiedzi → brak odpowiedzi = rezygnacja z companion, proces kontynuuje bez niego, sesja się nie zawiesza. (AC-15)
- Odwołaj `skills/feature-discuss/visual-companion.md` po szczegóły (uruchomienie serwera, loop, format ekranów) — nie kopiuj mechaniki serwera do SKILL.md.
- Dodaj przypomnienie: dopisać `.superpowers/` do `.gitignore` (katalog ekranów companion nie idzie do repo).

**Tests (grep-verifiable):**
- `grep -n "## Visual Companion" skills/feature-discuss/SKILL.md` → sekcja obecna.
- Odwołanie do guide: `grep -n "visual-companion.md" skills/feature-discuss/SKILL.md` → ≥1.
- Fallback/no-Node: `grep -niE "brak.*Node|bez Node|Node.*niedostęp|fallback.*terminal" skills/feature-discuss/SKILL.md`.
- Gate integrity: `grep -niE "niedostępn.*nie.*akceptacj|nie.*domyśln.*akceptacj|nadal wymaga.*akceptacj" skills/feature-discuss/SKILL.md`.
- gitignore reminder: `grep -n ".superpowers" skills/feature-discuss/SKILL.md` → ≥1 (w rejonie companion).

### Task 2: Wskaźniki do sekcji companion z faz 1/3/4
**Status:** completed
**Traces to:** AC-7

**Requirements:**
- Dodaj jednozdaniowy wskaźnik „gdy pytanie zyska na pokazaniu — patrz sekcja Visual Companion" (lub równoważny PL) w: **Faza 1** (Zrozumienie potrzeby), **Faza 3** (Propozycja rozwiązania), **Faza 4** (Doprecyzowanie).
- NIE dodawaj wskaźnika w **Faza 2** (Analiza kodu — brak pytań user-facing).
- Wskaźnik ma być krótki (jedno zdanie) i tylko kierować do sekcji przekrojowej, nie powtarzać jej treści.

**Tests (grep-verifiable):**
- ≥3 odwołania do „Visual Companion" łącznie (sekcja + wskaźniki): `grep -c "Visual Companion" skills/feature-discuss/SKILL.md` → ≥ 4 (1 nagłówek sekcji + 3 wskaźniki).
- Ręcznie: brak wskaźnika w rejonie „### Faza 2: Analiza kodu".

## Phase Verification
Run:
- `python3 -c "import yaml; yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print('FM OK')"`
- `grep -c "Visual Companion" skills/feature-discuss/SKILL.md` → ≥ 4.
- `grep -c "visual-companion.md" skills/feature-discuss/SKILL.md` → ≥ 1.
- Ręcznie potwierdź: Faza 2 bez wskaźnika companion; edge case'y AC-10/13/14/15 pokryte w sekcji.

## Completion Criteria
- Wszystkie taski fazy `completed`.
- Zmiany w Write Scope (SKILL.md); `visual-companion.md` NIEtknięty (read-only).
- Phase verification przechodzi.
- `implementation-context.md` zaktualizowany (nagłówek sekcji companion, że frontmatter-grant przyjdzie w Phase 6).
- Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Nowa sekcja `## Visual Companion — wizualne wspomaganie dyskusji` wstawiona bezpośrednio po bloku HARD-GATE (po akapicie rekoncyliacji micro-change), przed `## Router trybu` — analogiczne miejsce przekrojowe jak HARD-GATE, tak żeby wskaźniki z Faz 1/3/4 mogły odwoływać się "wyżej" w pliku.
- Sekcja zawiera 7 akapitów (każdy z pogrubionym leadem): just-in-time offer, decyzja per-pytanie, graceful fallback brak-Node, bezpieczeństwo (statyczny render), gate integrity (niedostępność ≠ akceptacja), tryb nieinteraktywny (gnhf), odwołanie do `visual-companion.md` po szczegóły serwera/pętli/CSS + przypomnienie `.superpowers/` w `.gitignore`.
- Kanoniczna fraza gate integrity (grep-verifiable, użyj tej samej jeśli kolejna faza odwołuje się do tego pomysłu): "niedostępność ≠ akceptacja" + "HARD-GATE ... nadal wymaga jawnej, wprost wyrażonej akceptacji użytkownika".
- Wskaźniki-jednozdaniowe wstawione: Faza 1 (tuż przed `ZASADA: JEDNO PYTANIE NA TURĘ`), Faza 3 (tuż przed `#### Prezentacja designu sekcjami`), Faza 4 (tuż przed `Pamiętaj: jedno pytanie na turę...`). Faza 2 celowo pominięta (brak pytań user-facing) — zweryfikowane awk-em że region Fazy 2 nie zawiera frazy "Visual Companion".
- `grep -c "Visual Companion" skills/feature-discuss/SKILL.md` = 4 (1 nagłówek + 3 wskaźniki) — dokładnie zgodne z minimum testu.
- `visual-companion.md` pozostał NIEtknięty (`git diff --stat` pusty) — potwierdzone read-only.
- Frontmatter-grant (`allowed-tools` dla `companion-scripts/*` i Write `.superpowers/brainstorm/**`) świadomie NIE dodany w tej fazie — przypisany do Fazy 6 (rozszerzenie `allowed-tools`) zgodnie z planningiem (krok 5a).
</content>
