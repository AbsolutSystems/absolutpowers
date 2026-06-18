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

# Step 5 (optional, pre-commit): harvest knowledge — learned skill + module docs
/absolutpowers:harvest @absolutpowers/feature/tasks-push-notifications.md
```

Each step produces files that feed into the next. Small features usually get one `tasks-{slug}.md`; larger features can get an orchestrated phase plan with `tasks-{slug}/NN-phase.md` files and a shared `implementation-context.md`. Review gates between steps catch issues automatically.

## The Pipeline

```
feature-discuss (+ qa-enrichment) → generate-tasks → implement → review → harvest
         CO?                            JAK?        BUDUJ+TEST    AUDYTUJ   UTRWAL
          │                               │              │                    │
          ▼                               ▼              ▼                    ▼
      review-plan                    review-tasks   review-implementation  try-learn-skill
       (gate)                          (gate)           (gate)             + document-feature
```

`problem-discuss` is an optional **intake/triage** front door — for a fuzzy, multi-item
client report where each item must be classified before it enters the pipeline:

```
problem-discuss (zgłoszenie klienta → klasyfikacja per sprawa)
  ├─ bug            → debug
  ├─ gap featurowy  → feature-discuss → generate-tasks → implement
  ├─ config / dane  → fix bezpośredni
  └─ nieporozumienie → close
```

`harvest` is an optional pre-commit closeout — see [Harvest Phase](#harvest-phase).

For larger Claude Code implementations, `implement` becomes an orchestrator:

```
tasks-{slug}.md
  ├─ implementation-worker → phase-review
  ├─ implementation-worker → phase-review
  ├─ final verification
  └─ review-implementation
```

Each implementation worker gets one phase file and a fresh, smaller context. `implementation-context.md` carries only concise handoff facts between phases.

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
- Runs QA enrichment to generate behavioral Acceptance Criteria (AC-1, AC-2, ...)
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
- Produces either a single sequential tasks file or an orchestrated phase plan for larger features
- For orchestrated plans, creates phase files with read scope, write scope, focused verification, and completion criteria
- Creates `implementation-context.md` as a concise handoff contract between phases
- Maps Acceptance Criteria from planning doc to tasks with `Traces to: AC-N` traceability
- Adds a final verification task with your project's build/test commands
- Runs `review-tasks` gate before finishing

**When to use:** After `feature-discuss` produces a planning doc, or after `review` produces a report with 3+ issues

**Input:** Path to a planning doc or review report

**Output:** `./absolutpowers/feature/tasks-{slug}.md`; for larger features also `./absolutpowers/feature/tasks-{slug}/`

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
- Picks first pending task or, for orchestrated plans, the first pending phase
- In Claude Code, delegates each orchestrated phase to `implementation-worker` and runs `phase-review` before advancing
- In Codex, executes phase files sequentially in the same session
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

### `/absolutpowers:triada-review` (Claude Code only)

On-demand **multi-agent** code review of the current branch vs master. The main
session orchestrates three agents with non-overlapping scopes **in parallel**, then
synthesizes one report. Complements — does not replace — the solo `review` skill.

**What it does:**
- Gathers context (diff, PR description, CI status, commit messages, `./absolutpowers/rules.md`)
- Reconstructs the change goal and sanity-checks description vs diff
- Splits large diffs into ≤5 packages (single mode under 1500 lines / 20 files)
- Delegates to three agents in parallel, each scoped to its own criteria:

| Role (scope label) | `subagent_type` | Scope |
|---|---|---|
| `tech-lead-advisor` | `absolutpowers:tech-lead-agent` | goal, architecture, overengineering, readability |
| `security-auditor` | `absolutpowers:codebase-auditor` | security, correctness, test quality |
| `ui-reviewer` | `absolutpowers:ui-reviewer` | UI states, interactions, a11y, data, UI races, user goal (UI files only) |

- Each agent also flags `rules.md` violations within its scope
- Synthesizes: merged findings by severity, rules compliance, cross-package issues, priority disagreements, final verdict (`approve` / `approve_with_comments` / `request_changes` / `block`)

**Defaults are baked in** — works with no config. Optionally override role →
`subagent_type` / `enabled` / `scope` per project via `.claude/triada-review.agents.json`.

**review vs triada-review:** `review` is solo, 4-phase, writes an audit-trail report,
integrates with `project-memory.md`, and works on Codex. `triada-review` is parallel,
multi-agent, JSON-synthesized, and Claude-only — reach for it on larger PRs.

**When to use:** Larger PRs, when you want independent perspectives, "review this branch"

**Input:** Optional context hint (e.g. "focus on the billing layer")

**Output:** Synthesized report in the session (no file written)

**Example:**
```bash
/absolutpowers:triada-review
/absolutpowers:triada-review "skup się na warstwie płatności"
```

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

### `/absolutpowers:problem-discuss`

Intake & triage for a fuzzy, multi-item client report. Decomposes the report into discrete
items, establishes the intended business rule per item, confronts it with the code, classifies
each item, and routes it onward. Cousin of `debug` (breadth-first), not `feature-discuss`.

**What it does:**
- Decomposes one client report into N discrete items (Faza 0)
- Per item: extracts the stated business rule (intended behavior) vs the reported discrepancy
- Reads attachments (images/files passed in the prompt) as evidence
- Investigates the code flow breadth-first, with `file:line` evidence (analysis, **not** a fix)
- Classifies each item into one of 6 buckets, then fans out a route recommendation
- Writes a report; **does not** fix, plan, or write tasks (hard boundary)

**Classification → route:**

| Bucket | Route |
|---|---|
| potwierdzony bug | `debug` |
| nie zaimplementowane (gap) | `feature-discuss` |
| błąd konfiguracji / env | fix bezpośredni |
| anomalia danych | fix danych |
| działa-jak-zaprojektowano (nieporozumienie) | close + wyjaśnienie klientowi |
| za mało danych | dopytaj klienta |

**When to use:** A client/stakeholder sends a multi-item report about an existing module —
"po akceptacji korekty powinny wyjść maile, w produkcji ich nie widzę", a list of remarks from
production, a discrepancy between a documented rule and observed behavior. **Not** for a clean
error/stack trace/test failure (that's `debug`) or a new feature request (that's `feature-discuss`).

**Input:** Client report text + paths to attachments (images/files)

**Output:** `./absolutpowers/problem/problem-{slug}.md` (per-item analysis + routing table)

**Example:**
```bash
/absolutpowers:problem-discuss "Klient zgłosił: 1) dlaczego user X dostaje maile (obraz.png), 2) po korekcie nie widzę 2 maili (culinar1.pdf)"
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

---

### `/absolutpowers:explain`

Generates a standalone HTML onboarding report for a plan or current code changes.

**What it does:**
- Reads a provided planning/tasks document or inspects the current git diff
- Separates verified facts from assumptions
- Highlights human decisions and open questions near the top
- Produces a self-contained HTML report with file map, risks, and optional Mermaid diagrams

**When to use:** After a plan, feature, refactor, or review when a human needs a fast, auditable explanation of what changed.

**Input:** Optional path or scope description; defaults to current repository changes.

**Output:** `./docs/onboarding/<slug>-<YYYY-MM-DD>.html`

**Example:**
```bash
/absolutpowers:explain @absolutpowers/feature/tasks-push-notifications.md
```

---

### `/absolutpowers:try-learn-skill`

Extracts a reusable procedure from a finished feature's artifacts into a callable
**learned skill** stored in your project under `.claude/skills/learned/`.

**What it does:**
- Reads the feature's `planning-{slug}.md`, `tasks-{slug}.md` (+ phase files), and the `git diff` (process + effect)
- Detects whether there is a **generalizable** procedure (repeatable on another task of the same class) — if not, reports "nic do utrwalenia" and stops
- Globs existing `.claude/skills/learned/**/SKILL.md` to decide **NEW vs UPDATE** (UPDATE bumps `occurrences` and promotes `confidence: candidate → established` on the 2nd encounter)
- **SKIP**s when the procedure overlaps a static skill (feature-discuss, implement, review, …) — no duplicating built-in behavior
- Proposes the full generated `SKILL.md` and **waits for your acceptance (human gate)** before writing
- Generated learned skills carry a `learned-meta` block in the body and a narrow `TRIGGER when:` to avoid retrieval collisions

**Manual, opt-in step.** `implement` only prints a soft, best-effort nudge after
completion — forgetting it is never an error.

**When to use:** After a feature is implemented and you want to preserve a repeatable procedure

**Input:** Path to a `tasks-*.md` or `planning-*.md`

**Output:** `{your-project}/.claude/skills/learned/learned-{name}/SKILL.md` (after approval)

**Example:**
```bash
/absolutpowers:try-learn-skill @absolutpowers/feature/tasks-push-notifications.md
```

---

### `/absolutpowers:document-feature`

Generates or updates durable **per-module** documentation from a finished
feature's artifacts, written to your project under `docs/modules/{module}.md`.

**What it does:**
- Reads the feature's `planning-{slug}.md` (the "why"), `tasks-{slug}.md` (+ phase files), and the `git diff` (the truth about the code)
- Detects which **modules** the feature touched (`CLAUDE.md` `## Project Structure` / `patterns.md` → path heuristic fallback)
- **Shows the detected file→module mapping and waits for confirmation** — the single hard gate (wrong detection = docs in the wrong file)
- For each module: NEW (create) or UPDATE (**intelligent merge** — rewrites touched sections to reflect the current state, not an append-changelog)
- **Auto-writes** the content (pre-commit `git diff` is the natural review surface; docs are non-executable) and stamps a `doc-meta` block (`last-updated`, `last-commit`)

**When to use:** After a feature, before commit — so the module doc stays "how it works now". Read it before extending the module ("read the `auth` module docs before you grow it").

**Input:** Path to a `tasks-*.md` or `planning-*.md`

**Output:** `{your-project}/docs/modules/{module}.md`

**Example:**
```bash
/absolutpowers:document-feature @absolutpowers/feature/tasks-push-notifications.md
```

---

### `/absolutpowers:document-module`

Generates **architectural documentation of an existing module from a code scan**:
structure, public API, dependencies, key flows, plus C4 diagrams (C1–C3) and
sequence diagrams. Two audiences — human (HTML) and AI-as-new-dev (markdown).

**What it does:**
- Resolves the module → file set (`CLAUDE.md` `## Project Structure` / `patterns.md` → explicit path → path heuristic) and echoes the boundary
- Scans the module's code: public API, internal components, in/out dependencies, persistence, key operations
- Marks **verified** (seen in code, `file:line`) vs **inferred** relationships (auditability)
- Generates Mermaid **C4** diagrams (C1 Context / C2 Container / C3 Component) + sequence diagrams for key flows; validates with `mermaid-cli` if available, falls back to `graph`/`flowchart`
- Writes markdown (**source of truth**, AI) and a self-contained HTML (**regenerable**, human, always overwritten)

**When to use:** "udokumentuj architekturę modułu auth", "diagram modułu", "C4 modułu" — when you want a durable, diagram-rich architecture reference of a module as it exists now. **Not** for documenting one finished feature (that's `document-feature`) or explaining a single change (that's `explain`).

**Input:** Module name or path (e.g. `auth` or `src/billing`)

**Output:** `{your-project}/docs/modules/{slug}-architecture.md` + `{your-project}/docs/architecture/{slug}.html`

**Example:**
```bash
/absolutpowers:document-module auth
/absolutpowers:document-module src/billing
```

---

### `/absolutpowers:harvest`

Thin closeout orchestrator for the **harvest phase**. Runs `try-learn-skill`,
`document-feature`, then `document-module` over one finished feature, each keeping its own gate.

**What it does:**
- Runs `try-learn-skill` (reusable procedure → learned skill, human gate)
- Runs `document-feature` (per-module prose docs, mapping-confirm gate)
- Runs `document-module` (module architecture + C4) **only for touched modules whose architecture changed** — new file / new public symbol / new cross-module import (NEW or refresh, decided by `document-module`); skips cosmetic/internal-only edits to avoid noisy diagram churn
- Gracefully **skips** a sub-skill the project opted out of — missing is not an error
- Reminds you to review the result in `git diff` before committing

**When to use:** At the end of `implement`, before commit. `implement` prints a single best-effort nudge toward it.

**Input:** Path to a `tasks-*.md` or `planning-*.md`

**Output:** Orchestrates both sub-skills (learned skill + module docs)

**Example:**
```bash
/absolutpowers:harvest @absolutpowers/feature/tasks-push-notifications.md
```

## Harvest Phase

The **harvest phase** runs at the end of `implement`, before commit. It is the
single closeout entry point that gathers durable knowledge from a finished
feature: a reusable procedure (`try-learn-skill`) and per-module documentation
(`document-feature`). Each sub-skill keeps its own gate; the result is reviewed
in `git diff` before commit.

```
feature-discuss → generate-tasks → implement → review
                                       │
                                       ▼ (optional, pre-commit)
                                    harvest
                                       ├─ try-learn-skill → .claude/skills/learned/
                                       ├─ document-feature → docs/modules/{module}.md
                                       └─ document-module → docs/modules/{module}-architecture.md + docs/architecture/*.html
                                          (tylko gdy zmiana architektury)
```

**Four documentation mechanisms — deliberately different:**

| | `document-feature` | `document-module` | `update-ai-context` | `explain` |
|---|---|---|---|---|
| Captures | Deep, **per-module** prose from planning + diff | **Architecture** of a module from a **code scan** (C4 diagrams) | Broad/shallow `CLAUDE.md` from a **code scan** | Ephemeral, single-change human onboarding |
| Source | One feature's planning (why) + git diff (truth) | One module's code (scan, as-is) | Whole-codebase structural scan | A plan/tasks doc or current git diff |
| Granularity | Per module (`docs/modules/{module}.md`) | Per module (`docs/modules/{slug}-architecture.md` + HTML) | Per package (hierarchical `CLAUDE.md`) | Per change |
| Trigger | After a feature, on-demand (or via harvest) | On-demand ("document module X") | Bootstrap / refresh | On-demand, when a human needs a fast explanation |
| Output | `docs/modules/{module}.md` (durable) | `docs/modules/{slug}-architecture.md` (md, truth) + `docs/architecture/{slug}.html` (regenerable) | `CLAUDE.md` / `AGENTS.md` (auto-injected) | `docs/onboarding/*.html` (ephemeral) |
| Audience | AI agent as a new developer | Human (HTML) + AI as new developer (md) | Every skill's auto-loaded context | A human |

If it is "deep, durable knowledge of how a module works and why," it belongs in
`document-feature`. If it is "the architecture/structure of a module with
diagrams, from a code scan," that is `document-module`. If it is "broad code
conventions auto-loaded into context," that is `update-ai-context`. If it is "a
one-off, human-readable explanation of a change," that is `explain`.

## Learned Skills

Learned skills are project-local, callable procedures that AbsolutPowers can
extract from finished work via `try-learn-skill`. They live in your project under
`.claude/skills/learned/` and are namespaced `learned-{name}`.

**Pipeline position:** part of the optional **harvest phase** after `implement`
(see [Harvest Phase](#harvest-phase)). `implement` nudges you toward `harvest`,
which runs `try-learn-skill` first. The pipeline does not require it.

```
feature-discuss → generate-tasks → implement → review
                                       │
                                       ▼ (optional, pre-commit)
                                    harvest → try-learn-skill → .claude/skills/learned/
```

**Learned skills vs `patterns.md`** — they are deliberately different and should
not duplicate each other:

| | Learned skill | `patterns.md` |
|---|---|---|
| Captures | A **procedure** (sequence of steps/tools/decisions) | **Code structure** (recurring conventions) |
| Form | Callable `SKILL.md` with a narrow `TRIGGER when:` | Descriptive reference, read by `generate-tasks` / `implement` |
| Lifecycle | NEW → UPDATE, `confidence: candidate → established`, `occurrences` | Re-scanned/refreshed by `update-ai-context` |
| Source | One finished feature's artifacts + git diff | Whole-codebase scan (pattern used 3+ times) |
| Stored in | `.claude/skills/learned/` | `./absolutpowers/patterns.md` |

If something is "how the code is shaped," it belongs in `patterns.md`. If it is
"how to carry out a class of task," it belongs in a learned skill.

## PreBoot Skill

AbsolutPowers includes one general `preboot` skill for the [PreBoot.io](https://preboot.io) library ecosystem. It is a documentation router and guardrail, not a bundled API reference.

This replaces the old per-module `preboot-*` skills. Projects using PreBoot should keep their module documentation in `./preboot-docs/`.

When the agent detects PreBoot usage, it maps the API or module to local project documentation under `./preboot-docs/`, reads the relevant file, and only then advises or implements. If the required local docs are missing, the skill stops instead of guessing the API.

Expected project documentation:

```text
preboot-docs/
├── index.md
├── preboot-core.md
├── preboot-query.md
├── preboot-securedata.md
├── preboot-eventbus.md
├── preboot-ddd.md
├── preboot-tasks.md
├── preboot-saga.md
├── preboot-files.md
├── preboot-sequence.md
└── preboot-documents-pdf.md
```

`index.md` is optional but recommended. Module files are required when the corresponding PreBoot API is used. The plugin does not create `preboot-docs/` and no longer ships per-module PreBoot reference docs.

The `preboot` skill triggers broadly on explicit PreBoot mentions, PreBoot dependencies/imports, and known APIs such as `FilterableRepository`, `SecureRepository`, `EventPublisher`, `TaskPublisher`, `@Saga`, `FileStorageService`, `SequenceApi`, and `DocumentGenerator`. Generic words like task, file, sequence, event, cache, or document require an explicit PreBoot dependency/import/API signal.

---

## Agents (Claude Code only)

Most agents are subagents that skills spawn automatically — you don't invoke them directly. Three are orchestrated by the `/triada-review` command instead of the pipeline.

| Agent | Spawned by | Purpose |
|-------|-----------|---------|
| `qa-enrichment` | feature-discuss | Analyzes planning doc and codebase, generates behavioral Acceptance Criteria |
| `review-plan` | feature-discuss | Validates planning doc completeness, feasibility, architecture |
| `review-tasks` | generate-tasks | Validates task granularity, ordering, specificity, code references |
| `implementation-worker` | implement | Implements one orchestrated phase with a fresh, narrow context |
| `phase-review` | implement | Lightweight quality gate after one orchestrated phase |
| `review-implementation` | implement | Validates code correctness, patterns, tests, safety |
| `tech-lead-advisor` | triada-review / manual | Strategic architecture guidance, technology choices, tradeoff analysis |
| `codebase-auditor` | triada-review | Deep security / correctness / test-quality review (JSON verdict) |
| `ui-reviewer` | triada-review | QA/UX review — UI states, interactions, a11y, UI races, user goal (JSON verdict) |

### Review agent criteria

**review-plan** checks: completeness, feasibility, architectural soundness, actionability, AC quality (behavioral, verifiable, complete coverage)

**review-tasks** checks: traceability to planning doc, granularity, ordering & dependencies, specificity of file paths and signatures, verification task presence, code reference accuracy, AC coverage (every AC-N traced by at least one task)

**phase-review** checks: phase write scope, completion, phase verification, handoff quality, obvious correctness issues, garbage, rules

**review-implementation** checks: correctness, patterns compliance, rules compliance, test coverage, completeness, safety (no secrets, no injection vectors), AC fulfillment (every AC-N has implementation and test)

**triada-review agents** check (non-overlapping scopes, each returns strict JSON): `tech-lead-advisor` → goal / architecture / overengineering / readability; `codebase-auditor` → security / correctness / test quality; `ui-reviewer` → UI states / interactions / data representation / a11y / UI races / user goal. All three also flag `rules.md` violations within their scope.

## Project Structure in Your Repo

After using AbsolutPowers, your project will contain:

```
your-project/
├── absolutpowers/
│   ├── feature/
│   │   ├── planning-{slug}.md      # Feature plans
│   │   ├── tasks-{slug}.md         # Implementation tasks or orchestrator index
│   │   └── tasks-{slug}/           # Phase files for larger orchestrated plans
│   │       ├── implementation-context.md
│   │       ├── 01-{phase}.md
│   │       └── 99-final-verification.md
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
# → analiza kodu → tasks doc or phase plan → review-tasks gate → PASS

/absolutpowers:implement @absolutpowers/feature/tasks-{slug}.md
# → TDD or phase workers → phase-review gates → verification → review-implementation gate → PASS

/absolutpowers:review
# → 4-phase review → report

/absolutpowers:harvest @absolutpowers/feature/tasks-{slug}.md
# → (optional, pre-commit) try-learn-skill + document-feature → review w git diff
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
| Skills | 12 workflow + 1 PreBoot | 12 workflow + tech-lead-advisor + 1 PreBoot |
| Onboarding reports | `explain` command | `explain` skill |
| Agents | 9 agents (review gates + phase worker + triada-review trio) | none |
| Slash commands | `triada-review` (multi-agent review) | Not available |
| Multi-agent review | `triada-review` (3 parallel agents + synthesis) | Not available (no parallel subagents) |
| Review gates | Automatic after each pipeline step, plus `phase-review` for orchestrated phases | Not available |
| Orchestrated implementation | Worker subagent per phase | Sequential phase files in one session |
| Skill invocation | `/absolutpowers:skill-name` | `$absolutpowers skill-name` |
| AI context | CLAUDE.md (source) | AGENTS.md (mirror) |

## Repo Structure (this repository)

```
absolut-ai-skills/
├── claude/                         # Claude Code plugin
│   ├── .claude-plugin/plugin.json
│   ├── commands/                   # triada-review slash command
│   ├── skills/                     # 12 workflow + 1 PreBoot skill
│   └── agents/                     # 9 subagent definitions
├── codex/                          # Codex plugin
│   ├── .codex-plugin/plugin.json
│   ├── skills/                     # 12 workflow + tech-lead-advisor + 1 PreBoot skill
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

## Changelog

Versioning is SemVer, kept in sync across both manifests
(`claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json`).

### 3.8.0 — Module architecture docs
- New `document-module` skill — architectural documentation of an existing module from a **code scan**: structure, public API, in/out dependencies, key flows + Mermaid **C4** diagrams (C1 Context / C2 Container / C3 Component) and sequence diagrams (both trees)
- Dual output: markdown (AI, **source of truth**) `docs/modules/{slug}-architecture.md` + self-contained HTML (human, **regenerable**, always overwritten) `docs/architecture/{slug}.html`
- Auditability: marks verified (from code) vs inferred relationships; `mermaid-cli` validation with `graph`/`flowchart` fallback
- `document-feature` and `explain` gain "vs document-module" notes; docs distinction table expanded to four mechanisms
- `harvest` wires in `document-module` as a third sub-step (`try-learn-skill` → `document-feature` → `document-module`) — auto-refreshes/creates module architecture docs, but **only for touched modules whose architecture changed** (new file / new public symbol / new cross-module import), to avoid noisy diagram churn on cosmetic edits

### 3.7.0 — Problem intake & triage
- New `problem-discuss` skill — intake/triage front door for fuzzy, multi-item client reports: decomposes into discrete items, extracts the business rule per item, investigates the code breadth-first, classifies into 6 buckets (bug / gap / config / dane / nieporozumienie / brak danych), and fans out routing to `debug` / `feature-discuss` / direct fix / close (both trees)
- Hard boundary: investigates and routes only — does not fix, plan, or write tasks
- New output dir `absolutpowers/problem/problem-{slug}.md`
- `debug` gains a "vs problem-discuss" note to keep triggers from colliding (both trees)

### 3.6.0 — Harvest phase
- New `harvest` skill — thin pre-commit closeout orchestrator: `try-learn-skill` → `document-feature`, each keeping its own gate (both trees)
- New `document-feature` skill — durable **per-module** docs (`docs/modules/{module}.md`) from planning + git diff, with file→module mapping confirm gate and intelligent merge (both trees)
- `implement` nudge reconciled `try-learn-skill` → `harvest` (single closeout entry point)
- Docs: Harvest Phase section + `document-feature` vs `update-ai-context` vs `explain` distinction

### 3.5.0 — Learned skills
- New `try-learn-skill` — extracts a reusable procedure from a finished feature into a callable learned skill under `.claude/skills/learned/`, human-gated (both trees)
- `implement` soft nudge toward skill extraction after completion

### 3.4.0 — Triada review
- `/absolutpowers:triada-review` — standalone parallel multi-agent branch review (Claude Code only)
- Epic phase-docs; `feature-discuss` inquiry mode

### 3.3.0 — Model routing
- Model routing by risk; max-requirements rule; `explain` skill migration

### 3.2.0 — QA enrichment
- Acceptance Criteria pipeline across all skills

### 3.0.0 — Orchestrated implementation
- Orchestrated `implement` (phase workers + phase-review gates); consolidated PreBoot skills

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension
- [Codex](https://github.com/openai/codex) (optional, for Codex target)

## License

MIT — [Absolut Systems](https://github.com/AbsolutSystems)
