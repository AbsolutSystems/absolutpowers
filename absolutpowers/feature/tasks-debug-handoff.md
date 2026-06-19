# Tasks: debug-handoff — domknięcie artefaktów na wejściu i wyjściu drzewa debug

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/planning-debug-handoff.md`

## Mode
orchestrated

## Project Context
**Stack:** Markdown skill-prompt files for an AbsolutPowers Claude Code + Codex plugin. No compiled code. Two parallel trees (`claude/`, `codex/`) share skill logic; expected drift = `allowed-tools`/`argument-hint` frontmatter + Claude-only agent gate sections.
**Verification commands:**
- Drift check: `./scripts/diff-skills.sh` (summary), `./scripts/diff-skills.sh --diff` (full)
- Version match: `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json`
**Shared implementation context:** `./absolutpowers/feature/tasks-debug-handoff/implementation-context.md`

## Phase Overview

### Phase 1: generate-tasks recognizes `planning-fix-` input
**Status:** completed
**File:** `./absolutpowers/feature/tasks-debug-handoff/01-generate-tasks-input.md`
**Depends on:** none
**Write scope:** `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
**Risk:** low

### Phase 2: debug emits/consumes handoff artefacts
**Status:** completed
**File:** `./absolutpowers/feature/tasks-debug-handoff/02-debug-handoff.md`
**Depends on:** Phase 1
**Write scope:** `claude/skills/debug/SKILL.md`, `codex/skills/debug/SKILL.md`
**Risk:** medium

### Phase 3: problem-discuss Faza 5 nudge points to file
**Status:** completed
**File:** `./absolutpowers/feature/tasks-debug-handoff/03-problem-discuss-nudge.md`
**Depends on:** Phase 2
**Write scope:** `claude/skills/problem-discuss/SKILL.md`, `codex/skills/problem-discuss/SKILL.md`
**Risk:** low

### Phase 4: docs + version consistency
**Status:** completed
**File:** `./absolutpowers/feature/tasks-debug-handoff/04-docs-version.md`
**Depends on:** Phase 1, Phase 2, Phase 3
**Write scope:** `README.md`, `CLAUDE.md`, `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/tasks-debug-handoff/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file.
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
- Cross-platform rule (binding): every behavioral change to a skill MUST land in BOTH `claude/` and `codex/` copies in the same phase. Only expected drift (`allowed-tools`, `argument-hint`, Agent in `allowed-tools`) may differ.
