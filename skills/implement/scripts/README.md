# Implement scripts (canonical)

These scripts are the **canonical** AbsolutPowers fork used by `implement`
orchestrated mode. See `references/fork-policy.md`.

| Script | Role |
|--------|------|
| `review-package` | Build a single review package for `phase-review` / `review-implementation` |
| `sdd-workspace` | Workspace helpers for orchestrated runs |

Upstream-shaped copies live under
`skills/vendored/subagent-driven-development/scripts/` for MIT tracking and
diffability. **Edit here first**; only port upstream fixes into this directory
intentionally.
