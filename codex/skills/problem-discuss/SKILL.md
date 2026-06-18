---
name: problem-discuss
description: >
  Intake i triage wieloelementowego zgłoszenia domenowego od klienta/stakeholdera.
  Rozbija zgłoszenie na sprawy, ustala regułę biznesową per sprawa, konfrontuje z kodem,
  klasyfikuje (bug / gap / config / dane / nieporozumienie / brak danych) i kieruje dalej.
  Breadth-first dochodzenie — NIE naprawia, NIE planuje, NIE pisze taskow.
  TRIGGER when: zgłoszenie klienta, "klient zgłosił", "klient napisał", wieloelementowa lista uwag,
  uwagi z produkcji, rozbieżność reguła-biznesowa↔produkcja, "po X powinno Y a nie ma",
  "weryfikacja zgłoszenia", "wpłynęło zgłoszenie", lista spraw do wyjaśnienia od klienta.
  NIE wyzwalaj na: czysty error/stack trace/test fail/CI fail (to `debug`) ani na prośbę o nowy
  feature (to `feature-discuss`).
---

# Problem Discussion — Intake & Triage zgłoszeń

Wieloelementowe zgłoszenie od klienta to nie jest jeszcze bug ani feature. To **surowy sygnał**,
który trzeba rozłożyć, zrozumieć i sklasyfikować, zanim ktokolwiek zacznie kopać w kodzie albo
projektować rozwiązanie. Ten skill jest **wejściem rozpoznawczym** pipeline'u.

## Granica (TWARDA — nie przekraczaj)

Ten skill **rozpoznaje i kieruje**. NIE:
- nie naprawia kodu (potwierdzony bug → `debug`),
- nie planuje rozwiązania (gap featurowy → `feature-discuss`),
- nie pisze taskow (`generate-tasks`),
- nie implementuje.

Produkt = **raport z analizą + klasyfikacją per sprawa + rekomendowaną ścieżką**. Koniec na routingu.
Jeśli łapiesz się na pisaniu fixa albo planu — STOP, to już inny skill.

## Pozycja w pipeline

```
                 ┌─ problem-discuss (mgliste zgłoszenie klienta, wiele spraw)
wejścia ─────────┤      │  klasyfikuje i kieruje per sprawa ↓
                 │      ├─ bug            → debug
                 │      ├─ gap featurowy  → feature-discuss → generate-tasks → implement
                 │      ├─ config / dane  → fix bezpośredni
                 │      └─ nieporozumienie → close (brak zmiany w kodzie)
                 ├─ feature-discuss (jasny nowy feature)
                 └─ debug (jasny bug: error / stack trace / test fail)
```

**vs `debug`:** `debug` zakłada znany failure i robi **głębokie** single root-cause z testowaniem
hipotez. `problem-discuss` jest **wszerz** — wiele spraw naraz, gdzie nie wiadomo jeszcze czy
którakolwiek to bug. Potwierdzony bug oddajesz do `debug`.

**vs `feature-discuss`:** `feature-discuss` jest **do przodu** (projektuje nowy X). Tu funkcja
rzekomo już istnieje i ma działać — patrzysz **wstecz** na rozbieżność reguła↔rzeczywistość.

## Context Files

Zanim zaczniesz, wczytaj (jeśli istnieją):
- **`./absolutpowers/project-memory.md`** — trwałe pułapki, znaki ostrzegawcze, obejścia.
  Używaj tylko wpisów `Status: active`. Pomijaj `superseded` / `archived`.
- **`./absolutpowers/rules.md`** — reguły projektu (mogą definiować oczekiwane zachowanie).
- **`./absolutpowers/patterns.md`** — wzorce kodu (gdzie szukać flow).
- **`AGENTS.md`** (`## Project Structure`) — mapa modułów, by przypisać sprawy do modułów.

Pamięć to kontekst, nie dowód. Gdy pamięć kłóci się z aktualnym kodem — ufaj kodowi.

## Faza 0: Dekompozycja zgłoszenia

Jeden mail/zgłoszenie = zwykle **N osobnych spraw**. Najpierw rozłóż.

1. Przeczytaj całe zgłoszenie. Wypisz sprawy jako numerowaną listę 1..N.
2. Każda sprawa = jedna rozbieżność/pytanie. Nie łącz dwóch problemów w jeden punkt.
3. Zmapuj **załączniki** (obrazy, pliki, zrzuty) do spraw — który dowód dotyczy której sprawy.
4. Pokaż użytkownikowi rozbicie i potwierdź, że nic nie zgubiłeś, zanim ruszysz dalej.

> Przykład: "po akceptacji korekty powinny wyjść 2 maile, nie widzę ich" = JEDNA sprawa
> z dwoma oczekiwanymi efektami; "dlaczego user X dostaje maile" = DRUGA, osobna sprawa.

## Faza 1: Per sprawa — reguła (kontrakt) + rozbieżność

Dla KAŻDEJ sprawy ustal dwie rzeczy, rozdzielnie:

1. **Reguła oczekiwana (intended behavior, WG KLIENTA)** — co według klienta/reguły biznesowej
   ma się dziać. Cytuj klienta. To kontrakt tej sprawy. Jeśli klient nie podał reguły wprost —
   wydobądź ją pytaniem, nie zgaduj.
2. **Stan faktyczny / zgłoszenie** — co klient zaobserwował (brak maila, zły adresat, zła wartość).

**Czytaj załączniki jako dowód.** Otwórz każdy załącznik (obraz/plik) przypisany do sprawy
i wyciągnij konkret (kto, kiedy, jaka wartość, jaki ekran). Nie opisuj załącznika ogólnikowo —
wyciągnij fakt, który rozstrzyga sprawę.

Jeśli reguła jest niejednoznaczna lub sprzeczna z `rules.md` — to sygnał do klasyfikacji
"nieporozumienie" albo "brak danych", nie do zgadywania.

## Faza 2: Dochodzenie w kodzie (analiza, NIE fix)

Dla każdej sprawy potwierdź lub obal regułę względem kodu:

1. **Znajdź flow.** Przejdź ścieżkę od zdarzenia do oczekiwanego efektu
   (np. korekta → akceptacja → trigger maila → wysyłka).
2. **Znajdź punkt, w którym efekt powinien powstać.** Czy w ogóle istnieje kod, który ma
   wyprodukować to zachowanie? Zacytuj `path/to/file:line`.
3. **Trace wstecz przy cichej rozbieżności.** Brak efektu (np. mail nie wyszedł) zwykle nie
   ma erroru. Idź wstecz: gdzie jest warunek wysyłki? jaki warunek go blokuje? czy dane go
   spełniają? (lekki wariant techniki trace z `debug` — bez naprawiania).
4. **Nie naprawiaj.** Zbierasz dowód do klasyfikacji, nie wprowadzasz zmian.

Każda konkluzja musi mieć dowód: `file:line` z kodu i/lub fakt z załącznika. Bez dowodu →
klasyfikacja "brak danych".

## Faza 3: Klasyfikacja per sprawa

Przypisz każdej sprawie dokładnie jeden kubełek:

| Kubełek | Znaczenie | Ścieżka |
|---|---|---|
| **potwierdzony bug** | kod ma realizować regułę, ale jej nie realizuje | `debug` |
| **nie zaimplementowane (gap)** | reguła nigdy nie została zbudowana | `feature-discuss` |
| **błąd konfiguracji / env** | kod OK, zła konfiguracja/zmienna/feature flag/dane środowiska | fix bezpośredni |
| **anomalia danych** | kod OK, konkretne dane w bazie/wejściu są nieprawidłowe | fix danych / dochodzenie danych |
| **działa-jak-zaprojektowano** | kod realizuje regułę, klient ma złe oczekiwanie/nieporozumienie | close + wyjaśnienie klientowi |
| **za mało danych** | nie da się rozstrzygnąć bez dodatkowych informacji/dostępu | dopytaj klienta / zbierz dane |

Klasyfikuj na podstawie dowodu z Fazy 2, nie przeczucia. Jeśli wahasz się między "bug" a
"gap" — sprawdź czy kod miał kiedykolwiek realizować regułę (bug = miał i nie działa; gap = nigdy nie było).

## Faza 4: Zapis raportu

Zapisz `absolutpowers/problem/problem-{slug}.md` (`{slug}` z tytułu zgłoszenia). Utwórz katalog
`absolutpowers/problem/` jeśli nie istnieje.

```markdown
# Problem Report — {tytuł zgłoszenia}

## Źródło
- Klient / kanał: ...
- Data zgłoszenia: YYYY-MM-DD
- Załączniki: {lista plików/obrazów}

## Sprawa 1 — {krótki tytuł}
- **Reguła oczekiwana (wg klienta):** ...
- **Stan faktyczny / zgłoszenie:** ...
- **Dowód:** `path/to/file:line`; załącznik {nazwa} → {wyciągnięty fakt}
- **Klasyfikacja:** potwierdzony bug | gap | config | dane | nieporozumienie | brak danych
- **Uzasadnienie:** dlaczego ten kubełek (1-2 zdania, oparte na dowodzie)
- **Rekomendowana ścieżka:** debug | feature-discuss | fix bezpośredni | fix danych | close | dopytaj
- **Co przekazać dalej:** {konkret dla następnego kroku — np. "debug: mail blokowany warunkiem X w PaymentService:142"}

## Sprawa 2 — {krótki tytuł}
...

## Podsumowanie / routing

| # | Sprawa | Klasyfikacja | Ścieżka |
|---|--------|--------------|---------|
| 1 | ...    | ...          | ...     |
| 2 | ...    | ...          | ...     |
```

## Faza 5: Routing / handoff (fan-out)

Jedno zgłoszenie rozsypuje się na wiele ścieżek. Po zapisie raportu, w odpowiedzi do
użytkownika, **zaproponuj** następny krok per sprawa (best-effort nudge, NIE wykonuj):

- potwierdzony bug → `debug` ze sprawą + dowodem `file:line`
- gap featurowy → `feature-discuss` z opisem brakującej funkcji
- config / dane → fix bezpośredni (wskaż plik/konfigurację/rekord)
- nieporozumienie → odpowiedź do klienta wyjaśniająca jak system działa (zaproponuj treść)
- brak danych → konkretne pytania/dostępy potrzebne do rozstrzygnięcia

Pogrupuj nudge wg ścieżki. Nie odpalaj kolejnych skilli automatycznie — wybór należy do użytkownika.

## Memory Capture (opcjonalnie)

Jeśli dochodzenie odsłoniło **trwałą** pułapkę (cichy warunek blokujący efekt, powtarzalny
rozjazd reguła↔kod, nieoczywiste źródło danych) — utwórz
`./absolutpowers/memory-candidates/memory-candidates-YYYY-MM-DD-{slug}.md` i zapytaj użytkownika,
czy promować do `./absolutpowers/project-memory.md`. Promocja wymaga zgody. Nie zapisuj
jednorazowych incydentów ani stanów, które się nie powtórzą.

Zapisuj lekcję **ogólnie** — przenośna klasa problemu (mechanizm) + znaki ostrzegawcze
rozpoznawalne w INNYM module; konkrety (pliki, ten incydent) tylko jako przykład, nie jako lekcja.

## Red Flags — STOP

Jeśli łapiesz się na którejś myśli — wróć do granicy skilla:
- "Od razu to naprawię" → to `debug` / fix, nie tutaj.
- "Rozpiszę jak to zbudować" → to `feature-discuss` / `generate-tasks`.
- "Klasyfikuję na czuja, bez czytania kodu" → wróć do Fazy 2, zbierz dowód.
- "Wrzucę wszystkie uwagi do jednej sprawy" → wróć do Fazy 0, rozbij.
- "Pominę załącznik, pewnie nic ważnego" → otwórz, dowód bywa właśnie tam.
