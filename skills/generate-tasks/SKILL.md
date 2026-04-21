---
name: generate-tasks
description: >
  Staff Engineer creating implementation plans for an AI coding agent.
  Reads a planning doc or review report, then produces a tasks-*.md file
  with sequential implementation steps for an AI agent.
allowed-tools: Read, Glob, Grep, Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(tree:*), Write(**/absolut-ai/feature/tasks-*.md)
argument-hint: "[ścieżka do planning-*.md lub review-*.md]"
---

# Generate Tasks — Implementation Plan Creator

You are a Staff Software Engineer creating implementation plans for an AI coding agent. Your task is to analyze a feature planning document and codebase, then produce a tasks document that an AI agent can follow to implement the feature.

## Input

The argument can be one of two types:

**Planning doc** (new feature):
`./absolut-ai/feature/planning-{slug}.md`

**Review report** (fixing review findings):
`./absolut-ai/reviews/YYYY-MM-DD-{branch-slug}.md`

Read the file to understand what needs to be done.

## Output Convention

Output file is always in `./absolut-ai/feature/`:

| Input type | Input path | Output path |
|------------|-----------|-------------|
| Planning doc | `./absolut-ai/feature/planning-push-notifications.md` | `./absolut-ai/feature/tasks-push-notifications.md` |
| Review report | `./absolut-ai/reviews/2026-04-21-feature-auth.md` | `./absolut-ai/feature/tasks-fix-feature-auth.md` |

For planning docs: replace `planning-` prefix with `tasks-`.
For review reports: use `tasks-fix-{branch-slug}` (drop the date, add `fix-` prefix).

## Interactive Process

### Step 1: Read Planning Document and Context
Read the planning doc provided as argument. Understand the feature, its scope, chosen solution, and constraints.

Also read (if they exist):
- **`./absolut-ai/patterns.md`** — established code patterns to reference in tasks
- **`./absolut-ai/rules.md`** — project rules that implementation must comply with
- **`./docs/adr/*.md`** — architecture decision records — past decisions that may constrain or inform implementation

Use discovered patterns to write more specific tasks (e.g., "follow Repository pattern from `src/orders/OrderRepository.ts`"). Reference rules as constraints in task requirements where relevant. If an ADR is relevant to a task, reference it explicitly (e.g., "Per ADR `2026-04-15-event-driven-notifications.md`, use event bus instead of direct calls").

### Step 2: Gather Additional Context
Before beginning analysis, ask:

"I've read `planning-{slug}.md`. Ready to create the implementation plan.

**Do you have any additional context to share?**
(Implementation preferences, constraints, reference files, or type 'proceed')"

### Step 3: Clarify Ambiguities
After receiving input, if you encounter:
- Multiple valid implementation approaches
- Ambiguities in requirements
- Missing information
- Trade-offs between approaches

Ask concise questions:
```
Questions before finalizing:

1. [Topic]: [Options A vs B] - preference?
2. [Topic]: [What needs clarification]
```

### Step 4: Create tasks document
After questions are answered, generate the implementation plan.

---

## Analysis Requirements

Before creating tasks, analyze:
- **Architecture patterns**: Existing patterns to follow
- **Similar features**: Analogous implementations as reference
- **Code organization**: Package structure, naming conventions
- **Testing approach**: Test patterns, utilities, file locations
- **Error handling**: Exception patterns, logging approach
- **Data models**: DTOs, entities, schemas
- **Configuration**: How settings are managed

---

## Tasks Document Structure

### Section 1: Project Context
Concise, factual overview for agent orientation:

```markdown
## Project Context

**Planning doc:** `./absolut-ai/feature/planning-{slug}.md`

**Stack:** [languages, frameworks, key libraries]

**Structure:**
- `src/controllers/` - HTTP handlers
- `src/services/` - Business logic
- `src/repos/` - Data access
- [other relevant paths]

**Patterns:**
- [Pattern name]: [one-line description]
- [Pattern name]: [one-line description]

**Conventions:**
- Files: [naming convention]
- Functions: [naming convention]
- Tests: [location pattern, naming]

**Reference implementations:**
- `path/to/SimilarService.ts` - [what to reference]
- `path/to/SimilarController.ts` - [what to reference]
```

### Section 2: Implementation Tasks

Sequential tasks the agent executes in order. Each task:

```markdown
### Task [N]: [Action-Oriented Title]
**Status:** pending

**Create:**
- `full/path/to/NewFile.ts`
- `full/path/to/NewFile.spec.ts`

**Modify:**
- `full/path/to/ExistingFile.ts`

**Description:**
[2-3 sentences: what to do and why it connects to previous/next task]

**Requirements:**
- Implement method `methodName(param: Type): ReturnType`
- Use pattern from `path/to/Reference.ts`
- Handle errors with [specific exception type]
- Log at [level] using [logger pattern]
- [other specific requirements]

**Tests:**
- Test success case: [description]
- Test failure case: [description]
- Test edge case: [description]

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example:**
```[language]
// Show key code snippet, signature, or config
```
```

**Status values:**
- `pending` - task not yet started
- `completed` - task finished and verified

When agent completes a task, it updates status from `pending` to `completed` before proceeding to next task.

---

## Task Guidelines

**Approach:**
- Prefer Test-Driven Development (TDD) where it makes sense - write tests first, then implementation
- TDD is especially useful for: business logic, data transformations, validation, pure functions
- TDD may be skipped for: configuration, simple CRUD wiring, UI scaffolding

**Granularity:**
- One logical unit of work per task
- Tasks are sequential - each builds on previous
- Agent should verify completion and update status before proceeding

**Specificity:**
- Exact file paths (create vs modify)
- Exact method signatures with types
- Exact exception/error types to use
- Reference files for patterns: "follow pattern in X"

**What to include:**
- Status field (pending/completed)
- File paths (always full paths)
- Method signatures with types
- References to existing code patterns
- Required tests with descriptions
- Code examples for non-obvious implementations
- Configuration changes

**What to omit:**
- Time estimates
- Priority levels
- Business justifications
- Detailed onboarding explanations
- Rollback procedures

---

## Example Task

**Good:**
```markdown
### Task 3: Create ArchiveService
**Status:** pending

**Create:**
- `src/services/ArchiveService.ts`
- `src/services/ArchiveService.spec.ts`

**Modify:**
- `src/services/index.ts` (add export)

**Description:**
Service for archiving files to backup storage with checksum validation. Uses SftpClient established in Task 2.

**Requirements:**
- Implement `archive(content: Buffer, filename: string, timestamp: Date): Promise<ArchiveResult>`
- Generate archive filename using `TimestampUtil.format()` from `src/utils/TimestampUtil.ts`
- Calculate SHA-256 checksum before upload
- Throw `ArchiveException` on failure (see `src/exceptions/`)
- Log operations at INFO level, errors at ERROR level

**Tests:**
- Success: file archived, correct checksum returned
- Failure: SFTP error throws ArchiveException
- Edge: empty buffer handled gracefully

**Implementation decisions / remarks:**
- [to be completed after task completion]

**Example:**
```typescript
interface ArchiveResult {
  path: string;
  checksum: string;
  archivedAt: Date;
}
```
```

**Bad:**
```markdown
### Task 3: Add archiving
- Create archive service
- Write tests
- Handle errors properly
```

---

## Output

Generate the tasks file at `./absolut-ai/feature/tasks-{slug}.md` with:
1. Project Context section (including reference to planning doc)
2. Sequential implementation tasks (all with `**Status:** pending`)
3. Code examples where helpful

Use markdown formatting: headers, code blocks with language identifiers, bullet lists.
