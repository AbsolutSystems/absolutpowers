# Code reference style: symbol over line number

**Read this file** before writing a comment or doc comment inside code, or before authoring/updating
a handoff or planning artifact (planning doc, tasks doc, phase file, `implementation-context.md`,
`progress.md`, ADR, module architecture doc). Two related problems, governed as one rule.

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
`implementation-context.md`, `progress.md`, ADRs, module architecture docs from `document-module`):
identify code by symbol name for the same reason — these are read again later, after further edits,
as a map of where things are. A line
number is permitted only when the referenced thing genuinely has no name (a specific line inside a
long literal, a migration body, a config block), and then only measured fresh at the moment of
writing that reference — never carried forward from an earlier draft.

**Reviews, findings, and reports are a third zone this rule does not touch**: `file:line` keeps
working there exactly as today. The dividing line between zone 2 and zone 3 is not an artifact's
label ("audit", "report") or how it gets superseded — that is at most a hint, and it points the
wrong way for a report that reuses its filename. What decides is the artifact's role **when it is
read**: consulted afterward as the current map of the code — navigated after further edits, expected
to still describe the code as-is (a module architecture doc's `zweryfikowane`/`wnioskowane` markers
included, an ADR read later as the binding reason the current design is the way it is) — is zone 2.
Read once to route a decision and then superseded, archived, or otherwise consumed, never navigated
as a map again — whether by overwriting the same path, versioning a new suffix, or dispositioning
entries in place — is zone 3, whatever its path or lifespan. Either zone's document may carry an
evidence/provenance trailer of what the author actually looked at (`file:line` is legitimate there,
even inside a zone-2 document); the instructional body a reader executes later against
by-then-changed code stays symbol-only. Do not assume otherwise from the two zones above — see the
full explanation and file list at the end of this document.

Doc comment *content* — what a doc comment should say, including the default one-sentence shape
and its named escapes — is a separate concern, owned by `references/doc-comment-style.md`; read
that file, not this one, before writing a doc comment.

## This does not narrow reviews, findings, reports, or commit messages

Reviews, review findings, audit/QA/tech-debt/debug reports, and commit messages keep using
`file:line` exactly as today — see `agents/review-implementation.md`, `agents/phase-review.md`,
`skills/debug/SKILL.md`, `skills/qa-review/`, `skills/tech-debt/SKILL.md`, `skills/analyze/SKILL.md`,
and, for the evidence trailer of its generated output, `skills/try-learn-skill/SKILL.md`. The
criterion above is why: they are read to route a decision, not navigated as a map afterward. Nothing
here changes that convention.
