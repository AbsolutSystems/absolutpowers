# Project Memory — shared contract

**Read this file** when a skill says to create/promote memory entries
(`debug`, `review`, `implement`, `problem-discuss`). One source of truth —
do not reinvent formats per skill.

## Paths

| Artifact | Path |
|----------|------|
| Permanent memory (cross-cutting) | `./absolutpowers/project-memory.md` |
| Package-local trap | `{package}/CLAUDE.md` → `## Gotchas` (+ `AGENTS.md` mirror) |
| Candidate (complex) | `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md` |

## Scope routing — package-local vs global (decide BEFORE writing)

Global `project-memory.md` is loaded as root context. Do not clutter it with facts that only
matter inside one package. Before creating or promoting, classify the lesson's scope:

- **Package-local** — the trap only matters when working inside one package/module. Destination:
  that package's `CLAUDE.md`, under a dedicated `## Gotchas` section (compact format below), then
  refresh the sibling `AGENTS.md` mirror. Do **NOT** also add it to global `project-memory.md`.
  This surfaces the trap only when the AI enters that package and keeps root context clean.
  - If the package has no `CLAUDE.md`, create `{package}/CLAUDE.md` (+ `AGENTS.md`) to host it.
    Creation is still gated by the same promotion approval.
- **Cross-cutting / root** — spans multiple packages, or has no single package owner. Destination:
  global `./absolutpowers/project-memory.md` (permanent-entry format below).

**Decision test:** "Would someone need this only when editing files under package P?" → package-local.
"Does it warn across modules or at the repo level?" → global. When genuinely unsure, prefer
package-local (cheaper to promote later than to unclutter root).

Package-local `## Gotchas` entry is a living-doc note, not a status-tracked record — keep it compact
and edit in place (no `Added`/`Last verified`/`Status` churn):

```markdown
## Gotchas

### Short title of the trap
- Warning signs: ...
- Example: `path/to/file` — what goes wrong
- Resolution / workaround: ...
```

## When reading

- Use only entries with `Status: active` as operational context.
- Ignore `Status: superseded` and `Status: archived`.
- Memory is **prior context, not proof**. If memory conflicts with current
  evidence/code, trust the fresh evidence.

## When to create a candidate / entry

Create only when **ALL** are true:

- you uncovered a recurring trap, workaround, or warning sign
- the lesson is still useful after the current task/session
- content is general enough to help future work in the same codebase

**Do NOT** create memory for:

- temporary hypotheses that were disproven
- one-off incident timelines or branch-specific status
- environment states unlikely to recur
- facts that belong in `patterns.md`, `rules.md`, ADRs, or the tasks/planning file
- subjective style preferences (for review)

## Write the LESSON generally

Memory must transfer to **new** places, not only where it was found:

- **Problem / Root cause / Warning signs** = general **class** of problem
  (portable mechanism), not “file X line Y” as the whole lesson
- **Affected paths + this incident** = concrete **example**

**Test:** would someone in a different module recognize the trap from the
Warning signs alone? If not → too narrow. Don’t overshoot into vague
(“be careful with config”). Target: **general rule + portable warning signs
+ one concrete example.**

## Permanent entry format

Group by module section; every entry needs explicit affected paths:

```markdown
## path/to/module

### Short title of the trap
- Added: YYYY-MM-DD
- Source: {skill} / {context}
- Last verified: YYYY-MM-DD
- Status: active
- Problem: ...
- Symptoms: ...
- Root cause: ...
- Resolution: ...
- Warning signs:
  - ...
- Affected paths:
  - `path/to/file`
```

Superseded entries keep audit trail:

```markdown
### ~~Old title~~
- Added: YYYY-MM-DD
- Source: ...
- Last verified: YYYY-MM-DD
- Status: superseded (by: "New title", YYYY-MM-DD)
- ~~Problem: ...~~
- ~~Resolution: ...~~
- Affected paths:
  - `path/to/file`
```

Valid statuses: `active`, `superseded`, `archived`.

## Candidate file format

```markdown
# Memory Candidate: [Short title]

## Status
Candidate — YYYY-MM-DD

## Metadata
- Added: YYYY-MM-DD
- Source: {skill} / {context}
- Status: candidate

## Module
`path/to/module`

## Problem
...

## Symptoms
...

## Root Cause
...

## Resolution
...

## Warning Signs
- ...

## Affected Paths
- `path/to/file`

## Why This May Matter Again
...
```

## Promotion rules

- Promotion requires **explicit user approval**
- Route first (see **Scope routing**): a package-local trap is promoted to `{package}/CLAUDE.md` → `## Gotchas` (+ `AGENTS.md` mirror), never to global `project-memory.md`; only cross-cutting/root lessons go global. State the proposed destination when asking for approval.
- Prefer updating an existing matching entry over duplicating
- When promoting: set `Added`, `Source`, `Last verified`, `Status: active`
- If conflicting with an existing active entry: mark the old one
  `Status: superseded (by: "[new title]", [date])` with strikethrough on old title/content
- After successful promotion of a candidate file: **delete** the candidate
- Simple lessons may be promoted **inline** (2–4 lines → write directly to
  `project-memory.md` after approval) without a candidate file
- Complex lessons (multi-file RCA, many symptoms): write a candidate first, then ask
