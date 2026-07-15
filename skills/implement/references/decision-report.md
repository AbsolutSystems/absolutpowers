# Implementation decision review

Run this checkpoint after final verification and `review-implementation` PASS/override, before
the normal completion handoff. It is a human review of implementation choices, not another code
quality gate.

## 1. Collect decisions and remarks

Read the main tasks doc and every referenced phase/task file. Collect all non-empty content under
`## Implementation Decisions / Remarks` or the equivalent task-level field. Preserve source task,
file, and original wording. Do not silently discard remarks as trivial.

Assign stable IDs in task order: `DEC-001`, `DEC-002`, ... For each entry, verify the affected
code/diff and distinguish:

- recorded fact;
- implementation choice within the plan;
- deviation from the plan;
- unresolved concern or assumption.

Explain rationale, alternatives (when known), downstream repercussions, risk level, reversibility,
and what the human is being asked to accept. Mark inference explicitly; never invent rationale.

## 2. Write the HTML report

Create `docs/onboarding/implementation-decisions-{slug}-YYYY-MM-DD.html`. If it exists, add
`-v2`, `-v3`, etc. Never overwrite an earlier review. Use a self-contained Polish HTML document
with inline responsive light/dark CSS; Mermaid via CDN only when a diagram materially clarifies
three or more related consequences.

Put these sections in order:

1. TL;DR with decision count and overall risk.
2. **Decyzje wymagające akceptacji** near the top: one card per `DEC-N`, source, original remark,
   verified context, rationale, alternatives, repercussions, risk, reversibility, recommendation,
   and explicit `Akceptuję / Proszę zmienić` question.
3. Cross-decision interactions and cumulative consequences.
4. Informational remarks and implementation facts.
5. Missing/ambiguous rationale and questions for the human.
6. Evidence map: task/phase file plus affected code paths.

If there are zero non-empty remarks, still generate a short report saying so and warning if
completed tasks unexpectedly lack the section. Do not manufacture decisions.

## 3. Persist the checkpoint

Add or update exactly one section in the main tasks doc:

```markdown
## Decision Review
- Report: `docs/onboarding/implementation-decisions-{slug}-YYYY-MM-DD[-vN].html`
- Decisions: DEC-001, DEC-002  <!-- `none` when empty -->
- Status: pending-human-review | accepted | changes-requested
- Reviewed: YYYY-MM-DD | pending
- Notes: [accepted scope or requested changes]
```

With non-empty remarks, set `Status: pending-human-review`, set the epic phase row (if applicable)
to `Do akceptacji decyzji`, show the report path and decision count, then stop for the user's
response. Do not print later-phase, review, analyze, or ship guidance yet.

With zero remarks, set `Status: accepted`, `Decisions: none`, explain that no human decision gate
was needed, set the epic phase to `Zrobiona`, and continue to the normal handoff.

## 4. Handle the human response

- Accept all: set `Status: accepted`, record date/notes, set the epic phase to `Zrobiona`, then
  print the normal completion handoff.
- Request changes for any `DEC-N`: set `Status: changes-requested`, record IDs and requested
  outcome, set the epic phase back to `W toku`, reopen the affected task(s), implement the agreed
  change, rerun relevant tests, final verification, and `review-implementation`, then emit a new
  versioned report.
- Partial/ambiguous response: keep `pending-human-review` and ask only about unresolved IDs.

On resume, read `## Decision Review` before generating anything. Reuse an existing pending report
instead of creating a duplicate; continue from its durable status.
