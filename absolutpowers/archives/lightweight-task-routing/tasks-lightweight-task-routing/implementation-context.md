# Implementation Context: Lightweight task routing w feature-discuss

## Purpose
Short handoff for phase workers. Keep this file concise. Add only facts that future phases need.
HARD BUDGET: max 10 lines per phase entry across all sections combined; whole file target ≤150 lines.
Every later worker reads this file — its size is paid on every phase.

## Completed Phases
- Phase 1: lightweight routing contract and its static contract tests; final-gate file-count wording fix applied and AC-1 rechecked.
- Phase 2: current documentation and accepted ADR synchronized; release metadata is 5.5.0; README route-aware lead fix applied and AC-3/AC-4 rechecked.

## Created / Changed API
- `FeatureDiscussPromptContractTest` and `read_repo_text(path: str) -> str` live in `tests/test_lightweight_task_routing.py`.
- `LightweightDocumentationContractTest` and `ManifestVersionContractTest` guard active docs and release metadata.

## Decisions Made
- Lightweight is risk/session based; its tracker is session-only; Explain generation is affirmative opt-in.

## Test Utilities / Fixtures
- None yet.

## Constraints For Next Phases
- Preserve user-owned untracked planning and ADR content; update only where required by this feature.

## Verification History
- Phase 1: `python3 -m unittest discover -s tests -p 'test_lightweight_task_routing.py'` and feature-discuss frontmatter check.
- Phase 2: 16 lightweight-routing contract tests and repository-wide manifest JSON validation passed.
