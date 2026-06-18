# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AbsolutPowers — a Claude Code + Codex plugin providing AI-assisted development lifecycle skills: problem intake/triage, feature discussion, task generation, implementation, review, debugging, and project context management. Version 3.8.0.

## Repository Layout

Two parallel plugin trees share most skill logic but differ in platform capabilities:

- `claude/` — Claude Code plugin. Has `skills/`, `agents/`, `commands/`, and `.claude-plugin/plugin.json`
- `codex/` — Codex plugin. Has `skills/`, `.codex-plugin/plugin.json`. No agents or commands (Codex lacks plugin-level subagent support)

Skills live in `{platform}/skills/{name}/SKILL.md`. Agents live in `claude/agents/{name}.md` (Claude only). Slash commands live in `claude/commands/{name}.md` (Claude only).

Supporting files:
- `scripts/diff-skills.sh` — drift detection between Claude and Codex skill files
- `scripts/sync_claude_to_agents.py` — CLAUDE.md → AGENTS.md sync helper for target projects
- `.claude-plugin/marketplace.json` → points to `claude/`
- `.agents/plugins/marketplace.json` → points to `codex/`

## Skill and Agent File Format

### Skills (`SKILL.md`)

```yaml
---
name: skill-name           # kebab-case
description: >             # triggers + purpose (used for auto-detection)
allowed-tools: Read, Glob  # Claude only — omit for Codex
argument-hint: "[hint]"    # Claude only — omit for Codex
---
```

Body after frontmatter is the prompt in Markdown. `$ARGUMENTS` is the user-supplied argument.

### Agents (Claude only)

```yaml
---
name: agent-name
description: >
model: sonnet              # optional: opus/sonnet/haiku
tools:                     # optional tool list
  - Read
  - Glob
---
```

Agent limitations in plugins: no `hooks`, `mcpServers`, or `permissionMode`.

## Pipeline Architecture

```
feature-discuss → generate-tasks → implement → review
     │                 │              │
     ▼                 ▼              ▼
 review-plan      review-tasks   review-implementation
  (gate)            (gate)           (gate)
```

### Intake / triage front door

`problem-discuss` is an optional entry point **upstream** of the pipeline. It takes a fuzzy,
multi-item client report, decomposes it into discrete items, extracts the intended business rule
per item, investigates the code breadth-first (evidence, not fixes), classifies each item into one
of 6 buckets, and fans out a route per item:

```
problem-discuss (no gate — investigative, like debug)
  ├─ potwierdzony bug          → debug
  ├─ nie zaimplementowane (gap) → feature-discuss → generate-tasks → implement
  ├─ błąd konfiguracji / dane   → fix bezpośredni
  └─ nieporozumienie            → close
```

Output: `absolutpowers/problem/problem-{slug}.md`. Hard boundary: it investigates and routes
only — it does not fix, plan, or write tasks. Cousin of `debug` (breadth-first triage vs depth
root-cause); both trees, no gate. Keep the `debug` "vs problem-discuss" note in sync so triggers
do not collide.

For larger features, `implement` orchestrates via subagents:

```
tasks-{slug}.md (orchestrator index)
  ├─ implementation-worker → phase-review (per phase)
  ├─ implementation-worker → phase-review
  ├─ 99-final-verification (run by orchestrator)
  └─ review-implementation (final gate)
```

### Harvest Phase (closeout)

After `implement`, before commit, an optional **harvest phase** gathers durable knowledge from the finished feature. `implement` prints one best-effort nudge toward `harvest`, a thin orchestrator that runs `try-learn-skill` (reusable procedure → `.claude/skills/learned/`), then `document-feature` (per-module prose docs → `docs/modules/`), then `document-module` (module architecture + C4 → `docs/modules/{slug}-architecture.md` + `docs/architecture/`, **only for touched modules whose architecture changed**), each keeping its own gate. `document-feature` is distinct from `document-module` (code-scan of one module → architecture + C4 diagrams, on-demand, `docs/modules/{slug}-architecture.md` + `docs/architecture/{slug}.html`), `update-ai-context` (code-scan → broad `CLAUDE.md`), and `explain` (ephemeral HTML). Both skills live in both trees.

### Review Gates (Claude only)

Subagents auto-verify each pipeline step. PASS or REJECTED with issues. Up to 3 fix iterations, then asks user. Codex runs without gates.

### Orchestrated Implementation (Claude only)

`generate-tasks` can produce two modes:
- `single-file` — one `tasks-{slug}.md` for small changes
- `orchestrated` — parent index + `tasks-{slug}/` directory with phase files, `implementation-context.md`, and `99-final-verification.md`

Ownership contract:
- `implementation-worker` updates only its phase file and `implementation-context.md`
- `implement` orchestrator updates phase status in parent tasks file
- `phase-review` is read-only, returns VERDICT only

### Standalone Triada Review (Claude only)

`/absolutpowers:triada-review` — on-demand multi-agent code review of the current
branch vs master. The main session acts as orchestrator: gathers context (diff, PR,
CI, `rules.md`), delegates to three agents **in parallel** with non-overlapping
scopes, then synthesizes one report (JSON per agent → merged verdict).

- `tech-lead-advisor` (`absolutpowers:tech-lead-agent`) — goal, architecture, overengineering, readability
- `security-auditor` (`absolutpowers:codebase-auditor`) — security, correctness, test quality
- `ui-reviewer` (`absolutpowers:ui-reviewer`) — UI states, interactions, a11y, data, UI races, user goal (spawned only when UI files present)

Defaults are baked into the command; an optional per-project
`.claude/triada-review.agents.json` can override role → `subagent_type`, `enabled`,
and `scope`. This is separate from the pipeline gates and from the solo `review`
skill — see the `review` SKILL for the distinction. Codex has no equivalent
(needs parallel subagents).

## Key Development Commands

```bash
# Detect drift between Claude and Codex skills
./scripts/diff-skills.sh           # summary
./scripts/diff-skills.sh --diff    # full diff

# Install plugin locally (Claude Code)
/plugin install absolutpowers@absolutpowers-skills

# Test a skill in a project directory
/absolutpowers:{skill-name} [args]
```

## Cross-Platform Editing Rules

When modifying task format or pipeline behavior, update these files together:
- `claude/skills/generate-tasks/SKILL.md`
- `claude/skills/implement/SKILL.md`
- `claude/agents/review-tasks.md`
- `claude/agents/review-implementation.md`
- `codex/skills/generate-tasks/SKILL.md`
- `codex/skills/implement/SKILL.md`
- `README.md` and `docs/`

Expected drift (Claude-only additions): `allowed-tools`, `argument-hint` in frontmatter, agent gate sections, orchestrated worker delegation. Unexpected drift to sync: changed phases/steps, new prompt sections, output format changes.

## PreBoot Skill

One shared `preboot` skill (not per-module). Acts as documentation router — maps detected PreBoot API usage to local `./preboot-docs/` in the target project. Does not ship bundled API docs. Stops if local docs missing. Should stay synchronized between Claude and Codex.

## Versioning

SemVer across both manifests (must match):
- `claude/.claude-plugin/plugin.json` → `"version"`
- `codex/.codex-plugin/plugin.json` → `"version"`

Major = breaking structure changes. Minor = new skill/agent/feature. Patch = prompt fixes/bugfixes.

## Language

Skills and docs are bilingual — Polish for user-facing prompts and docs, English for technical content and code. Follow existing language choice per file.
