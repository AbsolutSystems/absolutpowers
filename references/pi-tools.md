# Pi Tool Mapping

> Adapted from `obra/superpowers` (`skills/using-superpowers/references/pi-tools.md`, MIT
> License) — see `VENDORED.md`. Reworded for AbsolutPowers: no `using-superpowers`
> dispatcher exists here, and AbsolutPowers has registered gate agents (`review-tasks`,
> `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`,
> `implementation-worker`) that Pi does not know about — the "Review gates" section below
> is new content, not present in the upstream file.

Skills speak in actions ("dispatch a subagent", "invoke a review gate", "create a todo",
"read a file"). On Pi these resolve to the tools below.

| Action skills request | Pi equivalent |
| --- | --- |
| `Skill` tool / invoke a skill | Pi has no `Skill` tool. Load the relevant `SKILL.md` with `read` when the skill applies, or let a human invoke `/skill:name` explicitly. |
| Dispatch a subagent (`Agent(subagent_type=...)` template) | Use an installed subagent tool such as `subagent` from `pi-subagents` if available. |
| Review gate (`review-tasks`, `review-plan`, `review-implementation`, `phase-review`, `qa-enrichment`) | These are Claude Code **registered agent types** — they do not exist as such on Pi. See "Review gates on Pi" below. |
| Task tracking ("create a todo", "mark complete", `TodoWrite`) | Use an installed todo/task tool if available, otherwise track tasks in the plan file or a repo-local `TODO.md`. |

## Triada review on Pi

`triada-review` is a shared skill. If `pi-subagents` is installed, dispatch the active
roles as independent generic agents (parallel when supported), feeding each the full body
of its matching `agents/{name}.md` prompt plus the package context prepared by the skill.
Without a subagent extension, run the perspectives inline and label the result
`advisory (not fully isolated)`.

## Subagents

Pi core does not ship a standard subagent tool. The `pi-subagents` package is a strong
optional companion and provides a `subagent` tool with single-agent, chain, parallel,
async, forked-context, and resume/status workflows. If no subagent tool is available, do
not fabricate `Task`/`Agent` calls; execute the work sequentially in the current session
or explain that the optional subagent capability is not installed.

## Review gates on Pi

AbsolutPowers' pipeline skills (`feature-discuss`, `generate-tasks`, `implement`) call
Claude Code **registered agent types** by name — e.g.
`Agent(subagent_type="review-tasks", prompt=...)`. Those agent type registrations
(`agents/*.md`) are a Claude Code plugin mechanism; Pi has no equivalent registry, so the
literal `subagent_type` values do not resolve.

Degradation path, in order of preference:
1. **If `pi-subagents` (or another subagent tool) is installed:** dispatch a generic
   subagent and pass it the target agent's prompt content as the task — read the relevant
   `agents/{name}.md` file and use its body as the subagent's instructions, plus the same
   arguments the skill would have passed (tasks file path, phase file path, etc.).
2. **If no subagent tool is installed:** perform the review inline, in the current
   session, using the same `agents/{name}.md` content as your instructions. State
   explicitly in the output that this was *not* a fully isolated gate — the reviewing
   context was not fresh, so treat the verdict as advisory rather than as a hard gate.

Either way, do not skip the review step silently — always surface a verdict (PASS /
REJECTED) and the reasoning, even when the isolation guarantee is degraded.

## Task lists

Pi core does not ship a standard task-list tool. If a todo/task extension is installed,
use its documented tool. Otherwise use the tasks/phase files already produced by
`generate-tasks`, or a repo-local `TODO.md`, for task tracking. Older references to
`TodoWrite` should be treated as this task-tracking action.
