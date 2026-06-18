# Tasks: Harvest Phase — document-feature + harvest orchestrator

## Mode
single-file

## Project Context

**Source doc:** `./absolutpowers/feature/planning-harvest-docs.md`
**Related planning:** `./absolutpowers/feature/planning-learned-skills.md` (try-learn-skill — already shipped, harvest-aware)

**Stack:** Markdown prompt files (Claude Code + Codex plugin). No compiled code. Two parallel skill trees: `claude/skills/` and `codex/skills/`.

**Structure:**
- `claude/skills/{name}/SKILL.md` — Claude skill (full frontmatter: `allowed-tools`, `argument-hint`)
- `codex/skills/{name}/SKILL.md` — Codex mirror (NO `allowed-tools` / `argument-hint`)
- `claude/.claude-plugin/plugin.json` + `codex/.codex-plugin/plugin.json` — version manifests (must match)
- `README.md`, `docs/` — user docs
- `scripts/diff-skills.sh` — Claude↔Codex drift detector

**Patterns (existing skills to mirror):**
- `try-learn-skill` SKILL.md — the model: target-project `Write` scope, body-comment metadata block, propose→gate flow, graceful handling of missing dirs. Already references "odpalany przez harvest" in its TRIGGER.
- `explain` SKILL.md frontmatter — example of scoped `allowed-tools` and `argument-hint`.
- `feature-discuss` — `Write(**/absolutpowers/feature/**/*.md)` scope pattern (Write targets TARGET project, not repo).

**Conventions:**
- Skills: kebab-case `name`, `description:` with `TRIGGER when:` triggers for auto-detection.
- Metadata that the loader must not choke on → HTML comment in skill/doc **body**, never frontmatter (see `learned-meta` precedent).
- Bilingual: Polish user-facing prose, English technical terms.
- Codex skills omit `allowed-tools` and `argument-hint` — that is the only EXPECTED drift `diff-skills.sh` should report.

**Verification commands:**
- Drift check: `./scripts/diff-skills.sh` (and `./scripts/diff-skills.sh --diff` for detail)
- JSON validity: `python3 -m json.tool claude/.claude-plugin/plugin.json` + same for codex
- Frontmatter sanity: `grep -c '^---$' <SKILL.md>` must be `2`

**Reference implementations:**
- `claude/skills/try-learn-skill/SKILL.md` — closest sibling (harvest sub-skill, same family, target-project write, body-meta block). Mirror its shape.
- `codex/skills/try-learn-skill/SKILL.md` — the Codex-mirror reference (shows exactly what to strip).
- `claude/skills/implement/SKILL.md:528-537` — existing nudge block to reconcile.

---

## Current State (verified)

- `try-learn-skill` already exists in **both** trees and is harvest-aware (TRIGGER includes "odpalany przez harvest").
- `implement` nudge **already exists** in both trees pointing at `try-learn-skill` (Claude `:528-537`, Codex `:449-458`). This task set **reconciles** that nudge to point at `harvest` — it does NOT add a brand-new nudge.
- Current version in both manifests: **3.5.0** → bump to **3.6.0**.

---

## Implementation Tasks

### Task 1: Create `document-feature` skill (Claude)
**Status:** completed

**Create:**
- `claude/skills/document-feature/SKILL.md`

**Modify:**
- None

**Description:**
Core "meat" skill. Reads a finished feature's artifacts (planning + tasks + git diff), detects which **modules** the feature touched, confirms the file→module mapping (the single hard gate), then NEW-creates or intelligently UPDATE-merges per-module docs at `docs/modules/{module}.md` in the TARGET project, auto-writing and stamping freshness metadata. Models its shape on `try-learn-skill`.

**Requirements:**
- **Frontmatter:**
  - `name: document-feature`
  - `description:` — one-line purpose + `TRIGGER when:` narrow signals: "udokumentuj moduł", "document the module/feature", "zaktualizuj docs modułu", "harvest docs", "odpalany przez harvest", after a feature is implemented. Keep trigger narrow to avoid collision with `update-ai-context` / `explain`.
  - `allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/docs/modules/**/*.md)` — **Write scope targets the TARGET project's `docs/modules/`, NOT the AbsolutPowers repo** (same principle as `try-learn-skill` writing to target `.claude/skills/learned/`).
  - `argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"`
- **Body — input step:** From `$ARGUMENTS` derive `{slug}` + feature dir. Read what exists (handle each missing file gracefully, do NOT stop on partial):
  - `planning-{slug}.md` (intencja / decyzje — the "why"). Handle epic layout too (`{epic-slug}/planning-phase-N-*.md` + `planning-main.md`) as `try-learn-skill` does.
  - `tasks-{slug}.md` (+ phase files in `tasks-{slug}/`, + `implementation-context.md` if orchestrated).
  - **git diff** as the source of truth about the code:
    ```bash
    git diff <base>...HEAD   # base auto-detect: git rev-parse --verify main 2>/dev/null && echo main || echo master
    git diff --cached
    git diff
    ```
    Handle late runs where the diff is already committed/merged (`vs master` + specific-commit diff), exactly as `try-learn-skill` does.
  - If NO usable artifacts at all → report "za mało materiału" and exit WITHOUT writing.
- **Body — module detection (diff → module):**
  - **Primary:** read target project's `CLAUDE.md` (`## Project Structure` section) and `./absolutpowers/patterns.md` — source of truth for module structure.
  - **Fallback:** path heuristic from diff (top-level dir under `src/` or package/namespace; `src/auth/*` → module `auth`).
  - Sanitize module name → filename slug when the package name has special chars (open question #4 in planning — implement conservative kebab-case slug).
- **Body — mapping confirm (THE HARD GATE):** Print the detected file→module mapping (all modules if multiple) and **WAIT for confirmation/correction** before writing anything. This is the only blocking gate — bad detection = docs in the wrong file, which a new-file git diff would not catch. Auto-write applies to *content*, not to *which module file*.
- **Body — NEW vs UPDATE per module:** Loop over every touched module:
  - **NEW:** module doc absent → create `docs/modules/{module}.md` from the template (Task 7).
  - **UPDATE:** module doc exists → **intelligent merge**: rewrite the relevant sections so they reflect the CURRENT module state after the feature. NOT append-changelog (history = git + ADR). Include the explicit warning in the skill body: *"nie usuwaj wiedzy nieobjętej diffem — aktualizuj tylko dotknięte sekcje"* (don't delete knowledge outside the diff; only update touched sections).
- **Body — auto-write + stamp:** Write content directly (no extra prompt — pre-commit git diff is the natural review surface; docs are non-executable, so a lighter gate than `try-learn-skill`'s exec gate). Stamp `doc-meta` (Task 7): `last-updated` (today) + `last-commit` (current HEAD sha; note in body that the docs commit lands after, a 1-commit drift that is acceptable).
- **Body — rules section** mirroring `try-learn-skill`: hard gate = mapping confirm only; create `docs/modules/` dir on first write; never write outside `docs/modules/` of target project; intelligent merge must not drop undocumented knowledge.
- **Codex parity note** in body: the `codex/` mirror generates identical output without `allowed-tools`/`argument-hint`.

**Tests:**
- Manual structural: `grep -c '^---$'` returns `2`; frontmatter has `name`, `description` with `TRIGGER when:`, `allowed-tools` with the `docs/modules` Write scope, `argument-hint`.
- Body contains: input step (planning+tasks+diff), module detection (CLAUDE.md/patterns → path fallback), mapping-confirm hard gate, NEW vs UPDATE intelligent-merge, auto-write, `doc-meta` stamp, "don't delete undocumented knowledge" warning.

**Implementation decisions / remarks:**
- Modeled on `try-learn-skill` shape. Full module-doc template inlined here (so Task 7 is verification-only).
- Body uses `---` horizontal rules (convention: try-learn-skill has 7). So `grep -c '^---$'` = 5 for this file, NOT 2 — the naive ==2 frontmatter check in Task 10 was corrected to "well-formed frontmatter" (first line `---` + closing `---`).
- Added explicit "czym to NIE jest" block contrasting with update-ai-context / explain (feeds Task 8 distinction).

**Example (frontmatter skeleton):**
```yaml
---
name: document-feature
description: >
  Generuje/aktualizuje trwałą dokumentację MODUŁU z artefaktów zakończonego
  feature'a (planning + tasks + git diff) do `docs/modules/{moduł}.md` w
  target-projekcie. Wykrywa dotknięte moduły, potwierdza mapowanie plik→moduł
  (twardy gate), robi inteligentny merge w istniejące docs i stempluje świeżość.
  TRIGGER when: "udokumentuj moduł", "document the module", "zaktualizuj docs
  modułu", "harvest docs", po zakończonej implementacji, odpalany przez harvest.
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/docs/modules/**/*.md)
argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"
---
```

---

### Task 2: Create `document-feature` skill (Codex mirror)
**Status:** completed

**Create:**
- `codex/skills/document-feature/SKILL.md`

**Modify:**
- None

**Description:**
Codex mirror of Task 1. Identical body; drop the Claude-only frontmatter fields. This is the only EXPECTED drift.

**Requirements:**
- Copy the Claude `SKILL.md` body verbatim.
- Frontmatter: keep `name` + `description` (with same `TRIGGER when:`); **remove** `allowed-tools` and `argument-hint`.
- Keep the body's Codex-parity note consistent.
- After writing, the only `diff-skills.sh` difference for `document-feature` must be the missing `allowed-tools`/`argument-hint` lines.

**Tests:**
- `grep -c '^---$'` returns `2`; no `allowed-tools` / `argument-hint` lines present.
- `diff -u claude/skills/document-feature/SKILL.md codex/skills/document-feature/SKILL.md` shows ONLY the two frontmatter lines as difference.

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 3: Create `harvest` orchestrator skill (Claude)
**Status:** completed

**Create:**
- `claude/skills/harvest/SKILL.md`

**Modify:**
- None

**Description:**
Thin orchestrator for the harvest phase. Argument = feature path. Sequentially runs `try-learn-skill` → `document-feature`, each keeping its OWN gate. Gracefully skips a sub-skill that is unavailable in the project. One entry point so `implement` needs only one nudge instead of two.

**Requirements:**
- **Frontmatter:**
  - `name: harvest`
  - `description:` — purpose + `TRIGGER when:` "harvest", "faza harvest", "zbierz wiedzę z feature'a", "harvest this feature", run after `implement` before commit. Narrow trigger.
  - `allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md), Write(**/docs/modules/**/*.md)` — union of the two sub-skills' write scopes (harvest may execute their steps inline). Document this rationale in the body.
  - `argument-hint: "[ścieżka do tasks-*.md lub planning-*.md feature'a]"`
- **Body — sequence (deterministic order):**
  1. `try-learn-skill` on the feature path (its own human gate — extraction of a reusable procedure).
  2. `document-feature` on the feature path (its own mapping-confirm gate — module docs).
- **Body — graceful degradation:** Before each sub-step, check the sub-skill is available; if a project opted out of one (e.g. no learned-skills), **skip it and continue**, do not crash. State which sub-steps ran/were skipped in the closeout summary.
- **Body — closeout:** Remind the user to review the result in `git diff` before committing.
- Keep it THIN: no changelog, no history section, no duplicated logic from the sub-skills — it delegates.
- Document order rationale (independent, low-stakes; fixed for determinism: try-learn-skill → document-feature).

**Tests:**
- `grep -c '^---$'` returns `2`; frontmatter has narrow `TRIGGER when:`, union Write scope, `argument-hint`.
- Body invokes try-learn-skill then document-feature in that order, each "keeps its own gate", and includes the graceful-skip behavior + pre-commit git diff reminder.

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 4: Create `harvest` orchestrator skill (Codex mirror)
**Status:** completed

**Create:**
- `codex/skills/harvest/SKILL.md`

**Modify:**
- None

**Description:**
Codex mirror of Task 3. Identical body; drop Claude-only frontmatter.

**Requirements:**
- Copy Claude `harvest/SKILL.md` body verbatim.
- Frontmatter: keep `name` + `description`; remove `allowed-tools` and `argument-hint`.

**Tests:**
- `grep -c '^---$'` returns `2`; no `allowed-tools`/`argument-hint`.
- `diff -u` vs Claude version shows only the two frontmatter lines.

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 5: Reconcile `implement` nudge → harvest (both trees)
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/implement/SKILL.md` (nudge block at `:528-537`)
- `codex/skills/implement/SKILL.md` (nudge block at `:449-458`)

**Description:**
The existing best-effort nudge currently points at `try-learn-skill`. Replace it so it points at `harvest` (the single closeout entry point that runs try-learn-skill → document-feature). One nudge instead of two. Stays prompt-level/best-effort — not a hook.

**Requirements:**
- Replace the existing `### Optional: utrwal procedurę (best-effort)` block in BOTH files. Keep the same position (after the AC Fulfillment Report, before `## Begin`) and the same best-effort framing ("optional, forgetting is not an error, do not run automatically").
- New nudge points to `/absolutpowers:harvest @absolutpowers/feature/tasks-{slug}.md` and explains harvest runs try-learn-skill (procedure) + document-feature (module docs), each with its own gate, reviewed in git diff before commit.
- Rename/reframe the section heading to reflect harvest (e.g. `### Optional: faza harvest (best-effort)`).
- Apply identical edits to both Claude and Codex copies (this block is currently identical across trees — keep it so).

**Tests:**
- Both files reference `harvest`, no longer reference `try-learn-skill` in the nudge block.
- `diff -u` of the two nudge blocks across trees: identical.
- Nudge still sits between AC Fulfillment section and `## Begin`.

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example (replacement block):**
```markdown
### Optional: faza harvest (best-effort)

After reporting completion, optionally suggest one line to the user:

> Przed commitem rozważ fazę harvest:
> `/absolutpowers:harvest @absolutpowers/feature/tasks-{slug}.md`
> — uruchomi try-learn-skill (reużywalna procedura) i document-feature
> (docs modułu), każde z własnym gate; wynik przejrzyj w git diff przed commitem.

To czysto opcjonalne. Pominięcie nie jest błędem — nie blokuje ani nie cofa
completion. Nie odpalaj go automatycznie; tylko zaproponuj.
```

---

### Task 6: Reconcile note in `planning-learned-skills.md`
**Status:** completed

**Create:**
- None

**Modify:**
- `absolutpowers/feature/planning-learned-skills.md`

**Description:**
The learned-skills planning doc describes the implement nudge as "→ try-learn-skill". Since that nudge is now reconciled to "→ harvest" (Task 5), add a short reconciliation note so the planning doc is not misleading. Light-touch: a note, not a rewrite.

**Requirements:**
- Add a brief note (e.g. under "Soft nudge w `implement`" section ~`:106-111` and/or in the discussion table) stating the nudge was superseded by `harvest` (see `planning-harvest-docs.md`), since harvest now wraps try-learn-skill + document-feature.
- Do not delete the original rationale — annotate it.

**Tests:**
- `planning-learned-skills.md` contains a reference to `harvest` / `planning-harvest-docs.md` reconciling the nudge.

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 7: Document the module-doc template inside `document-feature` (both trees)
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/skills/document-feature/SKILL.md`
- `codex/skills/document-feature/SKILL.md`

**Description:**
Embed the canonical per-module doc template (sections + `doc-meta` block) inside the `document-feature` body so the skill generates a consistent structure. This is the structure NEW creates and UPDATE merges into. Done as a dedicated task to keep Task 1 focused; if the worker already inlined a complete template in Task 1, this task is verification-only.

**Requirements:**
- Template lives in the skill body as a fenced ```markdown block, used for both NEW and as the section contract for UPDATE.
- `doc-meta` is an **HTML comment in the doc body** (NOT frontmatter — `docs/` is not a skill, but keep it consistent and loader-safe, per planning + learned-meta precedent).
- Sections (Polish headings, per planning):
  - `# Moduł: {nazwa}`
  - `doc-meta` comment: `last-updated: YYYY-MM-DD`, `last-commit: <sha>`
  - `## Przegląd` — co to jest, za co odpowiada, granice
  - `## Jak działa` — kluczowe komponenty + przepływ, AI-as-dev: gdzie zacząć
  - `## Kluczowe decyzje (dlaczego)` — z planning rationale, tradeoffy
  - `## Punkty integracji` — zależności, API/kontrakty, eventy
  - `## Mapa plików` — `ścieżka — rola`
  - `## Pułapki / edge cases` — na co uważać przy rozbudowie
- Keep template identical in both trees (it's body content, not frontmatter).

**Tests:**
- Both `document-feature` bodies contain the full template with all 6 sections + `doc-meta` comment block.
- `diff_skills` shows no template-related difference between trees.

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example (`doc-meta` block):**
```markdown
# Moduł: {nazwa}

<!-- doc-meta
last-updated: YYYY-MM-DD
last-commit: <sha>
-->
```

---

### Task 8: README + docs — Harvest phase & 3-mechanism distinction
**Status:** completed

**Create:**
- None

**Modify:**
- `README.md`
- `CLAUDE.md` (repo root — optional pipeline-architecture mention)

**Description:**
Document the harvest phase, the two new skills, and the distinction between the three documentation mechanisms (`document-feature` vs `update-ai-context` vs `explain`). Update the pipeline position. Mirror the style of the existing `try-learn-skill` / `Learned Skills` README sections (`:319-374`).

**Requirements:**
- Add `### /absolutpowers:harvest` and `### /absolutpowers:document-feature` sections (what it does / when to use / input / output / example), styled like the existing skill sections.
- Add a "Harvest phase" subsection updating the pipeline diagram: after `implement`, optional `harvest → try-learn-skill + document-feature`. Extend or replace the existing `(optional) try-learn-skill` arrow (`:355-360`) so harvest is the closeout entry point.
- Add a distinction table/paragraph: **`document-feature`** (planning+diff → deep, per-module, on-demand docs in `docs/modules/`) vs **`update-ai-context`** (code-scan → broad/shallow CLAUDE.md, auto-injected) vs **`explain`** (ephemeral HTML, single-change human onboarding).
- Output paths: `document-feature` → `{your-project}/docs/modules/{module}.md`; `harvest` → orchestrates both.
- (Optional) In repo `CLAUDE.md`, add a one-line mention of the harvest phase in the pipeline architecture section.

**Tests:**
- README has `harvest` and `document-feature` sections + the 3-mechanism distinction + updated pipeline diagram.
- Internal consistency: output paths and trigger phrasing match the actual skills written in Tasks 1–4.

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 9: Bump version 3.5.0 → 3.6.0 (both manifests)
**Status:** completed

**Create:**
- None

**Modify:**
- `claude/.claude-plugin/plugin.json`
- `codex/.codex-plugin/plugin.json`

**Description:**
Minor bump (new skills = minor per repo SemVer policy). Both manifests must match.

**Requirements:**
- Set `"version": "3.6.0"` in both files.
- Change ONLY the version field; leave all other keys intact.
- Versions must be identical across both manifests.

**Tests:**
- `grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json` both show `3.6.0`.
- `python3 -m json.tool` parses both files (valid JSON).

**Implementation decisions / remarks:**
- [to be completed after task completion]

---

### Task 10: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- None

**Description:**
Run the project's verification gates against the fully integrated change. This repo has no compile/test step — verification = drift detection, JSON validity, and frontmatter structural sanity.

**Requirements:**
- Run drift check: `./scripts/diff-skills.sh` — the ONLY differences for `document-feature` and `harvest` must be the expected Claude-only frontmatter (`allowed-tools`, `argument-hint`). The `implement` nudge edit must keep that file's existing drift profile unchanged (nudge block identical across trees).
- Run `./scripts/diff-skills.sh --diff` and confirm no unexpected body drift for the new skills.
- Validate JSON: `python3 -m json.tool claude/.claude-plugin/plugin.json` and `python3 -m json.tool codex/.codex-plugin/plugin.json` (exit 0).
- Frontmatter sanity on all 4 new files: `grep -c '^---$'` returns `2` for each.
- Confirm both versions read `3.6.0`.
- Record any check intentionally skipped as `not applicable` with a reason.
- Do NOT mark completed if any check fails.

**Tests:**
- `diff-skills.sh` exits 0 and reports only expected drift for new skills.
- Both `plugin.json` parse as valid JSON.
- All 4 new SKILL.md files have exactly two frontmatter delimiters.

**Implementation decisions / remarks:**
- Commands executed: `./scripts/diff-skills.sh`; `diff <(sed strip) codex` per new skill; `python3 -m json.tool` both manifests; frontmatter well-formed check; `grep '"version"'`.
- Results: both new skills (`document-feature`, `harvest`) report ONLY the expected Claude-only frontmatter drift (`allowed-tools`, `argument-hint`); both manifests valid JSON at `3.6.0`; all 4 new SKILL.md frontmatter blocks well-formed (line 1 `---` + closing delim). `implement` "differs" is pre-existing drift — the nudge edit is identical across trees, adds no new drift.
- Skipped checks: naive `grep -c '^---$' == 2` — replaced with "well-formed frontmatter" check, because body `---` horizontal rules are a repo convention (try-learn-skill has 7). No build/test exists in this markdown-only repo.

**Example:**
```bash
./scripts/diff-skills.sh
./scripts/diff-skills.sh --diff
python3 -m json.tool claude/.claude-plugin/plugin.json >/dev/null && echo OK
python3 -m json.tool codex/.codex-plugin/plugin.json >/dev/null && echo OK
for f in claude/skills/document-feature claude/skills/harvest codex/skills/document-feature codex/skills/harvest; do
  echo "$f: $(grep -c '^---$' "$f/SKILL.md")"
done
grep '"version"' claude/.claude-plugin/plugin.json codex/.codex-plugin/plugin.json
```
```
