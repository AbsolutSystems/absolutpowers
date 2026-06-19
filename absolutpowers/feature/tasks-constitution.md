# Tasks: Constitution — pryncypia projektu jako pierwszorzędna ceremonia

## Status
completed

## Source
- Planning doc: `./absolutpowers/feature/planning-constitution.md`

## Mode
orchestrated

## Project Context
**Stack:** Markdown prompt-engineering plugin (Claude Code + Codex). No build system, no package.json. Two parallel skill trees: `claude/skills/{name}/SKILL.md` and `codex/skills/{name}/SKILL.md` sharing most logic with expected Claude-only drift (`allowed-tools`, `argument-hint` frontmatter).

**Verification commands:**
- Drift check between trees: `./scripts/diff-skills.sh` (summary) / `./scripts/diff-skills.sh --diff` (full)
- Manifest version match: `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json`

**Shared implementation context:** `./absolutpowers/feature/tasks-constitution/implementation-context.md`

**Key decisions baked from planning doc:**
- Two files: `constitution.md` (pryncypia/osąd) ≠ `rules.md` (mechanika/lint). Never merge.
- Versioning: semver + ratyfikacja date + changelog (decyzja #2 → semver).
- Review enforcement: **extend** review Faza 3 with a "Pryncypia (constitution)" sub-section (decyzja #3 → rozszerzyć, nie nowa faza).
- Version bump: one bundled `3.8.0 → 3.9.0` across both manifests (decyzja #4).
- Constitution NIE blokuje builda — review *raportuje* naruszenia (out of scope: hard gate).
- feature-discuss reads constitution as lightweight context (open question → tak).

## Phase Overview

### Phase 1: Author the `constitution` skill (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/01-author-constitution-skill.md`
**Depends on:** none
**Write scope:** `claude/skills/constitution/SKILL.md`, `codex/skills/constitution/SKILL.md`
**Risk:** medium

### Phase 2: Wire binding context into generate-tasks + implement (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/02-wire-generate-tasks-implement.md`
**Depends on:** Phase 1
**Write scope:** `claude/skills/generate-tasks/SKILL.md`, `codex/skills/generate-tasks/SKILL.md`, `claude/skills/implement/SKILL.md`, `codex/skills/implement/SKILL.md`
**Risk:** medium

### Phase 3: Wire review enforcement + update-ai-context demarcation (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/03-wire-review-update-ai-context.md`
**Depends on:** Phase 1
**Write scope:** `claude/skills/review/SKILL.md`, `codex/skills/review/SKILL.md`, `claude/skills/update-ai-context/SKILL.md`, `codex/skills/update-ai-context/SKILL.md`
**Risk:** medium

### Phase 4: Wire lightweight context into feature-discuss (both trees)
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/04-wire-feature-discuss.md`
**Depends on:** Phase 1
**Write scope:** `claude/skills/feature-discuss/SKILL.md`, `codex/skills/feature-discuss/SKILL.md`
**Risk:** low

### Phase 5: Docs + version bump
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/05-docs-and-version-bump.md`
**Depends on:** Phase 1, Phase 2, Phase 3, Phase 4
**Write scope:** `README.md`, `CLAUDE.md`, `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`
**Risk:** low

## Final Verification
**Status:** completed
**File:** `./absolutpowers/feature/tasks-constitution/99-final-verification.md`

## Orchestrator Notes
- Orchestrator updates statuses in this file.
- Workers update only their phase file and `implementation-context.md`.
- Do not mark a phase completed until phase verification and `phase-review` pass.
- Each phase file contains a Context Contract. Workers validate Requires before starting; `phase-review` checks Provides on completion.
- Phases 2, 3, 4 all depend only on Phase 1 and have disjoint write scopes — they may run in any order after Phase 1.
- Cross-tree sync is the core risk: every claude/ edit MUST have a mirrored codex/ edit with only expected frontmatter drift. `diff-skills.sh` is the gate.
