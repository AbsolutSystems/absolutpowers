# Phase 2: Wire binding context into generate-tasks + implement (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-constitution/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- `claude/skills/constitution/SKILL.md` exists (Phase 1) — defines the `absolutpowers/constitution.md` output path this phase references as binding context.
- The exact `constitution.md` path string recorded in `implementation-context.md` (Phase 1 Provides).

### Provides (for later phases)
- `generate-tasks` (both trees) reads `absolutpowers/constitution.md` as binding context in its Step-1 "Also read" block.
- `implement` (both trees) lists `absolutpowers/constitution.md` among binding context files it reads before executing tasks.

## Read Scope
- `claude/skills/generate-tasks/SKILL.md` (insertion point: Step 1 "Also read (if they exist)" list, ~L94–97)
- `claude/skills/implement/SKILL.md` (insertion point: binding-context list, ~L43–49)
- `codex/skills/generate-tasks/SKILL.md`
- `codex/skills/implement/SKILL.md`

## Write Scope
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`
- `claude/skills/implement/SKILL.md`
- `codex/skills/implement/SKILL.md`

## Objective
Add `absolutpowers/constitution.md` as a binding context source in both pipeline skills, alongside the existing `patterns.md` / `rules.md` / ADR references. Edits are purely additive — one bullet + a one-line note on how to use it (pryncypia constrain the plan; cite the relevant Artykuł where it shapes a task). Do not restructure existing sections.

## Tasks

### Task 1: Add constitution to generate-tasks binding context (both trees)
**Status:** completed

**Modify:**
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

**Requirements:**
- In the Step-1 "Also read (if they exist)" list, add a bullet: `**`./absolutpowers/constitution.md`** — ratified project principles (pryncypia); treat as binding — tasks MUST NOT violate an article, and SHOULD cite the relevant Artykuł when it shapes a requirement.`
- Mirror the edit identically in both trees (no Claude-only drift introduced here).
- Keep wording consistent with the adjacent `patterns.md`/`rules.md`/ADR bullets.

**Tests:**
- Manual: `grep -n constitution.md claude/skills/generate-tasks/SKILL.md codex/skills/generate-tasks/SKILL.md` — present in both.
- Manual: `diff-skills.sh` for `generate-tasks` shows no NEW unexpected drift from this edit.

### Task 2: Add constitution to implement binding context (both trees)
**Status:** completed

**Modify:**
- `claude/skills/implement/SKILL.md`
- `codex/skills/implement/SKILL.md`

**Requirements:**
- In the binding-context list (where `patterns.md` and `rules.md` are read before implementing), add `./absolutpowers/constitution.md` with a one-line note: implementation MUST respect ratified pryncypia; if a task forces a violation, stop and surface it rather than silently breaking an article.
- Mirror identically in both trees.
- Do not touch the ADR / CLAUDE.md / orchestrator-worker sections.

**Tests:**
- Manual: `grep -n constitution.md claude/skills/implement/SKILL.md codex/skills/implement/SKILL.md` — present in both.
- Manual: `diff-skills.sh` for `implement` shows only pre-existing expected drift.

## Phase Verification
Run:
- `grep -rn "constitution.md" claude/skills/generate-tasks/ codex/skills/generate-tasks/ claude/skills/implement/ codex/skills/implement/` — 4 hits minimum.
- `./scripts/diff-skills.sh` — no new unexpected drift for `generate-tasks` / `implement`.

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Phase verification commands pass.
- `implementation-context.md` updated (note: generate-tasks + implement now bind constitution).
- All items in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Inserted constitution bullet after `./docs/adr/*.md` bullet in both `generate-tasks` "Also read" lists (line 98 claude, line 96 codex). Wording: "treat as binding — tasks MUST NOT violate an article, and SHOULD cite the relevant Artykuł when it shapes a requirement."
- Inserted constitution bullet after `./absolutpowers/project-memory.md` bullet in both `implement` "Context Files" lists (line 51 claude, line 49 codex). Wording: "implementation MUST respect these articles. If a task forces a violation, stop and surface it rather than silently breaking an article."
- Both pairs of edits are body-identical (verified via diff). Only pre-existing allowed frontmatter drift (`allowed-tools`, `argument-hint`) remains; no new unexpected drift introduced.
- `./scripts/diff-skills.sh` confirms `generate-tasks` and `implement` were already `~` before and remain `~` — no status change to drift summary.
