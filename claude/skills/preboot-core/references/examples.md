# preboot-core — Przykłady użycia

## Spis treści

- [TTLMap — podstawowe użycie](#ttlmap--podstawowe-użycie)
- [TTLMap — eviction callback](#ttlmap--eviction-callback)
- [TTLMap — lifecycle management](#ttlmap--lifecycle-management)
- [AccessSynchronizer — prosty lock](#accesssynchronizer--prosty-lock)
- [AccessSynchronizer — composite key](#accesssynchronizer--composite-key)
- [AccessSynchronizer — void operations](#accesssynchronizer--void-operations)
- [RateLimiter — basic](#ratelimiter--basic)
- [RateLimiter — non-blocking](#ratelimiter--non-blocking)
- [RateLimiter — per-client limits](#ratelimiter--per-client-limits)
- [TransactionWrapper — mixed propagation](#transactionwrapper--mixed-propagation)
- [HashUtils — cache key generation](#hashutils--cache-key-generation)
- [HashUtils — edge cases](#hashutils--edge-cases)
- [BeanValidator — DTO validation](#beanvalidator--dto-validation)
- [JsonMapperFactory — standalone usage](#jsonmapperfactory--standalone-usage)
- [Integracja — rate limiter + synchronizer](#integracja--rate-limiter--synchronizer)

---

## TTLMap — podstawowe użycie

```java
import io.preboot.core.colections.TTLMap;

// Cache z 5-minutowym domyślnym TTL
TTLMap<String, String> cache = new TTLMap<>(300);

// Dodanie wpisów
cache.put("config-v1", "{\"feature\":true}");
cache.put("temp-token", "abc123", 30); // 30 sekund TTL

// Odczyt
String config = cache.get("config-v1"); // wartość lub null jeśli wygasł
boolean exists = cache.containsKey("config-v1");
int count = cache.size();

// Usunięcie
cache.remove("temp-token");
cache.clear(); // usuwa wszystko
```

## TTLMap — eviction callback

```java
import io.preboot.core.colections.TTLMap;

TTLMap<String, AutoCloseable> resources = new TTLMap<>(60, (key, resource) -> {
    try {
        resource.close();
        log.info("Resource {} auto-closed after expiry", key);
    } catch (Exception e) {
        log.warn("Failed to close resource {}", key, e);
    }
});

resources.put("conn-1", openConnection());
// Po 60 sekundach: callback wywoła close() na połączeniu
```

## TTLMap — lifecycle management

```java
import io.preboot.core.colections.TTLMap;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Component;

@Component
public class SessionStore {
    private final TTLMap<String, UserSession> sessions;

    public SessionStore() {
        this.sessions = new TTLMap<>(1800, (sessionId, session) -> {
            log.info("Session {} expired for user {}", sessionId, session.username());
        });
    }

    public void addSession(String id, UserSession session) {
        sessions.put(id, session);
    }

    public UserSession getSession(String id) {
        return sessions.get(id);
    }

    @PreDestroy
    public void cleanup() {
        sessions.close();
    }
}
```

## AccessSynchronizer — prosty lock

```java
import io.preboot.core.concurent.AccessSynchronizer;

@Service
public class AccountService {
    private final AccessSynchronizer sync = new AccessSynchronizer();
    private final AccountRepository accountRepo;

    public AccountService(AccountRepository accountRepo) {
        this.accountRepo = accountRepo;
    }

    public Account transfer(String accountId, BigDecimal amount) {
        return sync.synchronize(accountId, () -> {
            Account account = accountRepo.findById(accountId).orElseThrow();
            account.debit(amount);
            return accountRepo.save(account);
        });
    }
}
```

## AccessSynchronizer — composite key

```java
import io.preboot.core.concurent.AccessSynchronizer;
import static io.preboot.core.concurent.AccessSynchronizer.compositeKey;

@Service
public class InventoryService {
    private final AccessSynchronizer sync = new AccessSynchronizer();

    public void reserveItem(String warehouseId, String productId, int quantity) {
        sync.synchronizeVoid(compositeKey(warehouseId, productId), () -> {
            // Lock per (warehouse, product) — różne produkty w tym samym
            // magazynie nie blokują się nawzajem
            Inventory inv = inventoryRepo.find(warehouseId, productId);
            if (inv.available() < quantity) {
                throw new InsufficientStockException();
            }
            inv.reserve(quantity);
            inventoryRepo.save(inv);
        });
    }
}
```

## AccessSynchronizer — void operations

```java
import io.preboot.core.concurent.AccessSynchronizer;

AccessSynchronizer sync = new AccessSynchronizer();

// Operacja bez zwracania wartości
sync.synchronizeVoid("resource-key", () -> {
    externalService.update(data);
    auditLog.record("updated resource-key");
});
```

## RateLimiter — basic

```java
import io.preboot.core.concurent.RateLimiter;

@Service
public class ExternalApiClient {
    private final RateLimiter limiter = new RateLimiter(5); // 5 req/s

    public ApiResponse callExternalApi(String clientId, Request request)
            throws InterruptedException {
        return limiter.executeWithRateLimit(clientId, () -> {
            return httpClient.send(request);
        });
    }
}
```

## RateLimiter — non-blocking

```java
import io.preboot.core.concurent.RateLimiter;

RateLimiter limiter = new RateLimiter(10);

if (limiter.tryAcquire("client-1")) {
    processRequest();
} else {
    throw new TooManyRequestsException("Rate limit exceeded");
}
```

## RateLimiter — per-client limits

```java
import io.preboot.core.concurent.RateLimiter;

@Service
public class TieredApiService {
    private final RateLimiter limiter = new RateLimiter(10);

    public void configureClientTier(String clientId, String tier) {
        switch (tier) {
            case "free" -> limiter.setRateLimit(clientId, 5);
            case "pro" -> limiter.setRateLimit(clientId, 50);
            case "enterprise" -> limiter.setRateLimit(clientId, 500);
        }
    }

    public String process(String clientId, String payload) throws InterruptedException {
        return limiter.executeWithRateLimit(clientId, () -> doWork(payload));
    }
}
```

## TransactionWrapper — mixed propagation

```java
import io.preboot.core.transaction.TransactionWrapper;

@Service
public class PaymentService {
    private final TransactionWrapper tx;
    private final PaymentRepository paymentRepo;
    private final AuditRepository auditRepo;

    public PaymentService(TransactionWrapper tx, PaymentRepository paymentRepo,
                          AuditRepository auditRepo) {
        this.tx = tx;
        this.paymentRepo = paymentRepo;
        this.auditRepo = auditRepo;
    }

    public Payment processPayment(PaymentRequest request) {
        // Główna transakcja
        Payment payment = tx.doInTransaction(() -> {
            Payment p = new Payment(request.amount(), request.currency());
            return paymentRepo.save(p);
        });

        // Audit w osobnej transakcji — zapisze się nawet jeśli
        // zewnętrzna transakcja się cofnie
        tx.doAlwaysInNewTransaction(() -> {
            auditRepo.save(new AuditEntry("payment_processed", payment.id()));
        });

        return payment;
    }
}
```

## HashUtils — cache key generation

```java
import io.preboot.core.util.HashUtils;

@Service
public class CachedQueryService {
    private final TTLMap<String, QueryResult> cache = new TTLMap<>(600);

    public QueryResult executeQuery(Map<String, String> params) {
        String cacheKey = HashUtils.getHash(params);
        QueryResult cached = cache.get(cacheKey);
        if (cached != null) {
            return cached;
        }
        QueryResult result = db.query(params);
        cache.put(cacheKey, result);
        return result;
    }
}
```

## HashUtils — edge cases

```java
import io.preboot.core.util.HashUtils;

// Kolejność nie ma znaczenia
Map<String, String> map1 = new LinkedHashMap<>();
map1.put("a", "1");
map1.put("b", "2");

Map<String, String> map2 = new LinkedHashMap<>();
map2.put("b", "2");
map2.put("a", "1");

HashUtils.getHash(map1).equals(HashUtils.getHash(map2)); // true

// Pusta mapa i null
HashUtils.getHash(Map.of());   // "-"
HashUtils.getHash(null);       // "-"
```

## BeanValidator — DTO validation

```java
import io.preboot.core.validation.BeanValidator;
import jakarta.validation.constraints.*;

public record CreateUserRequest(
    @NotBlank String username,
    @Email String email,
    @Min(18) int age
) {}

// Użycie
CreateUserRequest request = new CreateUserRequest("", "invalid", 15);
try {
    BeanValidator.validate(request);
} catch (ConstraintViolationException e) {
    // e.getConstraintViolations() zawiera szczegóły:
    // - username: must not be blank
    // - email: must be a well-formed email address
    // - age: must be greater than or equal to 18
    Set<ConstraintViolation<?>> violations = e.getConstraintViolations();
}
```

## JsonMapperFactory — standalone usage

```java
import io.preboot.core.json.JsonMapperFactory;
import tools.jackson.databind.json.JsonMapper;

// Poza Spring context — np. w CLI tool, testach
JsonMapper mapper = JsonMapperFactory.createJsonMapper();

// Serializacja
String json = mapper.writeValueAsString(myObject);

// Deserializacja — null na boolean nie rzuci wyjątku
MyDto dto = mapper.readValue("""
    {"name": "test", "active": null}
    """, MyDto.class);
// dto.active() == false (domyślna wartość boolean)
```

## Integracja — rate limiter + synchronizer

```java
import io.preboot.core.concurent.AccessSynchronizer;
import io.preboot.core.concurent.RateLimiter;

@Service
public class ExternalOrderService {
    private final AccessSynchronizer sync = new AccessSynchronizer();
    private final RateLimiter limiter = new RateLimiter(10);
    private final OrderRepository orderRepo;

    public ExternalOrderService(OrderRepository orderRepo) {
        this.orderRepo = orderRepo;
    }

    public OrderResult submitOrder(String customerId, OrderRequest request)
            throws InterruptedException {
        // Rate limit per customer
        return limiter.executeWithRateLimit(customerId, () -> {
            // Synchronize per order to prevent duplicate submissions
            return sync.synchronize(request.orderId(), () -> {
                if (orderRepo.existsByOrderId(request.orderId())) {
                    return orderRepo.findByOrderId(request.orderId());
                }
                Order order = new Order(request);
                return orderRepo.save(order);
            });
        });
    }
}
```
