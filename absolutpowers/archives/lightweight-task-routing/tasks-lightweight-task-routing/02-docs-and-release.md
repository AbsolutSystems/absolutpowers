# Phase 2: Synchronize durable documentation and release metadata

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
- Python helper `read_repo_text(path: str) -> str` in `tests/test_lightweight_task_routing.py` from Phase 1.

### Provides (for later phases)
- Documentation contract in `README.md`, `CLAUDE.md`, and `docs/adr/2026-07-16-lightweight-task-routing.md`, validated by `LightweightDocumentationContractTest` in `tests/test_lightweight_task_routing.py`.
- Synchronized plugin version `5.5.0` and README changelog entry, validated by `ManifestVersionContractTest` in `tests/test_lightweight_task_routing.py`.

## Read Scope
- `absolutpowers/feature/planning-lightweight-task-routing.md`
- `skills/feature-discuss/SKILL.md`
- `README.md`
- `CLAUDE.md`
- `docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`
- `docs/adr/2026-07-16-lightweight-task-routing.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

## Write Scope
- `tests/test_lightweight_task_routing.py`
- `README.md`
- `CLAUDE.md`
- `docs/adr/2026-07-16-lightweight-task-routing.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

## Objective
Align current public and maintainer-facing documentation with the implemented lightweight routing contract without rewriting historical changelog entries or old artifacts. Preserve the accepted ADR and its link to the earlier HARD-GATE decision, then release the change as version 5.5.0 consistently across all manifests and the README changelog.

## Tasks

### Task 4: Update current documentation and the routing ADR
**Status:** completed
**Traces to:** AC-1, AC-3, AC-4, AC-5, AC-7, AC-10
**Test-first:** yes
**Produces:** documentation contract for Lightweight task and opt-in Explain in `README.md`, `CLAUDE.md`, and `docs/adr/2026-07-16-lightweight-task-routing.md`; `LightweightDocumentationContractTest` in `tests/test_lightweight_task_routing.py`
**Consumes:** Lightweight eligibility/context/escalation contract, Lightweight mini-design/session-execution contract, and standard/phase and epic-main opt-in Explain contract in `skills/feature-discuss/SKILL.md` from Phase 1; `read_repo_text(path: str) -> str` from Phase 1

**Create:**
- None

**Modify:**
- `tests/test_lightweight_task_routing.py`
- `README.md`
- `CLAUDE.md`
- `docs/adr/2026-07-16-lightweight-task-routing.md`

**Requirements:**
- Add `LightweightDocumentationContractTest(unittest.TestCase)` before editing docs; constrain checks to current feature/pipeline sections so historical changelog occurrences of `micro-change` remain valid.
- Update the README feature-discuss card and pipeline guidance with risk-based lightweight qualification, context pack, mini-design acceptance, session-only inline execution, mandatory verification/branch review, escalation, and opt-in Explain semantics.
- Update CLAUDE.md pipeline and terminal-state documentation to distinguish standard, epic-main, and Lightweight task outcomes and to explain that lightweight bypasses the planning/task stages without bypassing review.
- Keep `docs/adr/2026-07-16-lightweight-task-routing.md` aligned with the final prompt contract and retain its explicit link to `docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`.
- Do not edit archived planning files, historical ADRs, generated onboarding HTML, or historical README changelog entries.

**Tests:**
- `test_current_docs_describe_risk_based_lightweight_route_AC1` with display docstring `[AC-1]` verifies qualification is not described using LOC/file-count thresholds.
- `test_current_docs_preserve_gate_and_inline_review_handoff_AC3_AC4` with display docstring `[AC-3][AC-4]` verifies mini-design acceptance, inline execution, verification, and branch review.
- `test_current_docs_describe_escalation_boundaries_AC7` with display docstring `[AC-7]` verifies standard/epic escalation conditions.
- `test_current_docs_describe_opt_in_explain_and_skip_AC5_AC10` with display docstring `[AC-5][AC-10]` verifies affirmative-only generation and non-blocking skip/no-response behavior.

**Implementation decisions / remarks:**
- Added contracts scoped to the current README feature card, CLAUDE pipeline section, and accepted ADR so historical `micro-change` text remains valid.
- Documented risk/session qualification, context-pack fallback, mini-design HARD-GATE, inline verification/review, escalation, and affirmative-only Explain.
- After final-gate feedback, made the README card lead and `In → Out` route-aware instead of universally promising a planning doc and `review-plan`.

**Example:**
```python
class LightweightDocumentationContractTest(unittest.TestCase):
    def test_current_docs_describe_opt_in_explain_and_skip_AC5_AC10(self) -> None:
        """[AC-5][AC-10] Explain is opt-in; skip and no response do not generate it."""
        readme = read_repo_text("README.md")
        self.assertIn("Lightweight task", readme)
```

### Task 5: Publish synchronized 5.5.0 release metadata
**Status:** completed
**Traces to:** none (release metadata task)
**Test-first:** yes
**Produces:** synchronized plugin version `5.5.0`, README changelog entry `5.5.0 — Lightweight task routing`, and `ManifestVersionContractTest` in `tests/test_lightweight_task_routing.py`
**Consumes:** `read_repo_text(path: str) -> str` from Phase 1

**Create:**
- None

**Modify:**
- `tests/test_lightweight_task_routing.py`
- `README.md`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `.grok-plugin/plugin.json`

**Requirements:**
- Add `ManifestVersionContractTest(unittest.TestCase)` that parses all three manifests with `json.loads` and asserts the exact version set is `{"5.5.0"}`.
- Change the `version` field to `5.5.0` in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.grok-plugin/plugin.json` without altering unrelated manifest fields.
- Prepend README changelog section `### 5.5.0 — Lightweight task routing` above 5.4.0, covering the generalized fast path, context pack/mini-design safeguards, opt-in Explain, static contract tests, and synchronized manifest version.
- Preserve every historical changelog section and its terminology unchanged.

**Tests:**
- `test_all_plugin_manifests_are_version_5_5_0` verifies the exact three-manifest version set equals `{"5.5.0"}`.
- `test_readme_changelog_places_5_5_0_before_5_4_0` verifies the new heading exists once and precedes `### 5.4.0 — Static QA Review`.
- `test_manifest_json_files_parse` verifies each changed manifest parses with Python `json.loads`.

**Implementation decisions / remarks:**
- Parsed the three canonical manifests with `json.loads` and asserted their exact version set, while changing only each `version` field.
- Prepended the 5.5.0 changelog entry and preserved all existing release sections below it.

**Example:**
```python
MANIFEST_PATHS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".grok-plugin/plugin.json",
)
```

## Phase Verification
Run:
- `rtk proxy python3 -m unittest discover -s tests -p 'test_lightweight_task_routing.py'`
- `rtk proxy bash -lc 'for f in $(git ls-files "*.json"); do python3 -m json.tool "$f" >/dev/null || exit 1; done'`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- RED was recorded after adding documentation and release contracts: 12 expected failures against the pre-update docs/manifests.
- Current-contract tests deliberately extract active README/CLAUDE sections and the accepted ADR rather than scanning historical artifacts.
- Phase verification passed with 16 contract tests and repository-wide JSON parsing.
