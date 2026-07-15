---
name: try-learn-skill
description: >
  Skanuje CAŁY codebase projektu docelowego w poszukiwaniu powtarzalnych,
  NIEOCZYWISTYCH procedur (wzorzec występuje ≥3 razy w kodzie, z dowodem
  `file:line`) i proponuje je jako reużywalne learned-skille specyficzne dla
  tego projektu. Prezentuje listę kandydatów naraz (batch), zapisuje WYŁĄCZNIE
  zaznaczone przez użytkownika do learned path per harness (patrz tabela wyjść).
  Pomija kolizje ze statycznymi skillami. Odpalany ad-hoc, świadomie.
  TRIGGER when: "przeskanuj projekt pod skille", "wyciągnij reużywalne procedury",
  "zbuduj learned-skille z codebase", "try-learn-skill", "extract project skills",
  "jakie powtarzalne procedury ma ten projekt".
  NIE wyzwalaj na: pasywne patterns/rules/CLAUDE (to `update-ai-context`); docs modułu (to `document-feature`/`document-module`).
allowed-tools: Read, Glob, Grep, Bash(git:*), Write(**/.claude/skills/learned/**/*.md), Write(**/.agents/skills/learned/**/*.md), Write(**/.grok/skills/learned/**/*.md), Write(**/.pi/skills/learned/**/*.md)
argument-hint: "[opcjonalnie: ścieżka zawężająca skan (domyślnie cały codebase); opcjonalnie próg N (domyślnie 3)]"
---

# Try Learn Skill — Skan codebase → reużywalne learned-skille projektu

Jesteś inżynierem-mentorem o WYSOKIM progu wybredności. Twoim zadaniem jest
przeskanować **cały codebase projektu docelowego** i znaleźć **powtarzalne,
nieoczywiste procedury**, które warto utrwalić jako wywoływalne learned-skille
specyficzne dla tego projektu.

**Źródło sygnału to POWTARZALNOŚĆ W KODZIE, nie pojedynczy feature.** Skill nie
patrzy na artefakty jednego zadania (planning/tasks/diff) — patrzy na to, co w
projekcie robi się WIELOKROTNIE w ten sam sposób. Wzorzec, który występuje raz,
to nie procedura projektu — to jednorazowa robota. Dopiero **≥3 wystąpienia**
(próg domyślny, patrz niżej) tego samego proceduralnego wzorca, z konkretnym
dowodem `file:line`, są sygnałem, że warto zakodować "tak SIĘ ROBI X w tym
projekcie".

**ODWRÓCONA DOMYŚLNA: dla większości skanów poprawny wynik to KRÓTKA lista
albo BRAK kandydatów.** Nie szukaj procedury na siłę — szukaj powodu, żeby jej
NIE zapisywać, i proponuj tylko te, które przejdą i próg powtarzalności, i test
nieoczywistości. "Nic nie spełnia progu" to poprawny, uczciwy wynik.

**To NIE jest implementacja.** Nie piszesz kodu produktu. Zapisujesz co najwyżej
pliki `SKILL.md` w **learned path aktywnego harnessu** — i to WYŁĄCZNIE te, które
użytkownik zaznaczy w batch approval (patrz KROK 5).

## Ścieżki wyjścia per harness

Ustal harness z kontekstu sesji (narzędzia / env / jak załadowano plugin). Zapisz learned-skille tylko do **jednej** ścieżki:

| Harness | Learned path (w TARGET projekcie) |
|---------|-------------------------------------|
| Claude Code | `.claude/skills/learned/{name}/SKILL.md` |
| Codex | `.agents/skills/learned/{name}/SKILL.md` |
| Grok | `.grok/skills/learned/{name}/SKILL.md` |
| Pi | `.pi/skills/learned/{name}/SKILL.md` |

Jeśli harness niejasny — domyślnie `.claude/skills/learned/` i **powiedz to użytkownikowi**.
Glob istniejących learned: wszystkie powyższe wzorce przy collision-check.

## Wejście

Argument `$ARGUMENTS` (oba opcjonalne):
- **ścieżka** zawężająca skan (np. `src/payments/`) — domyślnie **cały codebase** projektu.
- **próg N** — minimalna liczba wystąpień wzorca, domyślnie **3**. Możesz podać inną (np. `--min=4`), ale domyślną jest 3.

$ARGUMENTS

## Granica vs `update-ai-context` (przeczytaj, zanim zaczniesz)

Oba skille skanują codebase — ale mają **różny cel i różny artefakt**. Nie
powielaj tu roboty `update-ai-context`:

- **`update-ai-context` → pasywna DOKUMENTACJA.** Produkuje `patterns.md`,
  `rules.md`, `CLAUDE.md` — opis "tak wygląda ten projekt" (wzorce, konwencje,
  reguły), czytany **biernie jako tło** przez agenta. Odpowiada na pytanie
  *"jaki jest ten projekt?"*.
- **`try-learn-skill` → aktywne, WYWOŁYWALNE procedury.** Produkuje learned-skille
  w `.claude/skills/learned/` — "tak SIĘ ROBI powtarzalną procedurę X w tym
  projekcie", które agent **odpala** jako narzędzie. Odpowiada na pytanie
  *"jak wykonać powtarzalne zadanie klasy X tak, jak robi się to tutaj?"*.

Jeśli wykryty wzorzec to opis stanu/konwencji (pasywne tło) → to należy do
`update-ai-context`, NIE tutaj. Tutaj kwalifikuje się tylko **proceduralna
sekwencja kroków**, którą da się odpalić.

---

## KROK 1: Skan codebase — znajdź powtarzalne wzorce proceduralne

Przeskanuj codebase (w zakresie z argumentu, domyślnie cały) szukając
**proceduralnych wzorców** — sekwencji kroków/struktury, która powtarza się w
wielu miejscach kodu. Użyj Glob/Grep do wykrycia rodzin plików robiących to samo
strukturalnie, np.:
- rodziny plików o tej samej roli (kontrolery, repozytoria, migracje, handlery,
  serializery, komendy, testy integracyjne o tym samym kształcie),
- powtarzalne sekwencje wywołań/adnotacji/konfiguracji,
- konwencjonalne "przepisy" na dodanie nowego elementu danej klasy.

Zbierz kandydatów-wzorce. Dla KAŻDEGO zbierz **konkretne wystąpienia z dowodem
`file:line`** — to jest twarda waluta tego skilla, nie ogólnik.

## KROK 2: Próg powtarzalności (twarda bramka #1)

Dla każdego wzorca policz wystąpienia z dowodem `file:line`:
- **≥ N wystąpień** (N domyślnie **3**) → przechodzi próg, kontynuuj do KROKU 3.
- **< N** → odrzuć jako kandydata na skill (to jeszcze nie procedura projektu,
  za mało dowodu powtarzalności).

**Dowód liczony rygorystycznie, nie z surowych trafień grepa.** Trafienie
prymitywu (`<Dialog` w 15 plikach) samo w sobie NIE jest wystąpieniem procedury.
Wystąpienie = miejsce, dla którego potrafisz powiedzieć: *"tu wykonano procedurę
klasy X — te same kroki, ta sama struktura"*. Każde wystąpienie ma konkretny
`file:line`.

## KROK 3: Test nieoczywistości (twarda bramka #2)

Powtarzalność to za mało — powtarzalna procedura może być oczywista (agent zrobi
ją sam). Learned-skill musi kodować wiedzę, której agent NIE ma z siebie.

**3A. Wypisz kroki procedury**, oznacz każdy `OCZYWISTY` / `NIEOCZYWISTY`:
- `OCZYWISTY` — senior/agent wykonałby sam ("utwórz serwis", "dodaj test").
- `NIEOCZYWISTY` — koduje coś nienaturalnego: wymuszoną kolejność ("X PRZED Y,
  bo inaczej Z"), pułapkę stacka/projektu, decyzję którą model bez tej wiedzy
  podjąłby źle, warunek brzegowy odkryty bólem.

**3B. Podmień rzeczowniki:** wykreśl nazwy plików/pól/encji konkretnych
wystąpień. Kroki, które po podmianie tracą sens, to część wystąpień, nie
procedury.

**3C. Bramka:** policz kroki `NIEOCZYWISTE`, które przetrwały podmianę:
- **≥2** → jest esencja skilla. Kontynuuj (KROK 4).
- **<2** → to nie materiał na skill (choćby powtarzalne i ogólne). Odrzuć.

### Antyprzykłady kalibracyjne
- ❌ **"Dodanie endpointu CRUD: model → serwis → kontroler → testy"** —
  powtarzalne, ale zero nieoczywistości. Agent zrobi sam. SKIP.
- ❌ **"Wszystkie repozytoria rozszerzają BaseRepo"** — to konwencja/stan
  (pasywne tło) → `update-ai-context`, nie skill.
- ✅ **"Migracja pola pod `SecureRepository`: najpierw migracja danych z
  wyłączonym listenerem, potem zmiana modelu, na końcu reindeks — w tej
  kolejności, bo SecureData szyfruje kolumnę przy starcie"** — powtarza się w
  kilku migracjach (≥3 `file:line`) + ≥2 nieoczywiste wymuszone kroki. Materiał.

## KROK 4: Collision-check i NEW vs UPDATE

Dla każdego wzorca, który przeszedł oba progi:

- **Collision-check vs skille STATYCZNE** (feature-discuss, generate-tasks,
  implement, review, triada-review, debug, problem-discuss, update-ai-context,
  document-feature, document-module, explain, ship, constitution, analyze,
  preboot…): jeśli statyczny skill już pokrywa ten zakres → **SKIP**, zaraportuj
  "to już robi skill X", nie proponuj.
- **Porównanie z istniejącymi learned-skillami**
  (`Glob` po ścieżkach z tabeli harness + legacy `.claude/…`): podobny istnieje →
  kandydat **UPDATE**; brak → **NEW**.

Zbuduj z ocalałych wzorców **listę kandydatów** do batch approval.

## KROK 5: Batch approval — jeden przebieg, człowiek zaznacza

Jeśli po KROKACH 2–4 **nie został żaden kandydat** → zaraportuj wprost "skan nie
znalazł wzorca spełniającego próg ≥N wystąpień i test nieoczywistości" (z krótkim
uzasadnieniem, np. co odpadło i dlaczego) i **zakończ BEZ zapisu jakiegokolwiek
pliku**. To poprawny wynik, nie porażka.

Jeśli są kandydaci — pokaż **CAŁĄ listę naraz** (batch), po jednym bloku na
kandydata:
```
[ ] {n}. learned-{kebab}  (NEW|UPDATE)
    Klasa: [jedno zdanie — klasa zadań]
    Nieoczywiste: [esencja z KROKU 3]
    Dowód (≥N wystąpień): file:line, file:line, file:line
    TRIGGER when: [wąski trigger]
```

**CZEKAJ NA WYBÓR UŻYTKOWNIKA.** Użytkownik zaznacza, które pozycje zapisać
(np. "1, 3", "wszystkie", "żadne"). **Zapisujesz WYŁĄCZNIE zaznaczone** — human
gate PRZED każdym zapisem jest twardy, nie ma ścieżki cichego zapisu. Użytkownik
może skorygować treść/trigger kandydata przed zapisem.

Dla każdego zaznaczonego:
```
{target-project}/{learned-root}/learned/{name}/SKILL.md
```
(`{learned-root}` z tabeli harness, np. `.claude/skills`, `.agents/skills`, …)
- Utwórz katalog jeśli nie istnieje.
- `name` z prefiksem `learned-`, kebab-case.
- **Write w TARGET projekcie**, NIE w repo AbsolutPowers.
- Wygeneruj treść wg szablonu niżej.

---

## Format generowanego learned `SKILL.md`

Skill MUSI generować dokładnie taki szablon:

```markdown
---
name: learned-{descriptive-kebab}
description: >
  [Jednozdaniowy cel procedury.]
  TRIGGER when: [WĄSKIE, precyzyjne sygnały — patrz reguła niżej].
allowed-tools: [scoped, np. Read, Glob, Grep, Edit, Bash(...)]
argument-hint: "[opcjonalnie]"
---

<!-- learned-meta
origin: learned
source: codebase-scan
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
occurrences: N (liczba znalezionych wystąpień w kodzie)
evidence: file:line, file:line, file:line
-->

# [Tytuł procedury]

## Kiedy używać
[Klasa zadań, dla której to działa.]

## Procedura
1. [Krok — narzędzie, decyzja, odwołanie do pliku/wzorca projektu]
2. ...

## Pułapki / uwagi
- [Nieoczywiste elementy z KROKU 3 — to jest jądro wartości skilla]

## Wystąpienia w kodzie (dowód)
- `file:line` — [czym różni się to wystąpienie / parametry klasy]
```

### Reguła: blok metadanych w CIELE, nie we frontmatter
`learned-meta` MUSI być komentarzem HTML w **ciele** pliku (zaraz po
frontmatter), NIE polem YAML frontmatter — unik ryzyka, że loader Claude Code
odrzuci nieznane pola. Pola: `origin`, `source: codebase-scan`, `created`,
`last-updated`, `occurrences` (N), `evidence` (lista `file:line`).

### Reguła: WĄSKI `TRIGGER when:`
Egzekwuj precyzyjny, wąski trigger w `description`. Learned-skill ładuje się
przez auto-detekcję — zbyt szeroki trigger powoduje retrieval-collision. Trigger
celuje w konkretną klasę zadań, nie ogólne słowa.

### Frontmatter per harness
- **Claude:** możesz dołączyć `allowed-tools` / `argument-hint`.
- **Codex / Pi / Grok:** generuj learned-skille **BEZ** tych pól — reszta szablonu (w tym `learned-meta`) identyczna.

---

## Zasady

- **Powtarzalność jest źródłem, nie feature.** Sygnał to ≥N wystąpień w kodzie z
  dowodem `file:line` — nie pojedynczy diff. To wprost zabija jednorazowce.
- **Dwie twarde bramki:** próg powtarzalności (≥N, KROK 2) ORAZ nieoczywistość
  (≥2 elementy po podmianie rzeczowników, KROK 3). Obie muszą przejść.
- **Kandydat ≠ trafienie grepa:** każde wystąpienie ma konkretny `file:line` i
  jest realnym wykonaniem procedury, nie trafieniem prymitywu.
- **Granica vs update-ai-context:** pasywna dokumentacja (stan/konwencje) → tam;
  aktywna wywoływalna procedura → tutaj. Nie powielaj.
- **SKIP > duplikat:** kolizja ze statycznym skillem → pomiń.
- **Batch approval, human gate twardy:** zapisujesz WYŁĄCZNIE pozycje zaznaczone
  przez użytkownika; brak ścieżki cichego zapisu SKILL.md.
- **Brak kandydatów = poprawny wynik:** gdy nic nie przejdzie progów, raportuj i
  kończ bez zapisu — nie forsuj ekstrakcji.
- **Write tylko do learned path aktywnego harnessu** w target-projekcie (tabela wyżej).
