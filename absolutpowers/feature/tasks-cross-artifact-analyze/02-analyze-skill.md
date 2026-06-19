# Phase 2: Ruch 2 — new `analyze` skill (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-cross-artifact-analyze.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-cross-artifact-analyze/implementation-context.md`
- `./absolutpowers/feature/planning-cross-artifact-analyze.md` (sections "Oczekiwane zachowanie", "Sześć klas rozjazdów", "Werdykt", "Ruch 2", "Edge cases i ryzyka")

## Context Contract

### Requires (from previous phases)
- None (independent; reuses existing `AC-N:` / `Traces to:` infrastructure already in the codebase — no new format).

### Provides (for later phases)
- `claude/skills/analyze/SKILL.md` — full skill prompt (Claude frontmatter with `allowed-tools` + `argument-hint`).
- `codex/skills/analyze/SKILL.md` — mirror of the Claude body, frontmatter without `allowed-tools`/`argument-hint`, no Claude-only subagent-delegation paragraph.
- Settled behavior referenced by Phase 3: report path `absolutpowers/reviews/analyze-{slug}.md`, verdict `CONSISTENT`/`INCONSISTENT`, on-demand (no gate), audit-only boundary.

## Read Scope
- `claude/skills/review/SKILL.md` (closest cousin — phased report style, file:line evidence, save-to-reviews/ convention)
- `claude/skills/generate-tasks/SKILL.md` (AC traceability + `Traces to:` + orchestrated phase-file structure / Write scope)
- `claude/agents/review-implementation.md` (how AC fulfillment + changed-files are reasoned about)
- `codex/skills/review/SKILL.md` (Codex frontmatter convention — no `allowed-tools`/`argument-hint`)

## Write Scope
- `claude/skills/analyze/SKILL.md`
- `codex/skills/analyze/SKILL.md`

## Objective
Create a new on-demand skill `analyze` that builds a consolidated AC→Task→code traceability matrix for a feature slug, detects the six divergence classes (each with `file:line` / `AC-N` / `Task N` evidence), emits a report to `absolutpowers/reviews/analyze-{slug}.md`, and returns a `CONSISTENT` / `INCONSISTENT` verdict. It audits and routes only — never fixes, plans, or writes code. Implement in both trees with identical body logic.

## Tasks

### Task 1: Author the canonical Claude `analyze` skill
**Status:** completed

**Create:**
- `claude/skills/analyze/SKILL.md`

**Description:**
Write the full skill prompt. Body is the canonical source that the Codex mirror (Task 2) copies. Follow the bilingual convention used across this repo: Polish for user-facing prose and report labels, English for technical identifiers and code/format blocks.

**Requirements (frontmatter):**
- YAML frontmatter:
  - `name: analyze`
  - `description:` a multi-line block describing purpose + a `TRIGGER when:` clause with NARROW triggers that do not collide with `review`/`triada-review`: trace'owalność / spójność artefaktów / pokrycie AC / "audyt cross-artifact" / "czy taski pokrywają plan" / "AC→task→kod" / "spójność planning↔tasks↔kod". Explicitly add a `NIE wyzwalaj na:` clause directing code-quality → `review`, architecture → `triada-review`.
  - `allowed-tools:` Read, Glob, Grep, Bash (git/cat/head/tail/wc/find/mkdir/diff as needed for reading diff + writing report dir), and `Write(**/absolutpowers/reviews/*.md)`. Mirror the scoping style of `claude/skills/review/SKILL.md`'s frontmatter. NO Edit/Write outside `absolutpowers/reviews/`.
  - `argument-hint: "[slug feature'a, np. push-notifications]"`

**Requirements (body — must cover all of these as explicit prompt sections):**
- **Input & artifact auto-detection:** argument is a feature slug. Discover which artifacts exist for that slug and audit only the available chain links (graceful degradation, never error):
  - planning: `./absolutpowers/feature/planning-{slug}.md` (and epic variant `./absolutpowers/feature/{epic-slug}/planning-*.md` + `planning-main.md` if present)
  - tasks: `./absolutpowers/feature/tasks-{slug}.md` (single-file) OR `./absolutpowers/feature/tasks-{slug}/` (orchestrated — read phase files + `implementation-context.md`)
  - diff: current branch vs `main` (via `git diff`/`git diff --name-only`)
- **AC extraction:** parse all `AC-N:` items from the planning doc's `## Acceptance Criteria` (Happy path / Edge cases / Security subsections). If no AC section: audit only task↔code, and clearly report "brak sekcji AC — pominięto wymiar AC→Task".
- **Traces-to extraction:** parse `**Traces to:** AC-N, ...` from each task, in BOTH single-file tasks and orchestrated phase files.
- **Matrix build:** construct the consolidated table **AC → Task(i) → Plik(i)/symbol(e) w diffie**. The visual matrix (AC × Task × Plik) is the core of the report.
- **Code↔task mapping:** map changed files back to tasks. For orchestrated, use each phase's `Write scope` globs + file paths named in tasks as the expected boundary. Treat Write scope as the boundary; flag a change only when it falls OUTSIDE every task/phase Write scope (mitigates false-positive scope-creep from broad globs).
- **Six divergence classes** (detect each, each finding carries evidence — `file:line`, `AC-N`, or `Task N`):
  1. AC bez taska — AC in plan, no `Traces to` in any task → coverage gap. **(BLOCKS)**
  2. Task bez AC — task exists, `Traces to: none` without an infra justification → orphan work. **(WARNS)**
  3. Task bez kodu — task `completed` but no corresponding change in the diff → status lies. **(BLOCKS)**
  4. Kod bez taska — diff change maps to no task / outside all Write scopes → scope creep. **(BLOCKS)**
  5. AC bez weryfikacji — AC covered by a task but no test references that AC. **(WARNS)**
  6. Sprzeczność — planning says X, task/code does non-X (different API contract, different rule). **(BLOCKS)**
- **Verdict:**
  - `CONSISTENT` — chain closed for all available links, zero class-1/3/4/6 divergences.
  - `INCONSISTENT` — at least one blocking divergence; report lists each with evidence + routing. Classes 2/5 are warnings only (do not, by themselves, flip the verdict).
- **Report output:** save full report to `absolutpowers/reviews/analyze-{slug}.md` (create dir if missing). Report contains: the AC×Task×Plik matrix, per-class findings with evidence, the verdict, and a routing section.
- **Hard boundary + routing:** audits and reports only — does NOT fix, does NOT add tasks, does NOT write code. Route divergences: "AC bez taska" / "missing task" → `generate-tasks`; "missing code" (Task bez kodu) → `implement`; "Sprzeczność" → back to the responsible artifact owner (planning/tasks). Include an explicit "Red Flags — STOP" subsection: if the skill finds itself about to edit code or write tasks, stop and route instead.
- **Degradation cases** (state behavior explicitly): only planning exists → AC→Task is empty, report "brak tasków do audytu", not an error; no AC section → task↔code only; orchestrated mapping imprecise → prefer false-negative over false-positive on scope creep, note the limitation.
- **vs review / vs triada-review note:** one short paragraph: `analyze` checks trace'owalność/kompletność łańcucha across artifacts; `review` checks code quality (4 phases) on the branch; `triada-review` checks architecture/security/UI. Different dimension, not a merge.
- **Claude-only optional delegation:** one short paragraph noting the matrix build MAY be delegated to a subagent for clean isolated reading, but the core logic lives in this prompt (works in Codex too). **Mark this paragraph clearly so Task 2 can omit it from the Codex mirror.**

**Tests:**
- Frontmatter parses: `name: analyze`, has `allowed-tools` + `argument-hint`, `description` contains `TRIGGER when:` and `NIE wyzwalaj na:`.
- Body contains all six divergence classes with the blocking/warning split (1/3/4/6 block, 2/5 warn).
- Body names report path `absolutpowers/reviews/analyze-{slug}.md` and both verdicts `CONSISTENT`/`INCONSISTENT`.
- Body contains the hard-boundary / routing section and the "vs review" note.

### Task 2: Mirror the skill to Codex
**Status:** completed

**Create:**
- `codex/skills/analyze/SKILL.md`

**Description:**
Produce the Codex copy. Identical body logic; only the platform-specific deltas differ, matching the established drift pattern for every other shared skill.

**Requirements:**
- Copy the Claude body verbatim EXCEPT:
  - Frontmatter: drop `allowed-tools` and `argument-hint`. Keep `name` and `description` (with the same TRIGGER/NIE-wyzwalaj clauses).
  - Remove the Claude-only "optional subagent delegation" paragraph marked in Task 1.
- Everything else (six classes, matrix, verdict, report path, hard boundary, routing, degradation, vs-review note) stays identical.
- After writing, run `./scripts/diff-skills.sh --diff` and confirm the `analyze` diff shows ONLY the expected drift (the two frontmatter keys + the delegation paragraph). No unexpected divergence in the audit logic.

**Tests:**
- `codex/skills/analyze/SKILL.md` exists; frontmatter has NO `allowed-tools` and NO `argument-hint`.
- `./scripts/diff-skills.sh` lists `analyze` as present in both trees (no `! analyze (missing ...)`).
- The `--diff` output for `analyze` contains only the expected frontmatter + delegation-paragraph drift.

## Phase Verification
Run:
- `python3 -c "import sys,re; t=open('claude/skills/analyze/SKILL.md').read(); assert t.startswith('---') and 'name: analyze' in t" && echo OK` (frontmatter sanity)
- `grep -c "CONSISTENT\|INCONSISTENT" claude/skills/analyze/SKILL.md codex/skills/analyze/SKILL.md`
- `./scripts/diff-skills.sh`

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope unless explicitly justified.
- Phase verification commands pass.
- `implementation-context.md` is updated with only durable handoff facts.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Claude canonical: 6-step structure (Krok 0–6). Krok 0 = auto-detection + degradation cases. Krok 1 = AC extraction. Krok 2 = Traces-to extraction (single-file + orchestrated). Krok 3 = matrix build. Krok 4 = six divergence classes. Krok 5 = verdict. Krok 6 = report save.
- Frontmatter `allowed-tools` scoped identically to `review` pattern: Read, Glob, Grep, Bash variants (git/cat/head/tail/wc/find/mkdir/diff), Write scoped to `**/absolutpowers/reviews/*.md` only. No Edit/Write outside that path.
- Claude-only delegation paragraph marked with HTML comments `<!-- CLAUDE-ONLY -->` / `<!-- /CLAUDE-ONLY -->` for easy strip in Codex mirror.
- Codex mirror produced by dropping `allowed-tools` + `argument-hint` frontmatter and removing the marked delegation paragraph. All audit logic (6 classes, matrix, verdict, report path, hard boundary, routing, degradation, vs-review note) is verbatim identical.
- `diff-skills.sh --diff` confirms analyze drift = exactly 2 frontmatter keys + 1 delegation paragraph (lines 14-15 and 324-326 in Claude file). No unexpected audit logic divergence.
- Report path: `absolutpowers/reviews/analyze-{slug}.md`. Verdict tokens: `CONSISTENT` / `INCONSISTENT`.
- Blocking classes (1/3/4/6) vs warning-only (2/5) clearly labeled with `**(BLOKUJE)**` / `**(OSTRZEŻENIE)**` in class headings and in the divergence section of the report format template.
