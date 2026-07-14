# Grok Tool Mapping

> Parallel to `references/codex-tools.md` and `references/pi-tools.md`. AbsolutPowers has registered gate agents
> (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`,
> `qa-enrichment`, `implementation-worker`) that Grok does not know about — the
> "Review gates on Grok" and "Orchestrated dispatch on Grok" sections below are
> AbsolutPowers content.

Skills speak in actions ("dispatch a subagent", "invoke a review gate", "run an
orchestrated phase", "read a file"). On Grok these resolve to the primitives below.

**No `Agent(subagent_type=...)` on Grok.** `Agent(subagent_type="review-tasks", ...)`,
`Agent(subagent_type="implementation-worker", ...)`, etc. are a **Claude Code plugin
primitive**: they resolve a registered agent type from `agents/*.md`. Grok has **no
registry of named agent types** (it uses `spawn_subagent` + `subagent_type` + optional
personas). Never emit a literal `Agent(subagent_type=...)` when the current harness/context
is Grok — translate it via this file instead.

Grok has excellent built-in **Claude Code compatibility** (it auto-scans `~/.claude/skills/`,
`CLAUDE.md`, Claude-style hooks, etc.). Many things will "just work" through that layer.
This document describes the **native first-class path**.

| Action skills request | Grok equivalent |
| --- | --- |
| `Skill` tool / invoke a skill | Grok has native skill support. Skills from the plugin appear as `/<skill-name>` (or qualified `plugin:absolutpowers:<name>`). Load `SKILL.md` content when needed; the model follows the body directly. |
| Dispatch a subagent (`Agent(subagent_type=...)` template) | Use the `spawn_subagent` tool. Provide `subagent_type: "general-purpose"` (or `"explore"` / `"plan"` when the role matches). Pass the target `agents/{name}.md` body as (part of) the prompt/instructions, plus the same arguments the skill would have passed. See "Subagents" and "Orchestrated dispatch on Grok" below. |
| Review gate (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) | No registered agent types. See "Review gates on Grok" below. |
| Task tracking ("create a todo", "mark complete", `TodoWrite`) | Use an installed todo/task tool if available, otherwise track state in the tasks/phase files already produced by `generate-tasks`, or a repo-local `TODO.md`. |

## Subagents

Grok uses the `spawn_subagent` tool (enabled by default). The child gets its own context
window. You choose the child via `subagent_type` (built-ins: `general-purpose`, `explore`,
`plan`; project/user-defined agents in `.grok/agents/` or config are also possible).

The *dispatch pattern* (read an `agents/*.md` body and hand it to a fresh subagent) is
portable. Only the *registered named type* mechanism is Claude-only.

To dispatch a subagent on Grok:

1. Read the target `agents/{name}.md` file (the prompt body).
2. Call `spawn_subagent` (or equivalent `task` tool in some contexts) with:
   - `subagent_type`: usually `"general-purpose"` (or a more specific built-in when it fits the role).
   - Prompt/instructions: the content of `agents/{name}.md` + the concrete arguments (tasks file path, phase file, etc.).
   - Optional: persona for tone/contract if defined.
3. Receive the child's summary/result when it finishes.

If subagent dispatch is unavailable or undesired, do not fabricate `Agent(...)` calls —
execute the work **sequentially/inline in the current session** and state so explicitly.

Personas (`.grok/personas/*.toml` or config) can be layered for behavior without changing
the agent type.

## Review gates on Grok

AbsolutPowers' pipeline skills (`feature-discuss`, `generate-tasks`, `implement`) call
Claude Code registered agent types by name (e.g. `Agent(subagent_type="review-tasks", ...)`).
Those do not exist on Grok.

Degradation path, in order of preference:

1. **If `spawn_subagent` is available (the normal case):** dispatch a generic subagent.
   Read the target `agents/{name}.md` and use its body as the instructions/prompt for the
   child, together with the exact arguments the original gate would have received (planning
   doc path, tasks file + phase files, implementation-context, etc.). The subagent should
   return a clear `VERDICT: PASS` or `REJECTED` with the usual issue list.

2. **If subagent dispatch is not practical:** perform the review **inline**, in the current
   session, using the same `agents/{name}.md` content as your instructions. State
   **explicitly** in the output that "this was not a fully isolated gate — the reviewing
   context was not fresh, so treat the verdict as **advisory** rather than a hard gate."

Either way, **do not skip the review step silently**. Always surface a verdict (PASS /
REJECTED) and the reasoning.

Grok's strong Claude compatibility layer may make some `Agent(...)` calls work
transparently in some environments. When writing for Grok, prefer the explicit native path
above and mention `references/grok-tools.md`.

## Orchestrated dispatch on Grok

`implement` in `orchestrated` mode dispatches `implementation-worker` per phase, then
`phase-review`, then a final `review-implementation`.

On Grok, translate each dispatch through the two-tier fallback:

- **Preferred:** Use `spawn_subagent` (usually `subagent_type: "general-purpose"`) for each
  phase worker, feeding the body of `agents/implementation-worker.md` (plus the phase file
  path, parent tasks path, `implementation-context.md`, etc.). Then spawn for `phase-review`
  and finally `review-implementation` the same way. Preserve the file ownership contract
  (worker updates only its phase file + `implementation-context.md`; the orchestrator
  updates parent phase status in the index).

- **Fallback (no convenient subagents or to keep context small):** execute the phase files
  **sequentially/inline in the current session**, preserving the same contracts. For each
  pending phase:
  0. Mark `pending` → `in-progress` in the parent.
  1. Follow the Read/Write scope in the phase file.
  2. Implement only the declared work.
  3. Run verification.
  4. Update status and remarks inside the phase file only.
  5. Compact-update `implementation-context.md` (≤10 lines added).
  6. Mark the phase `completed` in the parent.
  7. Run the corresponding review **inline** (see "Review gates on Grok") as an advisory
     gate before advancing — never skip silently.

  After all phases, run the Final Verification phase inline, followed by post-work
  housekeeping (AGENTS.md/CLAUDE.md, ADRs, memory candidates) and the final advisory
  `review-implementation` gate.

Never emit a literal `Agent(subagent_type=...)` in Grok context. Route every dispatch
through one of the two tiers above and always surface a verdict.

## Session bootstrap and project rules on Grok

Grok automatically loads project rules from `AGENTS.md` (and `CLAUDE.md` / `Claude.md` via
compatibility). `update-ai-context` already produces both, so the core project memory and
many conventions are present on every Grok session in a repo that has run it.

The shared `hooks/session-context.md` (the short pipeline-chain reminder + "return to
in-progress" rule + guardian skill nudges) is still valuable. Grok supports hooks
(`.grok/hooks/*.json` and plugin-bundled hooks) and Claude-compat hook scanning. The
primary discipline for Grok users comes from:
- The skills themselves (their `description` for auto-invocation + full body + `## Terminal state` prose).
- The generated `AGENTS.md` / `CLAUDE.md`.
- Explicit invocation of the skills (`/feature-discuss`, `/generate-tasks`, etc.).

If you want the exact `session-context.md` text injected on SessionStart in Grok, you can
configure a project or plugin hook (see Grok hooks docs). The content of
`hooks/session-context.md` remains the single source of truth — do not duplicate it.

## Task tracking

Grok does not mandate a specific todo tool. Use any installed task/todo extension when
available; otherwise keep state inside the `tasks-*.md` / phase files produced by
`generate-tasks`, or a local `TODO.md`. Older `TodoWrite` references should be treated as
this general task-tracking action.

## Summary rule for skill authors

When the active harness/context is Grok (or the user is running under Grok Build):
- Never emit the literal `Agent(subagent_type=...)` form.
- For subagent / gate work, either:
  - `spawn_subagent` (general-purpose) with the body of the corresponding `agents/{name}.md` plus arguments, **or**
  - run the work inline and clearly label the result "advisory (not a fully isolated gate)".
- Always surface a PASS/REJECTED-style verdict.
- Prefer the native Grok path described here; the Claude compatibility layer is a bonus, not the documented contract.

See the main `CLAUDE.md` / `README.md` "Platform Differences" and "Adding a New Harness"
sections for the overarching rules that apply to every harness.
