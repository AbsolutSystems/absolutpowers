# Phase 6: Rozszerzenie `allowed-tools` (frontmatter — permission surface)

## Status
completed

## Parent
`./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss.md`

## Shared Context
Read before starting:
- `./absolutpowers/feature/superpowers-faza2-fuzje/tasks-phase-1-feature-discuss/implementation-context.md`
- Planning: krok 5a + krok 7, AC-12
- Edge case planningu: zbyt szeroki wzorzec (np. `Bash(*)`) rozluźnia skill w trybie dyskusji — granty maksymalnie wąskie

## Context Contract

### Requires (from previous phases)
- Sekcja `## Visual Companion` obecna (Phase 5) — grant narzędzi ma sens dopiero gdy companion jest odwoływany; frontmatter domyka jego działanie.

### Provides (for later phases)
- Rozszerzony `allowed-tools` w frontmatter `skills/feature-discuss/SKILL.md`: dodane WYŁĄCZNIE (a) grant Bash na wykonanie `companion-scripts/start-server.sh` i `stop-server.sh`; (b) grant Write na `**/.superpowers/brainstorm/**/*.html`.
- `name`, `description`, `argument-hint` oraz wszystkie istniejące granty (`Read`, `Glob`, `Grep`, `Bash(find/wc/cat/head/tail/tree/mkdir)`, `Write(**/absolutpowers/feature/**/*.md)`, `Write(**/docs/adr/*.md)`, `Agent`) — NIEtknięte.

## Read Scope
- `skills/feature-discuss/SKILL.md` (frontmatter L1-16)
- `skills/feature-discuss/companion-scripts/start-server.sh`, `stop-server.sh` (potwierdź nazwy skryptów do grantu)

## Write Scope
- `skills/feature-discuss/SKILL.md` (wyłącznie frontmatter — pole `allowed-tools`)

## Objective
Companion działa tylko przy poszerzonym grancie narzędzi; obecny allowlist go nie pokrywa (Bash tylko `find/wc/cat/head/tail/tree/mkdir`; Write tylko `absolutpowers/feature/**` + `docs/adr/**`). Rozszerz `allowed-tools` **wąsko i celowo** o dokładnie dwa granty companion, nie luzując pozostałych. To jedyna dozwolona zmiana znacząca w frontmatter.

## Tasks

### Task 1: Wąskie rozszerzenie `allowed-tools` o granty companion
**Status:** completed
**Traces to:** AC-12

**Requirements:**
- Dodaj do `allowed-tools`:
  - Bash-exec na skrypty companion: grant wykonania `skills/feature-discuss/companion-scripts/start-server.sh` i `stop-server.sh` (użyj wzorca zgodnego z konwencją istniejących wpisów `Bash(...)`, wskazującego dokładne skrypty — np. `Bash(*/companion-scripts/start-server.sh:*)`, `Bash(*/companion-scripts/stop-server.sh:*)`; dobierz wzorzec tak, by celował w te skrypty, nie w dowolny Bash).
  - Write na katalog ekranów companion: `Write(**/.superpowers/brainstorm/**/*.html)`.
- NIE dodawaj `Bash(*)` ani szerokich wzorców. Granty maksymalnie wąskie (dokładne skrypty + katalog ekranów).
- NIE ruszaj: `name`, `description`, `argument-hint`, ani żadnego istniejącego grantu (`Read`, `Glob`, `Grep`, dotychczasowe `Bash(...)`, dotychczasowe `Write(...)`, `Agent`).
- `Read` jest bez restrykcji → `server-info`/`events` działają bez dodatkowego grantu (nie dodawaj).

**Tests (grep-verifiable):**
- Frontmatter YAML nadal parsuje: `python3 -c "import yaml; d=yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); print(d['allowed-tools'])"`.
- Grant Write companion: `grep -n "superpowers/brainstorm" skills/feature-discuss/SKILL.md` → obecny w linii `allowed-tools`.
- Grant Bash companion: `grep -niE "companion-scripts/(start|stop)-server" skills/feature-discuss/SKILL.md` → obecny w `allowed-tools`.
- Istniejące granty nietknięte: `grep -nE "Bash\(find:|Write\(\*\*/absolutpowers/feature|Write\(\*\*/docs/adr|argument-hint:" skills/feature-discuss/SKILL.md` → wszystkie obecne.

## Phase Verification
Run:
- `python3 -c "import yaml; d=yaml.safe_load(open('skills/feature-discuss/SKILL.md').read().split('---')[1]); assert d['name']=='feature-discuss'; assert 'brainstorm' in d['allowed-tools']; print('FM OK', d['name'])"`
- `git diff skills/feature-discuss/SKILL.md | grep -E '^[+-]' | grep -iE 'name:|description:|argument-hint:'` → oczekiwane: brak zmian (żaden `+`/`-` na tych polach; jeśli coś wyjdzie — regresja).
- Potwierdź brak `Bash(*)` / szerokiego wildcarda: `grep -nE "Bash\(\*\)|Bash\(:" skills/feature-discuss/SKILL.md` → brak trafień.

## Completion Criteria
- Task fazy `completed`.
- Zmiana wyłącznie w polu `allowed-tools`; reszta frontmatter bit-identyczna.
- Phase verification przechodzi; brak szerokich wzorców.
- `implementation-context.md` zaktualizowany (finalna postać `allowed-tools`).
- Context Contract → Provides spełnione.

## Implementation Decisions / Remarks
- Jedyna zmiana: pole `allowed-tools` w frontmatter (L14). Reszta frontmatter (`name`, `description`, `argument-hint`, ciało pliku) bit-identyczna — potwierdzone `git diff | grep name:/description:/argument-hint:` = pusty.
- Dodane WYŁĄCZNIE 3 granty companion, wąsko:
  - `Bash(companion-scripts/start-server.sh:*)` — literalny prefiks, zakotwiczony w poz. 0 (bez wildcarda poza końcowym `:*`), zgodny z konwencją Bash-grantów (`Bash(find:*)` itd., które są prefiksowe). Prefiks jest DOKŁADNIE tekstem polecenia dokumentowanym w `visual-companion.md` (L40/67/76: `companion-scripts/start-server.sh --project-dir ...`) — potwierdzone `grep -oE "^companion-scripts/start-server.sh" visual-companion.md`.
  - `Bash(companion-scripts/stop-server.sh:*)` — jw. (dopasowany do `companion-scripts/stop-server.sh $SESSION_DIR`, L285).
  - `Write(**/.superpowers/brainstorm/**/*.html)` — katalog ekranów companion (grant Write jest glob-owy, `**/` dozwolone — spójnie z istniejącymi `Write(**/absolutpowers/feature/**/*.md)`).
- Korekta po phase-review (odrzucenie #1): pierwotny `Bash(*/companion-scripts/...:*)` używał wiodącego wildcarda. Granty Bash w Claude Code są PREFIKSOWE (nie glob) — wiodące `*/` byłoby dopasowane literalnie i nigdy nie zmatchowałoby realnego polecenia. Zamieniono na literalny prefiks równy dokumentowanemu tekstowi polecenia. (Sugestia reviewera `skills/feature-discuss/...` odrzucona — plugin instalowany jest w cache o nieznanym ścieżkowo prefiksie absolutnym; zakotwiczenie na dokumentowanym poleceniu relatywnym jest jedynym stabilnym, in-scope rozwiązaniem. Rozbieżność runtime→docs, jeśli istnieje, to problem docs poza scope tej fazy frontmatterowej; najgorszy przypadek = jednorazowy prompt permission, bezpieczny fallback.)
- Umiejscowienie: dwa granty Bash wstawione po ostatnim istniejącym `Bash(mkdir:*)` (grupują się z pozostałymi Bash); grant Write wstawiony po istniejących `Write(...)`, przed `Agent`.
- NIE dodano `Bash(*)` ani żadnego szerokiego wildcarda — potwierdzone `grep -nE "Bash\(\*\)|Bash\(:"` = brak trafień.
- `Read` bez restrykcji, więc `server-info`/`events` companion działają bez dodatkowego grantu — nie dodawano.
- Nazwy skryptów potwierdzone w `skills/feature-discuss/companion-scripts/`: `start-server.sh`, `stop-server.sh` (obecne).
- Finalna wartość `allowed-tools`: `Read, Glob, Grep, Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(tree:*), Bash(mkdir:*), Bash(companion-scripts/start-server.sh:*), Bash(companion-scripts/stop-server.sh:*), Write(**/absolutpowers/feature/**/*.md), Write(**/docs/adr/*.md), Write(**/.superpowers/brainstorm/**/*.html), Agent`.
- Weryfikacja funkcjonalności grantu (reviewer issue #2): prefiks grantu Bash = literalny początek polecenia dokumentowanego w `visual-companion.md`. Potwierdzone: `grep -oE "Bash\(companion-scripts/(start|stop)-server.sh:\*\)" SKILL.md` = 2 trafienia; `grep -oE "^companion-scripts/(start|stop)-server.sh" visual-companion.md` = te same 2 prefiksy. Brak wiodącego wildcarda: `grep -nE "Bash\(\*" SKILL.md` = puste.
</content>
