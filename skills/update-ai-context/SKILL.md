---
name: update-ai-context
description: >
  Creates or updates hierarchical CLAUDE.md files, discovers and saves project
  patterns to ./absolut-ai/patterns.md, and proposes or audits project rules
  in ./absolut-ai/rules.md. Auto-detects bootstrap vs update mode.
  TRIGGER when: new project setup, "bootstrap AI docs", "zaktualizuj CLAUDE.md",
  "update AI context", project onboarding, missing CLAUDE.md detected,
  significant codebase changes, "refresh patterns", "discover conventions".
allowed-tools: Read, Glob, Grep, Bash(find:*), Bash(git:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(tree:*), Bash(ls:*), Bash(mkdir:*), Write, Edit
argument-hint: "[ścieżka do projektu, default: .]"
---

# Update AI Context — CLAUDE.md, Patterns & Rules

You are a Senior Software Engineer managing AI-assisted development documentation. Your task is to create or update:
1. **CLAUDE.md files** — hierarchical codebase documentation for AI agents
2. **`./absolut-ai/patterns.md`** — discovered code patterns and conventions
3. **`./absolut-ai/rules.md`** — project rules for code review compliance

## Mode Detection

Check what exists in the project:
- **No CLAUDE.md** → **Bootstrap mode** (create everything from scratch)
- **CLAUDE.md exists** → **Update mode** (audit and refresh)

Create `./absolut-ai/` directory if it doesn't exist.

---

## PHASE 1: CLAUDE.md (Bootstrap or Update)

### Bootstrap (no existing CLAUDE.md)

#### Step 1: Analyze Project Structure

Scan the codebase to understand:
- **Tech stack**: Languages, frameworks, key libraries
- **Architecture pattern**: Monolith, microservices, modular monolith, etc.
- **Package/module structure**: How code is organized
- **Domain boundaries**: Logical separations (features, domains, layers)
- **Shared code**: Utils, helpers, common types
- **Configuration**: How settings are managed
- **Testing setup**: Patterns, locations, utilities
- **Verification commands**: How the project builds, tests, type-checks, lints, and runs formatter checks

#### Step 2: Identify CLAUDE.md Locations

Place CLAUDE.md files at meaningful boundaries:

**Good locations:**
- Project root (always)
- Feature/domain packages (`src/orders/`, `src/payments/`)
- Major architectural layers if distinct (`src/api/`, `src/core/`)
- Shared utilities (`src/shared/`, `src/common/`)
- Complex subsystems that need explanation

**Avoid:**
- Every single folder (too granular)
- Folders with only 1-2 simple files
- Test folders (unless complex test utilities)
- Generated code folders

#### Step 3: Create Root CLAUDE.md

```markdown
# [Project Name]

## Stack
- **Language:** [language + version]
- **Framework:** [framework]
- **Database:** [database]
- **Key libraries:** [list main ones]

## Architecture
[2-3 sentences describing overall architecture pattern]

## Project Structure
```
src/
├── [package]/     # [one-line description]
├── [package]/     # [one-line description]
└── shared/        # [one-line description]
```

## Conventions
- **Files:** [naming convention]
- **Functions/Methods:** [naming convention]
- **Tests:** [location pattern, naming]

## Key Patterns
- [Pattern]: [one-line description]

## Getting Started
- Build: `[command]`
- Test: `[command]`
- Run: `[command]`

## Verification Commands
- Backend build/test: `[command]`
- Frontend build/typecheck: `[command]`
- Lint: `[command]`
- Formatter check: `[command]`

## AI Documentation

This project uses hierarchical CLAUDE.md files for AI-assisted development.
- Root CLAUDE.md: Project overview (you are here)
- Package CLAUDE.md: Domain-specific details in each major package
- `./absolut-ai/patterns.md`: Discovered code patterns
- `./absolut-ai/rules.md`: Project rules for code review

Run `/absolut-ai:update-ai-context` to refresh documentation.
```

#### Step 4: Create Package CLAUDE.md Files

For each identified package/module:

```markdown
# [Package Name]

## Purpose
[2-3 sentences: what this package does, its responsibility]

## Key Concepts
- **[Concept]:** [brief explanation]

## Main Components
| File | Responsibility |
|------|----------------|
| `ServiceName.ts` | [what it does] |

## Dependencies
- **Internal:** [which other packages this depends on]
- **External:** [key external libraries used here]

## Patterns Used
- [Pattern]: [how it's applied here]

## Important Rules
- [Business rule or constraint]

## Last Verified
- **Date:** YYYY-MM-DD
- **Commit:** [short hash]
```

### Update (CLAUDE.md exists)

1. Find all existing CLAUDE.md files, note location and last modified date
2. **Detect drift:** files that no longer exist, renamed packages, changed dependencies, shifted commands
3. **Detect gaps:** new folders with 3+ files lacking CLAUDE.md, new major dependencies
4. Update existing CLAUDE.md files — preserve structure, fix inaccuracies, add new components
5. Create missing CLAUDE.md files where warranted
6. Update `## Last Verified` sections

---

## PHASE 2: Patterns Discovery → `./absolut-ai/patterns.md`

Scan the entire codebase for recurring patterns. This file is read by `generate-tasks` and `implement` skills to ensure new code follows established conventions.

### What to look for:
- **Structural patterns**: Repository, Service, Factory, Controller, etc.
- **Custom abstractions**: Result types, Either monads, custom hooks, base classes
- **Error handling**: Exception hierarchy, error response format, logging approach
- **Data validation**: Schema validation, input sanitization, guard clauses
- **API conventions**: Response format, pagination, error codes, auth patterns
- **Testing patterns**: Fixtures, mocks, builders, test utilities, naming
- **Configuration**: Env vars, config files, feature flags
- **Verification commands**: build, typecheck, lint, formatter checks, project wrappers
- **Naming conventions**: Files, functions, variables, constants (what is ACTUALLY followed)

### Pattern must have proof
Only document patterns used **3+ times** in the codebase. Each pattern MUST include a concrete code reference.

### Format for `./absolut-ai/patterns.md`:

```markdown
# Project Patterns

> Auto-generated by `/absolut-ai:update-ai-context` on YYYY-MM-DD.
> Read by `generate-tasks` and `implement` skills.

## Structural Patterns

### [Pattern Name]
**What:** [one-line description]
**Where:** [which layer/packages use this]
**Example:** `path/to/file.ts:L15-45`
**Convention:**
- [specific rule 1]
- [specific rule 2]

## Error Handling

### [Pattern Name]
**What:** [description]
**Example:** `path/to/file.ts:L10-30`
**Convention:**
- [rules]

## Testing

### [Pattern Name]
**What:** [description]
**Example:** `path/to/test.ts:L5-25`
**Convention:**
- [rules]

## Naming Conventions

| What | Convention | Example |
|------|-----------|---------|
| Files | [convention] | `user-service.ts` |
| Components | [convention] | `UserProfile.tsx` |
| Tests | [convention] | `user-service.spec.ts` |
```

### Update mode
If `./absolut-ai/patterns.md` already exists:
- Check if documented patterns still exist in code (remove dead ones)
- Discover new patterns that emerged since last scan
- Update code references if files moved
- Mark file with new scan date

---

## PHASE 3: Rules → `./absolut-ai/rules.md`

Rules are prescriptive constraints used by `/absolut-ai:review` during code review (Phase 3: Rules Check).

### Bootstrap (no `./absolut-ai/rules.md`)

Based on patterns discovered in Phase 2 and project analysis, **propose** a draft rules file. Present the proposed rules to the user and ask for confirmation before saving.

```markdown
# Project Rules

> Used by `/absolut-ai:review` for automated rules checking.
> Last updated: YYYY-MM-DD

## Required Libraries
- [library]: used for [purpose] (not [alternative])

## Forbidden Patterns
- [pattern]: [why it's forbidden]

## Architecture
- [rule]: [description]

## Conventions
- [rule]: [description]

## Testing
- [rule]: [description]
```

Tell the user: "Proponuję następujące rules na bazie analizy kodu — przejrzyj i powiedz co zmienić."

### Update (`./absolut-ai/rules.md` exists)

1. Read existing rules
2. Compare against current codebase — are any rules systematically violated? (might be outdated)
3. Are there new conventions not yet captured as rules?
4. Report findings but **do not auto-modify** — rules require human approval
5. Propose additions/removals and ask for confirmation

---

## PHASE 4: Change Report

Output a summary of ALL changes across all three areas:

```markdown
## AI Context Update Report

### CLAUDE.md Changes
| File | Action | Details |
|------|--------|---------|
| `CLAUDE.md` | updated | Updated stack, added 2 patterns |
| `src/payments/CLAUDE.md` | created | New payment processing module |

### Patterns (./absolut-ai/patterns.md)
- **New patterns found:** [count]
- **Removed (dead) patterns:** [count]
- **Updated references:** [count]

### Rules (./absolut-ai/rules.md)
- **Status:** [created draft / no changes / proposed updates]
- **Proposed additions:** [list if any]
- **Potentially outdated:** [list if any]

### Requires Manual Review
- [ ] [items needing human decision]
```

---

## Guidelines

**Content principles:**
- Write for AI agents, not humans - be factual and precise
- Focus on WHAT and WHERE, less on WHY
- Include concrete file names and paths
- Patterns need proof — link to real code, not assumptions
- Rules need human approval — propose, don't impose

**Size guidelines:**
- Root CLAUDE.md: 50-100 lines
- Package CLAUDE.md: 30-60 lines
- patterns.md: as long as needed, but each pattern stays concise
- rules.md: focused, actionable constraints

**Conflict resolution:**
1. **Code wins** — update documentation to match reality
2. **Note oddities** — if code seems wrong, flag it but document actual behavior
3. **Don't assume intent** — describe what IS, not what SHOULD BE

---

## Begin

1. Check what exists → determine mode per area
2. Analyze project structure
3. Phase 1: Bootstrap or update CLAUDE.md files
4. Phase 2: Discover and save patterns
5. Phase 3: Propose or audit rules
6. Phase 4: Output change report
