---
name: debug
description: >
  Systematic debugging process — root cause investigation before any fixes.
  4 phases: root cause, pattern analysis, hypothesis testing, implementation.
  TRIGGER when: bug report, error message, test failure, "nie dziala", unexpected behavior,
  stack trace, CI failure, regression, crash, exception, "why does X return Y",
  flaky test, performance degradation, "something broke", "doesn't work".
  NIE wyzwalaj na: mgliste wieloelementowe zgłoszenie klienta (to `problem-discuss`);
  nowy feature bez buga (to `feature-discuss`); review jakości brancha (to `review`).
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Agent
argument-hint: "[opis buga lub błąd]"
---

# Systematic Debugging

> **vs `problem-discuss`:** `debug` to **głębokie** dochodzenie pojedynczego, znanego failure
> (error / stack trace / test fail / cicha rozbieżność, którą już zidentyfikowano). Jeśli masz
> **mgliste, wieloelementowe zgłoszenie od klienta**, w którym nie wiadomo jeszcze, czy każda
> sprawa to bug, gap featurowy, błąd danych czy nieporozumienie — zacznij od `problem-discuss`
> (intake + triage), który sklasyfikuje sprawy i odeśle potwierdzone bugi tutaj.

## Handoff Input

**OPTIONAL — only applies when invoked with a path to a `problem-{slug}.md` file.**

If invoked with a path to `absolutpowers/problem/problem-{slug}.md` (and optionally a case
number, e.g. `"Sprawa 2"`), read that file **BEFORE Phase 1** and use the named case's evidence
as the Phase 1 starting point:

- reguła biznesowa (contract / expected behavior)
- flow przejścia (step-by-step trigger path)
- `file:line` references found in the investigation
- facts extracted from attachments

**What this means:** confirm and deepen — do NOT re-derive from zero. Phase 1 still happens in
full, but you start with evidence already gathered by `problem-discuss` rather than a blank slate.

**When no path is given:** start Phase 1 normally. Zero regression for solo debug invocations.

**Edge cases:**
- Multi-case file + no case number given → ask which case before reading evidence.
- Evidence from `problem-discuss` contradicted by deeper investigation → trust the fresh
  evidence; note the divergence explicitly in your response (consistent with "memory is context,
  not proof").

**Iron Law is unchanged.** The handoff gives a head start; it does not waive root-cause
investigation. Debug may refute problem-discuss's preliminary hypothesis — with evidence.

## Context Files

Before starting investigation, also read (if they exist):
- **`./absolutpowers/project-memory.md`** — durable traps, warning signs, and workarounds discovered in earlier tasks

Use project memory as prior context, not as a substitute for fresh evidence. If memory conflicts with current evidence, trust the evidence.
When reading `project-memory.md`, use only entries with `Status: active` as investigation context. Ignore entries with `Status: superseded` or `Status: archived`.

## Project Memory

**Read** `references/project-memory.md` for read rules, formats, and promotion.
Debugging often yields high-value lessons — only durable traps belong in memory.
Source label: `debug / {bug or CI context}`.

At end of session: if a durable lesson exists, create a candidate (or promote simple
lessons after approval). See `references/project-memory.md` → Promotion rules.

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

5. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

**Step 0: Classify fix size (run once, at the start of Phase 4)**

Before writing any code, classify the fix using the same heuristic as `generate-tasks`
single-file vs orchestrated:

- **Small** — 1 file / 1 layer, no migration, no public API change, no security boundary,
  no shared-core impact → **inline** (proceed to steps 1–3 below as today).
- **Large** — multiple layers/modules, database migration, public API change, security
  boundary, shared-core impact, OR any Phase 4.5 escalation (3+ fixes failed /
  architectural problem) → **do NOT implement inline**. Write
  `absolutpowers/feature/planning-fix-{slug}.md` and route to generate-tasks (see template
  below and Phase 4.5 for escalation path).

**Borderline small/large → choose handoff** (gates > ungated inline fix). Justify the choice
explicitly in your response.

**Threshold = same heuristic as single-file vs orchestrated in `generate-tasks`.** One size
model across the whole pipeline.

---

**`planning-fix-{slug}.md` template** (write to `absolutpowers/feature/`):

```markdown
# Fix: {short description}

## Problem
{root cause with evidence — file:line, mechanism, NOT just symptoms}

## Wybrane rozwiązanie
{chosen fix approach}

## Zakres
{files / layers / modules affected}

## Acceptance Criteria
{optional but recommended for large fixes — what must be true after the fix;
root cause defines expected post-fix behavior, which maps naturally to AC
and enables downstream Intent Fidelity / AC Fulfillment checks}
```

After writing `planning-fix-{slug}.md`, nudge:
Wypisz jedną pełną, copy-paste'owalną komendę `generate-tasks` z `absolutpowers/feature/planning-fix-{slug}.md` w składni aktywnego harnessu zgodnie z `references/harness-command-contract.md`.

Do NOT implement the fix inline. Stop here and let the pipeline take over.

---

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No bundled refactoring
   - Identify code in comments by symbol name, not line number — see `references/code-reference-style.md`.
   - Before writing a doc comment, see `references/doc-comment-style.md` — one sentence by default, more lines only for a named reason.
   - Boy-scout rule for anything you spot nearby: a strictly trivial one-liner (typo,
     missing/dead import, obvious null-check — one line, no semantic risk) fix inline and note
     it; anything larger, name it (`file:line`, what is wrong) and ask the user whether to fix
     rather than silently patching or staying quiet. Keep it out of the root-cause fix itself.

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture (Phase 4.5)**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   This is NOT a failed hypothesis — this is a wrong architecture. Discuss the architectural
   question with the user. Then, regardless of whether you continue the same approach or pivot,
   **escalate through the artefact exit**:

   Write `absolutpowers/feature/planning-fix-{slug}.md` capturing:
   - current root cause (with `file:line` evidence)
   - failed hypotheses and what each revealed (valuable context for generate-tasks)
   - architectural question / pivot decision

   Nudge: wypisz jedną pełną, copy-paste'owalną komendę `generate-tasks` z `absolutpowers/feature/planning-fix-{slug}.md` w składni aktywnego harnessu zgodnie z `references/harness-command-contract.md`.

   This is automatically a **Large** fix (3+ failed attempts = architectural scope). Do NOT
   attempt Fix #4 inline. The pipeline with its gates is the correct path forward.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5)

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Classify fix size → small: inline (test, fix, verify); large: write `planning-fix-{slug}.md`, route to `generate-tasks` | Bug resolved (small) or handed off to pipeline (large) |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

Canonical AbsolutPowers debug path (see `references/fork-policy.md`). Vendored `systematic-debugging` is the MIT library sibling — prefer techniques in **this** directory.

Available in this directory:

- **`root-cause-tracing.md`** — Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** — Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** — Replace arbitrary timeouts with condition polling

## Memory Capture at the End

Follow `references/project-memory.md`. If a durable lesson was found: write candidate
and ask about promotion; if none, do nothing. Apply **Scope routing** first — a package-local
trap is promoted to that package's `CLAUDE.md` → `## Gotchas` (+ `AGENTS.md` mirror), not to
global `project-memory.md`; state the destination when asking.

## Terminal state

Stan terminalny zależy od rozmiaru fixa (Phase 4 Step 0):

| Wynik | Oddaje | Dalej |
|-------|--------|-------|
| Small fix inline | root cause + fix + tests green | opcjonalnie wypisz pełną natywną komendę `review` jeśli branch feature; done dla hotfixu |
| Large / 3+ failed | `planning-fix-{slug}.md` | wypisz pełną natywną komendę `generate-tasks` na tym pliku zgodnie z `references/harness-command-contract.md` |
| Routed from problem-discuss | potwierdzony/obalony root cause | jak wyżej; zaktualizuj understanding w odpowiedzi |

Nie kończ sesji na „quick patch" bez Phase 1. Iron Law obowiązuje do końca.
