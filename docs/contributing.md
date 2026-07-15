# Rozwój AbsolutPowers

Jak modyfikować skille, agentów i strukturę pluginu.

## Struktura repozytorium

Od wersji 5.0.0 repo trzyma **jedno** host-agnostyczne drzewo skilli — bez luster
`claude/`/`codex/`, bez skryptów sync, bez detekcji driftu (nie ma czego porównywać):

```
absolut-ai-skills/
├── skills/                          # jedno źródło prawdy dla każdego harnessu
│   ├── {skill-name}/
│   │   └── SKILL.md                 # definicja skilla (frontmatter + prompt), host-agnostyczna
│   └── vendored/                    # skille zvendorowane z obra/superpowers (MIT) — patrz VENDORED.md
│
├── agents/                          # prompty ról; Claude rejestruje je jako typy agentów,
│   └── {agent-name}.md              # pozostałe harnessy przekazują ciało generycznym agentom
├── references/                      # mapowania per-harness + shared contracts
│   ├── codex-tools.md
│   ├── pi-tools.md
│   ├── grok-tools.md
│   ├── harness-dispatch.md          # jak odpalać gate/workery na Claude/Codex/Pi/Grok
│   ├── project-memory.md            # wspólny kontrakt project-memory
│   ├── tdd-anti-patterns.md
│   └── fork-policy.md               # kanoniczne ścieżki vs vendored
│
├── hooks/                           # slim hook Claude (SessionStart)
│   ├── hooks.json
│   ├── run-hook.cmd
│   ├── session-start
│   └── session-context.md           # wspólna treść bootstrap — czyta ją też integracja Pi
│
├── .grok-plugin/plugin.json         # Grok manifest (first-class harness)
│
├── .pi/extensions/absolutpowers.ts  # integracja Pi (rejestruje skills/, wstrzykuje session-context.md)
│
├── .claude-plugin/plugin.json       # manifest Claude (root)
├── .claude-plugin/marketplace.json  # marketplace Claude → source: "."
├── .codex-plugin/plugin.json        # manifest Codex (root)
├── .agents/plugins/marketplace.json # marketplace Codex → source.path: "."
├── AGENTS.md                        # symlink → CLAUDE.md (bootstrap dla Codex)
│
├── VENDORED.md                      # log vendoringu: źródła, przypięty SHA, lokalne modyfikacje
├── LICENSE-VENDORED                 # pełny tekst licencji MIT dla treści zvendorowanej
│
├── docs/                            # dokumentacja
└── README.md
```

Dodanie kolejnego harnessu to nowa integracja + opcjonalny `references/{harness}-tools.md` —
**zero edycji skilli**. Zobacz `CLAUDE.md` → "Adding a New Harness" po szczegółowy przepis.

## Anatomia skilla

```markdown
---
name: skill-name
description: >
  Opis skilla — kiedy się triggeruje, co robi.
  TRIGGER when: lista fraz wyzwalających.
allowed-tools: Read, Glob, Grep, Agent, ...   # Claude only — inertne/ignorowane na Codex/Pi
argument-hint: "[opis argumentu]"             # Claude only — inertne/ignorowane na Codex/Pi
---

# Nagłówek

Prompt skilla — instrukcje dla AI agenta.
```

Jeden plik `SKILL.md` obsługuje wszystkie harnessy. Treść body musi być host-agnostyczna —
frontmatter Claude-only i sekcje wywołujące zarejestrowane agenty są tolerowane i inertne na
Codex/Pi (traktowane jako zwykła proza), więc nie wymagają osobnej kopii pliku.

### Frontmatter

| Pole | Wymagane | Opis |
|------|---------|------|
| `name` | Tak | Nazwa skilla (kebab-case) |
| `description` | Tak | Opis + triggery. Używany do auto-detection kiedy skill ma się uruchomić |
| `allowed-tools` | Claude only | Lista narzędzi które skill może używać |
| `argument-hint` | Claude only | Podpowiedź dla użytkownika co podać jako argument |

### Prompt

Reszta pliku po frontmatter to prompt — instrukcje w Markdown. Zmienne:
- `$ARGUMENTS` — argument podany przez użytkownika przy wywołaniu

### Różnice per harness — `references/{harness}-tools.md`

Kiedy konkretny harness potrzebuje innego mapowania akcji na prymitywy (np. dispatch subagenta,
degradacja review gate'a, task tracking) — ta różnica idzie do `references/{harness}-tools.md`,
czytanego warunkowo przez skill/integrację danego harnessu. Nigdy nie forkuj treści `SKILL.md` per
harness. Przykład: `references/pi-tools.md` opisuje mapowanie akcji na prymitywy Pi i dwustopniową
degradację zarejestrowanych bramek review.

## Anatomia agenta (Claude Code only)

```markdown
---
name: agent-name
description: >
  Opis co agent robi.
model: sonnet
tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Nagłówek

Prompt agenta.
```

### Frontmatter agentów

| Pole | Wymagane | Opis |
|------|---------|------|
| `name` | Tak | Nazwa agenta |
| `description` | Tak | Opis |
| `model` | Nie | Model (opus/sonnet/haiku). Domyślnie dziedziczony |
| `tools` | Nie | Lista dostępnych narzędzi |
| `maxTurns` | Nie | Limit iteracji agenta |
| `isolation` | Nie | Tylko `"worktree"` — izolowany git worktree |

**Ograniczenia agentów w pluginach:** `hooks`, `mcpServers`, `permissionMode` nie są obsługiwane.

Agenty (`agents/*.md`) to **zarejestrowane typy** — mechanizm dostępny wyłącznie w pluginach
Claude Code. Codex i Pi nie mają odpowiednika tej rejestracji (patrz `CLAUDE.md` → "Review Gates
(Claude only)" po precyzyjne rozróżnienie: brak rejestru ≠ brak dispatchu subagentów — Codex ma
`multi_agent=true`/`spawn_agent`, Pi ma opcjonalny `pi-subagents`).

### Jak skill uruchamia agenta

W SKILL.md dodaj `Agent` do `allowed-tools`, potem w promptcie:

```markdown
Uruchom subagenta:

\```
Agent(subagent_type="review-plan", prompt="Review planning document: ./absolutpowers/feature/planning-{slug}.md")
\```
```

AI agent przeczyta tę instrukcję i użyje narzędzia Agent z odpowiednimi parametrami. Na Codex/Pi
ta sama sekcja jest inertna (zwykła proza) — patrz `references/pi-tools.md` po wzorzec degradacji.

## Checklist nowego / zmienianego skilla

Przed PR-em na skill (lub agent/command, który zmienia kontrakt pipeline):

1. **`description`** — TRIGGER when + **NIE wyzwalaj na** (kolizje z sąsiednimi skillami).
2. **Hard boundary** — jeśli skill jest audit-only / design-only / no-push: jawna sekcja.
3. **`## Terminal state`** — co oddaje + następny krok / close (dla skilli pipeline i fan-out).
4. **`vs X` / disambiguation** — gdy overlap z innym skillem jest realny.
5. **Brak martwych ścieżek** — zero odniesień do usuniętych mirrorów `claude/`/`codex/`, usuniętych skilli (`harvest`, …).
6. **Single-tree** — nie dodawaj luster per harness; różnice → `references/{harness}-tools.md`.
7. **Długie szablony** — jeśli SKILL.md rośnie >~400–500 linii, wyciągnij formaty do `skills/{name}/references/` i zostaw pointer + reguły w SKILL.md.
8. **Shared contracts** — project-memory → `references/project-memory.md`; gate dispatch → `references/harness-dispatch.md`; dual copies → `references/fork-policy.md`.
9. **Wersja** — bump SemVer we **wszystkich** manifestach (`.claude-plugin`, `.codex-plugin`, `.grok-plugin`) + wpis w README changelog.
10. **Docs** — README tabela skilli / `hooks/session-context.md` skill map przy nowym skilu user-facing.

## Dodawanie nowego skilla

1. Utwórz `skills/{skill-name}/SKILL.md`
2. Zdefiniuj frontmatter z `name`, `description`, opcjonalnie `allowed-tools`/`argument-hint`
   (Claude-only pola — zostaw jeśli skill ich używa, będą inertne na innych harnessach)
3. Napisz prompt — host-agnostyczny; jeśli fragment dotyczy tylko jednego harnessu, rozważ
   przeniesienie go do `references/{harness}-tools.md` zamiast wplatania warunków w body
4. Jeden plik obsługuje Claude Code, Codex i Pi — nie ma potrzeby tworzyć kopii per platforma

## Dodawanie nowego agenta

1. Utwórz `agents/{agent-name}.md` (top-level, Claude-only)
2. Zdefiniuj frontmatter
3. Napisz prompt
4. W SKILL.md odpowiedniego skilla: dodaj `Agent` do `allowed-tools` i instrukcję spawnu

### Agenci orchestrated implementation

`implement` może używać dwóch dodatkowych agentów Claude-only:

| Agent | Rola |
|-------|------|
| `implementation-worker` | Implementuje dokładnie jeden phase file z `tasks-{slug}/NN-{phase}.md` |
| `phase-review` | Lekko sprawdza zakończoną fazę przed oznaczeniem jej jako completed w parent tasks file |

Uwaga: `qa-enrichment` nie jest agentem orchestrated implementation — jest agentem wzbogacającym spawned przez `feature-discuss` po zapisie planning doc. Patrz sekcja "Dodawanie nowego agenta".

### Agenci feature-discuss

| Agent | Rola |
|-------|------|
| `qa-enrichment` | Dopisuje Acceptance Criteria do planning doc po zapisie przez feature-discuss |
| `review-plan` | Weryfikuje planning doc — gate zwracający PASS lub REJECTED |

Kontrakt ownership:
- `implementation-worker` aktualizuje tylko swój phase file i `implementation-context.md`
- główny `implement` orchestrator aktualizuje status fazy w parent `tasks-{slug}.md`
- `phase-review` jest read-only i zwraca tylko `VERDICT: PASS` albo `VERDICT: REJECTED`
- pełny `review-implementation` zostaje końcowym gate'em po wszystkich fazach

Codex i Pi nie mają rejestru zarejestrowanych typów agentów, więc `implement` wykonuje phase
files sekwencyjnie w tej samej sesji na obu (Pi może opcjonalnie dispatchować przez
`pi-subagents`, jeśli zainstalowany — patrz `references/pi-tools.md`).

## Modyfikacja istniejącego skilla

1. Edytuj `skills/{skill-name}/SKILL.md` — jedna edycja serwuje wszystkie harnessy
2. Jeśli zmiana dotyczy zachowania specyficznego dla jednego harnessu — rozważ, czy powinna
   trafić do `references/{harness}-tools.md` zamiast rozgałęziać body skilla
3. Jeśli zmiana jest Claude-only (np. nowa sekcja agent gate) — dodaj ją jako sekcję tolerowaną
   przez pozostałe harnessy (proza inertna), nie jako osobny plik

### Zmiany w formacie tasków

`generate-tasks` obsługuje dwa tryby:
- `single-file` — jeden `tasks-{slug}.md` dla małych zmian
- `orchestrated` — parent `tasks-{slug}.md`, katalog `tasks-{slug}/`, phase files, `implementation-context.md`, `99-final-verification.md`

Przy zmianach w tym formacie aktualizuj razem:
- `skills/generate-tasks/SKILL.md`
- `skills/implement/SKILL.md`
- `agents/review-tasks.md`
- `agents/review-implementation.md`
- `agents/qa-enrichment.md` (jeśli zmiana dotyczy AC w tasks, np. format pola `Traces to:`)
- dokumentację w `README.md` i `docs/`

### PreBoot skill

PreBoot jest obsługiwany przez jeden skill na całe repo:
- `skills/preboot/SKILL.md`

Nie dodawaj z powrotem osobnych skilli `preboot-core`, `preboot-query`, `preboot-saga` itd. `preboot` ma tylko wykrywać moduł i routować agenta do lokalnej dokumentacji projektu w `./preboot-docs/`.

Zasady:
- plugin nie dostarcza bundlowanej dokumentacji API PreBoot
- plugin nie tworzy `preboot-docs/`
- jeśli lokalny plik dokumentacji modułu nie istnieje, skill ma zatrzymać pracę i poprosić o dokumentację
- generic keywords typu `task`, `file`, `event`, `sequence`, `document` nie powinny aktywować PreBoot bez jawnego dependency/import/API signal

## Wersjonowanie

Wersja w manifestach platform — wszystkie deklarowane wersje muszą być zgodne:

```
.claude-plugin/plugin.json    → "version"
.codex-plugin/plugin.json     → "version"
.grok-plugin/plugin.json      → "version"
```

Konwencja SemVer:
- **Major** (X.0.0) — zmiana struktury, breaking changes (np. kolaps do jednego drzewa w 5.0.0)
- **Minor** (0.X.0) — nowy skill, nowy agent, nowy feature, nowy harness
- **Patch** (0.0.X) — poprawki promptów, bugfixy

## Testowanie zmian

### Lokalne testowanie Claude Code

1. Edytuj SKILL.md
2. Zrestartuj Claude Code (`/plugin install absolutpowers@absolutpowers-skills`)
3. Wywołaj skill w projekcie testowym
4. Sprawdź czy output jest poprawny

### Lokalne testowanie Codex

1. Edytuj SKILL.md w `skills/`
2. Otwórz projekt testowy w Codex
3. Zainstaluj plugin z repo marketplace (`.agents/plugins/marketplace.json`)
4. Wywołaj skill

### Lokalne testowanie Pi

1. Edytuj SKILL.md w `skills/` (lub `.pi/extensions/absolutpowers.ts` / `references/pi-tools.md`)
2. Uruchom Pi z tym checkoutem jako tymczasowym pakietem: `pi -e /path/to/absolut-ai-skills`
3. Sprawdź czy bootstrap (`hooks/session-context.md`) wstrzykuje się przy starcie sesji i po compaction
4. Wywołaj skill

### Testowanie review gate'ów

1. Uruchom pełny pipeline: feature-discuss → generate-tasks → implement
2. Sprawdź czy gate'y się uruchamiają
3. Celowo wprowadź problem w output — sprawdź czy gate go łapie
4. Sprawdź czy iteracja (fix → re-review) działa

### Testowanie orchestrated implementation

1. Wygeneruj większy planning doc, który powinien uruchomić tryb `orchestrated`
2. Sprawdź czy `generate-tasks` tworzy parent tasks file, phase files, `implementation-context.md` i `99-final-verification.md`
3. Uruchom `implement` w Claude Code
4. Sprawdź czy `implementation-worker` działa tylko na jednej fazie
5. Sprawdź czy `phase-review` blokuje przejście dalej przy scope/test/handoff problemach
6. Sprawdź czy finalny `review-implementation` czyta wszystkie phase files

## Walidacja strukturalna (bez systemu budowania)

```bash
# Manifesty to poprawny JSON
for f in $(git ls-files '*.json'); do python3 -m json.tool "$f" >/dev/null || echo "BAD: $f"; done

# Hook emituje poprawny JSON
CLAUDE_PLUGIN_ROOT=. bash hooks/session-start | python3 -m json.tool >/dev/null

# Każdy SKILL.md ma frontmatter
for f in $(git ls-files 'skills/**/SKILL.md'); do head -1 "$f" | grep -q '^---$' || echo "NO FM: $f"; done
```

## Vendoring z obra/superpowers

`skills/vendored/` trzyma skille skopiowane, przycięte i dostosowane z
[obra/superpowers](https://github.com/obra/superpowers) na licencji MIT. Zasady:

- Pełna proweniencja (źródłowa ścieżka, przypięty SHA, lokalne modyfikacje) w `VENDORED.md`
- Pełny tekst licencji w `LICENSE-VENDORED`
- Każdy zvendorowany plik ma jednolinijkową notę MIT/source zaraz po frontmatter
- Śledzenie upstreamu jest kwartalne i selektywne (patrz proces w `VENDORED.md`) — nie
  auto-sync, nie parytet wersji z obrą
- `vendor/superpowers/` (klon roboczy poza repo pluginu, gitignorowany) to jedyne źródło do
  kopiowania — nie kopiuj z GitHub bez przypiętego SHA

Nie dodawaj nowych zvendorowanych skilli bez aktualizacji `VENDORED.md`.
