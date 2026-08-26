# Orchestrated implementation process

_Extracted from `implement`. **Read this file** when `## Mode` is `orchestrated` (Steps O1–O6)._

## Orchestrated Process

Use this process only when the main tasks file has `## Mode` set to `orchestrated`.

> Path note: resolve phase files, `implementation-context.md`, and the final verification file from the explicit paths recorded in the main tasks file (see **Path Resolution**). The `./absolutpowers/feature/tasks-{slug}/...` literals below are shorthand for the phase directory beside the main tasks file, which for an epic phase is `./absolutpowers/feature/{epic-slug}/tasks-{slug}/...`.

> Scope note (orchestrated-only): the 4-status protocol (`DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED`, Step O3), the model-routing-per-role table (Step O2), and the ledger below dotyczą wyłącznie trybu orchestrated — they exist because this mode dispatches subagents that need a resumable, model-tiered, statusable handoff protocol. **Single-File Process does not dispatch subagents, so none of these three mechanisms apply there.** It keeps its own `pending`/`in-progress`/`completed` task statuses (never `DONE`/`DONE_WITH_CONCERNS`/`NEEDS_CONTEXT`/`BLOCKED`) and resumes from the `in-progress` marker already in the tasks file (see Single-File Process Step 1) — it does not need `progress.md` or any ledger to resume.

### Durable Progress (ledger)

Orchestrated runs must survive context compaction and interrupted sessions. Three files carry this, each with a distinct role — do not let them blur together:

| File | Role | Granularity |
|---|---|---|
| Phase file (`NN-{slug}.md`) | Full spec + code for one phase | Complete task detail |
| `implementation-context.md` | Narrow cross-phase handoff | ≤10 lines per phase |
| `progress.md` (the ledger) | Git-anchored recovery map | 1 line per phase |
| `scout-findings.md` | Boy-scout findings ledger | 1 line per finding (created on first append) |

**`scout-findings.md`** sits beside `progress.md` (same directory). Workers run headless and
cannot ask the user, so any out-of-scope finding they cannot fix as a trivial one-liner is
**appended** here (create the file on the first finding) and mirrored under `Notes for
orchestrator`. It is a tracked artifact — it must survive compaction and resume. One line per
finding:
```
- [Faza N | file:line] symptom — suggested route (inline fix / follow-up / feature-discuss / debug)
```
The orchestrator reads it once at Step O5.7 and routes with the user; it never blocks the current
work's final gate.

**Path:** `progress.md` sits beside the phase directory, at the same level as `implementation-context.md` — for a normal feature `./absolutpowers/feature/tasks-{slug}/progress.md`, for an epic phase `./absolutpowers/feature/{epic-slug}/tasks-{slug}/progress.md` (see Path Resolution). This is the absolutpowers convention, NOT `.superpowers/sdd/`.

**Committed.** `progress.md` is a tracked feature artifact — it survives `git clean` and is auditable, unlike the gitignored scratch `review-package` workspace.

**Format:** one appended line per phase, written after `phase-review` PASS (Step O4):
```
Faza N: complete (commits base7..head7, review clean)
```
`base7`/`head7` are 7-char short commit hashes: `base7` is the BASE recorded before dispatch (Step O2, "Before spawning the worker"), `head7` is `git rev-parse HEAD` (short) at the moment of PASS. A one-line append is lighter than editing a status table and harder to skip by accident.

**Authoritative on resume (AC-9):** if `progress.md` and the phase status table in the parent tasks file ever disagree, `progress.md` plus `git log` are authoritative — trust the ledger, not the table. The status table in the parent tasks file remains a human-readable view for people skimming the file, never the source of truth for resume decisions. Step O1 reads the ledger before the status table for exactly this reason.

### Step O1: Read Orchestrator State

- Read the main tasks file completely.
- Read the shared `implementation-context.md` referenced in Project Context (use the `**Shared implementation context:**` path verbatim).

**Resumption detection:**
- **First, consult the ledger (`progress.md`) and `git log`** — this order is authoritative for resume: read `progress.md` beside the phase directory (if it exists) and cross-check its `Faza N: complete (commits base7..head7, ...)` entries against `git log`. Any phase present in the ledger with a resolvable `head7` is DONE — do not re-dispatch it, even if `## Phase Overview` disagrees.
- Then scan `## Phase Overview` for phase statuses — this is the secondary, human-facing view, not the source of truth.
- If ALL phases are `pending` (ledger empty or absent, table all-pending): fresh start. Proceed to first phase.
- If one or more phases are `completed` (per the ledger or the table):
  1. Report: "Resuming from Phase N. Phases 1 through M already completed."
  2. Read `## Completed Phases` in `implementation-context.md`.
  3. Cross-reference: each completed phase in the main tasks file should have a corresponding entry in `## Completed Phases`. If any completed phase is missing from `implementation-context.md`, warn: "Phase X marked completed but no entry in implementation-context.md — handoff data may be incomplete."
  4. Read the next pending phase's `## Context Contract -> Requires` (if present).
  5. Verify each Requires item against `implementation-context.md` and the codebase.
  6. If any Requires item is unsatisfied, warn about potential stale state from a previous interrupted session. Ask user whether to proceed or investigate.

**After resumption check or fresh start:**
- Find the first pending phase in `## Phase Overview` and note its `**File:**` path.
- Read the pending phase's `## Context Contract -> Requires` section (if present).
- Cross-reference each Requires item against `implementation-context.md` and the current project state.
- If any Requires item appears unsatisfied, warn the user before delegating: "Phase N Requires item '[item]' may not be satisfied." Ask whether to proceed or investigate.
- Do not start a later phase while an earlier dependency is pending or rejected.

### Step O2: Delegate One Phase

**Model routing by role (always explicit):**

Every subagent dispatch in this Step — implementer, and (in Step O4/O6) `phase-review` and `review-implementation` — MUST carry an explicit `model=` parameter. Dispatching without one is an error under this rule: inheriting the orchestrator session's model is NOT an acceptable shortcut for any role. Note (turn count beats token price): reviewers and implementers working with prose, not code, need at least a mid-tier floor — a wrong/too-cheap model that costs an extra retry turn is more expensive than one correctly-tiered dispatch up front.

| Role | Tier | Model | When |
|---|---|---|---|
| `implementation-worker` | transcription / cheapest | `haiku` | phase file contains complete, ready-to-transcribe code (e.g. `generate-tasks` already emitted full snippets) — implementation reduces to transcription + tests |
| `implementation-worker` | standard | `sonnet` | integration / multi-file / pattern-matching work, `Risk: low|medium`; **also the fallback** when it is ambiguous whether the phase file's code is complete — never default to the cheapest tier when in doubt |
| `implementation-worker` | most-capable | `opus` | `Risk: high` — security, migrations, shared core, design judgment |
| `phase-review` | scaled | explicit, sized to the diff | a small mechanical diff does not need `opus`; a subtle concurrency/security diff does — the model is always passed explicitly, never inherited from the session |
| `review-implementation` (final gate) | most-capable | `opus`, always | the final gate always dispatches with `model="opus"` regardless of phase risk |

Read the phase's `**Risk:**` field from the Phase Overview in the parent tasks file, then read the phase file itself to judge whether it contains complete, ready-to-transcribe code:
- phase file has complete code ready to transcribe (and Risk is not `high`) → `model="haiku"` (transcription tier)
- `Risk: low|medium` (or unspecified), or it is unclear/ambiguous whether the code is complete → `model="sonnet"` (standard tier — the fallback for doubt, not the cheapest tier)
- `Risk: high` → `model="opus"` (most-capable tier)

For the pending phase, spawn `implementation-worker`. Use the **exact** parent tasks file path (the argument) and the **exact phase file path from the Phase Overview `**File:**` field** — do not reconstruct them from a template, so epic-nested paths stay correct.

> Codex: patrz `references/codex-tools.md` — dispatch generic przez `spawn_agent` z ciałem `agents/implementation-worker.md`, lub sekwencyjnie inline w tej sesji; nie literalny `Agent(subagent_type=...)`.
> Grok: patrz `references/grok-tools.md` — `spawn_subagent` (general-purpose) + ciało `agents/implementation-worker.md`, lub inline; nie literalny `Agent(...)`.

**Codex model translation:** the Claude tier names in the routing table above are not
Codex model IDs. For Codex, `haiku` maps to `gpt-5.6-luna` + `reasoning_effort="medium"`,
`sonnet` maps to `gpt-5.6-luna` + `reasoning_effort="high"`, and `opus` maps to
`gpt-5.6-terra` + `reasoning_effort="high"`. Pass both overrides to `spawn_agent`; do not
let an orchestrated worker inherit the session model. For `phase-review`, choose Luna/high
for routine diffs or Terra/high for subtle diffs; `review-implementation` uses Sol/high.
Reserve `xhigh` for an explicit escalation when the failure cost justifies the additional
reasoning-token usage. Do not route to `gpt-5.5` unless the user explicitly requests it.

If Risk is `high`:
```
Agent(subagent_type="implementation-worker", model="opus", prompt="Implement this orchestrated phase. Parent tasks file: {parent-tasks-path}. Phase file: {phase-File-path-from-Phase-Overview}. Validate Context Contract Requires before starting. Follow the phase Write Scope, update only the phase file and implementation-context.md, run phase verification, and return PHASE_RESULT with contract check.")
```

If Risk is not `high` and the phase file contains complete, ready-to-transcribe code (transcription tier):
```
Agent(subagent_type="implementation-worker", model="haiku", prompt="Implement this orchestrated phase. Parent tasks file: {parent-tasks-path}. Phase file: {phase-File-path-from-Phase-Overview}. Validate Context Contract Requires before starting. Follow the phase Write Scope, update only the phase file and implementation-context.md, run phase verification, and return PHASE_RESULT with contract check.")
```

If Risk is `low`, `medium`, unspecified, or it is ambiguous whether the phase file's code is complete (standard tier — the fallback):
```
Agent(subagent_type="implementation-worker", model="sonnet", prompt="Implement this orchestrated phase. Parent tasks file: {parent-tasks-path}. Phase file: {phase-File-path-from-Phase-Overview}. Validate Context Contract Requires before starting. Follow the phase Write Scope, update only the phase file and implementation-context.md, run phase verification, and return PHASE_RESULT with contract check.")
```

Before spawning the worker:
- **Record BASE commit (MUST, before dispatch):** run `git rev-parse HEAD` in the target project and record the result as BASE **before** dispatching the worker, never after — this is the correct base for `review-package` (wired in Phase 5) and the ledger (formalized in Phase 3); recording BASE after the worker runs would silently fall back to `HEAD~1` and lose multi-commit phases.
- **Context budget check:** if `implementation-context.md` exceeds ~150 lines, compact it first — rewrite older `## Completed Phases` entries into a one-line digest each and drop entries in other sections that no remaining phase needs (Staleness rules). Every worker pays for this file's size in its context window; compaction is the orchestrator's job, not the workers'.
- Set the phase status in the parent tasks file from `pending` to `in-progress` (interruption marker). The worker must implement only that phase. The orchestrator remains responsible for updating the parent phase status: `in-progress` → `completed` only after `phase-review` PASS. On session start, a phase already `in-progress` with no matching `## Completed Phases` entry means an interrupted run — treat it like the stale-state warning in Step O1 (verify partial state, ask the user). If a phase worker appears stuck or unresponsive, the orchestrator may interrupt and ask the user for guidance.

### Step O3: Inspect Worker Result

Read the worker result and inspect:
- phase file status updates
- `implementation-context.md` changes
- relevant git diff
- reported verification commands
- contract check (all Requires satisfied, all Provides fulfilled)
- any Boy-scout finding: confirm the worker appended it to `scout-findings.md`; if a `Notes for orchestrator` finding is missing from the file, append it yourself. Do not act on findings mid-run — they are collected for Step O5.7.

Handle each of the four `PHASE_RESULT` values on its own path — never fall back to one shared "stop and report" branch:

- **`DONE`** → proceed to Step O4 (phase review).
- **`DONE_WITH_CONCERNS`** → read the reported concerns first. If a concern is about correctness or scope, address it before phase review. If it is an observation (e.g. "this file is getting large"), note it and proceed to phase review.
- **`NEEDS_CONTEXT`** → this is not an escalation. Supply the missing context (from `implementation-context.md`, the codebase, or earlier phases) and re-dispatch the **same** phase to the worker. If the reported gap is unsatisfied Context Contract Requires that you cannot supply yourself, report the specific unsatisfied items and ask the user whether to:
  1. Fix the dependency manually and retry
  2. Skip the contract check and force delegation
- **`BLOCKED`** → work the 4-way escalation ladder (drabina eskalacji), in order, and stop at the first rung that applies:
  1. problem kontekstu → dostarcz brakujący kontekst, re-dispatch **ten sam** model.
  2. wymaga więcej rozumowania → re-dispatch **mocniejszy** model.
  3. task za duży → **dekompozycja** fazy na mniejsze zadania.
  4. plan sam jest zły → **eskalacja do człowieka**.

  Never ignore an escalation and never force the same model to retry without changing the input.

### Step O4: Run Phase Review

After a worker reports `DONE`, generate the review package before dispatching `phase-review` — do not let the reviewer run its own `git diff`:

```bash
AP_TASKS_DIR=<phase-directory-from-Path-Resolution> skills/implement/scripts/review-package <BASE-recorded-in-O2> <HEAD=$(git rev-parse HEAD)>
```

`AP_TASKS_DIR` is the phase directory resolved per **Path Resolution** (the directory beside the main tasks file that already holds `implementation-context.md` and `progress.md`) — set/export it before invoking the script, it is a hard error if unset. BASE is the commit recorded in Step O2 ("Before spawning the worker") for this phase, never `HEAD~1`. The script prints `wrote <package-path>: N commit(s), ...`; capture `<package-path>` for the dispatch prompt.

Spawn `phase-review` with an explicit `model=` scaled to the size/risk of this phase's diff (see Step O2 model routing table — a small mechanical diff does not need `opus`; a subtle concurrency/security diff does). Pass the exact parent tasks path, the phase `**File:**` path, the `**Shared implementation context:**` path, and the review package path — the prompt carries the package path instead of any instruction to read `git diff` directly:

```
Agent(subagent_type="phase-review", model="<scaled-to-diff>", prompt="Review completed orchestrated phase. Parent tasks file: {parent-tasks-path}. Phase file: {phase-File-path-from-Phase-Overview}. Shared context: {shared-implementation-context-path}. Review package: {review-package-path}.")
```

> Codex: patrz `references/codex-tools.md` — dispatch generic z ciałem `agents/phase-review.md`, lub review inline z advisory verdictem; nie literalny `Agent(subagent_type=...)`.
> Grok: patrz `references/grok-tools.md` — `spawn_subagent` + ciało `agents/phase-review.md`, lub inline advisory; nie literalny `Agent(...)`.

If `VERDICT: PASS`:
- append a ledger line to `progress.md` (beside the phase directory; create the file with a one-line header if it does not yet exist): `Faza N: complete (commits base7..head7, review clean)`, using the BASE recorded before dispatch (Step O2) and `git rev-parse HEAD` (short) as HEAD — commit `progress.md` alongside the rest of the phase's changes, it is a tracked artifact, not scratch
- update the phase status in the parent main tasks file to `completed`
- add a concise note to the parent phase if useful
- continue to the next pending phase

If `VERDICT: REJECTED` (1st time):
- send the issues back to `implementation-worker` for the same phase, or spawn a fix worker
- rerun `phase-review`

If `VERDICT: REJECTED` (2nd time with similar issues):
- show user: "Phase review rejected for the 2nd time with similar issues. Options: (a) attempt fix again, (b) override phase review and proceed to next phase, (c) stop and investigate manually."

If `VERDICT: REJECTED` (3rd time):
- show remaining issues, same options (a/b/c)

### Step O5: Final Verification Phase

When all implementation phases are completed, execute the final verification phase (the Final Verification `**File:**` recorded in the main tasks file, e.g. `99-final-verification.md`) in the current orchestrator session:
- run the exact final verification commands listed in that phase file
- do not pipe a command's output through `tail`, `head`, or `grep`; redirect to a file and read it if it is long, or let it through unfiltered — piping deletes gradle's `actionable tasks: X executed, Y up-to-date, Z from-cache` summary and the `BUILD SUCCESSFUL in Xm Ys` line, so a cache replay becomes indistinguishable from a real run
- update that final verification file
- update the Final Verification status in the parent main tasks file
- do not continue if any required command fails

### Step O5.5: Post-Implementation Housekeeping (Orchestrator Only)

After all phases and final verification pass, the orchestrator runs Steps 4-6 once:
- Step 4: Review all completed phases for CLAUDE.md/AGENTS.md updates. Apply changes in a single pass.
- Step 5: Review all completed phases for ADR-worthy decisions. Create ADRs if needed.
- Step 6: Review all completed phases for memory candidates. Propose inline if found.

Workers never execute Steps 4-6.

### Step O5.7: Review Scout Findings (Orchestrator Only)

Read `scout-findings.md` (beside `progress.md`). If it is absent or empty, skip this step
silently. If it has entries, they are out-of-scope problems the workers surfaced but did not fix —
present the consolidated list to the user once and route each, do NOT silently swallow or
auto-fix:

- **Trivial one-liner** still open → offer to fix inline now.
- **Larger, but within this feature's spirit** → propose `generate-tasks` (fix tasks) or a direct fix with approval.
- **A separate concern / its own scope** → propose a separate `feature-discuss` (emit the full native command per `references/harness-command-contract.md`); do not fold it into the current change.
- **A latent bug needing root cause** → propose `debug`.
- The user may also defer (keep as a logged follow-up) or dismiss.

Mark each finding's disposition in `scout-findings.md` (e.g. `→ fixed`, `→ feature-discuss`,
`→ deferred`, `→ dismissed`) so a resumed session does not re-surface it. This step never blocks
Step O6: findings are separate scope from the current work's review gate.

### Step O6: Final Review Gate

After all phases and final verification pass, generate a whole-branch review package before dispatching the final gate — do not let the reviewer run its own `git diff`:

```bash
AP_TASKS_DIR=<phase-directory-from-Path-Resolution> skills/implement/scripts/review-package <branch-BASE> <HEAD=$(git rev-parse HEAD)>
```

`<branch-BASE>` is the `base7` of the earliest line in `progress.md` (the ledger) — the commit before Phase 1 started — so the package covers the full range of the orchestrated run, not just the last phase; if the ledger is empty or unavailable, fall back to `git merge-base HEAD main`. `AP_TASKS_DIR` is the same phase directory used in Step O4, set/export before invoking the script.

Run the existing final gate with an explicit `model="opus"` (the final gate is always the most-capable tier, per Step O2 — regardless of phase risk). Pass the exact parent tasks path and the review package path:

```
Agent(subagent_type="review-implementation", model="opus", prompt="Review implementation for orchestrated tasks: {parent-tasks-path}. Read all phase files referenced from Phase Overview and the final verification phase. Review package: {review-package-path}.")
```

> Codex: patrz `references/codex-tools.md` — dispatch generic z ciałem `agents/review-implementation.md`, lub review inline z advisory verdictem; nie literalny `Agent(subagent_type=...)`.
> Grok: patrz `references/grok-tools.md` — `spawn_subagent` + ciało `agents/review-implementation.md`, lub inline advisory; nie literalny `Agent(...)`.

If `VERDICT: PASS`, report completion.

If `VERDICT: REJECTED` (1st time): fix every `[BLOCKER]` issue (fix `[WARN]` only when cheap — warns never gate), rerun final verification if affected, regenerate the review package to cover the fix commits, then rerun `review-implementation` (`model="opus"`) PASSING the previous verdict and the fix list, so the gate accounts for old issues (FIXED/NOT-FIXED) and marks genuinely new findings `[NEW]`:

```
Agent(subagent_type="review-implementation", model="opus", prompt="Re-review implementation for tasks: {parent-tasks-path}. Previous verdict:\n{full previous verdict}\nApplied fixes:\n{issue #N → what changed}\nReview package: {review-package-path}.")
```

If `VERDICT: REJECTED` (2nd time — NOT-FIXED items or `[NEW]` blockers remain): show user options — (a) attempt fix again, (b) override review and proceed, (c) stop and investigate manually.

If `VERDICT: REJECTED` (3rd time): show remaining issues, same options (a/b/c).
