# AbsolutPowers session discipline

Skills are invoked explicitly with `@skill-name` — there is no auto-dispatcher. Keep the
pipeline chain in mind:

`@feature-discuss` -> `@generate-tasks` -> `@implement` -> `@review` / `@triada-review`
-> then close out with `@ship` (commit + archive; not a gate).

`@review`/`@triada-review` is the pipeline closure point; `@ship` is the mechanical
closeout after it (local commit + artifact archiving), followed by push/merge (the human's
move). Each of the four pipeline skills declares its terminal state and the next explicit
step; a human (or a headless runner) triggers the transition by invoking the next skill.

If this session was already mid-skill (an active checklist/todo, an implementation phase,
a pending gate) — return to that checklist and resume instead of starting fresh. This
matters most right after a context compaction, when the original explicit invocation no
longer protects you.

Auto-trigger ONLY for these guardian skills, whose right moment can't be scheduled ahead:
- Before proposing a fix for a bug/error/unexpected behavior -> `@debug` (or the vendored
  `systematic-debugging` skill).
- Before claiming code works, tests pass, or a task is complete -> the vendored
  `verification-before-completion` skill; show the evidence.
