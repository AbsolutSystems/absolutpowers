# Phase 5: Slim hook (session-start)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `.claude-plugin/plugin.json` na root (Phase 3 Provides) — do zadeklarowania hooka.
- `vendor/superpowers/hooks/` istnieje (Phase 1 Provides) — Read Scope czyta mechanizm hooka do zvendorowania.

### Provides (for later phases)
- `hooks/hooks.json` (matcher `startup|clear|compact`).
- `hooks/run-hook.cmd` (dispatcher komendy, zvendorowany mechanizm obry).
- `hooks/session-start` (skrypt Claude czytający wspólną treść).
- `hooks/session-context.md` — WSPÓLNA treść wstrzykiwana (chuda, własna, NIE using-superpowers); źródło prawdy współdzielone z integracją Pi (Phase 7).
- `.claude-plugin/plugin.json` z zadeklarowanym hookiem.

## Read Scope
- `vendor/superpowers/hooks/{hooks.json,run-hook.cmd,session-start}` (mechanizm do zvendorowania)
- `plan-migracji-hybrydowej-superpowers.md` (Faza 1.4 — treść slim hooka)
- `CLAUDE.md` (łańcuch pipeline'u do przypomnienia w treści hooka)

## Write Scope
- `hooks/**`
- `.claude-plugin/plugin.json` (deklaracja hooka)

## Objective
Zvendorować MECHANIZM hooka obry (matcher startup|clear|compact + run-hook.cmd), ale z własną chudą treścią zamiast wstrzykiwania pełnego `using-superpowers`. Cel: re-injekcja dyscypliny po kompakcji kontekstu, kluczowe dla długich sesji implement i nocnych runów.

## Tasks

### Task 1: Zvendorować mechanizm hooka
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Skopiować `vendor/superpowers/hooks/hooks.json` → `hooks/hooks.json`, zachować matcher `startup|clear|compact`, dostosować ścieżkę komendy do `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd`
- Skopiować `vendor/superpowers/hooks/run-hook.cmd` → `hooks/run-hook.cmd` (dispatcher; przyciąć do session-start jeśli obra ma więcej hooków)
- Dodać notę MIT do run-hook.cmd; odnotować w `VENDORED.md`

**Tests:**
- `hooks/hooks.json` to poprawny JSON z matcherem `startup|clear|compact`
- `hooks/run-hook.cmd` istnieje i jest wykonywalny (`test -x`)

### Task 2: Napisać wspólną chudą treść + skrypt session-start
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Utworzyć `hooks/session-context.md` — WSPÓLNE ~10-15 linii treści (źródło prawdy dla Claude hooka ORAZ integracji Pi z Phase 7), NIE using-superpowers:
  - (a) przypomnienie jawnego łańcucha pipeline'u: `@feature-discuss` → `@generate-tasks` → `@implement` → `@review`/`@triada-review`; skille wywołuje się jawnie przez `@`
  - (b) jeśli sesja w trakcie skilla (aktywna checklista/todo) — wróć do jego checklisty (kluczowe dla gałęzi `compact`)
  - (c) auto-trigger WYŁĄCZNIE dla skilli strażniczych: "przy debugowaniu → `debug`/`systematic-debugging`; przed twierdzeniem że coś działa → `verification-before-completion`"
- Utworzyć `hooks/session-start` (bash, wzorowany na obrze: `escape_for_json` + emisja `hookSpecificOutput.additionalContext` dla Claude) — czyta `hooks/session-context.md` i wstrzykuje jego treść
- Zachować output tylko dla Claude Code (Codex czyta AGENTS.md; usunąć gałęzie Cursor/Copilot jeśli obra je ma)

**Tests:**
- `hooks/session-context.md` istnieje, zawiera łańcuch pipeline'u + regułę skilli strażniczych, max ~15 linii merytorycznych
- `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start` emituje poprawny JSON (`| python3 -m json.tool` przechodzi)
- Wstrzyknięta treść pochodzi z `session-context.md` (nie zduplikowana inline)
- Treść NIE zawiera pełnego dispatchera using-superpowers

### Task 3: Zadeklarować hook w manifeście
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Dodać/potwierdzić w `.claude-plugin/plugin.json` wskaźnik na `hooks/hooks.json` (zgodnie ze schematem pluginów Claude Code)
- Codex: hooki nie są wspierane na poziomie pluginu (per CLAUDE.md agents limitation) — `.codex-plugin/plugin.json` NIE deklaruje hooka; odnotować w context

**Tests:**
- `.claude-plugin/plugin.json` poprawny JSON, referuje `hooks/hooks.json`
- `.codex-plugin/plugin.json` NIE referuje hooka

## Phase Verification
Run:
- `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null && echo "hook OK"`
- `python3 -m json.tool hooks/hooks.json >/dev/null && echo "hooks.json OK"`
- `grep -q 'startup|clear|compact' hooks/hooks.json && echo "matcher OK"`

## Completion Criteria
- All phase tasks are completed.
- Slim hook emituje poprawny JSON z własną chudą treścią.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- **`hooks/hooks.json`** copied verbatim from `vendor/superpowers/hooks/hooks.json` — matcher
  `startup|clear|compact` and command path `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd session-start`
  already matched our target layout 1:1, zero changes needed. `hooks-cursor.json` from upstream
  NOT vendored (Cursor is out of scope; Codex reads AGENTS.md, not this hook).
- **`hooks/run-hook.cmd`** copied verbatim (polyglot cmd.exe/bash dispatcher mechanism unchanged).
  Added one MIT attribution line as a `REM` comment inside the existing top comment block — safe
  because that block is (a) inert `REM` text on Windows and (b) absorbed into the bash heredoc
  (`: << 'CMDBLOCK' ... CMDBLOCK`) and discarded on Unix, so it cannot break either execution path.
  Verified with `bash hooks/run-hook.cmd session-start` piped through `python3 -m json.tool`.
  `chmod +x` applied (`test -x` passes).
- **`hooks/session-start`** keeps the vendored mechanism (`escape_for_json`, `printf` instead of
  heredoc to avoid the bash 5.3+ heredoc hang, `hookSpecificOutput.additionalContext` JSON shape)
  but drops the Cursor (`additional_context`) and Copilot/SDK-standard (top-level `additionalContext`)
  branches from upstream — only the Claude Code branch remains, since Codex reads `AGENTS.md`
  instead of this hook (per CLAUDE.md). Reads `hooks/session-context.md` instead of
  `skills/using-superpowers/SKILL.md`.
- **`hooks/session-context.md`** is entirely own content (not vendored) — 15 substantive lines:
  pipeline chain (`@feature-discuss` -> `@generate-tasks` -> `@implement` -> `@review`/`@triada-review`,
  explicit invocation only), return-to-checklist-after-compact rule, and auto-trigger restricted to
  the two guardian skills (`@debug`/vendored `systematic-debugging`, vendored
  `verification-before-completion`). This file is the shared source of truth the Phase 7 Pi
  extension will also read — do not duplicate its content inline in the Pi integration; read the
  file at runtime the same way `hooks/session-start` does.
- **`.claude-plugin/plugin.json`** now declares `"hooks": "./hooks/hooks.json"` explicitly (in
  addition to Claude Code's directory auto-discovery convention, which upstream `obra/superpowers`
  relies on without an explicit field) — added explicitly here to satisfy this phase's literal
  test wording ("referuje `hooks/hooks.json`") unambiguously. `.codex-plugin/plugin.json`
  intentionally has no `hooks` key (Codex has no plugin-level hook support).
- `VENDORED.md` updated with a new "Zvendorowany mechanizm hooka (Faza 5)" table section
  documenting source paths, pinned SHA `d884ae0`, and local modifications per file.
