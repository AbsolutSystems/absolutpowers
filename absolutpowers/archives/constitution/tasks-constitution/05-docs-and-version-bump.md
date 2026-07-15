# Phase 5: Docs + version bump

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-constitution/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Phase 1: `constitution` skill exists in both trees.
- Phase 2: generate-tasks + implement bind constitution.
- Phase 3: review enforces, update-ai-context demarcates.
- Phase 4: feature-discuss reads constitution (lightweight).
  (All wiring must be in place before documenting it as shipped and bumping the version.)

### Provides (for later phases)
- `README.md` + `CLAUDE.md` document the `constitution` skill and its pipeline wiring.
- Both manifests at version `3.9.0` (matching).

## Read Scope
- `README.md` (skill catalogue + pipeline architecture sections)
- `CLAUDE.md` (project root — "Pipeline Architecture" / skill list sections)
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

## Write Scope
- `README.md`
- `CLAUDE.md`
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

## Objective
Document the new skill and its wiring in `README.md` and root `CLAUDE.md`, then bump both manifests `3.8.0 → 3.9.0` (single bundled minor — decyzja #4). Keep both manifests in lockstep.

## Tasks

### Task 1: Document constitution in README.md + CLAUDE.md
**Status:** completed

**Modify:**
- `README.md`
- `CLAUDE.md`

**Requirements:**
- README: add `constitution` to the skill catalogue with a one-line purpose; note it produces `absolutpowers/constitution.md` (ratified pryncypia, semver+changelog) and is read as binding context by generate-tasks/implement, enforced (reported) by review Faza 3, and read lightweight by feature-discuss.
- README: state the two-file distinction explicitly — `constitution.md` (pryncypia/osąd, ratified) ≠ `rules.md` (mechanical/lint, code-derived).
- CLAUDE.md (root): in "Pipeline Architecture" / skill description area, add the constitution skill and its binding-context wiring; note `constitution.md` is a project-root artifact created by the skill, distinct from `rules.md`.
- Keep edits factual and consistent with how other skills (e.g. `update-ai-context`, `problem-discuss`) are described.

**Tests:**
- Manual: `grep -n constitution README.md CLAUDE.md` — present in both; two-file distinction stated.

### Task 2: Bump both manifests to 3.9.0
**Status:** completed

**Modify:**
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

**Requirements:**
- Set `"version": "3.9.0"` in both files (was `3.8.0`).
- Change nothing else in the manifests.
- Versions MUST match across both manifests (SemVer lockstep rule).

**Tests:**
- Manual: `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json` — both `3.9.0`.

## Phase Verification
Run:
- `grep -n constitution README.md CLAUDE.md` — documented in both.
- `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json` — both report `3.9.0`.

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Phase verification commands pass.
- `implementation-context.md` updated (docs + version shipped).
- All items in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- README.md: added full `/absolutpowers:constitution` skill entry with a two-file distinction table (`constitution.md` pryncypia/osąd vs `rules.md` mechanika/lint) and pipeline wiring summary. Updated Project Structure to include `constitution.md` and `problem/` dir. Updated Platform Differences skill count 12 → 13. Added 3.9.0 changelog entry.
- CLAUDE.md: bumped version in "What This Is" to 3.9.0. Added "Constitution Skill" subsection to Pipeline Architecture with two-file distinction and wiring details. No restructuring of existing sections.
- Both manifests: `"version": "3.8.0"` → `"3.9.0"`. No other changes.
- Two-file distinction phrasing kept consistent with the demarcation sentence from implementation-context.md: `constitution.md` = pryncypia/osąd; `rules.md` = mechanika/lint.
