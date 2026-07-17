# Vendored: obra/superpowers

AbsolutPowers vendoruje (kopiuje, przycina i dostosowuje) wybrane skille z pluginu
[obra/superpowers](https://github.com/obra/superpowers) na licencji MIT. Vendoring
zamiast dependency runtime: pełna kontrola nad treścią, zero ryzyka konfliktu
priorytetów dwóch pluginów, zero zależności od marketplace'u w czasie działania.
Pełny tekst licencji: [`LICENSE-VENDORED`](./LICENSE-VENDORED)
(Copyright (c) 2025 Jesse Vincent).

## Źródło

- Repo: https://github.com/obra/superpowers
- Wersja: `6.1.1` (potwierdzona w `package.json` klona)
- Przypięty SHA (tag `v6.1.1`): `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Data vendoringu: 2026-07-13
- Klon roboczy: `vendor/superpowers/` (gitignorowany, poza drzewem pluginu — patrz `.gitignore`)

## Proces śledzenia upstreamu (kwartalnie)

Raz na kwartał, w klonie `vendor/superpowers/`:

1. `git fetch` — pobrać nowe tagi/commity upstreamu.
2. `git diff <pinowany-SHA>..<nowy-tag> -- skills/` — diff ograniczony wyłącznie do
   zvendorowanych skilli (nie całego repo obry).
3. Przegląd diffa ręcznie (skille to markdown — diffy są czytelne). Selektywne
   przeniesienie wartościowych zmian do lokalnych kopii w `skills/vendored/`.
4. Aktualizacja przypiętego SHA w tym pliku (sekcja "Źródło" powyżej) i w tabeli
   poniżej dla każdego zaktualizowanego skilla.

Świadomie akceptowany dryf: nie każda zmiana upstreamu musi trafić do
absolutpowers — kryterium jest wartość dla procesu Absolut Systems, nie parytet
wersji z obrą.

## Zvendorowane skille

| Skill | Źródłowa ścieżka | SHA | Lokalne modyfikacje |
|---|---|---|---|
| `using-git-worktrees` | `skills/using-git-worktrees/` | `d884ae0` | Skopiowany bez zmian treści poza notą MIT (frontmatter → adnotacja). Brak sekcji Cursor/Kimi/Antigravity/Gemini w źródle — nic do przycięcia. |
| `systematic-debugging` | `skills/systematic-debugging/` | `d884ae0` | Skopiowany razem z pomocniczymi plikami. Cross-ref cleanup (2026): odniesienia `superpowers:*` zastąpione/adnotowane (patrz nowa sekcja "Cross-reference cleanup"). |
| `verification-before-completion` | `skills/verification-before-completion/` | `d884ae0` | Skopiowany bez zmian treści poza notą MIT. Brak sekcji harnessów do przycięcia. |
| `dispatching-parallel-agents` | `skills/dispatching-parallel-agents/` | `d884ae0` | Skopiowany bez zmian treści poza notą MIT. Brak sekcji harnessów do przycięcia. |
| `finishing-a-development-branch` | `skills/finishing-a-development-branch/` | `d884ae0` | Skopiowany bez zmian treści poza notą MIT. **5.2.0:** banner na górze — w AbsolutPowers preferuj `ship` w składni aktywnego harnessu; ten skill = opcjonalne menu merge/PR/worktree z obry. Polityka: `references/fork-policy.md`. |
| `executing-plans` | `skills/executing-plans/` | `d884ae0` | Skopiowany bez zmian treści poza notą MIT. Zawiera odniesienie do `superpowers:subagent-driven-development` i do `../using-superpowers/references/` (dawca niewendorowany) — świadomie NIE przepisane (poza scope tej fazy; wire-up cross-referencji to fuzja z Faz 2/3 planu, nie kopiowanie). |
| `subagent-driven-development` | `skills/subagent-driven-development/` | `d884ae0` | Skopiowany razem z `implementer-prompt.md`, `task-reviewer-prompt.md`, `scripts/review-package`, `scripts/task-brief`, `scripts/sdd-workspace` bez zmian treści poza notą MIT. Brak sekcji harnessów do przycięcia. Odniesienia `superpowers:*` (writing-plans, requesting-code-review, test-driven-development, using-git-worktrees, finishing-a-development-branch, executing-plans) pozostawione as-is — integracja z `implement` to Faza 2 planu, poza scope tej fazy. |
| Visual companion (feature-discuss) | `skills/brainstorming/visual-companion.md` + `skills/brainstorming/scripts/{server.cjs,helper.js,frame-template.html,start-server.sh,stop-server.sh}` | `d884ae0` | Skopiowany do `skills/feature-discuss/visual-companion.md` + `skills/feature-discuss/companion-scripts/`. **Telemetria zneutralizowana**: w `server.cjs` usunięto stałą `SUPERPOWERS_BRAND_IMAGE_URL` (zdalne logo Prime Radiant) i gałąź `<img>` w `brandMarkup()`; flaga `SUPERPOWERS_TELEMETRY_DISABLED` zahardkodowana na `true` (niezależna od zmiennych środowiskowych); usunięto nieużywaną już `isTruthyEnv()`. Branding uproszczony do lokalnego tekstu, zero zewnętrznego GET. Ścieżki w `visual-companion.md` zaktualizowane `scripts/` → `companion-scripts/`. **Wpięty do `feature-discuss/SKILL.md`** (2026) — dodano pełny "Companion Protocol" z operacyjnymi krokami (oferta → start → Write ekranów do screen_dir → Read events → waiting screens → stop), plus integracja w Faza 1/3/4. Szczegóły techniczne (klasy, fragmenty) pozostają w `visual-companion.md`. **Utwardzenie bezpieczeństwa (review major-v5, fix):** (a) `server.cjs` — restrykcyjne CSP na odpowiedziach HTML z helperem (`default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; script-src 'nonce-{losowy}'`), helper i bootstrap-script jedyne skrypty z per-response noncem; reject aktywnej treści ekranu (`findActiveContent`: `<script`, inline `on*=`, `javascript:`, remote `src/href/action`, `<link>/<base>/<meta http-equiv>`) — ekran z aktywną treścią zastąpiony statycznym "Screen blocked" (upstream renderował ekran verbatim z CSP tylko `frame-ancestors`). (b) `start-server.sh` — ostrzeżenie na stderr przy bind poza loopbackiem (`BIND_HOST` ≠ `127.0.0.1`/`localhost`), nie blokujące (0.0.0.0 dozwolone dla kontenerów). |

Ogólna uwaga: żaden z 7 skilli bez fuzji nie zawierał sekcji specyficznych dla
Cursor/Kimi/Antigravity/Gemini w źródle (zweryfikowane grep-em) — jedynym plikiem
obry z takimi sekcjami jest `using-superpowers/` (dispatcher, świadomie
niewendorowany, patrz Faza 1 planu). Zadanie "przycięcia harnessów" jest więc
spełnione przez brak takich sekcji od startu; nic nie usunięto.

## Zvendorowany mechanizm hooka (Faza 5)

| Element | Źródłowa ścieżka | SHA | Lokalne modyfikacje |
|---|---|---|---|
| `hooks/hooks.json` | `hooks/hooks.json` | `d884ae0` | Skopiowany bez zmian — matcher `startup\|clear\|compact` i ścieżka komendy `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd` już pasowały 1:1 do naszej struktury. |
| `hooks/run-hook.cmd` | `hooks/run-hook.cmd` | `d884ae0` | Skopiowany bez zmian mechanizmu (polyglot cmd.exe/bash dispatcher) — dodano wyłącznie notę MIT jako linię REM w istniejącym bloku komentarza. |
| `hooks/session-start` | `hooks/session-start` | `d884ae0` | **Zvendorowany wyłącznie mechanizm**, treść własna. Zachowano wzorzec: `escape_for_json`, odczyt pliku źródłowego, emisja `hookSpecificOutput.additionalContext`. Usunięto gałęzie Cursor (`additional_context`) i Copilot CLI/SDK-standard (top-level `additionalContext`) — zostawiono wyłącznie gałąź Claude Code (`CLAUDE_PLUGIN_ROOT` set), bo Codex czyta `AGENTS.md`, nie ten hook. Zamiast `skills/using-superpowers/SKILL.md` czyta `hooks/session-context.md`. |
| `hooks/session-context.md` | brak odpowiednika (treść `using-superpowers/SKILL.md` NIE skopiowana) | — | **Całkowicie własna treść** (~15 linii merytorycznych): łańcuch pipeline'u absolutpowers, powrót do checklisty po `compact`, auto-trigger wyłącznie dla `debug`/`systematic-debugging` i `verification-before-completion`. Współdzielona jako źródło prawdy z integracją Pi (Faza 7). |

`.codex-plugin/plugin.json` świadomie NIE deklaruje hooka (hooki pluginu nie są wspierane na
Codex — patrz `CLAUDE.md` "Agent limitations in plugins" / "Codex runs without gates").
`.claude-plugin/plugin.json` deklaruje `"hooks": "./hooks/hooks.json"`.

## Zvendorowana integracja Pi (Faza 7)

| Element | Źródłowa ścieżka | SHA | Lokalne modyfikacje |
|---|---|---|---|
| `.pi/extensions/absolutpowers.ts` | `.pi/extensions/superpowers.ts` | `d884ae0` | **Zvendorowany wyłącznie mechanizm** (rejestracja `resources_discover`/`session_start`/`session_compact`/`agent_end`/`context`, dedup marker, wstawianie po `compactionSummary`), treść własna. Zamiast `readFileSync` na `skills/using-superpowers/SKILL.md` (nie istnieje w absolutpowers) czyta `hooks/session-context.md` — ten sam plik co Claude hook `hooks/session-start` (Faza 5), bez duplikacji treści. Marker zmieniony z `superpowers:using-superpowers bootstrap for pi` na `absolutpowers session discipline bootstrap for pi`. Inline `piToolMapping()` skrócony i odsyła do `references/pi-tools.md` zamiast pełnego duplikatu; dodaje notę o degradacji zarejestrowanych bramek review absolutpowers (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) na Pi. |
| `references/pi-tools.md` | `skills/using-superpowers/references/pi-tools.md` | `d884ae0` | Adaptowany: zachowana tabela akcja→prymityw Pi i sekcja o `pi-subagents`/braku subagenta, dodana nowa sekcja "Review gates on Pi" (nie istnieje w źródle — absolutpowers ma zarejestrowane typy agentów, których obra nie ma) opisująca dwustopniową degradację (dispatch generycznego subagenta z treścią `agents/{name}.md`, albo review inline z jawną notą o braku pełnej izolacji bramki). |

## Dawcy sekcji (NIE vendorowani) — Faza 2 fuzji

| Dawca | Cel fuzji | Grafty | Metoda | ADR |
|---|---|---|---|---|
| `writing-plans` (`vendor/superpowers/skills/writing-plans/`) | `skills/generate-tasks/SKILL.md` | 5 graftów wariant A (wszczepienie w istniejący szkielet generate-tasks, zero osobnej kopii pliku): Global Constraints, Produces/Consumes (blok Interfaces, dwupoziomowy z `Context Contract → Provides`), No Placeholders, Self-Review, wzmocnienie kompletnego kodu w `**Example:**` | rewrite-to-unify — szkielet generate-tasks zachowany (624 linie gęstej warstwy domenowej), mechanika writing-plans wszczepiona w istniejące sekcje, nie dopisana na końcu | `docs/adr/2026-07-13-faza2-generate-tasks-writing-plans-fuzja.md` |

`writing-plans` NIE jest zvendorowany do `skills/vendored/` — pozostaje wyłącznie w klonie
roboczym `vendor/superpowers/` jako dawca sekcji jednorazowo wszczepionych do `generate-tasks`;
nie ma lokalnej kopii pliku do śledzenia dryfu upstreamu w tabeli "Zvendorowane skille" powyżej.

Nota o `subagent-driven-development` (~44 wyżej) nie zmienia się w tej fazie: graft Fazy 2
dotyczy wyłącznie `generate-tasks` i nie dotyka cross-refów `subagent-driven-development` —
integracja tego skilla z `implement` to Faza 3 fuzji, poza scope tego wpisu.

## Forkowane skrypty (Faza 3 fuzji: implement ← subagent-driven-development)

| Skrypt | Źródłowa ścieżka | Docelowa ścieżka | SHA | Delta wobec oryginału |
|---|---|---|---|---|
| `sdd-workspace` | `skills/vendored/subagent-driven-development/scripts/sdd-workspace` | `skills/implement/scripts/sdd-workspace` | `d884ae0` | Zachowany mechanizm (self-ignoring `.gitignore`, `mkdir -p`, `cd "$dir" && pwd`). Zmieniona **lokalizacja katalogu scratch**: z `<repo-root>/.superpowers/sdd` na scratch pod katalogiem faz feature'a, przekazanym przez orchestrator via `AP_TASKS_DIR` (`"${AP_TASKS_DIR:?AP_TASKS_DIR required}/.scratch"`). Dodana nota atrybucji MIT w nagłówku. |
| `review-package` | `skills/vendored/subagent-driven-development/scripts/review-package` | `skills/implement/scripts/review-package` | `d884ae0` | Zachowany mechanizm i interfejs (`review-package BASE HEAD [OUTFILE]`, walidacja `git rev-parse`, sekcje `## Commits`/`## Files changed`/`## Diff`, `git diff -U10`). Domyślny OUTFILE wywołuje forkowany `sdd-workspace` (obok, w `skills/implement/scripts/`), nie wersję vendored — więc dziedziczy tę samą zmianę katalogu scratch. Dodana nota atrybutu MIT w nagłówku. |

`task-brief` (`skills/vendored/subagent-driven-development/scripts/task-brief`) świadomie
**NIE forkowany** w tej fazie — poza scope Fazy 3 (nie jest jeszcze wpięty w `implement`;
patrz `planning-phase-3-implement.md`).

Weryfikacja składni TS: `npx --package=typescript@latest -- tsc --noEmit --module esnext
--moduleResolution bundler --target es2022 --skipLibCheck .pi/extensions/absolutpowers.ts`
— wymaga tymczasowego symlinku `node_modules/@earendil-works/pi-coding-agent` (moduł
zainstalowany lokalnie globalnie w `/opt/homebrew/lib/node_modules/`); usunięty po
weryfikacji, nie jest częścią repo. `--skipLibCheck` pomija niepowiązane błędy typów w
przechodnich zależnościach pakietu `@earendil-works/pi-coding-agent` samego
(`undici-types`, `@modelcontextprotocol/sdk`) — nasz plik przechodzi zero błędów zarówno
z, jak i bez tej flagi.

## Cross-reference cleanup (2026-07)

Podczas audytu skilli (po vendoringu Fazy 1-3) posprzątano odwołania `superpowers:*`
w vendored kopiach. Zmiany minimalne, dokumentacyjne + precyzyjne zastąpienia, żeby
ułatwić przyszłe upstream diffy.

Dotyczy:
- `skills/vendored/systematic-debugging/SKILL.md`
  - `superpowers:test-driven-development` → notka o konwencji `**Test-first:**` w AbsolutPowers (generate-tasks/implement)
  - `superpowers:verification-before-completion` → lokalny vendored odpowiednik
- `skills/vendored/executing-plans/SKILL.md`
  - `superpowers:subagent-driven-development`, `superpowers:finishing-a-development-branch`, `superpowers:writing-plans`, `../using-superpowers/references/` → adnotacje + mapowanie na lokalne vendored + `ship` / `generate-tasks`
- `skills/vendored/subagent-driven-development/SKILL.md` + skrypty
  - Wiele `superpowers:XXX` w sekcjach Integration, diagramach, Prompt Templates
  - `requesting-code-review` (niezvendorowane) → odwołanie do AbsolutPowers `review` / `review-implementation` / `triada-review`
  - `.superpowers/sdd` ścieżki w komentarzach i przykładach → dodano notki wyjaśniające, że aktywna implementacja używa forkowanych skryptów w `skills/implement/scripts/` + `progress.md` ledger
  - `writing-plans` → grafted do `generate-tasks`
  - `finishing-a-development-branch` → mapowane na `ship`

Skrypty w vendored/ dostały nagłówki z notką o forkach.

Zmiany dodają jasność dla użytkownika AbsolutPowers bez niszczenia wierności oryginałowi upstream (dla kwartalnych przeglądów).

Nowe nagłówki w plikach + sekcja w VENDORED.md. Żadnych zmian w logice promptów poza adnotacjami.
