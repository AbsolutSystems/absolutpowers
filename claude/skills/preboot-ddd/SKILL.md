---
name: preboot-ddd
description: "Skill do używania biblioteki preboot-ddd. Użyj tego skilla zawsze gdy użytkownik chce implementować agregaty DDD, persystencję agregatów, repozytorium DDD, domain events, snapshot pattern, soft delete, lub tworzy warstwę domenową. Obejmuje: AggregateRoot, AggregateRepository, AggregateMapper, SoftDeletable, AbstractAggregateRepository, AbstractPersistentTaskRepository. Triggeruje się na: DDD, aggregate, domain-driven design, repozytorium agregatów, zdarzenia domenowe, domain events, snapshot, soft delete, persystencja agregatów, warstwa domenowa, bounded context, event publishing, event bus."
---

# preboot-ddd

Moduł DDD dla frameworka PreBoot.io — dostarcza gotowe komponenty do persystencji agregatów z automatycznym publishingiem domain events.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-ddd</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Wymaga również `preboot-eventbus` (transitive dependency). Opcjonalnie `preboot-tasks` jeśli chcesz persistent event publishing.

## Szybki start

### 1. Stwórz agregat domenowy

```java
public class Product extends AggregateRoot<UUID> {
    private UUID id;
    private String name;
    private BigDecimal price;
    private ProductStatus status;

    public Product(UUID id, String name, BigDecimal price) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.status = ProductStatus.NEW;
    }

    // Wymagane — zwraca identyfikator agregatu
    @Override
    public UUID getId() {
        return id;
    }

    // Metoda biznesowa — rejestruje domain event
    public void changePrice(BigDecimal newPrice) {
        BigDecimal oldPrice = this.price;
        this.price = newPrice;
        registerEvent(new ProductPriceChanged(id, oldPrice, newPrice));
    }

    public void activate() {
        this.status = ProductStatus.ACTIVE;
        registerEvent(new ProductActivated(id));
    }
}
```

### 2. Stwórz snapshot (rekord bazodanowy)

```java
@Table("products")
public record ProductSnapshot(
    @Id UUID id,
    String name,
    BigDecimal price,
    String status
) {}
```

### 3. Stwórz mapper

```java
@Component
public class ProductMapper implements AggregateMapper<Product, ProductSnapshot, UUID> {

    @Override
    public Product toDomain(ProductSnapshot snapshot) {
        if (snapshot == null) return null;
        return new Product(
            snapshot.id(), snapshot.name(), snapshot.price(),
            ProductStatus.valueOf(snapshot.status())
        );
    }

    @Override
    public ProductSnapshot toSnapshot(Product product) {
        if (product == null) return null;
        return new ProductSnapshot(
            product.getId(), product.getName(),
            product.getPrice(), product.getStatus().name()
        );
    }
}
```

### 4. Stwórz interfejs repozytorium (warstwa domenowa)

```java
public interface ProductRepository extends AggregateRepository<Product, UUID> {
    // Opcjonalnie: dodaj custom query methods
}
```

### 5. Stwórz implementację repozytorium (warstwa infrastruktury)

```java
@Repository
public class JdbcProductRepository
        extends AbstractAggregateRepository<Product, ProductSnapshot, UUID>
        implements ProductRepository {

    // Wewnętrzny interfejs Spring Data
    interface SnapshotRepository extends CrudRepository<ProductSnapshot, UUID> {}

    public JdbcProductRepository(
            SnapshotRepository snapshotRepo,
            ProductMapper mapper,
            EventPublisher eventPublisher) {
        super(snapshotRepo, mapper, eventPublisher);
    }
}
```

### 6. Użyj w serwisie

```java
@Service
public class ProductService {
    private final ProductRepository productRepository;

    public void changePrice(UUID productId, BigDecimal newPrice) {
        Product product = productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        product.changePrice(newPrice);

        // save() automatycznie: konwertuje → zapisuje → publishuje eventy
        productRepository.save(product);
    }
}
```

## Główne koncepty

### Architektura warstwowa

```
core/ (warstwa domenowa)
├── AggregateRoot<ID>           — bazowa klasa abstrakcyjna dla agregatów
├── AggregateRepository<A, ID>  — interfejs repozytorium (domain layer)
├── AggregateMapper<A, S, ID>   — interfejs mappera agregat ↔ snapshot
└── SoftDeletable               — interfejs markujący do soft delete

infrastructure/ (warstwa infrastruktury)
├── AbstractAggregateRepository<A, S, ID>         — z in-memory event publishing
└── AbstractPersistentTaskRepository<A, S, ID>    — z persistent task publishing
```

### Wzorzec "register-then-pull"

Agregat rejestruje eventy wewnętrznie (`registerEvent()`), a repozytorium je wyciąga i publishuje po zapisie:

1. Metoda biznesowa wywołuje `registerEvent(event)` — event trafia do listy transient
2. `repository.save(aggregate)` konwertuje agregat → snapshot → zapis do DB
3. `aggregate.pullEvents()` wyciąga eventy i czyści listę
4. Każdy event jest publishowany przez EventPublisher/TaskPublisher

### Snapshot Pattern

Agregaty (rich domain model) są oddzielone od snapshotów (czyste dane do DB):
- **Agregat**: zachowanie + stan + eventy transient, nie zna DB
- **Snapshot**: record/POJO do persystencji, typy proste (String zamiast enum), bez logiki
- **Mapper**: bezstanowa translacja między nimi, żadnej logiki biznesowej

### Dwie strategie publishingu eventów

| Aspekt | `AbstractAggregateRepository` | `AbstractPersistentTaskRepository` |
|--------|-------------------------------|-------------------------------------|
| Publishing | In-memory `EventPublisher` | Persistent `TaskPublisher` |
| Przetwarzanie | Synchroniczne | Asynchroniczne |
| Niezawodność | Eventy tracone przy awarii | Eventy przeżywają restart |
| Retry | Brak | Automatyczny z exponential backoff |
| Kiedy użyć | Proste aplikacje | Systemy rozproszone, krytyczne operacje |

Migracja: zmień klasę bazową i wstrzyknij `TaskPublisher` zamiast `EventPublisher`.

### Soft Delete vs Hard Delete

| Aspekt | Soft Delete (domena) | Hard Delete (infrastruktura) |
|--------|---------------------|------------------------------|
| Operacja | `aggregate.markAsDeleted()` → `save()` | `repository.delete(aggregate)` |
| Eventy | Publikowane | Brak |
| Dane | Pozostają w DB | Usunięte permanentnie |
| Odzyskanie | `aggregate.restore()` → `save()` | Niemożliwe |

Implementuj interfejs `SoftDeletable` w agregacie. Użyj `findActiveById()` do filtrowania soft-deleted.

### Zależności od innych modułów PreBoot

- **preboot-eventbus** (wymagane) — dostarcza `EventPublisher` do synchronicznego publishingu
- **preboot-tasks** (opcjonalne, scope: provided) — dostarcza `TaskPublisher` do persistent publishingu

## Typowe przepływy

### Tworzenie nowego agregatu

```java
Product product = new Product(UUID.randomUUID(), "Laptop", new BigDecimal("4999.99"));
product.activate();
productRepository.save(product); // Zapisuje snapshot + publishuje ProductActivated
```

### Modyfikacja istniejącego agregatu

```java
Product product = productRepository.findById(id).orElseThrow();
product.changePrice(new BigDecimal("3999.99"));
productRepository.save(product); // Zapisuje zmieniony snapshot + publishuje PriceChanged
```

### Soft delete i restore

```java
// Soft delete
Product product = productRepository.findById(id).orElseThrow();
product.markAsDeleted();
productRepository.save(product); // Publishuje ProductDeleted event

// Restore
Product deleted = productRepository.findById(id).orElseThrow(); // findById zwraca też deleted
deleted.restore();
productRepository.save(deleted); // Publishuje ProductRestored event

// Filtrowanie — zwraca empty jeśli soft-deleted
Optional<Product> active = productRepository.findActiveById(id);
```

### Hard delete (GDPR, cleanup)

```java
productRepository.deleteById(id);      // Permanentne usunięcie, BEZ eventów
productRepository.delete(aggregate);   // j.w., przyjmuje agregat
```

## Pułapki i częste błędy

1. **Null ID w agregacie** — `save()` rzuca `IllegalArgumentException`. Zawsze ustawiaj ID w konstruktorze.

2. **Eventy w snapshocie** — NIGDY nie dodawaj domain events do snapshota. Eventy są transient i zarządzane przez repozytorium.

3. **Logika biznesowa w mapperze** — mapper to czysta translacja danych. Bez walidacji, bez side effects.

4. **Null handling w mapperze** — zawsze sprawdzaj `if (snapshot == null) return null;` i analogicznie dla agregatu.

5. **Zapomniany `save()` po modyfikacji** — eventy nie zostaną opublikowane jeśli nie wywołasz `repository.save()`.

6. **Double `markAsDeleted()`** — rzuca `IllegalStateException`. Sprawdź `isDeleted()` przed wywołaniem.

7. **Hard delete zamiast soft delete** — `repository.delete()` NIE publishuje eventów. Do domain-driven usuwania użyj `markAsDeleted()` + `save()`.

8. **Brak `preboot-tasks` w classpath** — jeśli używasz `AbstractPersistentTaskRepository`, dodaj zależność `preboot-tasks`.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury metod, parametry, wyjątki, typy generyczne
- **examples.md** — kompletne przykłady: agregat z soft delete, persistent tasks, testy, domain events
