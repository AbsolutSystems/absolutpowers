# Testing Anti-Patterns (AbsolutPowers)

**Load when:** writing or changing tests, adding mocks, or tempted to add
test-only methods to production code. Complements `**Test-first:**` markers from
`generate-tasks` / `implement` (no separate full TDD skill).

Grafted from obra/superpowers `test-driven-development/testing-anti-patterns.md`
(MIT — see `LICENSE-VENDORED`); wording adapted for AbsolutPowers.

## Iron laws

1. **NEVER** test mock behavior
2. **NEVER** add test-only methods to production classes
3. **NEVER** mock without understanding dependencies

**Core principle:** Test what the code does, not what the mocks do.

## Anti-pattern 1: Testing mock behavior

```typescript
// ❌ BAD — asserts the mock exists
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// ✅ GOOD — assert real behavior / role / output
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

**Gate:** before asserting on a mock element, ask: “Am I testing real behavior
or mock existence?” If mock existence → delete assertion or unmock.

## Anti-pattern 2: Test-only methods in production

```typescript
// ❌ BAD — destroy() only used in tests, looks like production API
class Session { async destroy() { /* cleanup */ } }

// ✅ GOOD — test utilities own cleanup
// test-utils/cleanupSession(session)
```

Do not pollute production types with hooks that exist only for the test harness.

## Anti-pattern 3: Mocking without understanding

- Map real dependencies before replacing them
- Prefer narrow fakes at boundaries (HTTP, DB, clock) over mocking the unit under test
- If you cannot explain what the mock stands for, do not mock yet

## Tie-in to AbsolutPowers

- Planner sets `**Test-first:** yes | no (reason)` in tasks
- Implementer follows the marker; silent deviation is a review blocker
- Traced AC tests embed literal `AC-N` in the test name for grep-based fulfillment
- Prefer real integration at the layer the task specifies; mock only forced edges
