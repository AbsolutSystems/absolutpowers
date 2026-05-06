# Examples — preboot-query

## Spis treści

- [1. Encja i repozytorium — minimalny setup](#1-encja-i-repozytorium--minimalny-setup)
- [2. Encja z UUID](#2-encja-z-uuid)
- [3. Filtrowanie — wszystkie operatory](#3-filtrowanie--wszystkie-operatory)
- [4. Złożone warunki OR/AND](#4-złożone-warunki-orand)
- [5. Paginacja i sortowanie](#5-paginacja-i-sortowanie)
- [6. Multi-field sorting](#6-multi-field-sorting)
- [7. Nested filtering (relacje)](#7-nested-filtering-relacje)
- [8. Projekcje — proste pola](#8-projekcje--proste-pola)
- [9. Projekcje — SpEL z obliczonymi polami](#9-projekcje--spel-z-obliczonymi-polami)
- [10. Projekcje — kolekcje (nested items)](#10-projekcje--kolekcje-nested-items)
- [11. @AggregateReference — JOIN do innego agregatu](#11-aggregatereference--join-do-innego-agregatu)
- [12. Złożone projekcje z @AggregateReference i kolekcjami](#12-złożone-projekcje-z-aggregatereference-i-kolekcjami)
- [13. Database views](#13-database-views)
- [14. REST controller — read-only](#14-rest-controller--read-only)
- [15. REST controller — pełne CRUD](#15-rest-controller--pełne-crud)
- [16. REST controller — CRUD z UUID](#16-rest-controller--crud-z-uuid)
- [17. REST controller — hooki CRUD](#17-rest-controller--hooki-crud)
- [18. REST API — JSON request/response](#18-rest-api--json-requestresponse)
- [19. Filtrowanie po enum](#19-filtrowanie-po-enum)
- [20. Stream i unpaged](#20-stream-i-unpaged)
- [21. Eksport danych](#21-eksport-danych)
- [22. Testowanie z Testcontainers](#22-testowanie-z-testcontainers)

---

## 1. Encja i repozytorium — minimalny setup

```java
// === Encja ===
@Table("orders")
@Data
public class Order {
    @Id
    private Long id;
    private String orderNumber;
    private BigDecimal amount;
    private String status;
    private LocalDateTime createdAt;

    @MappedCollection(idColumn = "order_id")
    private Set<OrderItem> orderItems = new HashSet<>();
}

@Table("order_items")
@Data
public class OrderItem {
    @Id
    private Long id;
    private String productCode;
    private Integer quantity;
    private BigDecimal unitPrice;
    private BigDecimal totalPrice;
}

// === Interfejs repozytorium ===
public interface OrderRepository extends FilterableRepository<Order, Long> {}

// === Implementacja — nazwa MUSI kończyć się na Impl i odpowiadać interfejsowi ===
@Repository
class OrderRepositoryImpl extends FilterableFragmentImpl<Order, Long> {
    public OrderRepositoryImpl(FilterableFragmentContext context) {
        super(context, Order.class);
    }
}

// === Użycie ===
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;

    public Page<Order> getActiveOrders() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("status", "ACTIVE")
        ).build();
        return orderRepository.findAll(params);
    }
}
```

---

## 2. Encja z UUID

```java
// === Encja implementująca HasUuid ===
@Table("orders")
@Data
public class Order implements HasUuid {
    @Id
    private Long id;
    private UUID uuid;
    private String orderNumber;
    private BigDecimal amount;
    private String status;

    @Override
    public UUID getUuid() { return uuid; }

    @Override
    public void setUuid(UUID uuid) { this.uuid = uuid; }
}

// === Interfejs — FilterableUuidRepository ===
public interface OrderRepository extends FilterableUuidRepository<Order, Long> {}

// === Implementacja — FilterableUuidFragmentImpl ===
@Repository
class OrderRepositoryImpl extends FilterableUuidFragmentImpl<Order, Long> {
    public OrderRepositoryImpl(FilterableFragmentContext context) {
        super(context, Order.class);
    }
}

// === Użycie — dodatkowe metody UUID ===
Optional<Order> order = orderRepository.findByUuid(uuid);
boolean exists = orderRepository.existsByUuid(uuid);
orderRepository.deleteByUuid(uuid);
```

---

## 3. Filtrowanie — wszystkie operatory

```java
// Equals (case-sensitive)
FilterCriteria.eq("status", "COMPLETED")

// Not equals
FilterCriteria.neq("status", "CANCELLED")

// Equals (case-insensitive)
FilterCriteria.eqic("status", "completed")  // LOWER(col) = LOWER(:val)

// Like (ILIKE, auto-dodaje %)
FilterCriteria.like("orderNumber", "ORD")    // ILIKE 'ORD%' — NIE dodawaj % sam!

// Greater than / Less than
FilterCriteria.gt("amount", new BigDecimal("100"))
FilterCriteria.lt("amount", new BigDecimal("500"))

// Greater/Less or equal
FilterCriteria.gte("amount", new BigDecimal("100"))
FilterCriteria.lte("amount", new BigDecimal("500"))

// Between (inclusive, oba argumenty wymagane non-null)
FilterCriteria.between("amount", new BigDecimal("100"), new BigDecimal("500"))

// In / Not in
FilterCriteria.in("status", "COMPLETED", "PENDING")
FilterCriteria.notIn("status", "CANCELLED", "REJECTED")

// Array overlap (PostgreSQL) — kolumna typu ARRAY
FilterCriteria.ao("tags", "urgent", "priority")  // col && ARRAY['urgent','priority']

// Is null / Is not null
FilterCriteria.isNull("deletedAt")
FilterCriteria.isNotNull("assignedTo")

// === Przykład z wieloma filtrami (domyślnie AND) ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "COMPLETED"),
    FilterCriteria.gte("amount", new BigDecimal("100")),
    FilterCriteria.lte("amount", new BigDecimal("500")),
    FilterCriteria.like("orderNumber", "ORD")
).build();

Page<Order> orders = orderRepository.findAll(params);
```

---

## 4. Złożone warunki OR/AND

```java
// === OR — status COMPLETED lub PENDING ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.or(List.of(
        FilterCriteria.eq("status", "COMPLETED"),
        FilterCriteria.eq("status", "PENDING")
    ))
).build();

// === Nested AND/OR — (status = COMPLETED AND amount > 200) OR (status = PENDING) ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.or(List.of(
        FilterCriteria.and(List.of(
            FilterCriteria.eq("status", "COMPLETED"),
            FilterCriteria.gt("amount", new BigDecimal("200"))
        )),
        FilterCriteria.eq("status", "PENDING")
    ))
).build();

Page<Order> orders = orderRepository.findAll(params);

// === Explicit AND ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.and(List.of(
        FilterCriteria.eq("status", "COMPLETED"),
        FilterCriteria.gt("amount", new BigDecimal("200"))
    ))
).build();
```

---

## 5. Paginacja i sortowanie

```java
// === Paginacja z sortowaniem ===
SearchParams params = SearchParams.builder()
    .page(0)           // pierwsza strona (0-indexed)
    .size(20)          // 20 wyników na stronę
    .sort(List.of(SortOrder.desc("amount")))
    .filters(List.of(
        FilterCriteria.eq("status", "COMPLETED")
    ))
    .build();

Page<Order> result = orderRepository.findAll(params);

// Informacje o paginacji
long totalElements = result.getTotalElements();
int totalPages = result.getTotalPages();
List<Order> content = result.getContent();
boolean hasNext = result.hasNext();

// === Dynamiczne dodawanie filtrów ===
SearchParams params = SearchParams.builder()
    .page(0)
    .size(50)
    .build();

// setFilter dodaje/nadpisuje filtr po nazwie pola
params.setFilter(FilterCriteria.eq("status", "ACTIVE"));
params.setFilter(FilterCriteria.gte("amount", new BigDecimal("100")));
```

---

## 6. Multi-field sorting

```java
// === Sortowanie po wielu polach ===
SearchParams params = SearchParams.builder()
    .sort(List.of(
        SortOrder.asc("status"),     // najpierw po statusie ASC
        SortOrder.desc("amount")     // potem po kwocie DESC
    ))
    .build();

Page<Order> result = orderRepository.findAll(params);

// === Sortowanie z filtrowaniem ===
SearchParams params = SearchParams.builder()
    .sort(List.of(
        SortOrder.desc("createdAt"),
        SortOrder.asc("orderNumber")
    ))
    .filters(List.of(
        FilterCriteria.eq("status", "COMPLETED"),
        FilterCriteria.gt("amount", new BigDecimal("100"))
    ))
    .page(0)
    .size(20)
    .build();
```

---

## 7. Nested filtering (relacje)

Filtrowanie po polach zagnieżdżonych kolekcji (np. `@MappedCollection`).

```java
// === Filtruj zamówienia po polach pozycji (order items) ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("orderItems.productCode", "PROD-A"),
    FilterCriteria.gt("orderItems.quantity", 3)
).build();

Page<Order> orders = orderRepository.findAll(params);

// === Połączenie filtrów parent + nested ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "COMPLETED"),           // filtr na Order
    FilterCriteria.like("orderItems.productCode", "PROD") // filtr na OrderItem
).build();

Page<Order> orders = orderRepository.findAll(params);

// === findOne z nested filter ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("orderItems.productCode", "PROD-A")
).build();

Optional<Order> order = orderRepository.findOne(params);

// === count z nested filter ===
long count = orderRepository.count(params);
```

---

## 8. Projekcje — proste pola

```java
// === Interfejs projekcji — tylko wybrane pola ===
public interface OrderNumberOnly {
    String getOrderNumber();
}

// === Użycie ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("orderNumber", "ORD001")
).build();

Optional<OrderNumberOnly> result = orderRepository.findOneProjectedBy(
    params, OrderNumberOnly.class
);

// === Projekcja z wieloma polami ===
public interface OrderSummary {
    Long getId();
    String getOrderNumber();
    String getStatus();
    BigDecimal getAmount();
}

Page<OrderSummary> summaries = orderRepository.findAllProjectedBy(
    SearchParams.criteria(FilterCriteria.eq("status", "COMPLETED")).build(),
    OrderSummary.class
);
```

---

## 9. Projekcje — SpEL z obliczonymi polami

```java
// === Projekcja z @Value (SpEL expressions) ===
public interface OrderWithStatus {
    Long getId();
    String getOrderNumber();
    String getStatus();
    BigDecimal getAmount();

    // Obliczone pole — konkatenacja
    @Value("#{target.orderNumber + ' - ' + target.status}")
    String getOrderSummary();

    // Obliczone pole — warunek
    @Value("#{target.amount > 150 ? 'High Value' : 'Standard'}")
    String getValueCategory();
}

// === Użycie ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "COMPLETED")
).build();

Page<OrderWithStatus> result = orderRepository.findAllProjectedBy(
    params, OrderWithStatus.class
);

// Każdy element ma obliczone pola:
// order.getOrderSummary()   → "ORD001 - COMPLETED"
// order.getValueCategory()  → "Standard" lub "High Value"
```

---

## 10. Projekcje — kolekcje (nested items)

```java
// === Projekcja pozycji zamówienia ===
public interface OrderItemProjection {
    String getProductCode();
    Integer getQuantity();
    BigDecimal getTotalPrice();
}

// === Projekcja zamówienia z zagnieżdżonymi items ===
public interface OrderWithItems {
    String getOrderNumber();
    String getStatus();

    @Value("#{target.orderItems}")
    List<OrderItemProjection> getOrderItems();
}

// === Użycie ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("orderNumber", "ORD001")
).build();

Optional<OrderWithItems> result = orderRepository.findOneProjectedBy(
    params, OrderWithItems.class
);

OrderWithItems order = result.get();
List<OrderItemProjection> items = order.getOrderItems();
// items.get(0).getProductCode() → "PROD-A"
// items.get(0).getQuantity()    → 2
```

---

## 11. @AggregateReference — JOIN do innego agregatu

```java
// === Encja kategorii (docelowy agregat) ===
@Data
@Table("categories")
public class Category {
    @Id
    private Long id;
    private UUID uuid;
    private String name;
    private String description;
}

// === Encja produktu z referencją do kategorii ===
@Table("products")
@Data
public class Product {
    @Id
    private Long id;
    private UUID uuid;
    private String name;
    private BigDecimal price;

    @AggregateReference(
        target = Category.class,       // klasa docelowego agregatu
        targetColumn = "uuid",         // kolumna w tabeli categories
        sourceColumn = "category_uuid", // kolumna w tabeli products
        alias = "category"             // alias do użycia w filtrach i projekcjach
    )
    private UUID categoryUuid;
}

// === Repozytorium ===
public interface ProductRepository extends FilterableRepository<Product, Long> {}

@Repository
class ProductRepositoryImpl extends FilterableFragmentImpl<Product, Long> {
    public ProductRepositoryImpl(FilterableFragmentContext context) {
        super(context, Product.class);
    }
}

// === Projekcja z polami z JOINowanego agregatu ===
public interface ProductWithCategoryProjection {
    UUID getUuid();
    String getName();
    BigDecimal getPrice();

    @Value("#{target.category.name}")
    String getCategoryName();

    @Value("#{target.category.description}")
    String getCategoryDescription();

    @Value("#{target.name + ' - ' + target.category.name}")
    String getDisplayName();

    @Value("#{target.price > 100 ? 'Premium' : 'Standard'}")
    String getPriceCategory();
}

// === Filtrowanie po polach agregatu ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("category.name", "Electronics"),
    FilterCriteria.gt("price", new BigDecimal("100"))
).build();

Page<ProductWithCategoryProjection> result = productRepository.findAllProjectedBy(
    params, ProductWithCategoryProjection.class
);
// result.getContent().get(0).getCategoryName() → "Electronics"
// result.getContent().get(0).getDisplayName()  → "Laptop - Electronics"

// === findOne z filtrem na agregat ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("category.name", "Electronics")
).build();

Optional<ProductWithCategoryProjection> product = productRepository.findOneProjectedBy(
    params, ProductWithCategoryProjection.class
);
```

---

## 12. Złożone projekcje z @AggregateReference i kolekcjami

Scenariusz: Transaction ma wiele categories przez tabelę łączącą (MappedCollection + AggregateReference).

```java
// === Encja kategorii ===
@Data
@Table("categories")
public class Category implements HasUuid {
    @Id private Long id;
    private UUID uuid;
    private String name;
    private String color;
}

// === Tabela łącząca — nested w Transaction ===
@Data
@Table("transaction_categories")
public class TransactionCategory {
    @AggregateReference(
        target = Category.class,
        targetColumn = "uuid",
        sourceColumn = "category_uuid",
        alias = "category"
    )
    private UUID categoryUuid;
}

// === Encja transakcji ===
@Data
@Table("transactions")
public class Transaction implements HasUuid {
    @Id private Long id;
    private UUID uuid;
    private String name;
    private BigDecimal amount;
    @Column("type") private String type;
    private LocalDate transactionDate;

    @MappedCollection(idColumn = "transaction_id")
    private Set<TransactionCategory> categories;
}

// === Projekcja kategorii ===
public interface CategoryInfo {
    UUID getCategoryUuid();

    @Value("#{target.category.name}")
    String getName();

    @Value("#{target.category.color}")
    String getColor();
}

// === Projekcja transakcji z kolekcją kategorii ===
public interface TransactionWithCategories {
    Long getId();
    UUID getUuid();
    String getName();
    BigDecimal getAmount();
    String getType();
    LocalDate getTransactionDate();

    @Value("#{target.categories}")
    List<CategoryInfo> getCategories();
}

// === Repozytorium ===
public interface TransactionRepository extends FilterableRepository<Transaction, Long> {}

@Repository
class TransactionRepositoryImpl extends FilterableFragmentImpl<Transaction, Long> {
    public TransactionRepositoryImpl(FilterableFragmentContext context) {
        super(context, Transaction.class);
    }
}

// === Filtrowanie po polach kategorii ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("categories.category.name", "Food")
).build();

var result = transactionRepository.findAllProjectedBy(
    params, TransactionWithCategories.class
);

// === OR na kategoriach ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.or(List.of(
        FilterCriteria.eq("categories.category.name", "Food"),
        FilterCriteria.eq("categories.category.name", "Entertainment")
    ))
).build();

// === Filtrowanie + paginacja + sortowanie z projekcją ===
SearchParams params = SearchParams.builder()
    .page(0)
    .size(2)
    .sort(List.of(SortOrder.desc("amount")))
    .filters(List.of(
        FilterCriteria.gt("amount", new BigDecimal("100")),
        FilterCriteria.eq("categories.category.name", "Food")
    ))
    .build();

var result = transactionRepository.findAllProjectedBy(
    params, TransactionWithCategories.class
);
```

---

## 13. Database views

```java
// === Encja widoku — mapuj na VIEW ===
@Table("v_order_summary")
// UWAGA: NIE używaj @Immutable — powoduje null we wszystkich polach w Spring Data JDBC 4.0.0
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderSummaryView {
    @Id
    private Long id;

    @Column("order_number")     // alias widoku ≠ snake_case pola → użyj @Column
    private String orderNumber;

    private BigDecimal amount;
    private String status;

    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("item_count")       // kolumna z agregacji (COUNT)
    private Long itemCount;

    @Column("total_quantity")   // kolumna z agregacji (SUM)
    private Long totalQuantity;

    @Column("product_codes")    // kolumna z agregacji (STRING_AGG)
    private String productCodes;
}

// === Interfejs repozytorium — read-only (FilterableRepository, nie FilterableUuid) ===
public interface OrderSummaryViewRepository extends FilterableRepository<OrderSummaryView, Long> {}

@Repository
class OrderSummaryViewRepositoryImpl extends FilterableFragmentImpl<OrderSummaryView, Long> {
    public OrderSummaryViewRepositoryImpl(FilterableFragmentContext context) {
        super(context, OrderSummaryView.class);
    }
}

// === Użycie — filtrowanie, sortowanie, paginacja ===

// Filtr na kolumnie widoku
Page<OrderSummaryView> result = viewRepository.findAll(
    SearchParams.criteria(FilterCriteria.eq("status", "COMPLETED")).build()
);

// Filtr na kolumnie z agregacji
Page<OrderSummaryView> result = viewRepository.findAll(
    SearchParams.criteria(FilterCriteria.gt("itemCount", 1L)).build()
);

// Multi-field sorting na widoku
SearchParams params = SearchParams.builder()
    .sort(List.of(SortOrder.asc("status"), SortOrder.desc("amount")))
    .build();

Page<OrderSummaryView> result = viewRepository.findAll(params);

// Paginacja na widoku
SearchParams params = SearchParams.builder().page(0).size(2).build();
Page<OrderSummaryView> result = viewRepository.findAll(params);
// result.getTotalElements() → 3
// result.getTotalPages()    → 2
// result.getContent()       → 2 elementy

// count na widoku
long count = viewRepository.count(
    SearchParams.criteria(FilterCriteria.eq("status", "COMPLETED")).build()
);
```

### Widok z aliasami kolumn

```java
// === Widok z aliasami — np. v_task_list_test ===
// SQL: CREATE VIEW v_task_list_test AS
//      SELECT id, internal_status AS status, internal_priority AS priority,
//             title, created_at FROM tasks;

@Table("v_task_list_test")
@Data
public class TaskListView {
    @Id private Long id;

    // BEZ @Column — pole Java 'status' mapuje na kolumnę 'status' (alias z VIEW)
    private String status;
    private String priority;
    private String title;

    @Column("created_at")
    private LocalDateTime createdAt;
}
```

---

## 14. REST controller — read-only

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends FilterableController<Order, Long> {

    public OrderController(OrderRepository repository) {
        super(repository);
    }
}
```

Gotowe endpointy:
- `GET /api/orders/{id}` — pobierz po ID
- `POST /api/orders/search` — wyszukiwanie z filtrowaniem
- `POST /api/orders/find` — znajdź jeden
- `POST /api/orders/count` — policz pasujące

---

## 15. REST controller — pełne CRUD

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudFilterableController<Order, Long> {

    public OrderController(OrderRepository repository) {
        super(repository);
    }
}
```

Dodatkowe endpointy:
- `POST /api/orders/` — stwórz (201 Created)
- `PUT /api/orders/{id}` — full update
- `PATCH /api/orders/{id}` — partial update (deep merge)
- `DELETE /api/orders/{id}` — usuń

---

## 16. REST controller — CRUD z UUID

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudUuidFilterableController<Order, Long> {

    public OrderController(FilterableUuidRepository<Order, Long> repository) {
        super(repository);
    }
}
```

Endpointy używają UUID zamiast ID:
- `GET /api/orders/{uuid}` — pobierz po UUID
- `POST /api/orders/` — stwórz (auto-generuje UUID jeśli null)
- `PUT /api/orders/{uuid}` — full update po UUID
- `PATCH /api/orders/{uuid}` — partial update po UUID (deep merge)
- `DELETE /api/orders/{uuid}` — usuń po UUID

---

## 17. REST controller — hooki CRUD

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudFilterableController<Order, Long> {

    private final NotificationService notificationService;

    public OrderController(OrderRepository repository, NotificationService notificationService) {
        super(repository);
        this.notificationService = notificationService;
    }

    // === Walidacja przed tworzeniem ===
    @Override
    protected void validateCreate(Order entity) {
        if (entity.getAmount() == null || entity.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
    }

    // === Hook przed tworzeniem ===
    @Override
    protected void beforeCreate(Order entity) {
        entity.setStatus("PENDING");
        entity.setCreatedAt(LocalDateTime.now());
    }

    // === Hook po tworzeniu ===
    @Override
    protected void afterCreate(Order entity) {
        notificationService.notifyNewOrder(entity);
    }

    // === Walidacja przed update ===
    @Override
    protected void validateUpdate(Long id, Order entity) {
        // np. sprawdź czy można edytować zamówienie w tym statusie
    }

    // === Hook przed update ===
    @Override
    protected void beforeUpdate(Long id, Order entity) {
        entity.setUpdatedAt(LocalDateTime.now());
    }

    // === Hook po PATCH — przed i po ===
    @Override
    protected void beforePatch(Long id, Order existing, Order partial) {
        // existing — aktualny stan z bazy
        // partial — dane z requestu (non-null pola)
    }

    // === Walidacja przed usunięciem ===
    @Override
    protected void validateDelete(Long id) {
        // np. sprawdź czy zamówienie nie jest w trakcie realizacji
    }

    // === Zmiana max page size ===
    @Override
    protected int getMaxPageSize() {
        return 200; // default: 100
    }

    // === Hook afterRead — transformacja przed zwróceniem ===
    @Override
    protected Order afterRead(Order entity) {
        // np. maskowanie danych wrażliwych
        return entity;
    }
}
```

### Hooki CRUD z UUID

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudUuidFilterableController<Order, Long> {

    public OrderController(FilterableUuidRepository<Order, Long> repository) {
        super(repository);
    }

    // Hooki UUID przyjmują UUID zamiast Long:
    @Override
    protected void validateUpdate(UUID uuid, Order entity) { }

    @Override
    protected void beforeUpdate(UUID uuid, Order entity) { }

    @Override
    protected void afterUpdate(UUID uuid, Order entity) { }

    @Override
    protected void validateDelete(UUID uuid) { }

    @Override
    protected void beforeDelete(UUID uuid) { }

    @Override
    protected void afterDelete(UUID uuid) { }
}
```

---

## 18. REST API — JSON request/response

### POST /search — wyszukiwanie

```json
POST /api/orders/search
Content-Type: application/json

{
  "page": 0,
  "size": 20,
  "sort": [
    {"field": "amount", "direction": "DESC"},
    {"field": "status", "direction": "ASC"}
  ],
  "filters": [
    {"field": "status", "operator": "eq", "value": "COMPLETED"},
    {"field": "amount", "operator": "gt", "value": 100},
    {"field": "orderNumber", "operator": "like", "value": "ORD"}
  ]
}
```

### POST /search z OR/AND

```json
POST /api/orders/search
Content-Type: application/json

{
  "page": 0,
  "size": 20,
  "filters": [
    {
      "logicalOperator": "OR",
      "children": [
        {"field": "status", "operator": "eq", "value": "COMPLETED"},
        {"field": "status", "operator": "eq", "value": "PENDING"}
      ]
    },
    {"field": "amount", "operator": "gte", "value": 100}
  ]
}
```

### POST /search z between

```json
{
  "filters": [
    {"field": "amount", "operator": "between", "value": [100, 500]},
    {"field": "createdAt", "operator": "between", "value": ["2024-01-01T00:00:00", "2024-12-31T23:59:59"]}
  ]
}
```

### POST /search z in

```json
{
  "filters": [
    {"field": "status", "operator": "in", "value": ["COMPLETED", "PENDING", "PROCESSING"]}
  ]
}
```

### POST /find — znajdź jeden

```json
POST /api/orders/find
Content-Type: application/json

{
  "filters": [
    {"field": "orderNumber", "operator": "eq", "value": "ORD001"}
  ]
}
```

### POST /count

```json
POST /api/orders/count
Content-Type: application/json

{
  "filters": [
    {"field": "status", "operator": "eq", "value": "COMPLETED"}
  ]
}
```

Response: `2` (number)

### POST / — tworzenie

```json
POST /api/orders/
Content-Type: application/json

{
  "orderNumber": "ORD999",
  "amount": 250.00,
  "status": "PENDING"
}
```

Response: `201 Created` z body encji.

### PUT /{id} — full update

```json
PUT /api/orders/1
Content-Type: application/json

{
  "orderNumber": "ORD999",
  "amount": 300.00,
  "status": "COMPLETED"
}
```

### PATCH /{id} — partial update

```json
PATCH /api/orders/1
Content-Type: application/json

{
  "amount": 350.00
}
```

Tylko `amount` zostanie zmienione. Inne pola zachowują wartości z bazy (deep merge).

### Unpaged — wszystkie wyniki

```json
POST /api/orders/search
Content-Type: application/json

{
  "unpaged": true,
  "filters": [
    {"field": "status", "operator": "eq", "value": "COMPLETED"}
  ]
}
```

---

## 19. Filtrowanie po enum

```java
// === Encja z enum ===
@Table("orders_with_enum")
@Data
public class OrderWithEnum {
    @Id private Long id;
    private String orderNumber;
    private BigDecimal amount;
    private OrderStatus status;  // enum: PENDING, COMPLETED, CANCELLED
}

public enum OrderStatus {
    PENDING, COMPLETED, CANCELLED
}

// === Filtrowanie — enum jest automatycznie konwertowany ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", OrderStatus.COMPLETED)
).build();

// === IN z enumami ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.in("status", OrderStatus.COMPLETED, OrderStatus.PENDING)
).build();

// === String też działa (nazwa enuma) ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "COMPLETED")
).build();

// === NEQ z enum ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.neq("status", OrderStatus.CANCELLED)
).build();
```

---

## 20. Stream i unpaged

```java
// === findAllAsStream — lazy loading (unpaged) ===
SearchParams params = SearchParams.criteria(
    FilterCriteria.eq("status", "COMPLETED")
).unpaged(true).build();

try (Stream<Order> stream = orderRepository.findAllAsStream(params)) {
    stream.forEach(order -> processOrder(order));
}

// === Stream z projekcją ===
try (Stream<OrderSummary> stream = orderRepository.findAllProjectedByAsStream(
        params, OrderSummary.class)) {
    List<OrderSummary> summaries = stream.toList();
}

// === Unpaged z SearchParams ===
SearchParams params = SearchParams.builder()
    .unpaged(true)  // ignoruje page/size, zwraca wszystko
    .filters(List.of(FilterCriteria.gt("amount", BigDecimal.ZERO)))
    .build();

Page<Order> allOrders = orderRepository.findAll(params);
```

---

## 21. Eksport danych

### Kontroler z eksportem

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudFilterableController<Order, Long> {

    public OrderController(OrderRepository repository, List<DataExporter> exporters) {
        super(repository, false, exporters);
    }

    @Override
    protected Map<String, String> prepareExportLabels() {
        return Map.of(
            "orderNumber", "Order Number",
            "amount", "Amount",
            "status", "Status",
            "createdAt", "Created At"
        );
    }
}
```

### REST request — eksport synchroniczny

```json
POST /api/orders/export/csv
Content-Type: application/json

{
  "fileName": "orders-export",
  "searchRequest": {
    "filters": [
      {"field": "status", "operator": "eq", "value": "COMPLETED"}
    ],
    "sort": [
      {"field": "amount", "direction": "DESC"}
    ]
  }
}
```

### Asynchroniczny eksport (wymaga QueryControllersPort)

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController extends CrudFilterableController<Order, Long> {

    public OrderController(
            OrderRepository repository,
            List<DataExporter> exporters,
            QueryControllersPort controllersPort) {
        super(repository, false, exporters, controllersPort);
    }
}
```

```json
POST /api/orders/export-async/xlsx
Content-Type: application/json

{
  "fileName": "orders-report",
  "searchRequest": {
    "filters": [
      {"field": "status", "operator": "eq", "value": "COMPLETED"}
    ]
  }
}
```

Publikuje `AsyncExportEvent` — obsłuż go w oddzielnym handlerze.

---

## 22. Testowanie z Testcontainers

```java
// === Konfiguracja Testcontainers ===
@TestConfiguration
public class TestContainersConfig {

    @Bean
    @ServiceConnection
    PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>("postgres:16-alpine");
    }
}

// === Test integracyjny ===
@SpringBootTest
@Import(TestContainersConfig.class)
@Transactional
@Sql("/test-data.sql")  // ładuje dane testowe
class OrderRepositoryIntegrationTest {

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void shouldFilterByStatus() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("status", "COMPLETED")
        ).build();

        Page<Order> result = orderRepository.findAll(params);

        assertThat(result.getContent())
            .isNotEmpty()
            .allSatisfy(order ->
                assertThat(order.getStatus()).isEqualTo("COMPLETED")
            );
    }

    @Test
    void shouldFilterWithMultipleConditions() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("status", "COMPLETED"),
            FilterCriteria.gt("amount", new BigDecimal("100"))
        ).build();

        Page<Order> result = orderRepository.findAll(params);

        assertThat(result.getContent()).allSatisfy(order -> {
            assertThat(order.getStatus()).isEqualTo("COMPLETED");
            assertThat(order.getAmount()).isGreaterThan(new BigDecimal("100"));
        });
    }

    @Test
    void shouldSortAndPaginate() {
        SearchParams params = SearchParams.builder()
            .page(0)
            .size(2)
            .sort(List.of(SortOrder.desc("amount")))
            .build();

        Page<Order> result = orderRepository.findAll(params);

        assertThat(result.getContent()).hasSize(2);
        assertThat(result.getTotalPages()).isGreaterThanOrEqualTo(1);
        assertThat(result.getContent())
            .extracting(Order::getAmount)
            .isSortedAccordingTo(Comparator.reverseOrder());
    }

    @Test
    void shouldFindOneWithFilter() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("orderNumber", "ORD001")
        ).build();

        Optional<Order> result = orderRepository.findOne(params);

        assertThat(result).isPresent();
        assertThat(result.get().getOrderNumber()).isEqualTo("ORD001");
    }

    @Test
    void shouldCountWithFilter() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.eq("status", "COMPLETED")
        ).build();

        long count = orderRepository.count(params);

        assertThat(count).isGreaterThan(0);
    }

    @Test
    void shouldHandleOrConditions() {
        SearchParams params = SearchParams.criteria(
            FilterCriteria.or(List.of(
                FilterCriteria.eq("status", "COMPLETED"),
                FilterCriteria.eq("status", "PENDING")
            ))
        ).build();

        Page<Order> result = orderRepository.findAll(params);

        assertThat(result.getContent()).allSatisfy(order ->
            assertThat(order.getStatus()).isIn("COMPLETED", "PENDING")
        );
    }

    @Test
    void shouldProjectWithSpEL() {
        interface OrderSummary {
            String getOrderNumber();
            BigDecimal getAmount();

            @Value("#{target.amount > 150 ? 'High' : 'Standard'}")
            String getCategory();
        }

        Page<OrderSummary> result = orderRepository.findAllProjectedBy(
            SearchParams.empty(), OrderSummary.class
        );

        assertThat(result.getContent()).isNotEmpty();
    }
}
```

### SQL testowy — przykład

```sql
-- test-data.sql
INSERT INTO orders (order_number, amount, status, created_at)
VALUES
    ('ORD001', 100.00, 'COMPLETED', '2024-01-15 10:00:00'),
    ('ORD002', 200.00, 'PENDING', '2024-02-20 14:30:00'),
    ('ORD003', 300.00, 'COMPLETED', '2024-03-10 09:15:00');

INSERT INTO order_items (order_id, product_code, quantity, unit_price, total_price)
VALUES
    (1, 'PROD-A', 2, 50.00, 100.00),
    (1, 'PROD-B', 1, 50.00, 50.00),
    (2, 'PROD-C', 3, 66.67, 200.00),
    (3, 'PROD-A', 1, 300.00, 300.00);
```

### SQL widoku — przykład

```sql
-- view-test.sql
CREATE OR REPLACE VIEW v_order_summary AS
SELECT
    o.id,
    o.order_number,
    o.amount,
    o.status,
    o.created_at,
    COUNT(oi.id) AS item_count,
    COALESCE(SUM(oi.quantity), 0) AS total_quantity,
    STRING_AGG(oi.product_code, ', ' ORDER BY oi.product_code) AS product_codes
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id, o.order_number, o.amount, o.status, o.created_at;
```
