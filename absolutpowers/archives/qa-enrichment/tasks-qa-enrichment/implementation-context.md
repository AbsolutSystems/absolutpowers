# Implementation Context: QA Enrichment — Acceptance Criteria w pipeline

## Purpose
Short handoff for phase workers. Keep this file concise. Add only facts that future phases need.

## Completed Phases
- Phase 1: QA Enrichment Agent and Feature-Discuss update — DONE
- Phase 2: Review-Plan AC Quality criterion — DONE
- Phase 3: Add AC Traceability to Generate-Tasks — DONE
- Phase 4: Add AC Coverage to Review-Tasks — DONE
- Phase 5: Add AC Awareness to Implement — DONE
- Phase 6: Add AC Fulfillment to Review-Implementation — DONE

## Created / Changed API

### `claude/agents/qa-enrichment.md` (NEW)
- Frontmatter: `name: qa-enrichment`, `model: sonnet`, `tools: [Read, Glob, Grep, Bash, Edit]`
- Spawned by Claude feature-discuss Faza 5B via: `Agent(subagent_type="qa-enrichment", prompt="Enrich planning document with Acceptance Criteria: ./absolutpowers/feature/planning-{slug}.md")`
- Appends `## Acceptance Criteria` section to planning doc with three subsections: `### Happy path`, `### Edge cases`, `### Security`
- AC format: `- AC-N: [behavioral description]` with sequential numbering starting at AC-1 across all categories
- Returns summary: "QA Enrichment complete. Added N Acceptance Criteria: Happy path: N items (AC-1 to AC-X) ..."
- Min 9 ACs (3 per category), max 15 ACs total
- Section placed after `## Edge cases i ryzyka`, before `## Pytania otwarte`

### `claude/skills/feature-discuss/SKILL.md` (MODIFIED)
- Added Faza 5B between Faza 5 (write planning doc) and Faza 6 (review-plan gate)
- Faza numbering: 5 → 5B → 6 → 7 (Faza 6 and 7 unchanged)
- Planning doc template now includes `## Acceptance Criteria` section with placeholder subsections

### `codex/skills/feature-discuss/SKILL.md` (MODIFIED)
- Added inline Faza 5B between Faza 5 (write planning doc) and Faza 6 (ADR)
- Inline: no agent spawn, 6-step process to generate ACs directly
- Produces identical AC format (AC-N numbering, same three categories)
- Planning doc template includes same `## Acceptance Criteria` section

## Decisions Made
- AC numbering is continuous across categories (AC-1 in Happy path, AC-4 in Edge cases, etc.) — not per-category reset
- `## Acceptance Criteria` section placed after `## Edge cases i ryzyka`, before `## Pytania otwarte`
- Claude and Codex versions intentionally differ (subagent vs inline) — `diff-skills.sh` will report `feature-discuss (differs)` — expected, not a defect
- AC rules enforced: behavioral/user-facing, zero implementation details, verifiable as true/false

### `claude/skills/generate-tasks/SKILL.md` (MODIFIED)
- Step 1 reads `## Acceptance Criteria` section from planning doc if present; extracts all `AC-N:` items
- Added `### AC Traceability` section after `## Analysis Requirements` with rules: every AC covered by at least one task, `**Traces to:** AC-N, AC-M` field on each task, infra tasks may use `**Traces to:** none (reason)`, final verification task traces to all ACs, graceful fallback when no AC section
- Single-file task template: `**Traces to:** AC-N, AC-M` field added after `**Status:** pending`, before `**Create:**`
- Orchestrated phase task template: `**Traces to:** AC-N, AC-M` field added after `**Status:** pending` in `### Task 1: [Action]` block
- "Good" example task: `**Traces to:** AC-2, AC-5` added after `**Status:** pending`

### `codex/skills/generate-tasks/SKILL.md` (MODIFIED)
- Same changes as Claude version; no agent-specific content

### `claude/agents/review-plan.md` (MODIFIED)
- Added `### 5. AC Quality` criterion after `### 4. Actionability`
- `AC_QUALITY` added to Categories line (full list: `COMPLETENESS, FEASIBILITY, ARCHITECTURE, ACTIONABILITY, AC_QUALITY`)
- Criterion checks: AC section exists, three categories present, behavioral/user-facing, verifiable, sequential numbering, reasonable coverage, no trivial ACs
- Graceful fallback: if `## Acceptance Criteria` section absent, flags `AC_QUALITY` issue with message "Acceptance Criteria section missing — QA enrichment may not have run"

## Constraints For Next Phases
- Phase 2 (review-plan AC Quality): The new review criterion must check ACs produced by qa-enrichment. ACs will be in `## Acceptance Criteria` with `### Happy path`, `### Edge cases`, `### Security` subsections. Category: `AC_QUALITY`.
- Phase 3 (generate-tasks traceability): Tasks must reference ACs by `AC-N` id (e.g. `Traces to: AC-1, AC-3`). Planning docs may NOT have AC section if feature was processed before this phase — implement graceful fallback (traceability optional when no AC section found).
- Phase 4 (review-tasks AC coverage): Must verify each AC-N has at least one task with `Traces to: AC-N`. Category: `AC_COVERAGE`.
- Phase 5 (implement AC awareness): Must read `## Acceptance Criteria` from planning doc at start, report fulfillment status. Graceful fallback when no AC section.
- Phase 6 (review-implementation AC fulfillment): Must verify each AC-N is fulfilled. Category: `AC_FULFILLMENT`.

### `claude/agents/review-tasks.md` (MODIFIED)
- Added AC coverage checks inside `### 1. Traceability`: extract `AC-N` from planning doc if `## Acceptance Criteria` present, verify every AC-N referenced by at least one task's `**Traces to:**` field, flag suspicious `**Traces to:** none` tasks, skip silently when no AC section
- `AC_COVERAGE` added to Categories line (full list: `TRACEABILITY, GRANULARITY, ORDERING, SPECIFICITY, VERIFICATION, CODE_REFERENCE, AC_COVERAGE`)
- AC_COVERAGE issue format: `[AC_COVERAGE] General — AC-3 ("description...") not covered by any task`
- Orchestrated tasks: AC traceability checked across all phase files, not just main index

### `claude/skills/implement/SKILL.md` (MODIFIED)
- Added `### Acceptance Criteria` subsection inside `## Context Files`: reads planning doc from `**Source doc:**` field, extracts `AC-N:` items; graceful fallback when no AC section
- Added `### Step 7B: AC Fulfillment Report` between Step 7 (Continue or Stop) and Step 8 (Review Gate): determines FULFILLED/PARTIAL/NOT VERIFIED per AC; informational only; skipped when no ACs
- Orchestrated mode note in Step 7B: runs after all phases + final verification, before Step O6
- AC Fulfillment output block added to Output Format section

### `codex/skills/implement/SKILL.md` (MODIFIED)
- Same `### Acceptance Criteria` subsection and `### Step 7B: AC Fulfillment Report` added
- No agent-specific content: Step 7B runs before completion summary, no review gate reference
- AC Fulfillment output block added to Output Format section
- `diff-skills.sh` reports `implement (differs)` — expected by design

### `claude/agents/review-implementation.md` (MODIFIED)
- Added `### 7. AC Fulfillment` section after `### 6. Safety`
- Criterion reads planning doc from `**Source doc:**` field or `## Source` section; extracts `AC-N:` items
- Reports per-AC: `FULFILLED` | `NOT VERIFIED` | `MISSING`; `NOT VERIFIED` and `MISSING` are blocking rejection reasons
- For orchestrated tasks: reads fulfillment across all phase files and main tasks file
- Graceful skip: no `## Acceptance Criteria` section in planning doc → criterion omitted silently
- `AC_FULFILLMENT` added to Categories line
- PASS verdict extended with optional `AC Fulfillment: N/N FULFILLED` summary line

## Verification History
- Phase 1: All Python assertions passed (qa-enrichment.md name, Claude Faza 5B + qa-enrichment + AC, Codex Faza 5B + AC)
- `diff-skills.sh` output: feature-discuss (differs) — expected by design
- Phase 3: Grep confirmed "AC Traceability" in both generate-tasks files; `**Traces to:**` present in single-file template, orchestrated template, and example task in both files; `diff-skills.sh` output: generate-tasks (differs) — expected (Claude has allowed-tools, argument-hint, Review Gate section)
- Phase 4: Grep confirmed `AC-N` and `Traces to` in Traceability section; `AC_COVERAGE` in Categories line; frontmatter valid (two `---` delimiters); all 6 criteria sections present
- Phase 5: Grep confirmed "Acceptance Criteria" reading instruction in both implement files; "AC Fulfillment" in output format in both files; `diff-skills.sh` output: implement (differs) — expected by design
- Phase 6: Grep confirmed "AC Fulfillment" section at line 76, "AC_FULFILLMENT" in Categories line at 119; frontmatter valid (two `---` delimiters); all 7 criteria sections present (### 1 through ### 7)
- Phase 7: All 4 grep verification checks passed (qa-enrichment in README agents table; Acceptance Criteria in getting-started; AC_QUALITY/AC_COVERAGE/AC_FULFILLMENT in review-gates; qa-enrichment in contributing)

## Phase 7 Documentation Changes
- `README.md`: pipeline diagram updated to show `feature-discuss (+ qa-enrichment)`; qa-enrichment row added to agents table; review agent criteria updated to list AC quality/coverage/fulfillment; feature-discuss and generate-tasks bullets updated
- `docs/getting-started.md`: QA Enrichment added as step 6 in Dyskusja phases (Review gate renumbered to 7); `Traces to: AC-N` note added to generate-tasks subsection; new Q&A on missing AC section added
- `docs/review-gates.md`: overview diagram shows qa-enrichment; new `## qa-enrichment` section (not a gate, enrichment agent); AC Quality subsection + AC_QUALITY category added to review-plan; AC Coverage subsection + AC_COVERAGE added to review-tasks; AC Fulfillment subsection + AC_FULFILLMENT added to review-implementation; Kategorie issues table updated with all new categories
- `docs/contributing.md`: `claude/agents/qa-enrichment.md` added to task-format cross-file update list; new "Agenci feature-discuss" table added distinguishing qa-enrichment from orchestrated implementation agents
