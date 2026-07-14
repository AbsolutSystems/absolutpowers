# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AbsolutPowers — a Claude Code + Codex + Pi + Grok plugin providing AI-assisted development lifecycle skills: problem intake/triage, feature discussion, task generation, implementation, review, debugging, project context management, and project constitution. Version 5.1.3. As of 5.0.0 the repo is a single host-agnostic skill tree (see Repository Layout) with thin per-harness manifests/integrations, replacing the earlier two mirrored `claude/`/`codex/` trees; it also introduces `skills/vendored/` — selected skills vendored from [obra/superpowers](https://github.com/obra/superpowers) under MIT (see `VENDORED.md`, `LICENSE-VENDORED`). Grok Build is supported as a first-class harness via `.grok-plugin/` + `references/grok-tools.md`.

## Repository Layout

One host-agnostic skill tree serves every harness (Claude Code, Codex, Pi); thin per-harness manifests and integrations layer on top (obra/superpowers pattern):

- `skills/{name}/SKILL.md` — single source of truth. Host-agnostic body; Claude-only sections (frontmatter `allowed-tools`/`argument-hint`, agent gate sections) are inert on Codex/Pi.
- `skills/vendored/{name}/` — vendored obra/superpowers skills with MIT attribution (see `VENDORED.md`, `LICENSE-VENDORED`).
- `agents/{name}.md`, `commands/{name}.md` — top-level, Claude-only; other harnesses ignore them.
- `hooks/` — slim Claude SessionStart hook (`hooks.json` + `run-hook.cmd` + `session-start`) plus shared `hooks/session-context.md`.
- `references/{harness}-tools.md` — per-harness primitive mappings, read conditionally. Adding a harness = new integration/manifest + optional reference, zero skill edits (Grok: `.grok-plugin/plugin.json` + `references/grok-tools.md`).

Manifests and marketplaces (all top-level, pointing at repo root):
- `.claude-plugin/plugin.json` — Claude manifest; `.claude-plugin/marketplace.json` → `source: "."`.
- `.codex-plugin/plugin.json` — Codex manifest; `.agents/plugins/marketplace.json` → `source.path: "."`.
- `AGENTS.md` — symlink to `CLAUDE.md` (bootstrap for harnesses that read AGENTS.md, e.g. Codex).

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

### Terminal-state contract (prose, `/goal`-aware)

Each of the four pipeline skills ends with a `## Terminal state` section (prose, Polish — no machine format / frontmatter key). The three intermediate skills (`feature-discuss`, `generate-tasks`, `implement`) declare what they deliver, name the next link as `@<skill>` (`@generate-tasks` / `@implement` / `@review`), and explicitly state the pipeline is **not closed** — so a session driven by Claude Code's `/goal` continues down the chain instead of stopping mid-pipeline. `review`/`triada-review` is the distinguished **closure point** (fix-loop or merge/ship), not a chain link — it names no forward `@skill`. There is no separate "execution-mode" fork: `implement` is the sole executor, and the `## Mode` field (`orchestrated`/`single-file`) set by `generate-tasks` is the absolutpowers analog of obra's `subagent-driven-development` vs `executing-plans` split (a resolved decision, not a missing feature).

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
root-cause); no gate, on every harness. Keep the `debug` "vs problem-discuss" note in sync so
triggers do not collide.

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

### Closeout and on-demand knowledge capture

There is no orchestrated closeout wrapper — closeout and knowledge capture are separate, on-demand skills the user runs when useful. `implement` prints one best-effort nudge toward `ship` (the closeout: commit message + PR description from artifacts, and — with approval — archiving the feature's `planning-*.md`/`tasks-*.md` into `absolutpowers/archives/{slug}/` with a `summary.md`, folded into the closing commit).

Knowledge-capture skills, each standalone and ad-hoc:
- `try-learn-skill` — **scans the whole codebase** for repeated (≥3 occurrences, `file:line` evidence), non-obvious procedures and proposes them as invocable project learned-skills → `.claude/skills/learned/` (batch approval, human gate). Its signal is codebase-wide repetition, NOT a single feature's artifacts. Boundary vs `update-ai-context`: the latter produces **passive documentation** (`patterns.md`/`rules.md`/`CLAUDE.md`, read as background), try-learn produces **active invocable procedures**.
- `document-feature` — per-module prose docs from a finished feature → `docs/modules/`.
- `document-module` — module architecture + C4 (code-scan of one module) → `docs/modules/{slug}-architecture.md` + `docs/architecture/{slug}.html`.
- `update-ai-context` (code-scan → broad `CLAUDE.md`/`patterns.md`/`rules.md`) and `explain` (ephemeral HTML) round out the doc skills.

### Constitution Skill

`constitution` is a standalone ceremony skill (not part of the linear pipeline) that guides
authoring and ratification of `absolutpowers/constitution.md` — the project's ratified
principles (pryncypia/osąd).

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

Subagents auto-verify each pipeline step. PASS or REJECTED with issues. Up to 3 fix iterations, then asks user.

**Precise Codex/Pi statement (do not simplify to "no subagent support"):** Codex and Pi lack **registered agent type definitions** — there is no mechanism to load `agents/*.md` as an installable subagent identity the way Claude Code plugins do, so `Agent(subagent_type="review-tasks", ...)` calls have nothing to resolve to. That is *not* the same as lacking subagent dispatch: Codex exposes `multi_agent=true` → `spawn_agent`/`wait_agent`/`close_agent` primitives, and Pi has the optional `pi-subagents` package. So the *execution pattern* (dispatch a subagent, hand it a prompt, wait, read its verdict) is portable across harnesses — only the *registry* (named, reusable agent types) is Claude-only. Practical effect: review gates as AbsolutPowers implements them (named `agents/*.md` types) are Claude-only, but a harness can still run the same review inline or via a generic dispatched subagent fed the `agents/{name}.md` body as its prompt. See `references/pi-tools.md` ("Review gates on Pi") and the parallel `references/codex-tools.md` ("Review gates on Codex" / "Orchestrated dispatch on Codex") for the worked-out degradation paths (see "Adding a New Harness" below).

### Orchestrated Implementation (Claude only)

`generate-tasks` can produce two modes:
- `single-file` — one `tasks-{slug}.md` for small changes
- `orchestrated` — parent index + `tasks-{slug}/` directory with phase files, `implementation-context.md`, and `99-final-verification.md`

Ownership contract:
- `implementation-worker` updates only its phase file and `implementation-context.md`
- `implement` orchestrator updates phase status in parent tasks file
- `phase-review` is read-only, returns VERDICT only

`implementation-worker` returns one of four `PHASE_RESULT` values — `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED` — instead of the older 3-state `COMPLETED`/`BLOCKED`/`FAILED`; the orchestrator (Step O3) branches on each independently, escalating (context → model → decomposition → human) only for `BLOCKED`. Every subagent dispatch (`implementation-worker`, `phase-review`, `review-implementation`) carries an explicit `model=` sized per role — transcription-tier `haiku`/standard `sonnet`/most-capable `opus` for the worker (by phase `Risk:` and code completeness), diff-scaled for `phase-review`, always `opus` for the final `review-implementation` gate. Progress is durable across three files: the phase file (full spec), `implementation-context.md` (narrow handoff), and a git-anchored `progress.md` ledger (one line per phase, `Faza N: complete (commits base7..head7, review clean)`) that Step O1 treats as authoritative on resume over the human-facing status table. Before dispatching each `phase-review`/`review-implementation` call, the orchestrator generates a `review-package` (forked from vendored `subagent-driven-development`) and passes its path in the prompt so reviewers read one file instead of running their own diff.

### Cross-artifact Audit: `analyze`

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
- Claude may delegate matrix build to a subagent

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
skill — see the `review` SKILL for the distinction. Codex/Pi have no equivalent —
not because dispatch is unavailable, but because there is no registered
`tech-lead-advisor`/`codebase-auditor`/`ui-reviewer` agent type to fan out to, and
no built-in mechanism to run three dispatched subagents in parallel and merge
their verdicts.

## Key Development Commands

```bash
# Install plugin locally (Claude Code)
/plugin install absolutpowers@absolutpowers-skills

# Test a skill in a project directory
/absolutpowers:{skill-name} [args]

# Validate every manifest is valid JSON
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done

# Validate the SessionStart hook emits valid JSON
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null

# Validate every SKILL.md has frontmatter
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done

# Typecheck the Pi extension (requires @earendil-works/pi-coding-agent resolvable, e.g. a
# temporary node_modules symlink to a local/global install; remove it afterwards, do not commit)
npx --package=typescript@latest -- tsc --noEmit --module esnext --moduleResolution bundler \
  --target es2022 --skipLibCheck .pi/extensions/absolutpowers.ts

# Grok plugin validation (if grok CLI available in the environment)
grok plugin validate .   # validates .grok-plugin/plugin.json when present
```

## Cross-Harness Editing Rules

There is now one skill tree, so there are no mirror files to keep in sync. A single edit to a `skills/{name}/SKILL.md` serves every harness. Keep skill bodies host-agnostic:

- Claude-only frontmatter (`allowed-tools`, `argument-hint`) and agent gate sections are tolerated and inert on Codex/Pi — do not duplicate skills per harness.
- Per-harness differences belong in `references/{harness}-tools.md` (read conditionally), never in a forked skill body.
- When changing task format or pipeline behavior, also update the relevant `agents/*.md`, `commands/*.md`, `README.md`, and `docs/`.

## Adding a New Harness

The obra/superpowers pattern this repo adopted in 5.0.0 is designed so a new harness costs an
integration, not a rewrite. To add harness `{h}`:

1. **Add a thin manifest/integration for `{h}`**, following the shape of the existing ones —
   `.codex-plugin/plugin.json` (declarative manifest, points at `./skills/`) or
   `.pi/extensions/absolutpowers.ts` (a small extension: register the skill directory, inject
   `hooks/session-context.md` at session start/compact). Nothing here duplicates skill content;
   it only wires the harness up to the one shared tree.
2. **Add an optional `references/{h}-tools.md`** if the harness has primitives that differ enough
   from Claude's to need a mapping (subagent dispatch, task tracking, review-gate degradation —
   see `references/pi-tools.md` for the template). Not every harness needs one — add it only when
   a skill actually needs to branch on harness-specific tooling.
3. **Zero skill edits.** `skills/{name}/SKILL.md` bodies stay host-agnostic. If `{h}` chokes on a
   specific frontmatter key or prose section, that content moves into `references/{h}-tools.md`
   (read conditionally), never into a forked copy of the skill.
4. **Gates and the Claude hook degrade gracefully.** Registered review-gate agent types
   (`agents/*.md`) and `hooks/` are Claude-only; `{h}` either dispatches a generic subagent fed the
   target agent's prompt, runs the review inline with an explicit non-isolation disclaimer, or (for
   session bootstrap) reads `hooks/session-context.md` directly from its own extension — the same
   file `hooks/session-start` reads, never duplicated inline.

**Realized examples of this exact pattern:** Codex (`.codex-plugin/plugin.json` +
`references/codex-tools.md`, which documents the `spawn_agent` dispatch path, the two-tier
review-gate degradation, and the sequential/inline orchestrated fallback), Pi
(`.pi/extensions/absolutpowers.ts` + `references/pi-tools.md`, which documents the `pi-subagents`
dispatch path and the two-tier review-gate degradation), and Grok
(`.grok-plugin/plugin.json` + `references/grok-tools.md`, which documents `spawn_subagent` +
`subagent_type: "general-purpose"`, two-tier gate degradation, and bootstrap via AGENTS.md/CLAUDE.md + hooks).

## PreBoot Skill

One shared `preboot` skill (not per-module, one copy in `skills/preboot/`, served to every harness). Acts as documentation router — maps detected PreBoot API usage to local `./preboot-docs/` in the target project. Does not ship bundled API docs. Stops if local docs missing.

## Versioning

SemVer across manifests (must match):
- `.claude-plugin/plugin.json` → `"version"`
- `.codex-plugin/plugin.json` → `"version"`
- `.grok-plugin/plugin.json` → `"version"` (Grok)

Major = breaking structure changes. Minor = new skill/agent/feature. Patch = prompt fixes/bugfixes.

## Language

Skills and docs are bilingual — Polish for user-facing prompts and docs, English for technical content and code. Follow existing language choice per file.
