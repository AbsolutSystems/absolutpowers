# Harness dispatch for review gates / workers

**Read this** before any `Agent(subagent_type=...)` call in AbsolutPowers
skills (`feature-discuss`, `generate-tasks`, `implement`, and any skill that
dispatches registered agents).

| Harness | How to dispatch |
|---------|-----------------|
| **Claude Code** | Registered agent types work as written: `Agent(subagent_type="{name}", ...)`. Names: `qa-enrichment`, `review-plan`, `review-tasks`, `implementation-worker`, `phase-review`, `review-implementation`, plus triada roles. |
| **Codex** | No agent-type registry. Do **not** emit literal `Agent(subagent_type=...)`. Prefer `spawn_agent` with the body of `agents/{name}.md` as the prompt; if multi-agent is unavailable, run the gate **inline** in this session with an **advisory** verdict. Never skip a gate silently. Details: `references/codex-tools.md`. |
| **Pi** | Use `pi-subagents` with the body of `agents/{name}.md`, or inline advisory with an explicit isolation disclaimer. Details: `references/pi-tools.md`. |
| **Grok** | Use `spawn_subagent` with `subagent_type: "general-purpose"` and the body of `agents/{name}.md` as instructions (or inline advisory). Never emit Claude’s literal `Agent(...)`. Details: `references/grok-tools.md`. |

**Rule:** isolation of the gate (fresh context) is preferred; when isolation is
impossible, an inline review with a stated “advisory / non-isolated” note is
acceptable — silent omission is not.
