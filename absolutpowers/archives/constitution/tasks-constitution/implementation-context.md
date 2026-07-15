# Implementation Context: Constitution

## Purpose
Short handoff for phase workers. Keep concise. Add only facts future phases need.

## Completed Phases
- Phase 1: `constitution` skill authored in both trees. Verification passed.
- Phase 2: `generate-tasks` + `implement` (both trees) now bind `absolutpowers/constitution.md` as required reading. Verification passed.
- Phase 3: `review` (both trees) extended with constitution sub-check in FAZA 3 + report format + Podsumowanie counter. `update-ai-context` (both trees) extended with demarcation note in PHASE 3. Verification passed.
- Phase 4: `feature-discuss` (both trees) reads `absolutpowers/constitution.md` as lightweight context (not a gate). Inserted as "Wstępne wczytanie kontekstu projektu" preamble before Faza 0 in `## Proces rozmowy`. Absent file = silent skip. Verification passed.
- Phase 5: `README.md` and root `CLAUDE.md` document the `constitution` skill, its output path, two-file distinction, and pipeline wiring. Both manifests bumped to `3.9.0`. Verification passed.

## Created / Changed API
- NEW `claude/skills/constitution/SKILL.md` — canonical Claude skill.
- NEW `codex/skills/constitution/SKILL.md` — Codex mirror (no `allowed-tools`/`argument-hint`).

### constitution.md output path (use verbatim in wiring phases)
```
absolutpowers/constitution.md
```

### constitution.md header format (use verbatim in wiring phases)
```
> Wersja: X.Y.Z · Ratyfikowano: YYYY-MM-DD · Egzekwowana przez: feature-discuss, generate-tasks, implement, review
```

### Demarcation sentence (use verbatim in Phase 3 — review + update-ai-context)
```
Konstytucja = pryncypia/osąd. Mechanika = `rules.md` / `update-ai-context`.
```

## Decisions Made
- Two files: `constitution.md` (pryncypia/osąd, ratyfikacja, semver) ≠ `rules.md` (mechanika/lint). Never merge.
- Constitution path: `absolutpowers/constitution.md` (project root, created by the skill at runtime — NOT authored by this feature).
- Versioning: semver + ratyfikacja date + changelog inside the file.
- Review enforcement = extend Faza 3 (not a new phase); constitution *reports* violations, does not block build.

## Test Utilities / Fixtures
- None (markdown plugin, no test runner). Verification = `./scripts/diff-skills.sh`.

## Constraints For Next Phases
- Every `claude/skills/*` edit MUST have a mirrored `codex/skills/*` edit. Only allowed drift: `allowed-tools`, `argument-hint` frontmatter (Claude-only).
- Wiring edits are additive (add `constitution.md` to existing "read context" lists) — do NOT restructure existing prompt sections.

## Verification History
- Phase 1: `./scripts/diff-skills.sh` → `~ constitution (differs)` (expected — only allowed-tools + argument-hint removed in Codex). `grep -l "name: constitution"` confirms both files exist.
- Phase 2: `grep -rn constitution.md` → 4 hits (one per file, all correct). Body diff between claude/codex pairs = identical. `diff-skills.sh` drift summary unchanged.
- Phase 3: `grep -rn constitution` across all four files → 4 files, multiple hits each. Direct `diff` between claude/codex pairs for both skills confirms new sections are identical (only frontmatter + triada-review blurb drift in review). `diff-skills.sh` summary unchanged (same ~ markers for review and update-ai-context as before).
- Phase 4: `grep -rn "constitution.md" claude/skills/feature-discuss/ codex/skills/feature-discuss/` → 1 hit in each file. Direct diff confirms bodies identical; only allowed-tools + argument-hint frontmatter drift (pre-existing). `diff-skills.sh` summary unchanged (~feature-discuss was already differing before this phase).
- Phase 5: `grep -n constitution README.md CLAUDE.md` → 17 hits in README.md, 9 hits in CLAUDE.md. `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json` → both report `"version": "3.9.0"`.
