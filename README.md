# AbsolutPowers

AI-assisted development lifecycle — from feature design through implementation to code review. Works with Claude Code and Codex.

AbsolutPowers gives your AI coding agent a structured workflow instead of ad-hoc prompting. Each skill handles one phase of the development process. Skills connect into a pipeline with automated quality gates that catch problems before they cascade.

## Quick Start

### 1. Install

**Claude Code:**

```bash
/plugin marketplace add AbsolutSystems/absolutpowers
/plugin install absolutpowers@absolutpowers-skills
```

Restart Claude Code. Type `/absolutpowers:` — autocomplete shows all skills.

**Codex:**

Open repo in Codex → repo marketplace (`.agents/plugins/marketplace.json`) → install `absolutpowers`.

### 2. Prepare your project

Run this once in your project to generate AI context files:

```bash
/absolutpowers:update-ai-context
```

This creates `CLAUDE.md`, `AGENTS.md`, `./absolutpowers/patterns.md`, and `./absolutpowers/rules.md`. These files help all other skills understand your codebase.

### 3. Build a feature

```bash
# Step 1: Discuss and plan
/absolutpowers:feature-discuss "system powiadomień push dla użytkowników"

# Step 2: Generate implementation tasks
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md

# Step 3: Implement
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md

# Step 4: Final code review
/absolutpowers:review
```

Each step produces a file that feeds into the next. Review gates between steps catch issues automatically.

## The Pipeline

```
feature-discuss → generate-tasks → implement → review
     CO?              JAK?        BUDUJ+TEST    AUDYTUJ
      │                 │              │
      ▼                 ▼              ▼
  review-plan      review-tasks   review-implementation
   (gate)            (gate)           (gate)
```

### How gates work

After each skill produces its output, a subagent reviews the result automatically:

1. Subagent reviews the output against specific criteria
2. Returns **PASS** or **REJECTED** with a list of specific issues
3. If REJECTED → the skill fixes the issues and resubmits (up to 3 iterations)
4. If still REJECTED after 3 tries → shows remaining issues and asks you what to do

Gates are Claude Code only. Codex skills run without gates.

## Skills Reference

### `/absolutpowers:feature-discuss`

Interactive Product Owner / Product Architect session. Discusses feature requirements before any code is written.

**What it does:**
- Asks clarifying questions one at a time (with options to choose from)
- Analyzes your codebase for relevant patterns and components
- Proposes 2-3 alternative approaches with tradeoffs
- Iterates on scope, edge cases, dependencies
- Writes a planning document
- Runs `review-plan` gate before finishing

**When to use:** Starting a new feature, brainstorming, "chcę dodać...", "potrzebujemy..."

**Input:** Feature description in natural language

**Output:** `./absolutpowers/feature/planning-{slug}.md`, optionally `./docs/adr/YYYY-MM-DD-{slug}.md`

**Example:**
```bash
/absolutpowers:feature-discuss "eksport danych użytkowników do CSV z filtrowaniem"
```

**Smart routing:** Trivial changes (one-liner, config change) skip the planning doc — the skill suggests direct implementation instead.

---

### `/absolutpowers:generate-tasks`

Reads a planning doc or review report and creates a step-by-step implementation plan for an AI agent.

**What it does:**
- Reads the planning doc and analyzes your codebase
- Discovers patterns, conventions, and existing code to reference
- Produces sequential tasks with exact file paths, method signatures, test cases
- Adds a final verification task with your project's build/test commands
- Runs `review-tasks` gate before finishing

**When to use:** After `feature-discuss` produces a planning doc, or after `review` produces a report with 3+ issues

**Input:** Path to a planning doc or review report

**Output:** `./absolutpowers/feature/tasks-{slug}.md`

**Examples:**
```bash
# From planning doc
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md

# From review report (generates fix tasks)
/absolutpowers:generate-tasks @absolutpowers/reviews/2026-04-21-feature-auth.md
```

---

### `/absolutpowers:implement`

Senior engineer executing tasks sequentially with TDD approach.

**What it does:**
- Picks first pending task, implements with TDD (tests first where appropriate)
- Updates task status to `completed` in-place after each task
- Proposes alternatives if it finds a better approach (asks before changing)
- Executes the final verification task (build, typecheck, lint)
- Runs `review-implementation` gate after all tasks pass
- Creates ADRs for significant implementation decisions
- Can create memory candidates for durable lessons

**When to use:** After `generate-tasks` produces a tasks file

**Input:** Path to a tasks file

**Output:** Implementation code + tests, updated tasks file

**Example:**
```bash
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md
```

---

### `/absolutpowers:review`

Full 4-phase code review of current branch changes.

**What it does:**

| Phase | Focus |
|-------|-------|
| 1. Semantic Review | What changed in behavior, blast radius, architectural decisions |
| 2. Edge Case Hunt | null, empty, off-by-one, race conditions, missing error handling |
| 3. Rules Check | Compliance with `./absolutpowers/rules.md` |
| 4. Garbage Collection | Dead imports, debug logs, commented code, stale TODOs |

**When to use:** Before merge, PR ready, "sprawdź kod", "is this ready"

**Input:** Optional base branch (default: main)

**Output:** `./absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md`

**Examples:**
```bash
/absolutpowers:review              # compare against main
/absolutpowers:review develop      # compare against develop
```

**Smart follow-up:**
- 0-2 issues → fix manually
- 3+ issues → suggests `/absolutpowers:generate-tasks` on the review report

---

### `/absolutpowers:debug`

Systematic debugging — root cause investigation before any fixes.

**What it does:**
- Phase 1: Root cause investigation (read errors, reproduce, trace data flow)
- Phase 2: Pattern analysis (find working examples, compare differences)
- Phase 3: Hypothesis and testing (one change at a time)
- Phase 4: Implementation (failing test → fix → verify)
- Escalates to architecture review if 3+ fixes fail

**When to use:** Bug report, test failure, "nie działa", unexpected behavior, CI failure

**Input:** Bug description or error message

**Output:** Fix + optional memory candidate

**Example:**
```bash
/absolutpowers:debug "endpoint /api/users zwraca 500 przy pustym query param"
/absolutpowers:debug "testy auth padają na CI ale przechodzą lokalnie"
```

---

### `/absolutpowers:update-ai-context`

Bootstraps or refreshes project documentation for AI agents.

**What it does:**
- **No CLAUDE.md** → creates full documentation from scratch (bootstrap)
- **CLAUDE.md exists** → audits for drift, discovers new patterns (update)
- Manages: `CLAUDE.md`, `AGENTS.md` mirrors, `./absolutpowers/patterns.md`, `./absolutpowers/rules.md`
- Proposes rules for human approval (never auto-imposes)

**When to use:** New project setup, after significant codebase changes, onboarding

**Input:** Optional project path (default: current directory)

**Output:** Updated documentation files + change report

**Example:**
```bash
/absolutpowers:update-ai-context
```

## Agents (Claude Code only)

Agents are subagents that skills spawn automatically. You don't invoke them directly — they're part of the pipeline.

| Agent | Spawned by | Purpose |
|-------|-----------|---------|
| `review-plan` | feature-discuss | Validates planning doc completeness, feasibility, architecture |
| `review-tasks` | generate-tasks | Validates task granularity, ordering, specificity, code references |
| `review-implementation` | implement | Validates code correctness, patterns, tests, safety |
| `tech-lead-advisor` | (available for manual use) | Strategic architecture guidance, technology choices, tradeoff analysis |

### Review agent criteria

**review-plan** checks: completeness, feasibility, architectural soundness, actionability

**review-tasks** checks: traceability to planning doc, granularity, ordering & dependencies, specificity of file paths and signatures, verification task presence, code reference accuracy

**review-implementation** checks: correctness, patterns compliance, rules compliance, test coverage, completeness, safety (no secrets, no injection vectors)

## Project Structure in Your Repo

After using AbsolutPowers, your project will contain:

```
your-project/
├── absolutpowers/
│   ├── feature/
│   │   ├── planning-{slug}.md      # Feature plans
│   │   └── tasks-{slug}.md         # Implementation tasks
│   ├── reviews/
│   │   └── YYYY-MM-DD-{branch}.md  # Code review reports
│   ├── memory-candidates/
│   │   └── memory-candidates-*.md  # Proposed durable lessons
│   ├── project-memory.md           # Approved operational memory
│   ├── patterns.md                 # Discovered code patterns
│   └── rules.md                    # Project rules for review
├── docs/adr/
│   └── YYYY-MM-DD-{slug}.md        # Architecture Decision Records
├── CLAUDE.md                        # AI context (Claude Code)
└── AGENTS.md                        # AI context mirror (Codex)
```

**Recommended `.gitignore` additions:**
```gitignore
# Keep planning docs and reviews in git (they're documentation)
# Exclude memory candidates (approval queue, not permanent)
absolutpowers/memory-candidates/
```

## Project Memory

Skills can discover durable lessons during work — recurring traps, non-obvious workarounds, failure patterns. These are captured as memory candidates.

**Workflow:**
1. Skill discovers a lesson worth preserving
2. Creates `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md`
3. Asks you whether to promote it to `./absolutpowers/project-memory.md`
4. Promotion requires your explicit approval
5. After promotion, candidate file is deleted

**What belongs in project memory:**
- Recurring traps with clear warning signs
- Non-obvious workarounds
- Failure patterns that are likely to recur

**What does NOT belong:**
- One-off debugging notes
- Branch-specific status
- Facts that belong in `patterns.md`, `rules.md`, or ADRs

## Workflows

### New feature (full pipeline)

```bash
/absolutpowers:feature-discuss "opis feature'a"
# → dyskusja → planning doc → review-plan gate → PASS

/absolutpowers:generate-tasks @absolutpowers/feature/planning-{slug}.md
# → analiza kodu → tasks doc → review-tasks gate → PASS

/absolutpowers:implement @absolutpowers/feature/tasks-{slug}.md
# → TDD → kod + testy → verification → review-implementation gate → PASS

/absolutpowers:review
# → 4-phase review → report
```

### Quick bug fix

```bash
/absolutpowers:debug "opis błędu"
# → root cause → fix → test
```

### Fix review findings

```bash
/absolutpowers:review
# → report z 5 problemami

/absolutpowers:generate-tasks @absolutpowers/reviews/2026-05-04-feature-auth.md
# → tasks doc z fixami

/absolutpowers:implement @absolutpowers/feature/tasks-fix-feature-auth.md
# → fix → verify
```

### Onboard a new project

```bash
/absolutpowers:update-ai-context
# → CLAUDE.md, AGENTS.md, patterns.md, rules.md (draft for approval)
```

## Platform Differences

| Feature | Claude Code | Codex |
|---------|------------|-------|
| Skills | 6 skills | 6 skills + tech-lead-advisor |
| Agents | 4 agents (review gates + tech-lead-advisor) | none |
| Review gates | Automatic after each pipeline step | Not available |
| Skill invocation | `/absolutpowers:skill-name` | `$absolutpowers skill-name` |
| AI context | CLAUDE.md (source) | AGENTS.md (mirror) |

## Repo Structure (this repository)

```
absolut-ai-skills/
├── claude/                         # Claude Code plugin
│   ├── .claude-plugin/plugin.json
│   ├── skills/                     # 6 skills with agent gates
│   └── agents/                     # 4 subagent definitions
├── codex/                          # Codex plugin
│   ├── .codex-plugin/plugin.json
│   ├── skills/                     # 7 skills (no agent gates)
│   └── scripts/
├── .claude-plugin/marketplace.json # Claude marketplace → claude/
├── .agents/plugins/marketplace.json # Codex marketplace → codex/
├── scripts/
│   ├── diff-skills.sh              # Drift detection between platforms
│   └── sync_claude_to_agents.py    # CLAUDE.md → AGENTS.md sync
└── README.md
```

## Updating

```bash
# Claude Code
/plugin install absolutpowers@absolutpowers-skills

# Codex — pull repo and reinstall from local marketplace
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension
- [Codex](https://github.com/openai/codex) (optional, for Codex target)

## License

MIT — [Absolut Systems](https://github.com/AbsolutSystems)
