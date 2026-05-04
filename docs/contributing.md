# Rozwój AbsolutPowers

Jak modyfikować skille, agentów i strukturę pluginu.

## Struktura repozytorium

```
absolut-ai-skills/
├── claude/                          # Claude Code plugin
│   ├── .claude-plugin/plugin.json   # Plugin manifest (wersja, opis)
│   ├── skills/                      # Skille — po jednym katalogu na skill
│   │   └── {skill-name}/
│   │       └── SKILL.md             # Definicja skilla (frontmatter + prompt)
│   └── agents/                      # Subagenty — po jednym pliku na agenta
│       └── {agent-name}.md          # Definicja agenta (frontmatter + prompt)
│
├── codex/                           # Codex plugin
│   ├── .codex-plugin/plugin.json    # Plugin manifest
│   ├── skills/                      # Skille (bez agent gates, bez Claude frontmatter)
│   └── scripts/
│       └── sync_claude_to_agents.py # CLAUDE.md → AGENTS.md sync helper
│
├── .claude-plugin/marketplace.json  # Claude marketplace (wskazuje na claude/)
├── .agents/plugins/marketplace.json # Codex marketplace (wskazuje na codex/)
│
├── scripts/
│   ├── diff-skills.sh               # Porównanie skilli Claude vs Codex
│   └── sync_claude_to_agents.py     # CLAUDE.md → AGENTS.md sync w projektach
│
├── docs/                            # Dokumentacja
└── README.md
```

## Anatomia skilla (Claude Code)

```markdown
---
name: skill-name
description: >
  Opis skilla — kiedy się triggeruje, co robi.
  TRIGGER when: lista fraz wyzwalających.
allowed-tools: Read, Glob, Grep, Agent, ...
argument-hint: "[opis argumentu]"
---

# Nagłówek

Prompt skilla — instrukcje dla AI agenta.
```

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

## Anatomia agenta (Claude Code)

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

### Jak skill uruchamia agenta

W SKILL.md dodaj `Agent` do `allowed-tools`, potem w promptcie:

```markdown
Uruchom subagenta:

\```
Agent(subagent_type="review-plan", prompt="Review planning document: ./absolutpowers/feature/planning-{slug}.md")
\```
```

AI agent przeczyta tę instrukcję i użyje narzędzia Agent z odpowiednimi parametrami.

## Anatomia skilla (Codex)

Identyczny format jak Claude, ale **bez** pól `allowed-tools` i `argument-hint` w frontmatter. Bez referencji do agentów w promptcie.

## Dodawanie nowego skilla

### Claude Code

1. Utwórz `claude/skills/{skill-name}/SKILL.md`
2. Zdefiniuj frontmatter z `name`, `description`, `allowed-tools`, `argument-hint`
3. Napisz prompt

### Codex

1. Utwórz `codex/skills/{skill-name}/SKILL.md`
2. Zdefiniuj frontmatter z `name`, `description` (bez `allowed-tools`, `argument-hint`)
3. Napisz prompt (bez referencji do agentów)

### Na obu platformach

Utwórz skill w obu katalogach. Użyj drift detection żeby sprawdzić różnice:

```bash
./scripts/diff-skills.sh --diff
```

## Dodawanie nowego agenta

1. Utwórz `claude/agents/{agent-name}.md`
2. Zdefiniuj frontmatter
3. Napisz prompt
4. W SKILL.md odpowiedniego skilla: dodaj `Agent` do `allowed-tools` i instrukcję spawnu

## Modyfikacja istniejącego skilla

1. Edytuj SKILL.md w `claude/skills/` lub `codex/skills/` (albo w obu)
2. Sprawdź drift: `./scripts/diff-skills.sh --diff`
3. Jeśli zmiana dotyczy obu platform — ręcznie zsynchronizuj
4. Jeśli zmiana jest Claude-only (np. agent gate) — edytuj tylko `claude/`

## Wersjonowanie

Wersja w trzech miejscach — wszystkie muszą być zgodne:

```
claude/.claude-plugin/plugin.json     → "version"
codex/.codex-plugin/plugin.json       → "version"
.claude-plugin/marketplace.json       → "version"
```

Konwencja SemVer:
- **Major** (X.0.0) — zmiana struktury, breaking changes
- **Minor** (0.X.0) — nowy skill, nowy agent, nowy feature
- **Patch** (0.0.X) — poprawki promptów, bugfixy

## Testowanie zmian

### Lokalne testowanie Claude Code

1. Edytuj SKILL.md
2. Zrestartuj Claude Code (`/plugin install absolutpowers@absolutpowers-skills`)
3. Wywołaj skill w projekcie testowym
4. Sprawdź czy output jest poprawny

### Lokalne testowanie Codex

1. Edytuj SKILL.md w `codex/skills/`
2. Otwórz projekt testowy w Codex
3. Zainstaluj plugin z repo marketplace
4. Wywołaj skill

### Testowanie review gate'ów

1. Uruchom pełny pipeline: feature-discuss → generate-tasks → implement
2. Sprawdź czy gate'y się uruchamiają
3. Celowo wprowadź problem w output — sprawdź czy gate go łapie
4. Sprawdź czy iteracja (fix → re-review) działa

## Drift management

Skille Claude i Codex będą z czasem coraz bardziej się różnić — to zamierzone. Żeby trzymać kontrolę:

```bash
# Podsumowanie różnic
./scripts/diff-skills.sh

# Pełny diff
./scripts/diff-skills.sh --diff
```

Oczekiwane różnice:
- Frontmatter (`allowed-tools`, `argument-hint`) — Claude only
- Sekcje agent gate — Claude only
- `$ARGUMENTS` vs nieco inna składnia — platform-specific

Nieoczekiwane różnice do zsynchronizowania:
- Zmiana w fazach/krokach skilla
- Nowe sekcje w promptcie
- Zmiana formatu output
