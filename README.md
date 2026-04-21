# Absolut AI Skills

Claude Code plugin for AI-assisted development lifecycle — from feature design through implementation to code review.

## Installation

### 1. Add marketplace

```bash
/plugin marketplace add absolut-systems/absolut-ai-skills
```

### 2. Install plugin

```bash
/plugin install absolut-ai@absolut-ai-skills
```

### 3. Verify

Restart Claude Code, then type `/absolut-ai:` — autocomplete should show all 6 skills.

### Updating

```bash
/plugin install absolut-ai@absolut-ai-skills
```

## Skills

### Development Pipeline

Each skill produces output consumed by the next:

```
feature-discuss → generate-tasks → implement → review
     (CO?)           (JAK?)         (BUDUJ)    (SPRAWDZ)
```

#### `/absolut-ai:feature-discuss`

Interactive Product Owner / Product Architect session. Discusses feature requirements before any code is written.

```
/absolut-ai:feature-discuss chce system powiadomien push dla uzytkownikow
```

- Asks clarifying questions to understand the need
- Analyzes existing codebase for relevant patterns and components
- Proposes 2-3 alternative approaches with tradeoffs
- Iterates on scope, edge cases, dependencies

**Output:** `./absolut-ai/feature/planning-{slug}.md`, optionally `./docs/adr/YYYY-MM-DD-{slug}.md`

**Smart routing:** Trivial changes skip planning doc — suggests direct implementation.

---

#### `/absolut-ai:generate-tasks`

Creates a step-by-step implementation plan from a planning document or review report.

```
/absolut-ai:generate-tasks @absolut-ai/feature/planning-push-notifications.md
/absolut-ai:generate-tasks @absolut-ai/reviews/2026-04-21-feature-auth.md
```

- Reads planning doc, `./absolut-ai/patterns.md`, `./absolut-ai/rules.md`, ADRs
- Analyzes codebase architecture, patterns, conventions
- Produces sequential tasks with exact file paths, method signatures, test cases

**Output:** `./absolut-ai/feature/tasks-{slug}.md`

---

#### `/absolut-ai:implement`

Executes tasks sequentially from a tasks document with TDD approach.

```
/absolut-ai:implement @absolut-ai/feature/tasks-push-notifications.md
```

- Picks first pending task, implements with TDD (tests first)
- Updates task status to `completed` in-place
- Creates ADR for significant implementation decisions

**Output:** Implementation code + tests, updated tasks file

---

#### `/absolut-ai:review`

Full 4-phase code review of current branch changes.

```
/absolut-ai:review
/absolut-ai:review develop    # custom base branch
```

| Phase | Focus |
|-------|-------|
| 1. Semantic Review | Behavior changes, blast radius, architectural decisions |
| 2. Edge Case Hunt | null, empty, off-by-one, race conditions |
| 3. Rules Check | Compliance with `./absolut-ai/rules.md` |
| 4. Garbage Collection | Dead imports, debug logs, commented code |

**Output:** `./absolut-ai/reviews/YYYY-MM-DD-{branch-slug}.md`

**Smart follow-up:** 0-2 problems → manual fix. 3+ problems → suggests `/absolut-ai:generate-tasks` on the review report.

---

### Supporting Skills

#### `/absolut-ai:debug`

Systematic debugging — root cause investigation before any fixes.

```
/absolut-ai:debug testy w module auth padaja na CI ale przechodza lokalnie
```

4 phases: Root Cause → Pattern Analysis → Hypothesis → Implementation.

Escalates to architecture review if 3+ fixes fail. Includes supporting techniques for root-cause tracing, defense-in-depth validation, and condition-based waiting.

---

#### `/absolut-ai:update-ai-context`

Bootstraps or refreshes AI documentation for the project.

```
/absolut-ai:update-ai-context
```

- **No CLAUDE.md** → Bootstrap: creates full documentation from scratch
- **CLAUDE.md exists** → Update: audits for drift, discovers new patterns

Manages: `CLAUDE.md`, `./absolut-ai/patterns.md`, `./absolut-ai/rules.md`

## File Conventions

All artifacts live under `./absolut-ai/` in the project root:

```
project/
├── absolut-ai/
│   ├── feature/
│   │   ├── planning-{slug}.md
│   │   └── tasks-{slug}.md
│   ├── reviews/
│   │   └── YYYY-MM-DD-{branch-slug}.md
│   ├── patterns.md
│   └── rules.md
├── docs/adr/
│   └── YYYY-MM-DD-{slug}.md
└── CLAUDE.md
```

## Typical Workflows

### New Feature

```bash
/absolut-ai:feature-discuss "system powiadomien push"
/absolut-ai:generate-tasks @absolut-ai/feature/planning-push-notifications.md
/absolut-ai:implement @absolut-ai/feature/tasks-push-notifications.md
/absolut-ai:review
```

### Bug Fix

```bash
/absolut-ai:debug "endpoint /api/users zwraca 500 przy pustym query param"
```

### Project Setup

```bash
/absolut-ai:update-ai-context
```

## Repo Structure

```
absolut-ai-skills/
├── .claude-plugin/
│   ├── marketplace.json    # Marketplace manifest
│   └── plugin.json         # Plugin manifest (name = "absolut-ai")
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
├── package.json
└── README.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension

## License

MIT — Absolut Systems
