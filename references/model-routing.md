# Model routing: which model, and at what effort

**Read this file before any dispatch.** It owns the choice of `model` and `effort` for every role
this plugin spawns. Dispatch sites name the role and link here; they do not restate the table.
This file owns *what* model/effort to use; `references/harness-dispatch.md` owns *how* to dispatch
on the active harness — read both, they answer different questions.

## Two axes, and the order to reach for them

A dispatch has two dials, not one. **Raise effort before raising tier.** A harder problem usually
needs more thinking on the same model, not a more expensive model — and effort is the cheaper of
the two to be wrong about.

- **`model`** — which model runs the role.
- **`effort`** — how much reasoning it spends. Reach for `xhigh` on work where being wrong is
  discovered late, and leave it at `high` for work that fails fast and visibly.

**Always pass both explicitly.** A dispatch that omits them inherits whatever the session happens to
be running, which makes the routing unreproducible and silently different between a fresh session
and a resumed one.

## Implementation

| Work | Model | Effort |
|---|---|---|
| Transcription only — the phase file already contains the complete code to write | `haiku` | `high` |
| Default for a phase or task | `sonnet` | `high` |
| Work whose failure surfaces late, but not on the expensive-if-wrong list | `sonnet` | `xhigh` |
| `Risk: high`, or anything on the expensive-if-wrong list | `opus` | `xhigh` |

**Expensive-if-wrong** is a short, closed list, not a feeling: security and authorization,
multi-tenancy and data isolation, database migrations, shared core code many callers reach, money
arithmetic and rounding, and anything where a wrong answer is silent rather than loud.

**`Risk: high` and that list are the same thing seen from two sides**, and they must not be read as
two different rows: the planner writes `Risk: high` on the Phase Overview when it recognises this
work at planning time, and the list is what to check when the field is missing, stale, or set low by
someone who did not see what the phase actually touches. Either signal alone is enough for `opus`.
A missing or low `Risk` is never permission when the work is plainly on the list.

**Why this one row does not follow "raise effort before tier".** Everywhere else that order holds,
because a wrong tier costs a retry and the failure is visible. Here it is not: the failure mode of
this work is a wrong answer nobody notices, so the retry never happens and the saving is imaginary.

**The transcription tier has three guards, because it is the one row that can be wrong cheaply and
cost dearly.** It applies only when the phase file carries the complete code to write, so the work
really is transcription plus tests. It never applies to a phase on the expensive-if-wrong list, whatever
the phase file contains. And it is **never the fallback for doubt** — if it is unclear whether the code
in the phase file is complete, the answer is `sonnet`, not the cheaper tier. "It looks mechanical" is
exactly the judgement that is wrong when it matters.

Worth knowing when you reach for it: across the recorded history of this pipeline this tier has never
actually been dispatched. That does not make it wrong, but it does mean it is untested in practice
rather than proven — treat a first use as something to check, not as a routine choice.

## Gates and reviews

| Role | Model | Effort |
|---|---|---|
| `review-plan` | `opus` | `xhigh` |
| `review-tasks` | `opus` | `xhigh` |
| `review-implementation` | `opus` | `xhigh` |
| `phase-review` | `sonnet` `high` for a small mechanical diff; `opus` `xhigh` when the diff touches anything on the expensive-if-wrong list | |
| `triada-review` roles, `qa-reviewer`, `tech-debt-auditor`, `codebase-auditor` | `opus` | `xhigh` |

A gate that judges a whole artifact runs `opus`. The reason is not symmetry with the implementer —
it is that a gate's output is a verdict someone acts on, and a cheaper gate does not fail loudly, it
fails by reporting smaller things: line counts and naming where the expensive finding was a
correctness or isolation defect.

`phase-review` is the one role scaled to its input, because it runs once per phase and most phases
are ordinary. Scale it to the **diff**, not to the phase's declared risk — a low-risk phase can
still produce a diff that reaches shared code.

## Research, exploration, and mechanical work

| Work | Model | Effort |
|---|---|---|
| Pure lookup — find where a symbol lives, list files matching a pattern, count occurrences | `haiku` | `high` |
| Locating code, mapping a directory, gathering context to reason over | `sonnet` | `high` |
| Measurement or analysis whose conclusion will be acted on | `sonnet` | `xhigh` |
| Synthesis across several agents' findings | `opus` | `xhigh` |

The line between the first two rows is whether a wrong answer is **immediately visible**. "Which file
declares `FooService`?" is checkable in one step, so `haiku` is fine. "Which call sites would this
change break?" is a judgement whose error surfaces much later — that is `sonnet` at minimum, and a
negative answer ("nothing else uses it") needs an exhaustive scan whatever the model.

## Never self-select a model outside this table

If a task seems to call for a model this file does not name, that is a signal to ask, not to choose.
Say what the work is and why the table seems wrong for it.
