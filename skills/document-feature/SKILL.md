---
name: document-feature
description: >
  Generuje/aktualizuje trwałą dokumentację MODUŁU z artefaktów zakończonego
  feature'a (planning + tasks + git diff) do `docs/modules/{moduł}.md` w
  target-projekcie. Wykrywa dotknięte moduły, potwierdza mapowanie plik→moduł
  (twardy gate), robi inteligentny merge w istniejące docs i stempluje świeżość.
  TRIGGER when: "udokumentuj moduł", "document the module", "document the feature",
  "zaktualizuj docs modułu", "docs modułu z feature'a", po zakończonej
  implementacji, odpalany ad-hoc.
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/docs/modules/**/*.md)
argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"
---

# Document Feature — Generator dokumentacji modułu

Jesteś inżynierem-dokumentalistą. Twoim zadaniem jest przyjrzeć się artefaktom
ZAKOŃCZONEGO feature'a i utworzyć lub zaktualizować **trwałą dokumentację
modułu** w target-projekcie. Odbiorca docu = **agent AI traktowany jak nowy
developer**, który czyta docs modułu zanim go rozbuduje ("jak to działa, gdzie
zacząć, na co uważać").

**To NIE jest implementacja.** Nie piszesz kodu produktu. Jedyne co zapisujesz
to pliki `docs/modules/{moduł}.md` w target-projekcie.

**Czym to NIE jest:**
- ≠ `update-ai-context` (skan KODU → broad/shallow CLAUDE.md, auto-injected). Tu:
  deep, per-moduł, z intencji (planning) + prawdy (diff), on-demand.
- ≠ `explain` (ephemeral raport HTML jednej zmiany dla człowieka). Tu: trwała
  dokumentacja modułu w repo.
- ≠ `document-module` (skan KODU całego modułu → struktura + diagramy C4 do
  osobnego `docs/modules/{slug}-architecture.md` + HTML). Tu: **proza** "jak
  działa + dlaczego" z JEDNEGO feature'a. Komplementarne — linkuj krzyżowo.

## Wejście

Argument `$ARGUMENTS` = ścieżka do artefaktu feature'a (zwykle `tasks-{slug}.md`
lub `planning-{slug}.md`).

$ARGUMENTS

---

## KROK 1: Wczytaj artefakty feature'a (INTENCJA + PRAWDA)

Z podanej ścieżki wyprowadź `{slug}` i katalog feature'a. Wczytaj co istnieje
(obsłuż brak każdego z osobna — **nie zatrzymuj się** gdy część plików nie
istnieje, pracuj na tym co masz):

**Intencja / decyzje (DLACZEGO):**
- `planning-{slug}.md` — intencja, wybrane rozwiązanie, rationale, tradeoffy.
  Obsłuż też layout epica (`{epic-slug}/planning-phase-N-*.md` + `planning-main.md`).

**Proces (co i jak zrobiono):**
- `tasks-{slug}.md` — taski / orchestrator index
- phase files w `tasks-{slug}/` (jeśli orchestrated): `NN-*.md`, `implementation-context.md`

**Prawda o kodzie (EFEKT) — źródło prawdy o module:**
```bash
git diff <base>...HEAD        # base = main/master (auto-detect)
git diff --cached
git diff
```
Auto-detect base: `git rev-parse --verify main 2>/dev/null && echo main || echo master`.
Git diff jest **źródłem prawdy o aktualnym stanie kodu** — nie zgaduj jak moduł
działa z samego planu, jeśli diff mówi co innego. Planning daje DLACZEGO, diff
daje JAK-TERAZ.

**Późne odpalenie:** gdy diff jest już scommitowany/zmergowany, obsłuż zarówno
`vs master` jak i diff konkretnego commita (jak w `try-learn-skill`).

Jeśli BRAK kluczowych artefaktów (np. nie ma ani tasks, ani planning, ani diffa)
→ zaraportuj "za mało materiału do dokumentacji" i zakończ BEZ zapisu.

## KROK 2: Wykryj dotknięte moduły (diff → moduł)

Z plików zmienionych w diffie wyznacz, które **moduły** feature dotknął.

**Primary (źródło prawdy o strukturze):**
- Wczytaj target-projekt `CLAUDE.md` → sekcja `## Project Structure` (mapowanie
  katalogów na moduły/odpowiedzialności).
- Wczytaj `./absolutpowers/patterns.md` jeśli istnieje (struktura modułów).

**Fallback (heurystyka ścieżek):** gdy brak CLAUDE.md/patterns.md lub nie
pokrywają ścieżki — top-level katalog pod `src/` albo pakiet/namespace:
`src/auth/*` → moduł `auth`, `packages/billing/*` → moduł `billing`.

**Sanityzacja nazwy → slug pliku:** gdy nazwa pakietu ma znaki specjalne
(`@scope/pkg`, kropki, slashe) → kebab-case slug bezpieczny dla nazwy pliku
(`@acme/auth-core` → `auth-core`). Plik docu: `docs/modules/{slug}.md`.

## KROK 3: Mapping confirm — TWARDY GATE

Pokaż użytkownikowi wykryte mapowanie plik→moduł dla WSZYSTKICH dotkniętych
modułów i **CZEKAJ na potwierdzenie/korektę** zanim cokolwiek zapiszesz.

```
Wykryte mapowanie plik→moduł:
- src/auth/login.ts, src/auth/session.ts   → moduł `auth`      → docs/modules/auth.md (UPDATE)
- src/billing/invoice.ts                    → moduł `billing`   → docs/modules/billing.md (NEW)

Potwierdź albo skoryguj mapowanie przed zapisem.
```

**To JEDYNY twardy gate.** Powód: zła detekcja = docs w złym pliku, czego git
diff nowego pliku nie wyłapie. Auto-write dotyczy **treści**, nie **wyboru pliku
modułu**. Nie pisz przed wyraźnym "ok / potwierdzam / zapisz".

## KROK 4: Dla każdego modułu — NEW vs UPDATE

Pętla po wszystkich potwierdzonych modułach:

- **NEW** (brak `docs/modules/{slug}.md`) → utwórz z szablonu (sekcja "Szablon
  docu modułu" niżej).
- **UPDATE** (doc istnieje) → **inteligentny merge**: przepisz odpowiednie sekcje
  tak, żeby odzwierciedlały AKTUALNY stan modułu po feature. Doc zostaje spójnym
  "jak moduł działa TERAZ", nie stosem changelogów.

**OSTRZEŻENIE przy UPDATE (krytyczne):** nie usuwaj wiedzy nieobjętej diffem —
aktualizuj tylko sekcje dotknięte feature'em. Diff mówi co się zmieniło; reszta
docu (wiedza o niezmienionych częściach modułu) zostaje. Append-changelog
ODRZUCONY (historia = git + ADR, nie stos logów w docu).

## KROK 5: Auto-write + stamp świeżości

Pisz treść **od razu** (bez dodatkowego promptu o akceptację treści):
- git diff przed commit = naturalna powierzchnia review treści,
- docs **nie wykonują się** (≠ learned-skills exec → tam pełny human gate;
  tu lżejszy gate uzasadniony niższym ryzykiem).

Utwórz katalog `docs/modules/` przy pierwszym zapisie jeśli nie istnieje.

Stempluj `doc-meta` w ciele docu:
- `last-updated`: dzisiejsza data (YYYY-MM-DD),
- `last-commit`: bieżący HEAD sha (`git rev-parse --short HEAD`).

Uwaga: commit z docs nastąpi PO zapisie, więc `last-commit` = HEAD sprzed commita
docs — drobny rozjazd 1 commita, akceptowalny.

---

## Szablon docu modułu

Skill MUSI generować dokładnie taki szablon (dla NEW; dla UPDATE = kontrakt
sekcji do inteligentnego merge):

```markdown
# Moduł: {nazwa}

<!-- doc-meta
last-updated: YYYY-MM-DD
last-commit: <sha>
-->

## Przegląd
[Co to jest, za co odpowiada, granice modułu]

## Jak działa
[Kluczowe komponenty + przepływ. Zorientowane na AI-jako-dev: gdzie zacząć]

## Kluczowe decyzje (dlaczego)
[Z planning rationale — czemu tak, nie inaczej; istotne tradeoffy]

## Punkty integracji
[Zależności, API/kontrakty, eventy, co woła / co woła ten moduł]

## Mapa plików
- `ścieżka` — [rola]

## Pułapki / edge cases
[Na co uważać przy rozbudowie]
```

### Reguła: `doc-meta` w CIELE, nie we frontmatter

`doc-meta` MUSI być komentarzem HTML w **ciele** docu (zaraz pod nagłówkiem),
NIE polem YAML frontmatter. Powód: konsekwencja i bezpieczeństwo loadera
(jak `learned-meta` w `try-learn-skill`). `docs/` nie jest skillem, ale trzymamy
metadane w ciele jednolicie. Pola: `last-updated`, `last-commit`. Przyszłe
tooling/AI wykryje drift (ile commitów w module od `last-commit`).

### Uwaga harness

Jedno drzewo skilli (od 5.0.0). Pola `allowed-tools`/`argument-hint` są Claude-only i inertne na innych harnessach.

---

## Zasady

- **Twardy gate tylko na mapping plik→moduł** (Krok 3). Treść = auto-write
  (git diff przed commit jest review).
- **Inteligentny merge, nie changelog**: doc = "jak działa TERAZ"; nie usuwaj
  wiedzy nieobjętej diffem.
- **Jednostka = MODUŁ**, nie feature. Feature dotykający 3 modułów → 3 docs.
- **Write tylko do `docs/modules/`** target-projektu, NIE do repo AbsolutPowers.
- **Brak materiału → zakończ czysto** bez tworzenia plików.
- **Źródło prawdy o JAK = diff** (kod), źródło DLACZEGO = planning.
