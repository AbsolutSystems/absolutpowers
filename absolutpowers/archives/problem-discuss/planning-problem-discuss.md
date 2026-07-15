# problem-discuss — wejście rozpoznawcze (intake + triage zgłoszeń klienta)

## Status
Zaimplementowane (v3.7.0). Skill w obu drzewach (Claude + Codex).

## Problem
Pipeline ma dwa wejścia, które zakładają, że problem został **już sklasyfikowany** przez
użytkownika:
- jasny feature → `feature-discuss`
- jasny bug (error / stack trace / test fail / CI) → `debug`

Brakuje wejścia dla **wieloelementowego zgłoszenia domenowego od klienta** — zakotwiczonego
w regułach biznesowych, z załącznikami, gdzie dla każdej sprawy NIE wiadomo jeszcze, czy to bug,
gap featurowy, błąd danych/konfiguracji czy nieporozumienie. Użytkownik musiał ręcznie
pre-klasyfikować zanim wszedł do pipeline'u.

Przykład realny (zgłoszenie klienta, dwie sprawy):
> 1. Wyjaśnić dlaczego użytkownik Tomasz Posiewka dostaje maile (+ obraz)
> 2. Po akceptacji korekty pozasezonowej powinny wyjść 2 maile (potwierdzenie zmiany mas +
>    potwierdzenie złożenia raportu rocznego) — w produkcji nie widzę żeby wyszły (+ plik)

## Użytkownicy
Developer/architekt odbierający komunikację od klienta/stakeholdera. Wejście: surowy mail/zgłoszenie
z wieloma uwagami + załączniki. Oczekiwanie: świadoma decyzja, którą ścieżką iść per sprawa,
zamiast zgadywania i marnowania czasu na debug czegoś, co okazuje się gapem albo nieporozumieniem.

## Oczekiwane zachowanie
- Rozbicie jednego zgłoszenia na N osobnych spraw.
- Per sprawa: wyciągnięcie reguły biznesowej (intended behavior wg klienta) + rozbieżności.
- Czytanie załączników (obrazy/pliki) jako dowodu.
- Dochodzenie w kodzie (breadth, nie depth) — potwierdzenie/obalenie reguły z dowodem `file:line`.
- Klasyfikacja per sprawa do jednego z 6 kubełków.
- Raport `absolutpowers/problem/problem-{slug}.md` + fan-out routing.
- **Twarda granica:** nie naprawia, nie planuje, nie pisze taskow.

## Wybrane rozwiązanie
Osobny skill `problem-discuss` jako **kuzyn `debug`** (nie `feature-discuss`):
- `debug` = depth, single root-cause, znany failure.
- `feature-discuss` = forward, projektowanie nowego X.
- `problem-discuss` = breadth, intake + dochodzenie + klasyfikacja + routing wielu spraw,
  gdzie status każdej jest nieznany.

Potwierdzony bug oddawany do `debug` na deep-dive; gap do `feature-discuss`.

### Klasyfikacja (6 kubełków)
potwierdzony bug → debug · nie zaimplementowane (gap) → feature-discuss · błąd konfiguracji/env →
fix bezpośredni · anomalia danych → fix danych · działa-jak-zaprojektowano → close (wyjaśnienie
klientowi) · za mało danych → dopytaj.

### Fan-out routing
Jedno zgłoszenie → wiele ścieżek naraz (best-effort nudge, bez automatyki). Skill kończy na
rekomendacji, nie wykonuje kolejnych kroków.

### Uzasadnienie
- Wypełnia realną dziurę między feature-discuss a debug.
- Wąski TRIGGER rozłączny z `debug` (zgłoszenie klienta / wieloelementowe / reguła↔produkcja),
  by uniknąć kolizji retrieval — dlatego też dodano notkę "vs problem-discuss" w `debug`.
- Twarda granica (intake/triage, nie fix/plan) zapobiega połknięciu debug+feature-discuss+implement.

### Rozważane alternatywy
- **Tryb `feature-discuss`** — odrzucone: miesza "mam rozwiązanie" z "mam objaw", muli trigger
  i output, duży overlap kierunkowo przeciwny (forward vs backward).
- **Tryb/rozszerzenie `debug`** — odrzucone: debug to depth single-issue; tu breadth multi-issue
  z ekstrakcją reguły biznesowej, obsługą załączników i klasyfikacją zamiast naprawy.
- **Cienki router bez dochodzenia** — odrzucone po doprecyzowaniu przykładu: realne zgłoszenie
  wymaga substancjalnego dochodzenia w kodzie per sprawa przed klasyfikacją.

## Zakres
### In scope
- `claude/skills/problem-discuss/SKILL.md` + `codex/skills/problem-discuss/SKILL.md`
- Notka "vs problem-discuss" w `debug` (oba drzewa)
- Nowy katalog wyjściowy `absolutpowers/problem/`
- Aktualizacja README.md, CLAUDE.md
- Bump wersji 3.6.0 → 3.7.0 (oba manifesty)

### Out of scope
- Gate (`review-problem`) — skill dochodzeniowy, brak artefaktu-kontraktu do walidacji.
- Automatyczne odpalanie kolejnych skilli po routingu (wybór należy do użytkownika).
- Integracja z systemami ticketowymi / pobieranie zgłoszeń (załączniki idą w prompcie).

## Decyzje (zatwierdzone w dyskusji)
1. Nowy katalog `absolutpowers/problem/`.
2. Bez gate.
3. Załączniki w prompcie (ścieżki/obrazy), skill je czyta.
4. Oba drzewa od razu.

## Pliki do zmodyfikowania / utworzenia
- NEW `claude/skills/problem-discuss/SKILL.md`
- NEW `codex/skills/problem-discuss/SKILL.md`
- NEW `absolutpowers/feature/planning-problem-discuss.md` (ten plik)
- MOD `claude/skills/debug/SKILL.md`, `codex/skills/debug/SKILL.md` (notka "vs")
- MOD `README.md`, `CLAUDE.md`
- MOD `claude/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json` (3.7.0)

## Edge cases i ryzyka
- Trigger collision z `debug` → mitygacja: wąski TRIGGER + notka "vs" w obu skillach.
- Sprawa bez dowodu → klasyfikacja "za mało danych", nie zgadywanie.
- Załącznik pominięty → Red Flag w skillu ("dowód bywa właśnie tam").
- Scope creep (skill zaczyna naprawiać/planować) → twarda granica + Red Flags STOP.

## Pytania otwarte
- Czy w przyszłości dodać lekki gate sprawdzający "każda sprawa ma dowód + klasyfikację"?
  Na razie nie — spójne z `debug`.

## Notatki z dyskusji
Skill powstał z dyskusji o tym, czy `feature-discuss` powinien mocniej drążyć "dlaczego"
(okazało się: już to robi — Faza 1 "ROZDZIEL CO/DLACZEGO od JAK"), oraz o równoległym wejściu
dla zgłoszeń klienta. Doprecyzowanie realnym przykładem (korekta → 2 maile, których nie ma
w produkcji) przesunęło projekt z "cienki router" na "substancjalny intake + dochodzenie".
