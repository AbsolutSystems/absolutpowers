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

In Codex, invoke the workflow through the plugin handle `&absolutpowers` plus the skill name or task context, for example:

```text
&absolutpowers feature-discuss zaprojektuj system powiadomien push
&absolutpowers generate-tasks ./absolutpowers/feature/planning-push-notifications.md
&absolutpowers implement ./absolutpowers/feature/tasks-push-notifications.md
&absolutpowers review
&absolutpowers debug test auth pada tylko na CI
&absolutpowers update-ai-context
```

### Updating

```bash
/plugin install absolutpowers@absolutpowers-skills
```

For Codex, refresh or reinstall the local repo plugin after pulling changes if your environment caches plugin versions.

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
│   ├── reviews/
│   │   └── YYYY-MM-DD-{branch-slug}.md
│   ├── patterns.md
│   └── rules.md
├── docs/adr/
│   └── YYYY-MM-DD-{slug}.md
├── CLAUDE.md
└── AGENTS.md
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
│       ├── .codex-plugin/
│       │   └── plugin.json     # Codex plugin manifest
│       ├── skills/
│       │   └── ...             # Codex skill set
│       └── scripts/
│           └── sync_claude_to_agents.py
├── scripts/
│   └── sync_claude_to_agents.py
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
