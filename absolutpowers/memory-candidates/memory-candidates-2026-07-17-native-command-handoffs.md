# Memory Candidate — Native command handoffs

## Candidate lesson

Shared skill prose must distinguish a bare skill name used in narrative from an executable next-step command. A phrase such as “uruchom `implement` w składni aktywnego harnessu” is not a reliable command contract: without a literal per-harness shape, the model may omit the dispatcher prefix, paraphrase the handoff, or revive a legacy prefix from another context source.

## Warning signs

- A handoff says “active harness syntax” but shows no complete command example.
- Canonical instructions forbid `@skill`, while ADRs, fork-policy files, tests, or task artifacts still contain `@skill`.
- The skill name and the artifact path are presented as separate prose fragments instead of one copy-paste line.

## Evidence from this incident

- `skills/feature-discuss/SKILL.md:442-444` and `skills/implement/SKILL.md:446-455` use bare/prose handoffs.
- `references/fork-policy.md:14-15` and `docs/adr/2026-07-16-lightweight-task-routing.md:42-44` retain legacy forms.
- User-observed Codex output omitted `$absolutpowers`; Claude output used prose and later `@implement @path`.

## Promotion

Promote to `absolutpowers/project-memory.md` only after user approval. This candidate is a reusable prompt/integration trap, not a fix for one feature.
