---
name: preboot-securedata
description: "Skill do używania biblioteki preboot-securedata. Użyj tego skilla zawsze gdy użytkownik chce implementować multi-tenancy, izolację danych między tenantami, role-based access control na repozytorium, automatyczne audit fields (createdBy, createdAt, modifiedBy, modifiedAt), bezpieczne repozytorium z filtrowaniem po tenant ID, lifecycle events na repozytorium, lub rozszerza preboot-query o warstwę bezpieczeństwa. Obejmuje: SecureRepository, SecureUuidRepository, SecureRepositoryImpl, SecureUuidRepositoryImpl, @Tenant, @SecureAccess, @AccessRule, @CreatedBy, @CreatedAt, @ModifiedBy, @ModifiedAt, @DisableSecureEntity, SecurityContext, SecurityContextProvider, SecureRepositoryEvent (BeforeCreate/AfterCreate/BeforeUpdate/AfterUpdate/BeforeDelete/AfterDelete), SecureEntityMetadata, SecureRepositoryContext, SecureDataException. Triggeruje się na: multi-tenant, tenant isolation, tenant filtering, row-level security, RBAC, role-based access, access control, audit trail, audit fields, created by, modified by, secure repository, tenant ID, data isolation, cross-tenant, security context, security provider, entity lifecycle events, before create event, after delete event, secure CRUD, tenant-aware repository, preboot security, multi-tenant Spring Data JDBC."
---

# preboot-securedata

Moduł rozszerzający `preboot-query` o multi-tenant data isolation, role-based access control (RBAC) i automatyczne audit fields. Każde zapytanie jest automatycznie filtrowane po tenant ID, dostęp walidowany po rolach, a pola audytowe (createdBy/createdAt/modifiedBy/modifiedAt) wypełniane z SecurityContext.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-securedata</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Wymaga: `preboot-core`, `preboot-query`, `preboot-eventbus` (transitive), `spring-boot-starter-data-jdbc`, `postgresql`.

## Szybki start

### 1. Zaimplementuj SecurityContextProvider

```java
@Component
public class MySecurityContextProvider implements SecurityContextProvider {
    @Override
    public SecurityContext getCurrentContext() {
        return new SimpleSecurityContext(
            getCurrentUserId(),    // UUID
            getCurrentTenantId(),  // UUID
            getCurrentRoles(),     // Set<String>
            getCurrentPermissions() // Set<String>
        );
    }
}
```

### 2. Zdefiniuj encję z adnotacjami bezpieczeństwa

```java
@Table("documents")
@SecureAccess(
    read = @AccessRule(roles = {"VIEWER", "EDITOR"}),
    write = @AccessRule(roles = {"EDITOR"})
)
@Data
public class Document {
    @Id private Long id;

    @Tenant
    private UUID tenantId;

    private String title;
    private String content;

    @CreatedBy  private UUID createdBy;
    @CreatedAt  private Instant createdAt;
    @ModifiedBy private UUID modifiedBy;
    @ModifiedAt private Instant modifiedAt;
}
```

### 3. Stwórz repozytorium

```java
public interface DocumentRepository extends SecureRepository<Document, Long> {}

@Repository
class DocumentRepositoryImpl extends SecureRepositoryImpl<Document, Long> {
    public DocumentRepositoryImpl(SecureRepositoryContext context) {
        super(context, Document.class);
    }
}
```

### 4. Używaj — security jest automatyczny

```java
@Service
@RequiredArgsConstructor
public class DocumentService {
    private final DocumentRepository documentRepository;

    public Document create(String title) {
        Document doc = new Document();
        doc.setTitle(title);
        // tenantId, createdBy, createdAt — automatycznie z SecurityContext
        return documentRepository.save(doc);
    }

    public Page<Document> search(String status) {
        // Filtr tenantId dodawany automatycznie do każdego zapytania
        return documentRepository.findAll(
            SearchParams.criteria(FilterCriteria.eq("status", status)).build()
        );
    }
}
```

## Główne koncepty

### Architektura

```
SecureRepository<T, ID>
├── extends FilterableRepository<T, ID>    — preboot-query (CRUD + filtrowanie)
└── + security layer:
    ├── Tenant isolation                   — automatyczny filtr po tenantId
    ├── RBAC                               — walidacja ról read/write
    ├── Audit fields                       — auto-populate created/modified
    └── Lifecycle events                   — Before/After Create/Update/Delete

SecureUuidRepository<T extends HasUuid, ID>
├── extends FilterableUuidRepository<T, ID> — + findByUuid, deleteByUuid
└── + security layer (jak wyżej)
    └── + auto-generate UUID               — UUID generowany jeśli null
```

### Kluczowe klasy

| Klasa | Rola |
|-------|------|
| `SecureRepository<T, ID>` | Interfejs — SecureRepository = FilterableRepository + security |
| `SecureUuidRepository<T, ID>` | Interfejs — jak wyżej + UUID operacje |
| `SecureRepositoryImpl<T, ID>` | Implementacja bazowa — rozszerzasz ją w swoim repo |
| `SecureUuidRepositoryImpl<T, ID>` | Jak wyżej + UUID (auto-generate, findByUuid, deleteByUuid) |
| `SecureRepositoryContext` | `@Component` — agreguje zależności (FilterableFragmentContext + security) |
| `SecurityContextProvider` | Interfejs — implementujesz, dostarcza SecurityContext |
| `SecurityContext` | Interfejs — userId, tenantId, roles, permissions |
| `SimpleSecurityContext` | Gotowa implementacja SecurityContext |
| `SecureEntityMetadata<T>` | Cache metadanych adnotacji encji |
| `SecureEntityMetadataCache` | `@Component` — cache metadanych (ConcurrentHashMap) |
| `SecureRepositoryEvent<T>` | Sealed interface — 6 eventów lifecycle |
| `SecureDataException` | RuntimeException — access denied, tenant violation |

### Adnotacje

| Adnotacja | Cel | Wymagany typ pola |
|-----------|-----|--------------------|
| `@Tenant` | Pole tenant ID — auto-populate + filtrowanie | `UUID` |
| `@Tenant(required = false)` | Tenant opcjonalny (shared entities) | `UUID` |
| `@SecureAccess` | RBAC na klasie encji | — (na klasie) |
| `@AccessRule(roles = {...})` | Wymagane role | — (w @SecureAccess) |
| `@CreatedBy` | Auto-populate user ID przy tworzeniu | `UUID` |
| `@CreatedAt` | Auto-populate timestamp przy tworzeniu | `Instant` |
| `@ModifiedBy` | Auto-populate user ID przy update | `UUID` |
| `@ModifiedAt` | Auto-populate timestamp przy update | `Instant` |
| `@DisableSecureEntity` | Wyłącza security dla encji | — (na klasie) |

### Co dzieje się automatycznie

**Przy `save()` (nowa encja):**
1. Tenant ID ustawiany z SecurityContext (jeśli null)
2. Walidacja write access (RBAC)
3. `@CreatedBy` ← userId, `@CreatedAt` ← Instant.now()
4. Publikacja `BeforeCreateEvent` → save → `AfterCreateEvent`
5. (SecureUuidRepositoryImpl) UUID generowany jeśli null

**Przy `save()` (update):**
1. Tenant ID walidowany (musi pasować do bieżącego)
2. Walidacja write access (RBAC)
3. `@ModifiedBy` ← userId, `@ModifiedAt` ← Instant.now()
4. Publikacja `BeforeUpdateEvent` → save → `AfterUpdateEvent`

**Przy `findAll(SearchParams)`:**
1. Walidacja read access (RBAC)
2. Automatyczny filtr `tenantId = :currentTenantId` dodany do SearchParams

**Przy `delete()`:**
1. Walidacja tenant access (encja musi należeć do bieżącego tenanta)
2. Walidacja write access (RBAC)
3. Publikacja `BeforeDeleteEvent` → delete → `AfterDeleteEvent`

### Lifecycle events

```java
SecureRepositoryEvent<T> (sealed interface)
├── BeforeCreateEvent<T>   — przed save() nowej encji
├── AfterCreateEvent<T>    — po save() nowej encji
├── BeforeUpdateEvent<T>   — przed save() istniejącej
├── AfterUpdateEvent<T>    — po save() istniejącej
├── BeforeDeleteEvent<T>   — przed delete()
└── AfterDeleteEvent<T>    — po delete()
```

Obsługa przez `@EventHandler(typeParameter = EntityClass.class)` z preboot-eventbus.

### Zależności od innych modułów PreBoot

- **preboot-query** (wymagane) — FilterableRepository, SearchParams, FilterCriteria, FilterableFragmentImpl
- **preboot-eventbus** (wymagane) — EventPublisher, @EventHandler, GenericEvent
- **preboot-core** (wymagane) — JsonMapper, utilities

## Typowe przepływy

### Encja z UUID + pełna security

```java
@Table("orders")
@SecureAccess(
    read = @AccessRule(roles = {"USER", "ADMIN"}),
    write = @AccessRule(roles = {"ADMIN"})
)
@Data
public class Order implements HasUuid {
    @Id private Long id;
    private UUID uuid;

    @Tenant
    private UUID tenantId;

    private String orderNumber;
    private BigDecimal amount;

    @CreatedBy  private UUID createdBy;
    @CreatedAt  private Instant createdAt;
    @ModifiedBy private UUID modifiedBy;
    @ModifiedAt private Instant modifiedAt;

    @Override public UUID getUuid() { return uuid; }
    @Override public void setUuid(UUID uuid) { this.uuid = uuid; }
}

public interface OrderRepository extends SecureUuidRepository<Order, Long> {}

@Repository
class OrderRepositoryImpl extends SecureUuidRepositoryImpl<Order, Long> {
    public OrderRepositoryImpl(SecureRepositoryContext context) {
        super(context, Order.class);
    }
}
```

### Event handler

```java
@Component
public class OrderEventHandler {
    @EventHandler(typeParameter = Order.class)
    public void onBeforeCreate(SecureRepositoryEvent.BeforeCreateEvent<Order> event) {
        Order order = event.getEntity();
        // walidacja, wzbogacenie danych...
    }

    @EventHandler(typeParameter = Order.class)
    public void onAfterCreate(SecureRepositoryEvent.AfterCreateEvent<Order> event) {
        Order order = event.getEntity();
        // notyfikacje, audit log...
    }

    @EventHandler(typeParameter = Order.class)
    public void onAfterDelete(SecureRepositoryEvent.AfterDeleteEvent<Order> event) {
        // cleanup...
    }
}
```

### Migracja z FilterableRepository na SecureRepository

```java
// PRZED (preboot-query):
public interface DocRepo extends FilterableRepository<Document, Long> {}
class DocRepoImpl extends FilterableFragmentImpl<Document, Long> {
    DocRepoImpl(FilterableFragmentContext context) { super(context, Document.class); }
}

// PO (preboot-securedata):
public interface DocRepo extends SecureRepository<Document, Long> {}
class DocRepoImpl extends SecureRepositoryImpl<Document, Long> {
    DocRepoImpl(SecureRepositoryContext context) { super(context, Document.class); }
}
// + dodaj @Tenant, @SecureAccess, @CreatedBy etc. na encji
// + dodaj kolumny tenant_id, created_by, created_at do tabeli
```

## Pułapki i częste błędy

1. **Brak beana `SecurityContextProvider`** — moduł wymaga implementacji `SecurityContextProvider` jako Spring beana. Bez tego `SecureRepositoryContext` nie będzie wstrzyknięty.

2. **Brak beana `EventPublisher`** — `SecureRepositoryContext` wymaga `EventPublisher` (z preboot-eventbus). Musi być synchroniczny (`LocalEventPublisher`), nie asynchroniczny.

3. **Typy pól audytowych** — `@CreatedBy`/`@ModifiedBy` MUSZĄ być `UUID`. `@CreatedAt`/`@ModifiedAt` MUSZĄ być `Instant`. Inny typ → `SecureDataException` przy starcie.

4. **Próba ustawienia cudzego tenantId** — jeśli encja ma już tenantId ustawiony i nie pasuje do bieżącego z SecurityContext, `save()` rzuci `SecureDataException("Access denied")`.

5. **`deleteAll()` nie jest wspierane** — rzuca `SecureDataException`. Użyj `deleteById()` lub `deleteByUuid()` per encja.

6. **Brak roli → Access Denied** — jeśli `@SecureAccess` jest zdefiniowane, użytkownik MUSI mieć co najmniej jedną rolę z każdego `@AccessRule`. Brak `@SecureAccess` = brak restrykcji.

7. **Logika reguł dostępu** — wiele `@AccessRule` = AND (musi spełniać każdą regułę). Role w jednym `@AccessRule` = OR (wystarczy jedna rola). Np. `@AccessRule(roles = {"A", "B"})` = A OR B.

8. **`@DisableSecureEntity`** — wyłącza CAŁĄ security (tenant, RBAC, audit). Używaj ostrożnie.

9. **findById zwraca Optional.empty() zamiast wyjątku** — jeśli encja istnieje ale należy do innego tenanta, dostaniesz `Optional.empty()`, nie wyjątek.

10. **Nazwa Impl klasy** — jak w preboot-query: nazwa implementacji MUSI kończyć się na `Impl` i odpowiadać nazwie interfejsu repozytorium.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury metod, parametry SecurityContext, hierarchia klas, walidacja AccessRule, SecureEntityMetadata
- **examples.md** — kompletne przykłady: setup, encje z security, UUID repo, event handlers, migracja z preboot-query, testowanie z Testcontainers, SecurityContextProvider z JWT
