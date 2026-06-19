# Implementation Context: analyze — cross-artifact consistency audit

## Purpose
Short handoff for phase workers. Keep concise. Add only facts later phases need.

## Completed Phases
- Phase 1: Intent Fidelity gate + feature-discuss source nudge (completed).
- Phase 2: New `analyze` skill — both trees (completed).
- Phase 3: Wiring notes — `review` "vs analyze" note + `generate-tasks` optional analyze suggestion, both trees (completed).
- Phase 4: Docs + version sanity — README.md, CLAUDE.md documented; manifests confirmed at 3.9.0 (completed).

## Created / Changed API
- `claude/agents/review-tasks.md`: new criterion `### 7. Intent Fidelity` added after
  `### 6. Code References`; `INTENT` appended to Categories line in Response Format.
- `claude/skills/feature-discuss/SKILL.md` + `codex/skills/feature-discuss/SKILL.md`:
  blockquote nudge added inside the `## Problem` template (standardowy planning doc format)
  reminding authors that goal/intent must be written explicitly — `review-tasks` Intent
  Fidelity gate reads a fresh context and only sees what the saved doc records.
- `claude/skills/analyze/SKILL.md` — new skill (Claude canonical). Frontmatter: `name: analyze`,
  `allowed-tools` (Read/Glob/Grep/Bash/Write scoped to `**/absolutpowers/reviews/*.md`),
  `argument-hint: "[slug feature'a, np. push-notifications]"`.
- `codex/skills/analyze/SKILL.md` — Codex mirror: identical body, no `allowed-tools`/`argument-hint`,
  no Claude-only delegation paragraph (marked `<!-- CLAUDE-ONLY -->`/`<!-- /CLAUDE-ONLY -->`).

## Decisions Made
- Skill name is `analyze` (both trees). Report output: `absolutpowers/reviews/analyze-{slug}.md`.
- Blocking divergence classes: 1 (AC bez taska), 3 (Task bez kodu), 4 (Kod bez taska), 6 (Sprzeczność). Warning-only: 2 (Task bez AC), 5 (AC bez weryfikacji). Verdict CONSISTENT / INCONSISTENT.
- Manifests already at version `3.9.0` (bundle bump applied with the broader 3.9.0 release). No further bump — analyze ships under 3.9.0.
- Hard boundary: analyze audits + routes only (missing task → generate-tasks; missing code → implement). Never fixes/plans/writes code.

## Test Utilities / Fixtures
- Verification = `./scripts/diff-skills.sh` + `python3 -m json.tool` on both manifests + grep checks. No build/test suite.

## Constraints For Next Phases
- Cross-platform sync: Codex SKILL.md mirrors Claude but omits `allowed-tools` + `argument-hint` frontmatter; any subagent-delegation paragraph is Claude-only. `diff-skills.sh` should show only this expected drift for `analyze`.

## Verification History
- Phase 1: `grep -n "### 7. Intent Fidelity" claude/agents/review-tasks.md` → 1 hit (line 95).
  `grep -n "INTENT" claude/agents/review-tasks.md` → 1 hit in Categories line.
  `grep -ci "review-tasks" claude/skills/feature-discuss/SKILL.md codex/skills/feature-discuss/SKILL.md` → 1 each.
  `./scripts/diff-skills.sh --diff` → feature-discuss diff shows only pre-existing frontmatter + subagent drift, no new nudge drift.
- Phase 2: `python3 -c "... assert 'name: analyze' in t"` → OK.
  `grep -c "CONSISTENT\|INCONSISTENT" claude/.../analyze/SKILL.md codex/.../analyze/SKILL.md` → 6 each.
  `./scripts/diff-skills.sh` → `~ analyze (differs)` (present in both trees; no `!`).
  `diff -u claude/.../analyze/SKILL.md codex/.../analyze/SKILL.md` → drift = `allowed-tools` + `argument-hint` frontmatter lines + `<!-- CLAUDE-ONLY -->` delegation paragraph only.
- Phase 3: `grep -cni "analyze"` → review 1/1, generate-tasks 3/3 (2 pre-existing prose + 1 new each).
  `./scripts/diff-skills.sh` → review + generate-tasks differ only by expected/pre-existing drift.
- Phase 4: `grep -ni "analyze" README.md CLAUDE.md` → 17 hits in README.md (skill section, pipeline, structure, changelog), 6 hits in CLAUDE.md (subsection, body, editing rules).
  `grep -ni "intent fidelity" CLAUDE.md` → 1 hit.
  `python3 -m json.tool` → JSON OK on both manifests.
  `python3 -c "... assert a==b=='3.9.0'"` → `versions OK 3.9.0`, exit 0.
