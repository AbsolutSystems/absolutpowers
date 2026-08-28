# Test scope policy: what to run, and when

**Read this file before writing a verification command into a plan, and before running one.** It
owns the choice of test scope and timing. Sites that verify link here; they do not restate it.

Deliberately free of any tool, task or command name — the rule is about scope and moment, so it
holds whatever the project's build tool is.

## Two axes, not one

**Scale scope to the change's blast radius, not to its size and not to the phase's declared risk.**
A small change in shared core has a wider radius than a large change in a new file nothing calls yet.

**Always state the command explicitly.** "Test it" without a scope means somebody picks a scope at
random, and the result stops being comparable between phases.

## Measure the radius before choosing the scope

Deciding to run everything is a measurement, not a hunch. Before you decide, count:

- constructors and call sites of the changed symbol, in production *and* test sources;
- specs that exercise the changed path;
- how many of those run the real dependency and how many mock it.

**A mock never executes the changed code, so it is not in the radius.** Record the count beside the
command you chose. Without it the next person inherits the conclusion and not the basis, and cannot
tell a measured decision from a guess.

## What to run

| Kind of change | Scope |
|---|---|
| New files nothing calls yet | Their own specs only |
| Signature, arity or type change — the failure is loud | Compile the test sources, plus the change's own specs |
| New behaviour lands under existing callers | Full unit suite |
| A semantic change a unit test cannot see | One scoped run against the real dependency |
| Closing the whole branch before review | Full unit suite plus the full integration suite |

## Run the full unit suite twice, not once per phase

Once in the phase where the changed behaviour **first** comes under existing callers, and once at
the end.

Not in every phase that changes behaviour. The second and third runs repeat the same measurement and
buy only finer attribution, while costing a full run each time.

If you skip an intermediate run, **write down the risk you accepted**: a regression from this phase
will surface later and with coarser attribution.

## Requires the full unit suite — closed list

- tightening a lenient shared type to fail loud;
- changing the behaviour of a symbol with many callers;
- changing a shared test base class or fixture;
- changing an ordering or a semantic that assertions outside the changed module rely on.

The common thread: **the changed class's own spec goes green and somebody else's breaks — one you
never opened.**

## Requires a run against the real dependency — closed list

- time and timezone boundaries;
- precision and rounding on the database side;
- types the driver binds differently from the language;
- generated queries, migrations and views;
- an HTTP contract, where the proof is the status code and the shape of the body.

A unit test asserts on a generated string and a bound object. It cannot show whether the database
actually matched a row.

**A newly written integration spec runs in the phase that wrote it, scoped to itself alone.** That
run is not for coverage — it verifies the spec: its seed data, its path, its authentication. A spec
that has never run is unverified, and the final gate is the most expensive moment to discover it.

## Know your test task before you rely on it

A task's name does not tell you what it runs. **Read its includes and excludes before you write a
command into a plan.**

An exclusion by glob means a spec named differently lands in a different task than its content
suggests: a spec that needs a container can run inside a task documented as fast and container-free,
and conversely, narrowing to that spec inside that task runs nothing at all.

**A command filtered to a spec the task excludes passes green having executed nothing.**

## A green run without a duration is not proof

**Report the elapsed time beside the exit code.** A suite that returns in seconds may have been
replayed from cache without executing a single test; the exit code is zero and the gate did not run.

When you suspect a cache, force execution and compare the **time**, not the result.

The same applies to narrowing: a run filtered to a pattern that matched nothing also exits zero.

## Frontend and backend are separate chains

One side's gate does not stand in for the other's, even when the change is single. Types generated
from the backend's contract are verified by the frontend build — not by the backend tests that
produced that contract.
