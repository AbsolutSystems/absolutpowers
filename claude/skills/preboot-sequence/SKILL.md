---
name: preboot-sequence
description: "Skill do używania biblioteki preboot-sequence. Użyj tego skilla zawsze gdy użytkownik chce implementować named atomic sequences, numerację dokumentów (faktury, umowy, zamówienia), auto-inkrementujące countery z konfigurowalnymi maskami, numerację per-oddział, numerację per-tenant, countery z automatycznym resetem na granicach roku/miesiąca, lub pracuje z generowaniem unikalnych numerów biznesowych. Obejmuje: SequenceApi, SequenceTenantProvider, PatternTokenizer, StoredMaskBuilder, SequenceFormatRegistrar, SequenceAutoConfiguration, SequenceCounter, AutoValueResolver. Triggeruje się na: sequence, counter, numeracja, numer faktury, numer umowy, document numbering, invoice number, contract number, auto-increment, atomic counter, padding, mask pattern, baked-in variable, shared variable, tenant isolation, counter reset, year rollover, month rollover, preboot-sequence, SequenceApi, getNext, peek, #counter#, %var%, $var$."
---

# preboot-sequence

Moduł named atomic sequences — generowanie unikalnych numerów biznesowych (faktury, umowy, zamówienia) z konfigurowalnych masek w `application.yml`. Atomiczny counter via PostgreSQL `INSERT ... ON CONFLICT ... RETURNING`, multi-tenant isolation, automatyczny reset counteru na granicach dat.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-sequence</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Zależności `provided` — projekt musi mieć `spring-boot-starter-data-jdbc`. Liquibase changelog w `db/changelog/db-changelog-preboot-sequence.xml`.

## Szybki start

### 1. Konfiguracja masek w `application.yml`

```yaml
preboot:
  sequence:
    formats:
      Faktura: "#year#/FV/#counter:4#"
      Umowy: "#year#/UM/#counter#"
      PerBranch: "#year#/%branch%/#counter#"
```

### 2. Generowanie numeru

```java
@Service
@RequiredArgsConstructor
public class InvoiceService {
    private final SequenceApi sequenceApi;

    public String nextInvoiceNumber() {
        return sequenceApi.getNext("Faktura", Map.of());
        // → "2026/FV/0001"
    }
}
```

### 3. Podgląd bez inkrementacji

```java
String preview = sequenceApi.peek("Faktura", Map.of());
// → "2026/FV/0042" (read-only, nie rezerwuje)
```

### 4. Zmienne w masce — baked-in vs shared

```java
// %branch% — OSOBNE countery per wartość
api.getNext("PerBranch", Map.of("branch", "WAW")); // → "2026/WAW/1"
api.getNext("PerBranch", Map.of("branch", "KRK")); // → "2026/KRK/1" (osobny counter)

// $branch$ — WSPÓLNY counter
api.getNext("Shared", Map.of("branch", "WAW")); // → "2026/WAW/1"
api.getNext("Shared", Map.of("branch", "KRK")); // → "2026/KRK/2" (ten sam counter)
```

## Główne koncepty

### Gramatyka masek

| Delimiter | Typ | Zachowanie | Przykład |
|-----------|-----|-----------|---------|
| `#...#` | Auto-value | Rozwiązywany przy wywołaniu: `year`, `month`, `day`, `counter` | `#year#` → `2026` |
| `%...%` | Baked-in var | Wchodzi do stored mask → **osobny counter per wartość** | `%branch%` baked into mask |
| `$...$` | Shared var | Placeholder w stored mask → **wspólny counter** | `$branch$` stays as placeholder |

Padding via `:N` (np. `#counter:4#`, `#month:2#`). Minimum width — counter rośnie ponad padding naturalnie.

### Auto-konfiguracja

`SequenceAutoConfiguration` aktywuje się gdy:
- `JdbcTemplate` na classpath
- `preboot.sequence.enabled=true` (default)

Rejestruje: `AutoValueResolver`, `PatternTokenizer`, `StoredMaskBuilder`, `SequenceFormatRegistrar`, `SequenceApiImpl`, `NoTenantProvider` (gdy brak custom `SequenceTenantProvider`).

### Multi-tenancy

Domyślnie single-tenant (stały UUID). Dla multi-tenancy dostarcz bean:

```java
@Bean
public SequenceTenantProvider tenantProvider(TenantResolver resolver) {
    return () -> resolver.getCurrentTenantId();
}
```

### Automatyczny reset counteru

Countery są scope'owane stored mask. Zmiana `#year#` (2026→2027) tworzy nowy stored mask → nowy counter od 1. Analogicznie `#month#`, `#day#`.

### Schemat DB

Dwie tabele (Liquibase):
- `preboot_sequences` — name (UNIQUE), mask
- `preboot_sequence_counters` — sequence_id, mask, counter, tenant_uuid (UNIQUE constraint na trójce)

## Typowe przepływy

### Numeracja faktur z paddingiem

```yaml
formats:
  Faktura: "#year#/#month:2#/FV/#counter:6#"
```
```java
api.getNext("Faktura", Map.of()); // → "2026/04/FV/000001"
```

### Numeracja per oddział (osobne countery)

```yaml
formats:
  FakturaOddzial: "#year#/%branch%/FV/#counter:4#"
```
```java
api.getNext("FakturaOddzial", Map.of("branch", "WAW")); // → "2026/WAW/FV/0001"
api.getNext("FakturaOddzial", Map.of("branch", "KRK")); // → "2026/KRK/FV/0001" (osobny!)
```

### Numeracja cross-branch (wspólny counter)

```yaml
formats:
  UmowaGlobalna: "#year#/$region$/UM/#counter:4#"
```
```java
api.getNext("UmowaGlobalna", Map.of("region", "PL")); // → "2026/PL/UM/0001"
api.getNext("UmowaGlobalna", Map.of("region", "DE")); // → "2026/DE/UM/0002" (wspólny!)
```

### Zmiana maski po restarcie

Zmiana maski w `application.yml` → upsert w DB. Stare counter rows zostają. Nowa maska zaczyna od 1.

## Pułapki i częste błędy

1. **Brak `#counter#`** — każda maska musi mieć dokładnie jeden counter placeholder. Startup fail.
2. **Wiele `#counter#`** — niedozwolone. Jeden counter per maska.
3. **Brak klucza w payload** — `%branch%` bez `"branch"` w Map → `MissingValueException`.
4. **`peek` nie rezerwuje** — współbieżny `getNext` może zwrócić tę samą wartość. Snapshot, nie rezerwacja.
5. **Tylko PostgreSQL** — `INSERT ... ON CONFLICT ... RETURNING` jest PostgreSQL-specific.
6. **Padding = minimum width** — counter `1000` z `#counter:3#` → `"1000"` (4 cyfry). Brak błędu.
7. **Max padding 32** — wartości powyżej odrzucone przy starcie.
8. **Max stored mask 512 chars** — przekroczenie → `InvalidPatternException`.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury metod, typy, wyjątki, schemat DB
- **examples.md** — zaawansowane scenariusze, multi-tenancy, testy, integracja z innymi modułami
