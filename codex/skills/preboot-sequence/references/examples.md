# preboot-sequence — Przykłady użycia

## Spis treści

- [Podstawowe użycie — faktura z paddingiem](#podstawowe-użycie--faktura-z-paddingiem)
- [Numeracja per oddział (baked-in %var%)](#numeracja-per-oddział-baked-in-var)
- [Numeracja cross-branch (shared $var$)](#numeracja-cross-branch-shared-var)
- [Podgląd następnego numeru](#podgląd-następnego-numeru)
- [Multi-tenancy](#multi-tenancy)
- [Data w numeracji — rok/miesiąc/dzień](#data-w-numeracji--rokmiesiącdzień)
- [Zmiana maski między restartami](#zmiana-maski-między-restartami)
- [Testowanie z fixed Clock](#testowanie-z-fixed-clock)
- [Integracja z preboot-auth (multi-tenant)](#integracja-z-preboot-auth-multi-tenant)
- [Obsługa błędów](#obsługa-błędów)
- [Test integracyjny z Testcontainers](#test-integracyjny-z-testcontainers)

---

## Podstawowe użycie — faktura z paddingiem

```yaml
preboot:
  sequence:
    formats:
      Faktura: "#year#/FV/#counter:4#"
```

```java
import io.preboot.sequence.SequenceApi;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class InvoiceService {

    private final SequenceApi sequenceApi;

    public String generateInvoiceNumber() {
        return sequenceApi.getNext("Faktura", Map.of());
    }
}
```

```
Wywołanie 1 → "2026/FV/0001"
Wywołanie 2 → "2026/FV/0002"
...
Wywołanie 9999 → "2026/FV/9999"
Wywołanie 10000 → "2026/FV/10000"  (padding = minimum width, rośnie naturalnie)
```

Zmiana roku: counter resetuje się automatycznie.
```
Ostatnie w 2026 → "2026/FV/4521"
Pierwsze w 2027 → "2027/FV/0001"  (nowy stored mask → nowy counter)
```

---

## Numeracja per oddział (baked-in %var%)

```yaml
preboot:
  sequence:
    formats:
      FakturaOddzial: "#year#/%branch%/FV/#counter:4#"
```

```java
// Każdy oddział ma osobny counter
api.getNext("FakturaOddzial", Map.of("branch", "WAW")); // → "2026/WAW/FV/0001"
api.getNext("FakturaOddzial", Map.of("branch", "WAW")); // → "2026/WAW/FV/0002"
api.getNext("FakturaOddzial", Map.of("branch", "KRK")); // → "2026/KRK/FV/0001"
api.getNext("FakturaOddzial", Map.of("branch", "KRK")); // → "2026/KRK/FV/0002"
api.getNext("FakturaOddzial", Map.of("branch", "WAW")); // → "2026/WAW/FV/0003"
```

DB — dwa counter rows:
- `stored_mask = "2026/WAW/FV/#counter:4#"`, counter = 3
- `stored_mask = "2026/KRK/FV/#counter:4#"`, counter = 2

---

## Numeracja cross-branch (shared $var$)

```yaml
preboot:
  sequence:
    formats:
      UmowaGlobalna: "#year#/$region$/UM/#counter:4#"
```

```java
// Wszystkie regiony współdzielą counter
api.getNext("UmowaGlobalna", Map.of("region", "PL")); // → "2026/PL/UM/0001"
api.getNext("UmowaGlobalna", Map.of("region", "DE")); // → "2026/DE/UM/0002"
api.getNext("UmowaGlobalna", Map.of("region", "PL")); // → "2026/PL/UM/0003"
```

DB — jeden counter row:
- `stored_mask = "2026/$region$/UM/#counter:4#"`, counter = 3

---

## Podgląd następnego numeru

```java
// peek nie inkrementuje — read-only
String preview = api.peek("Faktura", Map.of());
// → "2026/FV/0001" (jeśli counter jeszcze nie istnieje)

api.getNext("Faktura", Map.of()); // → "2026/FV/0001"

preview = api.peek("Faktura", Map.of());
// → "2026/FV/0002" (widzi aktualny stan)

// UWAGA: peek nie rezerwuje! Współbieżny getNext może zwrócić tę samą wartość.
```

---

## Multi-tenancy

```java
@Bean
public SequenceTenantProvider sequenceTenantProvider() {
    return () -> SecurityContextHolder.getContext().getTenantId();
}
```

```java
// Tenant A
api.getNext("Faktura", Map.of()); // → "2026/FV/0001" (tenant A, counter 1)
api.getNext("Faktura", Map.of()); // → "2026/FV/0002" (tenant A, counter 2)

// Tenant B
api.getNext("Faktura", Map.of()); // → "2026/FV/0001" (tenant B, counter 1!)
```

DB — dwa counter rows z różnym `tenant_uuid`, oba z `stored_mask = "2026/FV/#counter:4#"`.

---

## Data w numeracji — rok/miesiąc/dzień

```yaml
preboot:
  sequence:
    formats:
      Dzienny: "#year#/#month:2#/#day:2#/DOC/#counter:3#"
      Miesięczny: "#year#/#month:2#/INV/#counter:5#"
      Roczny: "#year#/CTR/#counter#"
```

```java
// 30 kwietnia 2026
api.getNext("Dzienny", Map.of());    // → "2026/04/30/DOC/001"
api.getNext("Miesięczny", Map.of()); // → "2026/04/INV/00001"
api.getNext("Roczny", Map.of());     // → "2026/CTR/1"

// 1 maja 2026 — counter "Dzienny" i "Miesięczny" resetują się
api.getNext("Dzienny", Map.of());    // → "2026/05/01/DOC/001" (nowy stored mask!)
api.getNext("Miesięczny", Map.of()); // → "2026/05/INV/00001" (nowy stored mask!)
api.getNext("Roczny", Map.of());     // → "2026/CTR/2" (ten sam stored mask)
```

---

## Zmiana maski między restartami

```yaml
# Wersja 1
preboot:
  sequence:
    formats:
      UmowyBateryjne: "#year#/BAT/#counter#"
```

Generujesz 3 numery: `2026/BAT/1`, `2026/BAT/2`, `2026/BAT/3`.

```yaml
# Wersja 2 — zmiana BAT → BAT2
preboot:
  sequence:
    formats:
      UmowyBateryjne: "#year#/BAT2/#counter#"
```

Po restarcie:
- DB: `preboot_sequences.mask` zaktualizowany na `#year#/BAT2/#counter#`
- Stary counter row (`mask = "2026/BAT/#counter#"`, counter = 3) **zostaje** w DB
- Nowy counter zaczyna od 1: `2026/BAT2/1`

---

## Testowanie z fixed Clock

```java
@SpringBootApplication
class TestApp {

    @Bean
    Clock sequenceClock() {
        return Clock.fixed(Instant.parse("2026-04-30T10:00:00Z"), ZoneOffset.UTC);
    }
}
```

```java
@SpringBootTest
@Testcontainers
class SequenceTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    SequenceApi api;

    @Test
    void shouldGenerateSequentialNumbers() {
        assertThat(api.getNext("Faktura", Map.of())).isEqualTo("2026/FV/0001");
        assertThat(api.getNext("Faktura", Map.of())).isEqualTo("2026/FV/0002");
    }
}
```

---

## Integracja z preboot-auth (multi-tenant)

```java
import io.preboot.auth.core.TenantResolver;
import io.preboot.sequence.SequenceTenantProvider;

@Configuration
public class SequenceTenantConfig {

    @Bean
    public SequenceTenantProvider sequenceTenantProvider(TenantResolver tenantResolver) {
        return () -> tenantResolver.getCurrentTenantId();
    }
}
```

`NoTenantProvider` automatycznie wyłączony dzięki `@ConditionalOnMissingBean`.

---

## Obsługa błędów

```java
import io.preboot.sequence.UnknownSequenceException;
import io.preboot.sequence.MissingValueException;

try {
    String number = api.getNext("NieIstniejaca", Map.of());
} catch (UnknownSequenceException e) {
    // "Sequence 'NieIstniejaca' is not registered. Add it under preboot.sequence.formats."
}

try {
    String number = api.getNext("PerBranch", Map.of()); // brak "branch" w payload
} catch (MissingValueException e) {
    // "Missing payload key for %branch%"
}
```

Błędy masek wykrywane przy starcie (fail-fast):

```yaml
preboot:
  sequence:
    formats:
      Bad: "FV/2026"  # brak #counter# → InvalidPatternException → context startup fail
```

---

## Test integracyjny z Testcontainers

```java
@SpringBootTest
@Testcontainers
class ConcurrencyTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    SequenceApi api;

    @Test
    void concurrentCallsShouldProduceUniqueValues() throws Exception {
        int requests = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(16);
        Set<String> results = ConcurrentHashMap.newKeySet();
        CountDownLatch latch = new CountDownLatch(requests);

        for (int i = 0; i < requests; i++) {
            executor.submit(() -> {
                try {
                    results.add(api.getNext("Faktura", Map.of()));
                } finally {
                    latch.countDown();
                }
            });
        }

        assertThat(latch.await(60, TimeUnit.SECONDS)).isTrue();
        executor.shutdown();

        assertThat(results).hasSize(requests); // 1000 unique values
    }
}
```

---

## Mieszane zmienne — baked-in + shared w jednej masce

```yaml
preboot:
  sequence:
    formats:
      Complex: "#year#/%type%/$region$/#counter:5#"
```

```java
// %type% baked-in → osobne countery per type
// $region$ shared → w ramach tego samego type, counter wspólny cross-region

api.getNext("Complex", Map.of("type", "FV", "region", "PL")); // → "2026/FV/PL/00001"
api.getNext("Complex", Map.of("type", "FV", "region", "DE")); // → "2026/FV/DE/00002" (shared!)
api.getNext("Complex", Map.of("type", "UM", "region", "PL")); // → "2026/UM/PL/00001" (osobny type!)
```

DB:
- `stored_mask = "2026/FV/$region$/#counter:5#"`, counter = 2
- `stored_mask = "2026/UM/$region$/#counter:5#"`, counter = 1
