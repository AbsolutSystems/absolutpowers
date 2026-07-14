# Phase 8: Bump 5.0.0 + README/docs/install

## Status
completed

## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Context Contract

### Requires (from previous phases)
- Wszystkie poprzednie fazy completed (struktura root ustabilizowana, incl. Pi z Phase 7).

### Provides (for later phases)
- Oba manifesty na `5.0.0`.
- README/CLAUDE/docs opisujące jednodrzewową architekturę v5 + atrybucję MIT.
- Naprawiona instrukcja instalacji.

## Read Scope
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
- `README.md`, `CLAUDE.md`, `docs/**`
- `VENDORED.md`, `LICENSE-VENDORED`
- `.pi/extensions/absolutpowers.ts`, `references/*-tools.md` (do opisu wieloharnessowości)
- `vendor/superpowers/README.md` (wzorzec sekcji atrybucji/telemetrii + instrukcje instalacji Pi/Codex)

## Write Scope
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `README.md`
- `CLAUDE.md`
- `docs/**`

## Objective
Podbić wersję do 5.0.0 (semver major — zmiana formatu) w obu manifestach zgodnie i przepisać dokumentację pod jednodrzewową architekturę: layout, reguły edycji, instalacja, atrybucja MIT, opis slim hooka i zvendorowanych skilli.

## Tasks

### Task 1: Bump wersji 5.0.0 (oba manifesty zgodnie)
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `.claude-plugin/plugin.json`: `"version": "5.0.0"`
- `.codex-plugin/plugin.json`: `"version": "5.0.0"`
- Potwierdzić zgodność (SemVer musi się zgadzać między manifestami — reguła z CLAUDE.md)

**Tests:**
- Oba manifesty mają `"version": "5.0.0"`
- `python3 -c "import json; a=json.load(open('.claude-plugin/plugin.json'))['version']; b=json.load(open('.codex-plugin/plugin.json'))['version']; assert a==b=='5.0.0'"` przechodzi

### Task 2: Przepisać README + CLAUDE.md pod v5
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- `CLAUDE.md`: zaktualizować Repository Layout (jedno drzewo `skills/` + `skills/vendored/` + top-level `agents/`/`commands/`/`hooks/`/`references/`/`.pi/`), usunąć sekcję dwudrzewową i "Cross-Platform Editing Rules" oparte na mirrorach (zastąpić notą o jednym źródle + `references/{harness}-tools.md` dla różnic per harness), zaktualizować "Key Development Commands" (usunąć diff-skills.sh; dodać walidację JSON/hook/Pi-ext), podbić wersję w opisie
- **KOREKTA faktograficzna w CLAUDE.md:** obecne zdanie "Codex lacks plugin-level subagent support" jest nieprecyzyjne. Zastąpić: Codex/Pi brakuje **zarejestrowanych definicji agentów** (nie da się wysłać `agents/*.md` jako typu subagenta) — ale dispatch subagentów istnieje (Codex: `multi_agent=true` → `spawn_agent`/`wait_agent`/`close_agent`; Pi: opcjonalny `pi-subagents`). Dlatego bramki review (zarejestrowane agenty) są Claude-only, ale wzorzec wykonawczy subagentów jest przenośny. Odesłać do `references/{harness}-tools.md`.
- `README.md`: naprawić instrukcję instalacji (poprzednio zepsutą — okazja do czystej naprawy) dla WSZYSTKICH TRZECH harnessów (Claude Code, Codex, Pi — wzorzec sekcji instalacji z `vendor/superpowers/README.md`), opisać jednodrzewową architekturę wieloharnessową, dodać sekcję atrybucji MIT (obra/superpowers + link `LICENSE-VENDORED`), opisać slim hook i listę zvendorowanych skilli
- Dodać changelog v5.0.0 (breaking: zmiana struktury, vendoring, slim hook, wsparcie Pi)

**Tests:**
- `CLAUDE.md` nie opisuje już dwóch drzew ani skryptów sync
- `CLAUDE.md` nie zawiera nieprecyzyjnego "Codex lacks plugin-level subagent support" (zastąpione korektą o zarejestrowanych agentach vs dispatch)
- `README.md` ma sekcję atrybucji MIT z `Jesse Vincent`/`obra/superpowers`
- `README.md` ma instrukcje instalacji dla Claude Code, Codex ORAZ Pi
- Changelog ma wpis 5.0.0 z wzmianką o wsparciu Pi

### Task 3: Przepis "jak dodać kolejny harness"
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Dodać do `CLAUDE.md` (lub `docs/`) sekcję "Dodanie nowego harnessu" opisującą rozszerzalny wzorzec: (1) cienki manifest/integracja per harness (jak `.codex-plugin/`, `.pi/extensions/`); (2) opcjonalny `references/{harness}-tools.md` mapujący akcje skilli na prymitywy harnessu; (3) ZERO edycji skilli — body są host-agnostyczne; (4) bramki/hook to Claude-only, na innych harnessach degradują gracefully
- Podać Pi i Codex jako zrealizowane przykłady tego wzorca

**Tests:**
- Sekcja "jak dodać harness" istnieje i wymienia 3 kroki wzorca
- Odwołuje się do Pi/Codex jako przykładów

### Task 4: Zaktualizować docs/
**Status:** completed
**Traces to:** none (infrastructure task)

**Requirements:**
- Przejrzeć `docs/**` pod kątem odniesień do dwudrzewowej struktury / diff-skills / sync — zaktualizować do v5
- Jeśli docs opisują pipeline — dodać wzmiankę o slim hooku i skillach strażniczych (bez rozpisywania fuzji — to Faza 2/3)

**Tests:**
- `grep -rn 'claude/skills\|codex/skills\|diff-skills\|sync_claude_to_agents' docs/` = brak trafień
- docs spójne z v5 (jedno drzewo)

## Phase Verification
Run:
- `python3 -c "import json; assert json.load(open('.claude-plugin/plugin.json'))['version']==json.load(open('.codex-plugin/plugin.json'))['version']=='5.0.0'" && echo "version OK"`
- `grep -rn 'Jesse Vincent' README.md LICENSE-VENDORED && echo "attribution OK"`
- `grep -rn 'claude/skills\|codex/skills\|diff-skills\|sync_claude_to_agents' --include='*.md' . | grep -v tasks-superpowers-faza1 || echo "docs clean"`

## Completion Criteria
- All phase tasks are completed.
- Oba manifesty na 5.0.0, zgodne.
- Dokumentacja opisuje v5, atrybucja MIT obecna, instalacja naprawiona.
- Phase verification commands pass.
- `implementation-context.md` zaktualizowany.
- All items listed in `## Context Contract -> Provides` are fulfilled.

## Implementation Decisions / Remarks
- **Version bump:** both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` → `5.0.0`. Only the `version` field touched — descriptions/keywords left as-is (out of Task 1 scope, no test required it).
- **CLAUDE.md was already partially updated in Phase 6** (Repository Layout, Key Development Commands, Cross-Harness Editing Rules, Versioning). This phase finished the job: swept remaining "both trees"/"Both trees" residue (harvest, constitution, analyze sections), bumped the version line + added the vendoring/Pi mention to "What This Is", rewrote the "Review Gates (Claude only)" section with the precise Codex/Pi correction, softened the `triada-review` "Codex has no equivalent" line with the same nuance, added JSON/hook/frontmatter/Pi-typecheck commands to Key Development Commands, and added a new `## Adding a New Harness` section (4 numbered steps, cites Codex + Pi as realized examples).
- **The literal old phrase "Codex lacks plugin-level subagent support" was not found verbatim** in CLAUDE.md at phase start (Phase 6 had already softened it to "Codex runs without gates"). Applied the requested precise correction anyway to every place carrying the same imprecision: `CLAUDE.md` (Review Gates section + Triada Review section), `README.md` ("How gates work" section + new Changelog entry + Platform Differences table), `docs/review-gates.md` ("Dostępność" table), `docs/getting-started.md` (Codex verification paragraph + orchestrated-implementation paragraph).
- **`references/codex-tools.md` does not exist** (confirmed — no prior phase created it, and it is outside this phase's Write Scope which excludes `references/`). Docs reference it only as "can be added following the pattern" / "not needed so far, gates simply don't run" — never claimed to exist.
- **README.md rewrite covers:** intro (3 harnesses), a 3-part Install section (Claude Code / Codex / Pi, following the `vendor/superpowers/README.md` per-harness pattern), Skills Reference table column renamed `Trees`→`Harnesses` and values `both`→`all` (16 rows, scripted with a small Python pass, verified count matches), "How gates work" Codex/Pi correction, Platform Differences table expanded to 3 columns with the precise dispatch-vs-registry distinction, Repo Structure section fully rewritten for the single tree (was still showing the old `claude/`/`codex/` mirror layout), Updating section gains a Pi line, a new `## Vendored Skills & Hook` section, a new `### Attribution` section with `Jesse Vincent`/`obra/superpowers`/`LICENSE-VENDORED`, and a new `### 5.0.0` Changelog entry.
- **Verification-grep discipline (important for any future phase touching these files):** the naive stale-path grep matches two more classes than documented in Phase 6/7 notes — (a) legit `.claude/skills/learned/` target-project paths (expected, must stay) and (b) **new-in-this-phase risk**: writing *historical/changelog prose* that describes the removal of `claude/`, `codex/`, `scripts/diff-skills.sh`, `scripts/sync_claude_to_agents.py` inevitably tends to reuse those literal substrings. Fixed two such self-inflicted hits during this phase (the new 5.0.0 changelog entry, and a pre-existing 3.10.0 changelog line that literally contained `claude/skills/tasks-to-issues/`) by describing removals in prose without the literal path substrings. **Rule for later phases:** when writing changelog/history prose about removed two-tree paths, never spell `claude/skills`, `codex/skills`, `diff-skills`, or `sync_claude_to_agents` literally — paraphrase instead. Confirmed clean via `git grep -n -E 'claude/skills|codex/skills|diff-skills|sync_claude_to_agents' -- '*.md' | grep -v '\.claude/skills/learned' | grep -v 'absolutpowers/feature/' | grep -v tasks-superpowers-faza1` → no output.
- **docs/contributing.md rewritten in full** (Write tool, not incremental Edit — nearly every section referenced the two-tree layout): repo structure, skill/agent anatomy, adding a skill/agent, task-format-change checklist, PreBoot note, versioning, testing (added a "Lokalne testowanie Pi" subsection), a new "Walidacja strukturalna" command block, and a new "Vendoring z obra/superpowers" section.
- **docs/getting-started.md and docs/review-gates.md got targeted edits, not full rewrites:** added Pi install/verification paragraphs, replaced the Codex-orchestrated-implementation line and the Codex-verification line with the precise dispatch-vs-registry wording, expanded the review-gates.md "Dostępność" table to 3 rows (Claude/Codex/Pi) with the same correction.
- **Not touched (deliberately, historical record):** the pre-5.0.0 changelog entries (3.0.0 through 3.13.0) in README.md still say "both trees" in their own historical context — these describe what was true *at that version*, not the current architecture, and rewriting them would falsify the historical record. Only the new-content additions in this phase (and the two hits noted above) were held to the "no `claude/skills`/`diff-skills`/etc. substring" bar.
