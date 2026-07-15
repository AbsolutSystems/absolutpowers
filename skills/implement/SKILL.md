---
name: implement
description: >
  Senior Engineer executing tasks from ./absolutpowers/feature/tasks-*.md sequentially
  with TDD approach. Updates task status in-place, maintains CLAUDE.md source files,
  and keeps mirrored AGENTS.md files in sync as needed. Handles task files that live
  in an epic subfolder (feature/{epic-slug}/tasks-*.md) by resolving all derived paths
  relative to the tasks file location.
  TRIGGER when: tasks-*.md file exists and user wants to start implementation,
  "zacznij implementacje", "implement this", "build it", "execute the plan",
  after generate-tasks produces tasks-*.md.
  NIE wyzwalaj na: pisanie planu/tasków (to `generate-tasks`); review jakości brancha (to `review`/`triada-review`);
  commit/closeout (to `ship`); design feature'a (to `feature-discuss`).
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Agent
argument-hint: "[ścieżka do tasks-*.md]"
---

# Implement — Task Executor

You are a Senior Software Engineer implementing features based on a predefined task list. Your job is to execute tasks sequentially from the provided tasks file.

## Input

The argument should be a path to a tasks document: `./absolutpowers/feature/tasks-{slug}.md`

For a phase of an epic, the tasks file lives inside the epic subfolder:
`./absolutpowers/feature/{epic-slug}/tasks-{slug}.md`

Read this file to understand the project context and find pending tasks.

Tasks documents can use two modes:
- `single-file` or missing `## Mode` - legacy sequential task execution in this session
- `orchestrated` - main tasks file delegates phase files to fresh worker subagents

> **Harness dispatch:** before any worker/gate dispatch, read `references/harness-dispatch.md` (and the matching `references/{harness}-tools.md`). Roles: `implementation-worker`, `phase-review`, `review-implementation`.

## Path Resolution

**All derived paths in this skill are resolved relative to the directory that contains the main tasks file, not assumed to be `./absolutpowers/feature/`.**

- For a normal feature, the main tasks file is `./absolutpowers/feature/tasks-{slug}.md`, so the phase directory `tasks-{slug}/` sits at `./absolutpowers/feature/tasks-{slug}/`.
- For an epic phase, the main tasks file is `./absolutpowers/feature/{epic-slug}/tasks-{slug}.md`, so the phase directory sits at `./absolutpowers/feature/{epic-slug}/tasks-{slug}/`.

Wherever this document writes `./absolutpowers/feature/tasks-{slug}/...`, read it as shorthand for "the phase directory that sits beside the main tasks file." In orchestrated mode, **always prefer the explicit paths recorded in the tasks file itself** — the `**File:**` values under `## Phase Overview`, the `**Shared implementation context:**` path in Project Context, and the Final Verification `**File:**` — over reconstructing paths from a template. `generate-tasks` writes those with the correct (possibly epic-nested) location.

Global, project-wide paths are NOT relative to the tasks file and stay as written:
`./absolutpowers/patterns.md`, `./absolutpowers/rules.md`, `./absolutpowers/project-memory.md`, `./absolutpowers/memory-candidates/`, `./docs/adr/`.

## Context Files

Before starting implementation, also read (if they exist):
- **`./absolutpowers/patterns.md`** — established code patterns and conventions to follow
- **`./absolutpowers/rules.md`** — project rules to comply with
- **`./absolutpowers/project-memory.md`** — durable traps, warning signs, and workarounds discovered in previous tasks
- **`./absolutpowers/constitution.md`** — ratified project principles (pryncypia); implementation MUST respect these articles. If a task forces a violation, stop and surface it rather than silently breaking an article.

Use patterns as reference for HOW to implement. Follow rules as constraints.
Use project memory as prior operational context: apply it when relevant, but do not force old workarounds onto unrelated code.
When reading `project-memory.md`, use only entries with `Status: active` as implementation hints. Ignore entries with `Status: superseded` or `Status: archived`.

### Acceptance Criteria

After reading the tasks file, find the `**Source doc:**` field in the `## Project Context` or `## Source` section. Read that planning doc and extract all items from the `## Acceptance Criteria` section (lines matching `- AC-N: ...`).

- If the planning doc has an `## Acceptance Criteria` section: extract all `AC-N:` items and keep them in memory for fulfillment tracking.
- If no `## Acceptance Criteria` section exists: note that AC traceability is not available for this tasks file and proceed normally.
- **If the source doc is an epic phase doc** (commonly `planning-phase-N-{subslug}.md`, but do not rely on the filename): the AC live in that phase doc — extract them from there. Resolve the exact parent epic-planning path using this precedence: (1) `**Epic context:**` / `Epic context` in the tasks doc, (2) the explicit parent-planning link under the phase doc's `## Kontekst nadrzędny`, (3) a unique planning document in the same epic directory whose phase map references the current phase doc. If none or multiple match, report the ambiguity instead of assuming `planning-main.md`. Read the resolved `{epic-main-path}` for cross-cutting context; treat it as binding context, but do NOT re-derive AC from it — the main intentionally has none.

### Epic continuation context

When the source doc is an epic phase doc, keep the epic identity until the final output — do not
collapse it into a standalone feature at closeout:

1. Match the current phase against its row in `{epic-main-path}` using the phase number and the
   `Plan` path from `## Mapa faz`.
2. Read the ordered phase map and dependencies. Identify the next actionable sibling after the
   current phase, skipping rows already marked `Zrobiona`. Do not implement or plan that sibling
   inside this invocation.
3. Before printing the final handoff, inspect the sibling's phase doc and tasks artifact (if any)
   so the suggested workflow reflects durable state:
   - phase status `Do zaplanowania` or a stub/TODO doc → `@feature-discuss` with
     `{epic-main-path}` and that phase;
   - full phase doc ready, but no tasks doc → `@generate-tasks` on the phase doc;
   - tasks doc exists with pending/in-progress work → `@implement` on that tasks doc;
   - phase marked `Zrobiona` → skip it and evaluate the next row.
4. If the current phase cannot be matched, or dependencies make the next phase ambiguous, report
   the mismatch instead of guessing a phase.

This continuation lookup is routing only. The current phase still requires `@review` or
`@triada-review` before moving to the sibling phase.

#### Durable phase status in the epic planning document

Treat the current row in `## Mapa faz` as cross-session state, not decorative documentation:

- Immediately before the first code change or orchestrated worker dispatch, change the current
  phase status from `Zaplanowana` to `W toku`. If it is already `W toku` during a resume, preserve
  it. Do not modify sibling rows.
- After final verification and `review-implementation` PASS (or an explicit recorded override),
  run the Decision Review checkpoint below. With non-empty remarks, set the current phase to
  `Do akceptacji decyzji`; change it to `Zrobiona` only after human acceptance. With no remarks,
  change it directly to `Zrobiona` after generating the zero-decision report.
- On a blocker, failed/skipped final verification, or unresolved rejected gate, leave the status
  as `W toku`. Never mark a phase `Zrobiona` merely because its implementation tasks were attempted.
- If the phase row cannot be matched or the main update fails, report the state-sync failure
  explicitly. Do not claim that the epic roadmap is synchronized and do not guess the next phase.

`Zrobiona` means the phase passed the implement skill's complete tasks + final verification +
implementation-gate contract. The separate branch-level `@review`/`@triada-review` remains required.

## Project Memory

**Read** `references/project-memory.md` for when/how to capture and promote memory.
During implementation: durable lessons only; simple → inline ask; complex → candidate file.
Source label: `implement / tasks-{slug}.md (Task N)`.

## Mode Detection

After reading the tasks file:
1. Look for a `## Mode` section.
2. If mode is missing or `single-file`, use **Single-File Process**.
3. If mode is `orchestrated`, use **Orchestrated Process**.
4. If mode has any other value, stop and ask the user for clarification.

## Orchestrated Process

Use only when the main tasks file has `## Mode` set to `orchestrated`.

**Read and follow** `skills/implement/scripts/` tooling plus the full procedure in:

→ **`skills/implement/references/orchestrated-process.md`**

That file covers: durable ledger (`progress.md`), Steps O1–O6 (delegate worker → phase-review → final verification → housekeeping → review-implementation), model routing, `PHASE_RESULT` branches, and review-package wiring.

Path resolution and Context Files rules above still apply. Single-File Process below does **not** use O1–O6.

## Single-File Process

### Step 1: Read Tasks Document
- Read the tasks file provided as argument
- Understand the Project Context section
- **Interruption check:** if any task has `**Status:** in-progress`, a previous session died
  mid-task. Do NOT implement blindly on top of it: compare the task's `Create:`/`Modify:`
  lists against the actual repo state (which files exist, `git status`/`git diff`) and report
  what is already done vs missing. Ask the user: (a) finish the remaining part, (b) revert
  partial changes and redo, (c) mark `completed` if verification confirms it is in fact done.
- Otherwise find the first task with `**Status:** pending`

### Step 2: Implement the Task
Before touching any code, update the task's status in the tasks file from
`**Status:** pending` to `**Status:** in-progress` and save — this is the interruption
marker for a future session.

For the task:

1. **Review task requirements**
   - Read all sections: Create, Modify, Description, Requirements, Tests, Example
   - Check referenced files mentioned in the task

2. **Implement following the task's `**Test-first:**` marker** (see also `references/tdd-anti-patterns.md`)
   - `Test-first: yes` → write the tests from the **Tests:** section first, run them to confirm they FAIL, implement, run them to confirm they pass. The red run is part of the task — do not skip it.
   - `Test-first: no (reason)` → implement directly; still add any tests listed in **Tests:** afterwards.
   - Marker absent (older tasks doc) → decide yourself using the legacy rule: test-first for business logic, transformations, validation, pure functions; skip for configuration, simple wiring, scaffolding.
   - When a test covers a traced AC, embed the literal `AC-N` token in the test name / display name (e.g. `shouldRejectEmptyQuery_AC4`, `@DisplayName("rejects empty query [AC-4]")`) — the AC fulfillment check greps for these tokens.
   - Deviating from the marker is allowed ONLY with a reason recorded in **Implementation decisions / remarks** (e.g. "Test-first skipped: scaffold must exist before the test harness compiles"). A silent deviation is a review blocker.

3. **Verify completion**
   - All files created/modified as specified
   - All requirements met
   - All tests written and passing
   - Code follows patterns from referenced files

### Step 3: Update Status
After successful implementation, update the tasks file in-place:
- Change task status from `**Status:** in-progress` to `**Status:** completed`
- Fill in the "Implementation decisions / remarks" section if relevant
- Save the file

### Post-completion housekeeping (Steps 4-6)

Steps 4-6 run **once after ALL tasks are completed** (just before Step 7B), not after each individual task. Skip any step that does not apply — most tasks will not trigger any of them. Do not let housekeeping delay forward progress on remaining tasks.

**Orchestrated mode:** Workers do NOT update CLAUDE.md, AGENTS.md, or create ADRs. The orchestrator handles Steps 4-6 in a single pass after all phases and final verification complete.

### Step 4: Update CLAUDE.md Source Files (if applicable)
If the completed task introduced:
- New package/module → consider if it needs its own CLAUDE.md
- New important component → update package's CLAUDE.md
- New pattern or convention → update relevant CLAUDE.md
- Changed package responsibility → update package's CLAUDE.md

Keep updates minimal - only add what helps AI agents understand the area.

After updating any `CLAUDE.md`, also refresh the sibling `AGENTS.md` mirror in the same directory. `CLAUDE.md` remains the editable source of truth; `AGENTS.md` is the generated mirror for Codex.

### Step 5: ADR for Significant Decisions
If during implementation you made a **significant architectural decision** (deviated from plan, chose between non-trivial alternatives, discovered a constraint that changed approach), create an ADR:

**Path:** `./docs/adr/YYYY-MM-DD-{slug}.md`

Create `./docs/adr/` directory if it doesn't exist.

```markdown
# ADR: [Tytuł decyzji]

## Data
YYYY-MM-DD

## Status
Accepted

## Kontekst
[Jaki problem napotkaliśmy podczas implementacji?]

## Decyzja
[Co postanowiliśmy i dlaczego]

## Rozważane alternatywy
- **[Alternatywa]:** [opis] — odrzucona, bo [powód]

## Konsekwencje
- [Pozytywna konsekwencja]
- [Negatywna konsekwencja / tradeoff]

## Powiązane
- Tasks: `./absolutpowers/feature/tasks-{slug}.md` (Task N)
```

**Only for significant decisions** — not every implementation choice warrants an ADR. If the "Implementation decisions / remarks" section in the task captures it sufficiently, that's enough.

### Step 6: Project Memory Candidate (if applicable)
Follow `references/project-memory.md`. After all tasks/verification: no durable lesson → silent;
simple → inline ask + promote; complex → candidate file then promote. Source:
`implement / tasks-{slug}.md (Task N)`.

### Step 7: Continue or Stop
- If there are more pending tasks: proceed to next pending task (go to **Step 2** — skip Steps 4-6 until all tasks are done).
- If all tasks completed (including final verification task): run **Steps 4-6 as a batch** (review all completed tasks for CLAUDE.md updates, ADR candidates, and memory candidates). Then proceed to **Step 7B: AC Fulfillment Report**.

### Step 7B: AC Fulfillment Report

Skip this step entirely if no `## Acceptance Criteria` section was found in the planning doc.

For each `AC-N` extracted at startup, determine fulfillment status:
- `FULFILLED` — at least one task traces to this AC (via `**Traces to:** AC-N`), that task is `completed`, a grep over the project's test sources finds the literal `AC-N` token in at least one test name/annotation, and those tests pass
- `PARTIAL` — at least one task traces to this AC but the task is not `completed` or implementation is incomplete
- `NOT VERIFIED (untested)` — a task traces to this AC, but no test source contains the `AC-N` token
- `NOT VERIFIED (untraced)` — no task traces to this AC at all (plan-level gap that should have been caught before implementation)

Determine test coverage by grepping test sources for the `AC-N` token — not by judgment. If the tasks doc predates the token convention (no `**Test-first:**` fields anywhere), fall back to judgment-based mapping and say so explicitly in the report.

Print the fulfillment summary before proceeding to the review gate:

```
AC Fulfillment:
- AC-1: FULFILLED
- AC-2: FULFILLED
- AC-3: NOT VERIFIED (untested) — token `AC-3` absent from test sources
```

`NOT VERIFIED (untraced)` and legacy-mode results are informational. `NOT VERIFIED (untested)` is NOT — a traced AC without a token-matched test means the work is unfinished. Before proceeding to the review gate: write the missing test (smallest honest fix), or — if the AC is genuinely untestable at this level — record why in the tasks doc remarks and tell the user. Never proceed silently with untested traced ACs.

In orchestrated mode: AC fulfillment report runs once after all phases are complete and final verification passes, before the `review-implementation` gate (Step O6).

### Step 8: Review Gate — Automatyczna weryfikacja implementacji

Po zakończeniu WSZYSTKICH tasków (włącznie z final verification), uruchom subagenta `review-implementation`:

```
Agent(subagent_type="review-implementation", prompt="Review implementation for tasks: {parent-tasks-path}")
```

**Jeśli VERDICT: PASS:**
- Raportuj completion summary użytkownikowi
- Implementacja gotowa

**Jeśli VERDICT: REJECTED (1. raz):**
- Wyświetl listę problemów, napraw każdą pozycję `[BLOCKER]` (`[WARN]` tylko gdy tanie — warny nie bramkują), uruchom `review-implementation` ponownie PRZEKAZUJĄC poprzedni werdykt i listę poprawek:

```
Agent(subagent_type="review-implementation", prompt="Re-review implementation for tasks: {parent-tasks-path}. Previous verdict:\n{pełny poprzedni werdykt}\nApplied fixes:\n{issue #N → co zmieniono}")
```

**Jeśli VERDICT: REJECTED (2. raz — pozycje NOT-FIXED lub `[NEW]` blockery):**
- Pokaż: "Review odrzucił implementację po raz drugi (NOT-FIXED / nowe blockery). Opcje: (a) popraw ponownie, (b) override review i kontynuuj, (c) zatrzymaj się i zbadaj ręcznie."
- Jeśli (b): kontynuuj jak przy PASS, dodaj notatkę `**Review override:** [data]` w tasks doc

**Jeśli VERDICT: REJECTED (3. raz):**
- Pokaż pozostałe problemy i te same opcje (a/b/c)

### Step 9: Decision Review — human checkpoint

After `review-implementation` PASS/override and before the completion handoff, **read and follow**:

→ **`skills/implement/references/decision-report.md`**

It aggregates every `## Implementation Decisions / Remarks` entry, writes a human-readable HTML
report, persists `## Decision Review` in the main tasks doc, and requires human acceptance when
remarks are non-empty. Do not suggest the next phase, `@ship`, or branch review while that
checkpoint is `pending-human-review` or `changes-requested`.

---

## Rules

**Do:**
- Follow task order strictly - tasks are sequential and may depend on previous ones
- In orchestrated mode, advance only one phase at a time and wait for `phase-review` PASS before updating the parent phase status
- In orchestrated mode, resolve phase/context/verification paths from the explicit fields in the main tasks file (see Path Resolution) so epic-nested locations stay correct
- For an epic phase, persist `W toku`/`Do akceptacji decyzji`/`Zrobiona` in the matching `{epic-main-path}` row at the lifecycle points defined above
- Use referenced files as implementation patterns
- Match existing code style and conventions
- Run tests after implementation
- Execute the final verification task exactly as specified before declaring the whole tasks file done
- Update status only after verified completion

**Don't:**
- Skip tasks or change task order
- In orchestrated mode, let a worker update the parent main tasks status
- In orchestrated mode, let workers update CLAUDE.md, AGENTS.md, or create ADRs — the orchestrator handles this in Step O5.5
- In orchestrated mode, reconstruct phase paths from a template instead of using the `**File:**` fields — this breaks epic-nested task sets
- Start a later phase while the current phase is rejected, blocked, or unverified
- Implement beyond task scope
- Leave task as pending if completed
- Report overall completion if the final build/verification task failed or was skipped
- Proceed to next task if current one fails

---

## Alternative Solutions

If during implementation you identify a better approach than what's specified in the task:

1. **Stop** before implementing the alternative
2. **Explain** the alternative approach and why it's better
3. **Compare** trade-offs between task's approach vs your suggestion
4. **Ask** for preference before proceeding

Example:
```
Task suggests using [approach A], but I noticed [approach B] would be better because:
- [reason 1]
- [reason 2]

Trade-offs:
- Approach A: [pros/cons]
- Approach B: [pros/cons]

Which approach do you prefer?
```

Do not implement the alternative without confirmation.

---

## Error Handling

If you encounter a blocker:
1. Document the issue clearly
2. Explain what's blocking progress
3. Ask for guidance before proceeding

If tests fail after implementation:
1. Analyze failure reason
2. Fix the implementation
3. Re-run tests
4. Only mark completed when tests pass

---

## Output Format

When starting a task, briefly state:
```
Starting Task [N]: [Title]
```

When completing a task, briefly state:
```
Completed Task [N]: [Title]
- Created: [files]
- Modified: [files]
- Tests: [pass/fail status]
- Verification commands: [executed/not applicable/failed]
- CLAUDE.md / AGENTS.md: [updated + synced/no changes needed]
- Memory: [no durable lesson/candidate created at .../promoted to project-memory]
```

When all tasks are complete (Step 7B), include the AC Fulfillment section if ACs were found:
```
AC Fulfillment:
- AC-1: FULFILLED
- AC-2: FULFILLED
- AC-3: NOT VERIFIED (untested) — token `AC-3` absent from test sources
```

### Optional QA review nudge after PASS

After `review-implementation` returns PASS, evaluate this decision once before printing the
existing closeout guidance:

```text
shouldSuggestQAReview(signals) -> boolean
```

It returns `true` when `signals` contains at least one of:
- orchestrated implementation mode;
- a security, public API, migration, integration, or multi-module boundary;
- a new critical flow;
- a substantial test rewrite;
- a test-related warning from an implementation or review gate;
- an Acceptance Criterion that was difficult to verify.

For `true`, print exactly one best-effort suggestion using the most relevant signal and an
available planning/tasks artifact when useful:

```text
QA review (optional): elevated test-risk signal `<signal>`; run `@qa-review feature [optional planning/tasks artifact]` to statically evaluate test value without rerunning tests.
```

For `false`, emit no QA-review nudge. This nudge never auto-invokes or dispatches QA review,
never gates implementation completion, and never replaces `@review` or `@triada-review` as the
pipeline closure point. It does not change the closeout order selected below: a standalone/last
phase uses `review -> ship -> merge`; an epic in progress uses `review current phase -> continue epic`.

Structural scenarios:
- `highRiskImplementationSuggestsQaReview`: each signal enumerated above independently makes
  `shouldSuggestQAReview` return `true` and produces the one post-PASS suggestion.
- `lowRiskImplementationDoesNotSuggestQaReview`: an empty signal set returns `false` and produces
  no suggestion for a small routine change.
- `qaReviewNudgeIsOptionalAndNonBlocking`: the suggestion contains no automatic dispatch, does
  not affect PASS/completion, and preserves the applicable closeout/continuation branch.

### Completion handoff (best-effort)

After reporting completion, select exactly one branch.

**Standalone feature or last unfinished epic phase:** optionally suggest:

> Po PASS bramki implementacji: (1) `@review` lub `@triada-review`, (2) opcjonalnie
> `@analyze {slug}` (traceability AC→task→kod — on-demand, nie gate), (3) po czystym
> review: `/absolutpowers:ship @absolutpowers/feature/tasks-{slug}.md`.
> Docs/learned: ad-hoc (`@document-feature`, `@try-learn-skill`).

**Epic phase with another actionable phase:** print the current review step plus one concrete
continuation command. Example when the next phase is still a stub:

> Faza {N} epica jest zaimplementowana. Najpierw uruchom `@review` lub `@triada-review`
> dla bieżących zmian. Po czystym review epic nadal jest w toku — nie uruchamiaj jeszcze
> `@ship` jako closeoutu epica. Następny krok:
> `@feature-discuss @{epic-main-path} "Omów Fazę {N+1}: {nazwa}"`.

If durable state routes to `@generate-tasks` or `@implement`, substitute that exact command and
artifact path instead. Mention the current phase and the selected next phase by number and name.
Do not suggest `@ship` in this branch; it becomes appropriate only after all epic phases are
implemented and reviewed.

These handoffs are best-effort guidance. Do not auto-invoke them from this skill.

Structural scenarios:
- `epicPhaseWithUnplannedSiblingContinuesDiscussion`: a completed phase whose next row is
  `Do zaplanowania` prints review first, then an exact `@feature-discuss {epic-main-path} + phase`
  command, with no `@ship` suggestion.
- `epicParentPathIsReferenceDriven`: a nonstandard parent filename referenced by tasks/phase docs
  is updated and used in the handoff; no `planning-main.md` path is synthesized.
- `epicPhaseWithPreparedSiblingUsesDurableState`: a ready phase doc or existing incomplete tasks
  doc routes to `@generate-tasks` or `@implement` respectively, without restarting discussion.
- `finalEpicPhaseAllowsCloseout`: when no unfinished sibling remains, the handoff uses the normal
  `review -> optional analyze -> ship` branch.
- `epicPhaseStatusSurvivesContextReset`: starting implementation writes `W toku`; only successful
  verification, implementation gate, and required human decision acceptance write `Zrobiona`.
- `remarksRequireHumanDecisionReview`: non-empty remarks create an HTML report and durable pending
  checkpoint; rejected decisions return the affected work to `W toku` before re-verification.

---

## Terminal state

Stan terminalny tego skilla: wszystkie taski **bieżącego tasks-doca** zaimplementowane i zweryfikowane, final verification wykonana, końcowa bramka `review-implementation` zwróciła PASS (albo świadomy override), a raport decyzji implementacyjnych został wygenerowany. Przy niepustych remarks wymagany jest dodatkowo zapisany human acceptance w `## Decision Review`. Kod bieżącego zakresu jest napisany — ale jeszcze nie zrewidowany jako całość ani nie zmergowany.

Następny krok zawsze zaczyna się od `@review` (solo) lub `@triada-review` (multi-agent) dla bieżących zmian. Dalej:
- **standalone feature / ostatnia faza epica:** opcjonalnie `@analyze {slug}`, potem `@ship`; kolejność: review → ship → merge;
- **faza epica z kolejną fazą:** po czystym review wróć do epica zgodnie ze stanem następnej fazy (`@feature-discuss` na wykrytym `{epic-main-path}` + faza, `@generate-tasks` na gotowym phase docu albo `@implement` na istniejącym tasks-docu). Nie sugeruj `@ship`, dopóki wszystkie fazy epica nie są zaimplementowane i zrewidowane.

Docs/learned pozostają ad-hoc (`@document-feature`, `@try-learn-skill`).

Pipeline NIE jest domknięty na tym etapie — final gate PASS oznacza „kod bieżącego zakresu zaimplementowany i zweryfikowany wewnętrznie", nie „feature/epic dowieziony i zmergowany". Jeśli działasz pod `/goal` (np. „dowieź feature X"), NIE uznawaj celu za osiągnięty po tym skillu: dokończ review bieżącej zmiany, wszystkie pozostałe fazy epica (jeśli istnieją), a dopiero potem closeout/merge.

---

## Begin

Read the tasks file and start implementing the first pending task.
