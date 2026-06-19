# Phase 1: Author the `constitution` skill (both trees)

## Status
completed

## Parent
`./absolutpowers/feature/tasks-constitution.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-constitution/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- None (first phase).

### Provides (for later phases)
- File `claude/skills/constitution/SKILL.md` — full skill spec (source of truth).
- File `codex/skills/constitution/SKILL.md` — mirror (Claude-only frontmatter drift removed).
- The exact `constitution.md` output path string `absolutpowers/constitution.md` and its `> Wersja: … · Ratyfikowano: … · Egzekwowana przez: …` header format, referenced by Phases 2–4 when they wire binding context.
- The demarcation sentence "pryncypia → constitution, mechanika → rules.md / update-ai-context" reused verbatim by Phase 3.

## Read Scope
- `claude/skills/update-ai-context/SKILL.md` (model the bootstrap/update + frontmatter + Phase 3 rules tier)
- `claude/skills/problem-discuss/SKILL.md` (model recent skill prose style, TRIGGER wording, "vs X" collision note)
- `codex/skills/update-ai-context/SKILL.md` (confirm Codex frontmatter shape — no `allowed-tools`/`argument-hint`)
- `absolutpowers/feature/planning-constitution.md` (binding spec, esp. struktura `constitution.md`)

## Write Scope
- `claude/skills/constitution/SKILL.md`
- `codex/skills/constitution/SKILL.md`

## Objective
Create the new `constitution` skill in both trees. It is a deliberate ratification ceremony that creates/updates `absolutpowers/constitution.md` as a set of versioned **artykuły** (pryncypia). It supports Bootstrap (code scan → proposed articles) and Amend (audit code vs articles → flag dead article or code-to-fix). It never auto-overwrites — every change needs explicit human ratification. It hard-refuses to write mechanical lint-level rules (those belong to `rules.md` / `update-ai-context`).

## Tasks

### Task 1: Write `claude/skills/constitution/SKILL.md`
**Status:** completed

**Create:**
- `claude/skills/constitution/SKILL.md`

**Description:**
Author the canonical (Claude) skill spec. This is the source of truth; the Codex mirror in Task 2 derives from it. Follow the prose style and section conventions of `update-ai-context` and `problem-discuss`.

**Requirements:**
- Frontmatter: `name: constitution`; bilingual `description:` with narrow TRIGGER (pryncypia / konstytucja / ratyfikacja / niezmienniki / wartości projektu / amendment) and an explicit "NIE wyzwalaj na: reguły mechaniczne lint-level → `update-ai-context`" anti-trigger; `allowed-tools: Read, Glob, Grep, Bash(find:*), Bash(git:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(mkdir:*), Write, Edit`; `argument-hint: "[ścieżka do projektu, default: .]"`.
- Body MUST specify: Mode detection (Bootstrap if no `absolutpowers/constitution.md`, else Amend); the exact output path `absolutpowers/constitution.md`; the article structure and file header from the planning doc (`# Konstytucja projektu — {nazwa}` + `> Wersja: X.Y.Z · Ratyfikowano: YYYY-MM-DD · Egzekwowana przez: feature-discuss, generate-tasks, implement, review`, `## Artykuł N: {nazwa}` with **Norma** (MUST/SHOULD/NEVER) / **Dlaczego** / **Jak stosować** / **Przykład**, and a `## Changelog`).
- Body MUST specify the ratification rule: present proposed/amended articles to the user and require explicit approval before writing; never auto-overwrite. Semver bump rules: NEVER-removal/incompatible = major, new article = minor, wording/clarification = patch; stamp `Ratyfikowano` date and append a changelog line per amendment.
- Body MUST include the hard boundary (scope creep guard): constitution = pryncypia/osąd only; mechanical rules are redirected to `update-ai-context`/`rules.md`. Reuse one verbatim demarcation sentence (Phase 3 reuses it).
- Body MUST include a "vs update-ai-context" collision note mirroring how `problem-discuss` documents its "vs debug" boundary.

**Tests:**
- Manual: frontmatter parses (valid YAML), `name` matches dir, TRIGGER + anti-trigger present.
- Manual: spec covers Bootstrap, Amend, ratification/no-auto-overwrite, semver+changelog, scope-creep boundary, and the exact `constitution.md` structure.
- Manual: skill writes only `absolutpowers/constitution.md` (no mechanical-rule output).

### Task 2: Write `codex/skills/constitution/SKILL.md` (mirror)
**Status:** completed

**Create:**
- `codex/skills/constitution/SKILL.md`

**Description:**
Mirror Task 1 into the Codex tree. Identical body; strip Claude-only frontmatter so `diff-skills.sh` reports only expected drift.

**Requirements:**
- Copy the Claude body verbatim (same Bootstrap/Amend/ratification/structure/boundary content).
- Frontmatter: keep `name` + `description`; REMOVE `allowed-tools` and `argument-hint` (Codex has no plugin tool restriction / argument hint).
- In the body, drop or neutralize any Claude-only agent/gate phrasing (Codex runs without gates) — match how other codex skills omit gate sections.

**Tests:**
- Manual: `./scripts/diff-skills.sh --diff` for `constitution` shows ONLY expected drift (`allowed-tools`, `argument-hint`, any gate lines) — no divergence in core procedure.
- Manual: Codex frontmatter has no `allowed-tools`/`argument-hint`.

## Phase Verification
Run:
- `./scripts/diff-skills.sh` — confirm `constitution` appears and reports only expected Claude-only drift.
- `grep -l "name: constitution" claude/skills/constitution/SKILL.md codex/skills/constitution/SKILL.md` — both exist.

## Completion Criteria
- All phase tasks are completed.
- All changes are within Write Scope.
- Phase verification commands pass.
- `implementation-context.md` updated with the final `constitution.md` header format string and demarcation sentence for Phases 2–4.
- All items in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- Both skill files created from scratch; no prior `constitution` skill existed in either tree.
- Claude frontmatter: `allowed-tools` with Read/Glob/Grep/Bash variants/Write/Edit and `argument-hint`; Codex mirror strips both (only `name` + `description` retained).
- Exact output path `absolutpowers/constitution.md` and header format `> Wersja: X.Y.Z · Ratyfikowano: YYYY-MM-DD · Egzekwowana przez: feature-discuss, generate-tasks, implement, review` specified verbatim in the Format section of both files.
- Demarcation sentence used verbatim: "Konstytucja = pryncypia/osąd. Mechanika = `rules.md` / `update-ai-context`." placed in the Granica section.
- `vs update-ai-context` collision note included as a dedicated bold paragraph in the Granica section, mirroring how `problem-discuss` documents its "vs debug" boundary.
- diff-skills.sh shows `~ constitution (differs)` — only allowed drift (2 frontmatter lines removed in Codex); body is identical.
- Article structure uses Roman numerals (I, II, III) and four fields: Norma (MUST/SHOULD/NEVER), Dlaczego, Jak stosować, Przykład (optional).
- Archivization pattern for removed articles: `## Artykuł N: [ARCHIWUM] {nazwa}` preserves changelog integrity.
