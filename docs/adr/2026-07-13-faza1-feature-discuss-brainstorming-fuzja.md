# ADR: Fuzja feature-discuss ← brainstorming — szkielet i rekoncyliacje (Faza 1)

## Data
2026-07-13

## Status
Accepted

## Kontekst
Faza 1 epica "fuzja mechaniki obry" wszczepia mechanikę `brainstorming` obry do `feature-discuss` metodą rewrite-to-unify (ADR wspólny: `2026-07-13-rewrite-to-unify-fuzja-obry.md`). Dwie mechaniki obry kolidują z istniejącymi mechanizmami feature-discuss i wymagają rozstrzygnięcia zanim powstaną taski:

1. Który skill jest szkieletem fuzji (baza rewrite'u)?
2. Dekompozycja obry (flaguj zbyt-duży-projekt przed pytaniami) vs istniejący tryb epica feature-discuss.
3. HARD-GATE obry (żaden kod przed zatwierdzonym designem, anty-wzorzec "too simple") vs istniejący micro-change fast-path.

## Decyzja

**1. Szkielet = feature-discuss.** Wszczepiamy mechanikę brainstorming w gotowy szkielet feature-discuss, nie odwrotnie. Powód: feature-discuss ma 583 linie gęstej, unikalnej warstwy domenowej (Tryb A/B/C, rozdział CO/JAK, Faza 0, epic main+stuby, ADR, QA-enrichment, gates), brainstorming 160 linii czystej mechaniki. Więcej do stracenia po stronie domenowej → mniejsze ryzyko i nakład przy grafcie mechaniki w domenę niż odwrotnie. To świadome odstępstwo od domyślnej hipotezy epica ("obra częściej szkielet, bo community-tested") — uzasadnione gęstością warstwy domenowej tego konkretnego skilla.

**2. Dekompozycja ROZSZERZA tryb epica (nie zastępuje).** Dekompozycja obry dostarcza *timing* — wczesny scope-check na wejściu Fazy 1, flagujący wiele-niezależnych-podsystemów ZANIM padnie pierwsze pytanie szczegółowe. Feeduje istniejącą maszynerię epica feature-discuss (detekcja w Fazie 3 → split na main+stuby → Tryb B). Obra = trigger/timing, feature-discuss = mechanizm splitu. Zero duplikacji mechanizmu.

**3. HARD-GATE rządzi AKCEPTACJĄ, nie ciężarem doca.** HARD-GATE = "brak implementacji przed **zaakceptowanym** designem", nie "przed **planning-docem**". Micro-change fast-path przeżywa jako lekka ścieżka pod tym samym gate: opis CO+GDZIE = mini-design, akceptacja użytkownika = brama spełniona, implementacja rusza bez ciężkiego doca. Anty-wzorzec "to zbyt proste" celuje w pomijanie **akceptacji**, nie w pomijanie doca.

## Rozważane alternatywy
- **Szkielet = brainstorming + wszczepienie warstwy domenowej** — odrzucone: odtwarzanie 583 linii warstwy domenowej w 160-liniowym szkielecie = większy nakład i ryzyko regresji.
- **Dekompozycja zastępuje epic** — odrzucone: obra nie zna main-doca/Trybu B; utrata warstwy domenowej splitu.
- **Pominąć dekompozycję obry** — odrzucone: traci wczesne flagowanie (feature-discuss dziś wykrywa epic dopiero w Fazie 3, po rundzie pytań).
- **HARD-GATE bezwzględny (wywalić micro-change)** — odrzucone: ciężar proceduralny na trywialnych zmianach, sprzeczny z zasadą "MNIEJ = WIĘCEJ"; feature-discuss świadomie usunął ten ciężar.
- **Micro-change omija gate (status quo)** — odrzucone: dziura w gate dokładnie tam, gdzie obra ostrzega ("simple projects = najwięcej nieprzemyślanych założeń").

## Konsekwencje
- (+) Warstwa domenowa feature-discuss zachowana w całości; mechanika obry wzmacnia bramkowanie i prezentację designu.
- (+) Micro-change fast-path i HARD-GATE współistnieją bez sprzeczności — lekka ścieżka nadal pod bramą akceptacji.
- (+) Wczesne flagowanie epica bez duplikacji mechanizmu splitu.
- (−/monitorować) Ryzyko podwójnego flagowania epica (scope-check na wejściu Fazy 1 + detekcja w Fazie 3) — scope-check ma kierować do Fazy 3, nie powielać jej komunikatu.
- (−/monitorować) Ryzyko odczytania gate jako zakazu micro-change — wymaga jawnego zdania rekoncyliacji w SKILL.md.
- (−/monitorować) Rozdęcie SKILL.md (583 linie + 5 wszczepień) — mitygacja przez rewrite-to-unify (konsolidacja, nie append) i trzymanie szczegółów companion w osobnym pliku.
- Severity taksonomia `[BLOCKER]`/`[WARN]` ↔ Critical/Important/Minor obry NIE jest rozstrzygana tutaj (spec self-review nie emituje severity) — punktowana do Fazy 2/3.

## Powiązane
- Planning: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-phase-1-feature-discuss.md`
- Epic: `./absolutpowers/feature/superpowers-faza2-fuzje/planning-main.md`
- ADR wspólny: `./docs/adr/2026-07-13-rewrite-to-unify-fuzja-obry.md`
