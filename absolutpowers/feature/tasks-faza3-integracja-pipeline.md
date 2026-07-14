# Tasks: Integracja warstwy domenowej — terminal-state kontrakty (Faza 3 migracji)

## Mode
single-file

## Project Context

**Source doc:** `./absolutpowers/feature/planning-faza3-integracja-pipeline.md`

**Stack:** Markdown (SKILL.md + agent .md), plugin wieloharnessowy (Claude/Codex/Pi) po Fazie 1. Repo **bez systemu budowania** — weryfikacja AC jest grep/strukturalna (odczyt plików + grep), nie uruchamianie testów.

**Struktura (jednodrzewowa, po Fazie 1):**
- `skills/{name}/SKILL.md` — jedno drzewo, źródło prawdy (host-agnostyczne; NIE ma już `claude/`/`codex/` mirrorów)
- `agents/*.md` — zarejestrowani agenci Claude-only (worker, review-*)
- `hooks/session-context.md` — wspólna treść hooka (deklaruje już łańcuch pipeline z Fazy 1)

**Patterns/Konwencje:**
- Dwujęzyczność (CLAUDE.md): prompty user-facing → **polski**; treść techniczna → angielski. Blok terminal-state = proza procesowa → PL.
- Filtr project-memory: wzorzec brzmienia w `skills/implement/SKILL.md` (sekcja Context Files, „use only entries with `Status: active`").
- Sekcje SKILL.md: nagłówki `##`; blok terminal-state to zwykła sekcja markdown (proza), NIE frontmatter/YAML/JSON (AC-11).

**Verification commands (grep/strukturalne — repo bez buildu):**
- Terminal-state obecny: `for f in feature-discuss generate-tasks implement review; do echo "$f: $(grep -c '## Terminal state' skills/$f/SKILL.md)"; done` (każdy = 1)
- gnhf w żywym prompcie: `grep -rl 'gnhf' skills/ agents/ hooks/` (pusto) + `grep -rl 'gnhf' absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md` (pusto)
- Filtr workera: `grep -i 'Status: active' agents/implementation-worker.md` (trafienie)
- Frontmatter bez nowych kluczy: `for f in feature-discuss generate-tasks implement review; do sed -n '1,/^---$/{/^---$/!p}' skills/$f/SKILL.md; done` — brak `next:`/`terminal-state:`
- feature-discuss fallback zachowany: `grep -ci 'Node' skills/feature-discuss/SKILL.md` (>0) + grep na tryb nieinteraktywny

**Reference:**
- `skills/implement/SKILL.md` — wzorzec brzmienia filtra `Status: active` (do skopiowania do workera, Task 5)
- `hooks/session-context.md` — istniejąca deklaracja łańcucha (spójność wordingu)

## Global Constraints
> Wymagania obowiązujące KAŻDE zadanie (verbatim z planning-doc + ADR/CLAUDE.md):
- **Dwujęzyczność:** blok terminal-state i wszelka treść user-facing → polski; nie zmieniać istniejącej konwencji.
- **Proza, nie format maszynowy:** terminal-state to sekcja markdown; ZERO nowych kluczy frontmatter / YAML / JSON (AC-11).
- **Unifikacja, nie duplikacja:** zastępuj istniejące luźne „Następny krok", nie dodawaj obok (AC-7).
- **gnhf w feature-discuss = relabel, NIE strip:** logika fallback bez Node + tryb nieinteraktywny MUSI zostać; ginie tylko słowo „gnhf" (AC-9b).
- **Filtr project-memory:** brzmienie skopiowane spójnie z `skills/implement/SKILL.md`, nie wymyślane od nowa.
- **Nie ruszać:** grep-AC, AC traceability, Review Gate flow, Mode single-file/orchestrated, HARD-GATE promocji project-memory (AC-13).

## Kanoniczny blok terminal-state (wzorzec z planning §26-34)
> Task 1 **Produkuje** to brzmienie; Tasks 2-4 **Konsumują** je (ten sam format, adaptowana treść per skill).
```
## Terminal state
Stan terminalny tego skilla: <co jest dostarczone>.
Następny krok w pipeline: `@<next-skill>` (<warunek/kiedy>).
Pipeline NIE jest domknięty na tym etapie — jeśli działasz pod `/goal`,
kontynuuj do skilla terminalnego (`@review`/`@triada-review` lub ship/merge),
zanim uznasz cel za osiągnięty.
```

## Implementation Tasks

### Task 1: Terminal-state — feature-discuss (kanon + unifikacja handoffu)
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-7, AC-11

**Modify:**
- `skills/feature-discuss/SKILL.md`

**Produces:**
- Kanoniczny format bloku `## Terminal state` (wording, struktura 3 zdań) — Tasks 2-4 konsumują ten sam format.

**Description:**
Dodać sekcję `## Terminal state` na końcu feature-discuss, deklarującą stan terminalny (zapisany + zaakceptowany spec) i następny krok `@generate-tasks`, z klauzulą anty-przedwczesny-stop pod `/goal`. Zunifikować istniejące luźne linie „Następny krok" (ok. l. 355, 406) — zastąpić/odesłać do bloku, nie zostawić sprzecznego duplikatu.

**Requirements:**
- Dodać `## Terminal state` na końcu pliku (po niej tylko ewentualne istniejące sekcje startowe); terminal: „spec zapisany i zaakceptowany przez użytkownika"; next: `@generate-tasks`.
- Klauzula: pipeline niedomknięty; pod `/goal` kontynuuj do skilla terminalnego (review/ship-merge).
- Zunifikować istniejące „Następny krok" (l. ~355 tryb epica, ~406 Tryb B) — nie tworzyć sprzecznego drugiego handoffu (dopuszczalne odwołania procesowe, nie konkurencyjny blok terminal-state).
- Proza PL; zero nowych kluczy frontmatter.
- (gnhf relabel w tym pliku → Task 6, osobno.)

**Tests (grep/strukturalne):**
- `grep -c '## Terminal state' skills/feature-discuss/SKILL.md` = 1 (AC-1)
- Sekcja zawiera `@generate-tasks` (AC-2) i klauzulę `/goal` (AC-4)
- Brak sprzecznego drugiego bloku terminal-state (AC-7)
- Frontmatter bez `next:`/`terminal-state:` (AC-11)

**Implementation decisions / remarks:**
- `## Terminal state` dodany na końcu (po liście „Zasady zachowania"), kanoniczny format 3-zdaniowy. terminal: zapisany+zaakceptowany spec (HARD-GATE), next: `@generate-tasks`, klauzula `/goal`.
- Istniejące linie „Następny krok" (l. ~355 epic, ~406 Tryb B) zostawione jako odwołania procesowe wewnątrz sub-flowów (dozwolone przez AC-7) — wskazują ten sam kierunek (generate-tasks / kolejna faza), brak sprzeczności z terminal-state.
- Grep: `## Terminal state`=1, `@generate-tasks` obecne, `/goal`=1, frontmatter clean.

### Task 2: Terminal-state — generate-tasks (+ nota Execution Handoff/Mode)
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-11

**Modify:**
- `skills/generate-tasks/SKILL.md`

**Consumes:**
- Kanoniczny format bloku terminal-state z Task 1.

**Description:**
Dodać `## Terminal state` (terminal: zweryfikowany tasks-doc z ustawionym `Mode`; next: `@implement`). Zunifikować istniejącą linię „Następny krok: /absolutpowers:implement" (ok. l. 647). Dopisać krótką notę Execution Handoff w sekcji o Mode.

**Requirements:**
- `## Terminal state` na końcu; terminal: „zweryfikowany tasks-doc, Mode ustawiony"; next: `@implement`; klauzula `/goal`.
- Zunifikować istniejący handoff do implement (l. ~647), nie dublować.
- Nota Execution Handoff (przy sekcji Mode): absolutpowers wykonuje przez `implement`; Mode (orchestrated/single-file) to analog forka obry subagent-driven/executing-plans — brak forka to nie luka (AC-5).
- Proza PL; zero nowych kluczy frontmatter.

**Tests (grep/strukturalne):**
- `grep -c '## Terminal state' skills/generate-tasks/SKILL.md` = 1 (AC-1); zawiera `@implement` (AC-2) + klauzula `/goal` (AC-4)
- Nota Execution Handoff wspomina `Mode` i „jedyny egzekutor implement" (AC-5)
- Brak sprzecznego duplikatu handoffu (AC-7); frontmatter czysty (AC-11)

**Implementation decisions / remarks:**
- Nota „Execution Handoff — rozstrzygnięcie (Mode = analog, nie luka)" wstawiona w sekcji `## Output Mode` (po Phase sizing by risk). Wprost: `implement` jedynym egzekutorem, `Mode` orchestrated/single-file = analog forka obry subagent-driven/executing-plans.
- `## Terminal state` na końcu: terminal = zweryfikowany tasks-doc z ustawionym `Mode`, next = `@implement`, klauzula `/goal`.
- Istniejąca linia „Następny krok: /absolutpowers:implement" (Review Gate PASS) zostawiona jako odwołanie procesowe (AC-7 dozwala).
- Grep: `## Terminal state`=1, `@implement` obecne, `/goal`=1, „Execution Handoff"=2, „jedynym egzekutorem"=2, frontmatter clean.

### Task 3: Terminal-state — implement (+ spójność z harvest)
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-7, AC-8, AC-11

**Modify:**
- `skills/implement/SKILL.md`

**Consumes:**
- Kanoniczny format bloku terminal-state z Task 1.

**Description:**
Dodać `## Terminal state` (terminal: zaimplementowane + final gate PASS; next: `@review`/`@triada-review`, opcjonalnie harvest przed commitem). Objąć istniejący nudge do harvest spójnie — nie tworzyć drugiego, sprzecznego zalecenia kolejności harvest vs review.

**Requirements:**
- `## Terminal state` na końcu; terminal: „zaimplementowane, final gate PASS"; next: `@review`/`@triada-review`; klauzula `/goal`.
- Spójność z istniejącym best-effort nudge do harvest (ok. l. 624-629): harvest opcjonalny przed commitem, review to gate — jedno spójne zalecenie (AC-8).
- **Uwaga na `## Begin` (l. ~638):** implement to jedyny z 4 plików z sekcją startową `## Begin`. Wstaw `## Terminal state` PRZED `## Begin` (AC-1 dopuszcza tylko sekcje startowe PO bloku terminal-state — ale tu Begin jest instrukcją startową; umieść terminal-state bezpośrednio przed nią, na końcu treści merytorycznej).
- Proza PL; zero nowych kluczy frontmatter.

**Tests (grep/strukturalne):**
- `grep -c '## Terminal state' skills/implement/SKILL.md` = 1 (AC-1); zawiera `@review` (AC-2) + klauzula `/goal` (AC-4)
- Terminal-state wspomina harvest spójnie z istniejącym nudge, bez sprzeczności (AC-8)
- Frontmatter czysty (AC-11)

**Implementation decisions / remarks:**
- `## Terminal state` wstawiony PRZED `## Begin` (po sekcji harvest nudge + separatorze), na końcu treści merytorycznej. terminal = zaimplementowane + final gate PASS, next = `@review`/`@triada-review`.
- Kolejność jednoznaczna i spójna z nudge (l. ~624-634): harvest (opcjonalnie) → review → merge/ship. Harvest opisany jako opcjonalny/best-effort PRZED review; review to bramka. Zero sprzeczności.
- Grep: `## Terminal state`=1, `@review` obecne, `/goal`=1, harvest w bloku terminal-state=1, frontmatter clean.

### Task 4: Terminal-state — review (punkt domknięcia, odróżniony)
**Status:** completed
**Traces to:** AC-1, AC-3, AC-6, AC-11

**Modify:**
- `skills/review/SKILL.md`

**Consumes:**
- Kanoniczny format bloku terminal-state z Task 1 (adaptowany — review to gate, nie ogniwo).

**Description:**
Dodać `## Terminal state` treściowo ODRÓŻNIONY: review to **punkt domknięcia** pipeline (fix-loop albo merge/ship), NIE „następny krok to `@<skill>`". Tu sesja pod `/goal` typu „dowieziony feature" może się realnie zatrzymać.

**Requirements:**
- `## Terminal state` na końcu; terminal: „raport review"; opisać jako punkt domknięcia/gate (fix-loop / merge/ship), NIE wskazywać kolejnego `@skilla` w łańcuchu (AC-6).
- Zaznaczyć że to miejsce gdzie `/goal` może uznać cel za osiągnięty (po PASS + merge).
- Proza PL; zero nowych kluczy frontmatter.

**Tests (grep/strukturalne):**
- `grep -c '## Terminal state' skills/review/SKILL.md` = 1 (AC-1)
- Sekcja opisuje domknięcie/fix-loop/merge, NIE „następny krok `@skill`" (AC-6)
- Frontmatter czysty (AC-11)

**Implementation decisions / remarks:**
- `## Terminal state` treściowo ODRÓŻNIONY: review = „punkt domknięcia pipeline, nie ogniwo łańcucha", jawnie NIE wskazuje forward `@skill`. Dwie ścieżki wyjścia: fix-loop (zawrót do generate-tasks jako pętla naprawcza) i merge/ship (realny koniec).
- Jawnie zaznaczone: to jedyne miejsce gdzie `/goal` „dowieziony feature" może uznać cel za osiągnięty (po PASS + merge).
- Grep: `## Terminal state`=1, „domknięcia"/„fix-loop"/„merge/ship" obecne, brak „Następny krok w pipeline: @" w bloku, frontmatter clean.

### Task 5: Filtr `Status: active` project-memory w workerze
**Status:** completed
**Traces to:** AC-12, AC-13

**Modify:**
- `agents/implementation-worker.md`

**Description:**
Realna naprawa latentnego buga: worker (l. ~35) czyta `project-memory.md` bez filtra `Status: active` — jako jedyny komponent pipeline (implement/review/generate-tasks/debug/problem-discuss mają go). Dodać instrukcję filtra spójną z brzmieniem w `skills/implement/SKILL.md`.

**Requirements:**
- Dodać do `agents/implementation-worker.md` (przy odczycie project-memory, l. ~35) instrukcję: używać wyłącznie wpisów `Status: active` jako podpowiedzi; ignorować `superseded`/`archived`.
- Brzmienie skopiowane/dostosowane z `skills/implement/SKILL.md` (jedno źródło konwencji) — nie wymyślać nowego.
- NIE zmieniać HARD-GATE promocji project-memory ani żadnego innego wymogu zgody (AC-13).

**Tests (grep/strukturalne):**
- `grep -i 'Status: active' agents/implementation-worker.md` = trafienie (AC-12)
- Brzmienie wspomina ignorowanie `superseded`/`archived` (AC-12)
- Brak zmian w wymogu zgody na promocję (AC-13)

**Implementation decisions / remarks:**
- Filtr dopisany do `agents/implementation-worker.md` Required Context, pkt 5 (odczyt project-memory) — brzmienie skopiowane verbatim z `skills/implement/SKILL.md` l.57: „use only entries with `Status: active` as implementation hints. Ignore entries with `Status: superseded` or `Status: archived`."
- Worker nigdy nie promuje wpisów (grep promotion/promocja=0) — HARD-GATE promocji poza jego zakresem, nietknięty (AC-13).
- Grep: `Status: active`=1, `superseded`=1 w workerze.

### Task 6: gnhf cleanup (relabel żywy + strip archiwa + notka plan-migracji)
**Status:** completed
**Traces to:** AC-9, AC-9b, AC-10

**Modify:**
- `skills/feature-discuss/SKILL.md` (relabel)
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md` (strip)
- `plan-migracji-hybrydowej-superpowers.md` (notka Faza 4)

**Description:**
Wyczyścić martwy label „gnhf" (narzędzie nieużywane) w dwóch klasach: RELABEL w żywym feature-discuss (logika zostaje), STRIP w archiwalnych planning-docach, plus notka rescope przy Fazie 4 planu migracji.

**Requirements:**
- `skills/feature-discuss/SKILL.md` (l. ~49, 55): relabel „nocne runy gnhf" → „runy headless/nieinteraktywne", „Tryb nieinteraktywny (gnhf)" → „Tryb nieinteraktywny (headless)". Logika fallback-bez-Node i tryb-nieinteraktywny ZOSTAJE nietknięta (AC-9b).
- `absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md`: strip wzmianek gnhf (martwa proza).
- `plan-migracji-hybrydowej-superpowers.md`: dopisać przy Fazie 4 notkę, że wymaga rescope'u/wycięcia (gnhf nieużywany) — bez przepisywania całej fazy (AC-10). NIE stripować gnhf z tego pliku (historyczny — poza grepem AC-9).
- NIE dotykać `docs/onboarding/*.html` (poza scope AC-9).

**Tests (grep/strukturalne):**
- `grep -rl 'gnhf' skills/ agents/ hooks/` = pusto (AC-9)
- `grep -rl 'gnhf' absolutpowers/feature/superpowers-faza2-fuzje/planning-*.md` = pusto (AC-9)
- feature-discuss nadal ma logikę fallback-bez-Node + tryb nieinteraktywny (AC-9b)
- plan-migracji ma notkę rescope przy Fazie 4 (AC-10)

**Implementation decisions / remarks:**
- feature-discuss RELABEL: „nocne runy gnhf" → „runy headless/nieinteraktywne" (l.49), „Tryb nieinteraktywny (gnhf)" → „Tryb nieinteraktywny (headless)" (l.55). Logika fallback-bez-Node i handling nieinteraktywny NIETKNIĘTE (AC-9b: oba nagłówki + treść zostają).
- Archiwum STRIP: token `gnhf`→`headless` w 3 plikach `superpowers-faza2-fuzje/planning-*.md` (perl bulk). Pliki w podfolderze `tasks-phase-1-feature-discuss/` NIE dotknięte — poza grepem AC-9 (`planning-*.md` glob) i pod zasadą „archiwum = nie rewizjonizm".
- plan-migracji: notka „⚠️ Rescope wymagany" wstawiona pod nagłówkiem Fazy 4; gnhf w tym pliku ZOSTAJE (historyczny, poza grepem AC-9). docs/onboarding/*.html nietknięte.
- Grep: gnhf w skills/agents/hooks = pusto, w archiwum planning-*.md = pusto.

### Task 7: Docs sweep (warunkowy) — CLAUDE.md/README
**Status:** completed
**Traces to:** none (docs, warunkowe — wzmocnienie AC-5)

**Modify:**
- `CLAUDE.md` (jeśli potrzeba)
- `README.md` (jeśli potrzeba)

**Description:**
Przejrzeć opis pipeline w CLAUDE.md/README; jeśli warto — dopisać wzmiankę o kontrakcie terminal-state i o Execution Handoff = Mode (analog). Warunkowe: żaden AC nie wymusza edycji; jeśli opis już spójny, odnotować „bez zmian".

**Requirements:**
- Jeśli CLAUDE.md pipeline section warto wzbogacić o terminal-state / Execution-Handoff=Mode — dopisać zwięźle.
- Jeśli nie ma czego poprawiać — odnotować „not applicable" z powodem, nie wymuszać zmiany.

**Tests (grep/strukturalne):**
- Jeśli edytowano: opis spójny z terminal-state/Mode; jeśli nie: uzasadnienie w remarks.

**Implementation decisions / remarks:**
- CLAUDE.md: DODANA podsekcja „Terminal-state contract (prose, `/goal`-aware)" w `## Pipeline Architecture` (pod diagramem). Dokumentuje kontrakt terminal-state 4 skilli, punkt domknięcia review, i Execution-Handoff=Mode (analog obry) — wzmacnia AC-5 na poziomie repo-guidance. AGENTS.md = symlink do CLAUDE.md (auto-mirror, brak osobnej edycji).
- README.md: NIE edytowany (not applicable). README jest user-facing/marketingowy; kontrakt terminal-state to wewnętrzny szczegół implementacyjny należący do CLAUDE.md, nie do README. README już opisuje chaining pipeline'u ogólnie („Skills chain into a pipeline") — nic sprzecznego do poprawy.

### Task 8: Final Verification
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-9b, AC-10, AC-11, AC-12, AC-13

**Create:**
- None

**Modify:**
- None

**Description:**
Uruchomić grep/strukturalne komendy weryfikacyjne przeciw zintegrowanej zmianie. Repo bez buildu — bramki to walidacja strukturalna. Nie oznaczać completed jeśli któraś faili.

**Requirements:**
- Terminal-state ×4: `for f in feature-discuss generate-tasks implement review; do echo "$f: $(grep -c '## Terminal state' skills/$f/SKILL.md)"; done` → każdy 1 (AC-1)
- Łańcuch `@`: feature-discuss→`@generate-tasks`, generate-tasks→`@implement`, implement→`@review` (AC-2); review = punkt domknięcia bez `@next` (AC-6)
- Klauzula `/goal` w 3 pośrednich (AC-4); Execution Handoff/Mode w generate-tasks (AC-5); harvest spójny w implement (AC-8)
- gnhf: `grep -rl 'gnhf' skills/ agents/ hooks/` pusto + archiwa pusto (AC-9); feature-discuss fallback zachowany (AC-9b); plan-migracji notka Faza 4 (AC-10)
- `grep -i 'Status: active' agents/implementation-worker.md` trafienie (AC-12); HARD-GATE promocji nietknięty (AC-13)
- Frontmatter 4 skilli bez nowych kluczy `next:`/`terminal-state:` (AC-11)
- Nie oznaczać completed jeśli którakolwiek faili.

**Tests:**
- Wszystkie powyższe grepy zwracają oczekiwane wartości (0 rozbieżności)

**Implementation decisions / remarks:**
- Komendy wykonane: grep/strukturalne (repo bez buildu) — AC-1..AC-13.
- Wyniki (0 rozbieżności):
  - AC-1: terminal-state ×4 = każdy 1 (feature-discuss/generate-tasks/implement/review).
  - AC-2: feature-discuss→`@generate-tasks`, generate-tasks→`@implement`, implement→`@review` (obecne).
  - AC-4: klauzula `/goal` w 3 pośrednich = po 1.
  - AC-5: „Execution Handoff"=2, „jedynym egzekutorem"=2 w generate-tasks.
  - AC-6: review = „punkt domknięcia" + fix-loop + merge/ship; brak forward „Następny krok w pipeline: @" w bloku.
  - AC-8: harvest w bloku terminal-state implement=1, spójny z nudge.
  - AC-9: `grep -rl gnhf skills/ agents/ hooks/` pusto; archiwum `planning-*.md` pusto.
  - AC-9b: „Graceful fallback — brak Node"=1, „Tryb nieinteraktywny (headless)"=1 (logika zachowana).
  - AC-10: „Rescope wymagany" przy Fazie 4 planu migracji=1.
  - AC-11: frontmatter 4 skilli clean (brak `next:`/`terminal-state:`).
  - AC-12: worker `Status: active`=1, `superseded`=1.
  - AC-13: „Promotion requires explicit user approval" (implement)=1, „Promocja wymaga jawnej zgody" (review)=1 — nietknięte; worker promotion=0.
- Pominięte: none.

**Example:**
```bash
for f in feature-discuss generate-tasks implement review; do echo "$f: $(grep -c '## Terminal state' skills/$f/SKILL.md)"; done
grep -rl 'gnhf' skills/ agents/ hooks/ || echo "no gnhf in live prompt"
grep -i 'Status: active' agents/implementation-worker.md && echo "worker filter OK"
```
