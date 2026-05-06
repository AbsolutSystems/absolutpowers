# API Reference — preboot-saga

Pakiety: `io.preboot.saga`, `io.preboot.saga.config`, `io.preboot.saga.scheduling`, `io.preboot.saga.query`, `io.preboot.saga.visualization`, `io.preboot.saga.model`, `io.preboot.saga.test`

## Spis treści

- [Adnotacje](#adnotacje)
  - [@Saga](#saga)
  - [@SagaStart](#sagastart)
  - [@SagaEventHandler](#sagaeventhandler)
  - [@CompensationHandler](#compensationhandler)
  - [@SagaTimeout](#sagatimeout)
- [ErrorStrategy (enum)](#errorstrategy)
- [SagaLifecycleState (enum)](#sagalifecyclestate)
- [SagaContext (interfejs)](#sagacontext)
- [SagaPublisher (interfejs)](#sagapublisher)
- [SagaRunner (interfejs)](#sagarunner)
- [SagaQueryService (interfejs)](#sagaqueryservice)
- [SagaVisualizationService (interfejs)](#sagavisualizationservice)
- [SagaInstance (record)](#sagainstance)
- [SagaMetrics (record)](#sagametrics)
- [Repozytoria](#repozytoria)
  - [SagaRepository](#sagarepository)
  - [SagaEventRepository](#sagaeventrepository)
  - [SagaCompensationRepository](#sagacompensationrepository)
  - [SagaEventQueueRepository](#sagaeventqueuerepository)
- [Model classes](#model-classes)
- [SagaTestFixture (klasa)](#sagatestfixture)
- [Konfiguracja](#konfiguracja)
  - [SagaProperties](#sagaproperties)
  - [SagaSchedulingProperties](#sagaschedulingproperties)
  - [SagaAutoConfiguration](#sagaautoconfiguration)
  - [SagaSchedulingAutoConfiguration](#sagaschedulingautoconfiguration)

---

## Adnotacje

### @Saga

**Adnotacja na klasie** — definiuje klasę jako sagę.

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Saga {
    String correlationProperty();
    String timeout() default "";
    ErrorStrategy errorStrategy() default ErrorStrategy.COMPENSATE;
    int maxRetries() default 3;
    int version() default 1;
}
```

| Parametr | Default | Opis |
|----------|---------|------|
| `correlationProperty` | (wymagane) | Nazwa property w eventach do korelacji (np. `"orderId"`). Wspiera: getter, field, record component, nested dot notation |
| `timeout` | `""` (brak) | Timeout sagi. Format: `"30m"`, `"1h"`, `"P1D"` (ISO-8601 duration). Pusty = brak timeout |
| `errorStrategy` | `COMPENSATE` | Domyślna strategia obsługi błędów dla handlerów (nadpisywalna per handler) |
| `maxRetries` | `3` | Domyślna liczba retry dla strategii RETRY |
| `version` | `1` | Wersja sagi (do wersjonowania definicji) |

---

### @SagaStart

**Adnotacja na metodzie** — marker oznaczający handler startowy. MUSI być w parze z `@SagaEventHandler`. Dokładnie jeden per saga.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface SagaStart {}
```

---

### @SagaEventHandler

**Adnotacja na metodzie** — handler eventu. Sygnatura: `(SagaContext<T> ctx, EventType event)`.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface SagaEventHandler {
    ErrorStrategy errorStrategy() default ErrorStrategy.INHERIT;
    int maxRetries() default -1;
}
```

| Parametr | Default | Opis |
|----------|---------|------|
| `errorStrategy` | `INHERIT` | Strategia błędów dla tego handlera. INHERIT = użyj z `@Saga` |
| `maxRetries` | `-1` | Liczba retry. -1 = użyj wartości z `@Saga` |

---

### @CompensationHandler

**Adnotacja na metodzie** — handler kompensacji. Sygnatura: `(SagaContext<T> ctx)` — bez parametru eventu.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface CompensationHandler {
    Class<?> value();
}
```

| Parametr | Opis |
|----------|------|
| `value` | Klasa eventu, dla którego ta kompensacja jest przeznaczona |

Kompensacje wykonywane w kolejności LIFO (odwrotnej do przetworzonych eventów).

---

### @SagaTimeout

**Adnotacja na metodzie** — handler timeout. Sygnatura: `(SagaContext<T> ctx)`. Maksymalnie jeden per saga.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface SagaTimeout {}
```

---

## ErrorStrategy

**Enum** — strategia obsługi błędów.

```java
public enum ErrorStrategy {
    INHERIT,
    COMPENSATE,
    RETRY,
    IGNORE,
    FAIL
}
```

| Wartość | Zachowanie |
|---------|-----------|
| `INHERIT` | Używa strategii z `@Saga` (domyślna dla handlerów) |
| `COMPENSATE` | Błąd → uruchom handlery kompensacji w kolejności LIFO |
| `RETRY` | Retry z exponential backoff, po wyczerpaniu prób → kompensacja |
| `IGNORE` | Loguj błąd i kontynuuj sagę (niebezpieczne!) |
| `FAIL` | Oznacz sagę jako FAILED natychmiast, bez kompensacji |

---

## SagaLifecycleState

**Enum** — stany cyklu życia sagi.

```java
public enum SagaLifecycleState {
    STARTED,        // Saga utworzona, nie przetworzyła jeszcze eventów
    RUNNING,        // Aktywna, przetwarza eventy
    COMPENSATING,   // Wykonuje handlery kompensacji (LIFO)
    COMPLETED,      // Sukces (terminal)
    FAILED,         // Błąd bez kompensacji (terminal)
    COMPENSATED,    // Kompensacja zakończona (terminal)
    TIMED_OUT;      // Timeout (terminal)
}
```

### Metody

| Metoda | Opis |
|--------|------|
| `isTerminal()` | `true` dla COMPLETED, FAILED, COMPENSATED, TIMED_OUT |
| `isActive()` | `true` dla STARTED, RUNNING |
| `isFailure()` | `true` dla FAILED, COMPENSATED, TIMED_OUT |
| `canTransitionTo(SagaLifecycleState)` | Sprawdza czy przejście jest dozwolone |
| `getDescription()` | Opis stanu (po angielsku) |

### Dozwolone przejścia

```
STARTED → RUNNING
RUNNING → COMPLETED, COMPENSATING, TIMED_OUT, FAILED
COMPENSATING → COMPENSATED, FAILED
COMPLETED, FAILED, COMPENSATED, TIMED_OUT → (brak — terminal)
```

---

## SagaContext

**Interfejs** — API dostępne w handlerach sagi.

```java
public interface SagaContext<T> {
    // Identification
    UUID getSagaId();
    String getCorrelationId();
    String getSagaType();

    // State Management
    T getState();
    void setState(T state);

    // Event Publishing
    void publish(Object event);
    void publishAll(Object... events);

    // Lifecycle Control
    void completeSaga();
    void compensate();
    void compensate(String reason);

    // Queries
    int getEventsProcessed();
    Instant getCreatedAt();
    Instant getLastEventAt();
    SagaLifecycleState getLifecycleState();

    // Sub-Sagas
    UUID startSubSaga(Class<?> sagaClass, Object startEvent);
    void completeSubSaga(UUID subSagaId);
}
```

| Metoda | Opis |
|--------|------|
| `getSagaId()` | UUID instancji sagi |
| `getCorrelationId()` | Correlation ID wyciągnięty ze start eventu |
| `getSagaType()` | Pełna nazwa klasy sagi |
| `getState()` | Aktualny stan sagi (deserializowany z JSON) |
| `setState(T)` | Zapisz stan. ZAWSZE wywołuj po modyfikacji, nawet in-place! |
| `publish(Object)` | Opublikuj event do kolejki (async, FIFO) |
| `publishAll(Object...)` | Opublikuj wiele eventów naraz |
| `completeSaga()` | Zakończ sagę sukcesem → COMPLETED |
| `compensate()` | Uruchom kompensację (LIFO) |
| `compensate(String)` | Kompensacja z opisem przyczyny |
| `getEventsProcessed()` | Liczba przetworzonych eventów |
| `getCreatedAt()` | Timestamp utworzenia sagi |
| `getLastEventAt()` | Timestamp ostatniego eventu (null jeśli brak) |
| `getLifecycleState()` | Aktualny stan lifecycle |
| `startSubSaga(Class, Object)` | Uruchom pod-sagę. Zwraca UUID pod-sagi |
| `completeSubSaga(UUID)` | Oznacz pod-sagę jako zakończoną |

---

## SagaPublisher

**Interfejs** — entry point do startowania sag i publikowania eventów.

```java
public interface SagaPublisher {
    <T> UUID startSaga(Class<?> sagaClass, T event);
    <T> UUID startSaga(Class<?> sagaClass, T event, UUID parentSagaId);
    <T> void publishToSaga(T event);
    <T> void publishToSaga(String correlationId, T event);
}
```

| Metoda | Opis |
|--------|------|
| `startSaga(Class, event)` | Utwórz nową instancję sagi z eventem startowym. Zwraca UUID sagi |
| `startSaga(Class, event, parentSagaId)` | Jak wyżej, ale jako sub-saga |
| `publishToSaga(event)` | Opublikuj event do istniejącej sagi (correlation ID wyciągany z eventu) |
| `publishToSaga(correlationId, event)` | Opublikuj event z jawnym correlation ID |

Wyjątki: `IllegalArgumentException` — brak `@Saga`, nie można wyciągnąć correlationProperty, nie znaleziono sagi.

---

## SagaRunner

**Interfejs** — silnik przetwarzania eventów.

```java
public interface SagaRunner {
    String getRunnerId();
    String runSagaEvent();
    void updateHeartbeat();
    void retrieveStalledSagas(Instant threshold);
    void processTimeouts();
    void processCompensations();
    void cleanCompletedSagas(Instant threshold);
    boolean hasPendingSagaEvents();
}
```

| Metoda | Opis |
|--------|------|
| `getRunnerId()` | Unikalny ID runnera |
| `runSagaEvent()` | Procesuj jeden event z kolejki. Zwraca typ eventu lub null jeśli brak |
| `updateHeartbeat()` | Aktualizuj heartbeat dla wszystkich sag tego runnera |
| `retrieveStalledSagas(Instant)` | Odzyskaj "zawieszone" sagi (stary heartbeat) |
| `processTimeouts()` | Przetwórz sagi po timeout |
| `processCompensations()` | Wykonaj oczekujące kompensacje |
| `cleanCompletedSagas(Instant)` | Wyczyść zakończone sagi starsze niż threshold |
| `hasPendingSagaEvents()` | Czy są oczekujące eventy w kolejce |

---

## SagaQueryService

**Interfejs** — monitoring i metryki sag (read-only).

```java
public interface SagaQueryService {
    Optional<SagaInstance> findBySagaId(UUID sagaId);
    Optional<SagaInstance> findByCorrelationId(String sagaType, String correlationId);
    List<SagaInstance> findByState(SagaLifecycleState state);
    List<SagaInstance> findByState(String sagaType, SagaLifecycleState state);
    List<SagaInstance> findExpiringBefore(Instant instant);
    List<SagaEvent> getEventHistory(UUID sagaId);
    List<SagaCompensation> getCompensationHistory(UUID sagaId);
    SagaMetrics getMetrics(String sagaType);
    Map<String, SagaMetrics> getAllMetrics();
}
```

---

## SagaVisualizationService

**Interfejs** — wizualizacja sag jako diagramy Mermaid.

```java
public interface SagaVisualizationService {
    SagaFlowGraph visualizeSaga(UUID sagaId);
    SagaFlowGraph visualizeSagaDefinition(Class<?> sagaClass);
    String exportToMermaid(UUID sagaId);
    String exportSagaDefinitionToMermaid(Class<?> sagaClass);
}
```

| Metoda | Opis |
|--------|------|
| `visualizeSaga(UUID)` | Graf wykonania konkretnej instancji sagi |
| `visualizeSagaDefinition(Class)` | Graf definicji — wszystkie możliwe ścieżki |
| `exportToMermaid(UUID)` | Diagram Mermaid instancji (kolor: zielony=done, żółty=current, czerwony=failed) |
| `exportSagaDefinitionToMermaid(Class)` | Diagram Mermaid definicji (handlery, kompensacje, error strategies) |

---

## SagaInstance

**Record** — DTO instancji sagi z `SagaQueryService`.

```java
public record SagaInstance(
    UUID uuid,
    String sagaType,
    int version,
    String correlationId,
    String state,                    // JSON
    SagaLifecycleState lifecycleState,
    Instant createdAt,
    Instant updatedAt,
    Instant completedAt,             // null jeśli niezakończona
    Instant timeoutAt,               // null jeśli brak timeout
    int eventsProcessed,
    String lastEventType,
    Instant lastEventAt,
    String metadata,                 // JSON
    String errorMessage,
    int errorCount,
    boolean compensationInProgress,
    Instant compensationStartedAt,
    String executorInstanceId,
    Instant heartbeat,
    UUID parentSagaId                // null jeśli top-level
) {
    boolean isCompleted();
    boolean isRunning();
    boolean isFailed();
    boolean hasTimedOut();
    boolean isSubSaga();
    Long getDurationMillis();        // null jeśli niezakończona
}
```

---

## SagaMetrics

**Record** — metryki agregowane per typ sagi.

```java
public record SagaMetrics(
    String sagaType,
    SagaLifecycleState lifecycleState,
    long count,
    Double avgDurationSeconds,       // null jeśli brak zakończonych
    Double avgEventsPerSaga,         // null jeśli brak sag
    double compensationRate,         // 0.0 - 1.0
    double failureRate               // 0.0 - 1.0
) {
    static SagaMetrics empty(String sagaType, SagaLifecycleState lifecycleState);
    double getSuccessRate();         // 1.0 - failureRate
    boolean hasData();               // count > 0
}
```

---

## Repozytoria

### SagaRepository

```java
public interface SagaRepository {
    UUID save(Saga saga);
    Optional<Saga> findBySagaId(UUID sagaId);
    Optional<Saga> findByCorrelationId(String sagaType, String correlationId);
    List<Saga> findByLifecycleState(SagaLifecycleState lifecycleState);
    List<Saga> findChildSagasByParentId(UUID parentSagaId);
    void updateState(UUID sagaId, String stateJson);
    void updateLifecycleState(UUID sagaId, SagaLifecycleState lifecycleState);
    void incrementEventsProcessed(UUID sagaId, String eventType);
    void updateHeartbeat(UUID sagaId, String executorInstanceId);
    void updateHeartbeat(String executorInstanceId);
    List<Saga> findStalledSagas(Instant threshold);
    List<Saga> findTimedOutSagas(Instant now);
}
```

### SagaEventRepository

```java
public interface SagaEventRepository {
    SagaEvent save(SagaEvent event);
    List<SagaEvent> findBySagaIdOrderBySequenceNumber(UUID sagaId);
    List<SagaEvent> findBySagaIdAndCompensatedFalseOrderBySequenceNumberDesc(UUID sagaId);
    void markAsCompensated(Long eventId, Long compensationId);
}
```

### SagaCompensationRepository

```java
public interface SagaCompensationRepository {
    SagaCompensation save(SagaCompensation compensation);
    List<SagaCompensation> findBySagaIdOrderByExecutedAtDesc(UUID sagaId);
    List<SagaCompensation> findBySagaId(UUID sagaId);  // alias
    int countFailedCompensationsBySagaId(UUID sagaId);
}
```

### SagaEventQueueRepository

```java
public interface SagaEventQueueRepository {
    Long queueEvent(SagaEventQueue event);
    Optional<SagaEventQueue> fetchNextEvent();          // z row-level locking
    void markAsProcessing(Long eventId, String runnerId);
    void markAsCompleted(Long eventId);
    void markAsFailed(Long eventId, String errorMessage, Instant nextRunAt);
    List<SagaEventQueue> findBySagaId(UUID sagaId);
    int countPendingEvents();
    int deleteCompletedEvents(Instant threshold);
}
```

---

## Model classes

### Saga (encja)

Tabela: `sagas`. Pola: `id` (PK), `uuid`, `saga_type`, `version`, `correlation_id`, `state` (JSONB), `lifecycle_state`, `created_at`, `updated_at`, `completed_at`, `timeout_at`, `events_processed`, `last_event_type`, `last_event_at`, `metadata` (JSONB), `error_message`, `error_count`, `compensation_in_progress`, `compensation_started_at`, `executor_instance_id`, `heartbeat`, `parent_saga_id`.

### SagaEvent (encja)

Tabela: `saga_events`. Pola: `id` (PK), `saga_id` (FK), `event_type`, `event_payload` (JSONB), `sequence_number`, `processed_at`, `processing_duration_ms`, `compensation_event_id`, `compensated`, `compensated_at`, `error_message`.

### SagaCompensation (encja)

Tabela: `saga_compensations`. Pola: `id` (PK), `saga_id` (FK), `saga_event_id` (FK), `handler_method`, `compensation_payload` (JSONB), `executed_at`, `execution_duration_ms`, `status` (SUCCESS/FAILED), `error_message`.

### SagaEventQueue (encja)

Tabela: `saga_event_queue`. Pola: `id` (PK), `saga_id` (FK), `event_type`, `event_payload` (JSONB), `correlation_id`, `status` (PENDING/PROCESSING/COMPLETED/FAILED), `priority`, `max_retries`, `created_at`, `next_run_at`, `started_at`, `runner_id`, `fail_count`, `error_message`, `completed_at`, `failed_at`.

---

## SagaTestFixture

**Klasa** — fluent API do testowania sag w izolacji (bez Spring context, bez bazy danych).

```java
public class SagaTestFixture<S, T> {
    // Factory
    static <S, T> SagaTestFixture<S, T> forSaga(Class<S> sagaClass, Class<T> stateClass);

    // GIVEN (setup)
    SagaTestFixture<S, T> givenNoPriorActivity();
    SagaTestFixture<S, T> givenStarted(Object startEvent);
    SagaTestFixture<S, T> givenState(T initialState);
    SagaTestFixture<S, T> givenCorrelationId(String correlationId);
    SagaTestFixture<S, T> withInitialState(T initialState);  // alias givenState

    // WHEN (actions)
    SagaTestFixture<S, T> whenStartingWith(Object startEvent);
    SagaTestFixture<S, T> whenPublishing(Object event);
    SagaTestFixture<S, T> whenTimeoutOccurs();

    // THEN (assertions)
    SagaTestFixture<S, T> thenExpectState(Consumer<T> stateAssertion);
    SagaTestFixture<S, T> thenExpectLifecycleState(SagaLifecycleState expectedState);
    SagaTestFixture<S, T> thenExpectCompleted();
    SagaTestFixture<S, T> thenExpectCompensating();
    SagaTestFixture<S, T> thenExpectCompensated();
    SagaTestFixture<S, T> thenExpectFailed();
    SagaTestFixture<S, T> andThenExpectPublishedEvent(Class<?> eventClass);
    SagaTestFixture<S, T> andThenExpectPublishedEventCount(int expectedCount);
    SagaTestFixture<S, T> andThenExpectNoPublishedEvents();
    SagaTestFixture<S, T> thenExpectException(Class<? extends Exception> exceptionClass);
    SagaTestFixture<S, T> andThenExpectCompensatedEventFor(Class<?> eventClass);

    // Inspection
    T getCurrentState();
    List<Object> getPublishedEvents();
    SagaLifecycleState getLifecycleState();
}
```

---

## Konfiguracja

### SagaProperties

**Prefix:** `preboot.saga`

```java
@ConfigurationProperties(prefix = "preboot.saga")
public class SagaProperties {
    private boolean enabled = true;
    private String runnerIdPrefix = "saga-runner-";
    private int maxSubSagaDepth = 10;
}
```

### SagaSchedulingProperties

**Prefix:** `preboot.saga.scheduling`

```java
@ConfigurationProperties(prefix = "preboot.saga.scheduling")
public class SagaSchedulingProperties {
    private boolean enabled = true;
    private int maxConcurrentEvents = 4;
    private boolean autoStart = true;
    private Duration heartbeatInterval = Duration.ofMinutes(3);
    private Duration stalledCheckInterval = Duration.ofMinutes(15);
    private Duration stalledThreshold = Duration.ofMinutes(5);
    private Duration timeoutCheckInterval = Duration.ofMinutes(1);
    private Duration compensationCheckInterval = Duration.ofSeconds(30);
    private Duration shutdownTimeout = Duration.ofSeconds(60);
    private Duration cleanupInterval;           // null = disabled
    private Duration cleanupThreshold = Duration.ofDays(7);
}
```

### SagaAutoConfiguration

Auto-konfiguruje beany: `SagaConfigFactory`, `SagaRepository`, `SagaEventQueueRepository`, `SagaEventRepository`, `SagaCompensationRepository`, `SagaHandlerRegistry`, `SagaPublisher`, `CompensationCoordinator`, `SagaRunner`, `SagaQueryService`.

Aktywuje się gdy: `JdbcTemplate` jest dostępny + `preboot.saga.enabled=true` (domyślnie).

Wszystkie beany mają `@ConditionalOnMissingBean` — można nadpisać dowolny komponent.

### SagaSchedulingAutoConfiguration

Auto-konfiguruje `SagaSchedulingService` (singleton). Aktywuje się gdy: `SagaRunner` bean + `preboot.saga.scheduling.enabled=true` (domyślnie).

Zarządza: wątkami roboczymi, heartbeat, timeout check, compensation processing, stalled recovery, cleanup.
