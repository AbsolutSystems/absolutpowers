---
name: constitution
description: >
  Tworzy lub aktualizuje `absolutpowers/constitution.md` — zestaw wersjonowanych artykułów-pryncypiów
  projektu (niezmienniki, wartości, granice decyzyjne). Świadoma ceremonia ratyfikacji, nie efekt
  uboczny skanu. Auto-wykrywa tryb Bootstrap (brak pliku) lub Amend (plik istnieje).
  TRIGGER when: pryncypia projektu, konstytucja projektu, ratyfikacja, niezmienniki,
  wartości projektu, "ustal pryncypia", "zaktualizuj konstytucję", "dodaj artykuł",
  "amendment", "amend constitution".
  NIE wyzwalaj na: reguły mechaniczne lint-level, constrainty review, wzorce kodu — to należy do
  `update-ai-context` (Faza 3 → `absolutpowers/rules.md`).
---

# Constitution — Pryncypia projektu jako pierwszorzędna ceremonia

Pryncypia projektu to nie reguły mechaniczne. Są to **niezmienniki i heurystyki decyzyjne** —
"optymalizujemy czytelność ponad spryt", "zero breaking changes API bez ADR",
"multi-tenancy to granica bezpieczeństwa, nigdy obejście". Ten skill tworzy i utrzymuje
`absolutpowers/constitution.md` jako ratyfikowany, wersjonowany kontrakt nadrzędny pipeline'u.

## Granica (TWARDA — nie przekraczaj)

**Konstytucja = pryncypia/osąd.** Mechanika = `rules.md` / `update-ai-context`.

- Pryncypium: "Nigdy nie łączymy warstw domenowych bez ADR" (osąd, WHY, rzadka zmiana).
- Reguła mechaniczna: "Kontrolery dziedziczą po BaseController" (mechanika, HOW, derywat kodu).

Jeśli użytkownik prosi o dodanie reguły mechanicznej — odmów i przekieruj do `update-ai-context`.
Pryncypium rodzi reguły, ale to dwa osobne pliki.

**vs `update-ai-context`:** `update-ai-context` skanuje kod i proponuje reguły mechaniczne
(`absolutpowers/rules.md`) jako derywat skanu. `constitution` jest ceremonią ratyfikacji
pryncypiów strategicznych — źródłem są decyzje architekta, nie skan kodu. Nigdy nie scalaj
tych dwóch plików — mają dwie prędkości zmian i dwie natury.

## Pozycja w pipeline

Konstytucja to **kontrakt nadrzędny**:
- `generate-tasks` i `implement` czytają `absolutpowers/constitution.md` jako wiążący kontekst.
- `review` egzekwuje pryncypia jako osobny check (sekcja "Pryncypia — constitution").
- `feature-discuss` czyta konstytucję jako lekki kontekst, by rozwiązanie respektowało pryncypia od początku.

## Wykrywanie trybu

Sprawdź czy plik `absolutpowers/constitution.md` istnieje:
- **Nie istnieje** → **Bootstrap** (skan kodu jako materiał + dyskusja z architektem → propozycja artykułów)
- **Istnieje** → **Amend** (audyt artykułów względem kodu + propozycja zmian)

Utwórz katalog `absolutpowers/` jeśli nie istnieje.

---

## TRYB BOOTSTRAP

### Krok 1: Skan kodu jako materiał

Przeskanuj projekt, żeby zebrać materiał do propozycji artykułów. Skup się na:
- Wzorcach architektonicznych (warstwy, granice modułów, zależności)
- Kluczowych ograniczeniach (bezpieczeństwo, wielodostępność, API publiczne)
- Powtarzalnych decyzjach projektowych (konwencje, which-library)
- Historiach w `git log` — jakie problemy były wielokrotnie naprawiane?

Skan to **materiał**, nie źródło pryncypiów. Artykuły rodzą się z potwierdzenia architekta.

### Krok 2: Dyskusja z architektem

Na podstawie skanu przedstaw użytkownikowi:
1. Zaobserwowane wzorce i ograniczenia, które mogą być pryncypiami.
2. Pytania otwarte: "Czy czytelność ponad spryt to dla Ciebie artykuł, czy oczywistość?"
3. Propozycję listy artykułów (nazwa + draft normy) — max 5–8 artykułów na start.

Każdy artykuł musi mieć realne uzasadnienie — nie "dobra praktyka", lecz "dlatego że w tym
projekcie X powodowało Y". Bez uzasadnienia artykuł jest ozdobą.

### Krok 3: Propozycja konstytucji

Po potwierdzeniu artykułów przez użytkownika przygotuj draft pliku (patrz Format poniżej).

**Wymagane zatwierdzenie:** Pokaż cały draft użytkownikowi i czekaj na jawną akceptację.
Sformułowanie: "Oto propozycja konstytucji — przejrzyj i powiedz co zmienić. Zapiszę po Twojej akceptacji."

Nie zapisuj pliku bez jawnej akceptacji użytkownika.

### Krok 4: Zapis

Po akceptacji zapisz `absolutpowers/constitution.md` z wersją `1.0.0` i datą ratyfikacji.

---

## TRYB AMEND

### Krok 1: Wczytaj aktualną konstytucję

Przeczytaj `absolutpowers/constitution.md`. Zanotuj aktualną wersję i wszystkie artykuły.

### Krok 2: Audyt artykułów względem kodu

Dla każdego artykułu sprawdź:
1. **Czy norma jest przestrzegana w kodzie?** (Grep/Glob/Read)
2. **Czy artykuł jest martwy?** (systematyczne naruszenia bez naprawy = prawdopodobnie cel się zmienił)
3. **Czy kod wymagałby naprawy?** (naruszenia są incydentalne = artykuł aktualny, kod do poprawienia)

Klasyfikuj per artykuł:
- `aktywny` — norma przestrzegana
- `martwy` — systematyczne naruszenia (artykuł do archiwizacji lub rewizji)
- `naruszony-incydentalnie` — kod wymaga korekty, artykuł aktualny

### Krok 3: Zbierz propozycje zmian

Zbierz od użytkownika:
- Nowe artykuły do dodania
- Artykuły do zarchiwizowania lub rewizji
- Wnioski z audytu (krok 2)

### Krok 4: Propozycja zmienionych artykułów

Przygotuj diff artykułów. Pokaż użytkownikowi co się zmienia i czekaj na akceptację.

**Wymagane zatwierdzenie.** Nie auto-nadpisuj konstytucji. Sformułowanie:
"Oto proponowane zmiany — przejrzyj i powiedz co zmienić. Zaktualizuję po Twojej akceptacji."

### Krok 5: Aktualizacja po akceptacji

Po akceptacji:
1. Oblicz nową wersję semver (patrz Semver poniżej).
2. Zaktualizuj artykuły.
3. Zaktualizuj nagłówek (`Wersja`, `Ratyfikowano`).
4. Dopisz linię do `## Changelog`.
5. Zapisz plik.

---

## Format `absolutpowers/constitution.md`

```markdown
# Konstytucja projektu — {nazwa}
> Wersja: X.Y.Z · Ratyfikowano: YYYY-MM-DD · Egzekwowana przez: feature-discuss, generate-tasks, implement, review

## Artykuł I: {Nazwa pryncypium}
**Norma:** {MUST/SHOULD/NEVER ...}
**Dlaczego:** {uzasadnienie — konkretna przyczyna w kontekście tego projektu}
**Jak stosować:** {konkret w kontekście pipeline — np. "generate-tasks powinien odrzucić zadanie X jeśli…"}
**Przykład:** {opcjonalnie — kod, sytuacja, kontrprzykład}

## Artykuł II: {Nazwa pryncypium}
...

## Changelog
- X.Y.Z (YYYY-MM-DD): {opis zmiany}
- 1.0.0 (YYYY-MM-DD): Ratyfikacja pierwsza
```

### Reguły semver

- **Major** (X.0.0): usunięcie artykułu lub zmiana normy niekompatybilna (MUST → SHOULD, NEVER zniesione).
- **Minor** (0.Y.0): nowy artykuł.
- **Patch** (0.0.Z): rewizja sformułowania bez zmiany normy, korekta przykładu, klaryfikacja.

Zawsze aktualizuj `Ratyfikowano` i dopisuj linię changelog.

### Numeracja artykułów

Nowe artykuły dostają kolejny numer (I, II, III…). Usunięte artykuły nie są renumerowane —
archiwizuj je jako `## Artykuł N: [ARCHIWUM] {nazwa}` z datą archiwizacji, by changelog był
spójny z historią.

---

## Scope creep guard

Jeśli w trakcie ceremonii łapiesz się na którejś myśli — STOP:
- "Dopiszę regułę 'kontrolery dziedziczą po BaseController'" → to `update-ai-context` / `rules.md`.
- "Generuję automatycznie rules.md z artykułów" → out of scope; pryncypia *rodzą* reguły, ale to ręczna decyzja.
- "Nadpisuję bez pytania" → ratyfikacja wymaga jawnej akceptacji; nigdy auto-overwrite.
- "Piszę o tym jak zaimplementować feature" → to `generate-tasks` / `feature-discuss`.

---

## Przykład artykułu (wzorzec)

```markdown
## Artykuł III: Granice multi-tenancy
**Norma:** NEVER obchodź izolację tenantów — każda operacja na danych MUST walidować tenant_id.
**Dlaczego:** Wyciek danych między tenantami to naruszenie bezpieczeństwa i zaufania.
  Jedna pominięta walidacja kompromituje całą architekturę.
**Jak stosować:** generate-tasks odrzuca zadania, które modyfikują zapytania DB bez tenant_id;
  review flaguje każde nowe zapytanie bez klauzuli tenantowej.
**Przykład:** `SELECT * FROM orders WHERE id = ?` → NARUSZENIE.
  `SELECT * FROM orders WHERE id = ? AND tenant_id = ?` → OK.
```

---

## Begin

1. Sprawdź czy `absolutpowers/constitution.md` istnieje → ustal tryb.
2. Utwórz `absolutpowers/` jeśli nie istnieje.
3. Wykonaj kroki zgodnie z trybem Bootstrap lub Amend.
4. Każda zmiana wymaga jawnej akceptacji użytkownika przed zapisem.
5. Po zapisie poinformuj użytkownika o nowej wersji i dacie ratyfikacji.
