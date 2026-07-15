# Phase 1: Ruch 1 — Intent Fidelity gate + feature-discuss source nudge

## Status
completed

## Parent
`./absolutpowers/feature/tasks-cross-artifact-analyze.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`
- `./absolutpowers/feature/planning-cross-artifact-analyze.md` (sections "Ruch 1", "Zależność: Intent Fidelity czyta z czystego kontekstu")

## Context Contract

### Requires (from previous phases)
- None (independent of other phases; may run first).

### Provides (for later phases)
- `claude/agents/review-tasks.md` has a new criterion `### 7. Intent Fidelity` under `## Review Criteria` and `INTENT` added to the Categories line of the Response Format.
- `feature-discuss` (both trees) instructs that the feature GOAL/intent MUST be written explicitly into the planning doc's Problem/Cel section (rationale: downstream Intent Fidelity gate reads only the saved doc).

## Read Scope
- `claude/agents/review-tasks.md`
- `claude/skills/feature-discuss/SKILL.md`
- `codex/skills/feature-discuss/SKILL.md`
- `claude/skills/review/SKILL.md` (reference: existing criterion/verdict style)

## Write Scope
- `claude/agents/review-tasks.md`
- `claude/skills/feature-discuss/SKILL.md`
- `codex/skills/feature-discuss/SKILL.md`

## Objective
Add a semantic (non-mechanical) Intent Fidelity criterion to the `review-tasks` gate so it flags task sets that cover every requirement literally but miss the plan's goal. Add a matching source-side nudge to `feature-discuss` (both trees) so the intent is always written into the planning doc — without it the gate is blind.

## Tasks

### Task 1: Add criterion #7 Intent Fidelity + INTENT category to review-tasks gate
**Status:** completed

**Modify:**
- `claude/agents/review-tasks.md`

**Description:**
The `review-tasks` agent runs with a fresh context and judges the tasks doc against the saved planning doc only. Add one judgment criterion that evaluates whether the task set as a whole achieves the plan's GOAL, plus a new verdict category so the issue can be reported.

**Requirements:**
- Under `## Review Criteria`, after the existing `### 6. Code References`, add a new section `### 7. Intent Fidelity` with exactly this content:
  ```markdown
  ### 7. Intent Fidelity
  - The task set as a whole achieves the GOAL/intent of the planning doc, not just literal
    per-requirement coverage. Read the planning doc's problem statement and chosen solution,
    then judge: if an agent executed exactly these tasks, would the feature's intent be met?
  - Flag when tasks technically cover each requirement but collectively miss the point
    (e.g. plan wants "users self-serve password reset"; tasks build the endpoint but no email
    delivery — every requirement "checked", intent unmet).
  - This is a judgment criterion, not a checklist. Only flag a CLEAR intent gap, not stylistic
    preference. When the intent is genuinely met, do not invent gaps.
  ```
- In the Response Format `Categories:` line, append `INTENT` to the existing list (`TRACEABILITY, GRANULARITY, ORDERING, SPECIFICITY, VERIFICATION, CODE_REFERENCE, AC_COVERAGE, INTENT`).
- For an epic phase, judge intent against the phase doc's goal (plus `planning-main.md` for shared context), not against sibling phases. Add a one-line note to this effect inside criterion #7 if the existing epic-phase handling sections make it natural; otherwise keep criterion #7 as the canonical block above.
- Do not change any other criterion or the PASS/REJECTED format.
- This is Claude-only (Codex has no gates) — do NOT create a Codex equivalent of `review-tasks`.

**Tests:**
- `grep -n "### 7. Intent Fidelity" claude/agents/review-tasks.md` returns one hit.
- `grep -n "INTENT" claude/agents/review-tasks.md` shows it in the Categories line.
- The PASS/REJECTED `## Response Format` block is otherwise unchanged.

### Task 2: Add intent-into-planning-doc nudge to feature-discuss (both trees)
**Status:** completed

**Modify:**
- `claude/skills/feature-discuss/SKILL.md`
- `codex/skills/feature-discuss/SKILL.md`

**Description:**
The Intent Fidelity gate reads intent only from the saved planning doc. If the goal lives only in conversation, the gate is blind. Add a short, explicit reminder in feature-discuss that the GOAL/intent must land in the planning doc's Problem/Cel section. Reinforces the existing CLAUDE.md "dokumentacja jako produkt — samodzielna" principle.

**Requirements:**
- Add a concise reminder (Polish, matching surrounding tone) near where the doc-writing / Problem section is described (around the `## Problem` template or the "CO i DLACZEGO" guidance) stating: the feature's goal/intent MUST be written explicitly into the planning doc's Problem/Cel section, because the downstream `review-tasks` Intent Fidelity gate reads a fresh context and only sees what the doc records — intent that stays in conversation is invisible to it.
- Apply the SAME content to both `claude/` and `codex/` files (this is shared logic, not Claude-only). Keep wording identical between the two files so `diff-skills.sh` shows only pre-existing expected frontmatter drift.
- Do not restructure the planning-doc template; add a one- to three-line note, not a new section.

**Tests:**
- `grep -ni "intent fidelity\|review-tasks" claude/skills/feature-discuss/SKILL.md` returns a hit referencing the gate.
- The same reminder text exists in the codex file (`diff` of the two reminder paragraphs is empty).

## Phase Verification
Run:
- `grep -n "### 7. Intent Fidelity" claude/agents/review-tasks.md`
- `grep -ci "review-tasks" claude/skills/feature-discuss/SKILL.md codex/skills/feature-discuss/SKILL.md`
- `./scripts/diff-skills.sh` (feature-discuss should still show only expected frontmatter drift)

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Criterion #7 inserted verbatim from the phase spec after `### 6. Code References`, with an
  additional fourth bullet for the epic-phase case ("judge against phase doc's goal plus
  planning-main.md, not sibling phases"), as permitted by the requirement.
- `INTENT` appended to the Categories line in `## Response Format`; no other format changes made.
- Nudge placed in the `## Format: standardowy planning doc` template's `## Problem` section
  (immediately after `[Co chcemy rozwiązać i dlaczego]`) as a blockquote. This is the most
  natural place: it sits at exactly the point where the writer fills in the goal, making it
  impossible to miss. Polish tone matches the surrounding template text.
- Identical nudge text in both `claude/` and `codex/` trees — `diff-skills.sh --diff` shows
  no new drift for the nudge paragraph; only pre-existing expected frontmatter and subagent
  differences appear in the feature-discuss diff.
