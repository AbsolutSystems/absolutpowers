---
name: debug
description: >
  Systematic debugging process — root cause investigation before any fixes.
  4 phases: root cause, pattern analysis, hypothesis testing, implementation.
  TRIGGER when: bug report, error message, test failure, "nie dziala", unexpected behavior,
  stack trace, CI failure, regression, crash, exception, "why does X return Y",
  flaky test, performance degradation, "something broke", "doesn't work".
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Agent
argument-hint: "[opis buga lub błąd]"
---

# Systematic Debugging

> **vs `problem-discuss`:** `debug` to **głębokie** dochodzenie pojedynczego, znanego failure
> (error / stack trace / test fail / cicha rozbieżność, którą już zidentyfikowano). Jeśli masz
> **mgliste, wieloelementowe zgłoszenie od klienta**, w którym nie wiadomo jeszcze, czy każda
> sprawa to bug, gap featurowy, błąd danych czy nieporozumienie — zacznij od `problem-discuss`
> (intake + triage), który sklasyfikuje sprawy i odeśle potwierdzone bugi tutaj.

## Context Files

Before starting investigation, also read (if they exist):
- **`./absolutpowers/project-memory.md`** — durable traps, warning signs, and workarounds discovered in earlier tasks

Use project memory as prior context, not as a substitute for fresh evidence. If memory conflicts with current evidence, trust the evidence.
When reading `project-memory.md`, use only entries with `Status: active` as investigation context. Ignore entries with `Status: superseded` or `Status: archived`.

## Project Memory

Debugging often uncovers high-value lessons, but most raw notes should NOT become permanent memory.

Create a memory candidate only when ALL of these are true:
- the investigation was non-trivial
- it uncovered a recurring trap, workaround, or warning sign
- the lesson is likely to help future debugging or implementation in the same codebase

Do NOT create memory entries for:
- temporary hypotheses that were disproven
- one-off incident timelines
- environment states that are unlikely to recur
- details that belong only in the current bug report or commit history

When a durable lesson is worth capturing, use:
- candidate path: `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md`
- permanent memory path: `./absolutpowers/project-memory.md`

`project-memory.md` should be grouped by module, but each entry must also include explicit affected paths:

```markdown
## infra/ci

### Signing identity missing inside nested build step
- Added: 2026-02-20
- Source: debug / CI release failure
- Last verified: 2026-02-20
- Status: active
- Problem: workflow secret exists, but nested script cannot see it
- Symptoms: signing fails only in CI, env looks correct in top-level workflow
- Root cause: env var was never passed into the nested build invocation
- Resolution: forward the variable explicitly through the wrapper script
- Warning signs:
  - secret shows as set in workflow logs
  - nested process prints env as missing
- Affected paths:
  - `.github/workflows/release.yml`
  - `scripts/build-release.sh`
```

### Write the LESSON generally — keep specifics as the example

Memory must transfer to NEW places, not only where it was found. So:
- **Problem / Root cause / Warning signs** = the general CLASS of problem — a portable rule that applies to another module/file of the same nature. Capture the *mechanism*, not "file X line Y".
- **Affected paths + this incident** = the concrete EXAMPLE (where it first showed up), not the lesson itself.

Test: would someone working in a DIFFERENT module recognize this trap from the Warning signs alone? If not, it is too narrow — generalize the mechanism, keep one concrete example. Do not overshoot into uselessly vague ("be careful with config") either. Target: **general rule + portable warning signs + one concrete example.**

Candidate file template:

```markdown
# Memory Candidate: [Short title]

## Status
Candidate — YYYY-MM-DD

## Metadata
- Added: YYYY-MM-DD
- Source: debug / [bug / failing test / CI issue]
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

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

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

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with the user before attempting more fixes**

   This is NOT a failed hypothesis - this is a wrong architecture.

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
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

Available in this directory:

- **`root-cause-tracing.md`** — Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** — Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** — Replace arbitrary timeouts with condition polling

## Memory Capture at the End

After the debugging session is complete:
- If you did NOT uncover a durable, reusable lesson: do nothing
- If you DID uncover one: create `./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md`
- In your final response, explicitly ask the user whether to promote that candidate into `./absolutpowers/project-memory.md`

Promotion rules:
- Promotion requires explicit user approval
- Update an existing matching memory entry instead of duplicating it
- After successful promotion, delete the candidate file
