# Tasks (fix): Codex fallback regression + companion CSP (review major v5)

## Mode
single-file

## Project Context

**Source doc:** `./absolutpowers/reviews/2026-07-14-major-v5-review.md`

**Stack:** Markdown (SKILL.md + references), plus vendored Node companion (`server.cjs`/`start-server.sh`). Repo **bez systemu budowania**; weryfikacja skilli grep/strukturalna, companion — `node --check` + smoke curl.

**Struktura:**
- `skills/{name}/SKILL.md` — jedno host-agnostyczne drzewo; harness-specyfika w `references/{harness}-tools.md` (czytane warunkowo)
- `references/pi-tools.md` — istniejący wzorzec degradacji Pi (dispatch + review gates)
- `skills/feature-discuss/companion-scripts/` — vendored Node companion (server.cjs, start-server.sh)
- `VENDORED.md` — rejestr lokalnych modyfikacji treści vendored

**Konwencje:**
- Dwujęzyczność: prompty user-facing → polski; treść techniczna → angielski.
- Degradacja bramek per harness: wzorzec z `references/pi-tools.md` (dwustopniowy: dispatch generic subagent z `agents/{name}.md` jako promptem / review inline z jawnym disclaimerem braku izolacji).

**Verification commands:**
- `node --check skills/feature-discuss/companion-scripts/server.cjs`
- smoke: unauth→403, auth→200, traversal→404, nagłówek CSP zawiera `script-src` (kody zweryfikowane wobec server.cjs: unauth `403` l.376-379, traversal `404` l.409-417 — NIE zmieniamy ich w tym fixie)
- grep: 3 skille kierują Codex do `references/codex-tools.md`; codex-tools.md ma sekcję orchestrated fallback

**Reference:**
- `references/pi-tools.md` — wzorzec do odbicia dla Codex (Task 1)
- `codex/skills/implement/SKILL.md` (v3.13.0, git show `ff9cd48:`) — poprzedni jawny sekwencyjny fallback Codex do odtworzenia

**Findingi review (mapowanie):**
- **[HIGH]** Codex stracił działającą ścieżkę orchestrated + bramek (skille kierują tylko do Pi-only `pi-tools.md`; brak `codex-tools.md`; brak Codex-inline fallback) → Task 1 + Task 2.
- **[MED]** Companion nie spełnia kontraktu „statyczny render" (CSP tylko `frame-ancestors`, brak `script-src`; render verbatim; `--host` poza loopback) → Task 3 + Task 4.
- **[LOW]** brak testów regresyjnych nowego runtime → Task 5 (smoke, lekkie).

## Global Constraints
- **NIE regresja Claude:** zmiany w 3 skillach to DODANIE gałęzi Codex, nie zmiana ścieżki Claude (zarejestrowani agenci działają wprost).
- **Companion = vendored:** każda edycja `companion-scripts/*` odnotowana w `VENDORED.md` (lista lokalnych modyfikacji).
- **Bez nowego frameworka testowego:** smoke-test to samodzielny skrypt (curl/node), nie zależność.

## Implementation Tasks

### Task 1: `references/codex-tools.md` — ścieżka degradacji Codex
**Status:** completed
**Traces to:** none (naprawa [HIGH], review report bez AC)

**Create:**
- `references/codex-tools.md`

**Description:**
Utworzyć plik mapowania per-harness dla Codex, równoległy do `references/pi-tools.md`, definiujący dwustopniową degradację dispatchu subagentów i bramek review. Bez tego skille kierujące Codex „do odpowiedniego references/{harness}-tools.md" trafiają w pustkę.

**Requirements:**
- Odbić strukturę `references/pi-tools.md`: sekcje dla dispatchu subagentów i „Review gates on Codex".
- **Dispatch (orchestrated `implement`):** Codex ma `multi_agent=true` → `spawn_agent`/`wait_agent`/`close_agent`, ale BRAK rejestru nazwanych typów (`agents/*.md`). Zdefiniować: jeśli dostępny multi-agent → `spawn_agent` z ciałem docelowego `agents/{name}.md` jako promptem; w przeciwnym razie → **wykonanie sekwencyjne/inline w tej samej sesji** (odtworzenie zachowania v3.13.0 `codex/skills/implement`).
- **Review gates (review-plan/review-tasks/phase-review/review-implementation):** degradacja dwustopniowa — dispatch generic subagent z `agents/{name}.md` jako promptem, albo review inline z **jawnym disclaimerem braku izolacji** i **advisory verdictem** (nie cichym pominięciem bramki).
- Zaznaczyć wprost: brak `Agent(subagent_type=...)` na Codex — to Claude-only prymityw.
- Treść techniczna EN (spójnie z pi-tools.md).

**Tests (grep/strukturalne):**
- plik istnieje; zawiera sekcję orchestrated dispatch fallback + „Review gates on Codex"
- wzmiankuje `spawn_agent` i sekwencyjny/inline fallback; zakazuje `Agent(subagent_type=...)`

**Implementation decisions / remarks:**
- Utworzono `references/codex-tools.md` równolegle do `pi-tools.md`: tabela akcja→prymityw, sekcja Subagents (`multi_agent`/`spawn_agent`/`wait_agent`/`close_agent`), "Review gates on Codex" (dwustopniowa degradacja), "Orchestrated dispatch on Codex" (odtworzenie sekwencyjnego fallbacku v3.13.0 `codex/skills/implement`). Jawny zakaz `Agent(subagent_type=...)` w nagłówku i na końcu.

### Task 2: Branch Claude/Codex/Pi w 3 skillach pipeline
**Status:** completed
**Traces to:** none (naprawa [HIGH])

**Modify:**
- `skills/implement/SKILL.md`
- `skills/generate-tasks/SKILL.md`
- `skills/feature-discuss/SKILL.md`

**Description:**
Zastąpić w każdym z 3 skilli obecną notę „Na Pi/Codex: patrz `references/pi-tools.md` (lub odpowiedni references/{harness}-tools.md)" jawnym rozgałęzieniem per harness kierującym Codex do `references/codex-tools.md` (Task 1) i Pi do `pi-tools.md`. W `implement` (przy dispatchu orchestrated, ok. l. 33 + Step O2/O4/O6) dodać jawną instrukcję: na Codex użyj ścieżki z codex-tools (dispatch generic albo sekwencyjny inline), NIE literalnego `Agent(subagent_type=...)`.

**Requirements:**
- W każdym z 3 skilli nota harness-fallback wskazuje: Claude → zarejestrowani agenci (wprost); Pi → `references/pi-tools.md`; **Codex → `references/codex-tools.md`**.
- `implement` orchestrated: przy każdym dispatchu (`implementation-worker`, `phase-review`, `review-implementation`) dopisać krótkie „(Codex: patrz references/codex-tools.md — dispatch generic lub sekwencyjnie inline z advisory verdictem)".
- NIE zmieniać ścieżki Claude (zarejestrowani agenci działają jak dotąd).
- Proza dwujęzyczna zgodna z plikiem.

**Tests (grep/strukturalne):**
- `grep -rl 'references/codex-tools.md' skills/implement/SKILL.md skills/generate-tasks/SKILL.md skills/feature-discuss/SKILL.md` = 3 trafienia
- `implement` wspomina Codex fallback przy dispatchu orchestrated (grep `codex-tools` w kontekście Step O2/dispatch)
- Ścieżka Claude nietknięta (zarejestrowani agenci nadal opisani)

**Implementation decisions / remarks:**
- W 3 skillach zastąpiono notę Pi-only jawnym rozgałęzieniem Claude/Codex/Pi (Codex → `references/codex-tools.md`). W `implement` nota nagłówkowa "dotyczy każdego `Agent(subagent_type=...)` niżej" + 3 krótkie przypomnienia Codex przy dispatchu worker/phase-review/review-implementation (Step O2/O4/O6). Ścieżka Claude nietknięta (8 literalnych `subagent_type=` nadal obecnych).

### Task 3: Companion CSP + odrzucanie aktywnej treści (server.cjs)
**Status:** completed
**Traces to:** none (naprawa [MED])

**Modify:**
- `skills/feature-discuss/companion-scripts/server.cjs`

**Description:**
Domknąć kontrakt „statyczny render, nigdy nie wykonuje kodu z requestu". Obecnie CSP to tylko `frame-ancestors 'none'` (l.359), a ekran renderowany verbatim (l.395) — `<script>`/`onerror`/remote resource w wygenerowanym HTML wykona się w przeglądarce. Narzucić restrykcyjne CSP + odrzucać/sanityzować aktywną treść.

**Requirements:**
- Ustawić restrykcyjne CSP na odpowiedzi serwującej ekran i frame: `default-src 'none'; style-src 'unsafe-inline'; img-src data:; connect-src 'self'; frame-ancestors 'none'; script-src 'nonce-{losowy}'` — jedyny dozwolony skrypt to helper wstrzykiwany przez serwer z tym noncem (albo hash). Zero `script-src` dla treści ekranu.
- **Reject/sanitize aktywnej treści ekranu:** przed serwowaniem wykryć w HTML ekranu `<script`, inline event-handlery (`on*=`), `javascript:`, zewnętrzne `src`/`href` do zasobów zdalnych → albo odrzucić z czytelnym błędem, albo wystripować (wybrać: **reject** jest bezpieczniejszy — ekran generuje asystent, więc naruszenie = bug generatora, lepiej głośno).
- Helper serwera dostaje `nonce` zgodny z CSP (jedyny wykonywalny skrypt).
- Zachować istniejące zabezpieczenia (token per-sesja, timingSafeEqual, WS Origin, traversal guard) nietknięte.

**Tests:**
- `node --check server.cjs` OK
- smoke: nagłówek odpowiedzi `/` zawiera `script-src 'nonce-` i `default-src 'none'`
- ekran z wstrzykniętym `<script>` → odrzucony (albo skrypt nieobecny w odpowiedzi)

**Implementation decisions / remarks:**
- Dodano `documentCsp(nonce)` + `documentSecurityHeaders(nonce)`: `default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; script-src 'nonce-{losowy}'`. Nonce per-response (`crypto.randomBytes(16).base64`).
- **Deviation od literalnego wymogu:** `img-src 'self' data:` zamiast `img-src data:` — ekrany companionu legalnie ładują same-origin `/files/*.png` (mockupy kart); `data:`-only zepsułoby je bez zysku (remote i tak blokowane przez brak `http(s):`). Reszta CSP wg specyfikacji review.
- `helperInjection` const → funkcja `helperInjection(nonce)`; helper to jedyny skrypt z noncem. `bootstrapPage(key)` → `bootstrapPage(key, nonce)` (jego inline script też nonce'owany).
- **Reject (nie sanitize):** `findActiveContent()` + `ACTIVE_CONTENT_PATTERNS` na surowej treści ekranu (nigdy na zaufanym frame/helperze) — wykrywa `<script`, inline `on*=`, `javascript:`, remote `src/href/action`, `<link>/<base>/<meta http-equiv>`. Trafienie → log `screen-blocked` na stderr + statyczny `activeContentBlockedFragment` w ramce zamiast ekranu. Reject bo ekran generuje asystent → aktywna treść = bug generatora.
- Defense-in-depth: nawet gdyby reject ominięto, screen-script nie ma nonce → CSP go nie wykona.
- Zabezpieczenia nietknięte: token/timingSafeEqual, WS Origin, traversal guard, kody 403/404.
- Zweryfikowane runtime: unauth 403, auth 200 + CSP `default-src 'none'`+`script-src 'nonce-`, clean screen ma `nonce=`, malicious `<script>alert(1)</script>` → strona "Screen blocked", zero wycieku `alert(1)`.

### Task 4: `--host` guard + wpis VENDORED.md
**Status:** completed
**Traces to:** none (naprawa [MED] + hygiene)

**Modify:**
- `skills/feature-discuss/companion-scripts/start-server.sh`
- `VENDORED.md`

**Description:**
Bind poza loopbackiem (`--host 0.0.0.0`) zwiększa powierzchnię ataku. Dodać ostrzeżenie/gate. Odnotować lokalne modyfikacje companionu (Task 3+4) w VENDORED.md.

**Requirements:**
- `start-server.sh`: gdy `BIND_HOST` ≠ `127.0.0.1`/`localhost` — wypisać wyraźne ostrzeżenie na stderr („bind poza loopbackiem: companion serwuje lokalne screeny, brak auth poza tokenem — używaj tylko w zaufanym środowisku/kontenerze") i kontynuować (nie blokować — 0.0.0.0 jest udokumentowane dla kontenerów). Domyślka loopback bez zmian.
- `VENDORED.md`: dopisać do listy lokalnych modyfikacji companionu wpisy o (a) utwardzeniu CSP + reject aktywnej treści (Task 3), (b) ostrzeżeniu `--host` (Task 4) — spójnie z istniejącą notą o neutralizacji telemetrii.

**Tests (grep/strukturalne):**
- `start-server.sh` zawiera warunek na BIND_HOST ≠ loopback z ostrzeżeniem
- `VENDORED.md` wzmiankuje CSP hardening + `--host` warning w sekcji modyfikacji companionu

**Implementation decisions / remarks:**
- `start-server.sh`: po rozwiązaniu URL_HOST — warunek `BIND_HOST` ≠ `127.0.0.1`/`localhost` → `echo WARNING ... >&2`, kontynuuje (nie blokuje). Domyślka loopback cicha.
- `VENDORED.md`: wpis (a) CSP hardening + reject, (b) `--host` warning dopisany do celi companionu, spójnie z notą o telemetrii.

### Task 5: Smoke-test companionu (lekki, bez frameworka)
**Status:** completed
**Traces to:** none (naprawa [LOW])

**Create:**
- `skills/feature-discuss/companion-scripts/smoke-test.sh`

**Description:**
Repo nie ma frameworka testowego; dodać samodzielny skrypt smoke pokrywający krytyczne zachowania runtime companionu wskazane w review (unauth/auth, traversal, CSP). Uruchamiany ręcznie, zero zależności poza `node`/`curl`.

**Requirements:**
- Skrypt startuje serwer na losowym porcie loopback, po czym sprawdza (kody zgodne z realnym handlerem, NIE zmieniamy statusów): (1) GET `/` bez ważnego tokenu → **403** (server.cjs:376-379); (2) z ważnym tokenem → **200**; (3) `/files/../etc/passwd` (traversal) → **404** (server.cjs:409-417 — `path.basename` + guard); (4) nagłówek CSP odpowiedzi zawiera `default-src 'none'` i `script-src 'nonce-`; na końcu zabija serwer.
- Wyjście: czytelne PASS/FAIL per check, exit code ≠ 0 przy dowolnym FAIL.
- `bash -n smoke-test.sh` OK; skrypt nie jest zależnością pluginu, tylko narzędziem dev.
- Zakres świadomie ograniczony do HTTP (WS Origin / bootstrap-after-compact poza smoke — odnotować w skrypcie jako TODO manualny, żeby nie udawać pełnego pokrycia).

**Tests:**
- `bash -n smoke-test.sh` OK
- uruchomienie skryptu na czystym repo → wszystkie checki PASS (po Task 3)

**Implementation decisions / remarks:**
- `smoke-test.sh`: start server losowy port loopback + fixed token (env), 4 wymagane checki (unauth→403, auth→200, traversal→404, CSP `default-src 'none'`+`script-src 'nonce-`) + bonus reject aktywnej treści. PASS/FAIL per check, exit ≠0 przy dowolnym FAIL. Trap cleanup zabija serwer + `wait` (bez szumu job-control).
- Zakres świadomie HTTP-only; WS Origin / bootstrap-after-compact / lifecycle jako manualny TODO w nagłówku skryptu.
- Uruchomienie na czystym repo: 5/5 PASS, exit 0.

### Task 6: Final Verification
**Status:** completed
**Traces to:** none (weryfikacja całości)

**Create:**
- None

**Modify:**
- None

**Description:**
Uruchomić weryfikację zintegrowanej zmiany. Repo bez buildu — grep/strukturalne + `node --check` + smoke. Nie oznaczać completed jeśli którakolwiek faili.

**Requirements:**
- [HIGH] `test -f references/codex-tools.md` + zawiera orchestrated fallback i „Review gates on Codex"; `grep -l 'references/codex-tools.md' skills/{implement,generate-tasks,feature-discuss}/SKILL.md` = 3
- [HIGH] `implement` zabrania Codexowi `Agent(subagent_type=...)` / kieruje do codex-tools (grep)
- [MED] `node --check skills/feature-discuss/companion-scripts/server.cjs` OK; CSP odpowiedzi zawiera `default-src 'none'` + `script-src 'nonce-`; ekran z aktywną treścią odrzucany
- [MED] `start-server.sh` ma warning na bind poza loopback; `VENDORED.md` odnotowuje modyfikacje
- [LOW] `bash -n smoke-test.sh` OK; smoke przechodzi wszystkie checki (unauth→403, auth→200, traversal→404, CSP `default-src 'none'`+`script-src 'nonce-`)
- JSON manifestów walid (jeśli dotknięte — nie powinny); wersja bump patch przy commicie
- Nie oznaczać completed jeśli którakolwiek faili.

**Tests:**
- Wszystkie powyższe zwracają oczekiwane wartości (0 rozbieżności)

**Implementation decisions / remarks:**
- Komendy wykonane:
  - `test -f references/codex-tools.md` + sekcje "Orchestrated dispatch on Codex"/"Review gates on Codex"/`spawn_agent` → OK
  - `grep -l references/codex-tools.md` w 3 skillach → 3 trafienia
  - `implement` zakaz literalnego `Agent(subagent_type=)` na Codex + kierowanie do codex-tools → obecne
  - `node --check server.cjs` → OK
  - `start-server.sh` warning bind poza loopback → obecny; `bash -n` OK
  - `VENDORED.md` odnotowuje CSP hardening + `--host` warning
  - `bash -n smoke-test.sh` OK; pełne uruchomienie → 5/5 PASS (unauth 403, auth 200, traversal 404, CSP `default-src 'none'`+`script-src 'nonce-`, reject aktywnej treści)
  - JSON manifestów walid, hook emituje JSON, frontmatter skilli OK, `git diff --check` czysty
- Wyniki: 0 rozbieżności. Wersja 5.1.1 (bump patch przy commicie — poza scope implementacji).
- Housekeeping: CLAUDE.md zaktualizowany (2 miejsca) — codex-tools.md już istnieje (nie "yet"), realized example Codex opisany. AGENTS.md = symlink → CLAUDE.md, auto-sync. ADR: brak (deviation img-src ujęty w remarks Task 3). Memory: brak trwałej lekcji.
- Review gate #1 REJECTED (5× COMPLETENESS, jeden root cause): README.md + docs/ nadal głosiły przed-fixowe "Codex bez gate'ów / brak codex-tools.md", sprzeczne z Task 1/2 (reguła CLAUDE.md "Cross-Harness Editing Rules" wymaga aktualizacji README.md+docs/ przy zmianie pipeline behavior). Naprawione 5 miejsc: README l.106 (registered gates + oba references), l.412 (tabela Codex degraduje), l.474 (drzewo repo dodaje codex-tools.md), docs/review-gates.md l.45 (Codex degradacja dwustopniowa + link), docs/getting-started.md l.55 (Codex degradacja + link). Grep stale phrases → 0.
- Pominięte: none

**Example:**
```bash
test -f references/codex-tools.md && grep -l 'references/codex-tools.md' skills/implement/SKILL.md skills/generate-tasks/SKILL.md skills/feature-discuss/SKILL.md
node --check skills/feature-discuss/companion-scripts/server.cjs
bash skills/feature-discuss/companion-scripts/smoke-test.sh
```
