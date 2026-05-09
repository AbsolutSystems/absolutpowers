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

**Claude Code:** wpisz `/absolutpowers:` i sprawdź czy widzisz 6 workflow skilli oraz `preboot`:
- feature-discuss
- generate-tasks
- implement
- review
- debug
- update-ai-context
- preboot

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

### Projekty używające PreBoot

Jeśli projekt używa bibliotek PreBoot, dodaj lokalną dokumentację pod `./preboot-docs/`. AbsolutPowers nie dostarcza już bundlowanych reference docs dla modułów PreBoot i nie zgaduje API.

Minimalny oczekiwany układ:

```text
preboot-docs/
├── index.md
├── preboot-core.md
├── preboot-query.md
├── preboot-securedata.md
├── preboot-eventbus.md
├── preboot-ddd.md
├── preboot-tasks.md
├── preboot-saga.md
├── preboot-files.md
├── preboot-sequence.md
└── preboot-documents-pdf.md
```

`index.md` jest opcjonalny, ale przydatny jako mapa wersji i modułów. Plik modułu jest wymagany dopiero wtedy, gdy agent ma pracować z tym modułem.

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

Małe zmiany dostają jeden plik `tasks-{slug}.md`. Większe feature'y mogą dostać tryb orchestrated:

```text
absolutpowers/feature/
├── tasks-csv-export.md
└── tasks-csv-export/
    ├── implementation-context.md
    ├── 01-domain-foundation.md
    ├── 02-service-behavior.md
    └── 99-final-verification.md
```

W tym trybie główny plik jest indeksem faz, a konkretna implementacja jest w małych phase files po 1-3 powiązane taski. `implementation-context.md` jest krótkim handoffem między fazami, nie dziennikiem pracy.

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

W Claude Code dla orchestrated tasków `implement` działa jako orkiestrator:
1. Czyta główny `tasks-{slug}.md`
2. Odpala `implementation-worker` dla pierwszej pending fazy
3. Worker implementuje tylko swój phase file i aktualizuje `implementation-context.md`
4. Orkiestrator uruchamia `phase-review`
5. Dopiero po `VERDICT: PASS` oznacza fazę jako `completed`
6. Po wszystkich fazach uruchamia final verification i pełny `review-implementation`

W Codex phase files są wykonywane sekwencyjnie w tej samej sesji, bez plugin-level subagentów.

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

### Czym jest implementation-context.md?

To krótki handoff między fazami orchestrated implementation. Powinien zawierać tylko fakty potrzebne kolejnym fazom: nowe API, decyzje techniczne, wspólne test fixtures, ograniczenia i wyniki weryfikacji. Nie powinien zawierać pełnych diffów ani długiego opisu procesu.

### Jak zaktualizować patterns.md po zmianach w kodzie?

```bash
/absolutpowers:update-ai-context
```

W trybie update skill wykryje nowe wzorce i zaproponuje aktualizację.

### Czym jest project-memory.md?

Trwała wiedza operacyjna — recurring traps, workaroundy, failure patterns. Skille czytają ją na starcie żeby nie powtarzać błędów. Nowe wpisy wymagają Twojej akceptacji.

### Co jeśli agent wykryje PreBoot, ale nie ma preboot-docs?

Skill `preboot` zatrzyma pracę i wskaże brakujący plik, np. `./preboot-docs/preboot-query.md`. To celowe: API PreBoot ma pochodzić z lokalnej dokumentacji projektu, nie z pamięci modelu ani starej dokumentacji bundlowanej w pluginie.

### Czy to działa z monorepo?

Tak. `update-ai-context` tworzy hierarchiczne CLAUDE.md w podkatalogach. Skille respektują scope katalogu w którym je uruchomisz.

## Następne kroki

- [Opis skilli](./skills-reference.md) — szczegółowa dokumentacja każdego skilla
- [Architektura review gate'ów](./review-gates.md) — jak działają automatyczne weryfikacje
- [Rozwój pluginu](./contributing.md) — jak modyfikować skille i agentów
