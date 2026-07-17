# Problem Report — Błędne komendy następnego kroku w handoffach harnessów

## Źródło
- Klient / kanał: użytkownik, obserwacje z sesji Codex i Claude Code
- Data zgłoszenia: 2026-07-17
- Załączniki: brak
- Kontekst: `absolutpowers/rules.md`, `absolutpowers/patterns.md` i `absolutpowers/project-memory.md` nie istnieją w repozytorium.
- Podejrzany punkt regresji: commit `92d9214` (`chore(docs): align harness syntax and Codex model routing`), który zastąpił część konkretnych komend opisami z bare skill names.

## Sprawa 1 — Codex pomija prefiks `$absolutpowers`
- **Reguła oczekiwana (wg użytkownika):** Codex ma otrzymać pełną, wykonywalną komendę w natywnej składni, np. `$absolutpowers feature-discuss absolutpowers/feature/workspace-esm-packages/planning-main.md "Omów Fazę 3: Core consumers"`.
- **Stan faktyczny / zgłoszenie:** sesja Codex zwróciła `feature-discuss absolutpowers/feature/workspace-esm-packages/planning-main.md "Omów Fazę 3: Core consumers"`, bez `$absolutpowers`.
- **Dowód:** `CLAUDE.md:24-32` definiuje składnię Codex jako `$absolutpowers skill-name [args]`; `references/codex-tools.md:12-17` nakazuje renderować właśnie tę składnię. Jednocześnie `skills/feature-discuss/SKILL.md:442-444` podaje tylko bare `feature-discuss` w opisie następnego kroku. Commit `92d9214` usunął wcześniejszy prefiks z tego handoffu, ale nie wstawił konkretnej komendy per harness.
- **Klasyfikacja:** potwierdzony bug
- **Uzasadnienie:** Kontrakt native command syntax istnieje, a aktualny handoff nie dostarcza komendy zgodnej z tym kontraktem. To regresja w formie handoffu, nie brak funkcjonalności.
- **Rekomendowana ścieżka:** `debug`
- **Co przekazać dalej:** zbadać `skills/feature-discuss/SKILL.md:442-444` oraz zmianę `92d9214`; ustalić, jak zapewnić, że opis fazy jest rozpoznawany jako wykonywalny handoff i zawsze dostaje składnię aktywnego harnessu.

## Sprawa 2 — Claude Code nie podaje pełnej komendy do kopiowania
- **Reguła oczekiwana (wg użytkownika):** Claude Code ma otrzymać jedną pełną linię `/absolutpowers:feature-discuss {ścieżka} "{argument}"`, gotową do skopiowania.
- **Stan faktyczny / zgłoszenie:** Claude zamiast pełnej linii napisał w przybliżeniu „następnie odpal feature-discuss na dokumencie”, dodatkowo z literówką `feature-discus`.
- **Dowód:** `CLAUDE.md:24-32` definiuje składnię Claude; `skills/feature-discuss/SKILL.md:442-444` zawiera tylko instrukcję „odpal feature-discuss” oraz przykład w cudzysłowie, nie komendę `/absolutpowers:feature-discuss ...`; `skills/implement/SKILL.md:446-455` podobnie mówi „feature-discuss na `{epic-main-path}` z argumentem” zamiast renderować pełną linię. `skills/feature-discuss/SKILL.md:498-500` wymaga składni aktywnego harnessu, ale nie podaje mechanizmu ani przykładu pełnego handoffu.
- **Klasyfikacja:** potwierdzony bug
- **Uzasadnienie:** Zamiast stabilnego interfejsu copy-paste skill emituje opis semantyczny. Model ma wtedy swobodę parafrazy, co bezpośrednio tłumaczy zarówno skrócenie komendy, jak i literówkę.
- **Rekomendowana ścieżka:** `debug`
- **Co przekazać dalej:** prześledzić wszystkie handoffy w `feature-discuss`, `generate-tasks` i `implement`; sprawdzić, gdzie wymaganie „wyrenderuj w składni aktywnego harnessu” nie jest połączone z literalnym formatem komendy.

## Sprawa 3 — Claude Code wraca do legacyjnego `@implement @ścieżka`
- **Reguła oczekiwana (wg użytkownika):** Claude Code ma otrzymać `/absolutpowers:implement absolutpowers/feature/tasks-push-based-task-notify.md` — bez `@` przed skillem i bez `@` przed ścieżką.
- **Stan faktyczny / zgłoszenie:** Claude zwrócił: `Następny krok pipeline: @implement @absolutpowers/feature/tasks-push-based-task-notify.md. Odpalić implementację, czy stop tutaj?`
- **Dowód:** `CLAUDE.md:24-32` oraz `hooks/session-context.md:1-9` zakazują `@skill` i definiują `/absolutpowers:skill-name [args]` dla Claude. `skills/generate-tasks/SKILL.md:410-412` mówi „wyrenderuj komendę w składni aktywnego harnessu”, a `:438` zakazuje `@implement`, lecz nie zawiera pozytywnego, literalnego przykładu. W aktywnych materiałach repo nadal istnieją sprzeczne wzorce: `references/fork-policy.md:14-15` preferuje `@ship`/`@implement`, `docs/adr/2026-07-16-lightweight-task-routing.md:42-44` używa `@implement`/`@review`, a `tests/test_lightweight_task_routing.py:118-119,150,206` nadal asercyjnie szuka legacyjnych prefiksów. Commit `92d9214` usunął część dawnych komend z głównych skillów, ale nie wyczyścił tych aktywnych źródeł.
- **Klasyfikacja:** potwierdzony bug
- **Uzasadnienie:** Obserwowany output narusza jednoznaczny kontrakt Claude i jest wspierany przez realną sprzeczność w materiale kontekstowym. Nie da się przypisać tej konkretnej sesji do jednego pliku bez logu promptu, ale regresja kontraktu jest potwierdzona.
- **Rekomendowana ścieżka:** `debug`
- **Co przekazać dalej:** ustalić pełny zbiór źródeł czytanych przy handoffie implementacji, rozdzielić historyczne artefakty od aktywnego kontekstu i usunąć/oznaczyć każdy aktywny legacyjny wzorzec `@skill`.

## Podsumowanie / routing

| # | Sprawa | Klasyfikacja | Ścieżka |
|---|--------|--------------|---------|
| 1 | Codex bez `$absolutpowers` | potwierdzony bug | `debug` |
| 2 | Claude bez pełnej komendy | potwierdzony bug | `debug` |
| 3 | Claude z legacyjnym `@implement @ścieżka` | potwierdzony bug | `debug` |

## Wspólny sygnał do następnego dochodzenia

Wszystkie trzy przypadki dotyczą tego samego kontraktu interfejsu, ale nie zostały połączone w jedną sprawę, ponieważ każdy ma inną obserwowalną rozbieżność: brak prefiksu Codex, parafraza Claude oraz powrót do starego prefiksu Claude. Najmocniejszy wspólny trop to commit `92d9214`, który zamienił konkretne komendy na nazwy skillów + instrukcję „w składni aktywnego harnessu”, pozostawiając jednocześnie część legacyjnych wzorców w aktywnych dokumentach i testach.
