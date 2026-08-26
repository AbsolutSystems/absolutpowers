# Code reference style: symbol over line number

**Read this file** before writing a comment or doc comment inside code, or before authoring/updating
a handoff or planning artifact (planning doc, tasks doc, phase file, `implementation-context.md`,
`progress.md`, ADR). Two related problems, governed as one rule.

## Why

A line number is a coordinate into a snapshot of a file. It goes stale the moment anything above it
changes, and nothing warns you when it does — the reference just becomes silently wrong. This has
already cost real work on this project: a full quality-gate round was spent on stale anchors in one
epic's later phase, and a handoff document's references had to be re-measured because they had
drifted.

## Rule 1 — identify code by name, not line — three zones

**Inside code** (comments, doc comments/javadoc): never write a line number. Point at the class,
method, function, field, or constant by name — `// see calculateTotal()`, not `// see line 214`.

**In handoff and planning artifacts** (planning docs, tasks docs, phase files,
`implementation-context.md`, `progress.md`, ADRs): identify code by symbol name for the same
reason — these are read again later, after further edits, as a map of where things are. A line
number is permitted only when the referenced thing genuinely has no name (a specific line inside a
long literal, a migration body, a config block), and then only measured fresh at the moment of
writing that reference — never carried forward from an earlier draft.

**Reviews, findings, and reports are a third zone this rule does not touch**: `file:line` keeps
working there exactly as today. Do not assume otherwise from the two zones above — see the full
explanation and file list at the end of this document.

## Rule 2 — a doc comment should not restate the signature

The signature already states the parameter names and the return type. A doc comment that only
repeats them in prose adds nothing and is one more thing that can go stale. Say what the signature
cannot express instead: invariants, units, ownership, failure modes, or why a surprising choice is
that way. This is not license to skip documenting — it redirects effort toward the part of a doc
comment that actually carries information.

## This does not narrow reviews, findings, reports, or commit messages

Reviews, review findings, audit/QA/tech-debt/debug reports, and commit messages keep using
`file:line` exactly as today — see `agents/review-implementation.md`, `agents/phase-review.md`,
`skills/debug/SKILL.md`, `skills/qa-review/`, `skills/tech-debt/SKILL.md`, `skills/analyze/SKILL.md`,
and `skills/try-learn-skill/SKILL.md`. Those are records of what was true at the moment of writing —
a reviewer citing `file:line` is being precise about what they looked at, not building a map for
someone else to navigate the codebase by later. Nothing here changes that convention.
