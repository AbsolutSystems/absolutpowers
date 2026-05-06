# API Reference — preboot-query

Pakiety: `io.preboot.query`, `io.preboot.query.web`, `io.preboot.query.web.spi`, `io.preboot.query.exception`

## Spis treści

- [FilterableRepository (interfejs)](#filterablerepository)
- [FilterableUuidRepository (interfejs)](#filterableuuidrepository)
- [UuidRepository (interfejs)](#uuidrepository)
- [HasUuid (interfejs)](#hasuuid)
- [FilterableFragmentImpl (klasa)](#filterablefragmentimpl)
- [FilterableUuidFragmentImpl (klasa)](#filterableuuidfragmentimpl)
- [FilterableFragmentContext (klasa)](#filterablefragmentcontext)
- [SearchParams (klasa)](#searchparams)
- [FilterCriteria (klasa)](#filtercriteria)
- [SortOrder (record)](#sortorder)
- [LogicalOperator (enum)](#logicaloperator)
- [@AggregateReference (adnotacja)](#aggregatereference)
- [FilterableController (klasa)](#filterablecontroller)
- [CrudFilterableController (klasa)](#crudfilterablecontroller)
- [UuidFilterableController (klasa)](#uuidfilterablecontroller)
- [CrudUuidFilterableController (klasa)](#cruduuidfilterablecontroller)
- [SearchRequest (record)](#searchrequest)
- [ExportRequest (record)](#exportrequest)
- [AsyncExportEvent (record)](#asyncexportevent)
- [QueryControllersPort (interfejs SPI)](#querycontrollersport)
- [UserContext (record)](#usercontext)
- [Wyjątki](#wyjątki)

---

## FilterableRepository

**Interfejs** — główne repozytorium z filtrowaniem. Rozszerza `CrudRepository` i `FilterableFragment`.

```java
@NoRepositoryBean
public interface FilterableRepository<T, ID> extends CrudRepository<T, ID>, FilterableFragment<T> {}
```

### Metody z FilterableFragment

| Metoda | Zwraca | Opis |
|--------|--------|------|
| `findAll(SearchParams params)` | `Page<T>` | Wyszukiwanie z filtrowaniem, paginacją i sortowaniem |
| `findAllAsStream(SearchParams params)` | `Stream<T>` | Jak findAll ale zwraca Stream (unpaged) |
| `findOne(SearchParams params)` | `Optional<T>` | Pierwszy pasujący wynik |
| `count(SearchParams params)` | `long` | Liczba pasujących rekordów |
| `findAllProjectedBy(params, projectionType)` | `Page<P>` | Wyszukiwanie z projekcją |
| `findAllProjectedByAsStream(params, projectionType)` | `Stream<P>` | Stream z projekcją |
| `findOneProjectedBy(params, projectionType)` | `Optional<P>` | Jeden wynik z projekcją |

Plus wszystkie metody z `CrudRepository`: `save()`, `findById()`, `deleteById()`, etc.

---

## FilterableUuidRepository

**Interfejs** — FilterableRepository + operacje UUID.

```java
@NoRepositoryBean
public interface FilterableUuidRepository<T extends HasUuid, ID>
    extends FilterableRepository<T, ID>, UuidRepository<T> {}
```

---

## UuidRepository

**Interfejs** — operacje UUID.

```java
@NoRepositoryBean
public interface UuidRepository<T extends HasUuid> {
    Optional<T> findByUuid(UUID uuid);
    boolean existsByUuid(UUID uuid);
    void deleteByUuid(UUID uuid);
}
```

---

## HasUuid

**Interfejs** — marker dla encji z UUID.

```java
public interface HasUuid {
    UUID getUuid();
    void setUuid(UUID uuid);
}
```

---

## FilterableFragmentImpl

**Klasa abstrakcyjna** — bazowa implementacja `FilterableFragment` i `CrudRepository`. Rozszerzasz ją w swoim repozytorium.

```java
public abstract class FilterableFragmentImpl<T, ID>
    implements FilterableFragment<T>, CrudRepository<T, ID>
```

### Konstruktor

```java
protected FilterableFragmentImpl(FilterableFragmentContext context, Class<T> entityClass)
```

### Chronione metody

| Metoda | Opis |
|--------|------|
| `createPageable(SearchParams)` | Tworzy Pageable z SearchParams |
| `getEntityType()` | Zwraca klasę encji |

---

## FilterableUuidFragmentImpl

**Klasa** — rozszerzenie `FilterableFragmentImpl` z UUID. Implementuje `UuidRepository`.

```java
public class FilterableUuidFragmentImpl<T extends HasUuid, ID>
    extends FilterableFragmentImpl<T, ID>
    implements UuidRepository<T>
```

`findByUuid()` jest zaimplementowane jako `findOne(SearchParams.criteria(FilterCriteria.eq("uuid", uuid)).build())`.

---

## FilterableFragmentContext

**Klasa `@Service`** — agreguje wszystkie zależności potrzebne do `FilterableFragmentImpl`. Auto-konfigurowana.

```java
@Service
public class FilterableFragmentContext {
    // Wymagane zależności (wszystkie auto-konfigurowane przez Spring Boot):
    // - NamedParameterJdbcTemplate
    // - SqlBuilder
    // - RelationalMappingContext
    // - JdbcConverter
    // - ConversionService
    // - JdbcAggregateTemplate
    // - PropertyResolver
}
```

---

## SearchParams

**Klasa** — parametry wyszukiwania.

```java
@Data @Builder
public class SearchParams {
    public static final int DEFAULT_PAGE = 0;
    public static final int DEFAULT_SIZE = 20;
    public static final Sort.Direction DEFAULT_DIRECTION = Sort.Direction.ASC;
    public static final String DEFAULT_SORT_FIELD = "id";

    private List<FilterCriteria> filters;
    private Integer page;           // default: 0
    private Integer size;           // default: 20
    @Deprecated private String sortField;        // default: "id" — use sort instead
    @Deprecated private Sort.Direction sortDirection; // default: ASC — use sort instead
    private List<SortOrder> sort;   // multi-field sort (takes precedence)
    private boolean unpaged;        // default: false
}
```

### Factory methods

| Metoda | Opis |
|--------|------|
| `SearchParams.empty()` | Puste params (brak filtrów, default paginacja) |
| `SearchParams.criteria(FilterCriteria...)` | Builder z filtrami |
| `SearchParams.builder()` | Full builder |

### Kluczowe metody

#### `getEffectiveSortOrders()`
Zwraca efektywne sortowanie. `sort` > `sortField`/`sortDirection` > default (`id ASC`).

#### `setFilter(FilterCriteria filter)`
Dodaje/nadpisuje filtr (po nazwie pola). Chainable.

---

## FilterCriteria

**Klasa** — kryterium filtrowania. Może być proste (field + operator + value) lub złożone (children + logicalOperator).

```java
@Data @Builder
public class FilterCriteria {
    private String field;
    private String operator;
    private Object value;
    private List<FilterCriteria> children;
    private LogicalOperator logicalOperator;
}
```

### Factory methods

| Metoda | Operator SQL |
|--------|-------------|
| `eq(field, value)` | `= :val` |
| `neq(field, value)` | `!= :val` |
| `eqic(field, value)` | `LOWER(col) = LOWER(:val)` |
| `like(field, value)` | `ILIKE :val%` (auto-dodaje %) |
| `gt(field, value)` | `> :val` |
| `lt(field, value)` | `< :val` |
| `gte(field, value)` | `>= :val` |
| `lte(field, value)` | `<= :val` |
| `between(field, from, to)` | `BETWEEN :from AND :to` |
| `in(field, values...)` | `IN (:vals)` |
| `notIn(field, values...)` | `NOT IN (:vals)` |
| `ao(field, values...)` | `&& ARRAY[:vals]` (PostgreSQL array overlap) |
| `isNull(field)` | `IS NULL` |
| `isNotNull(field)` | `IS NOT NULL` |
| `or(List<FilterCriteria>)` | `(child1 OR child2 OR ...)` |
| `and(List<FilterCriteria>)` | `(child1 AND child2 AND ...)` |

### Metody

#### `isCompound()`
`true` jeśli kryterium jest złożone (ma `children`).

#### `isNullOperation()`
`true` dla `isnull` / `isnotnull`.

#### `getValue()`
Zwraca wartość. Dla `like` automatycznie dodaje `%` na końcu.

---

## SortOrder

**Record** — pojedynczy porządek sortowania.

```java
public record SortOrder(String field, Sort.Direction direction) {
    public static SortOrder asc(String field);
    public static SortOrder desc(String field);
    public static SortOrder of(String field, Sort.Direction direction);
}
```

Pole `field` jest walidowane: `^[a-zA-Z0-9_.]+$`.

---

## LogicalOperator

**Enum** — operator logiczny.

```java
public enum LogicalOperator {
    AND("AND"),
    OR("OR");

    public String sql();
}
```

---

## @AggregateReference

**Adnotacja** — oznacza pole jako referencję do innego agregatu. Umożliwia JOIN w zapytaniach i filtrowanie po polach referencji.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AggregateReference {
    Class<?> target();                    // klasa docelowego agregatu
    String targetColumn() default "uuid"; // kolumna w tabeli docelowej
    String sourceColumn() default "";     // kolumna w tabeli źródłowej
    String alias();                       // alias w zapytaniach (np. "category")
}
```

---

## FilterableController

**Klasa abstrakcyjna** — read-only REST controller z filtrowaniem.

```java
public abstract class FilterableController<T, ID>
```

### Konstruktory

```java
protected FilterableController(FilterableRepository<T, ID> repository)
protected FilterableController(repo, boolean supportsProjections, List<DataExporter> dataExporters)
protected FilterableController(repo, supportsProjections, dataExporters, QueryControllersPort controllersPort)
```

### Endpointy

| Metoda HTTP | Path | Opis |
|-------------|------|------|
| `GET` | `/{id}` | Pobierz po ID |
| `POST` | `/search` | Wyszukaj z filtrowaniem (body: `SearchRequest`) |
| `POST` | `/find` | Znajdź jeden (body: `SearchRequest`) |
| `POST` | `/count` | Policz pasujące (body: `SearchRequest`) |
| `POST` | `/search/{projection}` | Wyszukaj z projekcją |
| `POST` | `/export/{format}` | Eksport synchroniczny |
| `POST` | `/export-async/{format}` | Eksport asynchroniczny |

### Chronione metody (override)

| Metoda | Opis |
|--------|------|
| `beforeRead(T entity)` | Hook przed odczytem |
| `afterRead(T entity)` | Hook po odczycie (return przetworzona encja) |
| `resolveProjectionClass(String name)` | Resolve nazwy projekcji na klasę |
| `getMaxPageSize()` | Max page size (default: 100) |
| `prepareExportLabels()` | Etykiety kolumn dla eksportu |
| `getRepository()` | Dostęp do repozytorium |

---

## CrudFilterableController

**Klasa abstrakcyjna** — rozszerza `FilterableController` o operacje CRUD.

```java
public abstract class CrudFilterableController<T, ID> extends FilterableController<T, ID>
```

### Dodatkowe endpointy

| Metoda HTTP | Path | Opis |
|-------------|------|------|
| `POST` | `/` | Stwórz encję (201 Created) |
| `PUT` | `/{id}` | Full update |
| `PATCH` | `/{id}` | Partial update (deep merge) |
| `DELETE` | `/{id}` | Usuń |

### Hooki CRUD (override)

| Metoda | Kiedy |
|--------|-------|
| `validateCreate(T)` | Przed tworzeniem |
| `beforeCreate(T)` / `afterCreate(T)` | Przed/po tworzeniu |
| `validateUpdate(ID, T)` | Przed update |
| `beforeUpdate(ID, T)` / `afterUpdate(ID, T)` | Przed/po update |
| `validatePatch(ID, T)` | Przed patch |
| `beforePatch(ID, T existing, T partial)` / `afterPatch(ID, T)` | Przed/po patch |
| `validateDelete(ID)` | Przed usunięciem |
| `beforeDelete(ID)` / `afterDelete(ID)` | Przed/po usunięciu |

### Merge (PATCH)

`merge(T existing, T partial)` — deep merge przez Jackson. Non-null pola z `partial` nadpisują `existing`. Override dla custom logiki.

---

## UuidFilterableController

**Klasa abstrakcyjna** — read-only REST controller z UUID.

```java
public abstract class UuidFilterableController<T extends HasUuid, ID>
```

Identyczne endpointy jak `FilterableController`, ale `GET /{uuid}` zamiast `GET /{id}`.

---

## CrudUuidFilterableController

**Klasa abstrakcyjna** — pełne CRUD z UUID.

```java
public abstract class CrudUuidFilterableController<T extends HasUuid, ID>
    extends UuidFilterableController<T, ID>
```

### Dodatkowe endpointy

| Metoda HTTP | Path | Opis |
|-------------|------|------|
| `POST` | `/` | Stwórz (auto-generuje UUID jeśli null) |
| `PUT` | `/{uuid}` | Full update po UUID |
| `PATCH` | `/{uuid}` | Partial update po UUID |
| `DELETE` | `/{uuid}` | Usuń po UUID |

Hooki CRUD przyjmują `UUID` zamiast `ID`:
- `validateCreate(T)`, `beforeCreate(T)`, `afterCreate(T)`
- `validateUpdate(UUID, T)`, `beforeUpdate(UUID, T)`, `afterUpdate(UUID, T)`
- `validatePatch(UUID, T)`, `beforePatch(UUID, T existing, T partial)`, `afterPatch(UUID, T)`
- `validateDelete(UUID)`, `beforeDelete(UUID)`, `afterDelete(UUID)`

---

## SearchRequest

**Record** — body dla `POST /search`.

```java
@Builder
public record SearchRequest(
    @Min(0) Integer page,
    @Min(1) Integer size,
    @Deprecated String sortField,
    @Deprecated Sort.Direction sortDirection,
    List<SortOrder> sort,
    List<FilterCriteria> filters,
    boolean unpaged
)
```

### Factory methods

| Metoda | Opis |
|--------|------|
| `SearchRequest.empty()` | Domyślne (page=0, size=20) |
| `SearchRequest.of(page, size)` | Z paginacją |
| `SearchRequest.withFilters(filters)` | Z filtrami |
| `SearchRequest.withSort(SortOrder...)` | Z sortowaniem |
| `SearchRequest.all()` | Unpaged |

---

## ExportRequest

**Record** — body dla `POST /export/{format}`.

```java
@Builder
public record ExportRequest(
    @Pattern(regexp = "^[a-zA-Z0-9_\\-. ]+$") String fileName,
    @NotNull @Valid SearchRequest searchRequest
)
```

---

## AsyncExportEvent

**Record** — event publikowany przy asynchronicznym eksporcie.

```java
public record AsyncExportEvent(
    UUID userId, UUID tenantId, String format, String requestedFileName,
    SearchParams searchParams, Locale locale, Map<String, String> labels,
    String repositoryName
)
```

---

## QueryControllersPort

**Interfejs SPI** — port dla kontrolerów potrzebujących kontekstu użytkownika i event publishing.

```java
public interface QueryControllersPort {
    UserContext getUserContext();
    <T> void publishEvent(T event);
}
```

---

## UserContext

**Record** — kontekst użytkownika.

```java
public record UserContext(UUID userId, UUID tenantId) {}
```

---

## Wyjątki

### FilteringException (bazowy)

```java
public class FilteringException extends RuntimeException {
    public FilteringException(String message);
    public FilteringException(String message, Throwable cause);
}
```

### InvalidFilterCriteriaException

```java
public class InvalidFilterCriteriaException extends FilteringException {
    public InvalidFilterCriteriaException(String field, String operation, String message);
    public String getField();
    public String getOperation();
}
```

### PropertyNotFoundException

```java
public class PropertyNotFoundException extends FilteringException {
    public PropertyNotFoundException(String propertyPath);
    public String getPropertyPath();
}
```

### TypeConversionException

```java
public class TypeConversionException extends FilteringException {
    public TypeConversionException(Class<?> sourceType, Class<?> targetType, String message);
    public Class<?> getSourceType();
    public Class<?> getTargetType();
}
```

Kontrolery automatycznie obsługują te wyjątki i zwracają `400 Bad Request`.
