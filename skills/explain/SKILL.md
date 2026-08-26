---
name: explain
description: >
  Generuje raport HTML wyjaśniający plan lub wprowadzone zmiany (onboarding dla człowieka).
  TRIGGER when: "explain", "explain me", "opisz", "wyjaśnij", "wytłumacz",
  "co się zmieniło", "what changed", "onboarding", "podsumuj zmiany",
  "opisz plan", "explain the plan", "explain changes".
allowed-tools: Read, Glob, Grep, Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(ls:*), Bash(npx @mermaid-js/mermaid-cli:*), Write
argument-hint: "[opcjonalnie: ścieżka do dokumentu planu lub zakres np. 'ostatni feature']"
---

# Explain — Human Onboarding Report

Twoim zadaniem jest stworzenie samodzielnego pliku HTML, który ma pomóc człowiekowi (developerowi) szybko i bez wysiłku zrozumieć plan pracy lub zmiany wprowadzone w kodzie. To dokument onboardingowy — pisany dla człowieka, nie dla maszyny. Ma być narzędziem, któremu można zaufać, a nie ładnie wyglądającym podsumowaniem.

> **vs `document-module`:** `explain` jest **per-zmiana** i **ephemeralny** (snapshot planu/diffa, `docs/onboarding/*.html` z sufiksem wersji). Jeśli chcesz **trwałej dokumentacji architektury istniejącego modułu** ze skanu kodu (diagramy C4, regenerowalny HTML + markdown źródłowy) — to `document-module`.

## Krok 0: Oceń rozmiar i charakter zmiany, dobierz głębokość

Zanim cokolwiek napiszesz, oceń skalę:
- **Drobna** (1-2 pliki, fix, mała poprawka): wersja skrócona — TL;DR, mapa plików, ewentualne ryzyka, sekcja pytań/decyzji jeśli są. Bez diagramów chyba że naprawdę pomagają.
- **Średnia/duża** (feature, refaktor, zmiana architektury): pełna wersja ze wszystkimi sekcjami.

Ustal też **charakter** zmiany, bo wpływa na formę:
- **Refaktor / migracja / wymiana rozwiązania** (zmienia się coś, co już istniało) → preferuj **tabelę porównawczą „przed → po"** zamiast dwóch osobnych akapitów. To dużo czytelniejsze.
- **Nowy feature** (powstaje coś nowego) → opis narracyjny, „stan przed" może być krótki lub pominięty.

Nie rozdmuchuj raportu dla małej zmiany — fałszywa rozbudowa obniża zaufanie do dokumentu.

## Krok 1: Zbierz materiał

Zakres: $ARGUMENTS

1. Jeśli podano ścieżkę do dokumentu planu/zadań — przeczytaj go.
2. Jeśli nie podano zakresu — przeanalizuj bieżący stan: `git status`, `git log --oneline -20`, `git diff` względem głównego brancha. Ustal co się zmieniło.
3. Przejrzyj kluczowe pliki, których dotyczą zmiany, żeby zrozumieć **faktyczną implementację**, a nie tylko opis w planie.
4. Jeśli istnieją dokumenty planowania/ADR w repo — uwzględnij je.

## ZASADA NACZELNA: audytowalność

To jest najważniejsza reguła całego skilla. Przy każdej istotnej tezie czytelnik musi wiedzieć, na czym opierasz wniosek. Rozróżniaj wizualnie i językowo:
- **Zweryfikowane** — „widać w kodzie/diffie", „plik X robi Y" (sprawdziłeś to bezpośrednio).
- **Wnioskowane / założone** — „zakładam, że…", „prawdopodobnie…", „nie zweryfikowałem, ale…".

Nigdy nie pisz pewnym tonem o czymś, czego nie sprawdziłeś. Przekonująco brzmiąca konfabulacja jest gorsza niż brak dokumentu. Jeśli czegoś nie wiesz — to trafia do sekcji „Pytania i decyzje", nie do sekcji opisowych jako fakt.

## Krok 2: Sekcje raportu

Pomiń sekcje, dla których naprawdę nie ma treści (nie wymyślaj wypełniacza). Dla zmian drobnych użyj wersji skróconej z Kroku 0.

1. **TL;DR** — 3-5 zdań: co to za zmiana/plan i po co.
2. **Pytania i decyzje dla człowieka** — UMIEŚĆ TO WYSOKO, zaraz po TL;DR. Lista miejsc gdzie:
   - podjąłeś arbitralny wybór, który człowiek powinien zatwierdzić lub zakwestionować,
   - plan ma lukę albo niejednoznaczność,
   - czegoś nie udało Ci się ustalić z kodu/dokumentów,
   - coś wymaga szczególnej uwagi przy review.
   To najcenniejsza sekcja onboardingu po pracy agenta — odwraca dynamikę z „wszystko jasne" na „tu potrzebny jest człowiek". Jeśli pusta — napisz wprost „Brak otwartych kwestii".
3. **Stan przed (co było)** — krótki opis punktu wyjścia. Przy refaktorach NIE rób tu osobnego akapitu, jeśli zaraz potem idzie sekcja 4 jako tabela — połącz je w jedną tabelę porównawczą (patrz niżej).
4. **Co się zmienia / co planujemy**:
   - **Dla refaktorów/migracji**: użyj **tabeli porównawczej** z kolumnami `Aspekt | Przed | Po | Dlaczego`. Wiersze to konkretne wymiary zmiany (np. mechanizm, biblioteka, struktura pakietu, sposób konfiguracji, obsługa błędów, testowalność). Kolumna „Dlaczego" krótka — jedno zdanie. Tam gdzie warto, dorzuć pod tabelą minimalny przykład kodu przed/po dla najważniejszego wiersza.
   - **Dla nowych feature'ów**: opis narracyjny z odniesieniem do plików i komponentów.
   - W obu przypadkach oznaczaj zweryfikowane vs wnioskowane.
5. **Diagram(y) architektury** — Mermaid przez CDN. Pokaż przepływ danych / relacje komponentów / sekwencję dla kluczowego scenariusza. Przy zmianie architektury — dwa diagramy „przed" i „po" obok siebie lub pod sobą, ta sama konwencja w obu, żeby różnica była widoczna na pierwszy rzut oka. Zasady: każdy diagram prosty (max ~15 węzłów); rozbij złożoność na kilka mniejszych zamiast jednego molocha.
6. **Wybrane rozwiązania i uzasadnienie** — dla każdej istotnej decyzji: co wybraliśmy → dlaczego (trade-offy) → jakie alternatywy odrzucono i czemu. (Przy refaktorze nie powtarzaj tego, co już jest w kolumnie „Dlaczego" tabeli — tu rozwijaj tylko decyzje wymagające szerszego uzasadnienia.)
7. **Ryzyka i otwarte kwestie** — jeśli widać: dług techniczny, założenia mogące nie być prawdziwe, brakujące testy, wpływ na wydajność/bezpieczeństwo. Oznacz poziom (wysokie/średnie/niskie) i kolorystycznie. Przy refaktorach zwróć szczególną uwagę na ryzyko regresji i zmiany zachowania (behavior parity).
8. **Mapa zmienionych plików** — lista plików z jednozdaniowym opisem roli każdego w tej zmianie.
9. **Glosariusz** (OPCJONALNIE, tylko większe zmiany) — 3-5 pojęć domenowych specyficznych dla repo. Pomiń przy drobnych zmianach.

## Krok 3: Wygeneruj i zweryfikuj diagramy

Po napisaniu każdego diagramu Mermaid sprawdź jego składnię. Jeśli dostępne jest `npx @mermaid-js/mermaid-cli`, zwaliduj nim; jeśli nie — przejdź składnię uważnie ręcznie (domknięte nawiasy, poprawne strzałki, brak niedozwolonych znaków w etykietach). Błędny diagram renderuje się jako pusty prostokąt. Lepszy prosty działający diagram niż ambitny zepsuty.

## Krok 4: Zapis pliku

- Katalog: `docs/onboarding/` (utwórz jeśli nie istnieje).
- Nazwa: `<krótki-slug-opisujący-zmianę>-<YYYY-MM-DD>.html`.
- **Idempotentność**: jeśli plik o tej nazwie już istnieje, NIE nadpisuj — dodaj sufiks `-v2`, `-v3` itd.

## Wymagania techniczne dla HTML

- Jeden samodzielny plik `.html`, działający po otwarciu w przeglądarce bez serwera.
- Mermaid przez CDN: `<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>` + `mermaid.initialize({startOnLoad:true})`.
- **CSS**: przeczytaj `skills/explain/references/report-base.css` w całości i wklej jego treść bez zmian jako pierwszy blok jedynego `<style>` w `<head>` — to reset, tokeny kolorów (jasny, `prefers-color-scheme: dark`, `[data-theme="dark"]`), typografia oraz gotowe komponenty: sekcje jako karty (`.card`), `.callout-question`/`.callout-risk-high`/`-medium`/`-low`, `.badge-verified`/`.badge-inferred`, `.table-compare` (kolumny „Przed"/„Po", zebra), `.toc`, `.report-footer` i `.scroll-x` do owijania szerokiej treści (tabel, kodu, diagramów), żeby scrollowała się sama, nie cała strona. Nie odtwarzaj tego od zera. Za wklejoną bazą dopisz w tym samym `<style>` tylko to, czego potrzebuje konkretnie ten dokument, referencjonując istniejące `var(--color-...)` — layout i dodatkowe komponenty strony pozostają otwarte, baza niczego nie wymusza.
- **Tabele porównawcze**: czytelne, z wyraźnym nagłówkiem; kolumny „Przed" i „Po" odróżnione kolorystycznie (np. subtelne tło — chłodne dla „przed", ciepłe/zielonkawe dla „po"), naprzemienne tła wierszy, responsywne (na wąskim ekranie nie rozjeżdżają się — pozwól na poziomy scroll tabeli zamiast łamania).
- Sekcja „Pytania i decyzje" oraz ryzyka — wizualnie wyróżnione (kolor, ramka).
- Zweryfikowane vs wnioskowane — odróżnij wizualnie (badge/ikona/kolor obramowania), konsekwentnie w całym dokumencie.
- Ryzyka kolorowo wg poziomu.
- Spis treści z kotwicami na górze.
- Stopka: data wygenerowania, zakres/commity, legenda oznaczeń.
- Język: polski.

## Ton

Pisz jak senior tłumaczący zmianę koledze przy kawie — zwięźle, konkretnie, bez lania wody i korpo-żargonu. Zakładaj, że czytelnik zna stack, ale nie zna szczegółów tej zmiany. Czego nie jesteś pewien — zaznacz wprost. Bez estymacji czasu.

Po wygenerowaniu pliku podaj jego ścieżkę i jednozdaniowe podsumowanie, z naciskiem na to, ile pozycji trafiło do sekcji „Pytania i decyzje".
