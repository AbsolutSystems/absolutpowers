# API Reference — preboot-securedata

Pakiety: `io.preboot.securedata.annotation`, `io.preboot.securedata.context`, `io.preboot.securedata.event`, `io.preboot.securedata.exception`, `io.preboot.securedata.metadata`, `io.preboot.securedata.repository`

## Spis treści

- [Adnotacje](#adnotacje)
  - [@Tenant](#tenant)
  - [@SecureAccess](#secureaccess)
  - [@AccessRule](#accessrule)
  - [@CreatedBy](#createdby)
  - [@CreatedAt](#createdat)
  - [@ModifiedBy](#modifiedby)
  - [@ModifiedAt](#modifiedat)
  - [@DisableSecureEntity](#disablesecureentity)
- [SecurityContext (interfejs)](#securitycontext)
- [SecurityContextProvider (interfejs)](#securitycontextprovider)
- [SimpleSecurityContext (klasa)](#simplesecuritycontext)
- [TestSecurityContextProvider (klasa)](#testsecuritycontextprovider)
- [SecureRepository (interfejs)](#securerepository)
- [SecureUuidRepository (interfejs)](#secureuuidrepository)
- [SecureRepositoryImpl (klasa)](#securerepositoryimpl)
- [SecureUuidRepositoryImpl (klasa)](#secureuuidrepositoryimpl)
- [SecureRepositoryContext (klasa)](#securerepositorycontext)
- [SecureRepositoryEvent (sealed interface)](#securerepositoryevent)
- [SecureEntityMetadata (klasa)](#secureentitymetadata)
- [SecureEntityMetadataCache (klasa)](#secureentitymetadatacache)
- [SecureDataException (wyjątek)](#securedataexception)

---

## Adnotacje

### @Tenant

**Adnotacja na polu** — oznacza pole tenant ID. Pole musi być typu `UUID`.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Tenant {
    boolean required() default true;
}
```

| Parametr | Default | Opis |
|----------|---------|------|
| `required` | `true` | Czy filtrowanie po tenant jest wymagane. `false` = shared/global entity |

Zachowanie:
- `save()` nowej encji → jeśli null, auto-populate z `SecurityContext.getTenantId()`
- `save()` z ustawionym tenantId ≠ bieżący → `SecureDataException("Access denied")`
- `findAll()` → automatyczny filtr `tenantId = :currentTenantId`
- `findById()` → post-fetch walidacja (zwraca `Optional.empty()` jeśli inny tenant)
- `delete()` → walidacja przed usunięciem

---

### @SecureAccess

**Adnotacja na klasie encji** — definiuje RBAC read/write.

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface SecureAccess {
    AccessRule[] read() default {};
    AccessRule[] write() default {};
}
```

| Parametr | Opis |
|----------|------|
| `read` | Reguły dostępu dla operacji odczytu (findAll, findOne, findById, count) |
| `write` | Reguły dostępu dla operacji zapisu (save, delete) |

Brak `@SecureAccess` = brak restrykcji RBAC (ale tenant isolation nadal działa).

---

### @AccessRule

**Adnotacja** — pojedyncza reguła dostępu, używana w `@SecureAccess`.

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface AccessRule {
    String[] roles() default {};
}
```

**Logika walidacji:**
- Role w jednym `@AccessRule` = **OR** — użytkownik musi mieć co najmniej jedną rolę
- Wiele `@AccessRule` = **AND** — użytkownik musi spełniać każdą regułę

Przykład:
```java
@SecureAccess(
    read = {
        @AccessRule(roles = {"VIEWER", "EDITOR"}),    // musi mieć VIEWER lub EDITOR
        @AccessRule(roles = {"ACTIVE_USER"})           // I musi mieć ACTIVE_USER
    },
    write = @AccessRule(roles = {"EDITOR"})
)
```

---

### @CreatedBy

**Adnotacja na polu** — automatycznie ustawiana na `SecurityContext.getUserId()` przy tworzeniu encji. Pole MUSI być typu `UUID`.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface CreatedBy {}
```

---

### @CreatedAt

**Adnotacja na polu** — automatycznie ustawiana na `Instant.now()` przy tworzeniu encji. Pole MUSI być typu `Instant`.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface CreatedAt {}
```

---

### @ModifiedBy

**Adnotacja na polu** — automatycznie ustawiana na `SecurityContext.getUserId()` przy update. Pole MUSI być typu `UUID`.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface ModifiedBy {}
```

---

### @ModifiedAt

**Adnotacja na polu** — automatycznie ustawiana na `Instant.now()` przy update. Pole MUSI być typu `Instant`.

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface ModifiedAt {}
```

---

### @DisableSecureEntity

**Adnotacja na klasie encji** — wyłącza całą warstwę security (tenant, RBAC, audit) dla tej encji.

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface DisableSecureEntity {}
```

Gdy obecna, `SecureEntityMetadata.isEnabled()` zwraca `false` i wszystkie operacje działają jak w zwykłym `FilterableRepository`.

---

## SecurityContext

**Interfejs** — dostarcza informacje o bieżącym użytkowniku i tenancie.

```java
public interface SecurityContext {
    UUID getUserId();
    UUID getTenantId();
    Set<String> getRoles();
    Set<String> getPermissions();
}
```

| Metoda | Opis |
|--------|------|
| `getUserId()` | ID bieżącego użytkownika (używany w @CreatedBy/@ModifiedBy) |
| `getTenantId()` | ID tenanta (używany w @Tenant auto-populate i filtrowaniu) |
| `getRoles()` | Role użytkownika (walidowane przez @AccessRule) |
| `getPermissions()` | Uprawnienia (dostępne, ale nie walidowane automatycznie) |

---

## SecurityContextProvider

**Interfejs** — dostarczyciel SecurityContext. Musisz go zaimplementować jako Spring `@Component`.

```java
public interface SecurityContextProvider {
    SecurityContext getCurrentContext();
}
```

---

## SimpleSecurityContext

**Klasa** — gotowa implementacja `SecurityContext`.

```java
public class SimpleSecurityContext implements SecurityContext {
    public SimpleSecurityContext(UUID userId, UUID tenantId, Set<String> roles, Set<String> permissions);

    // Getters
    public UUID getUserId();
    public UUID getTenantId();
    public Set<String> getRoles();
    public Set<String> getPermissions();
}
```

---

## TestSecurityContextProvider

**Klasa** — testowa implementacja `SecurityContextProvider`. Generuje random userId/tenantId jeśli nie podane.

```java
@Getter
public class TestSecurityContextProvider implements SecurityContextProvider {
    public TestSecurityContextProvider(UUID userId, UUID tenantId, Set<String> roles, Set<String> permissions);
    public TestSecurityContextProvider(Set<String> roles, Set<String> permissions);

    @Override
    public SecurityContext getCurrentContext();
}
```

---

## SecureRepository

**Interfejs** — marker rozszerzający `FilterableRepository` o security. Nie definiuje dodatkowych metod.

```java
@NoRepositoryBean
public interface SecureRepository<T, ID> extends FilterableRepository<T, ID> {}
```

Dziedziczy wszystkie metody z `FilterableRepository` (CrudRepository + FilterableFragment):
- `findAll(SearchParams)`, `findOne(SearchParams)`, `count(SearchParams)`
- `findAllProjectedBy(SearchParams, Class)`, `findOneProjectedBy(SearchParams, Class)`
- `save()`, `findById()`, `deleteById()`, etc.

---

## SecureUuidRepository

**Interfejs** — SecureRepository + operacje UUID.

```java
@NoRepositoryBean
public interface SecureUuidRepository<T extends HasUuid, ID> extends FilterableUuidRepository<T, ID> {}
```

Dodatkowe metody (z `UuidRepository`):
- `findByUuid(UUID)` → `Optional<T>`
- `existsByUuid(UUID)` → `boolean`
- `deleteByUuid(UUID)` → `void`

---

## SecureRepositoryImpl

**Klasa abstrakcyjna** — bazowa implementacja z pełną logiką security. Rozszerzasz ją w swoim repozytorium.

```java
public abstract class SecureRepositoryImpl<T, ID> extends FilterableFragmentImpl<T, ID>
```

### Konstruktor

```java
protected SecureRepositoryImpl(SecureRepositoryContext context, Class<T> entityType)
```

### Nadpisane metody z security

| Metoda | Security |
|--------|----------|
| `findAll(SearchParams)` | Read access + tenant filter |
| `findOne(SearchParams)` | Read access + tenant filter |
| `count(SearchParams)` | Read access + tenant filter |
| `findAll()` | Deleguje do `findAll(SearchParams.empty())` |
| `count()` | Deleguje do `count(SearchParams.empty())` |
| `findById(ID)` | Read access + tenant post-check |
| `existsById(ID)` | Deleguje do `findById()` |
| `findAllById(Iterable<ID>)` | Read access + tenant post-filter |
| `save(S entity)` | Tenant populate + write access + audit fields + events |
| `saveAll(Iterable<S>)` | Jak save() per encja |
| `delete(T)` | Tenant check + write access + events |
| `deleteById(ID)` | findById() → delete() |
| `deleteAllById(Iterable)` | deleteById() per ID |
| `deleteAll(Iterable)` | delete() per encja |
| `deleteAll()` | **THROWS** `SecureDataException` — nie wspierane |

### Logika save()

```
1. populateTenantId()     — ustawia tenant z SecurityContext jeśli null, waliduje jeśli ustawiony
2. validateWriteAccess()  — sprawdza @AccessRule write
3. populateAuditFields()  — @CreatedBy/@CreatedAt (new) lub @ModifiedBy/@ModifiedAt (update)
4. publish BeforeCreate/BeforeUpdate event
5. super.save()
6. publish AfterCreate/AfterUpdate event
```

### Logika findAll(SearchParams)

```
1. validateReadAccess()         — sprawdza @AccessRule read
2. addSecurityConstraints()     — dodaje FilterCriteria.eq("tenantId", currentTenantId)
3. super.findAll(secureParams)
```

---

## SecureUuidRepositoryImpl

**Klasa abstrakcyjna** — jak `SecureRepositoryImpl` ale dla encji UUID. Rozszerza `FilterableUuidFragmentImpl`.

```java
public abstract class SecureUuidRepositoryImpl<T extends HasUuid, ID>
    extends FilterableUuidFragmentImpl<T, ID>
```

### Konstruktor

```java
protected SecureUuidRepositoryImpl(SecureRepositoryContext context, Class<T> entityType)
```

### Dodatkowe/zmienione metody

| Metoda | Różnica vs SecureRepositoryImpl |
|--------|------|
| `save(S entity)` | Jeśli `entity.getUuid() == null` → `entity.setUuid(UUID.randomUUID())` |
| `saveAll(Iterable<S>)` | Jak wyżej per encja |
| `findByUuid(UUID)` | Read access + tenant post-check → `Optional.empty()` jeśli inny tenant |
| `existsByUuid(UUID)` | Deleguje do `findByUuid()` |
| `deleteByUuid(UUID)` | `findByUuid()` → `delete()` |

---

## SecureRepositoryContext

**Klasa `@Component`** — agreguje wszystkie zależności potrzebne do `SecureRepositoryImpl`.

```java
@Component
@Getter
@RequiredArgsConstructor
public class SecureRepositoryContext {
    private final FilterableFragmentContext filterableContext;
    private final SecurityContextProvider securityContextProvider;
    private final SecureEntityMetadataCache metadataCache;
    private final EventPublisher eventPublisher;
}
```

Wszystkie zależności auto-konfigurowane przez Spring Boot. `EventPublisher` musi być synchroniczny.

---

## SecureRepositoryEvent

**Sealed interface** — eventy lifecycle repozytorium. Rozszerza `GenericEvent<T>` z preboot-eventbus.

```java
public sealed interface SecureRepositoryEvent<T> extends GenericEvent<T> {
    T getEntity();
    LocalDateTime getTimestamp();

    record BeforeCreateEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public BeforeCreateEvent(T entity);  // timestamp = LocalDateTime.now()
    }
    record AfterCreateEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public AfterCreateEvent(T entity);
    }
    record BeforeUpdateEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public BeforeUpdateEvent(T entity);
    }
    record AfterUpdateEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public AfterUpdateEvent(T entity);
    }
    record BeforeDeleteEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public BeforeDeleteEvent(T entity);
    }
    record AfterDeleteEvent<T>(T entity, LocalDateTime timestamp) implements SecureRepositoryEvent<T> {
        public AfterDeleteEvent(T entity);
    }
}
```

Obsługa eventów przez `@EventHandler(typeParameter = EntityClass.class)`:
```java
@EventHandler(typeParameter = Order.class)
public void handle(SecureRepositoryEvent.AfterCreateEvent<Order> event) {
    Order created = event.getEntity();
}
```

**Ważne:** `typeParameter` musi wskazywać na klasę encji (np. `Order.class`), NIE na `SecureRepositoryEvent.class`.

---

## SecureEntityMetadata

**Klasa** — metadane security encji. Tworzona refleksyjnie, cache'owana przez `SecureEntityMetadataCache`.

```java
@Getter
public class SecureEntityMetadata<T> {
    public SecureEntityMetadata(Class<T> entityType);

    public Class<T> getEntityType();
    public boolean isEnabled();         // false jeśli @DisableSecureEntity
    public Field getTenantField();      // pole z @Tenant (lub null)
    public Field getCreatedByField();
    public Field getCreatedAtField();
    public Field getModifiedByField();
    public Field getModifiedAtField();
    public AccessRule[] getReadRules();
    public AccessRule[] getWriteRules();

    public boolean hasTenantField();
    public boolean requiresTenant();    // hasTenantField() && @Tenant.required == true
    public boolean hasCreatedByField();
    public boolean hasCreatedAtField();
    public boolean hasModifiedByField();
    public boolean hasModifiedAtField();
}
```

Walidacja przy tworzeniu:
- `@CreatedAt`/`@ModifiedAt` na polu nie-`Instant` → `SecureDataException`
- `@CreatedBy`/`@ModifiedBy` na polu nie-`UUID` → `SecureDataException`

---

## SecureEntityMetadataCache

**Klasa `@Component`** — cache metadanych encji.

```java
@Component
public class SecureEntityMetadataCache {
    public <T> SecureEntityMetadata<T> get(Class<T> entityType);
}
```

Thread-safe (`ConcurrentHashMap`). Metadata tworzona lazy — raz per typ encji.

---

## SecureDataException

**Wyjątek** — RuntimeException dla błędów security.

```java
public class SecureDataException extends RuntimeException {
    public SecureDataException(String message);
    public SecureDataException(String message, Throwable cause);
}
```

Rzucany gdy:
- Access denied (read/write RBAC)
- Tenant violation (próba dostępu do danych innego tenanta)
- Bulk `deleteAll()` na secure repository
- Nieprawidłowy typ pola audytowego
- Błąd refleksji przy ustawianiu pól
