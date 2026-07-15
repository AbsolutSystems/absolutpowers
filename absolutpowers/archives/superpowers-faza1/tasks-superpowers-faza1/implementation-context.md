# Implementation Context: Superpowers vendoring — Faza 1

## Purpose
Handoff między workerami faz. Trzymaj zwięźle — tylko fakty potrzebne kolejnym fazom.

## Completed Phases
- Phase 1: Infrastruktura vendoringu + atrybucja MIT — completed.
- Phase 2: Kolaps do jednego drzewa `skills/` — completed.
- Phase 3: Top-level agents/commands + rewire manifestów/marketplace'ów — completed.
- Phase 4: Kopiowanie + przycinanie zvendorowanych skilli obry — completed.
- Phase 5: Slim hook (session-start) — completed.
- Phase 6: Usunięcie luster i skryptów sync — completed.
- Phase 7: Wsparcie harnessu Pi — completed.
- Phase 8: Bump 5.0.0 + README/docs/install — completed.

## Created / Changed API (Phase 8)
- Both manifests bumped to `5.0.0`. README/CLAUDE/docs rewritten for the single-tree v5 architecture (3 harnesses), MIT attribution added (README `## Attribution` + `## Vendored Skills & Hook`), `## Adding a New Harness` recipe added to `CLAUDE.md`. **Precise Codex/Pi correction applied repo-wide** (registered-agent-type registry vs subagent-dispatch primitive) — see phase file remarks for the full list of touched files. **Phase 99 (final verification) must use `git grep`/`--include='*.md'` scoping (not a bare recursive grep), or exclude `vendor/`** — a naive whole-tree grep also matches `vendor/superpowers/`'s own docs and is not a meaningful signal.

## Created / Changed API
- **Kanoniczne drzewo `skills/{name}/SKILL.md` (16 skilli)** — jedno źródło prawdy na top-level (przeniesione z `claude/skills/` przez `git mv`). Zawiera pliki pomocnicze `skills/debug/` (condition-based-waiting.md, condition-based-waiting-example.ts, defense-in-depth.md, root-cause-tracing.md). Treść niezmieniona vs poprzedni `claude/`. Kolejne fazy (manifesty, hook, Pi, docs) muszą wskazywać na `skills/`, nie `claude/skills/`.
- **Top-level manifesty i artefakty (Phase 3):**
  - `agents/*.md` (9) i `commands/*.md` (1, `triada-review.md`) na top-level (git mv z `claude/`, R100). Claude-only; inne harnessy ignorują.
  - `.claude-plugin/plugin.json` (root) — BEZ pól ścieżkowych; Claude auto-discover `skills/`/`agents/`/`commands/`/`hooks/` względem root pluginu. BEZ pola `hooks` (auto-discovery `hooks/hooks.json` — wzorzec obry). Phase 5 doda/potwierdzi hooks jeśli będzie trzeba.
  - `.codex-plugin/plugin.json` (root) — deklaruje `"skills": "./skills/"` (root-relative, poprawne). `hooks: {}` (pusty).
  - `.claude-plugin/marketplace.json` → plugin `source: "."`; `.agents/plugins/marketplace.json` → plugin `source.path: "."`. Oba wskazują root, nie `claude/`/`codex/`.
  - `name` = `absolutpowers` w obu manifestach i obu marketplace'ach (bez regresji identyfikatora). Wersja `3.13.0` niezmieniona — bump do 5.0.0 w P8.
  - `AGENTS.md` = relatywny symlink → `CLAUDE.md` (readlink `CLAUDE.md`, bez leading `/`). Kanał bootstrapu dyscypliny dla harnessów czytających AGENTS.md (Codex); hook Claude (P5) to tylko re-injekcja po kompakcji, nie bootstrap. Phase 8 (docs/CLAUDE.md) i Phase 5 (hook) mogą na nim polegać.

## Decisions Made
- **(P2 — POTWIERDZONE) `claude/` = źródło prawdy; jedno host-agnostyczne body serwowane wszystkim harnessom.** Codex toleruje nieznany frontmatter (`allowed-tools`, `argument-hint`) i traktuje sekcje gate (`## Review Gate` + wywołania `Agent(subagent_type=...)`) jako inertną prozę → "Codex runs without gates". Potwierdzone wzorcem obry (`vendor/superpowers/skills/using-superpowers/SKILL.md`: jedno body dla 8 harnessów). ŻADEN klucz frontmatter nie wymagał przeniesienia do `references/` — kolaps to czysty `git mv`.
- **Konwencja host-agnostyczności (wiążąca kolejne fazy):** body skilli neutralne; różnice per harness idą do `references/{harness}-tools.md` czytanych warunkowo (wzorzec obry: `codex-tools.md`, `pi-tools.md`, `antigravity-tools.md`). Dodanie harnessu = nowy reference + integracja, ZERO edycji skilli. Sekcje gate/agent są Claude-only i degradują gracefully na Codex/Pi.
- **Parytet z Codex:** żadna unikalna treść Codeksowa NIE zaginęła — pozorne "codex-only" linie to relokacja/przeredagowanie treści obecnej w claude, plus adaptacja modelu sekwencyjnego w `implement` (semantycznie równoważna delegacji do `implementation-worker`).

## Created / Changed API (Phase 4)
- **`skills/vendored/{name}/`** — 7 no-fusion skills copied verbatim from `vendor/superpowers/skills/` (SHA `d884ae0`, tag v6.1.1): `using-git-worktrees`, `systematic-debugging` (+ helper files: CREATION-LOG.md, condition-based-waiting.md/.ts, defense-in-depth.md, root-cause-tracing.md, find-polluter.sh, test-*.md), `verification-before-completion`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `executing-plans`, `subagent-driven-development` (+ `implementer-prompt.md`, `task-reviewer-prompt.md`, `scripts/{review-package,task-brief,sdd-workspace}`, all executable). Each `SKILL.md` has a one-line MIT/source note right after frontmatter. **No harness-specific sections existed in any of the 7 source skills** (verified by grep for Cursor/Kimi/Antigravity/Gemini) — the only file upstream with those sections is `using-superpowers/` (not vendored). So "trimming" produced zero diffs vs upstream beyond the MIT note.
- **`skills/feature-discuss/visual-companion.md` + `skills/feature-discuss/companion-scripts/{server.cjs,helper.js,frame-template.html,start-server.sh,stop-server.sh}`** — visual companion vendored from `vendor/superpowers/skills/brainstorming/`. Telemetry **hard-removed** (not just env-gated): `SUPERPOWERS_BRAND_IMAGE_URL` constant and the `<img>` branch in `brandMarkup()` deleted from `server.cjs`; `SUPERPOWERS_TELEMETRY_DISABLED` hardcoded `true`; dead `isTruthyEnv()`/`TELEMETRY_DISABLE_ENV_VARS` removed. Branding is now a plain local text string, zero external GET possible. All `scripts/` references in `visual-companion.md` rewritten to `companion-scripts/`. **NOT wired into `skills/feature-discuss/SKILL.md`** — files sit alongside, ready for the fusion phase (plan Faza 2/3, out of scope for absolutpowers Faza 1).
- **`VENDORED.md`** table filled: one row per vendored skill/subtree with source path, SHA, and local-modification notes (harness trims, telemetry removal, MIT note placement, unresolved `superpowers:*` cross-references).

## Created / Changed API (Phase 5)
- **`hooks/hooks.json`** — `SessionStart` hook, matcher `startup|clear|compact`, command
  `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start`. Copied verbatim from
  `vendor/superpowers/hooks/hooks.json` (already matched our layout, zero edits needed).
- **`hooks/run-hook.cmd`** — vendored polyglot cmd.exe/bash dispatcher mechanism, unchanged
  beyond one MIT `REM` note in the existing top comment block (inert on both platforms). `chmod +x`
  applied.
- **`hooks/session-start`** — our own Claude-only script (vendored mechanism: `escape_for_json`,
  `printf`-based JSON emission, `hookSpecificOutput.additionalContext`). Reads
  `hooks/session-context.md` (NOT `skills/using-superpowers/SKILL.md`). Cursor/Copilot/SDK-standard
  output branches from upstream removed — only the Claude Code branch remains (Codex reads
  `AGENTS.md`, not this hook).
- **`hooks/session-context.md`** — **the shared source-of-truth content** later consumed by both
  this hook AND the Phase 7 Pi extension. ~15 substantive lines, entirely own content (not
  vendored): explicit pipeline chain (`@feature-discuss` -> `@generate-tasks` -> `@implement` ->
  `@review`/`@triada-review`), return-to-active-checklist rule for the `compact` branch, and
  auto-trigger restricted to exactly two guardian skills — `@debug` (or vendored
  `systematic-debugging`) and vendored `verification-before-completion`. **Phase 7 must read this
  file at runtime from the Pi extension, not duplicate its text inline** — same pattern
  `hooks/session-start` uses (`cat` the file, do not hardcode the string elsewhere).
- **`.claude-plugin/plugin.json`** now has `"hooks": "./hooks/hooks.json"` (explicit field, added
  on top of Claude Code's directory auto-discovery convention already relied on for
  skills/agents/commands). `.codex-plugin/plugin.json` unchanged — still no `hooks` key (Codex has
  no plugin-level hook support, confirmed both by grep and by upstream's own
  `.codex-plugin/plugin.json` in `vendor/superpowers/`).
- `VENDORED.md` — new "Zvendorowany mechanizm hooka (Faza 5)" table appended after the skills
  table; documents source paths, pinned SHA `d884ae0`, per-file local modifications.

## Created / Changed API (Phase 6)
- **Lustra i skrypty sync USUNIĘTE (git):** `codex/` (18 plików, w tym `codex/scripts/sync_claude_to_agents.py` i `codex/skills/tech-lead-advisor/`), `scripts/sync_claude_to_agents.py`, `scripts/diff-skills.sh`. `claude/` nie miał trackowanych plików (empty po P2 git mv) — usunięty fizycznie. `scripts/` zniknął (pusty). Jedyne źródło prawdy to `skills/` + top-level `agents/`/`commands/`/manifesty.
- **`sync_claude_to_agents.py` NIE zarchiwizowany** — obsoletny, bo `AGENTS.md` to symlink → `CLAUDE.md` (P3). Jeśli kolejna faza/dok potrzebuje mechanizmu CLAUDE.md→AGENTS.md, wzorzec to **symlink**, nie skrypt generujący.
- **`CLAUDE.md` odkłamany minimalnie (P6):** Repository Layout, Key Development Commands, Cross-Harness Editing Rules (dawniej "Cross-Platform"), Versioning — dopasowane do jednego drzewa. **Pełny przepis README/CLAUDE/docs to Phase 8.** Rezydualna stara fraza ("Both skills live in both trees" itp.) w innych sekcjach CLAUDE.md do sprzątnięcia w P8.
- **Verification-grep caveat (P8 + final-verification MUSZĄ to uwzględnić):** literalny broad grep `claude/skills|codex/skills|sync_claude_to_agents|diff-skills` na `*.md`/`*.json` NIGDY nie zwróci pustego. Dwie trwałe klasy trafień to NIE-cele: (a) legit `.claude/skills/learned/` (ścieżki target-projektu w `CLAUDE.md` + `skills/harvest` + `skills/try-learn-skill` — poprawna treść, zostaje); (b) archiwum `absolutpowers/feature/*.md` (zapisy zamkniętych ficzerów — nie przepisywać). Po ich wykluczeniu pozostają TYLKO `README.md` + `docs/contributing.md` — **do sprzątnięcia w Phase 8** (są w jego Write Scope). Sensowna komenda bramki: dodać `| grep -v '\.claude/skills/learned' | grep -v 'absolutpowers/feature/'`.

## Created / Changed API (Phase 7)
- **`.pi/extensions/absolutpowers.ts`** — Pi integration. `resources_discover` → `{ skillPaths: [resolve(packageRoot, "skills")] }`. `session_start`/`session_compact` set `injectBootstrap = true`; `agent_end` sets it `false`. `context` hook reads `hooks/session-context.md` (NOT any SKILL.md — no `using-superpowers` exists in absolutpowers) and wraps it in `<EXTREMELY_IMPORTANT>` + dedup marker `absolutpowers session discipline bootstrap for pi` + a short inline Pi-tool-mapping summary that points to `references/pi-tools.md`. Same dedup-guard/insert-after-`compactionSummary` mechanism as upstream, unchanged. **Later phases (P8 docs) should cite this file as the Pi integration entry point** — do not duplicate `hooks/session-context.md`'s text anywhere else; both the Claude hook (P5) and this extension read that one file at runtime.
- **`references/pi-tools.md`** — new top-level `references/` directory (did not exist before P7; `codex-tools.md` was NOT created — no earlier phase produced it and it is out of this phase's Write Scope, so `references/` currently contains only `pi-tools.md`). Maps `Skill`→native Pi skills/`read`, subagent dispatch→`pi-subagents`, task tracking→`TODO.md`/plan files, and adds a "Review gates on Pi" section (new content, not in upstream) covering degradation of AbsolutPowers' registered agent types (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) on Pi: dispatch a generic subagent with the target `agents/{name}.md` as prompt if `pi-subagents` is installed, else review inline with an explicit non-isolation disclaimer.
- **Bounded Pi/Codex reference pointer added to exactly 3 skills** (verified via `grep -l 'subagent_type\|Agent(' skills/*/SKILL.md` → exactly these 3, no others): `skills/feature-discuss/SKILL.md` (before Faza 5B's `qa-enrichment` dispatch), `skills/generate-tasks/SKILL.md` (right under the `## Review Gate` heading), `skills/implement/SKILL.md` (right after the two-modes bullet list, near the top, covering all of its later gate sections in one shot). One `>` blockquote line each, no skill logic changed. `skills/analyze/SKILL.md`'s pre-existing optional subagent-delegation note was deliberately left untouched (generic optional delegation, not a registered-agent review gate — out of Task 3's scope).
- **`grep -l 'references/.*-tools.md' skills/*/SKILL.md`** is now the authoritative "which skills point at harness references" check — returns exactly `feature-discuss`, `generate-tasks`, `implement`. Phase 8 (or any future phase adding another harness reference) should preserve this bounded set unless a skill gains new subagent-dispatch logic.
- **TS verification for `.pi/extensions/*.ts` going forward:** `@earendil-works/pi-coding-agent` is not a repo dependency (no `package.json` at root, none added by this phase — out of Write Scope). Verification requires a temporary symlink from a local `node_modules/@earendil-works/pi-coding-agent` to wherever the package is installed (this dev machine has it globally at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`), then `npx --package=typescript@latest -- tsc --noEmit --module esnext --moduleResolution bundler --target es2022 --skipLibCheck <file>.ts`, then delete the symlink/`node_modules` — do not commit it. `--skipLibCheck` is required because the package's own transitive deps (`undici-types`, `@modelcontextprotocol/sdk` inside its `node_modules`) have unrelated pre-existing type errors; without the flag those same errors appear but nothing new from our file.

## Open Items For Later Phases
- **Rozjazd nazw tech-lead — ROZSTRZYGNIĘTE w Phase 6:** tech-lead zostaje jako agent
  Claude-only (`agents/tech-lead-agent.md`); Codeksowy skill `tech-lead-advisor` był tylko
  cieniem tego agenta i znika wraz z `codex/`. Nazwa NIE zmieniona → `commands/triada-review.md`
  (`absolutpowers:tech-lead-agent`) bez zmian. Codex traci samodzielny trigger — akceptowalne
  (agenty/bramki są Claude-only, degradują gracefully). Brak dalszej akcji dla kolejnych faz.
- `claude/skills/`, `claude/agents/`, `claude/commands/`, `claude/.claude-plugin/` to teraz puste katalogi (git nie trackuje) — Phase 6 usuwa całe `claude/` i `codex/`. `codex/.codex-plugin/` przeniesiony do root `.codex-plugin/` w P3; `codex/skills/` i `codex/scripts/` nadal istnieją do P6. Diffing parytetu do Phase 6 rób względem `codex/skills/`.
- **Symlink `.claude/triada-review.agents.json`:** `commands/triada-review.md` wspomina `.claude/triada-review.agents.json` — to per-project config w target-projekcie, NIE drzewo pluginu. Grep-check „stale claude/ paths" musi to wykluczać (nie jest wiszącą referencją).
- **Nierozwiązane cross-referencje `superpowers:*` w vendorowanych skillach (Phase 4) — pełny inwentarz:**
  - `skills/vendored/executing-plans/SKILL.md`: `superpowers:writing-plans`, `superpowers:finishing-a-development-branch`, `superpowers:using-git-worktrees`, `superpowers:subagent-driven-development`, oraz `../using-superpowers/references/`.
  - `skills/vendored/subagent-driven-development/SKILL.md`: `superpowers:writing-plans`, `superpowers:requesting-code-review`, `superpowers:test-driven-development`, `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:executing-plans`.
  - `skills/vendored/systematic-debugging/SKILL.md` (dodane po phase-review, wcześniej pominięte w inwentarzu): `superpowers:test-driven-development` (linia ~181, ~289), `superpowers:verification-before-completion` (linia ~290). **Kolizja nazw:** `superpowers:verification-before-completion` odwołuje się do nieistniejącego namespace `superpowers:`, mimo że lokalny odpowiednik `skills/vendored/verification-before-completion/` już istnieje w tym samym vendoringu — to NIE jest automatyczne aliasowanie, tekst nadal literalnie mówi `superpowers:`.
  - Część dawców (`writing-plans`, `using-superpowers`, `requesting-code-review`, `test-driven-development`) nie jest vendorowana w ogóle (fuzja-only donors lub świadomie pominięte — patrz plan Faza 2). Wszystkie powyższe odniesienia świadomie pozostawione as-is w P4 (poza scope kopiowania — czyste `cp`, bez rewrite'u treści).
  - Faza 2/3 planu migracji (integracja sdd w `implement`, fuzja `writing-plans`→`generate-tasks`) będzie musiała dla każdego z powyższych albo przepisać referencję na lokalny odpowiednik absolutpowers (np. `superpowers:verification-before-completion` → lokalny `skills/vendored/verification-before-completion/`), albo jawnie udokumentować które zostają martwe/nieaktywne. Ten bullet jest pełnym inwentarzem — kolejna faza nie musi re-grepować, tylko zaadresować listę.
- **Companion nie ma jeszcze integracji runtime:** `skills/feature-discuss/visual-companion.md` + `companion-scripts/` istnieją jako gotowe pliki, ale `skills/feature-discuss/SKILL.md` ich nie referuje. Wire-up (just-in-time oferowanie companiona przy pytaniach wizualnych, fallback bez Node) to osobna fuzja poza scope Fazy 1 absolutpowers (plan Faza 2/3).

## Test Utilities / Fixtures
- Walidacja JSON: `python3 -m json.tool`. Walidacja hooka: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool`.
- Walidacja składni companiona: `node -c skills/feature-discuss/companion-scripts/server.cjs` (wymaga Node.js na maszynie deweloperskiej; sam companion degraduje gracefully bez Node w target-projekcie — patrz plan Faza 1.3).
- Telemetria companiona zero-trust check: `grep -rl 'primeradiant.com' skills/feature-discuss/` (oczekiwany brak trafień — komentarze w kodzie też muszą unikać tego literału, nie tylko żywy kod).

## Constraints For Next Phases
- Wszystkie przenosiny plikami przez `git mv` (zachowanie historii).
- Nota MIT obry musi zostać w każdym zvendorowanym pliku (LICENSE-VENDORED + nagłówek/notka per skill).
- Klon obry żyje w `vendor/superpowers/` (gitignorowany, poza repo pluginu). Klon jest checked-out na tagu `v6.1.1` (detached HEAD) — kolejne fazy (P4) czytają skille bezpośrednio z tej ścieżki na dysku, nie z GitHub.
- `vendor/superpowers/CLAUDE.md` zawiera reguły kontrybucji obry (PR template, zakaz "compliance" zmian do skilli, itd.) — dotyczą wyłącznie ewentualnych PR-ów upstream, nie mają zastosowania do procesu vendoringu (kopiowania) w P4.

## Verification History
- Phase 1: `test -f LICENSE-VENDORED && grep -q 'Jesse Vincent' LICENSE-VENDORED` -> OK; `test -f VENDORED.md && grep -qE '[0-9a-f]{7,40}' VENDORED.md` -> OK; `git check-ignore vendor/superpowers` -> OK.
- Phase 2: `ls skills/ | wc -l` -> 16; frontmatter loop (skills/*/SKILL.md head-1 == `---`) -> brak outputu (OK); `ls skills/debug/` -> SKILL.md + 4 helpers; `git log --follow --oneline skills/feature-discuss/SKILL.md` -> historia sprzed przenosin (sięga initial release); wszystkie 16 przeniesień wykryte jako git rename (R).
- Phase 3: 4× `python3 -m json.tool` (oba plugin.json + oba marketplace.json) -> OK; `grep -rn 'claude/\|codex/' .claude-plugin/ .codex-plugin/ .agents/` -> no stale paths; `test -d agents && test -d commands` -> OK; `ls agents/*.md | wc -l` -> 9; `ls commands/*.md | wc -l` -> 1; `name` obu manifestów/marketplace'ów = `absolutpowers`; marketplace source = root (`.`); `test -L AGENTS.md && readlink` -> `CLAUDE.md` (relatywny); przenosiny agents/commands/plugin.json wykryte jako R100.
- Phase 4: `ls skills/vendored/ | wc -l` -> 7; `test -x skills/vendored/subagent-driven-development/scripts/task-brief` -> OK (i sdd-workspace, review-package, wszystkie 755); `grep -rl 'primeradiant.com' skills/feature-discuss/` -> brak trafień; `grep -c '|' VENDORED.md` -> tabela wypełniona (8 wierszy danych: 7 skilli + companion); `grep -rliE 'cursor|kimi|antigravity|gemini' skills/vendored/` -> brak trafień (nic do przycięcia, potwierdzone źródłowo); `node -c skills/feature-discuss/companion-scripts/server.cjs` -> syntax OK; globalny JSON-loop i frontmatter-loop z parent tasks file -> OK (bez regresji).
- Phase 5: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool` -> valid JSON, `hookSpecificOutput.additionalContext` present and contains the exact text of `hooks/session-context.md` (verified by inspection, not duplicated inline); `python3 -m json.tool hooks/hooks.json` -> OK; `grep -q 'startup|clear|compact' hooks/hooks.json` -> OK; `test -x hooks/run-hook.cmd` -> OK; `CLAUDE_PLUGIN_ROOT=. hooks/run-hook.cmd session-start | python3 -m json.tool` -> OK (dispatcher path exercised end-to-end); `python3 -m json.tool .claude-plugin/plugin.json` -> OK, contains `"hooks": "./hooks/hooks.json"`; `grep hooks .codex-plugin/plugin.json` -> no match (confirmed absent); global JSON-loop + frontmatter-loop from parent tasks file re-run -> OK (no regression). Repo-wide stale-path grep still flags pre-existing `claude/skills`/`codex/skills` references in `CLAUDE.md`/`README.md` — out of scope for this phase (Phase 6/8 territory), not introduced by Phase 5.

- Phase 6: `test ! -d claude && test ! -d codex` -> "mirrors removed"; `test ! -f scripts/diff-skills.sh` + `test ! -f scripts/sync_claude_to_agents.py` -> gone; `scripts/` empty/gone; `git status` -> 20 staged deletions (18 codex + 2 scripts); global JSON-loop (`git ls-files '*.json'` + `python3 -m json.tool`) -> all valid (no regression); `grep 'claude/skills|...' CLAUDE.md` -> only legit `.claude/skills/learned/` (line ~102, target-project path). Stale-ref broad grep residuals after excluding legit `.claude/skills/learned` + `absolutpowers/feature/` archive = only `README.md` + `docs/contributing.md` (Phase 8 Write Scope). tech-lead-advisor content compared vs tech-lead-agent -> same function, cień agenta, safe to drop on Codex.

- Phase 7: `test -f .pi/extensions/absolutpowers.ts` -> OK; `test -f references/pi-tools.md && grep -q 'pi-subagents' references/pi-tools.md` -> OK; `grep -c 'session-context.md' .pi/extensions/absolutpowers.ts` -> 2 (>0); TS check `npx --package=typescript@latest -- tsc --noEmit --module esnext --moduleResolution bundler --target es2022 --skipLibCheck .pi/extensions/absolutpowers.ts` (with a temporary `node_modules/@earendil-works/pi-coding-agent` symlink to the machine's global install, removed after) -> zero errors; sanity-checked against a deliberately broken copy (bad import, missing `node:` types) to confirm the check is real, not a no-op -> broken copy produced 5 real errors, our file produced 0; `grep -l 'references/.*-tools.md' skills/*/SKILL.md` -> exactly `feature-discuss`, `generate-tasks`, `implement` (bounded, matches the `subagent_type\|Agent(` dispatch grep 1:1); global JSON-loop + frontmatter-loop + repo-wide stale-path grep from parent tasks file re-run -> OK, same pre-existing README.md/docs/contributing.md residuals as Phase 6 (no regression, not introduced here).

## Vendored SHA
- Repo: `obra/superpowers`, tag `v6.1.1`, `package.json` version `6.1.1` (potwierdzone).
- SHA (pełny, 40 znaków): `d884ae04edebef577e82ff7c4e143debd0bbec99`
