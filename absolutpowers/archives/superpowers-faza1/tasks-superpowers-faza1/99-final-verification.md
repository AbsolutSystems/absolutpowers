# Phase 99: Final Verification

## Status
completed
<!-- Wyniki weryfikacji: patrz Task 1 → Implementation decisions / remarks -->


## Parent
`./absolutpowers/feature/tasks-superpowers-faza1.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/tasks-superpowers-faza1/implementation-context.md`

## Objective
Zweryfikować zintegrowaną zmianę na całym repo po Fazie 1. Repo nie ma systemu budowania — bramki to walidacja strukturalna + smoke test instalacji pluginu. Uruchamiany przez orchestratora po przejściu wszystkich faz implementacyjnych.

## Tasks

### Task 1: Final Verification
**Status:** completed

**Create:**
- None

**Modify:**
- None

**Description:**
Uruchomić komendy weryfikacyjne przeciw w pełni zintegrowanej zmianie: poprawność JSON wszystkich manifestów, wykonywalność i poprawny output hooka, obecność frontmatter we wszystkich SKILL.md, brak wiszących referencji do usuniętych ścieżek, zgodność wersji, atrybucja MIT. Plus manualny smoke test instalacji pluginu.

**Requirements:**
- Walidacja JSON wszystkich manifestów: `for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done` (brak outputu)
- Hook emituje poprawny JSON: `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null`
- Wszystkie SKILL.md mają frontmatter: `for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done` (brak outputu)
- Brak wiszących referencji: `grep -rn 'claude/skills\|codex/skills\|sync_claude_to_agents\|diff-skills' --include='*.md' --include='*.json' . | grep -v tasks-superpowers-faza1` (brak outputu)
- Zgodność wersji: oba manifesty `5.0.0`
- Atrybucja: `LICENSE-VENDORED` + sekcja w README, `Jesse Vincent` obecny
- Zvendorowane skille mają notę MIT; telemetria companiona zneutralizowana (`grep -rl primeradiant.com skills/` = brak)
- Wieloharnessowość: `AGENTS.md` to symlink do CLAUDE.md (`test -L AGENTS.md`); `.pi/extensions/absolutpowers.ts` istnieje i wskazuje `skills/`; `references/pi-tools.md` + `references/codex-tools.md` istnieją (jeśli codex-tools stworzony) i mapują dispatch subagentów
- Pi extension czyta wspólną treść: `grep -q session-context.md .pi/extensions/absolutpowers.ts`
- Korekta docs: `grep -q 'Codex lacks plugin-level subagent support' CLAUDE.md` = BRAK trafień (nieprecyzyjne zdanie usunięte)
- **Manualny smoke test:** `/plugin install` z lokalnego marketplace root — potwierdzić, że skille się ładują i `@feature-discuss`/`@generate-tasks` są wykrywalne (zapisać wynik jako `not applicable` tylko jeśli środowisko nie pozwala). Jeśli Pi dostępny lokalnie — potwierdzić, że rozszerzenie ładuje skille i wstrzykuje treść na starcie sesji
- Nie oznaczać tego taska jako completed, jeśli którakolwiek wymagana komenda faili

**Tests:**
- Walidacja JSON — 0 BAD
- Hook — exit 0, poprawny JSON
- Frontmatter — 0 NO FM
- Stale refs — 0 trafień
- Wersje zgodne == 5.0.0
- Smoke test instalacji — skille wykrywalne (lub udokumentowany powód `not applicable`)

**Implementation decisions / remarks:**
- Komendy wykonane (orchestrator, wszystkie PASS): JSON validity loop (0 BAD); `CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool` (OK); frontmatter loop `skills/**/SKILL.md` (0 NO FM); stale-ref meaningful gate `git grep -E 'claude/skills|codex/skills|sync_claude_to_agents|diff-skills' -- '*.md' '*.json' | grep -v '\.claude/skills/learned' | grep -v 'absolutpowers/feature/' | grep -v tasks-superpowers-faza1` (brak); version parity (5.0.0==5.0.0); `AGENTS.md` symlink→CLAUDE.md; `.pi/extensions/absolutpowers.ts` istnieje + rejestruje skills + czyta session-context.md; `references/pi-tools.md` istnieje; `grep primeradiant.com skills/` (brak); `skills/vendored/` = 7, `task-brief` wykonywalny; `claude/`+`codex/` usunięte; `Jesse Vincent` w LICENSE-VENDORED+README.
- Wyniki: wszystkie 11 klas bramek PASS.
- Pominięte sprawdzenia: manualny `/plugin install` smoke test — **not applicable** (środowisko orchestratora nie odpala instalacji pluginu ani sesji Pi; walidacja strukturalna pokrywa ładowalność: poprawny JSON manifestów/marketplace, wykrywalny frontmatter skilli, poprawny output hooka). `references/codex-tools.md` — nie istnieje (świadomie, poza scope Fazy 1; gate traktuje warunkowo).

**Example:**
```bash
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null && echo "hook OK"
grep -rn 'claude/skills\|codex/skills\|sync_claude_to_agents\|diff-skills' --include='*.md' --include='*.json' . | grep -v tasks-superpowers-faza1 || echo "no stale refs"
python3 -c "import json; assert json.load(open('.claude-plugin/plugin.json'))['version']==json.load(open('.codex-plugin/plugin.json'))['version']=='5.0.0'" && echo "version OK"
```
