# Przykłady — preboot-eventbus

## Spis treści

- [Podstawowe użycie](#podstawowe-użycie)
- [Generic Events z type filtering](#generic-events-z-type-filtering)
- [Priorytet handlerów](#priorytet-handlerów)
- [Wymuszenie wyjątku przy braku handlera](#wymuszenie-wyjątku-przy-braku-handlera)
- [Synchroniczny + asynchroniczny publisher razem](#synchroniczny--asynchroniczny-publisher-razem)
- [Handler z @Transactional (Spring AOP proxy)](#handler-z-transactional-spring-aop-proxy)
- [Overriding auto-konfiguracji](#overriding-auto-konfiguracji)
- [Testowanie handlerów](#testowanie-handlerów)
- [Integracja z preboot-ddd](#integracja-z-preboot-ddd)

---

## Podstawowe użycie

### Event jako record

```java
public record OrderPlacedEvent(
    UUID orderId,
    String customerEmail,
    BigDecimal totalAmount,
    LocalDateTime placedAt
) {}
```

### Handler

```java
@Service
public class OrderEventHandler {

    private final EmailService emailService;

    public OrderEventHandler(EmailService emailService) {
        this.emailService = emailService;
    }

    @EventHandler
    public void onOrderPlaced(OrderPlacedEvent event) {
        emailService.sendOrderConfirmation(event.customerEmail(), event.orderId());
    }
}
```

### Publisher

```java
@Service
public class OrderService {

    private final EventPublisher eventPublisher;
    private final OrderRepository orderRepository;

    public OrderService(EventPublisher eventPublisher, OrderRepository orderRepository) {
        this.eventPublisher = eventPublisher;
        this.orderRepository = orderRepository;
    }

    public Order placeOrder(CreateOrderRequest request) {
        Order order = orderRepository.save(new Order(request));

        eventPublisher.publish(new OrderPlacedEvent(
            order.getId(),
            request.customerEmail(),
            order.getTotalAmount(),
            LocalDateTime.now()
        ));

        return order;
    }
}
```

---

## Generic Events z type filtering

### Event generyczny

```java
public record DataProcessedEvent<T>(
    String processId,
    T data,
    LocalDateTime timestamp
) implements GenericEvent<T> {

    @Override
    public T getTypeParameter() {
        return data;
    }
}
```

### Handlery filtrowane po typie

```java
@Service
public class DataProcessingHandler {

    @EventHandler(typeParameter = String.class)
    public void handleStringData(DataProcessedEvent<String> event) {
        System.out.println("Processing string: " + event.data());
    }

    @EventHandler(typeParameter = Integer.class)
    public void handleIntegerData(DataProcessedEvent<Integer> event) {
        System.out.println("Processing integer: " + event.data());
    }
}
```

### Publishing

```java
@Service
public class DataService {

    private final EventPublisher eventPublisher;

    public DataService(EventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void processString(String data) {
        // WAŻNE: publishuj DataProcessedEvent, NIE sam String
        eventPublisher.publish(new DataProcessedEvent<>(
            UUID.randomUUID().toString(), data, LocalDateTime.now()
        ));
        // Wywoła TYLKO handleStringData()
    }

    public void processInteger(Integer data) {
        eventPublisher.publish(new DataProcessedEvent<>(
            UUID.randomUUID().toString(), data, LocalDateTime.now()
        ));
        // Wywoła TYLKO handleIntegerData()
    }
}
```

---

## Priorytet handlerów

```java
@Service
public class ValidationHandler {

    @EventHandler(priority = 100)  // Wykonany PIERWSZY
    public void validate(PaymentEvent event) {
        if (event.amount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Invalid payment amount");
        }
    }
}

@Service
public class PaymentProcessingHandler {

    @EventHandler(priority = 50)  // Wykonany DRUGI
    public void process(PaymentEvent event) {
        // przetwarzanie płatności — walidacja już przeszła
    }
}

@Service
public class AuditHandler {

    @EventHandler(priority = 0)  // Wykonany OSTATNI (default)
    public void audit(PaymentEvent event) {
        // zapis audytu
    }
}
```

**Kolejność:** `validate(100)` → `process(50)` → `audit(0)`

---

## Wymuszenie wyjątku przy braku handlera

```java
@ExceptionIfNoHandler
public record CriticalBusinessEvent(UUID entityId, String action) {}

// Użycie:
try {
    eventPublisher.publish(new CriticalBusinessEvent(id, "approve"));
} catch (NoEventHandlerException e) {
    log.error("No handler for critical event! Check handler registration.", e);
    throw new IllegalStateException("System misconfigured", e);
}
```

Bez `@ExceptionIfNoHandler`:

```java
public record OptionalNotificationEvent(String message) {}

// Brak handlera = warning w logach, event ignorowany, brak wyjątku
eventPublisher.publish(new OptionalNotificationEvent("hello"));
```

---

## Synchroniczny + asynchroniczny publisher razem

```java
@Service
public class OrderFulfillmentService {

    private final EventPublisher eventPublisher;          // sync (@Primary)
    private final EventPublisher asyncEventPublisher;     // async

    public OrderFulfillmentService(
            EventPublisher eventPublisher,
            @Qualifier("async") EventPublisher asyncEventPublisher) {
        this.eventPublisher = eventPublisher;
        this.asyncEventPublisher = asyncEventPublisher;
    }

    public void fulfillOrder(UUID orderId) {
        // Krytyczne — synchronicznie, wyjątek propaguje
        eventPublisher.publish(new OrderFulfilledEvent(orderId));

        // Nieistotne — asynchronicznie, fire-and-forget
        asyncEventPublisher.publish(new OrderFulfillmentNotification(orderId));
    }
}
```

---

## Handler z @Transactional (Spring AOP proxy)

Handlery za Spring AOP proxy są automatycznie wykrywane:

```java
@Service
public class InventoryHandler {

    private final InventoryRepository inventoryRepository;

    public InventoryHandler(InventoryRepository inventoryRepository) {
        this.inventoryRepository = inventoryRepository;
    }

    @Transactional
    @EventHandler
    public void onOrderPlaced(OrderPlacedEvent event) {
        // Wykonywane w transakcji — rollback działa poprawnie
        inventoryRepository.reserveStock(event.orderId());
    }
}
```

`LocalEventHandlerRepository` używa `AopUtils.getTargetClass()` i `AnnotationUtils.findAnnotation()` do wykrycia handlerów za proxy.

---

## Overriding auto-konfiguracji

### Nadpisanie tylko async publishera (custom thread pool)

```java
@Configuration
public class CustomEventBusConfig {

    @Bean("asyncEventPublisher")
    @Qualifier("async")
    public EventPublisher asyncEventPublisher(LocalEventHandlerRepository repository) {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(500);
        executor.setThreadNamePrefix("event-async-");
        executor.initialize();
        return new LocalAsynchronousEventPublisher(repository, executor);
    }
    // Sync publisher nadal auto-konfigurowany
}
```

### Nadpisanie sync publishera z metrykami

```java
@Configuration
public class MetricsEventBusConfig {

    @Bean
    @Primary
    public EventPublisher eventPublisher(LocalEventHandlerRepository repository) {
        LocalEventPublisher delegate = new LocalEventPublisher(repository);
        return new EventPublisher() {
            @Override
            public <T> void publish(T event) {
                long start = System.nanoTime();
                try {
                    delegate.publish(event);
                } finally {
                    long duration = System.nanoTime() - start;
                    log.info("Event {} published in {}ms",
                        event.getClass().getSimpleName(),
                        duration / 1_000_000);
                }
            }

            @Override
            public <T> boolean hasHandler(T event) {
                return delegate.hasHandler(event);
            }
        };
    }
}
```

### Wyłączenie async publishera

Najprościej: nie wstrzykuj `@Qualifier("async")` nigdzie. Bean istnieje, ale nie jest używany — zero narzutu.

---

## Testowanie handlerów

### Test jednostkowy z mock ApplicationContext

```java
@ExtendWith(MockitoExtension.class)
class OrderEventHandlerTest {

    private LocalEventHandlerRepository repository;
    private LocalEventPublisher publisher;

    @BeforeEach
    void setUp() {
        ApplicationContext ctx = mock(ApplicationContext.class);

        OrderEventHandler handler = new OrderEventHandler(mock(EmailService.class));

        when(ctx.getBeanDefinitionNames()).thenReturn(new String[]{"handler"});
        when(ctx.getBean("handler")).thenReturn(handler);

        repository = new LocalEventHandlerRepository(ctx);
        publisher = new LocalEventPublisher(repository);
    }

    @Test
    void shouldHandleOrderPlacedEvent() {
        OrderPlacedEvent event = new OrderPlacedEvent(
            UUID.randomUUID(), "test@test.com", BigDecimal.TEN, LocalDateTime.now()
        );

        // Nie rzuca wyjątku = handler znaleziony i wykonany
        assertDoesNotThrow(() -> publisher.publish(event));
    }

    @Test
    void shouldDetectMissingHandler() {
        UnhandledEvent event = new UnhandledEvent();
        assertThat(publisher.hasHandler(event)).isFalse();
    }
}
```

### Test auto-konfiguracji

```java
class EventBusAutoConfigurationTest {

    private final ApplicationContextRunner contextRunner =
        new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(EventBusAutoConfiguration.class));

    @Test
    void shouldAutoConfigureBothPublishers() {
        contextRunner.run(context -> {
            assertThat(context.getBeansOfType(EventPublisher.class)).hasSize(2);

            // Sync (@Primary)
            EventPublisher sync = context.getBean("eventPublisher", EventPublisher.class);
            assertThat(sync).isInstanceOf(LocalEventPublisher.class);

            // Async
            EventPublisher async = context.getBean("asyncEventPublisher", EventPublisher.class);
            assertThat(async).isInstanceOf(LocalAsynchronousEventPublisher.class);

            // Default = sync
            assertThat(context.getBean(EventPublisher.class)).isSameAs(sync);
        });
    }

    @Test
    void shouldAllowCustomPublisher() {
        contextRunner
            .withUserConfiguration(CustomConfig.class)
            .run(context -> {
                EventPublisher pub = context.getBean("eventPublisher", EventPublisher.class);
                assertThat(pub).isInstanceOf(LocalAsynchronousEventPublisher.class);
            });
    }

    @Configuration
    static class CustomConfig {
        @Bean
        public EventPublisher eventPublisher(LocalEventHandlerRepository repository) {
            return new LocalAsynchronousEventPublisher(
                repository, Executors.newSingleThreadExecutor());
        }
    }
}
```

### Test generic event filtering

```java
@ExtendWith(MockitoExtension.class)
class GenericEventFilteringTest {

    private static int stringHandlerCalls;
    private static int integerHandlerCalls;

    @BeforeEach
    void setUp() {
        ApplicationContext ctx = mock(ApplicationContext.class);
        StringHandler stringHandler = new StringHandler();
        IntegerHandler integerHandler = new IntegerHandler();

        when(ctx.getBeanDefinitionNames()).thenReturn(new String[]{"s", "i"});
        when(ctx.getBean("s")).thenReturn(stringHandler);
        when(ctx.getBean("i")).thenReturn(integerHandler);

        LocalEventHandlerRepository repo = new LocalEventHandlerRepository(ctx);
        LocalEventPublisher publisher = new LocalEventPublisher(repo);

        stringHandlerCalls = 0;
        integerHandlerCalls = 0;

        // Publish string event
        publisher.publish(new TypedEvent<>("hello"));

        assertThat(stringHandlerCalls).isEqualTo(1);
        assertThat(integerHandlerCalls).isEqualTo(0);

        // Publish integer event
        publisher.publish(new TypedEvent<>(42));

        assertThat(stringHandlerCalls).isEqualTo(1);
        assertThat(integerHandlerCalls).isEqualTo(1);
    }

    public record TypedEvent<T>(T value) implements GenericEvent<T> {
        @Override
        public T getTypeParameter() { return value; }
    }

    public static class StringHandler {
        @EventHandler(typeParameter = String.class)
        public void handle(TypedEvent<String> e) { stringHandlerCalls++; }
    }

    public static class IntegerHandler {
        @EventHandler(typeParameter = Integer.class)
        public void handle(TypedEvent<Integer> e) { integerHandlerCalls++; }
    }
}
```

---

## Integracja z preboot-ddd

`preboot-ddd` używa `EventPublisher` do automatycznego publishingu domain events po `save()`:

```java
// Agregat rejestruje event
public class Product extends AggregateRoot<UUID> {
    public void changePrice(BigDecimal newPrice) {
        this.price = newPrice;
        registerEvent(new ProductPriceChanged(getId(), newPrice));
    }
}

// Repozytorium DDD automatycznie publishuje eventy po save()
@Repository
public class JdbcProductRepository
        extends AbstractAggregateRepository<Product, ProductSnapshot, UUID>
        implements ProductRepository {

    public JdbcProductRepository(
            SnapshotRepository repo,
            ProductMapper mapper,
            EventPublisher eventPublisher) {  // <-- preboot-eventbus EventPublisher
        super(repo, mapper, eventPublisher);
    }
}

// Handler eventu domenowego
@Service
public class PriceChangeHandler {

    @EventHandler
    public void onPriceChanged(ProductPriceChanged event) {
        // reaguj na zmianę ceny
    }
}

// Użycie:
productRepository.save(product);
// 1. Konwertuje Product → ProductSnapshot → zapis do DB
// 2. Wyciąga ProductPriceChanged z agregatu
// 3. Publishuje przez EventPublisher → wywołuje PriceChangeHandler
```

EventPublisher jest wstrzykiwany do `AbstractAggregateRepository` — domyślny synchroniczny publisher zapewnia, że domain events są przetworzone przed powrotem z `save()`.
