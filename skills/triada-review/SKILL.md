---
name: triada-review
description: >
  Host-agnostic, multi-agent code review of the current branch: delegates independent
  tech-lead, security/correctness/test, and optional UI perspectives, then synthesizes
  one verdict. TRIGGER when: "triada review", "multi-agent review", "review trzema
  agentami", "sprawdź branch z kilku perspektyw", large PR review, independent
  architecture/security/UI review before merge. NIE wyzwalaj na: solo full review
  (use review); incoming PR feedback (use receiving-code-review); AC-to-task-to-code
  traceability (use analyze).
allowed-tools: Read, Glob, Grep, Bash, Agent
argument-hint: "[dodatkowy kontekst]"
---

# Triada Review — Orchestrator

Dodatkowy kontekst od użytkownika (jeśli pusty, zignoruj):
$ARGUMENTS

---

Wykonaj code review aktualnego brancha względem mastera, używając trzech agentów z rozłącznymi zakresami. Ty (orchestrator) zbierasz kontekst, delegujesz, syntetyzujesz.

> To jest **standalone, host-agnostyczny multi-agent review na żądanie** — nie
> zastępuje gate'ów pipeline (`review-implementation`) ani solo skilla `review`.
> Różnica: `review` = solo, 4 fazy i audit trail do pliku.
> `triada-review` = niezależne perspektywy, JSON + synteza na każdym harnessie
> wyposażonym w dispatch subagentów; bez dispatchu działa sekwencyjnie/inline jako advisory.

---

## Kontrakt dispatchu per harness

Przed pierwszym delegowaniem przeczytaj `references/harness-dispatch.md` oraz mapping
aktywnego harnessu, jeśli istnieje (`references/codex-tools.md`,
`references/pi-tools.md` albo `references/grok-tools.md`).

Dla każdej aktywnej roli przeczytaj pełne ciało odpowiadającego jej promptu:

| Rola | Prompt roli | Claude registered type |
|---|---|---|
| `tech-lead-advisor` | `agents/tech-lead-agent.md` | `absolutpowers:tech-lead-agent` |
| `security-auditor` | `agents/codebase-auditor.md` | `absolutpowers:codebase-auditor` |
| `ui-reviewer` | `agents/ui-reviewer.md` | `absolutpowers:ui-reviewer` |

Registered type jest optymalizacją Claude Code, a nie warunkiem działania skilla.
Na harnessie bez registry dispatchuj świeżego generycznego subagenta z pełnym ciałem
promptu roli i konkretnym kontekstem z KROKU 3. Preferuj równoległy dispatch. Jeśli
harness potrafi uruchamiać subagentów tylko sekwencyjnie, zachowaj osobny świeży
kontekst dla każdej roli. Dopiero przy całkowitym braku dispatchu wykonaj perspektywy
inline i oznacz końcowy wynik jako `advisory (not fully isolated)`.

Przy wielu paczkach dispatchuj w falach mieszczących się w limicie współbieżności
harnessu. Nie zamieniaj braku wolnego slotu w inline fallback — poczekaj na wynik
bieżącej fali, a następnie uruchom kolejną.

Nigdy nie próbuj najpierw wywoływać nieistniejącego registered type na Codex, Pi lub
Grok. Użyj od razu natywnej ścieżki z mappingu harnessu.

---

## KROK 0 — Wczytaj konfigurację agentów

Domyślnie prompty ról są **wbudowane w plugin** (tabela wyżej), więc skill działa
bez configu. Opcjonalnie pozwól projektowi nadpisać mapowanie: najpierw odczytaj
`.absolutpowers/triada-review.agents.json` z root repo. Dla kompatybilności wstecznej,
jeśli go nie ma, odczytaj `.claude/triada-review.agents.json`.

Struktura: `agents.<rola>.{ subagent_type, enabled, scope }`.
- `subagent_type` — opcjonalny natywny/registered type. Użyj go tylko, jeśli aktywny
  harness potrafi go rozwiązać; w przeciwnym razie użyj generycznego subagenta z promptem roli.
- `enabled` — `true` (zawsze), `false` (pomiń tę rolę całkowicie), `"ui-only"` (spawn tylko dla paczek zawierających pliki UI).
- `scope` — **steruje którymi kryteriami** ocenia ta rola. Wartości:
  - `"all"` lub pominięte → wszystkie kryteria roli (patrz tabela kluczy w KROKU 3).
  - lista kluczy, np. `["security", "correctness"]` → tylko te kryteria. Klucze spoza zestawu roli ignoruj i odnotuj w syntezie.
  - `[]` (pusta lista) → brak kryteriów → potraktuj jak `enabled: false` dla tej roli (odnotuj w syntezie).

**Defaulty Claude Code** (gdy configu brak lub jest niepoprawny). Pozostałe harnessy
używają tych samych promptów ról przez swoje generyczne primitive dispatchu:

| Rola | subagent_type | enabled |
|---|---|---|
| `tech-lead-advisor` | `absolutpowers:tech-lead-agent` | true |
| `security-auditor` | `absolutpowers:codebase-auditor` | true |
| `ui-reviewer` | `absolutpowers:ui-reviewer` | ui-only |

W finalnym podsumowaniu odnotuj role, faktyczny mechanizm dispatchu (registered type,
generic isolated subagent, sequential isolated albo inline advisory) oraz pominięcia.

---

## KROK 1 — Zbierz kontekst (sam, przed delegacją)

```bash
git fetch origin master
git log origin/master..HEAD --oneline           # lista commitów
git diff origin/master...HEAD --stat            # skala (pliki, +/-)
git diff origin/master...HEAD --name-only       # lista plików
git diff origin/master...HEAD                   # pełny diff
```

> Jeśli repo używa `main` zamiast `master`, podstaw `main` we wszystkich komendach
> (`git rev-parse --verify main` → jeśli istnieje, użyj `main`).

### Zbierz pełny kontekst zmiany

Commit messages:
git log origin/master..HEAD --format="%h %s%n%b"

Opis PR (jeśli gh dostępne):
gh pr view --json title,body,labels,closingIssuesReferences 2>/dev/null

Komentarze do PR (jeśli istnieją i wyglądają na istotne):
gh pr view --comments 2>/dev/null

Połącz wszystko w CEL ZMIANY (2-3 zdania). Priorytet źródeł:
1. Opis PR — bo zwykle zawiera "dlaczego" i pełniejszy kontekst
2. Linked issues — bo definiują problem do rozwiązania
3. Commit messages — bo opisują "co" krok po kroku
4. Labels — bo mówią o charakterze zmiany (bug/feature/refactor/hotfix)

Status CI (jeśli `gh` dostępne):
```bash
gh pr checks 2>/dev/null || gh run list -b $(git branch --show-current) -L 1
```
Jeśli CI fail-uje — odnotuj, ale kontynuuj. Jeśli przechodzi — przyjmij że testy są zielone i skup się na ich **jakości**, nie wyniku.

### Wczytaj reguły projektu

Przeczytaj `./absolutpowers/rules.md` z roota projektu (jeśli istnieje). To **ważny
plik** — definiuje twarde reguły projektu (architektoniczne, security, konwencje,
testowe). Zapamiętaj treść; przekażesz ją każdemu agentowi jako reguły do
sprawdzenia w jego zakresie (KROK 3) i podsumujesz zgodność w syntezie (KROK 4).
Jeśli pliku nie ma — pomiń sekcję zgodności i odnotuj to w finalnym raporcie.

---

## KROK 1.5 — Sanity check kontekstu

Zanim przejdziesz dalej, oceń jakość samego kontekstu. To wpłynie
na pewność całego review.

### Czy opis pasuje do diffu?

Przejdź szybko przez listę plików z `--name-only` i sprawdź:
- Czy każda znacząca zmiana w kodzie jest wspomniana w opisie PR/commitach?
- Czy w diffie są zmiany, które wyglądają na NIEzwiązane z deklarowanym celem?
  (np. PR "dodaje walidację emaila" ale zmienia też logikę autoryzacji)
- Czy są zmiany "po drodze" — refaktoring, formatowanie, rename —
  zmieszane ze zmianami funkcjonalnymi?

### Czy cel ma sens?

- Czy commit messages opisują CO i DLACZEGO, czy są typu "fix", "wip", "update"?
- Czy opis PR mówi tylko "co" (np. "Adds new service layer") bez "dlaczego"?
- Czy cel sam w sobie wygląda na uzasadniony, czy brzmi jak rozwiązanie
  szukające problemu?

### Co z tym zrobić

Jeśli kontekst jest słaby lub niespójny z diffem — kontynuuj review, ale:
- W finalnym raporcie dodaj sekcję `⚠️ KONTEKST` z konkretnymi obserwacjami.
- Przy ocenie `goal_achievement` weź pod uwagę, że "cel" mógł być
  niekompletny — jeśli kod robi więcej niż opis, to nie znaczy że robi źle,
  ale autor powinien to uzupełnić.
- W `open_questions` dla autora wpisz pytania o niespójności.

NIE rób tego inkwizycyjnie — większość PR-ów ma niedoskonały opis
i to jest normalne. Sygnalizuj tylko gdy niespójność jest znacząca
lub gdy cel jest tak słabo opisany, że nie da się sensownie ocenić
"czy kod realizuje cel".

## KROK 2 — Pojedynczo czy z podziałem?

Policz: `rozmiar_diffu = insertions + deletions` (z `--stat`).

| Warunek | Tryb |
|---|---|
| `rozmiar_diffu < 1500` AND `liczba_plików < 20` | **POJEDYNCZY** |
| `rozmiar_diffu >= 1500` OR `liczba_plików >= 20` | **PODZIELONY** |

### Strategia podziału (wybierz pierwszą która pasuje do struktury repo)

1. Po **warstwach** — `{api, db/migrations, frontend, infra/config, tests}`
2. Po **feature folderach** — jeśli repo jest zorganizowane per-feature
3. Po **pakietach** w monorepo (`apps/*`, `packages/*`)
4. Po **domenach funkcjonalnych** — wywnioskuj z commitów i ścieżek

### Zasady podziału

- Plik nie jest rozdzielany między paczki (idzie cały do jednej).
- Pliki silnie powiązane (komponent + jego test + style) idą razem.
- Każda paczka powinna mieścić się poniżej 1500 linii diffu.
- Maksymalnie **5 paczek**. Powyżej — zasugeruj autorowi rozbicie PR-a.

Dla każdej paczki przygotuj mini-kontekst: nazwa, rola, lista plików, fragment diffu, **cel zmiany z kroku 1** (ten sam dla wszystkich paczek — agenci muszą wiedzieć do czego dąży całość).

---

## KROK 3 — Deleguj do trzech agentów równolegle

Każda paczka (lub cały diff w trybie pojedynczym) idzie do aktywnych ról. Każda ma
**inny zakres** i nie wchodzi w cudzy. Dispatchuj role **równolegle**, jeśli harness
to obsługuje, używając kontraktu dispatchu powyżej.

### Co przekazać każdemu agentowi

- Cel zmiany (krok 1)
- Lista commitów
- Diff (paczki lub całość)
- Status CI
- **Treść `rules.md`** (jeśli istnieje) — z instrukcją: „sprawdź naruszenia reguł
  mieszczące się w twoim zakresie i raportuj je w `findings` z kategorią `rules`".
- **Jego zakres kryteriów** (sekcja niżej)
- Format outputu (JSON, sekcja niżej)
- W trybie podzielonym: nazwa i rola paczki

### Podział kryteriów

> Dla każdej roli użyj mechanizmu dispatchu ustalonego w KROKU 0. `subagent_type`
> stosuj tylko wtedy, gdy harness rzeczywiście go rejestruje. Role z `enabled: false` pomiń. `ui-reviewer` (`enabled: "ui-only"`) spawnuj tylko dla paczek z plikami UI. Nazwy ról poniżej (`tech-lead-advisor` itd.) to **etykiety zakresów**, nie typy agentów — typ bierzesz z configu.
>
> **Filtr kryteriów przez `scope`:** każde kryterium ma stały klucz (tabela niżej). Agent ocenia **tylko** kryteria, których klucz jest w `scope` danej roli. `scope: "all"` lub brak → wszystkie kryteria roli. W instrukcji dla agenta wymień konkretnie które kryteria (z numerami) ma ocenić, a które pominąć. W syntezie odnotuj zawężenie scope (np. „`security-auditor` ograniczony do security + correctness — testy pominięte przez config").
>
> **Reguły projektu (`rules`):** niezależnie od scope, każdy agent sprawdza naruszenia `rules.md` mieszczące się w jego zakresie i raportuje je z kategorią `rules`. Jeśli `rules.md` nie istnieje — pomiń.

#### Klucze kryteriów (dla pola `scope` w configu)

| Rola | Klucz | Nr kryterium |
|---|---|---|
| `tech-lead-advisor` | `cel` | 1 |
| | `architektura` | 2 |
| | `overengineering` | 3 |
| | `czytelnosc` | 4 |
| `security-auditor` | `security` | 5 |
| | `correctness` | 6 |
| | `testy` | 7 |
| `ui-reviewer` | `stany_ui` | 8 |
| | `interakcje` | 9 |
| | `reprezentacja` | 10 |
| | `a11y` | 11 |
| | `race_ui` | 12 |
| | `cel_usera` | 13 |

**`tech-lead-advisor`** — perspektywa pragmatyczna, mentoring, dług techniczny:

1. **CEL** — czy kod realizuje to, co opisują commity? Scope creep? Połowiczne wykonanie?
2. **ARCHITEKTURA** — wzorce, spójność z resztą kodu, separacja warstw, kierunek zależności, dopasowanie do istniejących konwencji.
3. **OVERENGINEERING** — abstrakcje bez powodu, premature generalization, warstwy "na zaś", konfiguracja której nikt nie użyje, factory dla jednej implementacji.
4. **CZYTELNOŚĆ** — nazewnictwo, długość funkcji, komentarze tam gdzie trzeba (i ich brak gdzie kod się sam tłumaczy).

> Instrukcja dla `tech-lead-advisor`: w tym workflow oceniasz **tylko** powyższe cztery kategorie (plus naruszenia `rules.md` w zakresie architektury/konwencji → kategoria `rules`). Security, edge case'y, testy i UI ocenią inni — nie wchodź w ich zakres, nawet jeśli zauważysz problem. Zgłoś tylko w `open_questions` jeśli uważasz że coś jest poza twoim zakresem ale wymaga uwagi. **Zwróć wyłącznie JSON w formacie z sekcji niżej** (`agent: "tech-lead-advisor"`), bez dodatkowego tekstu ani prozy doradczej.

**`security-auditor`** — głęboka analiza techniczna, podejście paranoidalne (agent `codebase-auditor`):

5. **SECURITY** — walidacja inputu, auth/authz, sekrety w kodzie/logach, SQL injection, XSS, path traversal, SSRF, brak rate limitingu, logowanie PII/tokenów.
6. **CORRECTNESS** — edge cases, error handling, null/undefined safety, off-by-one, kolejność operacji, transakcyjność, race conditions (poza UI).
7. **JAKOŚĆ TESTÓW** (przegląd kodu, nie uruchamianie):
  - Czy zmiany są pokryte? Co nie jest?
  - Testy testują **zachowanie** (input→output, side effects) czy **implementację** (wewnętrzne wywołania)?
  - Nazwy testów opisują co testują?
  - Edge case'y obecne? (puste, null, błędy zewnętrzne)
  - Flaky patterns: `sleep()`, hardcoded czas, kolejność zależna od HashMapy, współdzielony stan między testami?
  - Mocki tam gdzie wystarczy fake, lub odwrotnie?

> Instrukcja dla `security-auditor`: w tym workflow oceniasz **tylko** powyższe trzy kategorie (plus naruszenia `rules.md` w zakresie security/correctness/testów → kategoria `rules`). Architektura, czytelność i UI to nie twoja działka — nie komentuj. Jeśli zauważysz coś krytycznego poza zakresem, zgłoś w `open_questions`.

**`ui-reviewer`** — perspektywa QA/UX, tylko jeśli paczka zawiera UI:

8. **STANY UI** — każdy widok obsługuje loading, error, empty, success? Disabled state na buttonach podczas requestu?
9. **INTERAKCJE** — każdy `onClick`/`onSubmit` faktycznie coś robi (nie dead buttons, TODO, puste handlery)? Linki mają poprawne `href`? Walidacja formularzy?
10. **REPREZENTACJA DANYCH** — null/undefined safety w renderze, formatowanie dat/liczb/walut, długie stringi, pusty stan listy, stable keys w mapowaniu.
11. **ACCESSIBILITY** — `aria-label`/`role` gdy trzeba, `<label>` dla inputów, focus management w modalnych, kolor nie jako jedyny nośnik informacji, kontrast.
12. **RACE CONDITIONS UI** — stale state po podwójnym kliku, optimistic update bez rollback, `useEffect` bez cleanup, kolejność requestów.
13. **CEL UŻYTKOWNIKA** — prześledź flow z commitów oczami usera. Czy ścieżka klików realizuje cel? Gdzie user może się zgubić? Czy feedback po sukcesie/błędzie jest widoczny i konkretny?

> Jeśli paczka **nie zawiera plików UI** (czyste API/DB/infra), pomiń `ui-reviewer` dla tej paczki i odnotuj w syntezie.

---

## KROK 4 — Synteza

W trybie pojedynczym: masz 3 review.
W trybie podzielonym: masz do 3×N review.

### Co robisz

1. **Merge findings po `(file, linia)`** — jeśli ≥2 agentów wskazuje to samo miejsce (rzadkie, bo zakresy są rozłączne — ale możliwe na granicach), oznacz jako "wysoka pewność".
2. **Zgodność z `rules.md`** — zbierz wszystkie findings z kategorią `rules` od wszystkich agentów. Zestaw złamane reguły (z `plik:linia`) vs reguły potwierdzone jako spełnione (jeśli agenci to odnotowali). Jeśli `rules.md` nie istnieje — pomiń tę sekcję i napisz to wprost.
3. **Cross-package issues** (tylko tryb podzielony) — twoja własna analiza:
  - Czy interfejs zmieniony w paczce A jest uaktualniony w paczce B?
  - Czy nowy endpoint w paczce API ma frontend w paczce UI?
  - Czy migracja DB w paczce X ma odpowiadające zmiany kodu w paczce Y?
  - Czy nowe pole w modelu jest obsłużone wszędzie gdzie model jest używany?
4. **Rozbieżności priorytetów** — jeśli `tech-lead-advisor` mówi że coś jest minor a `security-auditor` że blocker (lub odwrotnie), wystaw własną decyzję z uzasadnieniem.
5. **Final verdict** — zgodnie z formatem niżej.

---

## Format outputu od każdego agenta (sztywny JSON)

```json
{
  "agent": "tech-lead-advisor | security-auditor | ui-reviewer",
  "package": "nazwa paczki lub 'full' w trybie pojedynczym",
  "verdict": "approve | approve_with_comments | request_changes | block",
  "goal_achievement": "pełne | częściowe | rozminięte | nie_dotyczy",
  "findings": [
    {
      "severity": "blocker | major | minor | nit",
      "category": "cel | architektura | overengineering | czytelność | security | correctness | testy | stany_ui | interakcje_ui | reprezentacja | a11y | race_ui | cel_usera | rules",
      "file": "ścieżka/do/pliku.ts:linia",
      "issue": "1-2 zdania co jest nie tak",
      "suggestion": "konkretna propozycja (kod albo opis)"
    }
  ],
  "what_works_well": ["...", "..."],
  "open_questions": ["..."]
}
```

> Uwaga: `goal_achievement` ocenia tylko `tech-lead-advisor` (cel jest w jego zakresie). Pozostali ustawiają `nie_dotyczy`. `ui-reviewer` ocenia własny wariant celu — cel użytkownika (kryterium 13) — i raportuje to w `findings`, nie w `goal_achievement`.

---

## Finalne podsumowanie (output orchestratora dla użytkownika)

```
═══════════════════════════════════════════════════════════════
TRIADA REVIEW — <branch> vs master
═══════════════════════════════════════════════════════════════

Cel zmiany (z commitów):
  <2-3 zdania>

Skala: <X plików, +Y/-Z linii>
Tryb: <pojedynczy | podzielony na N paczek: [nazwy]>
CI: <pass | fail | unknown>

WERDYKT: <approve | approve_with_comments | request_changes | block>
Goal achievement (tech-lead-advisor): <pełne | częściowe | rozminięte>

───────────────────────────────────────────────────────────────
⚠️ KONTEKST  (tylko jeśli wykryto problemy)
───────────────────────────────────────────────────────────────
- Opis PR wspomina X, ale diff zawiera też Y (niezwiązane?)
- Commit messages mało opisowe — cel zrekonstruowany głównie z kodu
- Brak linked issue / opisu "dlaczego" — ocena celu mniej pewna

───────────────────────────────────────────────────────────────
🔴 BLOCKERS
───────────────────────────────────────────────────────────────
[file:linia] <kategoria> — <issue>
  agent: <który zgłosił>
  sugestia: <suggestion>

───────────────────────────────────────────────────────────────
🟡 MAJOR
───────────────────────────────────────────────────────────────
...

───────────────────────────────────────────────────────────────
🔵 MINOR / NITS
───────────────────────────────────────────────────────────────
...

───────────────────────────────────────────────────────────────
📏 ZGODNOŚĆ Z RULES.MD  (tylko jeśli rules.md istnieje)
───────────────────────────────────────────────────────────────
Złamane:
- [reguła] — [file:linia] — <issue> (agent: <który>)
Spełnione / brak naruszeń w sprawdzonych obszarach:
- [reguła lub obszar]

───────────────────────────────────────────────────────────────
🔗 CROSS-PACKAGE ISSUES  (tylko tryb podzielony)
───────────────────────────────────────────────────────────────
...

───────────────────────────────────────────────────────────────
⚖️ ROZBIEŻNOŚCI / DECYZJE ORCHESTRATORA
───────────────────────────────────────────────────────────────
- <opis różnicy zdań, moja decyzja, uzasadnienie>

───────────────────────────────────────────────────────────────
✅ CO DZIAŁA DOBRZE
───────────────────────────────────────────────────────────────
- ...

───────────────────────────────────────────────────────────────
❓ PYTANIA DO AUTORA
───────────────────────────────────────────────────────────────
- ...

───────────────────────────────────────────────────────────────
🤖 UŻYCI AGENCI
───────────────────────────────────────────────────────────────
- tech-lead-advisor — prompt: agents/tech-lead-agent.md; dispatch: <...>; scope: <...>
- security-auditor — prompt: agents/codebase-auditor.md; dispatch: <...>; scope: <...>
- ui-reviewer — prompt: agents/ui-reviewer.md; dispatch: <...>; <użyty dla paczek [...] | pominięty: brak UI>
```


## Terminal state

Skill kończy się po syntezie wszystkich aktywnych perspektyw i zwróceniu jednego
werdyktu. To punkt domknięcia review: przy `approve` / `approve_with_comments`
można przejść do `ship`; przy `request_changes` / `block` wróć do pętli poprawek. Komendę wyrenderuj w składni aktywnego harnessu.
