# preboot-sequence — API Reference

## Spis treści

- [SequenceApi](#sequenceapi)
- [SequenceTenantProvider](#sequencetenantprovider)
- [Exceptions](#exceptions)
- [Token Grammar](#token-grammar)
- [SequenceAutoConfiguration](#sequenceautoconfiguration)
- [SequenceProperties](#sequenceproperties)
- [Database Schema](#database-schema)

---

## SequenceApi

Pakiet: `io.preboot.sequence`

Publiczny interfejs do generowania wartości z named atomic sequences.

### Metody

```java
String getNext(String name, Map<String, String> payload)
```

Atomicznie inkrementuje counter i zwraca wyrenderowaną wartość.

- **name** — nazwa sekwencji z `preboot.sequence.formats`
- **payload** — klucz/wartość dla `%var%` i `$var$` tokenów. Może być `null` (traktowane jako pusty Map).
- **returns** — wyrenderowana wartość, np. `"2026/FV/0001"`
- **throws**:
  - `UnknownSequenceException` — nazwa nie istnieje w konfiguracji
  - `MissingValueException` — brak wymaganego klucza w payload
- **transakcja** — read-write `@Transactional`

```java
String peek(String name, Map<String, String> payload)
```

Read-only podgląd następnej wartości. Nie mutuje DB.

- **name** — nazwa sekwencji
- **payload** — klucz/wartość dla zmiennych. Może być `null`.
- **returns** — podgląd następnej wartości (snapshot, nie rezerwacja)
- **throws**:
  - `UnknownSequenceException` — nazwa nie istnieje
  - `MissingValueException` — brak wymaganego klucza
- **transakcja** — `@Transactional(readOnly = true)`

---

## SequenceTenantProvider

Pakiet: `io.preboot.sequence`

SPI do izolacji counterów per tenant.

```java
public interface SequenceTenantProvider {
    UUID getCurrentTenant();
}
```

- **getCurrentTenant()** — zwraca UUID bieżącego tenanta
- Wyjątki propagowane do wywołującego `getNext`/`peek`
- Domyślna implementacja: `NoTenantProvider` — stały UUID `00000000-0000-0000-0000-000000000001`
- Rejestracja via `@ConditionalOnMissingBean` — custom bean nadpisuje automatycznie

---

## Exceptions

### UnknownSequenceException

Pakiet: `io.preboot.sequence`

Rzucany gdy `name` nie istnieje w `preboot.sequence.formats`.

```java
public class UnknownSequenceException extends RuntimeException
```

### MissingValueException

Pakiet: `io.preboot.sequence`

Rzucany gdy payload nie zawiera wymaganego klucza dla `%var%` lub `$var$`.

```java
public class MissingValueException extends RuntimeException
```

### InvalidPatternException

Pakiet: `io.preboot.sequence`

Rzucany przy starcie gdy maska jest nieprawidłowa. Powoduje fail kontekstu Spring.

```java
public class InvalidPatternException extends RuntimeException
```

Przyczyny:
- Null/empty pattern
- Brak `#counter#`
- Wiele `#counter#`
- Nieznany auto-value (np. `#hour#`)
- Niezamknięty delimiter
- Malformed padding (np. `#counter:abc#`, `#counter:-3#`)
- Padding > 32
- Stored mask > 512 znaków
- Nieprawidłowa nazwa zmiennej (nie pasuje do `[a-zA-Z][a-zA-Z0-9_]*`)

---

## Token Grammar

### Auto-values (`#...#`)

| Token | Rozwiązanie | Przykład |
|-------|------------|---------|
| `#year#` | `LocalDate.now().getYear()` | `2026` |
| `#year:4#` | year z paddingiem (redundantne, rok ma 4 cyfry) | `2026` |
| `#month#` | `LocalDate.now().getMonthValue()` | `4` |
| `#month:2#` | month z paddingiem | `04` |
| `#day#` | `LocalDate.now().getDayOfMonth()` | `30` |
| `#day:2#` | day z paddingiem | `05` |
| `#counter#` | atomiczny counter (no padding) | `1`, `42`, `1000` |
| `#counter:4#` | counter z paddingiem (minimum width) | `0001`, `0042`, `1000` |

### Baked-in variables (`%...%`)

Wartość podstawiana do stored mask. Różne wartości → różne stored maski → **osobne countery**.

```
%name%        — bez paddingu
%name:3%      — z paddingiem (minimum width)
```

### Shared variables (`$...$`)

Placeholder pozostaje w stored mask. Wszystkie wartości współdzielą counter.

```
$name$        — bez paddingu
$name:5$      — z paddingiem (minimum width)
```

### Stored Mask

Stored mask = maska po rozwiązaniu auto-values i %vars%. Counter i $vars$ pozostają jako placeholdery.

Pattern: `#year#/%branch%/FV/#counter:4#`
Payload: `{"branch": "WAW"}`
Stored mask: `2026/WAW/FV/#counter:4#`

Counter row keyed by: `(sequence_id, stored_mask, tenant_uuid)`.

---

## SequenceAutoConfiguration

Pakiet: `io.preboot.sequence.impl`

Warunki aktywacji:
- `@ConditionalOnClass(JdbcTemplate.class)`
- `@ConditionalOnProperty(prefix = "preboot.sequence", name = "enabled", havingValue = "true", matchIfMissing = true)`

### Rejestrowane beany

| Bean | Typ | Warunek |
|------|-----|---------|
| `sequenceClock` | `Clock` | `@ConditionalOnMissingBean(name = "sequenceClock")` |
| `autoValueResolver` | `AutoValueResolver` | `@ConditionalOnMissingBean` |
| `patternTokenizer` | `PatternTokenizer` | `@ConditionalOnMissingBean` |
| `storedMaskBuilder` | `StoredMaskBuilder` | `@ConditionalOnMissingBean` |
| `sequenceTenantProvider` | `SequenceTenantProvider` | `@ConditionalOnMissingBean(SequenceTenantProvider.class)` |

Plus `@ComponentScan` + `@EnableJdbcRepositories` — rejestruje `SequenceApiImpl`, `SequenceFormatRegistrar`, `SequenceFormatBootstrapper`, repozytoria.

### Clock Override

Domyślnie `Clock.systemDefaultZone()`. Do testów:

```java
@Bean
Clock sequenceClock() {
    return Clock.fixed(Instant.parse("2026-04-30T10:00:00Z"), ZoneOffset.UTC);
}
```

---

## SequenceProperties

Pakiet: `io.preboot.sequence.impl`

```java
@ConfigurationProperties(prefix = "preboot.sequence")
class SequenceProperties {
    private boolean enabled = true;
    private Map<String, String> formats = new LinkedHashMap<>();
}
```

| Property | Typ | Default | Opis |
|----------|-----|---------|------|
| `preboot.sequence.enabled` | boolean | `true` | Włącz/wyłącz moduł |
| `preboot.sequence.formats` | Map<String, String> | `{}` | Mapa: nazwa → maska |

---

## Database Schema

### Tabela `preboot_sequences`

| Kolumna | Typ | Constraint |
|---------|-----|-----------|
| `id` | BIGINT AUTO_INCREMENT | PRIMARY KEY |
| `name` | VARCHAR(128) | UNIQUE, NOT NULL |
| `mask` | VARCHAR(512) | NOT NULL |

### Tabela `preboot_sequence_counters`

| Kolumna | Typ | Constraint |
|---------|-----|-----------|
| `id` | BIGINT AUTO_INCREMENT | PRIMARY KEY |
| `sequence_id` | BIGINT | FK → preboot_sequences(id), NOT NULL |
| `mask` | VARCHAR(512) | NOT NULL |
| `counter` | BIGINT | NOT NULL, DEFAULT 0 |
| `tenant_uuid` | UUID | NOT NULL |

**Unique constraint:** `(sequence_id, mask, tenant_uuid)` — `uk_preboot_sequence_counters_resolution`

### Counter Increment SQL

```sql
INSERT INTO preboot_sequence_counters (sequence_id, mask, counter, tenant_uuid)
VALUES (?, ?, 1, ?)
ON CONFLICT (sequence_id, mask, tenant_uuid) DO UPDATE
  SET counter = preboot_sequence_counters.counter + 1
RETURNING counter
```

### Sequence Upsert SQL

```sql
INSERT INTO preboot_sequences (name, mask)
VALUES (?, ?)
ON CONFLICT (name) DO UPDATE
  SET mask = EXCLUDED.mask
RETURNING id
```

Liquibase changelog: `db/changelog/db-changelog-preboot-sequence.xml`
