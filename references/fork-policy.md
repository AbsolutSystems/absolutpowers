# Fork policy — vendored vs AbsolutPowers-owned copies

When the same logical asset exists in more than one place, this file names the
**source of truth**. Prefer reading this over “which copy looks newer.”

## Canonical map

| Asset | Canonical | Secondary | Notes |
|-------|-----------|-----------|--------|
| Debugging process (main skill) | `skills/debug/SKILL.md` | `skills/vendored/systematic-debugging/` | Session auto-trigger uses **`debug` only**. Vendored copy is the MIT library + techniques; `debug` is AbsolutPowers process (handoff from `problem-discuss`, large-fix → `planning-fix-*`, project-memory). |
| Debug techniques (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting*`) | `skills/debug/` | vendored `systematic-debugging/` may diverge | **Prefer `skills/debug/`**. When porting from upstream, merge into `skills/debug/` then optionally refresh vendored. Do not silently edit only one side. |
| Orchestrated scripts (`review-package`, `sdd-workspace`) | `skills/implement/scripts/` | `skills/vendored/subagent-driven-development/scripts/` | **Prefer implement fork** (AbsolutPowers path conventions, `AP_TASKS_DIR`). Vendored scripts stay for upstream diffability. |
| Visual companion | `skills/feature-discuss/companion-scripts/` + `visual-companion.md` | obra brainstorming (vendor clone) | Feature-discuss is canonical; telemetry/CSP hardened. |
| Closeout / ship | `ship` in active harness syntax | vendored `finishing-a-development-branch` | Prefer the native `ship` command rendered by `references/harness-command-contract.md`. Vendored skill is optional legacy path for worktree merge menus; see banner in that skill. |
| Plan execution | `implement` in active harness syntax (`## Mode`) | vendored `executing-plans` / `subagent-driven-development` | Prefer AbsolutPowers pipeline and render the command natively. Vendored SDD is reference / partial tooling source. |

## Rules for editors

1. **Edit the canonical path first.** If you must keep secondary in sync, do it in the same change and note it in the PR.
2. **Do not “fix drift” by overwriting canonical with vendored** without checking AbsolutPowers-specific grafts (handoff, gates, paths).
3. **Quarterly upstream sync** (`VENDORED.md`) reviews vendored trees only; after a useful upstream fix, port intentionally into the canonical AbsolutPowers path.
4. New dual copies require an update to this table.

## Why dual copies exist

Vendoring keeps MIT attribution and upstream diffs readable. AbsolutPowers then
owns the operational path used by the pipeline so harness-specific and process
grafts do not fight the vendor pin.
