# Lightweight task routing w feature-discuss — streszczenie (zarchiwizowano 2026-07-16)

## Co zbudowano

`feature-discuss` otrzymał risk- i uncertainty-based ścieżkę `Lightweight task` zamiast wąskiego `Micro-change`. Ścieżka obsługuje scoped context pack, mini-design z HARD-GATE, wykonanie inline w bieżącej sesji oraz obowiązkową weryfikację i branch review. Explain HTML dla standardu, faz i epic overview jest generowany wyłącznie po jawnym opt-in. Dodano kontrakty statyczne i wydano manifesty w wersji 5.5.0.

## Dlaczego (intent)

Małe, spójne zadania wieloplikowe nie powinny przechodzić pełnej ceremonii planningu, QA i task generation, ale nadal muszą respektować reguły projektu, analizę kodu, HARD-GATE, testy i review. Zadania niepewne, wysokiego ryzyka, wielosystemowe lub wymagające handoffu są eskalowane do standardu albo epica.

## Kluczowe decyzje i odrzucone alternatywy

- Zastąpiono `Micro-change` przez `Lightweight task`, bez dodawania czwartego poziomu routingu.
- Kwalifikacja opiera się na ryzyku, niepewności i trwałości handoffu, nie na LOC ani liczbie plików.
- Context pack jest scoped i opcjonalny; świeży kod ma pierwszeństwo przed aktywną pamięcią projektu.
- Mini-design i jawna akceptacja zachowują HARD-GATE; tracker Lightweight pozostaje sesyjny.
- Explain jest opt-in; `skip` i brak odpowiedzi nie blokują workflow.
- Odrzucono osobną czwartą ścieżkę, progi LOC/file-count, uproszczony trwały tasks-doc i domyślne Explain.
- ADR: `docs/adr/2026-07-16-lightweight-task-routing.md` oraz wcześniejsza decyzja HARD-GATE: `docs/adr/2026-07-13-faza1-feature-discuss-brainstorming-fuzja.md`.

## Acceptance Criteria

- AC-1: FULFILLED — routing risk/session based, test token.
- AC-2: FULFILLED — scoped context and code precedence, test token.
- AC-3: FULFILLED — mini-design and explicit acceptance, test token.
- AC-4: FULFILLED — inline execution with verification/review, test token.
- AC-5: FULFILLED — affirmative Explain opt-in, test token.
- AC-6: FULFILLED — optional context tolerance, test token.
- AC-7: FULFILLED — escalation boundaries, test token.
- AC-8: FULFILLED — preserved findings on escalation, test token.
- AC-9: FULFILLED — session-only tracker fallback, test token.
- AC-10: FULFILLED — skip/no-response semantics, test token.
- AC-11: FULFILLED — security boundaries escalate, test token.
- AC-12: FULFILLED — repository content has no authority, test token.
- AC-13: FULFILLED — secret redaction contract, test token.

## Gdzie jest trwała wiedza

- `docs/adr/2026-07-16-lightweight-task-routing.md`
- `docs/onboarding/implementation-decisions-lightweight-task-routing-2026-07-16.html`
- `README.md`, `CLAUDE.md`, `skills/feature-discuss/SKILL.md`
