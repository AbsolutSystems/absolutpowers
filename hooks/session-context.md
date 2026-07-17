# AbsolutPowers session discipline

Skills are invoked explicitly. Render every executable next-step command using the active
harness syntax below; never use `@skill-name` as a command prefix:

- Claude Code: `/absolutpowers:skill-name [args]`
- Codex: `$absolutpowers skill-name [args]`
- Pi: native skill invocation or the corresponding `SKILL.md` read action
- Grok Build: `/skill-name [args]`

Mandatory handoff contract: whenever a next step invokes a skill or passes a path, output one
standalone copy-pasteable command line with the native prefix and all arguments. Do not replace
it with prose, a bare skill name, or `@` before the skill/path. The full contract and examples
are in `references/harness-command-contract.md`.

In the shared pipeline description, skill names are written without a prefix:

`feature-discuss` -> `generate-tasks` -> `implement` -> `review` / `triada-review`
-> then close out with `ship` (commit + archive; not a gate).

Optional front door (fuzzy multi-item client report): `problem-discuss` → routes per case to
`debug` / `feature-discuss` / direct fix / close.

`review`/`triada-review` is the pipeline closure point; `ship` is the mechanical
closeout after it (local commit + artifact archiving), followed by push/merge (the human's
move). Each of the four pipeline skills declares its terminal state and the next explicit
step; a human (or a headless runner) triggers the transition by invoking the next skill.

## Skill map (quick)

| Need | Skill |
|------|--------|
| Client multi-item triage | `problem-discuss` |
| Design feature / epic phase | `feature-discuss` |
| Tasks from planning/review | `generate-tasks` |
| Execute tasks | `implement` |
| Code quality on branch | `review` or `triada-review` |
| AC↔task↔code consistency | `analyze` (on-demand) |
| Static test-value audit | `qa-review [feature [artifact] \| codebase [path]]` (on-demand) |
| Technical-debt backlog audit | `tech-debt [codebase \| path]` (on-demand) |
| Commit + archive feature | `ship` |
| Bug / test fail root cause | `debug` |
| Project principles | `constitution` |
| CLAUDE/AGENTS + rules scan | `update-ai-context` |
| Module prose from feature | `document-feature` |
| Module C4 from code | `document-module` |
| Ephemeral HTML explain | `explain` |
| Mine learned skills | `try-learn-skill` |
| PR review feedback | `receiving-code-review` |

`qa-review` is a read-only specialist audit, never a pipeline gate: it inspects test value
statically without running tests, measuring coverage, or editing code. Use `qa-review` for the
current feature, `qa-review feature absolutpowers/feature/planning-auth.md` for an explicit
artifact, `qa-review codebase` for logical-area synthesis across the repository, or
`qa-review codebase skills/generate-tasks` for a bounded module. An empty current feature stops
without a report; it never expands into a whole-codebase audit. Reports are immutable
`absolutpowers/reviews/qa-review-{scope}-YYYY-MM-DD-HHmmss.md` files with rubric-derived verdicts
and stable `Actionable Findings`; route decisions first (`FEATURE_DISCUSS`), then separately
approved `INLINE_FIX`, then `GENERATE_TASKS`, and finally re-run the audit. The canonical finding
contract and calibration live only in `skills/qa-review/references/testing-rubric.md`.

`tech-debt` is a read-only, static audit of accumulated maintainability cost—not a current-branch
review, deep test-value audit, or bug investigation. Use `tech-debt` / `tech-debt codebase` for
the project, or `tech-debt path/to/module` for a strict scope. It writes one immutable
`absolutpowers/reviews/tech-debt-{scope}-YYYY-MM-DD-HHmmss.md` backlog with evidence, ongoing
cost, priority, bounded effort, and a route to `FEATURE_DISCUSS`, `GENERATE_TASKS`, `DEBUG`, or
`WATCH`; it never implements its recommendations.

If this session was already mid-skill (an active checklist/todo, an implementation phase,
a pending gate) — return to that checklist and resume instead of starting fresh. This
matters most right after a context compaction, when the original explicit invocation no
longer protects you.

Auto-trigger ONLY for these guardian skills, whose right moment can't be scheduled ahead:
- Before proposing a fix for a bug/error/unexpected behavior -> **`debug`**
  (canonical; do not prefer vendored `systematic-debugging` name).
- Before claiming code works, tests pass, or a task is complete -> the vendored
  `verification-before-completion` skill; show the evidence.
