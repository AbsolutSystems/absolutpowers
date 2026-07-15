# Tasks: QA Enrichment — Acceptance Criteria w pipeline

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/planning-qa-enrichment.md`

## Mode
orchestrated

## Project Context
**Stack:** Markdown prompt files (SKILL.md, agent .md), Bash scripts, Python sync script
**Verification commands:** `./scripts/diff-skills.sh --diff` (drift detection between Claude and Codex skills)
**Shared implementation context:** `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

**Structure:**
- `claude/skills/{name}/SKILL.md` — Claude Code skill prompts (with `allowed-tools`, `argument-hint` frontmatter)
- `codex/skills/{name}/SKILL.md` — Codex skill prompts (no `allowed-tools`, no `argument-hint`, no agent references)
- `claude/agents/{name}.md` — Claude Code subagent definitions (with `model`, `tools` frontmatter)
- `docs/` — user-facing documentation
- `README.md` — main project readme

**Patterns:**
- Skill frontmatter: Claude has `allowed-tools` and `argument-hint`; Codex omits both
- Agent frontmatter: `name`, `description`, `model` (optional), `tools` (optional list)
- Review agents return `VERDICT: PASS` or `VERDICT: REJECTED` with categorized issues
- Skills spawn agents via `Agent(subagent_type="agent-name", prompt="...")`
- Planning doc template defined in feature-discuss SKILL.md lines 147–196
- Task template defined in generate-tasks SKILL.md lines 173–206
- Review criteria categories listed in agent files and referenced in `docs/review-gates.md`

**Conventions:**
- Files: kebab-case for skill/agent names
- Agent categories: UPPERCASE (e.g., `COMPLETENESS`, `FEASIBILITY`, `AC_QUALITY`)
- Pipeline flow: upstream skills reference downstream agents by `subagent_type` name
- Claude/Codex parity: shared logic identical, Claude adds agent gates + `allowed-tools` + `argument-hint`

**Reference implementations:**
- `claude/agents/review-plan.md` — pattern for review criteria structure (4 numbered sections + categories + rules)
- `claude/agents/review-tasks.md` — pattern for traceability checks
- `claude/agents/review-implementation.md` — pattern for code verification criteria
- `claude/skills/feature-discuss/SKILL.md` — pattern for phased skill with agent spawning (Faza 5→6→7)
- `codex/skills/feature-discuss/SKILL.md` — pattern for Codex skill without agents (Faza 5→6)

## Phase Overview

### Phase 1: Create QA Enrichment Agent and Update Feature-Discuss
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/01-qa-agent-and-feature-discuss.md`
**Depends on:** none
**Write scope:** `claude/agents/qa-enrichment.md`, `claude/skills/feature-discuss/SKILL.md`, `codex/skills/feature-discuss/SKILL.md`
**Risk:** medium

### Phase 2: Extend Review-Plan with AC Quality Criterion
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/02-review-plan-ac-quality.md`
**Depends on:** Phase 1
**Write scope:** `claude/agents/review-plan.md`
**Risk:** low

### Phase 3: Add AC Traceability to Generate-Tasks
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/03-generate-tasks-traceability.md`
**Depends on:** Phase 1
**Write scope:** `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`
**Risk:** medium

### Phase 4: Add AC Coverage to Review-Tasks
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/04-review-tasks-ac-coverage.md`
**Depends on:** Phase 3
**Write scope:** `claude/agents/review-tasks.md`
**Risk:** low

### Phase 5: Add AC Awareness to Implement
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/05-implement-ac-awareness.md`
**Depends on:** Phase 3
**Write scope:** `claude/skills/implement/SKILL.md`, `codex/skills/implement/SKILL.md`
**Risk:** low

### Phase 6: Add AC Fulfillment to Review-Implementation
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/06-review-implementation-ac-fulfillment.md`
**Depends on:** Phase 5
**Write scope:** `claude/agents/review-implementation.md`
**Risk:** low

### Phase 7: Update Documentation
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/07-documentation.md`
**Depends on:** Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6
**Write scope:** `README.md`, `docs/getting-started.md`, `docs/review-gates.md`, `docs/contributing.md`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/tasks-qa-enrichment/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file.
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
- Phase 2 and Phase 3 can run in parallel (both depend only on Phase 1).
- Phase 4 and Phase 5 can run in parallel (both depend on Phase 3).
