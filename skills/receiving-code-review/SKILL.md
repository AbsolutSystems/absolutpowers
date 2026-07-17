---
name: receiving-code-review
description: >
  Handle incoming code review feedback (human or bot) with technical rigor:
  verify against the codebase before implementing, clarify unclear items,
  push back when wrong for this stack, implement one fix at a time with tests.
  TRIGGER when: PR review comments, "address review", "fix review feedback",
  "komentarze z review", "popraw po review", "reviewer said", GitHub review thread,
  CodeRabbit/bot review, "odnieś się do review".
  NIE wyzwalaj na: wykonywanie pełnego review brancha (to `review`/`triada-review`);
  generowanie tasków z raportu review (to `generate-tasks` na pliku review).
allowed-tools: Read, Glob, Grep, Edit, Write, Bash(git:*), Bash(gh:*)
argument-hint: "[opcjonalnie: URL/PR number lub wklejona lista punktów review]"
---

# Receiving Code Review

Adapted from obra/superpowers `receiving-code-review` (MIT — see `LICENSE-VENDORED`)
and aligned with AbsolutPowers gates.

**Core principle:** Verify before implementing. Ask before assuming. Technical
correctness over social comfort.

## Input

`$ARGUMENTS` may be a PR number/URL, a path to a review report, or pasted comments.

$ARGUMENTS

## Response pattern

```
1. READ    — full feedback without reacting
2. UNDERSTAND — restate each item (or ask)
3. VERIFY  — check against THIS codebase (and rules.md / constitution if relevant)
4. EVALUATE — sound for this stack? YAGNI? conflicts with prior decisions?
5. RESPOND — technical ack or reasoned pushback
6. IMPLEMENT — one item at a time, test each
```

## Forbidden

- Performative agreement ("You're absolutely right!", "Great point!", empty thanks)
- Implementing before verification
- Partial batch: do not implement 1–3 while 4–5 are unclear

## Unclear items

If any item is unclear: **STOP**, list what you understand vs what needs
clarification, wait. Items may be related.

## Source-specific

| Source | Stance |
|--------|--------|
| Project owner / human partner | Trusted after understanding; still ask on scope |
| External human reviewer | Skeptical verify: correctness, regressions, platform, full context |
| Bot (CodeRabbit, etc.) | Same as external; high false-positive rate — verify hard |

If feedback conflicts with an explicit prior decision (ADR / planning / constitution
article): stop and discuss with the user before changing architecture.

## YAGNI

If reviewer asks to "implement properly" a surface that is unused: grep for
callers. If unused, propose remove (YAGNI) instead of expanding scope.

## Implementation order

1. Clarify all unclear items first
2. Blocking (breaks, security)
3. Simple fixes (typos, imports)
4. Complex (logic, refactors)
5. Test each fix; avoid silent multi-fix commits without evidence

For **3+ non-trivial** items that map to a feature still in pipeline: prefer a complete,
copy-pasteable native `generate-tasks` command on a short fix list or on
`absolutpowers/reviews/….md` rather than ad-hoc thrash — then emit a complete native
`implement` command. Follow `references/harness-command-contract.md` for both handoffs.

## Push back when

- Breaks existing functionality or tests
- Reviewer lacks full context
- Technically wrong for this stack
- YAGNI / conflicts with ADR or ratified constitution article

Push back with evidence (`file:line`, tests), not defensiveness.

## GitHub threads

Reply in the **inline comment thread** when using `gh`, not only as a top-level
PR comment:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body='...'
```

## AbsolutPowers wiring

| Situation | Skill |
|-----------|--------|
| You are writing the review | `review` / `triada-review` |
| You received feedback to address | **this skill** |
| Feedback is large structured report | emit one full native `generate-tasks` command on the report, then one full native `implement` command |
| Root-cause bug buried in feedback | emit one full native `debug` command with the relevant report/context |

For every route rendered to the user, follow `references/harness-command-contract.md`.

## Terminal state

Stan terminalny: każdy zaakceptowany punkt review jest albo **zafiskowany i
zweryfikowany testem/dowodem**, albo **odparty z uzasadnieniem** (i ustalone z
użytkownikiem). Nie zostawiaj pół-zaimplementowanej listy.

Następny krok (jeśli to domknięcie feature'a): wypisz pełną natywną komendę `review` ponownie
jeśli diff duży, potem pełną natywną komendę `ship`. Stosuj
`references/harness-command-contract.md` dla każdej komendy.
