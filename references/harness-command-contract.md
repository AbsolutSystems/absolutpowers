# Native Command Handoff Contract

This is the mandatory output contract for every executable next-step handoff in an
AbsolutPowers skill.

## Required output

When the next step invokes a skill and/or passes a path or arguments:

1. Give the user exactly one standalone, copy-pasteable command line in a fenced `text` block.
2. Keep the skill invocation, every path, and every argument on that line.
3. Use the active harness's native syntax:
   - Claude Code: `/absolutpowers:skill-name [args]`
   - Codex: `$absolutpowers skill-name [args]`
   - Pi: the native Pi skill invocation or the corresponding `SKILL.md` read action
   - Grok Build: `/skill-name [args]` (qualified if the harness requires it)
4. Quote an argument when it contains spaces.
5. Do not put `@` before the skill name or an argument path.

A status sentence may precede the command, but it never replaces the command line.
Never emit only a bare skill name, a prose description such as “run `implement` on
the tasks file”, or a legacy form such as `@implement @path`.

## Examples

For the semantic next step “plan Phase 3 from this epic main”:

```text
/absolutpowers:feature-discuss absolutpowers/feature/example/planning-main.md "Omów Fazę 3: Core consumers"
```

```text
$absolutpowers feature-discuss absolutpowers/feature/example/planning-main.md "Omów Fazę 3: Core consumers"
```

The first line is the Claude Code form; the second is the Codex form. Use the equivalent
native form for Pi or Grok from the active harness reference. These examples are output
shapes, not commands to execute automatically.
