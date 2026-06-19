# Tasks: analyze — cross-artifact consistency audit (planning ↔ tasks ↔ kod)

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/planning-cross-artifact-analyze.md`
- Epic context (if applicable): none

## Mode
orchestrated

## Project Context
**Stack:** Markdown skill/agent prompts (Claude Code + Codex plugins). No compiled code. Two parallel trees `claude/` and `codex/` share skill logic; Claude adds frontmatter (`allowed-tools`, `argument-hint`), agents, and commands.
**Verification commands:**
- Drift between trees: `./scripts/diff-skills.sh` (and `--diff` for full diff)
- JSON manifests valid + versions match: `python3 -m json.tool claude/.claude-plugin/plugin.json` and `python3 -m json.tool codex/.codex-plugin/plugin.json`
- Targeted grep checks (see `99-final-verification.md`)

**Shared implementation context:** `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`

> No `## Acceptance Criteria` section in the planning doc → AC traceability is skipped for this plan (no `**Traces to:**` fields).

## Phase Overview

### Phase 1: Ruch 1 — Intent Fidelity gate + feature-discuss source nudge
**Status:** completed
**File:** `./absolutpowers/feature/tasks-cross-artifact-analyze/01-intent-fidelity-gate.md`
**Depends on:** none
**Write scope:** `claude/agents/review-tasks.md`, `claude/skills/feature-discuss/SKILL.md`, `codex/skills/feature-discuss/SKILL.md`
**Risk:** low

### Phase 2: Ruch 2 — new `analyze` skill (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-cross-artifact-analyze/02-analyze-skill.md`
**Depends on:** none
**Write scope:** `claude/skills/analyze/SKILL.md`, `codex/skills/analyze/SKILL.md`
**Risk:** medium

### Phase 3: Wiring notes — `review` and `generate-tasks` (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-cross-artifact-analyze/03-wiring-notes.md`
**Depends on:** Phase 2
**Write scope:** `claude/skills/review/SKILL.md`, `codex/skills/review/SKILL.md`, `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
**Risk:** low

### Phase 4: Docs + version sanity — README, CLAUDE.md, manifests
**Status:** completed
**File:** `./absolutpowers/feature/tasks-cross-artifact-analyze/04-docs-and-version.md`
**Depends on:** Phase 1, Phase 2, Phase 3
**Write scope:** `README.md`, `CLAUDE.md`, `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/tasks-cross-artifact-analyze/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file.
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
- Phase 1 and Phase 2 are independent and may run in either order. Phase 3 depends on the `analyze` skill name/behavior settled in Phase 2. Phase 4 documents everything and must run last.
