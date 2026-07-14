# try-learn-skill jako codebase-scan + usunięcie harvest — streszczenie (zarchiwizowano 2026-07-14)

## Co zbudowano
`try-learn-skill` przepisany z uczenia się z artefaktów jednego feature'a na **skan całego codebase** projektu: proceduralny wzorzec kwalifikuje się na learned-skilla tylko przy ≥3 wystąpieniach z dowodem `file:line` i ≥2 nieoczywistych krokach, kandydaci prezentowani batch, zapis tylko zaznaczonych (human gate). Skill `harvest` usunięty całkowicie; jego jedyna unikalna funkcja — archiwizacja artefaktów feature'a — przeniesiona do `ship` (KROK 4.5).

## Dlaczego (intent)
Stary try-learn generalizował z n=1 (pojedynczy planning+tasks+diff) → skille jednorazowe, przywiązane do feature'a, bezużyteczne później. Candidate-ledger (3.12.0) nie łagodził tego w praktyce (izolowane sesje, punkt obserwacji za wąski). Zmiana źródła sygnału na powtarzalność w kodzie rozwiązuje problem u korzenia. Harvest był pustym orkiestratorem — sub-skille (document-feature/document-module) już standalone, try-learn wyprowadzony.

## Kluczowe decyzje i odrzucone alternatywy
- **Codebase-scan zamiast feature-artefaktu** — powtarzalność w kodzie to twardy, weryfikowalny sygnał; diff to zgadywanie z n=1. Odrzucone: „podkręcić próg na feature-artefakcie" (nie adresuje korzenia).
- **Ledger wywalony** — istniał tylko po to, by łapać 2. wystąpienie między sesjami; skan widzi wszystkie naraz.
- **Archiwizacja → ship (nie osobny mikro-command)** — ship to naturalny closeout; jeden command zamiast dwóch.
- **Batch approval (próg ≥3 znajduje, człowiek zaznacza)** — twardy próg + human gate; batch szybszy niż gate-per-skill przy bootstrapie wielu.
- **Granica vs update-ai-context** — pasywna dokumentacja (patterns/rules/CLAUDE.md) vs aktywne wywoływalne procedury (learned-skille); zapisana wprost w skillu, by nie zrobić drugiego narzędzia do tego samego.
- Próg N=3 domyślny, tunable w argumencie. Brak forka `commands/` (skill wywoływalny jako `/absolutpowers:try-learn-skill`).

## Acceptance Criteria
13/13 FULFILLED (grep/strukturalne — repo bez buildu):
- AC-1 codebase-scan wejście · AC-2 próg 3 + file:line · AC-3 batch approval · AC-4 harvest usunięty
- AC-5 ship archiwizacja · AC-6 ledger usunięty · AC-7 granica update-ai-context · AC-8 graceful brak-kandydatów
- AC-9 ship reconcile · AC-10 zero żywych harvest · AC-11 human gate · AC-12 hard boundary · AC-13 gate przed mv

## Gdzie jest trwała wiedza
- skille: `skills/try-learn-skill/SKILL.md` (rewrite), `skills/ship/SKILL.md` (KROK 4.5)
- docs: `CLAUDE.md` (Closeout section), `README.md` (changelog 5.1.0, Skills Reference, Key Concepts)
- raport review: `absolutpowers/reviews/2026-07-14-feat-try-learn-codebase-scan.md`
- ADR: brak (decyzje utrwalone w tym streszczeniu + planning docu)
- learned-skill: brak (feature nie generalizowalny jako reużywalna procedura)
