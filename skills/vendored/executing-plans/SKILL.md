---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

_Vendored from [obra/superpowers](https://github.com/obra/superpowers) `skills/executing-plans` @ `d884ae0` (tag v6.1.1, MIT license — see [`LICENSE-VENDORED`](../../../LICENSE-VENDORED))._

**Cross-ref cleanup (2026):** upstream `superpowers:*` names replaced/annotated with local vendored or AbsolutPowers equivalents (writing-plans was grafted; finishing-a-development-branch role largely moved to `ship`). See VENDORED.md.

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that this works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (Claude Code, Codex, Pi, Grok Build all qualify; see `references/*-tools.md` in the AbsolutPowers tree). If subagents are available, prefer the local vendored `subagent-driven-development` (or AbsolutPowers `implement` in orchestrated mode) instead of this skill.

(Upstream references to `../using-superpowers/references/` were not vendored; use the AbsolutPowers harness references instead.)

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "Completing the feature."
- In AbsolutPowers the closeout role is largely covered by the `ship` skill (commit message + PR description + optional artifact archiving). The local vendored `finishing-a-development-branch` can still be used as reference if needed.
- **Local equivalent:** `finishing-a-development-branch` (vendored) or `@absolutpowers:ship` after review.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required / related workflow skills (local vendored or AbsolutPowers equivalents):**
- **using-git-worktrees** (local vendored) - Ensures isolated workspace
- **writing-plans** — upstream donor; its content was grafted into AbsolutPowers `generate-tasks` (see planning docs and ADR for fuzja)
- **finishing-a-development-branch** (local vendored) — closeout; in AbsolutPowers largely replaced by `ship` for commit + archive after `review`

See main `CLAUDE.md` / `README.md` for how AbsolutPowers wires planning → tasks → implement → review → ship.
