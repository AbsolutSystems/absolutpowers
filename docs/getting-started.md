# Getting Started with AbsolutPowers

Ten przewodnik przeprowadzi Cię przez instalację i pierwsze użycie AbsolutPowers w Twoim projekcie.

## Wymagania

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI lub IDE extension (VS Code / JetBrains)
- Opcjonalnie: [Codex](https://github.com/openai/codex) jeśli chcesz korzystać z obu platform

## Instalacja

### Claude Code

```bash
/plugin marketplace add AbsolutSystems/absolutpowers
/plugin install absolutpowers@absolutpowers-skills
```

Zrestartuj Claude Code. Wpisz `/absolutpowers:` — autouzupełnianie pokaże dostępne skille.

### Codex

Otwórz dowolne repozytorium w Codex. Repo AbsolutPowers Skills eksponuje marketplace w `.agents/plugins/marketplace.json`. Zainstaluj plugin `absolutpowers` z repo marketplace.

### Weryfikacja instalacji

**Claude Code:** wpisz `/absolutpowers:` i sprawdź czy widzisz 6 skilli:
- feature-discuss
- generate-tasks
- implement
- review
- debug
- update-ai-context

**Codex:** wpisz `$absolutpowers` i sprawdź autouzupełnianie.

## Krok 1: Przygotuj projekt

Zanim zaczniesz korzystać ze skilli, musisz wygenerować kontekst AI dla projektu. Wejdź do katalogu projektu i uruchom:

```bash
/absolutpowers:update-ai-context
```

To stworzy:

| Plik | Co zawiera |
|------|-----------|
| `CLAUDE.md` | Dokumentacja projektu dla Claude Code (stack, architektura, konwencje) |
| `AGENTS.md` | Mirror CLAUDE.md dla Codex |
| `./absolutpowers/patterns.md` | Odkryte wzorce w kodzie (minimum 3 wystąpienia) |
| `./absolutpowers/rules.md` | Draft reguł projektowych — **wymaga Twojej akceptacji** |

Skill zaproponuje reguły na podstawie analizy kodu. Przejrzyj je i potwierdź — reguły nigdy nie są narzucane automatycznie.

### Co dodać do .gitignore

```gitignore
# Memory candidates to kolejka do review — nie commituj
absolutpowers/memory-candidates/
```

Planning docs, tasks, reviews i project-memory warto trzymać w git — to dokumentacja projektu.

## Krok 2: Twój pierwszy feature

### Dyskusja

```bash
/absolutpowers:feature-discuss "chcę dodać eksport danych do CSV"
```

Skill zadaje pytania pojedynczo, z opcjami do wyboru. Odpowiadaj literką (a/b/c) albo napisz swoją wersję. Dyskusja ma kilka faz:

1. **Zrozumienie potrzeby** — co, kto, dlaczego
2. **Analiza kodu** — skill przegląda Twój codebase
3. **Propozycja rozwiązań** — 2-3 opcje z tradeoffami
4. **Doprecyzowanie** — edge case'y, zależności
5. **Zapis** — generuje `planning-csv-export.md`
6. **Review gate** — subagent weryfikuje plan (automatycznie)

Na końcu zobaczysz `VERDICT: PASS` albo listę poprawek (skill naprawia sam, do 3 iteracji).

### Generowanie tasków

```bash
/absolutpowers:generate-tasks @absolutpowers/feature/planning-csv-export.md
```

Skill czyta plan, analizuje kod, i generuje sekwencyjne taski z:
- Dokładnymi ścieżkami plików
- Sygnaturami metod z typami
- Przypadkami testowymi
- Referencjami do istniejących wzorców
- Finalnym taskiem weryfikacyjnym (build, typecheck, lint)

Potem automatyczny review gate sprawdza jakość tasków.

### Implementacja

```bash
/absolutpowers:implement @absolutpowers/feature/tasks-csv-export.md
```

Skill realizuje taski po kolei z podejściem TDD:
1. Czyta task
2. Pisze test (jeśli TDD ma sens dla tego tasku)
3. Implementuje kod
4. Uruchamia testy
5. Oznacza task jako `completed`
6. Przechodzi do następnego

Po ukończeniu wszystkich tasków — automatyczny review gate sprawdza kod.

### Code review

```bash
/absolutpowers:review
```

4-fazowy review wszystkich zmian na branchu. Generuje raport w `./absolutpowers/reviews/`.

## Krok 3: Debugowanie

Dla bugów nie potrzebujesz pełnego pipeline'u:

```bash
/absolutpowers:debug "endpoint /api/users zwraca 500 przy pustym query"
```

Skill wymusza systematyczne podejście:
- Najpierw root cause, potem fix
- Jedno rozwiązanie na raz
- Test przed fixem
- Eskalacja po 3 nieudanych próbach

## Typowe pytania

### Czy muszę używać wszystkich skilli po kolei?

Nie. Każdy skill działa samodzielnie. Ale pipeline `feature-discuss → generate-tasks → implement → review` daje najlepsze rezultaty, bo każdy krok buduje na poprzednim.

### Co jeśli review gate odrzuci mój plan 3 razy?

Skill pokaże pozostałe problemy i zapyta Cię co robić. Możesz:
- Ręcznie poprawić plan
- Kontynuować mimo problemów
- Wrócić do dyskusji

### Czy mogę edytować planning doc / tasks doc ręcznie?

Tak. To pliki Markdown — możesz je edytować w dowolnym edytorze. Skill `implement` czyta plik as-is.

### Jak zaktualizować patterns.md po zmianach w kodzie?

```bash
/absolutpowers:update-ai-context
```

W trybie update skill wykryje nowe wzorce i zaproponuje aktualizację.

### Czym jest project-memory.md?

Trwała wiedza operacyjna — recurring traps, workaroundy, failure patterns. Skille czytają ją na starcie żeby nie powtarzać błędów. Nowe wpisy wymagają Twojej akceptacji.

### Czy to działa z monorepo?

Tak. `update-ai-context` tworzy hierarchiczne CLAUDE.md w podkatalogach. Skille respektują scope katalogu w którym je uruchomisz.

## Następne kroki

- [Opis skilli](./skills-reference.md) — szczegółowa dokumentacja każdego skilla
- [Architektura review gate'ów](./review-gates.md) — jak działają automatyczne weryfikacje
- [Rozwój pluginu](./contributing.md) — jak modyfikować skille i agentów
