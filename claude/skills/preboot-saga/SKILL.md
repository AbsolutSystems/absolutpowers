---
name: preboot-saga
description: "Skill do używania biblioteki preboot-saga. Użyj tego skilla zawsze gdy użytkownik chce implementować saga pattern, orkiestrację procesów biznesowych, distributed transactions, long-running business processes, kompensację transakcji, zarządzanie stanem procesu, workflow z wieloma krokami, lub koordynację między serwisami. Obejmuje: @Saga, @SagaStart, @SagaEventHandler, @CompensationHandler, @SagaTimeout, ErrorStrategy (INHERIT/COMPENSATE/RETRY/IGNORE/FAIL), SagaContext, SagaPublisher, SagaRunner, SagaLifecycleState, SagaQueryService, SagaVisualizationService, SagaTestFixture, SagaInstance, SagaMetrics, sub-sagas, SagaProperties, SagaSchedulingProperties. Triggeruje się na: saga, saga pattern, orchestration, distributed transaction, compensation, compensating transaction, long-running process, business process, process manager, workflow orchestration, rollback, undo, saga state, saga event, saga timeout, saga retry, saga compensation, saga lifecycle, saga monitoring, saga metrics, saga visualization, mermaid diagram, sub-saga, child saga, parent saga, saga test fixture, BDD saga test, event-driven workflow, preboot saga, saga correlation, correlation ID, saga event handler, saga start, saga error strategy, multi-step transaction, transaction coordinator, saga runner, saga publisher, saga query."
---

# preboot-saga

Moduł implementujący Saga Pattern do orkiestracji długo-trwających procesów biznesowych i rozproszonych transakcji. Każda saga to klasa z adnotacjami definiującymi event handlery, compensation handlery i timeouty. Framework automatycznie zarządza stanem sagi, kolejką eventów, kompensacją (LIFO), i monitoringiem — wszystko persystowane w PostgreSQL.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-saga</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Wymaga: `preboot-core`, `spring-boot-starter-data-jdbc`, `spring-boot-starter-json`, `postgresql`, `liquibase-core`.

## Szybki start

### 1. Zdefiniuj sagę

```java
@Saga(correlationProperty = "orderId", timeout = "30m", errorStrategy = ErrorStrategy.COMPENSATE)
public class OrderSaga {

    @SagaStart
    @SagaEventHandler
    public void onOrderCreated(SagaContext<OrderState> ctx, OrderCreatedEvent event) {
        OrderState state = new OrderState();
        state.orderId = event.orderId();
        state.status = "CREATED";
        ctx.setState(state);
        ctx.publish(new ReserveInventoryCommand(event.orderId()));
    }

    @SagaEventHandler
    public void onInventoryReserved(SagaContext<OrderState> ctx, InventoryReservedEvent event) {
        OrderState state = ctx.getState();
        state.inventoryReserved = true;
        state.status = "INVENTORY_RESERVED";
        ctx.setState(state);
        ctx.publish(new ProcessPaymentCommand(state.orderId));
    }

    @SagaEventHandler
    public void onPaymentProcessed(SagaContext<OrderState> ctx, PaymentProcessedEvent event) {
        OrderState state = ctx.getState();
        state.status = "COMPLETED";
        ctx.setState(state);
        ctx.completeSaga();
    }

    @CompensationHandler(InventoryReservedEvent.class)
    public void compensateInventory(SagaContext<OrderState> ctx) {
        // Zwolnij zarezerwowany inventarz
    }

    @SagaTimeout
    public void onTimeout(SagaContext<OrderState> ctx) {
        ctx.compensate("Order timed out after 30 minutes");
    }

    public static class OrderState {
        public String orderId;
        public String status;
        public boolean inventoryReserved;
    }
}
```

### 2. Uruchom sagę

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final SagaPublisher sagaPublisher;

    public UUID createOrder(String orderId) {
        return sagaPublisher.startSaga(
            OrderSaga.class,
            new OrderCreatedEvent(orderId, "CUSTOMER-1", 99.99)
        );
    }

    public void processPayment(String orderId) {
        sagaPublisher.publishToSaga(
            new PaymentProcessedEvent(orderId, "TXN-123", 99.99)
        );
    }
}
```

### 3. Konfiguracja — automatyczna

Schemat bazy danych tworzony automatycznie przez Liquibase (tabele: `sagas`, `saga_events`, `saga_compensations`, `saga_event_queue`). Scheduling włączony domyślnie.

## Główne koncepty

### Architektura

```
@Saga class (twoja klasa)
├── @SagaStart + @SagaEventHandler  — handler startowy (dokładnie 1)
├── @SagaEventHandler               — handlery kolejnych eventów (0..N)
├── @CompensationHandler(Event.class) — handlery kompensacji (0..N, LIFO)
└── @SagaTimeout                     — handler timeout (0..1)

SagaPublisher → startSaga() / publishToSaga()
    └── event → saga_event_queue (PostgreSQL)
        └── SagaRunner → procesuje eventy, wywołuje handlery
            └── SagaContext<T> — API w handlerach (state, publish, complete, compensate)
```

### Lifecycle state

```
STARTED → RUNNING → COMPLETED (sukces)
                  → COMPENSATING → COMPENSATED (kompensacja OK)
                  → COMPENSATING → FAILED (kompensacja błąd)
                  → TIMED_OUT (timeout)
                  → FAILED (ErrorStrategy.FAIL)
```

### Kluczowe klasy

| Klasa | Rola |
|-------|------|
| `@Saga` | Adnotacja na klasie — definiuje correlationProperty, timeout, errorStrategy, maxRetries |
| `@SagaStart` | Marker na metodzie — handler startowy (musi być też `@SagaEventHandler`) |
| `@SagaEventHandler` | Adnotacja na metodzie — handler eventu. Sygnatura: `(SagaContext<T>, Event)` |
| `@CompensationHandler(Event.class)` | Adnotacja na metodzie — kompensacja dla eventu. Sygnatura: `(SagaContext<T>)` |
| `@SagaTimeout` | Marker na metodzie — handler timeout. Sygnatura: `(SagaContext<T>)` |
| `ErrorStrategy` | Enum: INHERIT, COMPENSATE, RETRY, IGNORE, FAIL |
| `SagaContext<T>` | API w handlerach — getState/setState, publish, completeSaga, compensate, startSubSaga |
| `SagaPublisher` | Entry point — startSaga(Class, event), publishToSaga(event) |
| `SagaRunner` | Event processing engine (auto-konfigurowany) |
| `SagaLifecycleState` | Enum stanów: STARTED, RUNNING, COMPENSATING, COMPLETED, FAILED, COMPENSATED, TIMED_OUT |
| `SagaQueryService` | Monitoring — findBySagaId, findByState, getMetrics, getEventHistory |
| `SagaVisualizationService` | Diagramy Mermaid — exportToMermaid, exportSagaDefinitionToMermaid |
| `SagaTestFixture<S,T>` | BDD testing — givenNoPriorActivity/whenStartingWith/thenExpectState |

### Adnotacje — szczegóły

| Adnotacja | Parametry |
|-----------|-----------|
| `@Saga` | `correlationProperty` (wymagane), `timeout` (np. "30m", "1h"), `errorStrategy` (default COMPENSATE), `maxRetries` (default 3), `version` (default 1) |
| `@SagaEventHandler` | `errorStrategy` (default INHERIT), `maxRetries` (default -1 = inherit) |
| `@CompensationHandler` | `value` = klasa eventu do kompensacji |

### ErrorStrategy

| Strategia | Zachowanie |
|-----------|-----------|
| `INHERIT` | Używa strategii z `@Saga` (domyślna dla handlerów) |
| `COMPENSATE` | Błąd → uruchom kompensację (LIFO) |
| `RETRY` | Retry z exponential backoff, potem kompensacja |
| `IGNORE` | Loguj błąd, kontynuuj sagę (niebezpieczne!) |
| `FAIL` | Oznacz sagę jako FAILED natychmiast, bez kompensacji |

### Correlation — jak saga łączy eventy

Parametr `@Saga(correlationProperty = "orderId")` mówi frameworkowi, aby wyciągnął wartość `orderId` z każdego eventu (getter, field, record component, nawet nested dot notation np. `order.id`). Wszystkie eventy z tym samym `correlationId` trafiają do tej samej instancji sagi.

### Kompensacja — kolejność LIFO

Handlery kompensacji (`@CompensationHandler`) wykonywane są w odwrotnej kolejności do przetworzonych eventów. Jeśli saga przetworzyła eventy A → B → C, kompensacja uruchamia handlery dla C → B → A.

### Sub-sagas

Saga może uruchomić pod-sagę przez `ctx.startSubSaga(ChildSaga.class, startEvent)`. Pod-saga ma własny cykl życia, stan i eventy, ale jest powiązana z rodzicem przez `parent_saga_id`. Maksymalna głębokość: `preboot.saga.max-sub-saga-depth` (domyślnie 10).

### Konfiguracja

```yaml
# application.yml
preboot:
  saga:
    enabled: true                    # Włącz/wyłącz moduł (default: true)
    runner-id-prefix: "saga-runner-" # Prefiks ID runnera (default: "saga-runner-")
    max-sub-saga-depth: 10           # Max głębokość sub-sag (default: 10)
    scheduling:
      enabled: true                  # Włącz scheduling (default: true)
      max-concurrent-events: 4      # Wątki robocze (default: 4)
      auto-start: true               # Auto-start (false dla testów)
      heartbeat-interval: PT3M
      timeout-check-interval: PT1M
      compensation-check-interval: PT30S
      stalled-check-interval: PT15M
      stalled-threshold: PT5M
      cleanup-interval: PT1H         # null = wyłączony
      cleanup-threshold: P7D
```

### Zależności od innych modułów PreBoot

- **preboot-core** (wymagane) — JsonMapper, utilities

## Typowe przepływy

### Saga z UUID repo i event publishing

```java
@Saga(correlationProperty = "orderId", timeout = "1h")
public class OrderSaga {
    @SagaStart @SagaEventHandler
    public void onOrderCreated(SagaContext<OrderState> ctx, OrderCreatedEvent event) {
        ctx.setState(new OrderState(event.orderId()));
        ctx.publish(new ReserveInventoryCommand(event.orderId(), event.items()));
    }

    @SagaEventHandler
    public void onInventoryReserved(SagaContext<OrderState> ctx, InventoryReservedEvent event) {
        ctx.getState().setInventoryReserved(true);
        ctx.setState(ctx.getState());
        ctx.publish(new ProcessPaymentCommand(ctx.getState().getOrderId()));
    }

    @SagaEventHandler
    public void onPaymentProcessed(SagaContext<OrderState> ctx, PaymentProcessedEvent event) {
        ctx.getState().setPaymentProcessed(true);
        ctx.setState(ctx.getState());
        ctx.publish(new ShipOrderCommand(ctx.getState().getOrderId()));
    }

    @SagaEventHandler
    public void onOrderShipped(SagaContext<OrderState> ctx, OrderShippedEvent event) {
        ctx.completeSaga();
    }

    @CompensationHandler(InventoryReservedEvent.class)
    public void compensateInventory(SagaContext<OrderState> ctx) { /* release inventory */ }

    @CompensationHandler(PaymentProcessedEvent.class)
    public void compensatePayment(SagaContext<OrderState> ctx) { /* refund payment */ }

    @SagaTimeout
    public void onTimeout(SagaContext<OrderState> ctx) {
        ctx.compensate("Order processing timed out");
    }
}
```

### Monitoring

```java
@Service
@RequiredArgsConstructor
public class SagaMonitoringService {
    private final SagaQueryService queryService;

    public void checkOrder(String orderId) {
        queryService.findByCorrelationId("com.example.OrderSaga", orderId)
            .ifPresent(saga -> {
                System.out.println("Status: " + saga.lifecycleState());
                System.out.println("Events: " + saga.eventsProcessed());
            });
    }

    public void showMetrics() {
        SagaMetrics metrics = queryService.getMetrics("com.example.OrderSaga");
        System.out.println("Success rate: " + (metrics.getSuccessRate() * 100) + "%");
    }
}
```

### Unit testing z SagaTestFixture

```java
@Test
void testHappyPath() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderState.class)
        .givenNoPriorActivity()
        .whenStartingWith(new OrderCreatedEvent("ORDER-1", "CUST-1", 100.0))
        .thenExpectState(state -> assertThat(state.orderId).isEqualTo("ORDER-1"))
        .thenExpectLifecycleState(SagaLifecycleState.RUNNING)
        .whenPublishing(new PaymentProcessedEvent("ORDER-1", "TXN-1", 100.0))
        .thenExpectCompleted();
}
```

## Pułapki i częste błędy

1. **Brak `@SagaStart` na handlerze startowym** — każda saga musi mieć dokładnie jeden handler z `@SagaStart` + `@SagaEventHandler`. Bez tego saga nie może zostać wystartowana.

2. **Brak `@SagaEventHandler` na `@SagaStart`** — `@SagaStart` to marker, musi być w parze z `@SagaEventHandler`.

3. **Sygnatura handlera** — `@SagaEventHandler`: `(SagaContext<T> ctx, EventType event)`. `@CompensationHandler` i `@SagaTimeout`: `(SagaContext<T> ctx)` — bez parametru eventu.

4. **Zapomnienie `ctx.setState(state)`** — ZAWSZE wywołaj `setState()` po modyfikacji stanu, nawet jeśli mutowałeś obiekt in-place. Inaczej zmiany nie zostaną persystowane.

5. **correlationProperty musi istnieć na eventach** — framework wyciąga `correlationProperty` z eventów przez refleksję. Jeśli event nie ma tego pola/gettera, rzuci `IllegalArgumentException`.

6. **`deleteAll()` analogia** — saga nie wspiera bulk operacji. Każdy event jest procesowany indywidualnie.

7. **ErrorStrategy.IGNORE jest niebezpieczna** — loguje błąd ale kontynuuje sagę, co może prowadzić do niespójnego stanu.

8. **Timeout format** — format ISO-8601 duration: `"30m"` = 30 minut, `"1h"` = 1 godzina, `"P1D"` = 1 dzień. Pusty string = brak timeout.

9. **CompensationHandler.value()** — musi wskazywać na klasę eventu (nie handlera). Kompensacja jest wywoływana w odwrotnej kolejności procesowania eventów.

10. **Sub-saga depth** — domyślnie max 10 poziomów zagnieżdżenia. Przekroczenie rzuci `IllegalStateException`.

11. **Scheduling w testach** — ustaw `preboot.saga.scheduling.auto-start=false` i ręcznie wywołuj `sagaRunner.runSagaEvent()`.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury wszystkich interfejsów, adnotacji, enumów, DTOs, repozytoriów, konfiguracji scheduling
- **examples.md** — kompletne przykłady: pełna saga z kompensacją, sub-sagas (parent/child), unit testy z SagaTestFixture, monitoring z SagaQueryService, konfiguracja scheduling
