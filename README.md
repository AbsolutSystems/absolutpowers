# AbsolutPowers

AI-assisted development lifecycle — from feature design through implementation to code review. Works with **Claude Code**, **Codex**, **Pi**, and **Grok Build** (first-class via `.grok-plugin/`).

Instead of ad-hoc prompting, AbsolutPowers gives your AI agent a structured workflow. Each skill owns one phase. Skills chain into a pipeline with automated quality gates (Claude Code) that catch problems before they cascade.

As of **5.0.0** the repo is one host-agnostic skill tree under `skills/` — not mirrored per-harness trees — plus a thin manifest/integration per harness (Claude, Codex, Pi, Grok) and a small set of skills vendored under MIT from [obra/superpowers](https://github.com/obra/superpowers) in `skills/vendored/`. Current release: **5.6.4** (native command handoff contract). See [Repo Structure](#repo-structure-this-repository) and [Attribution](#attribution).

## Quick Start

### 1. Install

Installation differs by harness. If you use more than one, install AbsolutPowers separately for each.

**Claude Code**

```bash
/plugin marketplace add AbsolutSystems/absolutpowers
/plugin install absolutpowers@absolutpowers-skills
```

Restart Claude Code, then type `/absolutpowers:` — autocomplete lists every skill. The bundled `hooks/hooks.json` `SessionStart` hook re-injects pipeline discipline (`hooks/session-context.md`) at startup, `clear`, and after `compact`.

**Codex**

Open this repo (or a project that vendors it) in Codex → repo marketplace (`.agents/plugins/marketplace.json`) → install `absolutpowers`. Codex reads `AGENTS.md` (a symlink to `CLAUDE.md`) as its bootstrap context and runs the shared `SessionStart` hook from `hooks/hooks.json`.

**Pi**

For local development, run Pi with this checkout loaded as a temporary extension source:

```bash
pi -e /path/to/absolut-ai-skills
```

`.pi/extensions/absolutpowers.ts` registers `skills/` with Pi and re-injects `hooks/session-context.md` at `session_start` and after `session_compact` — the same shared bootstrap content the Claude hook reads, never duplicated. Pi has native skill support, so no compatibility `Skill` tool is required; subagent dispatch (`pi-subagents`) is an optional companion package — see `references/pi-tools.md` for what degrades without it.

**Grok Build**

```bash
grok plugin marketplace add AbsolutSystems/absolutpowers
grok plugin install absolutpowers --trust
```

Or for local development:

```bash
grok plugin install /path/to/absolut-ai-skills --trust
```

Grok discovers `skills/` via `.grok-plugin/plugin.json`. Skills appear as `/feature-discuss`, `/generate-tasks` etc. (qualified names if needed). Grok reads `AGENTS.md` / `CLAUDE.md` for bootstrap; review gates degrade via `spawn_subagent` + `references/grok-tools.md`. See `references/grok-tools.md`.

### 2. Bootstrap project context (once)

```bash
/absolutpowers:update-ai-context
```

Creates `CLAUDE.md`, `AGENTS.md`, `absolutpowers/patterns.md`, `absolutpowers/rules.md`. Every other skill reads these.

### 3. Build a feature

```bash
/absolutpowers:feature-discuss "system powiadomień push dla użytkowników"   # WHAT  → planning doc + AC
/absolutpowers:generate-tasks absolutpowers/feature/planning-push-notifications.md  # HOW → tasks
/absolutpowers:implement absolutpowers/feature/tasks-push-notifications.md  # BUILD+TEST
/absolutpowers:review                                                        # AUDIT
/absolutpowers:ship absolutpowers/feature/tasks-push-notifications.md        # CLOSE (commit + PR text + archive artifacts)
```

Knowledge capture and side tools (`try-learn-skill`, `document-feature`, `document-module`, `receiving-code-review`, `analyze`, `qa-review`) are separate and on-demand — run them when useful, they are not pipeline gates.

Each step writes a file that feeds the next. Review gates between steps (Claude Code) catch issues automatically. Each pipeline skill ends with a **`## Terminal state`** block (what it delivered + next step / close) so `/goal` sessions keep chaining correctly.

`feature-discuss` first routes by uncertainty, risk, and whether the work needs a durable
handoff. A **Lightweight task** is the same disciplined entry point with a shorter middle:
after an explicitly accepted mini-design it executes inline in the current session, then still
requires verification and branch-level `review` or `triada-review`. It skips planning/task
artifacts, not the HARD-GATE or review.

## The Pipeline

```
feature-discuss ──→ generate-tasks ──→ implement ──→ review ──→ ship
     WHAT?              HOW?          BUILD+TEST     AUDIT      CLOSE
       │                  │               │
       ▼                  ▼               ▼
  review-plan        review-tasks   review-implementation
   (gate)              (gate)            (gate)
```

### Three entry points

Pick by how well the problem is already classified:

```
   entry ──┬─ feature-discuss   a clear NEW feature ("I want to add X")
           ├─ debug             a clear BUG (error / stack trace / test fail / CI)
           └─ problem-discuss   a FUZZY client report (many items: bug? gap? config? data? misunderstanding?)
```

**`feature-discuss` — you know you want to build something new.** A single, already-classified feature request. It routes to a risk-based Lightweight task, a standard feature, or an epic. Standard work follows discussion → planning doc + AC → tasks → implement; Lightweight work follows an accepted mini-design → inline execution → verification → branch review.

**`problem-discuss` — you have a vague report and don't yet know what each item is.** A multi-item client/stakeholder message about an *existing* module where each item could turn out to be a bug, a gap, a config error, a data anomaly, or a misunderstanding. It splits the report, classifies every item, and routes each onward (see [Client report workflow](#client-report-workflow-problem-discuss)). It investigates and routes only — never fixes or plans. **Don't reach for it** for a clean error/stack trace (that's `debug`) or a single known feature idea (that's `feature-discuss`).

`debug` branches on fix size — small fix stays inline, large fix (multi-layer / migration / public API / security boundary / shared core, or 3+ failed attempts) writes `planning-fix-{slug}.md` and routes into the pipeline so gates apply.

### On-demand tools (no gate, run anytime)

- **`review`** — solo 4-phase audit of **your own** branch before merge. Writes a report, integrates with project memory, works on every harness. Default choice for everyday code review.
- **`triada-review`** — host-agnostic multi-agent review for **larger PRs or someone else's branch** — three independent perspectives (tech-lead / security / optional UI). Claude uses registered roles; Codex, Pi, and Grok dispatch generic isolated agents with the same role prompts, or fall back to an explicitly advisory inline review.
- **`analyze`** — traceability audit, not code quality: does planning ↔ tasks ↔ code form a consistent chain? Optional after `implement` / before merge when you suspect scope creep or coverage gaps. Orthogonal to `review`/`triada-review`.
- **`qa-review`** — static, read-only test-value audit: it identifies missing scenarios, misleading tests, weak doubles, wrong test levels, and integration/E2E gaps without executing tests, measuring coverage, or editing code. It complements `review` (solo branch quality), `triada-review` (multi-perspective branch quality), and `analyze` (AC→task→code traceability); it never becomes a mandatory gate.

  ```text
  qa-review
  qa-review feature absolutpowers/feature/planning-auth.md
  qa-review codebase
  qa-review codebase skills/generate-tasks
  ```

  Empty arguments audit the current feature. An explicit feature artifact anchors intent; an empty feature with no changes or scope artifact stops without silently widening to the whole project. Whole-codebase mode discovers logical areas, audits them in module waves, and synthesizes cross-boundary risks; a path keeps local findings inside that module and labels advice requiring other modules separately. Every completed audit writes a new immutable report: feature mode uses `absolutpowers/reviews/qa-review-{feature-slug}-YYYY-MM-DD-HHmmss.md`, whole-codebase mode uses `absolutpowers/reviews/qa-review-codebase-YYYY-MM-DD-HHmmss.md`, and scoped mode uses `absolutpowers/reviews/qa-review-{module-slug}-YYYY-MM-DD-HHmmss.md`. Reports use verdict `ADEQUATE`, `IMPROVEMENTS_RECOMMENDED`, `GAPS_FOUND`, or `MISLEADING_CONFIDENCE` and expose a stable `Actionable Findings` section. Follow findings safely in this order: resolve `FEATURE_DISCUSS`, obtain explicit approval for any `INLINE_FIX`, send `GENERATE_TASKS` findings to `generate-tasks`, then re-run `qa-review`. Render executable commands in the active harness syntax; never use `@skill` as a prefix. The canonical schema and calibration remain in [`skills/qa-review/references/testing-rubric.md`](skills/qa-review/references/testing-rubric.md).
- **`tech-debt`** — static, read-only technical-debt audit for the codebase or one module. It turns evidence of architecture, complexity, duplication, coupling, reliability, test, and operability debt into a prioritized backlog with ongoing cost, confidence, bounded effort, and a smallest safe next step. It never executes code or tests, edits files, or treats an unverified dependency/security claim as fact.

  ```text
  tech-debt
  tech-debt codebase
  tech-debt path/to/module
  ```

  Every completed audit writes one immutable `absolutpowers/reviews/tech-debt-{scope}-YYYY-MM-DD-HHmmss.md` report. It is for accumulated maintainability cost, not a current-branch review (`review` / `triada-review`), deep test-value audit (`qa-review`), or active bug investigation (`debug`). Select a finding and follow its route: `FEATURE_DISCUSS`, `GENERATE_TASKS`, `DEBUG`, or `WATCH`.
- **`receiving-code-review`** — you **received** PR/review feedback (human or bot) and need to address it: verify against the codebase first, clarify unclear items, push back when wrong, implement one fix at a time. Not for *writing* a review (that's `review` / `triada-review`).
- **`explain`** — standalone HTML when a **human** needs a fast explanation of a plan or diff. Ephemeral, not durable docs.
- Also: `constitution` (ratify project principles), `try-learn-skill` / `document-feature` / `document-module` (knowledge capture).

### How gates work (Claude Code only)

After a skill produces output, a subagent reviews it:

1. Reviews against criteria specific to that step
2. Returns **PASS** or **REJECTED** — every issue tagged `[BLOCKER]` or `[WARN]`
3. REJECTED requires at least one `[BLOCKER]`; a review that finds only `[WARN]`s **passes** and lists them as non-blocking. The skill fixes blockers and resubmits (up to 3 iterations)
4. Still REJECTED after 3 → shows remaining issues, asks you

**Convergence contract:** on resubmit the skill passes the previous verdict + the fixes it applied, so the gate first accounts for each prior issue (`FIXED` / `NOT-FIXED`) and only then reports genuinely new findings (marked `[NEW]`). The verdict follows solely from `NOT-FIXED` blockers and `[NEW]` blockers — you reach PASS by clearing the reported list, not by chasing a fresh top-list each round.

Codex and Pi run without the *registered* gates — not because dispatch is unavailable (Codex has `spawn_agent`/`wait_agent`, Pi has the optional `pi-subagents` package) but because AbsolutPowers' review gates are **registered Claude Code agent types** (`agents/*.md`), and neither harness has an equivalent registry to resolve them against. Both degrade rather than skip: see `references/codex-tools.md` and `references/pi-tools.md` for how each degrades a review gate (dispatch a generic subagent fed the target `agents/{name}.md` as its prompt, or review inline with an explicit non-isolation disclaimer and an advisory verdict).

### Orchestrated implementation (Claude Code only)

For larger features, `generate-tasks` emits an orchestrated plan and `implement` becomes an orchestrator:

```
tasks-{slug}.md (index)
  ├─ implementation-worker → phase-review   (per phase, fresh narrow context)
  ├─ implementation-worker → phase-review
  ├─ final verification
  └─ review-implementation (final gate)
```

`implementation-context.md` carries only concise handoff facts between phases under a **hard budget** (≤10 lines added per phase, ≤150 lines total) — every worker pays for its size, so the orchestrator compacts it before spawning the next worker. Small features get one `tasks-{slug}.md` instead.

Tasks move `pending → in-progress → completed`. `in-progress` is an **interruption marker**: if a run dies mid-task, the next session finds it, compares declared `Create:`/`Modify:` lists against the repo, and asks whether to finish, redo, or confirm-done — instead of blindly implementing on top of partial work.

`implementation-worker` reports one of four statuses — `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED` — so the orchestrator can re-supply missing context or escalate model tier before falling back to human intervention. Every dispatch (worker, `phase-review`, `review-implementation`) names an explicit model per role (transcription/standard/most-capable for the worker, diff-scaled for `phase-review`, always most-capable for the final gate). A git-anchored `progress.md` ledger — one line per phase — makes resumption authoritative across interrupted sessions, and a generated review package (diff + status, no live `git diff`) is what reviewers actually read.

### Driving the whole pipeline under `/goal` (Claude Code only)

[`/goal`](https://code.claude.com/docs/en/goal) (Claude Code v2.1.139+) keeps one session working across turns until a completion condition holds — after each turn a small fast model checks the condition and either stops or tells Claude to keep going. It's the native way to run the AbsolutPowers pipeline unattended, from `feature-discuss` all the way to a merged feature, without prompting each step.

Each of the four pipeline skills ends with a `## Terminal state` block written as **prose**. That is deliberate and it's what makes `/goal` work: the evaluator **reads the conversation, not your files** — it can't parse a frontmatter key. The three intermediate skills state "pipeline is NOT closed — continue to the terminal skill", so a `/goal` run doesn't stop early after `generate-tasks` or `implement`; `review`/`triada-review` is the distinguished closure point where "feature delivered" first becomes true.

Practical use:

```bash
# unattended, to completion, from an interactive session
/goal feature X delivered = review PASS and branch merged to main, or stop after 25 turns

# headless, single invocation
claude -p "/goal <same condition>" --output-format stream-json --verbose
```

- **Write the condition against what Claude surfaces** — a review verdict, a build exit code, `git status` clean — not against something only a tool run would prove.
- **Bound it** with `or stop after N turns` so a stuck run terminates.
- **Pair with [auto mode](https://code.claude.com/docs/en/auto-mode-config)** for truly unattended runs — `/goal` alone doesn't change permissions, so Claude still prompts for tool calls your settings don't already allow.
- Escalation stays **in-session**: a phase that returns `BLOCKED`/`NEEDS_CONTEXT` is handled by the orchestrator within the same run — there is no cross-invocation handoff file to manage.

## Skills Reference

`all` = every harness (Claude Code, Codex, Pi, Grok — one shared `skills/{name}/SKILL.md`). `Claude` = Claude Code only (registered agent types and/or parallel subagent dispatch).

**17 workflow skills + `preboot`** in the shared tree (plus vendored helpers under `skills/vendored/`, not counted as pipeline skills).

| Skill | What it does | In → Out | Harnesses |
|---|---|---|---|
| `feature-discuss` | PO/architect Q&A → planning doc + Acceptance Criteria | idea → `planning-{slug}.md` | all |
| `generate-tasks` | Planning doc → sequential tasks or orchestrated phase plan | `planning-*.md` → `tasks-{slug}.md` (+ phase dir) | all |
| `implement` | Executes tasks per `Test-first:` marker, marks `completed` in-place | `tasks-*.md` → code + tests | all |
| `review` | 4-phase code-quality audit (semantic / edge / rules / GC) | branch → `reviews/YYYY-MM-DD-{branch}.md` | all |
| `ship` | Commit message + PR description from artifacts, archives feature artifacts, local commit (gated) | `tasks-*.md` + diff → conventional commit + PR text + `archives/{slug}/` | all |
| `debug` | Root-cause first, then size the fix (inline vs hand-off) | bug desc → fix or `planning-fix-{slug}.md` | all |
| `problem-discuss` | Triage fuzzy multi-item client report: split, classify, route | report → `problem/problem-{slug}.md` | all |
| `analyze` | Cross-artifact audit: AC→task→code matrix, 6 divergence classes | slug → `reviews/analyze-{slug}.md` | all |
| `triada-review` | Multi-agent branch review + synthesis with per-harness dispatch | branch → report in session | all |
| `qa-review` | Static test-value audit for a feature, module, or whole codebase | scope → immutable `reviews/qa-review-{scope}-{timestamp}.md` | all |
| `tech-debt` | Static prioritized technical-debt audit for the codebase or a module | scope → immutable `reviews/tech-debt-{scope}-{timestamp}.md` | all |
| `constitution` | Author/ratify project principles (pryncypia) | topic → `constitution.md` | all |
| `update-ai-context` | Bootstrap/refresh `CLAUDE.md`, `AGENTS.md`, `patterns.md`, `rules.md` | path → context files | all |
| `explain` | Standalone HTML onboarding report for a plan or diff | path/diff → `docs/onboarding/*.html` | all |
| `try-learn-skill` | Scan whole codebase for repeated (≥3×, `file:line`) non-obvious procedures → invocable learned-skills (batch approval) | codebase → learned path **per harness** (see below) | all |
| `receiving-code-review` | Address PR/review feedback with verify-first rigor (not blind agreement) | review comments → fixes or reasoned pushback | all |
| `document-feature` | Per-module prose docs from planning + diff (intelligent merge) | `tasks-*.md` → `docs/modules/{module}.md` | all |
| `document-module` | Architecture docs from a code scan + C4 diagrams | module → `docs/modules/{slug}-architecture.md` + HTML | all |
| `preboot` | Doc router / guardrail for the PreBoot.io library ecosystem | PreBoot usage → reads `./preboot-docs/` | all |

**Learned-skill output paths** (`try-learn-skill` picks one from session harness):

| Harness | Path in the **target** project |
|---------|--------------------------------|
| Claude Code | `.claude/skills/learned/{name}/SKILL.md` |
| Codex | `.agents/skills/learned/{name}/SKILL.md` |
| Grok | `.grok/skills/learned/{name}/SKILL.md` |
| Pi | `.pi/skills/learned/{name}/SKILL.md` |

Cards below cover the four pipeline skills plus `try-learn-skill`, `ship`, and `receiving-code-review`. The rest behave as the table describes.

---

### `/absolutpowers:feature-discuss`

Interactive Product Owner / Product Architect session — discusses requirements before any code is written. Asks clarifying questions one at a time, analyzes your codebase, and proposes 2-3 approaches with tradeoffs. It then routes an accepted design to Lightweight inline execution, a standard planning doc with behavioral Acceptance Criteria and `review-plan`, or an epic roadmap with per-phase planning. Reads the scoped project context before routing.

- **When:** starting a feature, brainstorming, "chcę dodać…", "potrzebujemy…"
- **In → Out:** feature description → accepted Lightweight mini-design + inline work, standard `absolutpowers/feature/planning-{slug}.md`, or epic `planning-main.md` + phase docs (with an ADR when required)
- **Lightweight task:** one cohesive goal using an existing pattern, with no unresolved product decision or high-risk boundary, that can finish safely in the current session. Qualification is based on risk, uncertainty, and handoff needs regardless of file count. Before proposing its mini-design, the skill reads a scoped context pack (nearest `AGENTS.md`/`CLAUDE.md`, constitution, patterns, rules, relevant ADRs, active path-overlapping project memory, and current code); a missing optional source is skipped without error.
- **Planning guardrails:** surface assumptions; ask for a decision only when uncertainty changes the contract, data, security, migration, scope, or cost; otherwise record the minimal assumption. Recommend the smallest viable approach, record tempting exclusions under `Deliberately not doing`, and keep every plan step traceable to scope, acceptance criteria, or a necessary accompanying change. Under the **boy-scout rule**, a real adjacent problem spotted during analysis is named and offered to the user (include / follow-up / skip) rather than silently dropped.
- After explicit acceptance of the complete mini-design (the same **HARD-GATE**), in-scope implementation runs **inline** with a session-only task list. It creates no planning/tasks doc and skips QA enrichment, `review-plan`, `generate-tasks`, and `implement`, but must finish with the promised verification and branch-level `review` or `triada-review`.
- Escalate to a standard feature or epic when the area or solution is uncertain, or work involves migration, a public API/public contract, a security boundary, multiple subsystems, or durable resume/handoff. **Epics** split into a main planning document (default name `planning-main.md`) + per-phase docs in a `feature/{epic-slug}/` subfolder; downstream skills preserve its exact referenced path instead of reconstructing the filename (next step = plan each phase in a new session, not `generate-tasks` on the main).
- For a standard/phase `review-plan: PASS` and for an epic main roadmap, Explain HTML is **opt-in** and generated only after an affirmative answer. `skip` does not generate a report or link, is not a warning, and does not block the next step; no response does not generate Explain automatically.
- **Gap handoff (Mode C):** hand it a `problem-{slug}.md` from `problem-discuss` (item classified as a gap) and it inherits the confirmed evidence — business rule, what's missing, where — instead of re-interviewing from zero. It designs only *how* to fill the gap and stamps `**Źródło:** problem-{slug}.md, Sprawa N` for traceability.
- Optional **Visual Companion** (browser mockups/options) after explicit approval — see `skills/feature-discuss/visual-companion.md`.

```bash
/absolutpowers:feature-discuss "eksport danych użytkowników do CSV z filtrowaniem"
```

> **Intent matters:** the feature's goal MUST be written into the planning doc explicitly — the downstream Intent Fidelity check (review-tasks) judges intent only from the written plan, not from the discussion.

---

### `/absolutpowers:generate-tasks`

Reads a planning doc (or a review report, or a `planning-fix-` doc from `debug`) and produces a step-by-step plan for an AI agent: exact paths, signatures, tests, plus `Traces to: AC-N` traceability. Sets a **`Test-first:` marker** (`yes` / `no + reason`) on every task at generation time — the planner owns the TDD decision, not the implementer mid-flight — and embeds the literal `AC-N` token in the planned test names of AC-traced tasks so fulfillment is grep-verifiable, not judged. Picks `single-file` mode (small) or `orchestrated` mode (phase files + `implementation-context.md` + final verification). Reads `constitution.md` as binding context and weaves **active `project-memory.md` traps** whose paths overlap a task into that task's Requirements (routes around known traps by construction). Runs the `review-tasks` gate.

- **When:** after `feature-discuss`, or after `review` finds 3+ issues
- **In → Out:** path to a planning doc / review report → `absolutpowers/feature/tasks-{slug}.md` (+ `tasks-{slug}/` for larger features)

```bash
/absolutpowers:generate-tasks absolutpowers/feature/planning-push-notifications.md
/absolutpowers:generate-tasks absolutpowers/reviews/2026-04-21-feature-auth.md   # review → fix tasks
```

---

### `/absolutpowers:implement`

Senior engineer executing tasks sequentially, following each task's `Test-first:` marker (write-tests-first + red run for `yes`, direct implement for `no`; legacy docs without the marker fall back to judgment; see also `references/tdd-anti-patterns.md`). Embeds the `AC-N` token in tests covering a traced AC; AC fulfillment is then determined by grepping test sources for that token, and a traced AC with **no** token-matched test (`NOT VERIFIED (untested)`) blocks completion. Marks a task `in-progress` before touching code and `completed` only after verification (interruption-safe). For epic phases it resolves the exact referenced parent planning document regardless of filename and persists phase state across sessions. After the implementation gate it aggregates every `Implementation Decisions / Remarks` entry into a versioned HTML report; non-empty remarks create a durable human-acceptance checkpoint before the phase becomes `Zrobiona`. Orchestrated plans → `implementation-worker` per phase + `phase-review` (Claude); other harnesses degrade via `references/harness-dispatch.md`. Under the **boy-scout rule**, trivial one-liners are fixed inline while larger out-of-scope findings are logged to `scout-findings.md` and reviewed by the orchestrator at Step O5.7 (routing a separate concern to its own `feature-discuss`). Respects `constitution.md`. Can create ADRs and memory candidates (`references/project-memory.md`).

- **When:** after `generate-tasks`
- **In → Out:** path to a tasks file → implementation code + tests, updated tasks file
- **After PASS:** next is `review` / `triada-review`. A standalone feature or final epic phase can then go through optional `analyze` and `ship`; an epic with remaining phases instead gets a state-aware handoff to the next phase (`feature-discuss` / `generate-tasks` / `implement`) and defers epic closeout. Render executable commands in the active harness syntax; never use `@skill` as a prefix.

```bash
/absolutpowers:implement absolutpowers/feature/tasks-push-notifications.md
```

---

### `/absolutpowers:review`

Full 4-phase code review of current-branch changes. Always runs all phases.

| Phase | Focus |
|---|---|
| 1. Semantic | behavior change, blast radius, architectural decisions |
| 2. Edge cases | null, empty, off-by-one, races, missing error handling |
| 3. Rules | compliance with `absolutpowers/rules.md` + `constitution.md` violations |
| 4. Garbage | dead imports, debug logs, commented code, stale TODOs |

- **When:** before merge, PR ready, "sprawdź kod", "is this ready"
- **In → Out:** optional base branch (default `main`) → `absolutpowers/reviews/YYYY-MM-DD-{branch-slug}.md`
- **Follow-up:** 0-2 issues → fix manually; 3+ → suggests `generate-tasks` on the report

```bash
/absolutpowers:review            # vs main
/absolutpowers:review develop    # vs develop
```

**review vs triada-review vs analyze:** `review` = solo 4-phase code-quality audit and writes a report. `triada-review` = multi-agent code-quality review for larger PRs, using the native dispatch primitive of each harness. `analyze` = traceability audit (planning↔tasks↔code), not code quality. Orthogonal — safe to run all three.

---

### `/absolutpowers:try-learn-skill`

Ad-hoc, on-demand knowledge capture — **not a pipeline step**. Scans the whole codebase (optional path narrows the scope; optional threshold, default N=3) for **repeated, non-obvious procedures** and proposes them as invocable project learned-skills. Its signal is codebase-wide repetition, not a single feature's artifacts — which is what keeps it from producing one-off skills.

Two hard gates before anything is proposed: **repetition** (a procedural pattern must occur ≥N times with concrete `file:line` evidence) and **non-obviousness** (≥2 steps survive noun-substitution — knowledge the agent wouldn't have on its own). Survivors are shown as a **batch** of candidates; you tick which to keep, and only those are written (human gate, no silent writes). Nothing meeting the bar → it reports that and writes nothing.

**Write path depends on harness** (target project, not the AbsolutPowers repo):

| Harness | Learned skills live under |
|---------|---------------------------|
| Claude Code | `.claude/skills/learned/` |
| Codex | `.agents/skills/learned/` |
| Grok | `.grok/skills/learned/` |
| Pi | `.pi/skills/learned/` |

Boundary vs `update-ai-context`: that skill produces **passive documentation** (`patterns.md`/`rules.md`/`CLAUDE.md`); `try-learn-skill` produces **active, invocable procedures**.

- **When:** whenever you want to mine the project for reusable procedures — deliberately, not tied to a feature
- **In → Out:** codebase (optional scope) → selected `{harness}/skills/learned/{name}/SKILL.md`

```bash
/absolutpowers:try-learn-skill                 # scan whole codebase
/absolutpowers:try-learn-skill src/payments/   # narrow the scan
```

---

### `/absolutpowers:receiving-code-review`

Handle **incoming** code review feedback (human partner, external reviewer, or bot) with technical rigor — not performative agreement and not blind implementation.

```
READ → UNDERSTAND → VERIFY against this codebase → EVALUATE → RESPOND → IMPLEMENT (one item at a time)
```

- **When:** PR comments to address, "fix review feedback", bot review (e.g. CodeRabbit), unclear multi-item lists
- **Hard rules:** clarify unclear items **before** coding; push back with evidence when the suggestion is wrong for this stack / YAGNI / conflicts with ADR or constitution; no empty "thanks you're right" theater
- **Not for:** writing a full branch review (`review` / `triada-review`) or turning a large structured report into tasks (`generate-tasks` on the review file)
- **In → Out:** PR URL / pasted comments → verified fixes (or reasoned pushback)

```bash
/absolutpowers:receiving-code-review 123
/absolutpowers:receiving-code-review "1) … 2) … from the PR thread"
```

---

### `/absolutpowers:ship`

Feature closeout — turns the pipeline artifacts (planning = intent, tasks = scope, AC = verification, diff = truth) into a **conventional-commit message and a PR description** so you don't hand-write them or reverse-engineer them from the diff. With approval it **archives the feature's artifacts** (`planning-*.md`/`tasks-*.md` → `absolutpowers/archives/{slug}/` + a `summary.md`, folded into the closing commit) and makes the **local commit**. Autodetects the feature slug from the branch across `feature/` and `archives/`.

- **When:** after `review`, changes ready to commit
- **In → Out:** path to a `tasks-*.md` (or branch autodetect) + `git diff` → commit message + PR text, optional local commit
- **Hard boundary:** never changes code or task statuses, never pushes, never opens a PR on its own (`gh pr create` only on explicit request, after `gh auth status`), never creates issues. Nothing is staged or committed before the human gate.

```bash
/absolutpowers:ship absolutpowers/feature/tasks-push-notifications.md
/absolutpowers:ship            # autodetect slug from current branch
```

## Situation → skill

Start from where you are, not from the skill list.

| You have… | Start with | Why |
|---|---|---|
| A new project with no `CLAUDE.md` | `update-ai-context` | Generates the AI context every other skill reads |
| An idea for a new feature | `feature-discuss` | PO/architect discussion → planning doc + AC |
| A planning doc | `generate-tasks` | Breaks the plan into sequential tasks |
| A tasks doc | `implement` | Executes tasks (TDD), with gates |
| A clear bug (error / stack trace / test fail) | `debug` | Root cause before any fix |
| A fuzzy, multi-item client report | `problem-discuss` | Triage: split, classify, route per item |
| A branch ready to merge | `review` (solo) / `triada-review` (multi-agent) | Code-quality audit |
| Doubt: "is the feature consistent / any scope creep?" | `analyze` | AC→task→code traceability audit |
| Want to prioritize accumulated maintainability cost | `tech-debt` | Evidence-backed technical-debt backlog |
| Changes ready to commit (feature closeout) | `ship` | Commit message + PR text from artifacts, archives artifacts, local commit (gated) |
| Want reusable procedures mined from the project | `try-learn-skill` | Codebase scan → invocable project learned-skills (ad-hoc) |
| PR/review comments to address (not write the review) | `receiving-code-review` | Verify → fix or push back, one item at a time |
| A change/plan to explain to a human | `explain` | Standalone HTML report |
| The need to set project principles | `constitution` | Ratifies `constitution.md` (opt-in) |

### Client report workflow (problem-discuss)

A fuzzy, multi-item report doesn't enter the pipeline directly — `problem-discuss` splits it into discrete items, extracts the intended business rule per item, investigates the code breadth-first with `file:line` evidence, classifies each item, and routes it. It **investigates and routes only** — never fixes, plans, or writes tasks. Output: `absolutpowers/problem/problem-{slug}.md`.

```
problem-discuss (fuzzy report → split into items → classify per item → route)
  ├─ confirmed bug        → debug (reads problem-{slug}.md as starting evidence)
  ├─ gap (not built)      → feature-discuss → generate-tasks → implement
  ├─ config / env error   → direct fix
  ├─ data anomaly         → data fix
  ├─ works-as-designed    → close + explain to client
  └─ not enough data      → ask client
```

| Bucket | Route |
|---|---|
| potwierdzony bug | `debug` |
| nie zaimplementowane (gap) | `feature-discuss` |
| błąd konfiguracji / env | fix bezpośredni |
| anomalia danych | fix danych |
| działa-jak-zaprojektowano (nieporozumienie) | close + wyjaśnienie klientowi |
| za mało danych | dopytaj klienta |

**Use it when:** a client/stakeholder sends a multi-item report about an existing module ("po akceptacji korekty powinny wyjść maile, w produkcji ich nie widzę", a list of production remarks, a rule↔behavior discrepancy). **Not** for a clean error/stack trace/test failure (that's `debug`) or a new feature request (that's `feature-discuss`).

```bash
/absolutpowers:problem-discuss "Klient zgłosił: 1) dlaczego user X dostaje maile (obraz.png), 2) po korekcie nie widzę 2 maili (culinar1.pdf)"
# then, for a confirmed-bug item:
/absolutpowers:debug absolutpowers/problem/problem-slug.md "Sprawa 2"
```

## Key Concepts

### Constitution vs rules — never merge

Two files, two purposes:

| File | Content | Author |
|---|---|---|
| `absolutpowers/constitution.md` | Pryncypia/osąd — ratified principles, values, hard limits (semver + ratification date + changelog) | `constitution` skill (human-driven session) |
| `absolutpowers/rules.md` | Mechanika/lint — formatting, naming, forbidden patterns, required libraries | `update-ai-context` (code scan) |

`constitution.md` shapes judgement (*should we?*); `rules.md` enforces mechanics (*did we follow the convention?*). It is **not a precondition** — the pipeline runs without it. When present: binding context for `generate-tasks`/`implement`, reported in `review` Faza 3. When absent: every consumer silently skips it.

### Four documentation mechanisms — deliberately different

| | `document-feature` | `document-module` | `update-ai-context` | `explain` |
|---|---|---|---|---|
| Captures | Deep **per-module** prose from planning + diff | **Architecture** of a module from a code scan (C4) | Broad/shallow `CLAUDE.md` from a code scan | Ephemeral single-change human onboarding |
| Source | One feature's planning (why) + git diff (truth) | One module's code (scan, as-is) | Whole-codebase structural scan | A plan/tasks doc or current git diff |
| Output | `docs/modules/{module}.md` (durable) | `docs/modules/{slug}-architecture.md` (md, truth) + `.html` (regenerable) | `CLAUDE.md` / `AGENTS.md` (auto-injected) | `docs/onboarding/*.html` (ephemeral) |
| Audience | AI agent as new dev | Human (HTML) + AI as new dev (md) | Every skill's auto-loaded context | A human |

### Learned skills vs `patterns.md`

Learned skills are project-local callable procedures extracted by `try-learn-skill` into the **harness-specific** learned root (`.claude/skills/learned/`, `.agents/skills/learned/`, `.grok/skills/learned/`, or `.pi/skills/learned/`). The bar is deliberately high: scan the **whole codebase** (ad-hoc, not per-feature); a procedure qualifies only when it recurs **≥3 times with `file:line` evidence** AND encodes **≥2 non-obvious steps** (surviving noun-substitution). Survivors are proposed as a batch; only user-approved ones are written (human gate). They differ from `patterns.md`:

| | Learned skill | `patterns.md` |
|---|---|---|
| Captures | A **procedure** (steps/tools/decisions) | **Code structure** (recurring conventions) |
| Form | Callable `SKILL.md` with narrow `TRIGGER when:` | Descriptive reference, read by generate-tasks / implement |
| Lifecycle | Codebase scan → candidates meeting ≥3 occurrences + ≥2 non-obvious steps → batch approval → written on user tick | Re-scanned by `update-ai-context` |
| Source | Whole-codebase scan (procedure recurs ≥3×, `file:line` evidence) | Whole-codebase scan (structural convention used 3+ times) |

"How the code is shaped" → `patterns.md`. "How to carry out a class of task" → learned skill.

### Project memory

Skills discover durable lessons (recurring traps, non-obvious workarounds, failure patterns) and capture them as candidates in `absolutpowers/memory-candidates/`. Promotion to `absolutpowers/project-memory.md` requires your explicit approval; the candidate is then deleted. One-off notes, branch status, and facts that belong in `patterns.md`/`rules.md`/ADRs do **not** belong in project memory.

Formats, promotion rules, and "write the lesson generally" guidance are shared in **`references/project-memory.md`** (used by `debug`, `review`, `implement`, `problem-discuss`) so skills do not drift.

### PreBoot skill

One general `preboot` skill for the [PreBoot.io](https://preboot.io) ecosystem — a documentation router and guardrail, not a bundled reference. On detecting PreBoot usage it maps the API/module to local docs under `./preboot-docs/`, reads the relevant file, then advises. If the local docs are missing it **stops** instead of guessing the API. Triggers on explicit PreBoot mentions, dependencies/imports, and known APIs (`FilterableRepository`, `SecureRepository`, `EventPublisher`, `TaskPublisher`, `@Saga`, `FileStorageService`, `SequenceApi`, `DocumentGenerator`); generic words (task, file, event…) require an explicit PreBoot signal.

Expected project docs:

```text
preboot-docs/
├── index.md            (optional)
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

## Agent role prompts

Claude Code registers these files as named agent types. Codex, Pi, and Grok reuse the
same bodies as prompts for generic subagents. Most are dispatched automatically; three
role prompts are orchestrated by the shared `triada-review` skill.

| Agent | Spawned by | Purpose |
|---|---|---|
| `qa-enrichment` | feature-discuss | Generates behavioral Acceptance Criteria |
| `review-plan` | feature-discuss | Validates planning completeness, feasibility, architecture, AC quality |
| `review-tasks` | generate-tasks | Validates traceability, granularity, ordering, specificity, AC coverage, `Test-first:` markers, AC-token tests, **Intent Fidelity** |
| `implementation-worker` | implement | Implements one orchestrated phase with a fresh, narrow context |
| `phase-review` | implement | Lightweight gate after one orchestrated phase |
| `review-implementation` | implement | Validates correctness, patterns, rules, tests, safety, `Test-first:` adherence, AC fulfillment (token-grep) |
| `tech-lead-advisor` | triada-review / manual | Goal, architecture, overengineering, readability |
| `codebase-auditor` | triada-review | Security, correctness, test quality (JSON verdict) |
| `ui-reviewer` | triada-review | UI states, interactions, a11y, data, UI races, user goal (JSON verdict) |
| `tech-debt-auditor` | tech-debt | Isolated static audit of one codebase area; returns debt evidence for synthesis |

**Intent Fidelity** (review-tasks #7, `INTENT` category, Claude-only): judges whether the task set as a whole achieves the goal/intent of the planning doc — not just literal per-requirement coverage. Complements `analyze` (in-flight gate vs post-hoc audit). The three triada-review agents have non-overlapping scopes and each also flags `rules.md` violations within its scope.

## Platform Differences

Every harness shares the exact same `skills/{name}/SKILL.md` — **16 workflow skills + `preboot`**, plus `skills/vendored/` (not user-facing pipeline skills). What differs is the thin per-harness layer on top:

| Feature | Claude Code | Codex | Pi | Grok Build |
|---|---|---|---|---|
| Skills | 16 workflow + 1 PreBoot (shared tree) | same shared tree | same shared tree | same shared tree |
| Registered agent types | 9 (`agents/*.md`: review gates + phase worker + triada trio) | none — no plugin-level agent-type registry | none — no plugin-level agent-type registry | none (uses `spawn_subagent` + `subagent_type` + personas) |
| Subagent dispatch primitive | `Agent(subagent_type=...)` against a registered type | available (`multi_agent=true` → `spawn_agent`/`wait_agent`), but nothing registered to dispatch *to* for gates | available via optional `pi-subagents` package | `spawn_subagent` (with `subagent_type: "general-purpose"` etc.) |
| Multi-agent review | shared `triada-review`: parallel registered agents | shared `triada-review`: parallel generic `spawn_agent` | shared `triada-review`: `pi-subagents` when installed, otherwise inline advisory | shared `triada-review`: parallel generic `spawn_subagent` |
| Review gates | automatic after each step + `phase-review` | degrades: dispatch a generic subagent fed `agents/{name}.md`, or review inline (non-isolation disclaimer + advisory verdict) — see `references/codex-tools.md` | degrades: dispatch a generic subagent fed `agents/{name}.md`, or review inline (non-isolation disclaimer) — see `references/pi-tools.md` | degrades: `spawn_subagent` (general-purpose) with `agents/{name}.md` body, or inline advisory — see `references/grok-tools.md` |
| Orchestrated implementation | worker subagent per phase | generic `spawn_agent` worker per phase with explicit 5.6 routing; sequential fallback without dispatch | sequential phase files in one session (or dispatched via `pi-subagents` if installed) | sequential or via `spawn_subagent` per phase (see grok-tools) |
| Skill invocation | `/absolutpowers:skill-name` | `$absolutpowers skill-name` | native Pi skill invocation / `read` the `SKILL.md` | `/feature-discuss`, `/generate-tasks` etc. (plugin-qualified if needed) |
| Session bootstrap | `hooks/hooks.json` `SessionStart` hook reads `hooks/session-context.md` | `AGENTS.md` (symlink to `CLAUDE.md`) plus shared `hooks/hooks.json` `SessionStart` hook | `.pi/extensions/absolutpowers.ts` reads `hooks/session-context.md` at `session_start`/`session_compact` | reads `AGENTS.md` / `CLAUDE.md`; hooks via `.grok/hooks/` or compat; session-context via reference |
| AI context | `CLAUDE.md` (source) | `AGENTS.md` (symlink to `CLAUDE.md`, not a generated mirror) | `CLAUDE.md` (via the extension's injected context) | `AGENTS.md` / `CLAUDE.md` (primary) |

For Codex orchestrated implementation, the shared Claude tiers are translated explicitly:
`haiku` → `gpt-5.6-luna`/`medium`, `sonnet` → `gpt-5.6-luna`/`high`, and `opus` →
`gpt-5.6-terra`/`high`. The final implementation review uses Sol with `high`; reserve
`xhigh` for an explicit escalation when the failure cost justifies the extra reasoning-token
usage;
Codex should not silently hand off implementation to `gpt-5.5`.

## Project Structure (in your repo)

```
your-project/
├── absolutpowers/
│   ├── feature/
│   │   ├── planning-{slug}.md          # Feature plans
│   │   ├── planning-fix-{slug}.md      # Large root-cause fix plans (from debug)
│   │   ├── tasks-{slug}.md             # Tasks or orchestrator index
│   │   └── tasks-{slug}/               # Phase files for orchestrated plans
│   │       ├── implementation-context.md
│   │       ├── 01-{phase}.md
│   │       └── 99-final-verification.md
│   ├── reviews/
│   │   ├── YYYY-MM-DD-{branch}.md      # Code review reports
│   │   └── analyze-{slug}.md           # Cross-artifact audit reports
│   ├── archives/{slug}/                # Archived planning/tasks + summary.md (from ship)
│   ├── memory-candidates/              # Proposed durable lessons (approval queue)
│   ├── problem/problem-{slug}.md       # Problem triage reports
│   ├── project-memory.md               # Approved operational memory
│   ├── patterns.md                     # Discovered code patterns
│   ├── rules.md                        # Mechanical lint rules (code-derived)
│   └── constitution.md                 # Ratified principles / pryncypia (≠ rules.md)
├── docs/adr/YYYY-MM-DD-{slug}.md        # Architecture Decision Records
├── CLAUDE.md                            # AI context (Claude Code)
└── AGENTS.md                            # AI context mirror (Codex), generated by update-ai-context
```

Recommended `.gitignore` — keep planning docs and reviews (they're documentation), exclude the approval queue:

```gitignore
absolutpowers/memory-candidates/
```

## Repo Structure (this repository)

Since 5.0.0 there is **one** host-agnostic skill tree — no `claude/`/`codex/` mirrors, no
sync scripts, no drift-detection script. Each harness (Claude, Codex, Pi, Grok) gets a thin
manifest/integration on top of the same `skills/` (the obra/superpowers pattern):

```
absolut-ai-skills/
├── skills/                            # single source of truth (all harnesses)
│   ├── {name}/
│   │   ├── SKILL.md                   # 16 workflow skills + preboot (host-agnostic body;
│   │   │                              # Claude-only frontmatter/gate sections inert elsewhere)
│   │   └── references/                # optional large templates (formats, orchestrated steps)
│   │                                  # e.g. feature-discuss, generate-tasks, implement
│   └── vendored/                      # obra/superpowers (MIT) — see VENDORED.md + fork-policy.md
│       ├── using-git-worktrees/
│       ├── systematic-debugging/      # library; canonical process = skills/debug
│       ├── verification-before-completion/
│       ├── dispatching-parallel-agents/
│       ├── finishing-a-development-branch/  # prefer ship for AbsolutPowers closeout
│       ├── executing-plans/
│       └── subagent-driven-development/
├── agents/                            # 9 role prompts; registered by Claude, reused as prompts elsewhere
├── references/                        # shared contracts + per-harness mappings
│   ├── codex-tools.md                 # Codex dispatch + gate degradation
│   ├── pi-tools.md
│   ├── grok-tools.md
│   ├── harness-dispatch.md            # Claude / Codex / Pi / Grok gate-worker dispatch
│   ├── project-memory.md              # shared memory capture contract
│   ├── tdd-anti-patterns.md
│   └── fork-policy.md                 # which copy is canonical when dual assets exist
├── hooks/                             # shared Claude/Codex SessionStart hook
│   ├── hooks.json
│   ├── run-hook.cmd
│   ├── session-start
│   └── session-context.md             # pipeline + skill map + guardians (also Pi bootstrap)
├── .pi/extensions/absolutpowers.ts
├── .claude-plugin/plugin.json
├── .claude-plugin/marketplace.json
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json
├── .grok-plugin/plugin.json
├── AGENTS.md                          # symlink → CLAUDE.md (Codex bootstrap)
├── VENDORED.md
├── LICENSE-VENDORED
├── docs/
└── README.md
```

Adding a harness costs a new integration + optional `references/{harness}-tools.md` — zero
skill edits. Shared contracts (memory, dispatch, fork policy) live under `references/` so skills
stay thinner. See `CLAUDE.md` → "Adding a New Harness" and "Attribution" below.

## Updating

```bash
# Claude Code
/plugin install absolutpowers@absolutpowers-skills

# Codex — pull the repo and reinstall from the local marketplace

# Pi — re-run with the checkout loaded, or reinstall the package if published
pi -e /path/to/absolut-ai-skills

# Grok Build
grok plugin update absolutpowers
# or for local checkout
grok plugin install /path/to/absolut-ai-skills --trust
```

## Changelog

Versioning is SemVer, kept in sync across all manifests
(`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.grok-plugin/plugin.json`).

### 5.7.0 — Boy-scout rule + findings ledger

- Loosened the strict surgical-scope guardrail toward "leave code better than found": a strictly trivial one-liner (typo, dead/missing import, obvious null-check) is fixed inline; anything larger is named (`file:line`) and raised to the user instead of silently fixed or ignored
- Dropped the "did my part, the errors aren't mine" sign-off: `implement`/worker now separate own vs pre-existing build/test failures and offer to fix
- Added `scout-findings.md`, a tracked orchestrated ledger: headless workers append out-of-scope findings, and the orchestrator reviews them once at new **Step O5.7**, routing each (inline fix / `generate-tasks` / a separate `feature-discuss` / `debug` / defer / dismiss) without folding a separate concern into the current change
- Applies to `feature-discuss` (planning), `implement` + `implementation-worker`, and `debug`; `review` stays read-only
- Version **5.7.0** across all plugin manifests

### 5.6.4 — Native command handoff contract

- Added one shared contract for standalone, copy-pasteable next-step commands in each harness's native syntax
- Fixed bare skill names, prose-only handoffs, and legacy `@skill @path` examples across canonical skills and active references
- Added regression coverage for command handoffs and audited all routing skills
- Version **5.6.4** across all plugin manifests

### 5.6.3 — Shared Claude/Codex SessionStart hook

- Made the SessionStart hook work in both Claude Code and Codex using the appropriate plugin-root environment variable
- Added `resume` handling for Codex session restarts
- Version **5.6.3** across all plugin manifests

### 5.6.2 — Harness syntax and Codex model routing

- Documented native next-step command syntax per harness; `@skill` is never an executable command prefix
- Added explicit Codex 5.6 routing: Luna `medium`/`high` for mechanical/standard work, Terra `high` for high-risk work, and Sol `high` for the final implementation review
- Reserved `xhigh` for explicit escalation instead of using it as the default reasoning level
- Version **5.6.2** across all plugin manifests

### 5.6.1 — Feature-planning guardrails

- Added an explicit `feature-discuss` planning filter: disclose material assumptions and tradeoffs, prefer the minimum viable solution, and keep planned changes surgical
- Added `Deliberately not doing`, assumptions, and decision-to-confirm sections to standard and phase planning templates
- Version **5.6.1** across all plugin manifests

### 5.6.0 — Technical Debt Audit

- Added `tech-debt`, an on-demand, static, read-only audit for a whole codebase or a scoped module
- Added evidence-backed prioritization by ongoing cost, impact, confidence, bounded effort, and smallest safe next step, written as immutable `tech-debt-*.md` reports
- Added the isolated `tech-debt-auditor` worker and host-agnostic generic-dispatch fallback for Codex, Pi, and Grok
- Version **5.6.0** across all plugin manifests

### 5.5.0 — Lightweight task routing

- Generalized the `feature-discuss` fast path into a risk- and uncertainty-based **Lightweight task** route that may span several files while retaining one cohesive, session-completable goal
- Added scoped context-pack loading, explicit mini-design acceptance, and session-only task tracking; risky, unclear, cross-system, or durable-handoff work escalates to standard/epic
- Kept lightweight execution inline while requiring verification and branch review, without creating planning/tasks artifacts or invoking the standard execution stages
- Made Explain HTML affirmative opt-in after standard/phase review PASS and epic-main creation; `skip` and no response do not generate or block
- Added static prompt, documentation, and release contract tests and synchronized version **5.5.0** across all plugin manifests

### 5.4.0 — Static QA Review

- Added `qa-review`, an on-demand read-only audit of test value for the current feature, an explicit artifact, a module path, or the whole codebase
- Added the canonical testing rubric and isolated `qa-reviewer` worker, with parallel module waves and explicit sequential/inline reduced-isolation fallback across harnesses
- Added stable immutable reports and safe `FEATURE_DISCUSS` → approved `INLINE_FIX` → `GENERATE_TASKS` → re-audit routing
- Added optional post-implementation QA-review guidance for elevated test-risk signals; QA review remains outside the mandatory review pipeline
- Version **5.4.0** across all plugin manifests

### 5.3.0 — Host-agnostic Triada Review
- Promoted `triada-review` from a Claude-only command to `skills/triada-review/SKILL.md`, shared by Claude Code, Codex, Pi, and Grok
- Removed the legacy `commands/triada-review.md`; Claude invokes the shared plugin skill directly, leaving one discovery surface and one source of truth
- Added explicit role-prompt dispatch for harnesses without an agent registry: Codex `spawn_agent`, Grok `spawn_subagent`, Pi `pi-subagents`; inline execution is an advisory last resort
- Added canonical `.absolutpowers/triada-review.agents.json` config path with backward-compatible `.claude/triada-review.agents.json` fallback
- Version **5.3.0** across all plugin manifests

### 5.2.0 — Tech-lead skill audit: contracts, modularization, multi-harness hygiene
- **Contract hygiene:** removed stale `codex/` mirror notes (single-tree era); `feature-discuss` Terminal state branches **standard / epic main / micro-change** (micro-change skips `generate-tasks`); `NIE wyzwalaj` on core skills; Terminal state on `problem-discuss`, `debug`, `analyze`
- **Shared references:** `references/project-memory.md`, `harness-dispatch.md`, `tdd-anti-patterns.md`, `fork-policy.md`; large templates extracted to `skills/{name}/references/` (`feature-discuss`, `generate-tasks`, `implement`) so main `SKILL.md` files stay operable mid-context
- **Canonical paths:** session auto-trigger is **`debug` only** (not vendored `systematic-debugging`); vendored `finishing-a-development-branch` banners to prefer **`ship`**; `debug/FORK.md` + implement `scripts/README.md`
- **`try-learn-skill` multi-harness** write paths: `.claude` / `.agents` / `.grok` / `.pi` `…/skills/learned/`
- **New skill `receiving-code-review`** — verify-first handling of incoming PR feedback (15 workflow skills total + preboot)
- **DX:** skill map in `hooks/session-context.md`; skill authoring checklist in `docs/contributing.md`; optional `analyze` after implement PASS; README skills/platform/repo sections updated for 5.2.0
- Version **5.2.0** across all plugin manifests (`.claude-plugin`, `.codex-plugin`, `.grok-plugin`)

### 5.1.4 — Visual Companion wired + vendored cross-ref cleanup
- **Visual Companion fully wired into `feature-discuss`.** The companion (vendored from obra/superpowers `brainstorming`, telemetry removed, CSP hardened in 5.1.2) is now actively integrated. Added concrete "Companion Protocol" inside the skill (offer with explicit user approval → `start-server.sh` → Write HTML fragments to `screen_dir` via tool → Read `state_dir/events` for clicks → push waiting screens when returning to terminal → `stop-server.sh`). Integrated decision points and usage in Faza 1 (understanding), Faza 3 (solution proposal), and Faza 4 (refinement). The AI now drives the full loop instead of just being told to consult the guide. Updated `visual-companion.md` header and instructions.
- **Cross-references cleaned in vendored skills.** Removed or annotated outdated `superpowers:*` references across `systematic-debugging`, `executing-plans`, `subagent-driven-development` (including diagrams, Integration sections, and example paths). Mapped to local vendored equivalents or AbsolutPowers concepts (`ship` for closeout, `generate-tasks` grafts for writing-plans, `Test-first:` + `review` pipeline, etc.). Updated scripts comments. Added dedicated "Cross-reference cleanup (2026-07)" section in `VENDORED.md` documenting the pass.
- Version bumped to 5.1.4 across all plugin manifests.

### 5.1.3 — fix: duplicate hooks manifest reference
- **SessionStart hook load failure fixed (config bug).** `.claude-plugin/plugin.json` declared `"hooks": "./hooks/hooks.json"`, but Claude Code auto-loads the standard `hooks/hooks.json` — pointing the manifest at that same file triggered `Duplicate hooks file detected` on every session start, aborting hook load. `manifest.hooks` is only for *additional* hook files, so the key is removed; the standard hook still loads automatically. Codex manifest was already clean (no `hooks` key)

### 5.1.2 — Codex fallback path + companion CSP hardening (review major-v5)
- **Codex degradation path restored (HIGH).** New `references/codex-tools.md` mirrors `references/pi-tools.md`: `spawn_agent`/`wait_agent` dispatch, a two-tier "Review gates on Codex" degradation, and an "Orchestrated dispatch on Codex" sequential/inline fallback (reproducing the pre-5.0 `codex/skills/implement` behavior). The three pipeline skills (`implement`, `generate-tasks`, `feature-discuss`) now branch explicitly Claude → registered agents / Codex → `references/codex-tools.md` / Pi → `references/pi-tools.md`, and `implement` bans the literal `Agent(subagent_type=...)` on Codex at each orchestrated dispatch. Claude path untouched
- **Visual companion static-render contract closed (MED).** `server.cjs` now sets a restrictive CSP (`default-src 'none'` + per-response `script-src 'nonce-…'`) on every HTML response — the injected helper and bootstrap script are the only nonce'd scripts — and rejects assistant-generated screens carrying active content (`<script>`, inline `on*=`, `javascript:`, remote `src/href`, `<link>/<base>/<meta http-equiv>`) with a static "Screen blocked" page instead of rendering them verbatim. `start-server.sh` warns (non-blocking) on a non-loopback bind. Existing token/`timingSafeEqual`/WS-Origin/traversal guards untouched
- **Regression smoke test (LOW).** New `skills/feature-discuss/companion-scripts/smoke-test.sh` (no framework, `node`+`curl` only): unauth→403, auth→200, traversal→404, CSP header, active-content reject. Companion modifications logged in `VENDORED.md`

### 5.1.1 — `ship` terminal-state + spójne framowanie closeout (review 5.x)
- **`ship` gets a `## Terminal state` block** — it was the only pipeline-adjacent skill without one. Declares ship as the **mechanical closeout after `review`** (local commit + artifact archiving, then push/merge = the human's move), explicitly **not a gate/chain link**. Resolves the review finding that ship's role was framed two incompatible ways across docs
- **Consistent closeout framing:** `hooks/session-context.md` (injected every session) now names `ship` as the post-`review` closeout instead of omitting it; `docs/getting-started.md` FAQ no longer contradicts its own skills table (both now show `review` → `ship` closeout); README "6 core pipeline skills" relabeled (try-learn/ship are covered in depth but aren't pipeline-gate skills). Convention settled: four gated pipeline skills with `review` as the `/goal` closure point, `ship` as the closeout after
- Outcome of a full solo review of the whole 5.x delta vs 3.13.0 (report in `absolutpowers/reviews/2026-07-14-release-5x-vs-3130.md`): executable/config surfaces (`.pi` extension, hook chain, forked scripts, vendored companion) all clean, no HIGH/MED code findings

### 5.1.0 — `try-learn-skill` → codebase-scan; `harvest` removed, archiving folded into `ship`
- **`try-learn-skill` reworked from feature-artifact to codebase scan.** It no longer learns from a single finished feature's `planning`+`tasks`+`diff` (n=1 → one-off skills). It now **scans the whole codebase** (optional scope arg; threshold N, default 3) for repeated, non-obvious procedures — a pattern qualifies only with **≥N occurrences carrying `file:line` evidence** AND **≥2 non-obvious steps surviving noun-substitution**. Survivors are presented as a **batch**; only user-ticked candidates are written to `.claude/skills/learned/` (human gate preserved). The candidate ledger (`_candidates.md`), the "promote on 2nd occurrence" mechanism, and fast-track are gone — the scan supplies repetition evidence in one pass. A new explicit **boundary vs `update-ai-context`** (passive docs vs active invocable procedures) is written into the skill
- **`harvest` skill removed entirely.** It was a thin orchestrator over skills that are all standalone; `document-feature`/`document-module` stay callable on their own, `try-learn-skill` is now the ad-hoc codebase scan above
- **Artifact archiving moved into `ship`.** `ship` now (with approval) archives the feature's `planning-*.md`/`tasks-*.md` into `absolutpowers/archives/{slug}/` with a `summary.md`, folded into the closing commit — with the same hard boundary (only the current feature's artifacts) and human gate the harvest step had. `ship`'s `allowed-tools` extended (`mkdir`, `mv`, `Write(archives)`); its old "harvest may have archived already" assumption is gone
- **Rewiring:** `implement`'s closeout nudge points to `ship` (not harvest); `document-feature` trigger no longer says "run by harvest"; README pipeline diagram / Quick Start / skills table / Situation table / repo tree and `CLAUDE.md` no longer present harvest as a pipeline step (historical changelog entries left intact)

### 5.0.1 — feature-discuss: pytania o zakres z rekomendacją, nie jak menu
- **Scope-question framing fix** in `feature-discuss`: a CO-axis question now splits into two kinds. **Pure preference** (audience, business priority, timeline — no basis in code) → ask neutrally. **Scope with a technical basis** (you have an architecture/security/leverage/YAGNI argument for what should be in or out) → still the user's decision, but you ask **with your recommendation attached** ("I recommend without X because … — confirm the boundary, or override?"), never as a neutral menu. Fixes the failure mode where the architect held a strong scope opinion but posed the question as an equal-options menu, hiding the recommendation. The "don't present options as equal when you have a recommendation" rule now covers scope options, not just technical ones

### 5.0.0 — Migracja hybrydowa Superpowers (single-tree + vendoring + fuzje + terminal-state)

Jeden breaking release domykający całą migrację hybrydową obry/superpowers, dostarczoną w trzech fazach implementacyjnych (żadna nie była osobnym release'em — numery pośrednie były checkpointami rozwojowymi, tu skonsolidowane).

**Faza 1 — architektura jednodrzewowa + vendoring + Pi:**
- **Breaking structural change (major):** collapsed the two mirrored trees (`claude/`, `codex/`) into **one host-agnostic skill tree** at `skills/{name}/SKILL.md` — a single body serves every harness; Claude-only frontmatter (`allowed-tools`, `argument-hint`) and agent-gate sections are tolerated and inert on Codex/Pi. Adopts the obra/superpowers pattern: thin per-harness manifest/integration on top of one shared tree, per-harness differences isolated to `references/{harness}-tools.md` (read conditionally), zero skill duplication
- **New harness: Pi.** `.pi/extensions/absolutpowers.ts` registers `skills/` and re-injects the shared `hooks/session-context.md` bootstrap at `session_start`/`session_compact`; `references/pi-tools.md` maps skill actions (subagent dispatch, review gates, task tracking) to Pi primitives, including a two-tier degradation path for AbsolutPowers' registered review-gate agents (dispatch a generic subagent fed the target `agents/{name}.md`, or review inline with an explicit non-isolation disclaimer)
- **New `skills/vendored/`** — seven no-fusion skills vendored verbatim (MIT) from [obra/superpowers](https://github.com/obra/superpowers) `v6.1.1`: `using-git-worktrees`, `systematic-debugging`, `verification-before-completion`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `executing-plans`, `subagent-driven-development`. Plus a vendored, telemetry-hard-removed visual companion for `feature-discuss` (not yet wired in). Full provenance (source path, pinned SHA, local modifications) in `VENDORED.md`; full license text in `LICENSE-VENDORED`
- **New shared SessionStart hook:** `hooks/hooks.json` (`SessionStart`, vendored mechanism from obra/superpowers) drives `hooks/run-hook.cmd` → `hooks/session-start`, which re-injects `hooks/session-context.md` — the pipeline chain, the `in-progress` return-to-checklist rule, and the two guardian skills (`debug`/`systematic-debugging`, `verification-before-completion`) — at startup, resume, `clear`, and after `compact` for Claude and Codex. The same `session-context.md` is the single source the Pi extension reads too
- **Manifests and marketplaces moved to repo root:** `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`source: "."`), `.agents/plugins/marketplace.json` (`source.path: "."`) — no longer nested under `claude/`/`codex/`. `AGENTS.md` is now a symlink to `CLAUDE.md` (not a hand-maintained mirror in this repo) — the Codex bootstrap channel
- **Removed:** both former per-harness mirror trees, the drift-detection helper script (there is nothing left to drift between), and the CLAUDE.md→AGENTS.md sync helper script (both its top-level copy and the one duplicated inside the former Codex tree). The former Codex-tree `tech-lead-advisor` skill (a shadow of the Claude-only `tech-lead-agent`) is gone with it — Codex loses that standalone trigger, an accepted regression since registered agents/gates are Claude-only by design
- **Factual correction:** "Codex lacks plugin-level subagent support" was imprecise and is retired. The precise statement: Codex and Pi lack **registered agent type definitions** (no mechanism to install `agents/*.md` as a named subagent identity), but subagent *dispatch* exists on both (Codex `multi_agent=true` → `spawn_agent`/`wait_agent`; Pi's optional `pi-subagents`) — so the execution pattern is portable even though AbsolutPowers' specific registered-agent review gates are Claude-only. See `CLAUDE.md` → "Review Gates (Claude only)" and `references/pi-tools.md`
- Docs (`README.md`, `CLAUDE.md`, `docs/`) rewritten for the single-tree layout; `docs/contributing.md` no longer describes two trees, drift detection, or sync scripts

**Faza 2 — orkiestrowany `implement` ← `subagent-driven-development` (4 grafty):**
- **4-status worker protocol (Claude-only):** `implementation-worker` now returns `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` instead of the old 3-state `COMPLETED`/`BLOCKED`/`FAILED`. The orchestrator (`implement` Step O3) handles each on its own path — `NEEDS_CONTEXT` re-supplies missing context and re-dispatches the same phase (not an escalation); only `BLOCKED` walks the 4-rung escalation ladder (context → stronger model → decompose the phase → escalate to the human)
- **Explicit model routing per role:** every subagent dispatch in the orchestrated process — `implementation-worker`, `phase-review`, `review-implementation` — MUST carry an explicit `model=`; inheriting the orchestrator's model is no longer acceptable for any role. Worker tiers: `haiku` (phase file has complete, ready-to-transcribe code), `sonnet` (integration/multi-file work, `Risk: low|medium`, and the fallback when completeness is ambiguous), `opus` (`Risk: high`). `phase-review` is scaled to diff size/risk; the final `review-implementation` gate is always `opus`
- **`progress.md` ledger (git-anchored, durable progress):** a new committed file beside `implementation-context.md`, one line per phase (`Faza N: complete (commits base7..head7, review clean)`), appended after `phase-review` PASS. Authoritative on resume over the human-facing phase status table when the two disagree — Step O1 reads the ledger first
- **Forked `review-package`/`sdd-workspace` scripts** (MIT, from vendored `subagent-driven-development`, attributed in `VENDORED.md`) generate a file-based diff+status package that `phase-review` (per-phase range) and `review-implementation` (whole-branch range, via the ledger's earliest `base7`) read directly — reviewers no longer run their own `git diff`/status commands
- **Scope-guarded to orchestrated mode:** the 4-status protocol, model-routing table, and ledger apply only when `## Mode` is `orchestrated`; `Single-File Process` is unaffected (keeps `pending`/`in-progress`/`completed`, resumes from the in-file marker, no ledger)

**Faza 3 — jawne kontrakty terminal-state (`/goal`-aware):**
- **`## Terminal state` block in all 4 pipeline skills** (`feature-discuss`, `generate-tasks`, `implement`, `review`): each declares what it delivers, names the next link as `@<skill>`, and — for the three intermediate skills — states the pipeline is **not closed**, so a [`/goal`](https://code.claude.com/docs/en/goal) run continues down the chain instead of stopping mid-pipeline. `review`/`triada-review` is the distinguished **closure point** (fix-loop or merge/ship), naming no forward `@skill`
- **Prose, not machine format:** the `/goal` evaluator reads the conversation, not files — no frontmatter `next:` key, deliberately (an unused parser would be YAGNI). See the "Driving the whole pipeline under `/goal`" section above
- **Execution Handoff resolved:** `generate-tasks` documents that `implement` is the sole executor driven by the `## Mode` field (`orchestrated`/`single-file`) — the AbsolutPowers analog of obra's `subagent-driven-development` vs `executing-plans` split, a resolved decision rather than a missing feature
- **Latent bug fix:** `agents/implementation-worker.md` now filters `project-memory.md` to `Status: active` entries (ignoring `superseded`/`archived`), matching every other pipeline component — it was the only one reading memory unfiltered
- **`gnhf` cleanup:** dead "gnhf" label relabeled to "headless" in the live `feature-discuss` prompt (fallback logic untouched), stripped from archived Faza-2 planning docs; migration plan Faza 4 rescoped from the unused gnhf tool onto native `/goal`

### 3.13.0 — Test-first marker + grep-verifiable AC fulfillment
- **`Test-first:` marker per task** (both trees): `generate-tasks` decides TDD-or-not at generation time and stamps every implementation task `**Test-first:** yes | no ([reason])` — the planner owns the decision, not the implementer mid-flight. `yes` for business logic / transformations / validation / pure functions / bug-fix regressions; `no` (reason mandatory) for config / CRUD wiring / scaffolding / docs. `implement` follows the marker (`yes` → write tests first, confirm the **red run**, implement, confirm green; `no` → implement then add listed tests); deviating requires a recorded justification in the task remarks and is a review blocker otherwise. Docs with no `Test-first:` field anywhere are treated as legacy and fall back to judgment silently
- **Grep-verifiable AC fulfillment** (both trees): AC-traced tasks embed the literal `AC-N` token in their planned test names / display names (e.g. `shouldRejectEmptyQuery_AC4`, `@DisplayName("… [AC-4]")`). AC fulfillment is now determined by **grepping test sources for the token** instead of by judgment — the final verification task greps every traced `AC-N` and fails on a miss. New fulfillment states: `NOT VERIFIED (untested)` (task traces the AC but no test carries the token) and `NOT VERIFIED (untraced)` (no task traces it). `untested` is **no longer informational** — a traced AC without a token-matched test means the work is unfinished and blocks proceeding to the review gate; the smallest honest fix is to write the missing test (or record why it's untestable). Legacy docs fall back to judgment-based mapping and say so explicitly
- **Gate enforcement (Claude-only):** `review-tasks` gains category **`TEST_FIRST`** (missing/unreasoned marker → `[WARN]`) and an `AC_COVERAGE` blocker when a traced AC has no token-bearing planned test; `review-implementation` verifies AC fulfillment by grepping test sources for the `AC-N` token and treats a `Test-first: yes` marker silently ignored (no tests, no recorded reason) as a `[BLOCKER]` TESTS issue

### 3.12.0 — ship skill, gate convergence, interruptible task lifecycle
- New `ship` skill (both trees) — feature closeout: generates a **conventional-commit message and PR description** from the pipeline artifacts (planning intent + tasks scope + AC + diff), and on approval makes the **local commit**. Autodetects the slug from the branch across `feature/` and `archives/`. Hard boundary: never touches code/task statuses, never pushes, never opens a PR on its own (`gh pr create` only on explicit request after `gh auth status`), never creates issues; nothing staged/committed before the human gate. Natural step after `review`/`harvest`
- **Gate convergence protocol** across all three gates (`review-plan`, `review-tasks`, `review-implementation`) and their callers (Claude-only): every issue is tagged `[BLOCKER]` or `[WARN]`; `REJECTED` requires ≥1 blocker, a warns-only review **passes** with a `Warnings (non-blocking):` list. On resubmit the caller passes the previous verdict + applied fixes, so the gate accounts for each prior issue (`FIXED`/`NOT-FIXED`) before reporting new findings (marked `[NEW]`); the verdict follows solely from `NOT-FIXED` + `[NEW]` blockers. Fixes the "chase a fresh top-list every iteration" failure — you converge by clearing the reported list. Issue caps now list blockers first
- **Interruptible task lifecycle** `pending → in-progress → completed` (both trees): a task/phase is marked `in-progress` before code is touched, so a run that dies mid-task leaves a marker. `implement` / `implementation-worker` detect it at session start and reconcile declared `Create:`/`Modify:` lists against the repo (finish / redo / confirm-done) instead of implementing on top of partial work; `review-implementation` and `phase-review` treat a lingering `in-progress` as a completeness `[BLOCKER]`; `review-tasks` warns if a fresh doc contains anything but `pending`
- **`implementation-context.md` hard budget** (both trees): ≤10 lines added per phase, ≤150 lines total; the orchestrator compacts the file (digest older phases, drop entries no remaining phase needs) before spawning the next worker, and `phase-review` fails a materially over-budget entry — bounds the context every worker pays for
- `generate-tasks` now reads **`project-memory.md`** and weaves each active trap whose paths overlap a task into that task's Requirements — the plan routes around known traps by construction instead of leaving them for the implementer to rediscover (both trees)
- `feature-discuss` gains **Mode C — gap handoff from `problem-discuss`**: fed a `problem-{slug}.md` item classified as a gap, it inherits the confirmed evidence (business rule, what's missing, where) as fact, skips re-interviewing on settled points, designs only *how* to fill the gap, and stamps `**Źródło:** problem-{slug}.md, Sprawa N` for report→plan→tasks traceability (both trees)
- `harvest` gains **KROK 4: artifact archiving** (always last — earlier steps still read the artifacts): once every task is `completed`, moves `planning-{slug}.md`/`tasks-{slug}.md` into `absolutpowers/archives/{slug}/` with a `summary.md` (what/why/decisions/AC/where durable knowledge lives), gated, skipped for in-progress features/epics. Also adds a one-shot nudge toward `ship` (both trees)
- `try-learn-skill` reworked around a **candidate ledger** with an inverted default (both trees): most features → **no skill**. Adds an obviousness test (≥2 non-obvious steps surviving noun-substitution), logs a first sighting to `.claude/skills/learned/_candidates.md` without a gate, and promotes to a full learned-skill only on the **2nd occurrence** of the same class or a **fast-track** on strong static reuse evidence — abstraction built empirically by comparing two occurrences, not guessed from n=1. Module-specific gotchas are redirected to `document-feature`; ledger GC included. Supersedes the 3.11.0 reuse-surface gate

### 3.11.0 — try-learn-skill reuse-surface gate
- `try-learn-skill` KROK 2: added an **empirical reuse-surface scan** (2B) — Grep/Glob the repo for *other* instances of the detected procedure's class, count candidates outside the feature diff. Generalizability is now proven from code, not judged from the feature's own artifacts (n=1 always self-describes as a class)
- Decision rule (2C): **0 candidates + occurrences=1 → SKIP** (it's a one-feature solution log, not a reusable skill); module-specific gotchas get **redirected to `document-feature`** instead of saved as a fake procedure. `≥1 candidate` → genuine reuse surface, continue
- KROK 6 human gate now surfaces the candidate count as concrete evidence ("found N other `<Dialog` outside this feature") instead of a subjective "will this help?" (both trees)

### 3.10.1 — Fix harvest archive path
- `harvest` skill: archive path `absolutpowers/archiwa/` → `absolutpowers/archives/` (English, consistent with `feature/`, `problem/`, `reviews/`) (both trees)

### 3.10.0 — Remove tasks-to-issues
- Removed the `tasks-to-issues` skill (Claude-only GitHub Issues export) — its former Claude-tree skill directory, README/docs/CLAUDE.md references, and the `tasks-{slug}.issues.md` back-map artifact. The pipeline is again fully file-bound inside `absolutpowers/`; no outward-facing channel
- Claude skill count: 15 → 14 workflow (+ 1 PreBoot)

### 3.9.0 — Constitution + cross-artifact analyze + Intent Fidelity + tasks-to-issues + debug handoff
- New `constitution` skill — guides authoring and ratification of `absolutpowers/constitution.md` (pryncypia/osąd, semver + ratification date + changelog, numbered Artykuły) (both trees)
- Two-file distinction: `constitution.md` (pryncypia/osąd, human-driven, ratified) ≠ `rules.md` (mechanika/lint, code-derived) — never merged
- `generate-tasks` + `implement` read `constitution.md` as binding context **when it exists** (optional file — absent = silent skip, no error); when present, tasks/implementation MUST NOT violate an article (both trees)
- `review` Faza 3 extended with constitution sub-check — reads `constitution.md`, reports violations, adds counter to Podsumowanie (both trees)
- `feature-discuss` reads `constitution.md` as lightweight context (not a gate; absent file = silent skip) (both trees)
- `update-ai-context` PHASE 3 gains a demarcation note: pryncypia belong in `constitution.md` via the `constitution` skill, not in `rules.md` (both trees)
- New `analyze` skill — on-demand cross-artifact consistency audit: builds AC→task→code matrix, detects 6 divergence classes (1/3/4/6 blocking, 2/5 warning), outputs `absolutpowers/reviews/analyze-{slug}.md`, verdict CONSISTENT/INCONSISTENT, hard boundary (audit+route only, never fixes), both trees
- `review-tasks` gains criterion **#7 Intent Fidelity** (`INTENT` category, Claude-only): judges whether task set achieves the goal/intent of the planning doc, not just literal coverage
- `review` + `generate-tasks` gain "vs analyze" / post-PASS analyze notes (both trees)
- New `tasks-to-issues` skill — **Claude-only** outward bridge from `tasks-{slug}.md` to GitHub Issues via `gh`: epic issue per feature + sub-issue per phase (orchestrated) / per task (single-file), idempotent via back-map `tasks-{slug}.issues.md` (source of truth) + title marker `[{slug}]` (fallback), labels (`absolutpowers`, `{slug}`, `risk:*`), STOP-on-precondition, first-export publish confirmation, orphan flagging (no auto-close), hard boundary (issues + map only), provider extension point for `glab`/Jira. No Codex counterpart in v1 (deliberate asymmetry)
- `debug` handoff closed on both ends (both trees): reads `problem-{slug}.md` as starting evidence when routed from `problem-discuss` (no re-deriving Phase 1 from scratch); Phase 4 branches by fix size — small fix stays inline, large fix (multi-layer / migration / public API / security boundary / shared core, or 3+ failed attempts via Phase 4.5) writes `planning-fix-{slug}.md` and routes to `generate-tasks` so quality gates apply. `problem-discuss` Faza 5 nudge points `debug` at the report file + item; `generate-tasks` recognizes the `planning-fix-` prefix as planning input

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
- [Codex](https://github.com/openai/codex) (optional, for the Codex target)
- [Pi](https://github.com/earendil-works/pi) (optional, for the Pi target — local extension load, see [Install](#1-install))

## Vendored Skills & Hook

AbsolutPowers vendors (copies, trims, adapts) a small set of skills and one hook mechanism from
[obra/superpowers](https://github.com/obra/superpowers) under MIT, instead of depending on it at
runtime — full control over content, no marketplace dependency, no conflict between two plugins'
priorities. Full provenance table (source path, pinned SHA, per-file local modifications) lives in
[`VENDORED.md`](./VENDORED.md); full license text in [`LICENSE-VENDORED`](./LICENSE-VENDORED).

- **`skills/vendored/{name}/`** — seven no-fusion skills, copied verbatim beyond a one-line MIT note:
  `using-git-worktrees`, `systematic-debugging`, `verification-before-completion`,
  `dispatching-parallel-agents`, `finishing-a-development-branch`, `executing-plans`,
  `subagent-driven-development`. Plus a vendored visual companion for `feature-discuss`
  (`skills/feature-discuss/visual-companion.md` + `companion-scripts/`) with all remote-telemetry
  code paths hard-removed — not just disabled — so no external request is possible; not yet wired
  into `feature-discuss/SKILL.md` (a future fusion phase, out of scope here)
- **`hooks/`** — the shared Claude/Codex `SessionStart` hook mechanism (`hooks.json`, `run-hook.cmd`,
  `session-start`) is vendored from the same source; the content it injects
  (`hooks/session-context.md`) is entirely AbsolutPowers' own

Vendoring is one-way and selective — not every obra/superpowers skill is pulled in, and upstream
changes are reviewed quarterly (see `VENDORED.md` for the process), not auto-synced.

## License

MIT — [Absolut Systems](https://github.com/AbsolutSystems)

### Attribution

`skills/vendored/` and the `hooks/` SessionStart mechanism are adapted from
[obra/superpowers](https://github.com/obra/superpowers), created by **Jesse Vincent** and the team
at [Prime Radiant](https://primeradiant.com), licensed MIT. The full upstream license text is
preserved verbatim in [`LICENSE-VENDORED`](./LICENSE-VENDORED); per-file provenance and local
modifications are tracked in [`VENDORED.md`](./VENDORED.md). AbsolutPowers' own code, skills, and
docs remain MIT-licensed by Absolut Systems as stated above.
