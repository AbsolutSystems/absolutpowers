# Full Review Report — v5.1.0 vs v3.13.0

**Zakres:** `ff9cd48` (`v3.13.0`) → `0e2fe21` (`v5.1.0`), 154 pliki, +12 291 / -5 859 linii.

## Verdict

**REQUEST CHANGES** — migracja do jednego drzewa jest wyraźną poprawą architektoniczną,
ale v5 reguluje funkcjonalność Codex gorzej niż v3.13.0. Przed wydaniem należy przywrócić
jednoznaczną ścieżkę degradacji dla Codex i domknąć kontrakt bezpieczeństwa companionu.

## 1. Semantic Review

### Co się zmieniło

- Jedno `skills/` zastąpiło dwa lustrzane drzewa `claude/skills/` i `codex/skills/`.
  Usuwa to realne źródło driftu oraz zbędne skrypty synchronizacji.
- Manifesty marketplace wskazują na root; dodano integrację Pi oraz wspólny SessionStart
  context dla Claude/Pi.
- Pipeline otrzymał terminal-state, vendored workflow skills, model routing i review packages.
- Dodano browserowy Visual Companion — lokalny serwer HTTP/WebSocket renderujący HTML.

### Blast radius

- `feature-discuss`, `generate-tasks` i `implement` są centralnymi promptami pipeline'u;
  niejednoznaczny fallback wpływa na każde uruchomienie z Codex.
- Companion jest nową powierzchnią uruchamiania procesu i renderowania HTML w przeglądarce.

### Findings

1. **[HIGH] Codex stracił działającą ścieżkę wykonania orchestrated i review gate'ów.**
   W v3.13.0 `codex/skills/implement/SKILL.md` explicite wykonywał phase files sekwencyjnie
   w tej samej sesji, bo nie było zarejestrowanych agentów. W wspólnym pliku `implement`
   tryb `orchestrated` nakazuje dispatch `implementation-worker` z Claude-owym
   `subagent_type` ([skills/implement/SKILL.md:241](/Users/kamil/Projekty/absolut-ai-skills/skills/implement/SKILL.md:241)),
   a także `phase-review` i `review-implementation`; analogiczne literalne gate'y są w
   `feature-discuss` i `generate-tasks`.

   Tekst odsyła Codex do `references/pi-tools.md` ([skills/implement/SKILL.md:33](/Users/kamil/Projekty/absolut-ai-skills/skills/implement/SKILL.md:33)),
   ale ten plik definiuje wyłącznie Pi ([references/pi-tools.md:28](/Users/kamil/Projekty/absolut-ai-skills/references/pi-tools.md:28)).
   Nie ma `references/codex-tools.md` ani instrukcji: „w Codex dispatch generic agent z
   `agents/{name}.md`, a gdy nie ma multi-agent — wykonaj inline”. Rezultat: agent Codex
   może próbować nieważnego `Agent(subagent_type=...)`, albo ominąć gate bez jawnego
   werdyktu. To regresja względem v3, nie tylko brak nowej funkcji.

   **Fix:** dodaj `references/codex-tools.md` z dwustopniowym fallbackiem równoległym do
   Pi i zmień trzy wspólne skille, aby jawnie wybierały Claude / Codex / Pi. Dla Codex
   zachowaj poprzedni bezpieczny fallback sekwencyjny dla orchestrated mode.

2. **[MEDIUM] Visual Companion nie spełnia deklaracji „statycznego renderu”.**
   Skill obiecuje, że companion serwuje wyłącznie statyczny HTML i nigdy nie wykonuje kodu
   z requestu. Tymczasem serwer zwraca pełny HTML ekranu bez sanitizacji
   ([server.cjs:395](/Users/kamil/Projekty/absolut-ai-skills/skills/feature-discuss/companion-scripts/server.cjs:395))
   i jego CSP ogranicza wyłącznie `frame-ancestors`, bez `script-src`
   ([server.cjs:354](/Users/kamil/Projekty/absolut-ai-skills/skills/feature-discuss/companion-scripts/server.cjs:354)).
   Wystarczy, że HTML wygenerowany pod wpływem treści requestu zawiera `<script>`, event
   handler lub zewnętrzny resource — przeglądarka go wykona. Opcja `--host` dodatkowo
   przewiduje bind poza loopbackiem ([start-server.sh:11](/Users/kamil/Projekty/absolut-ai-skills/skills/feature-discuss/companion-scripts/start-server.sh:11)).

   **Fix:** albo narzuć CSP typu `default-src 'none'; style-src 'unsafe-inline'; img-src
   data:; connect-src 'self'; script-src` z nonce/hash dla jedynego helpera, oraz filtruj
   HTML, albo zmień kontrakt na render zaufanego HTML i nie generuj go z nieufnej treści.

## 2. Edge Cases

- **MEDIUM — harness bez capability subagentów:** scenariusz: Codex otwiera orchestrated
  tasks. Wspólny prompt wymaga zarejestrowanego Claude agent type. Pseudofix: `if Codex`
  → generic `spawn_agent` z body `agents/{name}.md`; `else` → sekwencyjnie/inline z
  advisory verdictem.
- **MEDIUM — HTML z instrukcją w treści użytkownika:** scenariusz: ekran companionu
  zawiera `script`, `onerror` albo remote image. Problem: serwer renderuje go w originie
  z aktywną sesją. Pseudofix: reject/sanitize active content i włącz restrykcyjne CSP.
- **LOW — brak regresyjnych testów dla nowego runtime.** Repo nie zawiera testów automatycznych
  dla HTTP/WebSocket servera, wrappera hooka ani integracji Pi; wykrywanie błędów pozostaje
  głównie manualne. Dodaj minimalne testy: unauthorized/authorized HTTP, traversal/symlink,
  CSP, WS Origin i bootstrap po compact.

## 3. Rules Check

Brak pliku `./absolutpowers/rules.md`, pomijam sprawdzanie reguł.

Brak pliku `./absolutpowers/constitution.md`, pomijam sprawdzanie pryncypiów.

## 4. Garbage Collection

- Nie wykryto błędów whitespace (`git diff --check`).
- Manifesty JSON, hook JSON i frontmatter wszystkich `skills/**/SKILL.md` są poprawne.
- `bash -n` przeszedł dla nowych skryptów, `node --check` dla extension/server/helper oraz
  TypeScript typecheck Pi przeszedł.
- Nie ma nieśledzonych ani lokalnych zmian do osobnego review.

## Ocena względem v3.13.0

**Tak — rdzeń v5 jest obiektywnie lepszy:** jedno źródło prawdy usuwa klasę błędów driftu,
manifesty są prostsze, AGENTS jest symlinkiem, a attribution vendored content jest jawne.
To redukcja kosztu utrzymania bez utraty zamierzonej funkcjonalności Claude.

**Nie — nie jest jeszcze bezwarunkowo lepszy jako produkt wieloharnessowy:** Codex ma
regresję opisanej ścieżki wykonania, a nowa warstwa companionu zwiększa powierzchnię ryzyka
bez testów i z kontraktem bezpieczeństwa niespełnianym przez implementację. Po naprawie
dwóch findingów powyżej ocena „lepiej niż v3” byłaby jednoznaczna.
