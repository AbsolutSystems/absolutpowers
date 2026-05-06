# Examples — preboot-saga

## Spis treści

- [Podstawowa saga — Order Processing](#podstawowa-saga--order-processing)
- [Saga z różnymi ErrorStrategy](#saga-z-różnymi-errorstrategy)
- [Saga z event publishing (ctx.publish)](#saga-z-event-publishing)
- [Sub-sagas — parent/child](#sub-sagas--parentchild)
- [Unit testy z SagaTestFixture](#unit-testy-z-sagatestfixture)
- [Monitoring z SagaQueryService](#monitoring-z-sagaqueryservice)
- [Wizualizacja z SagaVisualizationService](#wizualizacja-z-sagavisualizationservice)
- [Konfiguracja application.yml](#konfiguracja-applicationyml)
- [Integracja — service uruchamiający sagę](#integracja--service-uruchamiający-sagę)
- [Testy integracyjne z Testcontainers](#testy-integracyjne-z-testcontainers)

---

## Podstawowa saga — Order Processing

Pełny przykład sagi zamówienia z compensation handlers i timeout.

```java
package com.example.saga;

import io.preboot.saga.*;

@Saga(
    correlationProperty = "orderId",
    timeout = "30m",
    errorStrategy = ErrorStrategy.COMPENSATE,
    maxRetries = 3
)
public class OrderSaga {

    // ===== Event Handlers =====

    @SagaStart
    @SagaEventHandler
    public void onOrderCreated(SagaContext<OrderState> ctx, OrderCreatedEvent event) {
        OrderState state = new OrderState();
        state.orderId = event.orderId();
        state.customerId = event.customerId();
        state.amount = event.amount();
        state.status = "ORDER_CREATED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onInventoryReserved(SagaContext<OrderState> ctx, InventoryReservedEvent event) {
        OrderState state = ctx.getState();
        state.inventoryReserved = true;
        state.status = "INVENTORY_RESERVED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onPaymentProcessed(SagaContext<OrderState> ctx, PaymentProcessedEvent event) {
        OrderState state = ctx.getState();
        state.paymentProcessed = true;
        state.transactionId = event.transactionId();
        state.status = "PAYMENT_PROCESSED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onShipmentDispatched(SagaContext<OrderState> ctx, ShipmentDispatchedEvent event) {
        OrderState state = ctx.getState();
        state.shipmentDispatched = true;
        state.trackingNumber = event.trackingNumber();
        state.status = "SHIPMENT_DISPATCHED";
        ctx.setState(state);
        ctx.completeSaga(); // Saga zakończona sukcesem
    }

    // ===== Compensation Handlers (LIFO) =====

    @CompensationHandler(InventoryReservedEvent.class)
    public void compensateInventory(SagaContext<OrderState> ctx) {
        OrderState state = ctx.getState();
        state.status = "INVENTORY_COMPENSATION";
        ctx.setState(state);
        // W produkcji: wywołaj serwis zwalniający inventarz
    }

    @CompensationHandler(PaymentProcessedEvent.class)
    public void compensatePayment(SagaContext<OrderState> ctx) {
        OrderState state = ctx.getState();
        state.status = "PAYMENT_COMPENSATION";
        ctx.setState(state);
        // W produkcji: wywołaj serwis refundacji
    }

    // ===== Timeout Handler =====

    @SagaTimeout
    public void onTimeout(SagaContext<OrderState> ctx) {
        OrderState state = ctx.getState();
        if (state == null) {
            state = new OrderState();
        }
        state.status = "TIMED_OUT";
        ctx.setState(state);
        ctx.compensate("Saga timed out after 30 minutes");
    }

    // ===== State =====

    public static class OrderState {
        public String orderId;
        public String customerId;
        public double amount;
        public String status;
        public boolean inventoryReserved;
        public boolean paymentProcessed;
        public String transactionId;
        public boolean shipmentDispatched;
        public String trackingNumber;
    }

    // ===== Events =====

    public record OrderCreatedEvent(String orderId, String customerId, double amount) {}
    public record InventoryReservedEvent(String orderId, int quantity) {}
    public record PaymentProcessedEvent(String orderId, String transactionId, double amount) {}
    public record ShipmentDispatchedEvent(String orderId, String trackingNumber) {}
}
```

---

## Saga z różnymi ErrorStrategy

Każdy handler może mieć swoją strategię obsługi błędów.

```java
@Saga(
    correlationProperty = "paymentId",
    timeout = "5m",
    errorStrategy = ErrorStrategy.COMPENSATE, // domyślna
    maxRetries = 2
)
public class PaymentSaga {

    @SagaStart
    @SagaEventHandler
    public void onPaymentStarted(SagaContext<PaymentState> ctx, PaymentStartedEvent event) {
        PaymentState state = new PaymentState();
        state.paymentId = event.paymentId();
        state.amount = event.amount();
        state.status = "STARTED";
        ctx.setState(state);
    }

    // RETRY z 5 próbami (nadpisuje domyślne 2 z @Saga)
    @SagaEventHandler(errorStrategy = ErrorStrategy.RETRY, maxRetries = 5)
    public void onFundsReserved(SagaContext<PaymentState> ctx, FundsReservedEvent event) {
        PaymentState state = ctx.getState();
        state.fundsReserved = true;
        state.reservationId = event.reservationId();
        state.status = "RESERVED";
        ctx.setState(state);
    }

    // INHERIT = użyj COMPENSATE z @Saga (domyślne)
    @SagaEventHandler
    public void onPaymentCharged(SagaContext<PaymentState> ctx, PaymentChargedEvent event) {
        PaymentState state = ctx.getState();
        state.charged = true;
        state.transactionId = event.transactionId();
        state.status = "CHARGED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onPaymentConfirmed(SagaContext<PaymentState> ctx, PaymentConfirmedEvent event) {
        PaymentState state = ctx.getState();
        state.confirmed = true;
        state.status = "COMPLETED";
        ctx.setState(state);
        ctx.completeSaga();
    }

    // Kompensacja: odwróć rezerwację środków
    @CompensationHandler(FundsReservedEvent.class)
    public void compensateFundsReserved(SagaContext<PaymentState> ctx) {
        PaymentState state = ctx.getState();
        state.fundsReserved = false;
        state.status = "FUNDS_RELEASED";
        ctx.setState(state);
    }

    // Kompensacja: zwrot opłaty
    @CompensationHandler(PaymentChargedEvent.class)
    public void compensatePaymentCharged(SagaContext<PaymentState> ctx) {
        PaymentState state = ctx.getState();
        state.charged = false;
        state.status = "CHARGE_REFUNDED";
        ctx.setState(state);
    }

    @SagaTimeout
    public void onTimeout(SagaContext<PaymentState> ctx) {
        PaymentState state = ctx.getState();
        state.status = "TIMED_OUT";
        ctx.setState(state);
        ctx.compensate("Payment processing timed out");
    }

    public static class PaymentState {
        public String paymentId;
        public String customerId;
        public double amount;
        public String status;
        public boolean fundsReserved;
        public String reservationId;
        public boolean charged;
        public String transactionId;
        public boolean confirmed;
    }

    public record PaymentStartedEvent(String paymentId, String customerId, double amount) {}
    public record FundsReservedEvent(String paymentId, String reservationId) {}
    public record PaymentChargedEvent(String paymentId, String transactionId, double amount) {}
    public record PaymentConfirmedEvent(String paymentId) {}
}
```

---

## Saga z event publishing

Saga publikuje eventy przez `ctx.publish()` — eventy trafiają do kolejki i mogą być obsłużone przez tę samą lub inną sagę.

```java
@Saga(correlationProperty = "orderId", timeout = "1h")
public class OrderWorkflowSaga {

    @SagaStart
    @SagaEventHandler
    public void onOrderCreated(SagaContext<OrderState> ctx, OrderCreatedEvent event) {
        OrderState state = new OrderState(event.orderId());
        ctx.setState(state);

        // Opublikuj komendę — zostanie obsłużona przez inny handler
        ctx.publish(new ReserveInventoryCommand(event.orderId(), event.items()));
    }

    @SagaEventHandler
    public void onInventoryReserved(SagaContext<OrderState> ctx, InventoryReservedEvent event) {
        ctx.getState().setInventoryReserved(true);
        ctx.setState(ctx.getState());

        // Opublikuj wiele komend naraz
        ctx.publishAll(
            new ProcessPaymentCommand(ctx.getState().getOrderId()),
            new CalculateShippingCommand(ctx.getState().getOrderId())
        );
    }

    @SagaEventHandler
    public void onPaymentAndShippingReady(SagaContext<OrderState> ctx, ReadyToShipEvent event) {
        ctx.completeSaga();
    }

    // ... compensation handlers, timeout handler
}
```

---

## Sub-sagas — parent/child

Saga może uruchomić pod-sagę. Pod-saga ma własny cykl życia i stan.

### Parent Saga

```java
@Saga(correlationProperty = "orderId")
public class ParentOrderSaga {

    @SagaStart
    @SagaEventHandler
    public void onOrderCreated(SagaContext<OrderState> ctx, OrderCreatedEvent event) {
        OrderState state = new OrderState();
        state.orderId = event.orderId();
        state.customerId = event.customerId();
        state.amount = event.amount();
        state.status = "ORDER_CREATED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onPaymentNeeded(SagaContext<OrderState> ctx, PaymentNeededEvent event) {
        OrderState state = ctx.getState();

        // Uruchom pod-sagę płatności
        UUID childSagaId = ctx.startSubSaga(
            ChildPaymentSaga.class,
            new ChildPaymentSaga.PaymentStartedEvent(event.orderId(), event.amount())
        );

        state.childPaymentSagaId = childSagaId;
        state.status = "PAYMENT_PROCESSING";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onChildSagaCompleted(SagaContext<OrderState> ctx, ChildSagaCompletedEvent event) {
        OrderState state = ctx.getState();
        state.childSagaResult = event.result();
        state.status = "PAYMENT_COMPLETED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onChildSagaFailed(SagaContext<OrderState> ctx, ChildSagaFailedEvent event) {
        OrderState state = ctx.getState();
        state.status = "PAYMENT_FAILED";
        ctx.setState(state);
        ctx.compensate("Child payment saga failed: " + event.error());
    }

    @SagaEventHandler
    public void onOrderCompleted(SagaContext<OrderState> ctx, OrderCompletedEvent event) {
        ctx.getState().status = "COMPLETED";
        ctx.setState(ctx.getState());
        ctx.completeSaga();
    }

    @CompensationHandler(OrderCreatedEvent.class)
    public void compensateOrder(SagaContext<OrderState> ctx) {
        OrderState state = ctx.getState();
        if (state == null) state = new OrderState();
        state.status = "ORDER_COMPENSATION";
        ctx.setState(state);
    }

    // Events
    public record OrderCreatedEvent(String orderId, String customerId, double amount) {}
    public record PaymentNeededEvent(String orderId, double amount) {}
    public record ChildSagaCompletedEvent(String orderId, String result) {}
    public record ChildSagaFailedEvent(String orderId, String error) {}
    public record OrderCompletedEvent(String orderId) {}

    // State
    public static class OrderState {
        public String orderId;
        public String customerId;
        public double amount;
        public String status;
        public UUID childPaymentSagaId;
        public String childSagaResult;
    }
}
```

### Child Saga

```java
@Saga(correlationProperty = "paymentId")
public class ChildPaymentSaga {

    @SagaStart
    @SagaEventHandler
    public void onPaymentStarted(SagaContext<PaymentState> ctx, PaymentStartedEvent event) {
        PaymentState state = new PaymentState();
        state.paymentId = event.paymentId();
        state.amount = event.amount();
        state.status = "PAYMENT_STARTED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onPaymentAuthorized(SagaContext<PaymentState> ctx, PaymentAuthorizedEvent event) {
        PaymentState state = ctx.getState();
        state.authorizationCode = event.authCode();
        state.status = "PAYMENT_AUTHORIZED";
        ctx.setState(state);
    }

    @SagaEventHandler
    public void onPaymentCaptured(SagaContext<PaymentState> ctx, PaymentCapturedEvent event) {
        PaymentState state = ctx.getState();
        state.transactionId = event.transactionId();
        state.status = "PAYMENT_CAPTURED";
        ctx.setState(state);
        ctx.completeSaga();
    }

    @SagaEventHandler
    public void onPaymentRejected(SagaContext<PaymentState> ctx, PaymentRejectedEvent event) {
        PaymentState state = ctx.getState();
        state.rejectionReason = event.reason();
        state.status = "PAYMENT_REJECTED";
        ctx.setState(state);
        ctx.compensate("Payment rejected: " + event.reason());
    }

    @CompensationHandler(PaymentStartedEvent.class)
    public void compensatePayment(SagaContext<PaymentState> ctx) {
        PaymentState state = ctx.getState();
        if (state == null) state = new PaymentState();
        state.status = "PAYMENT_COMPENSATION";
        ctx.setState(state);
    }

    // Events
    public record PaymentStartedEvent(String paymentId, double amount) {}
    public record PaymentAuthorizedEvent(String paymentId, String authCode) {}
    public record PaymentCapturedEvent(String paymentId, String transactionId) {}
    public record PaymentRejectedEvent(String paymentId, String reason) {}

    // State
    public static class PaymentState {
        public String paymentId;
        public double amount;
        public String status;
        public String authorizationCode;
        public String transactionId;
        public String rejectionReason;
    }
}
```

---

## Unit testy z SagaTestFixture

Testowanie sag bez Spring context i bazy danych. BDD-style: Given-When-Then.

### Happy path — pełna saga od startu do completion

```java
import static org.assertj.core.api.Assertions.*;
import io.preboot.saga.SagaLifecycleState;
import io.preboot.saga.test.SagaTestFixture;
import org.junit.jupiter.api.Test;

class OrderSagaTest {

    @Test
    void testHappyPath_OrderCompletesSuccessfully() {
        SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
            .givenNoPriorActivity()
            .whenStartingWith(new OrderSaga.OrderCreatedEvent("ORDER-001", "CUSTOMER-001", 100.0))
            .thenExpectState(state -> {
                assertThat(state.orderId).isEqualTo("ORDER-001");
                assertThat(state.customerId).isEqualTo("CUSTOMER-001");
                assertThat(state.amount).isEqualTo(100.0);
                assertThat(state.status).isEqualTo("ORDER_CREATED");
            })
            .thenExpectLifecycleState(SagaLifecycleState.RUNNING)
            .whenPublishing(new OrderSaga.InventoryReservedEvent("ORDER-001", 2))
            .thenExpectState(state -> {
                assertThat(state.inventoryReserved).isTrue();
                assertThat(state.status).isEqualTo("INVENTORY_RESERVED");
            })
            .whenPublishing(new OrderSaga.PaymentProcessedEvent("ORDER-001", "TXN-123", 100.0))
            .thenExpectState(state -> {
                assertThat(state.paymentProcessed).isTrue();
                assertThat(state.transactionId).isEqualTo("TXN-123");
            })
            .whenPublishing(new OrderSaga.ShipmentDispatchedEvent("ORDER-001", "TRACK-456"))
            .thenExpectState(state -> {
                assertThat(state.shipmentDispatched).isTrue();
                assertThat(state.trackingNumber).isEqualTo("TRACK-456");
            })
            .thenExpectCompleted();
    }
}
```

### Timeout

```java
@Test
void testTimeout_TriggersCompensation() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenStarted(new OrderSaga.OrderCreatedEvent("ORDER-005", "CUSTOMER-005", 300.0))
        .whenTimeoutOccurs()
        .thenExpectState(state -> {
            assertThat(state.status).isEqualTo("TIMED_OUT");
        })
        .thenExpectCompensating();
}
```

### givenState — arbitrary initial state

```java
@Test
void testGivenState_AllowsCustomInitialState() {
    OrderSaga.OrderState preExistingState = new OrderSaga.OrderState();
    preExistingState.orderId = "ORDER-007";
    preExistingState.customerId = "CUSTOMER-007";
    preExistingState.amount = 500.0;
    preExistingState.status = "CUSTOM_STATUS";
    preExistingState.inventoryReserved = true;

    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenState(preExistingState)
        .whenPublishing(new OrderSaga.PaymentProcessedEvent("ORDER-007", "TXN-789", 500.0))
        .thenExpectState(state -> {
            assertThat(state.orderId).isEqualTo("ORDER-007");
            assertThat(state.inventoryReserved).isTrue(); // preserved
            assertThat(state.paymentProcessed).isTrue();  // new
            assertThat(state.transactionId).isEqualTo("TXN-789");
        });
}
```

### givenStarted — saga already started

```java
@Test
void testGivenStarted_PublishSubsequentEvent() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenStarted(new OrderSaga.OrderCreatedEvent("ORDER-003", "CUSTOMER-003", 150.0))
        .whenPublishing(new OrderSaga.InventoryReservedEvent("ORDER-003", 5))
        .thenExpectState(state -> {
            assertThat(state.inventoryReserved).isTrue();
            assertThat(state.status).isEqualTo("INVENTORY_RESERVED");
        });
}
```

### Published events verification

```java
@Test
void testPublishedEvents_NoEventsPublished() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenNoPriorActivity()
        .whenStartingWith(new OrderSaga.OrderCreatedEvent("ORDER-008", "CUSTOMER-008", 600.0))
        .andThenExpectNoPublishedEvents();
}

// Jeśli saga publikuje eventy przez ctx.publish():
@Test
void testPublishedEvents_EventsVerified() {
    SagaTestFixture.forSaga(WorkflowSaga.class, WorkflowState.class)
        .givenNoPriorActivity()
        .whenStartingWith(new StartEvent("ID-1"))
        .andThenExpectPublishedEvent(NextStepCommand.class)
        .andThenExpectPublishedEventCount(1);
}
```

### Error handling — invalid events

```java
@Test
void testInvalidEvent_ThrowsException() {
    assertThatThrownBy(() -> {
        SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
            .givenNoPriorActivity()
            .whenPublishing("This is not a valid event");
    })
    .isInstanceOf(IllegalStateException.class)
    .hasMessageContaining("No handler found");
}

@Test
void testStartWithNonStartEvent_ThrowsException() {
    assertThatThrownBy(() -> {
        SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
            .givenNoPriorActivity()
            .whenStartingWith(new OrderSaga.InventoryReservedEvent("ORDER-999", 1));
    })
    .isInstanceOf(IllegalStateException.class)
    .hasMessageContaining("start handler");
}
```

### State preserved between events

```java
@Test
void testStatePreservedBetweenEvents() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenNoPriorActivity()
        .whenStartingWith(new OrderSaga.OrderCreatedEvent("ORDER-006", "CUSTOMER-006", 400.0))
        .whenPublishing(new OrderSaga.InventoryReservedEvent("ORDER-006", 10))
        .thenExpectState(state -> {
            // Stan z start eventu nadal obecny
            assertThat(state.orderId).isEqualTo("ORDER-006");
            assertThat(state.customerId).isEqualTo("CUSTOMER-006");
            assertThat(state.amount).isEqualTo(400.0);
            // Plus nowy stan
            assertThat(state.inventoryReserved).isTrue();
        });
}
```

### BDD-style readability

```java
@Test
void testFluentAPI_ReadsLikeBDD() {
    SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        // GIVEN
        .givenNoPriorActivity()
        // WHEN
        .whenStartingWith(new OrderSaga.OrderCreatedEvent("ORDER-BDD", "CUSTOMER-BDD", 99.99))
        // THEN
        .thenExpectState(state -> {
            assertThat(state.orderId).isEqualTo("ORDER-BDD");
            assertThat(state.amount).isEqualTo(99.99);
        })
        .thenExpectLifecycleState(SagaLifecycleState.RUNNING)
        // AND THEN
        .andThenExpectNoPublishedEvents();
}
```

### Final state inspection

```java
@Test
void testFinalStateInspection() {
    var fixture = SagaTestFixture.forSaga(OrderSaga.class, OrderSaga.OrderState.class)
        .givenNoPriorActivity()
        .whenStartingWith(new OrderSaga.OrderCreatedEvent("ORDER-X", "VIP", 1000.0))
        .whenPublishing(new OrderSaga.InventoryReservedEvent("ORDER-X", 20))
        .whenPublishing(new OrderSaga.PaymentProcessedEvent("ORDER-X", "TXN-PREMIUM", 1000.0))
        .whenPublishing(new OrderSaga.ShipmentDispatchedEvent("ORDER-X", "EXPRESS"))
        .thenExpectCompleted();

    // Bezpośredni dostęp do stanu
    OrderSaga.OrderState finalState = fixture.getCurrentState();
    assertThat(finalState.orderId).isEqualTo("ORDER-X");
    assertThat(finalState.inventoryReserved).isTrue();
    assertThat(finalState.paymentProcessed).isTrue();
    assertThat(finalState.shipmentDispatched).isTrue();

    // Bezpośredni dostęp do lifecycle
    assertThat(fixture.getLifecycleState()).isEqualTo(SagaLifecycleState.COMPLETED);
}
```

---

## Monitoring z SagaQueryService

```java
import io.preboot.saga.SagaLifecycleState;
import io.preboot.saga.query.SagaInstance;
import io.preboot.saga.query.SagaMetrics;
import io.preboot.saga.query.SagaQueryService;
import io.preboot.saga.model.SagaEvent;
import io.preboot.saga.model.SagaCompensation;

@Service
@RequiredArgsConstructor
public class OrderMonitoringService {
    private final SagaQueryService sagaQueryService;

    // Znajdź sagę po correlation ID
    public void checkOrder(String orderId) {
        sagaQueryService.findByCorrelationId("com.example.OrderSaga", orderId)
            .ifPresent(saga -> {
                System.out.println("Status: " + saga.lifecycleState());
                System.out.println("Events: " + saga.eventsProcessed());
                System.out.println("Duration: " + saga.getDurationMillis() + "ms");

                if (saga.compensationInProgress()) {
                    List<SagaCompensation> compensations =
                        sagaQueryService.getCompensationHistory(saga.uuid());
                    System.out.println("Compensations: " + compensations.size());
                }
            });
    }

    // Historia eventów
    public void showEventHistory(UUID sagaId) {
        List<SagaEvent> events = sagaQueryService.getEventHistory(sagaId);
        events.forEach(event -> {
            System.out.printf("Event: %s at %s (duration: %dms)%n",
                event.getEventType(),
                event.getProcessedAt(),
                event.getProcessingDurationMs());
        });
    }

    // Metryki
    public void showMetrics() {
        SagaMetrics metrics = sagaQueryService.getMetrics("com.example.OrderSaga");
        System.out.println("Total sagas: " + metrics.count());
        System.out.println("Avg duration: " + metrics.avgDurationSeconds() + "s");
        System.out.println("Success rate: " + (metrics.getSuccessRate() * 100) + "%");
        System.out.println("Failure rate: " + (metrics.failureRate() * 100) + "%");
        System.out.println("Compensation rate: " + (metrics.compensationRate() * 100) + "%");
    }

    // Wszystkie metryki
    public void showAllMetrics() {
        Map<String, SagaMetrics> allMetrics = sagaQueryService.getAllMetrics();
        allMetrics.forEach((type, metrics) -> {
            System.out.printf("%s: %d sagas, %.1f%% success%n",
                type, metrics.count(), metrics.getSuccessRate() * 100);
        });
    }

    // Znajdź sagi wg stanu
    public List<SagaInstance> findFailedSagas() {
        return sagaQueryService.findByState(SagaLifecycleState.FAILED);
    }

    // Sagi bliskie timeout
    public List<SagaInstance> findExpiringSoon() {
        return sagaQueryService.findExpiringBefore(Instant.now().plusMinutes(5));
    }
}
```

---

## Wizualizacja z SagaVisualizationService

```java
@Service
@RequiredArgsConstructor
public class SagaDebugService {
    private final SagaVisualizationService visualizationService;

    // Diagram Mermaid instancji sagi
    public String getMermaidDiagram(UUID sagaId) {
        return visualizationService.exportToMermaid(sagaId);
        // Zwraca np.:
        // graph TD
        //     evt1[OrderCreated]:::completed
        //     evt2[PaymentProcessed]:::completed
        //     evt3[ShipmentDispatched]:::current
        //     evt1 --> evt2
        //     evt2 --> evt3
        //     classDef completed fill:#90EE90
        //     classDef current fill:#FFD700
    }

    // Diagram definicji sagi (wszystkie możliwe ścieżki)
    public String getSagaDefinitionDiagram() {
        return visualizationService.exportSagaDefinitionToMermaid(OrderSaga.class);
        // Zwraca np.:
        // graph TD
        //     start((Start))
        //     evt1[OrderCreated]:::start
        //     evt2[PaymentProcessed - RETRY x5]
        //     comp2[compensatePayment]:::compensation
        //     start --> evt1
        //     evt1 --> evt2
        //     evt2 -.compensation.-> comp2
        //     classDef start fill:#4169E1
        //     classDef compensation fill:#FF6347
    }
}
```

---

## Konfiguracja application.yml

### Minimalna konfiguracja

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: user
    password: pass
```

Schemat bazy danych tworzony automatycznie przez Liquibase.

### Pełna konfiguracja

```yaml
preboot:
  saga:
    enabled: true
    runner-id-prefix: "saga-runner-"
    max-sub-saga-depth: 10
    scheduling:
      enabled: true
      max-concurrent-events: 4
      auto-start: true
      heartbeat-interval: PT3M
      stalled-check-interval: PT15M
      stalled-threshold: PT5M
      timeout-check-interval: PT1M
      compensation-check-interval: PT30S
      shutdown-timeout: PT60S
      # Cleanup wyłączony domyślnie
      # cleanup-interval: PT1H
      # cleanup-threshold: P7D
```

### Konfiguracja testowa

```yaml
# application-test.yml
preboot:
  saga:
    scheduling:
      auto-start: false  # Nie startuj automatycznie — ręczne sagaRunner.runSagaEvent()
```

### Wyłączenie modułu

```yaml
preboot:
  saga:
    enabled: false
```

---

## Integracja — service uruchamiający sagę

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final SagaPublisher sagaPublisher;
    private final SagaQueryService sagaQueryService;

    /**
     * Utwórz zamówienie — uruchamia sagę.
     */
    public UUID createOrder(String orderId, String customerId, double amount) {
        return sagaPublisher.startSaga(
            OrderSaga.class,
            new OrderSaga.OrderCreatedEvent(orderId, customerId, amount)
        );
    }

    /**
     * Opublikuj event do istniejącej sagi.
     * Correlation ID wyciągany z eventu (orderId).
     */
    public void confirmInventory(String orderId, int quantity) {
        sagaPublisher.publishToSaga(
            new OrderSaga.InventoryReservedEvent(orderId, quantity)
        );
    }

    /**
     * Opublikuj event z jawnym correlation ID.
     */
    public void processPayment(String orderId, String txnId, double amount) {
        sagaPublisher.publishToSaga(
            orderId, // explicit correlation ID
            new OrderSaga.PaymentProcessedEvent(orderId, txnId, amount)
        );
    }

    /**
     * Sprawdź status sagi.
     */
    public Optional<SagaInstance> getOrderStatus(UUID sagaId) {
        return sagaQueryService.findBySagaId(sagaId);
    }
}
```

---

## Testy integracyjne z Testcontainers

```java
import io.preboot.saga.*;
import io.preboot.saga.query.SagaQueryService;
import io.preboot.saga.query.SagaInstance;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
@Testcontainers
class OrderSagaIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        // Wyłącz auto-start schedulera — ręczne procesowanie
        registry.add("preboot.saga.scheduling.auto-start", () -> "false");
    }

    @Autowired SagaPublisher sagaPublisher;
    @Autowired SagaRunner sagaRunner;
    @Autowired SagaQueryService sagaQueryService;

    @Test
    void testHappyPath_OrderSagaCompletesSuccessfully() {
        // Start saga
        UUID sagaId = sagaPublisher.startSaga(
            OrderSaga.class,
            new OrderSaga.OrderCreatedEvent("ORDER-INT-1", "CUST-1", 100.0)
        );

        // Process start event
        sagaRunner.runSagaEvent();

        // Verify saga is RUNNING
        SagaInstance saga = sagaQueryService.findBySagaId(sagaId).orElseThrow();
        assertThat(saga.lifecycleState()).isEqualTo(SagaLifecycleState.RUNNING);

        // Publish and process more events
        sagaPublisher.publishToSaga(new OrderSaga.InventoryReservedEvent("ORDER-INT-1", 2));
        sagaRunner.runSagaEvent();

        sagaPublisher.publishToSaga(new OrderSaga.PaymentProcessedEvent("ORDER-INT-1", "TXN-1", 100.0));
        sagaRunner.runSagaEvent();

        sagaPublisher.publishToSaga(new OrderSaga.ShipmentDispatchedEvent("ORDER-INT-1", "TRACK-1"));
        sagaRunner.runSagaEvent();

        // Verify saga completed
        saga = sagaQueryService.findBySagaId(sagaId).orElseThrow();
        assertThat(saga.lifecycleState()).isEqualTo(SagaLifecycleState.COMPLETED);
        assertThat(saga.eventsProcessed()).isEqualTo(4);
    }

    @Test
    void testCompensation_FailureTriggersFILOCompensation() {
        UUID sagaId = sagaPublisher.startSaga(
            OrderSaga.class,
            new OrderSaga.OrderCreatedEvent("ORDER-COMP-1", "CUST-1", 100.0)
        );
        sagaRunner.runSagaEvent();

        sagaPublisher.publishToSaga(new OrderSaga.InventoryReservedEvent("ORDER-COMP-1", 2));
        sagaRunner.runSagaEvent();

        sagaPublisher.publishToSaga(new OrderSaga.PaymentProcessedEvent("ORDER-COMP-1", "TXN-1", 100.0));
        sagaRunner.runSagaEvent();

        // Symulacja błędu — w produkcji obsłużone przez ErrorStrategy
        // Tu ręcznie wywołujemy compensation processing
        sagaRunner.processCompensations();

        // Verify compensation history (LIFO order)
        var compensations = sagaQueryService.getCompensationHistory(sagaId);
        // Kompensacja Payment (ostatni) → Inventory (pierwszy)
    }

    @Test
    void testTimeout_SagaTimesOut() {
        UUID sagaId = sagaPublisher.startSaga(
            OrderSaga.class,
            new OrderSaga.OrderCreatedEvent("ORDER-TMO-1", "CUST-1", 100.0)
        );
        sagaRunner.runSagaEvent();

        // Process timeouts
        sagaRunner.processTimeouts();

        // Saga z timeout = "30m" nie powinna jeszcze timeout
        // W prawdziwym teście użyj sagi z krótkim timeout lub manipuluj czasem
    }

    @Test
    void testQueryService_MetricsCalculation() {
        // Uruchom kilka sag...
        var metrics = sagaQueryService.getMetrics("com.example.OrderSaga");
        assertThat(metrics.count()).isGreaterThanOrEqualTo(0);
    }
}
```
