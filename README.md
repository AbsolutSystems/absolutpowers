# AbsolutPowers

AI-assisted development lifecycle — from feature design through implementation to code review. Works with **Claude Code** and **Codex**.

Instead of ad-hoc prompting, AbsolutPowers gives your AI agent a structured workflow. Each skill owns one phase. Skills chain into a pipeline with automated quality gates (Claude Code) that catch problems before they cascade.

## Quick Start

### 1. Install

**Claude Code**

```bash
/plugin marketplace add AbsolutSystems/absolutpowers
/plugin install absolutpowers@absolutpowers-skills
```

Restart Claude Code, then type `/absolutpowers:` — autocomplete lists every skill.

**Codex** — open the repo in Codex → repo marketplace (`.agents/plugins/marketplace.json`) → install `absolutpowers`.

### 2. Bootstrap project context (once)

```bash
/absolutpowers:update-ai-context
```

Creates `CLAUDE.md`, `AGENTS.md`, `absolutpowers/patterns.md`, `absolutpowers/rules.md`. Every other skill reads these.

### 3. Build a feature

```bash
/absolutpowers:feature-discuss "system powiadomień push dla użytkowników"   # WHAT  → planning doc + AC
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md  # HOW → tasks
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md  # BUILD+TEST
/absolutpowers:review                                                        # AUDIT
/absolutpowers:harvest @absolutpowers/feature/tasks-push-notifications.md     # CAPTURE (optional, pre-commit)
```

Each step writes a file that feeds the next. Review gates between steps (Claude Code) catch issues automatically.

## The Pipeline

```
feature-discuss ──→ generate-tasks ──→ implement ──→ review ──→ harvest
     WHAT?              HOW?          BUILD+TEST     AUDIT      CAPTURE
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

**`feature-discuss` — you know you want to build something new.** A single, already-classified feature request. Goes straight into the pipeline: discussion → planning doc + AC → tasks → implement.

**`problem-discuss` — you have a vague report and don't yet know what each item is.** A multi-item client/stakeholder message about an *existing* module where each item could turn out to be a bug, a gap, a config error, a data anomaly, or a misunderstanding. It splits the report, classifies every item, and routes each onward (see [Client report workflow](#client-report-workflow-problem-discuss)). It investigates and routes only — never fixes or plans. **Don't reach for it** for a clean error/stack trace (that's `debug`) or a single known feature idea (that's `feature-discuss`).

`debug` branches on fix size — small fix stays inline, large fix (multi-layer / migration / public API / security boundary / shared core, or 3+ failed attempts) writes `planning-fix-{slug}.md` and routes into the pipeline so gates apply.

### On-demand tools (no gate, run anytime)

- **`review`** — solo 4-phase audit of **your own** branch before merge. Writes a report, integrates with project memory, works on Codex. Default choice for everyday code review.
- **`triada-review`** — parallel multi-agent review (Claude-only) for **larger PRs or someone else's branch** — three independent perspectives (tech-lead / security / UI) you don't have yourself. Reach for it when one pass isn't enough.
- **`analyze`** — traceability audit, not code quality: does planning ↔ tasks ↔ code form a consistent chain? Run it when you suspect scope creep or coverage gaps ("czy mamy scope creep", "pokaż macierz AC→task→kod"). Orthogonal to `review`/`triada-review` — safe to run all three.
- **`explain`** — standalone HTML report when a **human** needs a fast, auditable explanation of a plan or a diff (onboarding, handoff). Ephemeral, not durable docs.
- Also: `constitution` (ratify project principles).

### How gates work (Claude Code only)

After a skill produces output, a subagent reviews it:

1. Reviews against criteria specific to that step
2. Returns **PASS** or **REJECTED** + list of issues
3. REJECTED → skill fixes and resubmits (up to 3 iterations)
4. Still REJECTED after 3 → shows remaining issues, asks you

Codex skills run without gates.

### Orchestrated implementation (Claude Code only)

For larger features, `generate-tasks` emits an orchestrated plan and `implement` becomes an orchestrator:

```
tasks-{slug}.md (index)
  ├─ implementation-worker → phase-review   (per phase, fresh narrow context)
  ├─ implementation-worker → phase-review
  ├─ final verification
  └─ review-implementation (final gate)
```

`implementation-context.md` carries only concise handoff facts between phases. Small features get one `tasks-{slug}.md` instead.

## Skills Reference

`both` = Claude Code + Codex. `Claude` = Claude Code only (needs agents / parallel subagents / external API).

| Skill | What it does | In → Out | Trees |
|---|---|---|---|
| `feature-discuss` | PO/architect Q&A → planning doc + Acceptance Criteria | idea → `planning-{slug}.md` | both |
| `generate-tasks` | Planning doc → sequential tasks or orchestrated phase plan | `planning-*.md` → `tasks-{slug}.md` (+ phase dir) | both |
| `implement` | Executes tasks TDD, marks `completed` in-place | `tasks-*.md` → code + tests | both |
| `review` | 4-phase code-quality audit (semantic / edge / rules / GC) | branch → `reviews/YYYY-MM-DD-{branch}.md` | both |
| `harvest` | Closeout: runs try-learn-skill → document-feature → document-module | `tasks-*.md` → learned skill + module docs | both |
| `debug` | Root-cause first, then size the fix (inline vs hand-off) | bug desc → fix or `planning-fix-{slug}.md` | both |
| `problem-discuss` | Triage fuzzy multi-item client report: split, classify, route | report → `problem/problem-{slug}.md` | both |
| `analyze` | Cross-artifact audit: AC→task→code matrix, 6 divergence classes | slug → `reviews/analyze-{slug}.md` | both |
| `triada-review` | Parallel 3-agent branch review + synthesis | branch → report in session | Claude |
| `constitution` | Author/ratify project principles (pryncypia) | topic → `constitution.md` | both |
| `update-ai-context` | Bootstrap/refresh `CLAUDE.md`, `AGENTS.md`, `patterns.md`, `rules.md` | path → context files | both |
| `explain` | Standalone HTML onboarding report for a plan or diff | path/diff → `docs/onboarding/*.html` | both |
| `try-learn-skill` | Extract reusable procedure → callable learned skill (human-gated) | `tasks-*.md` → `.claude/skills/learned/` | both |
| `document-feature` | Per-module prose docs from planning + diff (intelligent merge) | `tasks-*.md` → `docs/modules/{module}.md` | both |
| `document-module` | Architecture docs from a code scan + C4 diagrams | module → `docs/modules/{slug}-architecture.md` + HTML | both |
| `preboot` | Doc router / guardrail for the PreBoot.io library ecosystem | PreBoot usage → reads `./preboot-docs/` | both |

Cards below cover the 5 core pipeline skills in depth. The rest behave as the table describes.

---

### `/absolutpowers:feature-discuss`

Interactive Product Owner / Product Architect session — discusses requirements before any code is written. Asks clarifying questions one at a time, analyzes your codebase, proposes 2-3 approaches with tradeoffs, then writes a planning doc + behavioral Acceptance Criteria (AC-1, AC-2, …). Runs the `review-plan` gate before finishing. Reads `constitution.md` as light context if present.

- **When:** starting a feature, brainstorming, "chcę dodać…", "potrzebujemy…"
- **In → Out:** feature description → `absolutpowers/feature/planning-{slug}.md` (optionally `docs/adr/YYYY-MM-DD-{slug}.md`)
- **Trivial changes** (one-liner, config) skip the planning doc — the skill suggests direct implementation. **Epics** split into `planning-main.md` + per-phase docs in a `feature/{epic-slug}/` subfolder.

```bash
/absolutpowers:feature-discuss "eksport danych użytkowników do CSV z filtrowaniem"
```

> **Intent matters:** the feature's goal MUST be written into the planning doc explicitly — the downstream Intent Fidelity check (review-tasks) judges intent only from the written plan, not from the discussion.

---

### `/absolutpowers:generate-tasks`

Reads a planning doc (or a review report, or a `planning-fix-` doc from `debug`) and produces a step-by-step plan for an AI agent: exact paths, signatures, tests, plus `Traces to: AC-N` traceability. Picks `single-file` mode (small) or `orchestrated` mode (phase files + `implementation-context.md` + final verification). Reads `constitution.md` as binding context. Runs the `review-tasks` gate.

- **When:** after `feature-discuss`, or after `review` finds 3+ issues
- **In → Out:** path to a planning doc / review report → `absolutpowers/feature/tasks-{slug}.md` (+ `tasks-{slug}/` for larger features)

```bash
/absolutpowers:generate-tasks @absolutpowers/feature/planning-push-notifications.md
/absolutpowers:generate-tasks @absolutpowers/reviews/2026-04-21-feature-auth.md   # review → fix tasks
```

---

### `/absolutpowers:implement`

Senior engineer executing tasks sequentially with TDD. Picks the first pending task/phase, updates status to `completed` in-place, proposes alternatives (asks first), runs the final verification task, then the `review-implementation` gate. Orchestrated plans → `implementation-worker` per phase + `phase-review` before advancing (Claude); Codex runs phase files sequentially in one session. Respects `constitution.md`. Can create ADRs and memory candidates.

- **When:** after `generate-tasks`
- **In → Out:** path to a tasks file → implementation code + tests, updated tasks file

```bash
/absolutpowers:implement @absolutpowers/feature/tasks-push-notifications.md
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

**review vs triada-review vs analyze:** `review` = solo 4-phase code-quality audit, writes a report, works on Codex. `triada-review` = parallel multi-agent code-quality review, Claude-only, for larger PRs. `analyze` = traceability audit (planning↔tasks↔code), not code quality. Orthogonal — safe to run all three.

---

### `/absolutpowers:harvest`

Thin pre-commit closeout orchestrator. Runs three sub-skills, each keeping its own gate:

```
harvest
  ├─ try-learn-skill   → .claude/skills/learned/{name}/        (reusable procedure, human gate)
  ├─ document-feature  → docs/modules/{module}.md              (per-module prose, mapping-confirm gate)
  └─ document-module   → docs/modules/{slug}-architecture.md   (architecture + C4, only if architecture changed)
                         + docs/architecture/{slug}.html
```

`document-module` runs only for touched modules whose architecture changed (new file / new public symbol / new cross-module import) — cosmetic edits are skipped to avoid noisy diagram churn. A sub-skill the project opted out of is skipped, not an error. Reminds you to review the result in `git diff` before committing.

- **When:** end of `implement`, before commit (`implement` prints one best-effort nudge toward it)
- **In → Out:** path to a `tasks-*.md` / `planning-*.md` → learned skill + module docs

```bash
/absolutpowers:harvest @absolutpowers/feature/tasks-push-notifications.md
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
| A finished feature, pre-commit | `harvest` | Captures knowledge: learned skill + docs |
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
/absolutpowers:debug @absolutpowers/problem/problem-slug.md "Sprawa 2"
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

Learned skills are project-local callable procedures extracted by `try-learn-skill` into `.claude/skills/learned/learned-{name}/`. They differ from `patterns.md`:

| | Learned skill | `patterns.md` |
|---|---|---|
| Captures | A **procedure** (steps/tools/decisions) | **Code structure** (recurring conventions) |
| Form | Callable `SKILL.md` with narrow `TRIGGER when:` | Descriptive reference, read by generate-tasks / implement |
| Lifecycle | NEW → UPDATE, `confidence: candidate → established`, `occurrences` | Re-scanned by `update-ai-context` |
| Source | One finished feature + git diff | Whole-codebase scan (pattern used 3+ times) |

"How the code is shaped" → `patterns.md`. "How to carry out a class of task" → learned skill.

### Project memory

Skills discover durable lessons (recurring traps, non-obvious workarounds, failure patterns) and capture them as candidates in `absolutpowers/memory-candidates/`. Promotion to `absolutpowers/project-memory.md` requires your explicit approval; the candidate is then deleted. One-off notes, branch status, and facts that belong in `patterns.md`/`rules.md`/ADRs do **not** belong in project memory.

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

## Agents (Claude Code only)

Most agents are subagents that skills spawn automatically — you don't invoke them directly. Three are orchestrated by the `/triada-review` command.

| Agent | Spawned by | Purpose |
|---|---|---|
| `qa-enrichment` | feature-discuss | Generates behavioral Acceptance Criteria |
| `review-plan` | feature-discuss | Validates planning completeness, feasibility, architecture, AC quality |
| `review-tasks` | generate-tasks | Validates traceability, granularity, ordering, specificity, AC coverage, **Intent Fidelity** |
| `implementation-worker` | implement | Implements one orchestrated phase with a fresh, narrow context |
| `phase-review` | implement | Lightweight gate after one orchestrated phase |
| `review-implementation` | implement | Validates correctness, patterns, rules, tests, safety, AC fulfillment |
| `tech-lead-advisor` | triada-review / manual | Goal, architecture, overengineering, readability |
| `codebase-auditor` | triada-review | Security, correctness, test quality (JSON verdict) |
| `ui-reviewer` | triada-review | UI states, interactions, a11y, data, UI races, user goal (JSON verdict) |

**Intent Fidelity** (review-tasks #7, `INTENT` category, Claude-only): judges whether the task set as a whole achieves the goal/intent of the planning doc — not just literal per-requirement coverage. Complements `analyze` (in-flight gate vs post-hoc audit). The three triada-review agents have non-overlapping scopes and each also flags `rules.md` violations within its scope.

## Platform Differences

| Feature | Claude Code | Codex |
|---|---|---|
| Skills | 14 workflow + 1 PreBoot | 14 workflow + tech-lead-advisor + 1 PreBoot |
| Agents | 9 (review gates + phase worker + triada trio) | none |
| Slash commands | `triada-review` | not available |
| Multi-agent review | `triada-review` (3 parallel agents + synthesis) | not available (no parallel subagents) |
| Review gates | automatic after each step + `phase-review` | not available |
| Orchestrated implementation | worker subagent per phase | sequential phase files in one session |
| Skill invocation | `/absolutpowers:skill-name` | `$absolutpowers skill-name` |
| AI context | `CLAUDE.md` (source) | `AGENTS.md` (mirror) |

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
│   ├── memory-candidates/              # Proposed durable lessons (approval queue)
│   ├── problem/problem-{slug}.md       # Problem triage reports
│   ├── project-memory.md               # Approved operational memory
│   ├── patterns.md                     # Discovered code patterns
│   ├── rules.md                        # Mechanical lint rules (code-derived)
│   └── constitution.md                 # Ratified principles / pryncypia (≠ rules.md)
├── docs/adr/YYYY-MM-DD-{slug}.md        # Architecture Decision Records
├── CLAUDE.md                            # AI context (Claude Code)
└── AGENTS.md                            # AI context mirror (Codex)
```

Recommended `.gitignore` — keep planning docs and reviews (they're documentation), exclude the approval queue:

```gitignore
absolutpowers/memory-candidates/
```

## Repo Structure (this repository)

```
absolut-ai-skills/
├── claude/                            # Claude Code plugin
│   ├── .claude-plugin/plugin.json
│   ├── commands/                      # triada-review slash command
│   ├── skills/                        # 14 workflow + 1 PreBoot skill
│   └── agents/                        # 9 subagent definitions
├── codex/                             # Codex plugin
│   ├── .codex-plugin/plugin.json
│   ├── skills/                        # 14 workflow + tech-lead-advisor + 1 PreBoot skill
│   └── scripts/
├── .claude-plugin/marketplace.json    # Claude marketplace → claude/
├── .agents/plugins/marketplace.json   # Codex marketplace → codex/
├── scripts/
│   ├── diff-skills.sh                 # Drift detection between platforms
│   └── sync_claude_to_agents.py       # CLAUDE.md → AGENTS.md sync
└── README.md
```

## Updating

```bash
# Claude Code
/plugin install absolutpowers@absolutpowers-skills

# Codex — pull the repo and reinstall from the local marketplace
```

## Changelog

Versioning is SemVer, kept in sync across both manifests
(`claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json`).

### 3.10.0 — Remove tasks-to-issues
- Removed the `tasks-to-issues` skill (Claude-only GitHub Issues export) — `claude/skills/tasks-to-issues/`, README/docs/CLAUDE.md references, and the `tasks-{slug}.issues.md` back-map artifact. The pipeline is again fully file-bound inside `absolutpowers/`; no outward-facing channel
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

## License

MIT — [Absolut Systems](https://github.com/AbsolutSystems)
