# Final Verification: Lightweight task routing w feature-discuss

## Status
completed

## Parent
`./absolutpowers/feature/tasks-lightweight-task-routing.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-lightweight-task-routing/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Lightweight eligibility/context/escalation contract in `skills/feature-discuss/SKILL.md` from Phase 1.
- Lightweight mini-design/session-execution contract in `skills/feature-discuss/SKILL.md` from Phase 1.
- standard/phase and epic-main opt-in Explain contract in `skills/feature-discuss/SKILL.md` from Phase 1.
- Python contract-test class `FeatureDiscussPromptContractTest` and helper `read_repo_text(path: str) -> str` in `tests/test_lightweight_task_routing.py` from Phase 1.
- Documentation contract in `README.md`, `CLAUDE.md`, and `docs/adr/2026-07-16-lightweight-task-routing.md`, validated by `LightweightDocumentationContractTest` in `tests/test_lightweight_task_routing.py` from Phase 2.
- Synchronized plugin version `5.5.0` and README changelog entry, validated by `ManifestVersionContractTest` in `tests/test_lightweight_task_routing.py` from Phase 2.

### Provides (for later phases)
- None (final verification).

## Read Scope
- `absolutpowers/feature/planning-lightweight-task-routing.md`
- `absolutpowers/feature/tasks-lightweight-task-routing.md`
- `absolutpowers/feature/tasks-lightweight-task-routing/01-routing-contract.md`
- `absolutpowers/feature/tasks-lightweight-task-routing/02-docs-and-release.md`
- `skills/feature-discuss/SKILL.md`
- `tests/test_lightweight_task_routing.py`
- `README.md`
- `CLAUDE.md`
- `docs/adr/2026-07-16-lightweight-task-routing.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

## Write Scope
- None

## Objective
Run the repository's complete relevant validation against the integrated prompt, documentation, ADR, tests, and release metadata. Confirm every Acceptance Criterion has a literal token in the contract-test source and refuse completion if any required command fails.

## Task 6: Final Verification
**Status:** completed
**Traces to:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13

**Create:**
- None

**Modify:**
- None

**Description:**
Run the canonical static checks and the feature-specific contract suite against the fully integrated change. Record results in this file only after all commands finish; do not modify implementation files during final verification.

**Requirements:**
- Run contract tests: `rtk proxy python3 -m unittest discover -s tests -p 'test_lightweight_task_routing.py'`.
- Validate every tracked JSON manifest: `rtk proxy bash -lc 'for f in $(git ls-files "*.json"); do python3 -m json.tool "$f" >/dev/null || exit 1; done'`.
- Validate all tracked skill frontmatter: `rtk proxy bash -lc 'for f in $(git ls-files "skills/**/SKILL.md"); do test "$(head -n 1 "$f")" = "---" || { echo "NO FM: $f"; exit 1; }; done'`.
- Validate the SessionStart hook emits JSON: `rtk proxy bash -lc 'CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null'`.
- Verify each acceptance token with `rtk proxy bash -lc 'for n in $(seq 1 13); do rg -q "AC-$n" tests/test_lightweight_task_routing.py || { echo "MISSING: AC-$n"; exit 1; }; done'`; any missing literal token fails verification, and no required check may be marked completed after a non-zero exit.

**Tests:**
- Contract suite exits with code 0.
- JSON validation exits with code 0 for every tracked manifest.
- Skill frontmatter and SessionStart hook checks exit with code 0.
- Acceptance-token verification display `verify_all_acceptance_tokens [AC-1][AC-2][AC-3][AC-4][AC-5][AC-6][AC-7][AC-8][AC-9][AC-10][AC-11][AC-12][AC-13]` finds every token in `tests/test_lightweight_task_routing.py`.

**Implementation decisions / remarks:**
- Commands executed: all five canonical final-verification commands listed above.
- Results: PASS — 16 contract tests; JSON manifests, skill frontmatter, SessionStart hook JSON, and AC-1 through AC-13 token checks all exited 0, including the post-review fixes.
- Skipped checks: none.

**Example:**
```bash
rtk proxy python3 -m unittest discover -s tests -p 'test_lightweight_task_routing.py'
rtk proxy bash -lc 'for f in $(git ls-files "*.json"); do python3 -m json.tool "$f" >/dev/null || exit 1; done'
rtk proxy bash -lc 'CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null'
rtk proxy bash -lc 'for n in $(seq 1 13); do rg -q "AC-$n" tests/test_lightweight_task_routing.py || { echo "MISSING: AC-$n"; exit 1; }; done'
```

## Final Completion Criteria
- Both implementation phases are completed and their reviews passed.
- Every required verification command exits with code 0.
- Every `AC-N` from the source planning document appears in the contract-test source.
- Manifest versions are exactly synchronized at `5.5.0` and the README changelog is ordered correctly.
- Any skipped check is recorded as `not applicable` with a concrete reason; otherwise no check is skipped.
