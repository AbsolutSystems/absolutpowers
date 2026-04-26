# AbsolutPowers Skills

Shared Claude Code and Codex workflow for AI-assisted development lifecycle — from feature design through implementation to code review.

## Installation

### Claude Code

```bash
/plugin marketplace add AbsolutSystems/absolutpowers
/plugin install absolutpowers@absolutpowers-skills
```

Restart Claude Code, then type `/absolutpowers:` — autocomplete should show all 6 skills.

### Codex

This repository exposes a repo-local Codex marketplace at:

```text
.agents/plugins/marketplace.json
```

and the installable Codex plugin bundle at:

```text
./plugins/absolutpowers
```

Open the repository in Codex, use the repo marketplace, and install the `absolutpowers` plugin from there.

In Codex, invoke the workflow through the plugin handle `$absolutpowers` plus the skill name or task context, for example:

```text
$absolutpowers feature-discuss zaprojektuj system powiadomien push
$absolutpowers generate-tasks ./absolutpowers/feature/planning-push-notifications.md
$absolutpowers implement ./absolutpowers/feature/tasks-push-notifications.md
$absolutpowers review
$absolutpowers debug test auth pada tylko na CI
$absolutpowers update-ai-context
```

The plugin bundle can also expose dedicated slash commands under:

```text
./plugins/absolutpowers/commands
```

Current custom command:

```text
/tech-lead-advisor
```

Use it for strategic technical guidance, architectural review, and critical second opinions on major technical decisions.

### Updating

```bash
/plugin install absolutpowers@absolutpowers-skills
```

For Codex, refresh or reinstall the local repo plugin after pulling changes if your environment caches plugin versions.

## Maintaining Dual Targets

Repository source of truth lives in:

```text
./skills
```

The Codex plugin bundle mirrors those files in:

```text
./plugins/absolutpowers/skills
```

Before publishing or testing the Codex plugin bundle, refresh that mirror with:

```bash
python3 scripts/sync_skills_to_codex.py
```

The sync keeps all supporting files identical and removes Claude-specific frontmatter fields
(`allowed-tools`, `argument-hint`) from plugin `SKILL.md` files.

## Skills

### Development Pipeline

Each skill produces output consumed by the next:

```
feature-discuss → generate-tasks → implement → review
     (CO?)           (JAK?)      (BUDUJ+WERYFIKUJ)  (AUDYTUJ)
```

#### `/absolutpowers:feature-discuss`

Interactive Product Owner / Product Architect session. Discusses feature requirements before any code is written.

```
/absolutpowers:feature-discuss chce system powiadomien push dla uzytkownikow
```

- Asks clarifying questions to understand the need
- Analyzes existing codebase for relevant patterns and components
- Proposes 2-3 alternative approaches with tradeoffs
- Iterates on scope, edge cases, dependencies

**Output:** `./absolutpowers/feature/planning-{slug}.md`, optionally `./docs/adr/YYYY-MM-DD-{slug}.md`

**Smart routing:** Trivial changes skip planning doc — suggests direct implementation.

---

#### `/absolutpowers:generate-tasks`

Creates a step-by-step implementation plan from a planning document or review report.

```
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md
/absolutpowers:generate-tasks @absolutpowers/reviews/2026-04-21-feature-auth.md
```

- Reads planning doc or review report, `./absolutpowers/patterns.md`, `./absolutpowers/rules.md`, ADRs
- Analyzes codebase architecture, patterns, conventions
- Produces sequential tasks with exact file paths, method signatures, test cases
- Adds a final verification task with project-specific build / typecheck / formatter commands

**Output:** `./absolutpowers/feature/tasks-{slug}.md`

---

#### `/absolutpowers:implement`

Executes tasks sequentially from a tasks document with TDD approach.

```
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md
```

- Picks first pending task, implements with TDD (tests first)
- Updates task status to `completed` in-place
- Executes the final verification task before reporting overall completion
- Creates ADR for significant implementation decisions
- Reads `./absolutpowers/project-memory.md` on startup when present
- Can create `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md` for durable lessons worth reusing later

**Output:** Implementation code + tests, updated tasks file

---

#### `/absolutpowers:review`

Full 4-phase code review of current branch changes.

```
/absolutpowers:review
/absolutpowers:review develop    # custom base branch
```

| Phase | Focus |
|-------|-------|
| 1. Semantic Review | Behavior changes, blast radius, architectural decisions |
| 2. Edge Case Hunt | null, empty, off-by-one, race conditions |
| 3. Rules Check | Compliance with `./absolutpowers/rules.md` |
| 4. Garbage Collection | Dead imports, debug logs, commented code |

Review also checks whether there is evidence of final verification for executable code changes
(for example backend build, frontend build, typecheck, `spotlessCheck`).
It also reads `./absolutpowers/project-memory.md` on startup and can create memory candidates
for recurring traps or workarounds discovered during review.

**Output:** `./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md`

**Smart follow-up:** 0-2 problems → manual fix. 3+ problems → suggests `/absolutpowers:generate-tasks` on the review report.

---

### Supporting Skills

#### `/absolutpowers:debug`

Systematic debugging — root cause investigation before any fixes.

```
/absolutpowers:debug testy w module auth padaja na CI ale przechodza lokalnie
```

4 phases: Root Cause → Pattern Analysis → Hypothesis → Implementation.

Escalates to architecture review if 3+ fixes fail. Includes supporting techniques for root-cause tracing, defense-in-depth validation, and condition-based waiting.
Reads `./absolutpowers/project-memory.md` on startup when present and can emit memory candidates
after non-trivial investigations that uncovered future-useful traps or workarounds.

---

#### `/absolutpowers:update-ai-context`

Bootstraps or refreshes AI documentation for the project.

```
/absolutpowers:update-ai-context
```

- **No CLAUDE.md** → Bootstrap: creates full documentation from scratch
- **CLAUDE.md exists** → Update: audits for drift, discovers new patterns

Manages: `CLAUDE.md`, mirrored `AGENTS.md`, `./absolutpowers/patterns.md`, `./absolutpowers/rules.md`

## Shared AI Context

The project context workflow is shared across Claude Code and Codex:

- `CLAUDE.md` files are the editable source of truth
- `AGENTS.md` files are generated mirrors for Codex with the same directory scope
- `./absolutpowers/patterns.md` and `./absolutpowers/rules.md` are shared by both agents
- `./absolutpowers/project-memory.md` is optional operational memory for future coding work
- `./absolutpowers/memory-candidates/` is the approval queue for proposed durable memory entries

When `update-ai-context` runs, it should update the hierarchical `CLAUDE.md` files first and then refresh sibling `AGENTS.md` mirrors.

Helper script included in both plugin targets:

```bash
python3 scripts/sync_claude_to_agents.py /path/to/project
```

## File Conventions

All artifacts live under `./absolutpowers/` in the project root:

```
project/
├── absolutpowers/
│   ├── feature/
│   │   ├── planning-{slug}.md
│   │   └── tasks-{slug}.md
│   ├── memory-candidates/
│   │   └── memory-candidates-YYYY-MM-DD-{slug}.md
│   ├── project-memory.md
│   ├── reviews/
│   │   └── YYYY-MM-DD-{branch-slug}.md
│   ├── patterns.md
│   └── rules.md
├── docs/adr/
│   └── YYYY-MM-DD-{slug}.md
├── CLAUDE.md
└── AGENTS.md
```

## Project Memory

`project-memory.md` is for durable implementation knowledge that should help future agents and developers avoid repeating the same mistakes.

Use it for:
- recurring traps
- non-obvious workarounds
- failure patterns with clear warning signs
- lessons that are likely to matter again in future tasks

Do not use it for:
- one-off ticket context
- temporary debugging notes
- branch-specific status
- facts that belong in `patterns.md`, `rules.md`, or ADRs instead

Workflow:
- `implement`, `debug`, and `review` read `./absolutpowers/project-memory.md` on startup if it exists
- if a session uncovers a durable lesson, the agent may create `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md`
- the agent should ask the developer whether to promote that candidate into `project-memory.md`
- promotion requires explicit developer approval
- on promotion, update an existing matching memory entry instead of duplicating it
- after successful promotion, delete the candidate file

Recommended `project-memory.md` structure:

```markdown
# Project Memory

## src/auth

### Token refresh race in session bootstrap
- Problem: concurrent refresh paths invalidate each other
- Symptoms: flaky 401 on first page load, duplicate refresh requests
- Root cause: bootstrap and interceptor both refresh from stale state
- Resolution: gate refresh through a shared in-flight promise
- Warning signs:
  - intermittent auth failures only on cold start
  - duplicate refresh logs within one request cycle
- Affected paths:
  - `src/auth/bootstrap.ts`
  - `src/auth/refresh-token.ts`
```

Recommended candidate structure:

```markdown
# Memory Candidate: Token refresh race in session bootstrap

## Status
Candidate — YYYY-MM-DD

## Source
- Skill: implement | debug | review
- Context: task / bug / branch being worked on

## Module
`src/auth`

## Problem
...

## Symptoms
...

## Root Cause
...

## Resolution
...

## Warning Signs
- ...

## Affected Paths
- `src/auth/bootstrap.ts`
- `src/auth/refresh-token.ts`

## Why This May Matter Again
...
```

## Typical Workflows

### New Feature

```bash
/absolutpowers:feature-discuss "system powiadomien push"
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md
/absolutpowers:review
```

The generated tasks file should end with a final verification step, for example:
- backend compilation/build
- frontend production build
- typecheck
- formatter check such as `spotlessCheck`

`generate-tasks` should emit this as a normal last task in the same task format, not as a loose reminder.

### Bug Fix

```bash
/absolutpowers:debug "endpoint /api/users zwraca 500 przy pustym query param"
```

### Project Setup

```bash
/absolutpowers:update-ai-context
```

## Repo Structure

```
absolutpowers/
├── .agents/
│   └── plugins/
│       └── marketplace.json    # Repo-local Codex marketplace
├── .claude-plugin/
│   ├── marketplace.json    # Marketplace manifest
│   └── plugin.json         # Plugin manifest (name = "absolutpowers")
├── plugins/
│   └── absolutpowers/
│       ├── commands/
│       │   └── tech-lead-advisor.md
│       ├── .codex-plugin/
│       │   └── plugin.json     # Codex plugin manifest
│       ├── skills/
│       │   └── ...             # Codex skill set
│       └── scripts/
│           └── sync_claude_to_agents.py
├── scripts/
│   ├── sync_claude_to_agents.py
│   └── sync_skills_to_codex.py
├── skills/
│   ├── debug/
│   │   ├── SKILL.md
│   │   └── *.md            # Supporting techniques
│   ├── feature-discuss/
│   │   └── SKILL.md
│   ├── generate-tasks/
│   │   └── SKILL.md
│   ├── implement/
│   │   └── SKILL.md
│   ├── review/
│   │   └── SKILL.md
│   └── update-ai-context/
│       └── SKILL.md
└── README.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension

## License

MIT — Absolut Systems
