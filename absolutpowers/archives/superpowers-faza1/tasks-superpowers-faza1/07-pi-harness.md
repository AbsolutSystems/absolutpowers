# Phase 7: Wsparcie harnessu Pi

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `skills/` istnieje jako jedno drzewo (Phase 2 Provides) — Pi rejestruje ten katalog.
- `hooks/session-context.md` istnieje (Phase 5 Provides) — wspólna treść wstrzykiwana; Pi extension czyta TEN plik, nie duplikuje treści.
- `vendor/superpowers/.pi/extensions/superpowers.ts` + `vendor/superpowers/skills/using-superpowers/references/pi-tools.md` (Phase 1 Provides) — wzorzec do adaptacji.

### Provides (for later phases)
- `.pi/extensions/absolutpowers.ts` — integracja Pi: rejestruje `skills/` przez `resources_discover`, re-injektuje treść z `hooks/session-context.md` na `session_start`/`session_compact`, wyłącza na `agent_end`.
- `references/pi-tools.md` — mapowanie akcji skilli na prymitywy Pi (Skill→natywne skille, subagent→pi-subagents, todo→TODO.md).
- Warunkowe wskaźniki `references/pi-tools.md` w skillach dispatchujących subagenty (implement + skille z bramkami).

## Read Scope
- `vendor/superpowers/.pi/extensions/superpowers.ts` (wzorzec integracji)
- `vendor/superpowers/skills/using-superpowers/references/pi-tools.md` (wzorzec mapowania)
- `hooks/session-context.md` (wspólna treść — Pi wstrzykuje to samo co Claude hook)
- `skills/implement/SKILL.md` + skille wywołujące `Agent(subagent_type=...)` (miejsca wymagające wskaźnika Pi)

## Write Scope
- `.pi/extensions/absolutpowers.ts`
- `references/pi-tools.md`
- `skills/implement/SKILL.md` i inne skille dispatchujące subagenty (tylko dodanie jednolinijkowego wskaźnika warunkowego)

## Objective
Dodać Pi jako trzeci wspierany harness wzorcem obry: rozszerzenie TS rejestrujące drzewo `skills/` i re-injektujące wspólną treść dyscypliny na starcie/kompakcji sesji (odpowiednik matchera `startup|compact` hooka Claude), plus reference file mapujący akcje skilli na prymitywy Pi. Bramki review (zarejestrowane agenty Claude) degradują na Pi: albo `pi-subagents` jeśli zainstalowany, albo wykonanie sekwencyjne z jawną notą o braku możliwości.

## Tasks

### Task 1: Rozszerzenie Pi `.pi/extensions/absolutpowers.ts`
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Zaadaptować `vendor/superpowers/.pi/extensions/superpowers.ts` do `.pi/extensions/absolutpowers.ts`
- `resources_discover` → zwraca `{ skillPaths: [resolve(packageRoot, "skills")] }`
- `session_start` + `session_compact` → `injectBootstrap = true`; `agent_end` → `false` (SUBAGENT-STOP equivalent — subagenci nie dostają re-injekcji)
- `context` hook → wstrzykuje treść czytaną z `hooks/session-context.md` (NIE z SKILL.md — absolutpowers nie ma using-superpowers), owiniętą w `<EXTREMELY_IMPORTANT>` + marker deduplikacji + mapowanie narzędzi Pi (inline skrót lub odesłanie do `references/pi-tools.md`)
- Zachować guard deduplikacji (nie wstrzykiwać jeśli treść już w kontekście) i wstawianie po compactionSummary — jak w oryginale
- Zależność typu: `@earendil-works/pi-coding-agent` (`ExtensionAPI`); NIE hardcode'ować `Date.now()` jeśli Pi API tego nie wymaga (oryginał używa — zostawić zgodnie z API Pi)
- Dodać notę MIT (adaptacja z obry); odnotować w `VENDORED.md`

**Tests:**
- `.pi/extensions/absolutpowers.ts` parsuje się (`npx tsc --noEmit` jeśli TS dostępny, albo `node --check` po transpilacji — udokumentować metodę)
- `resources_discover` wskazuje na `skills/` (ścieżka rozwiązuje się do istniejącego katalogu)
- `context` hook czyta `hooks/session-context.md` (nie duplikuje treści inline)
- Marker deduplikacji obecny; `agent_end` wyłącza injekcję

### Task 2: `references/pi-tools.md`
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Utworzyć `references/pi-tools.md` (wzorzec `vendor/superpowers/skills/using-superpowers/references/pi-tools.md`), dostosowany do absolutpowers:
  - Tabela akcja→prymityw Pi: `Skill` tool → natywne skille Pi (`read` SKILL.md / `/skill:name`); dispatch subagenta / bramka review → `subagent` z `pi-subagents` jeśli dostępny, inaczej sekwencyjnie + nota o braku bramki; task tracking → TODO.md / plan file
  - Sekcja o bramkach review: na Pi zarejestrowane agenty absolutpowers (`review-tasks`, `phase-review` itd.) nie istnieją — jeśli `pi-subagents` dostępny, dispatchuj generycznego subagenta z treścią promptu agenta; jeśli nie — wykonaj review inline z jawną notą, że to nie pełna bramka
- Dodać notę MIT (adaptacja); odnotować w `VENDORED.md`

**Tests:**
- `references/pi-tools.md` istnieje, ma tabelę akcja→prymityw i sekcję o degradacji bramek
- Mapuje ≥3 akcje (Skill, subagent, task tracking)

### Task 3: Warunkowe wskaźniki Pi w skillach dispatchujących subagenty
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- W skillach które dispatchują subagenty lub wywołują zarejestrowane agenty (`implement` + skille z sekcją review gate) dodać JEDNOLINIJKOWY wskaźnik warunkowy: "Na Pi/Codex: patrz `references/{harness}-tools.md` po mapowanie dispatchu subagentów/bramek"
- Edytować TYLKO te skille (nie wszystkie 16) — bounded, nie fuzja
- NIE zmieniać logiki skilla — tylko dodać wskaźnik (host-agnostyczność)

**Tests:**
- Skille z dispatchem subagentów mają wskaźnik do `references/`
- Skille bez dispatchu subagentów NIE zmienione (diff ograniczony)
- `grep -l 'references/.*-tools.md' skills/*/SKILL.md` zwraca tylko skille z dispatchem

## Phase Verification
Run:
- `test -f .pi/extensions/absolutpowers.ts && echo "Pi ext OK"`
- `test -f references/pi-tools.md && grep -q 'pi-subagents' references/pi-tools.md && echo "pi-tools OK"`
- `grep -c 'session-context.md' .pi/extensions/absolutpowers.ts` (>0 — czyta wspólną treść)
- (jeśli TS dostępny) `npx tsc --noEmit .pi/extensions/absolutpowers.ts` lub udokumentowana alternatywa

## Completion Criteria
- All phase tasks are completed.
- Pi extension rejestruje skills/ i re-injektuje wspólną treść; nie duplikuje treści z session-context.md.
- references/pi-tools.md mapuje akcje na prymitywy Pi z degradacją bramek.
- Wskaźniki warunkowe tylko w skillach z dispatchem (bounded edit).
- Noty MIT dodane; VENDORED.md zaktualizowany.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- `.pi/extensions/absolutpowers.ts` reuses upstream's `resources_discover`/`session_start`/`session_compact`/`agent_end`/`context` wiring verbatim (mechanism unchanged). Only the bootstrap-content source changed: instead of `readFileSync` on `skills/using-superpowers/SKILL.md` + `stripFrontmatter`, it reads `hooks/session-context.md` directly (no frontmatter to strip) — the same file the Claude `hooks/session-start` hook (Phase 5) reads, so the two integrations never drift apart.
- Dedup marker renamed `superpowers:using-superpowers bootstrap for pi` → `absolutpowers session discipline bootstrap for pi` (no `using-superpowers` concept exists here).
- `piToolMapping()` kept inline (short summary) but shortened and points to `references/pi-tools.md` for the full table + gate-degradation rules, per Task 1's "inline skrót lub odesłanie" option — chose "both": short inline text + explicit pointer.
- `references/pi-tools.md` adds a "Review gates on Pi" section not present in the upstream file — required because AbsolutPowers (unlike obra/superpowers) has registered Claude Code agent types (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) that the skills call by name; obra has zero registered agents so this concept didn't need mapping upstream. Degradation is two-tier: dispatch a generic `pi-subagents` subagent with the target `agents/{name}.md` content as its prompt, or fall back to an inline (non-isolated) review with an explicit disclaimer.
- Task 3 bounded edit: grep for `subagent_type\|Agent(` across `skills/*/SKILL.md` found exactly 3 skills with subagent dispatch/registered-agent calls — `feature-discuss` (qa-enrichment, review-plan), `generate-tasks` (review-tasks), `implement` (implementation-worker, phase-review, review-implementation). Added one `>` blockquote line at the first dispatch/gate section of each file (not per-gate, not per-file-top) — `skills/analyze/SKILL.md`'s existing "Claude-only opcjonalne delegacja do subagenta" note was left untouched since it is optional generic delegation, not a registered-agent gate, and Task 3 explicitly scopes to "implement + skille z sekcją review gate".
- TS verification method (documented in `VENDORED.md`): `@earendil-works/pi-coding-agent` is installed globally on this dev machine (`/opt/homebrew/lib/node_modules/`) but not as a repo dependency. Verified by temporarily symlinking `node_modules/@earendil-works/pi-coding-agent` to the global install, running `npx --package=typescript@latest -- tsc --noEmit --module esnext --moduleResolution bundler --target es2022 --skipLibCheck .pi/extensions/absolutpowers.ts` (zero errors), then deleting the symlink/`node_modules` — not committed, not part of the repo's dependency graph. Sanity-checked the harness itself by tsc-ing a deliberately broken copy (bad import, no `node:` types) to confirm real type errors surface; `--skipLibCheck` only suppresses pre-existing transitive-dependency errors inside `@earendil-works/pi-coding-agent`'s own `node_modules` (`undici-types`, `@modelcontextprotocol/sdk`), unrelated to our file — confirmed by also running without the flag and seeing the exact same list of unrelated errors and nothing new.
