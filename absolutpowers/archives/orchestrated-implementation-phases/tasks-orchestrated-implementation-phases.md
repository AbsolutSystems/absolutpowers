# Tasks: Orchestrated Implementation Phases

## Project Context

**Source doc:** `./absolutpowers/feature/planning-orchestrated-implementation-phases.md`

**Stack:** Markdown-based Claude Code and Codex plugin definitions.

**Structure:**
- `claude/skills/` - Claude skill prompts with `allowed-tools`, agent gate instructions, and argument hints.
- `claude/agents/` - Claude subagent prompt definitions.
- `codex/skills/` - Codex skill prompts without plugin-level agent gates.
- `docs/` - user and contributor documentation.
- `README.md` - primary plugin documentation.

**Patterns:**
- Claude skills include frontmatter fields `name`, `description`, `allowed-tools`, and `argument-hint`.
- Codex skills keep compatible behavior but avoid Claude-only agent promises.
- Review gates are implemented as Claude agents under `claude/agents/`.
- Drift between Claude and Codex skills is checked with `./scripts/diff-skills.sh`.

**Conventions:**
- Skill files are named `SKILL.md`.
- Agent files use kebab-case names under `claude/agents/`.
- Documentation is Markdown and should stay concise and operational.

**Verification commands:**
- Drift summary: `./scripts/diff-skills.sh`
- Drift detail: `./scripts/diff-skills.sh --diff`

**Reference implementations:**
- `claude/skills/generate-tasks/SKILL.md` - existing task generation flow and review gate.
- `claude/skills/implement/SKILL.md` - existing implementation flow and final review gate.
- `claude/agents/review-implementation.md` - existing gate output contract.
- `claude/agents/review-tasks.md` - existing task review criteria.

## Implementation Tasks

### Task 1: Extend task generation format
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/generate-tasks/SKILL.md`
- `codex/skills/generate-tasks/SKILL.md`

**Description:**
Teach `generate-tasks` to choose between legacy single-file task lists and orchestrated phase-based task plans. Claude and Codex should share the same file format, but Codex must not promise subagent execution.

**Requirements:**
- Add mode selection between `single-file` and `orchestrated`.
- Keep legacy output valid for small changes.
- For orchestrated mode, require a main `tasks-{slug}.md`, a sibling `tasks-{slug}/` directory, phase files, `implementation-context.md`, and `99-final-verification.md`.
- Specify phase constraints: 1-3 related tasks, read scope, write scope, phase verification, completion criteria.
- Define `implementation-context.md` as a concise handoff contract, not a log.
- Update Claude review gate instructions so `review-tasks` reviews the main tasks file plus referenced phase files.
- In Codex, describe the same format as sequential phase guidance without Claude subagents.

**Tests:**
- Manual inspection confirms both skills contain orchestrated mode and legacy mode.
- `./scripts/diff-skills.sh` reports expected Claude/Codex drift only.

**Implementation decisions / remarks:**
- Added `single-file` and `orchestrated` output modes to Claude and Codex `generate-tasks`. Claude can generate phase plans for worker subagents; Codex gets the same phase file structure as sequential guidance without subagent promises.

### Task 2: Add Claude phase agents
**Status:** completed

**Create:**
- `claude/agents/implementation-worker.md`
- `claude/agents/phase-review.md`

**Modify:**
- None

**Description:**
Add the Claude-only agents required for orchestrated execution. `implementation-worker` performs one phase; `phase-review` validates that one phase before the orchestrator advances.

**Requirements:**
- `implementation-worker` must implement only one phase file.
- It must read the parent main tasks file, phase file, `implementation-context.md`, and relevant project context.
- It must respect write scope and report any justified scope expansion.
- It must update task statuses only inside the phase file.
- It must update `implementation-context.md` with concise handoff facts.
- It must not update the parent phase status.
- `phase-review` must be read-only and return exactly `VERDICT: PASS` or `VERDICT: REJECTED`.
- `phase-review` must check scope, completeness, tests, handoff quality, obvious correctness issues, garbage, and rules.

**Tests:**
- Manual inspection confirms agent frontmatter includes appropriate tools.
- Agent output contracts are exact and machine-readable.

**Implementation decisions / remarks:**
- Added `implementation-worker` for one-phase execution and `phase-review` as a lightweight read-only gate before the orchestrator advances.

### Task 3: Convert Claude implement into orchestrator with legacy fallback
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/implement/SKILL.md`
- `codex/skills/implement/SKILL.md`
- `claude/agents/review-tasks.md`
- `claude/agents/review-implementation.md`

**Description:**
Update `implement` so Claude can orchestrate phase workers while preserving legacy behavior. Codex should support the phase file structure as sequential execution guidance without spawning plugin-level agents.

**Requirements:**
- Detect `## Mode` value in the main tasks file.
- For missing or `single-file` mode, keep existing behavior.
- For `orchestrated`, Claude must:
  - find the first pending phase in `## Phase Overview`,
  - spawn `implementation-worker` for the phase file,
  - inspect the worker result,
  - spawn `phase-review`,
  - repeat fix/review up to 3 iterations,
  - mark the parent phase completed only after PASS,
  - continue until final verification,
  - run final `review-implementation` after all phases and final verification pass.
- Codex must execute phase files sequentially in the same session, update phase file plus parent status, and keep `implementation-context.md` concise.
- Preserve project memory and CLAUDE/AGENTS update guidance where relevant.

**Tests:**
- Manual inspection confirms Claude has explicit Agent calls for `implementation-worker`, `phase-review`, and final `review-implementation`.
- Manual inspection confirms Codex does not mention spawning Claude subagents.

**Implementation decisions / remarks:**
- Claude `implement` now detects mode and delegates orchestrated phases to `implementation-worker`, then gates with `phase-review`. Codex now executes phase files sequentially in one session. Existing review agents were updated to read phase files and `implementation-context.md`.

### Task 4: Update documentation and verify drift
**Status:** completed

**Create:**
- None

**Modify:**
- `README.md`
- `docs/getting-started.md`
- `docs/review-gates.md`
- `docs/contributing.md`
- `absolutpowers/feature/tasks-orchestrated-implementation-phases.md`

**Description:**
Document the new orchestrated workflow and verify expected Claude/Codex differences. Update this task file with completed statuses and verification notes after checks run.

**Requirements:**
- README describes orchestrated task plans, phase workers, phase review, and final review.
- Getting Started explains what users see when larger features generate phase files.
- Review Gates documents `phase-review` and its relationship to final `review-implementation`.
- Contributing documents the new agents and expected drift.
- Run `./scripts/diff-skills.sh`.
- Run `./scripts/diff-skills.sh --diff` if needed to inspect expected differences.
- Record verification results in this tasks file.

**Tests:**
- `./scripts/diff-skills.sh` completes successfully.
- Documentation mentions Claude-only agents and Codex fallback accurately.

**Implementation decisions / remarks:**
- README, Getting Started, Review Gates, and Contributing now describe orchestrated task plans, Claude-only phase agents, Codex fallback, and expected drift.

### Task 5: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- `absolutpowers/feature/tasks-orchestrated-implementation-phases.md`

**Description:**
Run final repository checks for this Markdown/plugin prompt change and record results.

**Requirements:**
- Run drift summary: `./scripts/diff-skills.sh`
- Run repository status: `git status --short`
- Review changed files list.
- Do not mark this task completed if drift script fails.

**Tests:**
- Drift script exits with code 0.
- Changed files match the planned scope.

**Implementation decisions / remarks:**
- Commands executed:
  - `./scripts/diff-skills.sh` -> pass
  - `git diff --check` -> pass
  - `git status --short` -> pass
  - `git diff --name-only && git ls-files --others --exclude-standard` -> pass
- Results: drift summary remains `10 identical, 6 differ, 0 claude-only, 1 codex-only`; expected workflow skill drift remains, and new Claude agents are untracked additions.
- Changed files match planned scope: Claude/Codex generate and implement skills, Claude review agents, new Claude phase agents, README/docs, and AbsolutPowers planning/tasks audit docs.
