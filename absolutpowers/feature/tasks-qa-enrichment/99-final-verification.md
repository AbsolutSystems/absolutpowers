# Phase 99: Final Verification

## Status
completed

## Parent
`./absolutpowers/feature/tasks-qa-enrichment.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-qa-enrichment/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- All implementation phases (1-7) completed

### Provides (for later phases)
- Verified integrated change: all skill files, agent files, and docs are consistent

## Objective
Run cross-cutting verification commands to confirm the entire QA enrichment feature is integrated correctly across Claude and Codex plugins.

## Verification Commands

### 1. Drift Detection
```bash
./scripts/diff-skills.sh --diff
```
Expected: feature-discuss differs (Claude has agent spawn, Codex has inline). generate-tasks differs (Claude has agent gate, Codex does not). implement differs (Claude has agent gates, Codex does not). No unexpected drift in other skills.

### 2. File Existence Checks
```bash
# New agent file
test -f claude/agents/qa-enrichment.md && echo "OK: qa-enrichment agent" || echo "FAIL: qa-enrichment agent missing"

# Verify all modified files exist
for f in \
  claude/skills/feature-discuss/SKILL.md \
  codex/skills/feature-discuss/SKILL.md \
  claude/agents/review-plan.md \
  claude/skills/generate-tasks/SKILL.md \
  codex/skills/generate-tasks/SKILL.md \
  claude/agents/review-tasks.md \
  claude/skills/implement/SKILL.md \
  codex/skills/implement/SKILL.md \
  claude/agents/review-implementation.md \
  README.md \
  docs/getting-started.md \
  docs/review-gates.md \
  docs/contributing.md; do
  test -f "$f" && echo "OK: $f" || echo "FAIL: $f missing"
done
```

### 3. Content Consistency Checks
```bash
# AC format references are consistent across files
grep -l "AC-" claude/agents/qa-enrichment.md claude/agents/review-plan.md claude/agents/review-tasks.md claude/agents/review-implementation.md claude/skills/generate-tasks/SKILL.md claude/skills/implement/SKILL.md

# New categories exist in agents
grep "AC_QUALITY" claude/agents/review-plan.md
grep "AC_COVERAGE" claude/agents/review-tasks.md
grep "AC_FULFILLMENT" claude/agents/review-implementation.md

# Feature-discuss references qa-enrichment
grep "qa-enrichment" claude/skills/feature-discuss/SKILL.md

# Codex has inline QA but no agent reference
grep "Acceptance Criteria" codex/skills/feature-discuss/SKILL.md
grep "qa-enrichment" codex/skills/feature-discuss/SKILL.md && echo "WARN: Codex should not reference qa-enrichment agent" || echo "OK: no agent reference in Codex"

# Traces to field in generate-tasks templates
grep "Traces to" claude/skills/generate-tasks/SKILL.md
grep "Traces to" codex/skills/generate-tasks/SKILL.md
```

### 4. Documentation Consistency
```bash
# README mentions qa-enrichment
grep "qa-enrichment" README.md

# Review gates doc has all three new categories
grep "AC_QUALITY" docs/review-gates.md
grep "AC_COVERAGE" docs/review-gates.md
grep "AC_FULFILLMENT" docs/review-gates.md
```

## Completion Criteria
- All verification commands pass
- No unexpected drift between Claude and Codex skills
- All new categories (AC_QUALITY, AC_COVERAGE, AC_FULFILLMENT) present in correct files
- Codex skills have no agent references (qa-enrichment is Claude-only agent)
- Documentation is consistent with implementation

## Implementation Decisions / Remarks
- Commands executed: `./scripts/diff-skills.sh --diff`, file existence checks (14 files), content consistency checks (AC- refs, categories, agent refs, Traces to, docs)
- Results: All pass. 6 skills differ (expected: frontmatter + agent gates). Codex has no qa-enrichment agent ref. All 3 new categories present in correct agent files. All docs updated.
- Skipped checks: none
