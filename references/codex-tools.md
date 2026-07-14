# Codex Tool Mapping

> Parallel to `references/pi-tools.md`. AbsolutPowers has registered gate agents
> (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`,
> `qa-enrichment`, `implementation-worker`) that Codex does not know about — the
> "Review gates on Codex" and "Orchestrated dispatch on Codex" sections below are
> AbsolutPowers content, not present upstream.

Skills speak in actions ("dispatch a subagent", "invoke a review gate", "run an
orchestrated phase", "read a file"). On Codex these resolve to the primitives below.

**No `Agent(subagent_type=...)` on Codex.** `Agent(subagent_type="review-tasks", ...)`,
`Agent(subagent_type="implementation-worker", ...)`, etc. are a **Claude Code plugin
primitive**: they resolve a registered agent type from `agents/*.md`. Codex has **no
registry of named agent types**, so those literal calls resolve to nothing. Never emit a
literal `Agent(subagent_type=...)` on Codex — translate it via this file instead.

| Action skills request | Codex equivalent |
| --- | --- |
| `Skill` tool / invoke a skill | Codex has no `Skill` tool. Load the relevant `SKILL.md` with a file read when the skill applies, or let a human invoke it explicitly. |
| Dispatch a subagent (`Agent(subagent_type=...)` template) | If `multi_agent=true`: `spawn_agent` with the target `agents/{name}.md` body as the prompt, then `wait_agent` / `close_agent`. Otherwise: run the work **sequentially/inline in the current session**. See "Subagents" and "Orchestrated dispatch on Codex" below. |
| Review gate (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) | Claude Code **registered agent types** — no equivalent registry on Codex. See "Review gates on Codex" below. |
| Task tracking ("create a todo", "mark complete", `TodoWrite`) | Use an installed todo/task tool if available, otherwise track state in the tasks/phase files already produced by `generate-tasks`, or a repo-local `TODO.md`. |

## Subagents

Codex exposes subagent dispatch when `multi_agent=true`: `spawn_agent` / `wait_agent` /
`close_agent`. What it lacks is the **registry** — there is no way to name
`subagent_type="implementation-worker"` and have it resolve to `agents/implementation-worker.md`.

So the *dispatch pattern* is portable; only the *named type* is Claude-only. To dispatch a
subagent on Codex:

1. Read the target `agents/{name}.md` file.
2. `spawn_agent` and pass that file's body as the subagent's instructions, plus the same
   arguments the skill would have passed (tasks file path, phase file path, shared context
   path, etc.).
3. `wait_agent` for its result, read the returned verdict/handoff, then `close_agent`.

If `multi_agent` is **not** available, do not fabricate `Agent`/`Task`/`spawn_agent` calls —
execute the work sequentially in the current session (see below) and say so.

## Review gates on Codex

AbsolutPowers' pipeline skills (`feature-discuss`, `generate-tasks`, `implement`) call
Claude Code registered agent types by name — e.g.
`Agent(subagent_type="review-tasks", prompt=...)`. Those registrations (`agents/*.md`) are a
Claude Code plugin mechanism; Codex has no equivalent registry, so the literal
`subagent_type` values do not resolve.

Degradation path, in order of preference:
1. **If `multi_agent` / `spawn_agent` is available:** dispatch a generic subagent and pass it
   the target agent's prompt content as the task — read the relevant `agents/{name}.md` file
   and use its body as the subagent's instructions, plus the same arguments the skill would
   have passed (tasks file path, phase file path, etc.). `wait_agent` for its verdict.
2. **If no subagent capability is available:** perform the review inline, in the current
   session, using the same `agents/{name}.md` content as your instructions. State
   **explicitly** in the output that this was *not* a fully isolated gate — the reviewing
   context was not fresh, so treat the verdict as **advisory** rather than as a hard gate.

Either way, do not skip the review step silently — always surface a verdict (PASS /
REJECTED) and the reasoning, even when the isolation guarantee is degraded.

## Orchestrated dispatch on Codex

`implement` in `orchestrated` mode dispatches `implementation-worker` per phase, then
`phase-review`, then a final `review-implementation` — all as Claude registered agent types.
On Codex, translate each dispatch through the two-tier fallback above:

- **If `multi_agent` is available:** `spawn_agent` per phase with the body of
  `agents/implementation-worker.md` as the prompt, plus the exact parent tasks path and the
  phase `**File:**` path from Phase Overview. Then `spawn_agent` `agents/phase-review.md` and
  finally `agents/review-implementation.md` the same way. Preserve the file ownership contract
  (worker updates only its phase file + `implementation-context.md`; the orchestrator updates
  parent phase status).
- **If `multi_agent` is NOT available:** execute phase files **sequentially/inline in the
  current session**, preserving the same file contracts (this reproduces the pre-5.0
  `codex/skills/implement` behavior). For each pending phase:
  0. Set the phase status in the main tasks file `pending` → `in-progress` (interruption
     marker).
  1. Follow the phase Read Scope and Write Scope.
  2. Implement only the tasks inside the phase file.
  3. Run the phase verification commands.
  4. Update task statuses inside the phase file only after verification passes.
  5. Fill `Implementation Decisions / Remarks` in the phase file.
  6. Update `implementation-context.md` with concise handoff facts (≤10 lines per phase).
  7. Verify all `## Context Contract -> Provides` items are fulfilled.
  8. Update the parent phase status `in-progress` → `completed`.
  9. Run the review **inline** as an advisory gate (see "Review gates on Codex") before
     advancing — do not skip it silently.

  Then run the Final Verification phase in the current session, followed by post-implementation
  housekeeping (CLAUDE.md/AGENTS.md, ADRs, memory) once, and the inline advisory
  `review-implementation` gate.

Never emit a literal `Agent(subagent_type=...)` on Codex — it resolves to nothing. Route
every dispatch through one of the two tiers above and always surface a verdict.
