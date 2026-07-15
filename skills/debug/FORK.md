# Fork: `debug` vs vendored `systematic-debugging`

| | |
|--|--|
| **Canonical process** | `skills/debug/SKILL.md` |
| **MIT library sibling** | `skills/vendored/systematic-debugging/` |
| **Policy** | `references/fork-policy.md` |

## AbsolutPowers-only grafts in `debug`

- Handoff from `problem-discuss` (`problem-{slug}.md`)
- Large-fix exit → `planning-fix-{slug}.md` → `generate-tasks`
- Project memory via `references/project-memory.md`
- Trigger disambiguation vs `problem-discuss`

## Technique files

Prefer copies under `skills/debug/` (`root-cause-tracing.md`, `defense-in-depth.md`,
`condition-based-waiting.md`). They may intentionally differ from vendored twins
after AbsolutPowers edits — do not bulk-overwrite from vendor without review.

## Session bootstrap

`hooks/session-context.md` auto-triggers **`@debug` only** (not the vendored name).
