# Tasks: tasks-to-issues — eksport tasków do GitHub Issues (most outward-facing)

## Source
- Planning doc: `./absolutpowers/feature/planning-tasks-to-issues.md`
- Epic context (if applicable): none

## Mode
single-file

> No `## Acceptance Criteria` section in the planning doc → AC traceability is skipped for this plan (no `**Traces to:**` fields).

## Project Context

**Stack:** Markdown skill/agent prompts (Claude Code + Codex plugins). No compiled code. Two parallel trees `claude/` and `codex/` share skill logic; Claude adds frontmatter (`allowed-tools`, `argument-hint`), agents, and commands. **This feature is Claude-only in v1** — Codex is out of scope (needs `Bash(gh:*)` + external API interaction).

**Structure:**
- `claude/skills/{name}/SKILL.md` — skill prompts (Claude)
- `codex/skills/{name}/SKILL.md` — skill prompts (Codex) — NOT touched by this feature
- `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json` — manifests (versions must match)
- `README.md`, `CLAUDE.md` — docs

**Patterns:**
- SKILL.md frontmatter (Claude): `name`, `description` (triggers + purpose), `allowed-tools`, `argument-hint`. Body is the prompt; `$ARGUMENTS` is user input.
- STOP-on-missing-precondition pattern: mirror `preboot` (stop with a clear message when local docs missing) — here: stop when `gh` unauthenticated / no repo remote / no issue permission.
- Hard-boundary skills: `problem-discuss` and `analyze` declare an explicit "investigates/audits and routes only — never fixes" boundary. Mirror that style for "creates/updates issues + map only".
- Resume-safe write: persist progress after each unit (mirror orchestrated `implementation-context.md` write-after-each-phase) — here: rewrite the map file after each created/updated issue.

**Conventions:**
- Files: kebab-case skill dirs. Bilingual: Polish user-facing prompts, English technical content.
- Reference recent additive skill `analyze` (`claude/skills/analyze/SKILL.md`) for boundary/STOP/output-file prose tone.

**Verification commands:**
- Drift between trees (expected: tasks-to-issues present only in `claude/`): `./scripts/diff-skills.sh`
- JSON manifests valid + versions match: `python3 -m json.tool claude/.claude-plugin/plugin.json` and `python3 -m json.tool codex/.codex-plugin/plugin.json`
- Targeted grep checks (see Final Verification task)

**Reference implementations:**
- `claude/skills/analyze/SKILL.md` — hard-boundary skill, output report file, route-don't-fix tone
- `claude/skills/preboot/SKILL.md` — STOP-on-missing-precondition pattern
- `claude/skills/generate-tasks/SKILL.md` — single-file vs orchestrated tasks-doc structure parsing (this skill must read both)

## Approved decisions (from planning doc)

Recommendations in the planning doc are adopted as the plan baseline:
1. **Granularność:** epic issue per feature + sub-issue per phase (orchestrated) / per task (single-file). Tasks inside a phase = checklist in the phase issue body.
2. **Mapa zwrotna:** separate file `absolutpowers/feature/tasks-{slug}.issues.md` (not a section inside tasks-doc).
3. **Claude-only v1.**
4. **Idempotencja:** map file = source of truth; title marker `[{slug}]` = fallback.
5. **Wersja:** bundled 3.9.0 — manifests already at 3.9.0 (no bump needed; only changelog wording).

---

## Implementation Tasks

### Task 1: Author `tasks-to-issues` skill prompt
**Status:** completed

**Create:**
- `claude/skills/tasks-to-issues/SKILL.md`

**Modify:**
- None

**Description:**
The core deliverable: a Claude-only skill that reads a `tasks-{slug}.md` (single-file or orchestrated, including epic subfolder), and creates/updates GitHub Issues via `gh` CLI idempotently, maintaining a back-map file. This is an authoring task — write the frontmatter + prompt body. No code compiles; correctness = the prompt fully specifies behavior, boundaries, STOP conditions, and edge cases from the planning doc.

**Requirements:**
- **Frontmatter:** `name: tasks-to-issues`; `description:` with triggers (`"eksportuj taski"`, `"tasks to issues"`, `"wystaw issues"`, `"export tasks"`, `"utwórz issues z tasków"`) + purpose + explicit "Claude-only, GitHub via `gh`" note + "NIE wyzwalaj" guard against `generate-tasks`/`implement`; `allowed-tools: Read, Glob, Grep, Edit, Write, Bash`; `argument-hint: "[ścieżka do tasks-{slug}.md]"`.
- **Input parsing:** accept `tasks-{slug}.md`. Detect `## Mode` (single-file vs orchestrated). For orchestrated, read Phase Overview + each referenced phase file + `99-final-verification.md`. Support epic subfolder input (`feature/{epic-slug}/tasks-{slug}.md`) — derive map path inside same subfolder; `{slug}` includes enough to avoid collisions (see edge cases).
- **Preconditions / STOP (mirror `preboot`):** before any write, verify `gh auth status` OK, a GitHub repo remote exists, and issue-create permission. On any failure → STOP with a clear Polish message, NO partial export.
- **Sensitive-content confirmation:** before the FIRST issue push for a slug, warn that export publishes task content to the tracker (possibly public repo) and require explicit user confirmation. Subsequent idempotent re-runs do not re-prompt.
- **Granularity model:** create one **epic issue** per feature. Then one **sub-issue per phase** (orchestrated) or **per task** (single-file). Tasks within a phase render as a markdown checklist in the phase sub-issue body.
- **Body content:** each issue body links the source tasks file path (in-repo), the epic issue (for sub-issues), and any AC the task/phase traces to (if `**Traces to:**` present). Epic issue body links all sub-issues.
- **Labels:** apply `absolutpowers`, `{slug}`, phase risk (`risk:low|medium|high` from Phase Overview `**Risk:**`), and status. Create labels if missing (`gh label create` tolerant of "already exists").
- **Idempotency (map = source of truth, title marker = fallback):** maintain `absolutpowers/feature/tasks-{slug}.issues.md` mapping epic/phase/task → issue number + URL. On re-run: read map first; for entries without a map hit, fall back to searching open issues by title marker `[{slug}]`. Missing → create; existing open → update title/body/labels; closed → leave untouched. Never create duplicates.
- **Orphan handling:** a task/phase removed from the tasks-doc but present in the map → do NOT auto-close the issue; flag it as `orphaned` in the run report.
- **Resume-safe writes:** rewrite the map file after EACH created/updated issue (so a rate-limit/API error mid-run leaves a consistent partial map). End with a report: created / updated / skipped(closed) / orphaned / failed.
- **Hard boundary (state explicitly):** creates/updates issues + map ONLY. Does NOT close issues after `implement`, does NOT push code, does NOT touch task statuses inside the tasks-doc (that is `implement`'s job), does NOT create milestones/assignees/project-board automation.
- **Provider extension point:** GitHub via `gh` is the only v1 provider, but structure the prompt with a clearly delimited "Provider: GitHub (`gh`)" section so a future `glab`/Jira provider can slot in without rewriting the skill.
- **Map file format:** specify a concrete table/structure for `tasks-{slug}.issues.md` (epic → phases/tasks → issue#/URL/status) so re-runs parse it deterministically.
- Language: Polish user-facing prose, English for technical/CLI content (match repo convention).

**Tests:**
- Manual/grep verification only (prose skill). Confirm the SKILL.md contains, in order: frontmatter with all 4 keys; Input parsing (both modes + epic subfolder); STOP preconditions; sensitive-content confirmation gate; granularity model; labels; idempotency (map-first, marker fallback); orphan flag; resume-safe map write; hard-boundary statement; provider extension section; map file format spec.
- `gh`-dependent behavior cannot be unit-tested here; correctness = completeness of the specification.

**Implementation decisions / remarks:**
- Created `claude/skills/tasks-to-issues/SKILL.md`. Frontmatter has all 4 keys; `allowed-tools: Read, Glob, Grep, Edit, Write, Bash`.
- Structure: Twarda granica → Provider section (`[provider:github]` markers as extension point) → Krok 0 STOP preconditions (`gh auth status`, `gh repo view` remote + `viewerPermission`) → Krok 1 parsing (single-file/orchestrated/epic subfolder) → Krok 2 granularity (epic + sub-issue) → Krok 3 marker+map → Krok 4 publish confirmation (first export only) → Krok 5 idempotent export (map-first, marker fallback, resume-safe write per issue) → Krok 6 orphaned (no auto-delete) → Krok 7 report → edge-case table.
- Verified spec coverage via grep (all required elements present, in order).

**Example:**
```yaml
---
name: tasks-to-issues
description: >
  Eksport tasków (tasks-{slug}.md, single-file lub orchestrated) do GitHub Issues
  przez gh CLI — idempotentnie, z mapą zwrotną. Most outward-facing pipeline'u.
  TRIGGER when: "eksportuj taski", "tasks to issues", "wystaw issues zespołowi",
  "export tasks to GitHub". Claude-only. NIE wyzwalaj na implement / generate-tasks.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: "[ścieżka do tasks-{slug}.md]"
---
```
```markdown
<!-- map file: absolutpowers/feature/tasks-{slug}.issues.md -->
# Issues map: {slug}

| Artefakt        | Typ   | Issue | URL                          | Status |
|-----------------|-------|-------|------------------------------|--------|
| (feature)       | epic  | #41   | https://github.com/o/r/issues/41 | open   |
| Phase 1: ...    | phase | #42   | https://github.com/o/r/issues/42 | open   |
| Phase 2: ...    | phase | #43   | https://github.com/o/r/issues/43 | open   |
```

---

### Task 2: Wire docs — README.md (pipeline + structure + changelog)
**Status:** completed

**Create:**
- None

**Modify:**
- `README.md`

**Description:**
Document the new outward-facing bridge so users discover it. Add tasks-to-issues to the pipeline narrative as an optional Claude-only outward channel, register the `.issues.md` artifact in the project structure, and append it to the 3.9.0 changelog.

**Requirements:**
- After the `analyze` block in `## The Pipeline` (around README.md:79–90), add a short **outward-facing** subsection: `tasks-to-issues` is an optional, on-demand, **Claude-only** bridge from `tasks-{slug}.md` to GitHub Issues via `gh`; idempotent; produces `tasks-{slug}.issues.md`. Include a small diagram in the existing style.
- In `## Project Structure in Your Repo` (around README.md:710), add `│   │   └── tasks-{slug}.issues.md  # tasks → GitHub Issues back-map (tasks-to-issues skill)` under `feature/`.
- In the `### 3.9.0` changelog block (around README.md:858), append a bullet: new `tasks-to-issues` skill — Claude-only outward bridge to GitHub Issues (epic + sub-issue per phase/task, idempotent via back-map, hard boundary, provider extension point for `glab`/Jira).
- Update the 3.9.0 heading wording to include tasks-to-issues (e.g. `### 3.9.0 — Constitution + cross-artifact analyze + Intent Fidelity + tasks-to-issues`).
- State Claude-only explicitly wherever the skill is introduced (Codex parity intentionally absent).

**Tests:**
- `grep -n "tasks-to-issues" README.md` returns ≥3 hits (pipeline, structure, changelog).
- `grep -n "tasks-{slug}.issues.md" README.md` returns ≥1 hit.

**Implementation decisions / remarks:**
- Added pipeline subsection (outward-facing bridge + diagram) after the `analyze` block, structure entry under `feature/`, changelog bullet, and updated 3.9.0 heading to include tasks-to-issues.
- Verification: `grep -c "tasks-to-issues" README.md` = 5 (≥3 ✓); `grep -Fc "tasks-{slug}.issues.md" README.md` = 4 (≥1 ✓). Used `-F` because the rg-backed grep proxy treats `{` in `{slug}` as a regex quantifier.

---

### Task 3: Wire docs — CLAUDE.md (pipeline architecture + cross-platform note)
**Status:** completed

**Create:**
- None

**Modify:**
- `CLAUDE.md`

**Description:**
Update the repo's own CLAUDE.md so future work on this codebase knows the bridge exists, that it is Claude-only, and what to keep in sync.

**Requirements:**
- In `## Pipeline Architecture`, add a short **outward-facing bridge** note describing `tasks-to-issues` (reads `tasks-{slug}.md`, creates/updates GitHub Issues via `gh`, idempotent via `tasks-{slug}.issues.md`, hard boundary: issues+map only, Claude-only).
- State the hard boundary explicitly (mirror the `problem-discuss`/`analyze` boundary phrasing already in CLAUDE.md): never closes issues, never pushes code, never mutates task statuses in the tasks-doc.
- Add a line noting the deliberate Claude-only asymmetry (no Codex counterpart in v1; Codex out of scope until contract stabilizes).
- Optionally add a `tasks-to-issues` cross-edit note to `## Cross-Platform Editing Rules` clarifying it is intentionally single-tree (no Codex sync expected — it is NOT drift to fix).
- Keep the repo CLAUDE.md `## What This Is` version line accurate (already 3.9.0).

**Tests:**
- `grep -n "tasks-to-issues" CLAUDE.md` returns ≥1 hit.
- CLAUDE.md states Claude-only + hard boundary for the skill.

**Implementation decisions / remarks:**
- Added `### Outward-facing bridge: tasks-to-issues (Claude only)` subsection under Pipeline Architecture (after Standalone Triada Review), with idempotency / STOP / hard boundary / provider / Claude-only-asymmetry notes.
- Added single-tree note to `## Cross-Platform Editing Rules` clarifying absence from Codex is expected drift.
- `grep -c "tasks-to-issues" CLAUDE.md` = 3 (≥1 ✓).

---

### Task 4: Soft nudge in generate-tasks (optional, Claude-only)
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/generate-tasks/SKILL.md`

**Description:**
Per planning doc (optional), add a light, non-automated nudge after the tasks Review Gate PASS pointing the user to `tasks-to-issues`. Export stays a deliberate decision — no automation, no Codex change (codex/generate-tasks must NOT get this nudge, since the skill is Claude-only).

**Requirements:**
- In the PASS branch of the `## Review Gate` section of `claude/skills/generate-tasks/SKILL.md`, append one optional line, e.g.: "Opcjonalnie: aby wystawić ten plan zespołowi w GitHub Issues — `/absolutpowers:tasks-to-issues @absolutpowers/feature/tasks-{slug}.md`."
- Keep it a single suggestion line; do NOT add automation or a gate.
- Do NOT modify `codex/skills/generate-tasks/SKILL.md` — this asymmetry is intentional (record it as expected drift).
- If integrating cleanly into the PASS message proves awkward, this task may be skipped — record the skip in remarks. (Planning marks this optional.)

**Tests:**
- `grep -n "tasks-to-issues" claude/skills/generate-tasks/SKILL.md` returns ≥1 hit (or task recorded as skipped).
- `grep -c "tasks-to-issues" codex/skills/generate-tasks/SKILL.md` returns 0 (Codex untouched).

**Implementation decisions / remarks:**
- Added one optional, no-gate suggestion line in the PASS branch of `claude/skills/generate-tasks/SKILL.md` (after the existing analyze nudge). Integrated cleanly — not skipped.
- `codex/skills/generate-tasks/SKILL.md` deliberately untouched. Verification: claude = 1 hit, codex = 0.

---

### Task 5: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- None

**Description:**
Run the project's verification commands against the integrated change. This repo has no compiled artifacts; verification = JSON manifests valid + versions matched, expected drift confirmed (skill present only in `claude/`), and grep checks that all required prose elements landed.

**Requirements:**
- Validate manifests + version match: `python3 -m json.tool claude/.claude-plugin/plugin.json` and `python3 -m json.tool codex/.codex-plugin/plugin.json` (both 3.9.0).
- Run `./scripts/diff-skills.sh` and confirm `tasks-to-issues` appears as **Claude-only** drift (expected, not a sync target).
- Confirm new skill file exists: `test -f claude/skills/tasks-to-issues/SKILL.md`.
- Grep coverage of the SKILL.md spec: `grep -nE "idempot|gh auth|orphan|epic|risk:|\\.issues\\.md|boundary|provider" claude/skills/tasks-to-issues/SKILL.md` — confirm idempotency, STOP precondition, orphan flag, granularity, labels, map file, hard boundary, provider section all present.
- Grep docs wiring: `grep -n "tasks-to-issues" README.md CLAUDE.md` returns hits in both.
- Confirm Codex untouched for this skill: `test ! -d codex/skills/tasks-to-issues`.
- Record any command intentionally skipped as `not applicable` with a short reason.
- Do not mark completed if any required check fails.

**Tests:**
- Both `json.tool` runs exit 0; versions equal.
- `diff-skills.sh` shows tasks-to-issues as Claude-only (expected drift).
- All grep checks return expected hits.

**Implementation decisions / remarks:**
- Commands executed: `python3 -m json.tool` (both manifests), `grep '"version"'`, `test -f`/`test ! -d`, `./scripts/diff-skills.sh`, grep coverage (SKILL spec + docs).
- Results: manifests valid, both 3.9.0; SKILL.md present; codex dir absent. diff-skills: `! tasks-to-issues (missing in codex)` + summary `1 claude-only` (expected drift, not a sync target). SKILL spec grep = 44 hits; `.issues.md` in SKILL = 5; README tasks-to-issues = 5; CLAUDE.md = 3. All thresholds met.
- Skipped checks: none. (No compiled artifacts in this repo — build/test steps not applicable.)

**Example:**
```bash
python3 -m json.tool claude/.claude-plugin/plugin.json >/dev/null && echo OK
python3 -m json.tool codex/.codex-plugin/plugin.json >/dev/null && echo OK
./scripts/diff-skills.sh
grep -n "tasks-to-issues" README.md CLAUDE.md
test -f claude/skills/tasks-to-issues/SKILL.md && test ! -d codex/skills/tasks-to-issues && echo "tree asymmetry OK"
```
