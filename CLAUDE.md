# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AbsolutPowers — a Claude Code + Codex plugin providing AI-assisted development lifecycle skills: problem intake/triage, feature discussion, task generation, implementation, review, debugging, project context management, and project constitution. Version 3.9.0.

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
  ├─ potwierdzony bug          → debug @absolutpowers/problem/problem-{slug}.md "Sprawa N"
  ├─ nie zaimplementowane (gap) → feature-discuss → generate-tasks → implement
  ├─ błąd konfiguracji / dane   → fix bezpośredni
  └─ nieporozumienie            → close
```

Output: `absolutpowers/problem/problem-{slug}.md`. Hard boundary: it investigates and routes
only — it does not fix, plan, or write tasks. Cousin of `debug` (breadth-first triage vs depth
root-cause); both trees, no gate. Keep the `debug` "vs problem-discuss" note in sync so triggers
do not collide.

`debug` reads `problem-{slug}.md` (when routed from `problem-discuss`) as the starting point for
Phase 1 — confirms/deepens the evidence instead of re-deriving from scratch. For large root-cause
fixes (multi-layer, migration, public API, security boundary, or 3+ failed attempts), `debug`
writes `absolutpowers/feature/planning-fix-{slug}.md` and nudges to
`/absolutpowers:generate-tasks` instead of implementing inline.

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

### Constitution Skill

`constitution` is a standalone ceremony skill (not part of the linear pipeline) that guides
authoring and ratification of `absolutpowers/constitution.md` — the project's ratified
principles (pryncypia/osąd). Both trees.

Two-file distinction (never merge):
- `absolutpowers/constitution.md` — pryncypia/osąd; ratified principles, values, hard limits.
  Created by the `constitution` skill at runtime. Semver + ratification date + changelog.
- `absolutpowers/rules.md` — mechanika/lint; formatting, naming, forbidden patterns, required libraries.
  Created/refreshed by `update-ai-context` from a code scan.

Pipeline wiring:
- `generate-tasks` + `implement` read `constitution.md` as **binding context** (tasks/implementation MUST NOT violate an article).
- `review` Faza 3 reads `constitution.md` and reports violations (non-blocking; absent file = skip).
- `feature-discuss` reads `constitution.md` as **lightweight context** (not a gate; absent file = silent skip).
- `update-ai-context` PHASE 3 includes a demarcation note directing pryncypia to `constitution.md`, not `rules.md`.

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

### Cross-artifact Audit: `analyze` (both trees)

`analyze` is an on-demand cross-artifact consistency audit — not a pipeline gate.
Invoke it at any point after `generate-tasks` (or before merge) to get a consolidated
AC→task→code traceability matrix and detect divergences that per-step gates miss.

- Builds the full **AC → Task(s) → File(s)/symbol(s)** matrix for a given feature slug
- Detects six divergence classes: (1) AC bez taska, (2) Task bez AC, (3) Task bez kodu,
  (4) Kod bez taska, (5) AC bez weryfikacji, (6) Sprzeczność
- Blocking classes: 1/3/4/6 → verdict **INCONSISTENT**; warning-only: 2/5
- Output: `absolutpowers/reviews/analyze-{slug}.md`, verdict CONSISTENT / INCONSISTENT
- Hard boundary: audits and routes only — routes missing tasks to `generate-tasks`,
  missing code to `implement`; never fixes, plans, or writes code
- Both trees; Claude may delegate matrix build to a subagent

`review-tasks` gained criterion **#7 Intent Fidelity** (category `INTENT`, Claude-only
gate): judges whether the task set as a whole achieves the *goal/intent* of the
planning doc, not just literal per-requirement coverage. Complements `analyze`
(in-flight gate vs post-hoc audit).

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

### Outward-facing bridge: `tasks-to-issues` (Claude only)

`tasks-to-issues` is the only **outward-facing** skill — the rest of the pipeline is
file-bound inside `absolutpowers/`. It reads a `tasks-{slug}.md` (single-file or
orchestrated, including epic subfolder) and exports it to **GitHub Issues** via `gh`:
one epic issue per feature + a sub-issue per phase (orchestrated) / per task
(single-file); tasks inside a phase become a checklist in the phase issue body.

- **Idempotent:** back-map `absolutpowers/feature/tasks-{slug}.issues.md` is the source of
  truth; title marker `[{slug}]` is the fallback. Re-runs add missing, update existing
  (open) issues, leave closed ones untouched, never duplicate. Map is rewritten after each
  issue (resume-safe).
- **STOP-on-precondition** (mirrors `preboot`): aborts with a clear message if `gh` is
  unauthenticated, no GitHub remote exists, or the user lacks issue-create permission — no
  partial export.
- **Hard boundary:** creates/updates issues + map ONLY. Never closes issues (even after
  `implement`/merge), never pushes code, never mutates task statuses in the tasks-doc (that
  is `implement`'s job), never creates milestones/assignees/board automation. One-directional
  (tasks → issues; no tracker → tasks-doc sync).
- **Provider:** GitHub via `gh` in v1, with a delimited provider section as the extension
  point for `glab`/Jira later.

**Claude-only asymmetry (deliberate):** no Codex counterpart in v1 — it needs `Bash(gh:*)` and
external API interaction. Codex is out of scope until the contract stabilizes. This is NOT
drift to fix (see Cross-Platform Editing Rules).

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

When modifying `analyze` (cross-artifact audit) or the divergence class list, update both trees together:
- `claude/skills/analyze/SKILL.md`
- `codex/skills/analyze/SKILL.md`

`tasks-to-issues` is intentionally **single-tree** (Claude only) — `claude/skills/tasks-to-issues/SKILL.md`
has no `codex/` counterpart. Its absence from Codex is expected, NOT drift to fix; `diff-skills.sh`
will list it as Claude-only.

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
