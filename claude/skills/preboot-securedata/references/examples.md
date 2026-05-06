# Examples — preboot-securedata

## Spis treści

- [1. Encja z tenant isolation — minimalny setup](#1-encja-z-tenant-isolation--minimalny-setup)
- [2. Encja z pełną security (RBAC + audit)](#2-encja-z-pełną-security-rbac--audit)
- [3. Encja z UUID + security](#3-encja-z-uuid--security)
- [4. SecurityContextProvider — implementacja produkcyjna (JWT)](#4-securitycontextprovider--implementacja-produkcyjna-jwt)
- [5. Tenant isolation — automatyczne filtrowanie](#5-tenant-isolation--automatyczne-filtrowanie)
- [6. Tenant isolation — przełączanie tenantów](#6-tenant-isolation--przełączanie-tenantów)
- [7. RBAC — kontrola dostępu](#7-rbac--kontrola-dostępu)
- [8. Audit fields — automatyczne śledzenie](#8-audit-fields--automatyczne-śledzenie)
- [9. Lifecycle events — event handlers](#9-lifecycle-events--event-handlers)
- [10. Lifecycle events — izolacja per typ encji](#10-lifecycle-events--izolacja-per-typ-encji)
- [11. UUID repository — auto-generate UUID](#11-uuid-repository--auto-generate-uuid)
- [12. Filtrowanie z preboot-query + security](#12-filtrowanie-z-preboot-query--security)
- [13. Projekcje z security](#13-projekcje-z-security)
- [14. @DisableSecureEntity — wyłączenie security](#14-disablesecureentity--wyłączenie-security)
- [15. @Tenant(required = false) — shared entities](#15-tenantrequired--false--shared-entities)
- [16. Migracja z FilterableRepository na SecureRepository](#16-migracja-z-filterablerepository-na-securerepository)
- [17. Testowanie z Testcontainers](#17-testowanie-z-testcontainers)
- [18. Test configuration — SecurityContextProvider](#18-test-configuration--securitycontextprovider)
- [19. Testowanie event handlers](#19-testowanie-event-handlers)
- [20. SQL schema — tabela z security](#20-sql-schema--tabela-z-security)

---

## 1. Encja z tenant isolation — minimalny setup

```java
// === Encja z @Tenant ===
@Table("documents")
@Data
public class Document {
    @Id
    private Long id;

    @Tenant
    private UUID tenantId;

    private String title;
}

// === Interfejs repozytorium ===
public interface DocumentRepository extends SecureRepository<Document, Long> {}

// === Implementacja ===
@Repository
class DocumentRepositoryImpl extends SecureRepositoryImpl<Document, Long> {
    public DocumentRepositoryImpl(SecureRepositoryContext context) {
        super(context, Document.class);
    }
}

// === SecurityContextProvider (wymagany bean) ===
@Component
public class AppSecurityContextProvider implements SecurityContextProvider {
    @Override
    public SecurityContext getCurrentContext() {
        return new SimpleSecurityContext(
            UUID.randomUUID(),             // userId
            UUID.fromString("..."),        // tenantId
            Set.of(),                      // roles
            Set.of()                       // permissions
        );
    }
}

// === Użycie ===
Document doc = new Document();
doc.setTitle("My Document");
// tenantId ustawiany automatycznie z SecurityContext
Document saved = documentRepository.save(doc);

// findAll automatycznie filtruje po tenantId
List<Document> docs = documentRepository.findAll(SearchParams.empty()).getContent();
// docs zawiera TYLKO dokumenty bieżącego tenanta
```

---

## 2. Encja z pełną security (RBAC + audit)

```java
@Table("documents")
@SecureAccess(
    read = @AccessRule(roles = {"VIEWER", "EDITOR"}),
    write = @AccessRule(roles = {"EDITOR"})
)
@Data
public class Document {
    @Id
    private Long id;

    @Tenant
    private UUID tenantId;

    private String title;
    private String content;
    private String status;

    // Audit fields — automatycznie wypełniane
    @CreatedBy
    private UUID createdBy;       // MUSI być UUID

    @CreatedAt
    private Instant createdAt;    // MUSI być Instant

    @ModifiedBy
    private UUID modifiedBy;      // MUSI być UUID

    @ModifiedAt
    private Instant modifiedAt;   // MUSI być Instant
}
```

---

## 3. Encja z UUID + security

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

// === SecureUuidRepository ===
public interface OrderRepository extends SecureUuidRepository<Order, Long> {}

@Repository
class OrderRepositoryImpl extends SecureUuidRepositoryImpl<Order, Long> {
    public OrderRepositoryImpl(SecureRepositoryContext context) {
        super(context, Order.class);
    }
}

// === Użycie — UUID generowany automatycznie ===
Order order = new Order();
order.setOrderNumber("ORD-001");
order.setAmount(new BigDecimal("100.00"));
// uuid, tenantId, createdBy, createdAt — wszystko automatyczne

Order saved = orderRepository.save(order);
// saved.getUuid() != null

// UUID operations z tenant isolation
Optional<Order> found = orderRepository.findByUuid(saved.getUuid());
boolean exists = orderRepository.existsByUuid(saved.getUuid());
orderRepository.deleteByUuid(saved.getUuid());
```

---

## 4. SecurityContextProvider — implementacja produkcyjna (JWT)

```java
@Component
public class JwtSecurityContextProvider implements SecurityContextProvider {
    private final JwtTokenProvider jwtTokenProvider;

    public JwtSecurityContextProvider(JwtTokenProvider jwtTokenProvider) {
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Override
    public SecurityContext getCurrentContext() {
        String token = getCurrentJwtToken(); // np. z SecurityContextHolder

        Claims claims = jwtTokenProvider.parseClaims(token);
        return new SimpleSecurityContext(
            UUID.fromString(claims.getSubject()),
            UUID.fromString(claims.get("tenantId", String.class)),
            new HashSet<>(claims.get("roles", List.class)),
            new HashSet<>(claims.get("permissions", List.class))
        );
    }

    private String getCurrentJwtToken() {
        // np. z Spring Security
        Authentication auth = org.springframework.security.core.context.SecurityContextHolder
            .getContext().getAuthentication();
        return ((JwtAuthenticationToken) auth).getToken().getTokenValue();
    }
}
```

---

## 5. Tenant isolation — automatyczne filtrowanie

```java
@Service
@RequiredArgsConstructor
public class DocumentService {
    private final DocumentRepository documentRepository;

    public Document createDocument(String title) {
        Document doc = new Document();
        doc.setTitle(title);
        // tenantId automatycznie ustawiany z SecurityContext
        return documentRepository.save(doc);
    }

    public Page<Document> findActiveDocuments() {
        // Filtr tenantId AUTOMATYCZNIE dodawany — nie musisz go dodawać sam
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("status", "ACTIVE")
        ).build();

        return documentRepository.findAll(params);
        // Wewnętrznie: WHERE status = 'ACTIVE' AND tenant_id = :currentTenantId
    }

    public Optional<Document> findById(Long id) {
        // findById sprawdza tenant po pobraniu — zwraca Optional.empty() jeśli inny tenant
        return documentRepository.findById(id);
    }

    public void deleteDocument(Long id) {
        // Usunie TYLKO jeśli dokument należy do bieżącego tenanta
        documentRepository.deleteById(id);
    }
}
```

---

## 6. Tenant isolation — przełączanie tenantów

```java
// Demonstracja izolacji danych między tenantami (typowe w testach)

// Tenant 1 widzi swoje dane
securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_1));
List<Document> tenant1Docs = documentRepository.findAll(SearchParams.empty()).getContent();
// tenant1Docs — tylko dokumenty TENANT_1

// Tenant 2 widzi swoje dane
securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_2));
List<Document> tenant2Docs = documentRepository.findAll(SearchParams.empty()).getContent();
// tenant2Docs — tylko dokumenty TENANT_2

// Dokumenty się nie nakładają
assertThat(tenant1Docs)
    .extracting(Document::getId)
    .doesNotContainAnyElementsOf(
        tenant2Docs.stream().map(Document::getId).toList()
    );

// Próba zapisu z cudzym tenantId → wyjątek
securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_1));
Document doc = new Document();
doc.setTenantId(TENANT_2); // ustawiam cudzy tenant!
assertThatExceptionOfType(SecureDataException.class)
    .isThrownBy(() -> documentRepository.save(doc))
    .withMessage("Access denied");
```

---

## 7. RBAC — kontrola dostępu

```java
// Encja z osobnymi regułami read/write
@Table("projects")
@SecureAccess(
    read = @AccessRule(roles = {"PROJECT_VIEWER", "PROJECT_MANAGER"}),
    write = @AccessRule(roles = {"PROJECT_MANAGER", "ADMIN"})
)
@Data
public class Project {
    @Id private Long id;
    @Tenant private UUID tenantId;
    private String name;
}

// Użytkownik z rolą PROJECT_VIEWER — może czytać, nie może pisać
SecurityContext viewerContext = new SimpleSecurityContext(
    userId, tenantId, Set.of("PROJECT_VIEWER"), Set.of()
);

// findAll — OK
Page<Project> projects = projectRepository.findAll(SearchParams.empty());

// save — SecureDataException: "Write access denied - insufficient privileges"
assertThatExceptionOfType(SecureDataException.class)
    .isThrownBy(() -> projectRepository.save(new Project()));

// Wiele @AccessRule = AND (użytkownik musi spełniać KAŻDĄ regułę)
@SecureAccess(
    read = {
        @AccessRule(roles = {"VIEWER", "EDITOR"}),   // musi mieć VIEWER lub EDITOR
        @AccessRule(roles = {"ACTIVE_USER"})          // I musi mieć ACTIVE_USER
    }
)
// Użytkownik z rolami {"VIEWER"} — READ DENIED (brak ACTIVE_USER)
// Użytkownik z rolami {"VIEWER", "ACTIVE_USER"} — READ OK
```

---

## 8. Audit fields — automatyczne śledzenie

```java
@Service
@RequiredArgsConstructor
public class DocumentService {
    private final DocumentRepository documentRepository;

    public Document createDocument(String title) {
        Document doc = new Document();
        doc.setTitle(title);

        Document saved = documentRepository.save(doc);

        // Po save():
        // saved.getCreatedBy()  == SecurityContext.getUserId()
        // saved.getCreatedAt()  == ~Instant.now()
        // saved.getModifiedBy() == null (bo nowa encja)
        // saved.getModifiedAt() == null (bo nowa encja)
        return saved;
    }

    public Document updateDocument(Long id, String newTitle) {
        Document doc = documentRepository.findById(id).orElseThrow();
        doc.setTitle(newTitle);

        Document saved = documentRepository.save(doc);

        // Po update():
        // saved.getCreatedBy()  == oryginalny userId (bez zmian)
        // saved.getCreatedAt()  == oryginalny timestamp (bez zmian)
        // saved.getModifiedBy() == SecurityContext.getUserId() (aktualny user)
        // saved.getModifiedAt() == ~Instant.now()
        return saved;
    }
}
```

---

## 9. Lifecycle events — event handlers

```java
@Component
public class DocumentEventHandler {

    @EventHandler(typeParameter = Document.class)
    public void onBeforeCreate(SecureRepositoryEvent.BeforeCreateEvent<Document> event) {
        Document doc = event.getEntity();
        // Walidacja, wzbogacenie danych przed zapisem
        if (doc.getTitle() == null) {
            throw new IllegalArgumentException("Title is required");
        }
    }

    @EventHandler(typeParameter = Document.class)
    public void onAfterCreate(SecureRepositoryEvent.AfterCreateEvent<Document> event) {
        Document doc = event.getEntity();
        // Notyfikacje, audit log, cache invalidation
        log.info("Document created: {} at {}", doc.getId(), event.getTimestamp());
    }

    @EventHandler(typeParameter = Document.class)
    public void onBeforeUpdate(SecureRepositoryEvent.BeforeUpdateEvent<Document> event) {
        Document doc = event.getEntity();
        // Np. archiwizacja poprzedniej wersji
    }

    @EventHandler(typeParameter = Document.class)
    public void onAfterUpdate(SecureRepositoryEvent.AfterUpdateEvent<Document> event) {
        // Np. indeksowanie w wyszukiwarce
    }

    @EventHandler(typeParameter = Document.class)
    public void onBeforeDelete(SecureRepositoryEvent.BeforeDeleteEvent<Document> event) {
        Document doc = event.getEntity();
        // Np. walidacja czy można usunąć
    }

    @EventHandler(typeParameter = Document.class)
    public void onAfterDelete(SecureRepositoryEvent.AfterDeleteEvent<Document> event) {
        Document doc = event.getEntity();
        // Cleanup: pliki, cache, powiązane dane
    }
}
```

---

## 10. Lifecycle events — izolacja per typ encji

Eventy są izolowane per typ encji — handler dla `Document` NIE dostanie eventów `Note`.

```java
// Handler dla Document
@Component
public class DocumentEventCollector {
    private final List<SecureRepositoryEvent<?>> events = new ArrayList<>();

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeCreate(SecureRepositoryEvent.BeforeCreateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterCreate(SecureRepositoryEvent.AfterCreateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeUpdate(SecureRepositoryEvent.BeforeUpdateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterUpdate(SecureRepositoryEvent.AfterUpdateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeDelete(SecureRepositoryEvent.BeforeDeleteEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterDelete(SecureRepositoryEvent.AfterDeleteEvent<Document> event) {
        events.add(event);
    }

    public List<SecureRepositoryEvent<?>> getEvents() { return new ArrayList<>(events); }
    public void clear() { events.clear(); }
}

// Użycie w teście:
documentRepository.save(newDocument);  // → 2 eventy (BeforeCreate, AfterCreate)
noteRepository.save(newNote);          // → 0 eventów w DocumentEventCollector
```

---

## 11. UUID repository — auto-generate UUID

```java
// SecureUuidRepositoryImpl automatycznie generuje UUID dla nowych encji

Order order = new Order();
order.setOrderNumber("ORD-001");
// order.getUuid() == null

Order saved = orderRepository.save(order);
// saved.getUuid() != null — auto-generated!

// Jeśli UUID podany, jest zachowany
Order order2 = new Order();
UUID customUuid = UUID.fromString("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa");
order2.setUuid(customUuid);
order2.setOrderNumber("ORD-002");

Order saved2 = orderRepository.save(order2);
// saved2.getUuid() == customUuid

// UUID operations z tenant isolation
Optional<Order> found = orderRepository.findByUuid(saved.getUuid());
// found.isPresent() == true (ten sam tenant)

// Przełącz tenant
securityContextHolder.setCurrentContext(new TestSecurityContext(OTHER_TENANT));
Optional<Order> notFound = orderRepository.findByUuid(saved.getUuid());
// notFound.isEmpty() == true (inny tenant!)

boolean exists = orderRepository.existsByUuid(saved.getUuid());
// exists == false (inny tenant!)
```

---

## 12. Filtrowanie z preboot-query + security

Wszystkie operatory preboot-query działają z automatycznym tenant filtering:

```java
// Proste filtrowanie — tenant dodawany automatycznie
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "ACTIVE"),
    FilterCriteria.gt("amount", new BigDecimal("100"))
).build();

Page<Document> docs = documentRepository.findAll(params);
// SQL: WHERE status = 'ACTIVE' AND amount > 100 AND tenant_id = :tenantId

// OR/AND z security
SearchParams params = SearchParams.criteria(
    FilterCriteria.or(List.of(
        FilterCriteria.eq("status", "ACTIVE"),
        FilterCriteria.eq("status", "PENDING")
    ))
).build();

// Paginacja + sortowanie + security
SearchParams params = SearchParams.builder()
    .page(0)
    .size(20)
    .sort(List.of(SortOrder.desc("createdAt")))
    .filters(List.of(FilterCriteria.like("title", "Report")))
    .build();

Page<Document> docs = documentRepository.findAll(params);

// count z security
long count = documentRepository.count(
    SearchParams.criteria(FilterCriteria.eq("status", "ACTIVE")).build()
);

// findOne z security
Optional<Document> doc = documentRepository.findOne(
    SearchParams.criteria(FilterCriteria.eq("title", "My Doc")).build()
);
```

---

## 13. Projekcje z security

```java
// Interfejs projekcji
public interface DocumentSummary {
    String getTitle();
    Instant getCreatedAt();

    @Value("#{target.createdBy}")
    UUID getCreatedBy();

    @Value("#{target.title + ' (Created: ' + target.createdAt + ')'}")
    String getDisplayName();
}

// Projekcja z security — tenant filtering automatyczny
Page<DocumentSummary> summaries = documentRepository.findAllProjectedBy(
    SearchParams.builder()
        .sort(List.of(SortOrder.desc("createdAt")))
        .build(),
    DocumentSummary.class
);
```

---

## 14. @DisableSecureEntity — wyłączenie security

```java
// Encja z wyłączonym security — zachowuje się jak zwykły FilterableRepository
@Table("public_settings")
@DisableSecureEntity
@Data
public class PublicSetting {
    @Id private Long id;
    private String key;
    private String value;
}

public interface PublicSettingRepository extends SecureRepository<PublicSetting, Long> {}

@Repository
class PublicSettingRepositoryImpl extends SecureRepositoryImpl<PublicSetting, Long> {
    public PublicSettingRepositoryImpl(SecureRepositoryContext context) {
        super(context, PublicSetting.class);
    }
}

// Brak tenant filtering, brak RBAC, brak audit
publicSettingRepository.findAll(SearchParams.empty()); // zwraca WSZYSTKIE rekordy
```

---

## 15. @Tenant(required = false) — shared entities

```java
// Encja z opcjonalnym tenantem — np. shared/global data
@Table("templates")
@Data
public class Template {
    @Id private Long id;

    @Tenant(required = false)  // NIE filtruje po tenant automatycznie
    private UUID tenantId;

    private String name;
    private String content;
}
```

---

## 16. Migracja z FilterableRepository na SecureRepository

### Krok 1: Zmień interfejs i implementację

```java
// PRZED (preboot-query):
public interface DocumentRepository extends FilterableRepository<Document, Long> {}

@Repository
class DocumentRepositoryImpl extends FilterableFragmentImpl<Document, Long> {
    public DocumentRepositoryImpl(FilterableFragmentContext context) {
        super(context, Document.class);
    }
}

// PO (preboot-securedata):
public interface DocumentRepository extends SecureRepository<Document, Long> {}

@Repository
class DocumentRepositoryImpl extends SecureRepositoryImpl<Document, Long> {
    public DocumentRepositoryImpl(SecureRepositoryContext context) {
        super(context, Document.class);  // SecureRepositoryContext zamiast FilterableFragmentContext
    }
}
```

### Krok 2: Dodaj adnotacje na encji

```java
// PRZED:
@Table("documents")
@Data
public class Document {
    @Id private Long id;
    private String title;
}

// PO:
@Table("documents")
@SecureAccess(read = @AccessRule(roles = {"USER"}))
@Data
public class Document {
    @Id private Long id;

    @Tenant
    private UUID tenantId;

    private String title;

    @CreatedBy  private UUID createdBy;
    @CreatedAt  private Instant createdAt;
    @ModifiedBy private UUID modifiedBy;
    @ModifiedAt private Instant modifiedAt;
}
```

### Krok 3: Migracja bazy danych

```sql
ALTER TABLE documents ADD COLUMN tenant_id UUID NOT NULL;
ALTER TABLE documents ADD COLUMN created_by UUID;
ALTER TABLE documents ADD COLUMN created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE documents ADD COLUMN modified_by UUID;
ALTER TABLE documents ADD COLUMN modified_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);
```

### Krok 4: Dodaj SecurityContextProvider i EventPublisher

```java
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityContextProvider securityContextProvider() {
        return new MySecurityContextProvider();
    }

    @Bean
    @Lazy
    LocalEventHandlerRepository localEventHandlerRepository(ApplicationContext ctx) {
        return new LocalEventHandlerRepository(ctx);
    }

    @Bean
    public EventPublisher eventPublisher(LocalEventHandlerRepository repo) {
        return new LocalEventPublisher(repo); // MUSI być synchroniczny!
    }
}
```

---

## 17. Testowanie z Testcontainers

```java
// === TestContainers config ===
@TestConfiguration
public class TestContainersConfig {
    @Bean
    @ServiceConnection
    PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    }
}

// === Integration test ===
@SpringBootTest
@Import({TestSecurityConfig.class, TestContainersConfig.class})
@Transactional
@Sql("/secure-test-data.sql")
class DocumentRepositoryTest {

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private TestSecurityContextHolder securityContextHolder;

    private static final UUID TENANT_1 = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final UUID TENANT_2 = UUID.fromString("22222222-2222-2222-2222-222222222222");

    @BeforeEach
    void setUp() {
        securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_1));
    }

    @Test
    void save_ShouldSetTenantId() {
        Document doc = new Document();
        doc.setTitle("New Document");

        Document saved = documentRepository.save(doc);

        assertThat(saved.getTenantId()).isEqualTo(TENANT_1);
    }

    @Test
    void findAll_ShouldOnlyReturnDocumentsForCurrentTenant() {
        List<Document> docs = documentRepository.findAll(SearchParams.empty()).getContent();

        assertThat(docs)
            .isNotEmpty()
            .allMatch(doc -> TENANT_1.equals(doc.getTenantId()));
    }

    @Test
    void findById_ShouldRespectTenantIsolation() {
        Document doc = new Document();
        doc.setTitle("Test");
        Document saved = documentRepository.save(doc);

        // Ten sam tenant — widzi
        assertThat(documentRepository.findById(saved.getId())).isPresent();

        // Inny tenant — nie widzi
        securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_2));
        assertThat(documentRepository.findById(saved.getId())).isEmpty();
    }

    @Test
    void delete_ShouldOnlyDeleteIfBelongsToCurrentTenant() {
        Document doc = new Document();
        doc.setTitle("To Delete");
        Document saved = documentRepository.save(doc);

        // Próba usunięcia z innego tenanta — nic się nie dzieje
        securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_2));
        documentRepository.deleteById(saved.getId());

        // Dokument nadal istnieje
        securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_1));
        assertThat(documentRepository.findById(saved.getId())).isPresent();

        // Usunięcie z poprawnego tenanta
        documentRepository.deleteById(saved.getId());
        assertThat(documentRepository.findById(saved.getId())).isEmpty();
    }

    @Test
    void save_WithWrongTenantId_ShouldThrow() {
        Document doc = new Document();
        doc.setTitle("Test");
        doc.setTenantId(TENANT_2); // ustawiam cudzy tenant!

        assertThatExceptionOfType(SecureDataException.class)
            .isThrownBy(() -> documentRepository.save(doc))
            .withMessage("Access denied");
    }
}
```

---

## 18. Test configuration — SecurityContextProvider

```java
// === Testowy SecurityContext ===
class TestSecurityContext implements SecurityContext {
    private final UUID tenantId;

    TestSecurityContext(UUID tenantId) {
        this.tenantId = tenantId;
    }

    @Override public UUID getUserId() { return UUID.randomUUID(); }
    @Override public UUID getTenantId() { return tenantId; }
    @Override public Set<String> getRoles() { return new HashSet<>(); }
    @Override public Set<String> getPermissions() { return new HashSet<>(); }
}

// === Testowy SecurityContextProvider z możliwością przełączania kontekstu ===
@Component
class TestSecurityContextHolder implements SecurityContextProvider {
    private SecurityContext currentContext;

    public void setCurrentContext(SecurityContext context) {
        this.currentContext = context;
    }

    @Override
    public SecurityContext getCurrentContext() {
        return currentContext;
    }
}

// === Test configuration ===
@TestConfiguration
public class TestSecurityConfig {
    @Bean
    @Primary
    public TestSecurityContextHolder securityContextHolder() {
        return new TestSecurityContextHolder();
    }

    @Bean
    @Lazy
    LocalEventHandlerRepository localEventHandlerRepository(ApplicationContext applicationContext) {
        return new LocalEventHandlerRepository(applicationContext);
    }

    @Bean
    public EventPublisher eventPublisher(LocalEventHandlerRepository localEventHandlerRepository) {
        return new LocalEventPublisher(localEventHandlerRepository);
    }
}
```

---

## 19. Testowanie event handlers

```java
// === Event collector do testów ===
@Component
public class DocumentEventCollector {
    private final List<SecureRepositoryEvent<?>> events = new ArrayList<>();

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeCreate(SecureRepositoryEvent.BeforeCreateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterCreate(SecureRepositoryEvent.AfterCreateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeUpdate(SecureRepositoryEvent.BeforeUpdateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterUpdate(SecureRepositoryEvent.AfterUpdateEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleBeforeDelete(SecureRepositoryEvent.BeforeDeleteEvent<Document> event) {
        events.add(event);
    }

    @EventHandler(typeParameter = Document.class)
    public void handleAfterDelete(SecureRepositoryEvent.AfterDeleteEvent<Document> event) {
        events.add(event);
    }

    public List<SecureRepositoryEvent<?>> getEvents() { return new ArrayList<>(events); }
    public void clear() { events.clear(); }
}

// === Test ===
@SpringBootTest
@Import({TestSecurityConfig.class, TestContainersConfig.class, EventTestConfig.class})
@Transactional
class DocumentEventTest {

    @Autowired private DocumentRepository documentRepository;
    @Autowired private DocumentEventCollector eventCollector;
    @Autowired private TestSecurityContextHolder securityContextHolder;

    @BeforeEach
    void setUp() {
        securityContextHolder.setCurrentContext(new TestSecurityContext(TENANT_1));
        eventCollector.clear();
    }

    @Test
    void save_NewEntity_ShouldTriggerCreateEvents() {
        Document doc = new Document();
        doc.setTitle("Event Test");

        Document saved = documentRepository.save(doc);

        assertThat(eventCollector.getEvents())
            .hasSize(2)
            .extracting("class")
            .containsExactly(
                SecureRepositoryEvent.BeforeCreateEvent.class,
                SecureRepositoryEvent.AfterCreateEvent.class
            );

        var afterEvent = (SecureRepositoryEvent.AfterCreateEvent<Document>)
            eventCollector.getEvents().get(1);
        assertThat(afterEvent.getEntity().getId()).isEqualTo(saved.getId());
    }

    @Test
    void save_ExistingEntity_ShouldTriggerUpdateEvents() {
        Document doc = new Document();
        doc.setTitle("Original");
        Document saved = documentRepository.save(doc);
        eventCollector.clear();

        saved.setTitle("Updated");
        documentRepository.save(saved);

        assertThat(eventCollector.getEvents())
            .hasSize(2)
            .extracting("class")
            .containsExactly(
                SecureRepositoryEvent.BeforeUpdateEvent.class,
                SecureRepositoryEvent.AfterUpdateEvent.class
            );
    }

    @Test
    void delete_ShouldTriggerDeleteEvents() {
        Document doc = new Document();
        doc.setTitle("To Delete");
        Document saved = documentRepository.save(doc);
        eventCollector.clear();

        documentRepository.delete(saved);

        assertThat(eventCollector.getEvents())
            .hasSize(2)
            .extracting("class")
            .containsExactly(
                SecureRepositoryEvent.BeforeDeleteEvent.class,
                SecureRepositoryEvent.AfterDeleteEvent.class
            );
    }

    @TestConfiguration
    static class EventTestConfig {
        @Bean
        DocumentEventCollector documentEventCollector() {
            return new DocumentEventCollector();
        }
    }
}
```

---

## 20. SQL schema — tabela z security

```sql
-- Tabela z pełnym zestawem kolumn security
CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    tenant_id   UUID         NOT NULL,
    uuid        UUID         NOT NULL DEFAULT gen_random_uuid(),
    title       VARCHAR(255) NOT NULL,
    content     TEXT,
    status      VARCHAR(50),
    created_by  UUID,
    created_at  TIMESTAMP WITH TIME ZONE,
    modified_by UUID,
    modified_at TIMESTAMP WITH TIME ZONE
);

-- Indeksy — kluczowe dla wydajności
CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX idx_documents_uuid ON documents(uuid);
CREATE UNIQUE INDEX idx_documents_tenant_uuid ON documents(tenant_id, uuid);

-- Minimalna tabela (tylko tenant)
CREATE TABLE notes (
    id        BIGSERIAL PRIMARY KEY,
    tenant_id UUID         NOT NULL,
    content   TEXT         NOT NULL
);

CREATE INDEX idx_notes_tenant_id ON notes(tenant_id);

-- Dane testowe
INSERT INTO documents (tenant_id, title)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Tenant 1 Document 1'),
    ('11111111-1111-1111-1111-111111111111', 'Tenant 1 Document 2'),
    ('22222222-2222-2222-2222-222222222222', 'Tenant 2 Document 1'),
    ('22222222-2222-2222-2222-222222222222', 'Tenant 2 Document 2');
```
