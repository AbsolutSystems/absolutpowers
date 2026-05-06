# preboot-ddd — Examples

## Spis treści

- [Podstawowy agregat z eventami](#podstawowy-agregat-z-eventami)
- [Snapshot i mapper](#snapshot-i-mapper)
- [Repozytorium z EventPublisher](#repozytorium-z-eventpublisher)
- [Repozytorium z TaskPublisher](#repozytorium-z-taskpublisher)
- [Agregat z soft delete](#agregat-z-soft-delete)
- [Serwis domenowy](#serwis-domenowy)
- [Domain events jako records](#domain-events-jako-records)
- [Testy jednostkowe agregatu](#testy-jednostkowe-agregatu)
- [Testy repozytorium z mockami](#testy-repozytorium-z-mockami)

---

## Podstawowy agregat z eventami

```java
package com.example.domain;

import io.preboot.ddd.core.AggregateRoot;
import java.math.BigDecimal;
import java.util.UUID;

public class Product extends AggregateRoot<UUID> {

    private final UUID id;
    private String name;
    private BigDecimal price;
    private ProductStatus status;

    // Konstruktor do tworzenia nowego agregatu
    public Product(UUID id, String name, BigDecimal price) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.status = ProductStatus.DRAFT;
    }

    // Konstruktor do odtwarzania z persystencji (używany przez mapper)
    public Product(UUID id, String name, BigDecimal price, ProductStatus status) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.status = status;
    }

    @Override
    public UUID getId() {
        return id;
    }

    public String getName() { return name; }
    public BigDecimal getPrice() { return price; }
    public ProductStatus getStatus() { return status; }

    // Metody biznesowe rejestrują eventy
    public void activate() {
        if (this.status != ProductStatus.DRAFT) {
            throw new IllegalStateException("Only DRAFT products can be activated");
        }
        this.status = ProductStatus.ACTIVE;
        registerEvent(new ProductActivated(this.id));
    }

    public void changePrice(BigDecimal newPrice) {
        if (newPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
        BigDecimal oldPrice = this.price;
        this.price = newPrice;
        registerEvent(new ProductPriceChanged(this.id, oldPrice, newPrice));
    }

    public void rename(String newName) {
        String oldName = this.name;
        this.name = newName;
        registerEvent(new ProductRenamed(this.id, oldName, newName));
    }
}
```

```java
public enum ProductStatus {
    DRAFT, ACTIVE, INACTIVE
}
```

---

## Snapshot i mapper

```java
package com.example.infrastructure;

import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Table;
import java.math.BigDecimal;
import java.util.UUID;

@Table("products")
public record ProductSnapshot(
    @Id UUID id,
    String name,
    BigDecimal price,
    String status  // Enum jako String do DB
) {}
```

```java
package com.example.infrastructure;

import com.example.domain.Product;
import com.example.domain.ProductStatus;
import io.preboot.ddd.core.AggregateMapper;
import org.springframework.stereotype.Component;
import java.util.UUID;

@Component
public class ProductMapper implements AggregateMapper<Product, ProductSnapshot, UUID> {

    @Override
    public Product toDomain(ProductSnapshot snapshot) {
        if (snapshot == null) return null;

        return new Product(
            snapshot.id(),
            snapshot.name(),
            snapshot.price(),
            ProductStatus.valueOf(snapshot.status())
        );
    }

    @Override
    public ProductSnapshot toSnapshot(Product product) {
        if (product == null) return null;

        return new ProductSnapshot(
            product.getId(),
            product.getName(),
            product.getPrice(),
            product.getStatus().name()
        );
    }
}
```

---

## Repozytorium z EventPublisher

Standardowa wersja — synchroniczne in-memory eventy.

```java
package com.example.domain;

import io.preboot.ddd.core.AggregateRepository;
import java.util.UUID;

// Interfejs w warstwie domenowej — nie wie nic o infrastrukturze
public interface ProductRepository extends AggregateRepository<Product, UUID> {
    // Opcjonalne domain-specific query methods
}
```

```java
package com.example.infrastructure;

import com.example.domain.Product;
import com.example.domain.ProductRepository;
import io.preboot.ddd.infrastructure.AbstractAggregateRepository;
import io.preboot.eventbus.EventPublisher;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;

@Repository
public class JdbcProductRepository
        extends AbstractAggregateRepository<Product, ProductSnapshot, UUID>
        implements ProductRepository {

    // Spring Data automatycznie generuje implementację
    interface SnapshotRepository extends CrudRepository<ProductSnapshot, UUID> {}

    public JdbcProductRepository(
            SnapshotRepository snapshotRepo,
            ProductMapper mapper,
            EventPublisher eventPublisher) {
        super(snapshotRepo, mapper, eventPublisher);
    }
}
```

---

## Repozytorium z TaskPublisher

Wersja z persistent tasks — eventy przeżywają restart, automatyczny retry.

```java
package com.example.infrastructure;

import com.example.domain.Product;
import com.example.domain.ProductRepository;
import io.preboot.ddd.infrastructure.AbstractPersistentTaskRepository;
import io.preboot.tasks.TaskPublisher;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;

@Repository
public class JdbcProductRepository
        extends AbstractPersistentTaskRepository<Product, ProductSnapshot, UUID>
        implements ProductRepository {

    interface SnapshotRepository extends CrudRepository<ProductSnapshot, UUID> {}

    public JdbcProductRepository(
            SnapshotRepository snapshotRepo,
            ProductMapper mapper,
            TaskPublisher taskPublisher) {
        super(snapshotRepo, mapper, taskPublisher);
    }
}
```

Dodatkowa zależność Maven:
```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-tasks</artifactId>
</dependency>
```

---

## Agregat z soft delete

```java
package com.example.domain;

import io.preboot.ddd.core.AggregateRoot;
import io.preboot.ddd.core.SoftDeletable;
import java.time.LocalDateTime;
import java.util.UUID;

public class Order extends AggregateRoot<UUID> implements SoftDeletable {

    private final UUID id;
    private String customerName;
    private boolean deleted;
    private LocalDateTime deletedAt;

    public Order(UUID id, String customerName) {
        this.id = id;
        this.customerName = customerName;
        this.deleted = false;
    }

    // Konstruktor do odtwarzania z persystencji
    public Order(UUID id, String customerName, boolean deleted, LocalDateTime deletedAt) {
        this.id = id;
        this.customerName = customerName;
        this.deleted = deleted;
        this.deletedAt = deletedAt;
    }

    @Override
    public UUID getId() { return id; }

    public String getCustomerName() { return customerName; }

    @Override
    public boolean isDeleted() { return deleted; }

    @Override
    public LocalDateTime getDeletedAt() { return deletedAt; }

    @Override
    public void markAsDeleted() {
        if (this.deleted) {
            throw new IllegalStateException("Order already deleted");
        }
        this.deleted = true;
        this.deletedAt = LocalDateTime.now();
        registerEvent(new OrderDeleted(this.id, this.deletedAt));
    }

    @Override
    public void restore() {
        if (!this.deleted) {
            throw new IllegalStateException("Order is not deleted");
        }
        this.deleted = false;
        this.deletedAt = null;
        registerEvent(new OrderRestored(this.id));
    }
}
```

Snapshot z polami soft delete:

```java
@Table("orders")
public record OrderSnapshot(
    @Id UUID id,
    String customerName,
    boolean deleted,
    LocalDateTime deletedAt
) {}
```

Mapper:

```java
@Component
public class OrderMapper implements AggregateMapper<Order, OrderSnapshot, UUID> {

    @Override
    public Order toDomain(OrderSnapshot snapshot) {
        if (snapshot == null) return null;
        return new Order(
            snapshot.id(), snapshot.customerName(),
            snapshot.deleted(), snapshot.deletedAt()
        );
    }

    @Override
    public OrderSnapshot toSnapshot(Order order) {
        if (order == null) return null;
        return new OrderSnapshot(
            order.getId(), order.getCustomerName(),
            order.isDeleted(), order.getDeletedAt()
        );
    }
}
```

Użycie w serwisie:

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;

    // Soft delete — operacja domenowa z eventami
    public void cancelOrder(UUID orderId) {
        Order order = orderRepository.findActiveById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        order.markAsDeleted();
        orderRepository.save(order); // Publishuje OrderDeleted event
    }

    // Restore
    public void restoreOrder(UUID orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        order.restore();
        orderRepository.save(order); // Publishuje OrderRestored event
    }

    // findActiveById zwraca empty jeśli soft-deleted
    public Order getActiveOrder(UUID orderId) {
        return orderRepository.findActiveById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
    }
}
```

---

## Serwis domenowy

Pełny przykład serwisu domenowego z użyciem repozytorium:

```java
package com.example.domain;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.UUID;

@Service
@Transactional
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public UUID createProduct(String name, BigDecimal price) {
        UUID id = UUID.randomUUID();
        Product product = new Product(id, name, price);
        productRepository.save(product); // Brak eventów — nie wywołano żadnej metody biznesowej
        return id;
    }

    public void activateProduct(UUID productId) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        product.activate(); // Rejestruje ProductActivated event

        productRepository.save(product); // Zapisuje + publishuje event
    }

    public void changePrice(UUID productId, BigDecimal newPrice) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        product.changePrice(newPrice); // Rejestruje PriceChanged event

        productRepository.save(product);
        // Po save: eventy wyczyszczone z agregatu
        assert product.getEvents().isEmpty();
    }

    public boolean productExists(UUID productId) {
        return productRepository.existsById(productId);
    }
}
```

---

## Domain events jako records

```java
package com.example.domain;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

// Eventy powinny:
// - Być immutable (records)
// - Używać past tense w nazwie
// - Zawierać wszystkie dane potrzebne handlerom

public record ProductActivated(UUID productId) {}

public record ProductPriceChanged(
    UUID productId,
    BigDecimal oldPrice,
    BigDecimal newPrice
) {}

public record ProductRenamed(
    UUID productId,
    String oldName,
    String newName
) {}

public record OrderDeleted(UUID orderId, LocalDateTime deletedAt) {}

public record OrderRestored(UUID orderId) {}
```

---

## Testy jednostkowe agregatu

```java
package com.example.domain;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import java.util.UUID;
import static org.assertj.core.api.Assertions.*;

class ProductTest {

    @Test
    void shouldRegisterEventOnActivation() {
        Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));

        product.activate();

        // getEvents() — sprawdza eventy bez ich czyszczenia
        assertThat(product.getEvents()).hasSize(1);
        assertThat(product.getEvents().iterator().next()).isInstanceOf(ProductActivated.class);
    }

    @Test
    void shouldRegisterEventOnPriceChange() {
        Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));

        product.changePrice(new BigDecimal("3999.99"));

        assertThat(product.getEvents()).hasSize(1);
        ProductPriceChanged event = (ProductPriceChanged) product.getEvents().iterator().next();
        assertThat(event.oldPrice()).isEqualByComparingTo("4999.99");
        assertThat(event.newPrice()).isEqualByComparingTo("3999.99");
    }

    @Test
    void shouldClearEventsOnPull() {
        Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));
        product.activate();
        product.changePrice(new BigDecimal("3999.99"));

        // pullEvents() — zwraca eventy i czyści listę
        var events = product.pullEvents();

        assertThat(events).hasSize(2);
        assertThat(product.getEvents()).isEmpty(); // Lista wyczyszczona
    }

    @Test
    void shouldPreserveEventOrder() {
        Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));

        product.activate();
        product.changePrice(new BigDecimal("3999.99"));
        product.rename("Gaming Laptop");

        var events = product.getEvents().stream().toList();
        assertThat(events.get(0)).isInstanceOf(ProductActivated.class);
        assertThat(events.get(1)).isInstanceOf(ProductPriceChanged.class);
        assertThat(events.get(2)).isInstanceOf(ProductRenamed.class);
    }

    @Test
    void shouldRejectNegativePrice() {
        Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));

        assertThatThrownBy(() -> product.changePrice(new BigDecimal("-1")))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

---

## Testy repozytorium z mockami

```java
package com.example.infrastructure;

import com.example.domain.Product;
import com.example.domain.ProductActivated;
import com.example.domain.ProductStatus;
import io.preboot.eventbus.EventPublisher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.repository.CrudRepository;
import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class JdbcProductRepositoryTest {

    @Mock
    private CrudRepository<ProductSnapshot, UUID> snapshotRepository;

    @Mock
    private EventPublisher eventPublisher;

    private ProductMapper mapper;
    private JdbcProductRepository repository;

    @BeforeEach
    void setUp() {
        mapper = new ProductMapper();
        // Użyj konstruktora bezpośrednio w testach
        repository = new JdbcProductRepository(snapshotRepository, mapper, eventPublisher);
    }

    @Test
    void shouldSaveSnapshotAndPublishEvents() {
        UUID id = UUID.randomUUID();
        Product product = new Product(id, "Laptop", new BigDecimal("4999.99"));
        product.activate(); // Rejestruje event

        repository.save(product);

        // Weryfikuj: snapshot zapisany do DB
        verify(snapshotRepository).save(any(ProductSnapshot.class));
        // Weryfikuj: event opublikowany
        verify(eventPublisher).publish(any(ProductActivated.class));
        // Weryfikuj: eventy wyczyszczone z agregatu
        assertThat(product.getEvents()).isEmpty();
    }

    @Test
    void shouldFindByIdAndConvertToDomain() {
        UUID id = UUID.randomUUID();
        ProductSnapshot snapshot = new ProductSnapshot(id, "Laptop", new BigDecimal("4999.99"), "ACTIVE");
        when(snapshotRepository.findById(id)).thenReturn(Optional.of(snapshot));

        Optional<Product> result = repository.findById(id);

        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(id);
        assertThat(result.get().getName()).isEqualTo("Laptop");
        assertThat(result.get().getStatus()).isEqualTo(ProductStatus.ACTIVE);
    }

    @Test
    void shouldReturnEmptyForMissingAggregate() {
        UUID id = UUID.randomUUID();
        when(snapshotRepository.findById(id)).thenReturn(Optional.empty());

        Optional<Product> result = repository.findById(id);

        assertThat(result).isEmpty();
    }

    @Test
    void shouldDeleteWithoutPublishingEvents() {
        UUID id = UUID.randomUUID();

        repository.deleteById(id);

        verify(snapshotRepository).deleteById(id);
        verifyNoInteractions(eventPublisher); // Hard delete = brak eventów
    }

    @Test
    void shouldThrowOnNullAggregate() {
        assertThatThrownBy(() -> repository.save(null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Aggregate must not be null");
    }
}
```

---

## Pełny test mappera (round-trip)

```java
@Test
void shouldPreserveDataInRoundTrip() {
    UUID id = UUID.randomUUID();
    Product original = new Product(id, "Laptop", new BigDecimal("4999.99"), ProductStatus.ACTIVE);

    // Aggregate → Snapshot → Aggregate
    ProductSnapshot snapshot = mapper.toSnapshot(original);
    Product restored = mapper.toDomain(snapshot);

    assertThat(restored.getId()).isEqualTo(original.getId());
    assertThat(restored.getName()).isEqualTo(original.getName());
    assertThat(restored.getPrice()).isEqualByComparingTo(original.getPrice());
    assertThat(restored.getStatus()).isEqualTo(original.getStatus());
}

@Test
void shouldHandleNullGracefully() {
    assertThat(mapper.toDomain(null)).isNull();
    assertThat(mapper.toSnapshot(null)).isNull();
}
```
