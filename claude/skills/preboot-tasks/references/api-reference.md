# API Reference — preboot-tasks

Pakiety: `io.preboot.tasks`, `io.preboot.tasks.scheduling`

## Spis treści

- [TaskPublisher (interfejs)](#taskpublisher)
- [TaskRunner (interfejs)](#taskrunner)
- [TaskContext\<T\> (interfejs)](#taskcontext)
- [TaskQueryService (interfejs)](#taskqueryservice)
- [TaskStatus (DTO)](#taskstatus)
- [TaskState (enum)](#taskstate)
- [TaskConfigFactory (klasa)](#taskconfigfactory)
- [TaskConfigAutoConfiguration (klasa)](#taskconfigautoconfiguration)
- [BackOffPolicy (interfejs)](#backoffpolicy)
- [ConstantBackOffPolicy (klasa)](#constantbackoffpolicy)
- [ExpandingTimeOfBackOffPolicy (klasa)](#expandingtimeofbackoffpolicy)
- [DeadQueuePolicy (interfejs)](#deadqueuepolicy)
- [TimeBasedDeadQueuePolicy (klasa)](#timebaseddeadqueuepolicy)
- [TaskRepository (interfejs)](#taskrepository)
- [TaskHashExistsException (wyjątek)](#taskhashexistsexception)
- [TaskSchedulingService (klasa)](#taskschedulingservice)
- [TaskSchedulerRegistry (record)](#taskschedulerregistry)
- [TaskSchedulingConfiguration (record)](#taskschedulingconfiguration)
- [TaskSchedulingProperties (record)](#taskschedulingproperties)
- [ScalingState (enum)](#scalingstate)
- [TaskSchedulingAutoConfiguration (klasa)](#taskschedulingautoconfiguration)
- [@ExcludeFromTaskScheduling (adnotacja)](#excludefromtaskscheduling)

---

## TaskPublisher

**Interfejs** — publishuje taski do bazy danych. Zwraca UUID stworzonego taska.

```java
public interface TaskPublisher {
    <T> UUID publishTask(T task);
    <T> UUID publishTask(T task, String hash);
    <T> UUID publishTask(T task, Map<String, Object> metadata);
    <T> UUID publishTask(T task, String hash, Map<String, Object> metadata);
}
```

### Metody

#### `publishTask(T task)`
Publishuje task bez deduplication i metadata.

#### `publishTask(T task, String hash)`
Publishuje task z hashem deduplication. Rzuca `TaskHashExistsException` jeśli aktywny task z tym hashem i typem istnieje.

#### `publishTask(T task, Map<String, Object> metadata)`
Publishuje task z metadata (JSON). Klucz `"priority"` ma specjalne znaczenie — wyciągany i ustawiany jako priorytet taska (int, default 0).

#### `publishTask(T task, String hash, Map<String, Object> metadata)`
Publishuje z hashem i metadata.

**Wspólne:**
- `task` — payload serializowalny do JSON
- Zwraca `UUID` taska
- `hash` — opcjonalny hash deduplication (unikalny per typ + hash, tylko aktywne taski)
- `metadata` — opcjonalne JSON metadata (klucz `"priority"` → priorytet taska)

---

## TaskRunner

**Interfejs** — pobiera i wykonuje taski z bazy.

```java
public interface TaskRunner {
    String getRunnerId();
    String runTask();
    void updateHeartbeat();
    void retrieveStalledTasks(Instant heartbeatThreshold);
    void cleanCompletedTasks(Instant completedThreshold);
    boolean hasPendingTasks();
}
```

### Metody

#### `getRunnerId()`
Zwraca unikalny UUID runnera (generowany przy tworzeniu).

#### `runTask()`
Pobiera najstarszy pending task (z uwzględnieniem priorytetu) i wykonuje go. Zwraca `String` — typ taska lub `null` jeśli brak pending tasków.

Logika:
1. `findTaskToRun()` z `FOR UPDATE SKIP LOCKED`
2. Deserializuje payload
3. Próbuje direct handler (`eventPublisher.publish(payload)`)
4. Fallback do TaskContext handler (`eventPublisher.publish(new TaskContextImpl(task, payload))`)
5. Sukces → `markAsCompleted()`, Porażka → `handleTaskFailure()` (retry/dead)

#### `updateHeartbeat()`
Aktualizuje heartbeat dla tasków uruchomionych przez tego runnera.

#### `retrieveStalledTasks(Instant heartbeatThreshold)`
Resetuje taski ze starym heartbeatem (stalled) — udostępnia je do ponownego uruchomienia.

#### `cleanCompletedTasks(Instant completedThreshold)`
Usuwa completed taski starsze niż próg.

#### `hasPendingTasks()`
Sprawdza czy istnieją pending taski gotowe do uruchomienia.

**UWAGA:** TaskRunner wymaga **synchronicznego** `EventPublisher`. Konstrukcja z `AsynchronousEventPublisher` rzuci `IllegalArgumentException`.

---

## TaskContext\<T\>

**Interfejs** — kontekst taska dostarczany do handlerów. Rozszerza `GenericEvent<T>` (umożliwia `typeParameter` filtering).

```java
public interface TaskContext<T> extends GenericEvent<T> {
    T getPayload();
    UUID getTaskId();
    String getTaskType();
    Map<String, Object> getCurrentMetadata();
    Map<String, Object> getPendingMetadataUpdates();
    void setMetadata(String key, Object value);
    void updateMetadata(Map<String, Object> updates);
    Instant getCreatedAt();
    Instant getStartedAt();
    int getFailCount();
}
```

### Kluczowe metody

#### `getPayload()`
Zwraca deserializowany payload taska.

#### `getTaskId()`
Zwraca UUID taska.

#### `setMetadata(String key, Object value)`
Ustawia metadata (pending — zapisywane po sukcesie). Klucz nie może być null.

#### `updateMetadata(Map<String, Object> updates)`
Batch update metadata.

#### `getCurrentMetadata()`
Aktualne metadata z bazy (unmodifiable). Nie zawiera pending updates.

#### `getFailCount()`
Ile razy task failed.

**Użycie w handlerze:**

```java
@EventHandler(typeParameter = MyTask.class)
public void handle(TaskContext<MyTask> ctx) {
    MyTask payload = ctx.getPayload();
    ctx.setMetadata("result", "ok");
}
```

---

## TaskQueryService

**Interfejs** — odpytywanie tasków. Zwraca `TaskStatus` DTO.

```java
public interface TaskQueryService {
    Optional<TaskStatus> getTaskStatus(UUID taskUuid);
    Optional<TaskStatus> findTaskByMetadata(String metadataKey, String metadataValue);
    List<TaskStatus> findTasksByMetadata(Map<String, Object> metadataFilter);
    List<TaskStatus> findTasksByType(String taskType);
    List<TaskStatus> findTasksByState(TaskState status);
    List<TaskStatus> findTasksByTypeAndMetadata(String taskType, Map<String, Object> metadataFilter);
    List<TaskStatus> findTasksByStateAndMetadata(TaskState status, Map<String, Object> metadataFilter);
    List<TaskStatus> findTasksByStateAndTypeAndMetadata(
        TaskState status, String taskType, Map<String, Object> metadataFilter);
    int cleanupCompletedTasks(Instant completedBeforeThreshold);
}
```

Metadata queries korzystają z PostgreSQL `JSONB @>` operator. Wszystkie filtry muszą pasować (AND). Metody rzucają `IllegalArgumentException` dla null/empty argumentów.

---

## TaskStatus

**DTO** — stan taska do zewnętrznego API.

```java
@Data
public class TaskStatus {
    private UUID uuid;
    private String type;
    private TaskState state;
    private Map<String, Object> metadata;
    private Instant createdAt;
    private Instant startedAt;
    private Instant completedAt;
    private int failCount;
    private String errorMessage;

    public boolean isCompleted();
    public boolean isRunning();
    public boolean isPending();
    public boolean isDead();
    public boolean hasErrors();
    public boolean isTerminal();
    public Duration getExecutionDuration();
}
```

`getExecutionDuration()` — zwraca `Duration` między `startedAt` a `completedAt` (lub `null`).

---

## TaskState

**Enum** — stany taska.

```java
public enum TaskState {
    PENDING, RUNNING, COMPLETED, FAILED, DEAD;

    public boolean isTerminal();  // COMPLETED lub DEAD
    public boolean isActive();    // PENDING lub RUNNING
    public boolean isFailure();   // FAILED lub DEAD
}
```

---

## TaskConfigFactory

**Klasa** — fabryka komponentów. Auto-konfigurowana jako bean.

```java
public class TaskConfigFactory {
    public TaskRepository createTaskRepository(String taskTableName);
    public TaskPublisher createTaskPublisher(TaskRepository taskRepository);
    public TaskRunner createTaskRunner(
        EventPublisher eventPublisher, TaskRepository taskRepository,
        DeadQueuePolicy deadQueuePolicy, BackOffPolicy backOffPolicy);
    public TaskQueryService createTaskQueryService(TaskRepository taskRepository);
}
```

`createTaskRepository()` automatycznie tworzy tabelę, widok i indeksy.

---

## TaskConfigAutoConfiguration

**Klasa** — Spring Boot auto-configuration. Tworzy `TaskConfigFactory` beana.

```java
@Configuration
@AutoConfigureAfter(JdbcTemplateAutoConfiguration.class)
@ConditionalOnClass(JdbcTemplate.class)
public class TaskConfigAutoConfiguration {
    @Bean
    public TaskConfigFactory taskConfigFactory(JdbcTemplate jdbcTemplate, JsonMapper jsonMapper);
}
```

Wymaga `JdbcTemplate` w kontekście.

---

## BackOffPolicy

**Interfejs** — polityka opóźnienia retry.

```java
public interface BackOffPolicy {
    Instant calculateNextRunAt(
        int failCount, String errorMessage, String errorStackTrace,
        String type, Instant createdAt);
}
```

Zwraca `Instant` kiedy task powinien zostać ponowiony.

---

## ConstantBackOffPolicy

**Klasa** — stały czas między retry.

```java
public class ConstantBackOffPolicy implements BackOffPolicy {
    public ConstantBackOffPolicy(TemporalAmount backOffPeriod);
}
```

Zawsze zwraca `Instant.now().plus(backOffPeriod)`.

---

## ExpandingTimeOfBackOffPolicy

**Klasa** — exponential backoff z randomizacją.

```java
public class ExpandingTimeOfBackOffPolicy implements BackOffPolicy {
    public ExpandingTimeOfBackOffPolicy(
        TemporalAmount beginBackoff, int randomnessInSeconds,
        int backoffMultiplier, int maxFallbackInMinutes);
}
```

Formuła: `now + beginBackoff + random(0..randomnessInSeconds)s + min(failCount * multiplier, maxMinutes)min`

---

## DeadQueuePolicy

**Interfejs** — polityka dead queue.

```java
public interface DeadQueuePolicy {
    boolean isDead(
        int failCount, String errorMessage, String errorStackTrace,
        String type, Instant createdAt);
}
```

Zwraca `true` jeśli task powinien trafić do dead queue.

---

## TimeBasedDeadQueuePolicy

**Klasa** — dead po upływie czasu od utworzenia.

```java
public class TimeBasedDeadQueuePolicy implements DeadQueuePolicy {
    public TimeBasedDeadQueuePolicy(TemporalAmount timeToLivePeriod);
}
```

Task jest dead gdy `createdAt + timeToLivePeriod < now`.

---

## TaskRepository

**Interfejs** — operacje bazodanowe na taskach. Implementacja: `TaskRepositoryPostgres`.

```java
public interface TaskRepository {
    UUID save(Task task);
    Optional<Task> findTaskToRun(String runnerId);
    void markAsCompleted(Long taskId);
    void updateTaskMetadata(Long taskId, String metadata);
    void updateHeartbeat(String executorInstanceId);
    void retrieveStalledTasks(Instant heartbeatThreshold);
    boolean hasPendingTasks();
    Optional<Task> findByUuid(UUID uuid);
    Stream<Task> findByMetadata(String key, String value);
    Stream<Task> findByMetadataFilter(Map<String, Object> filter);
    Stream<Task> findByType(String type);
    Stream<Task> findAll();
    int cleanupCompletedTasks(Instant completedBeforeThreshold);
    Stream<Task> findByComputedState(String state);
}
```

**UWAGA:** Metody zwracające `Stream<Task>` wymagają zamknięcia (`try-with-resources`).

`findTaskToRun()` używa `FOR UPDATE SKIP LOCKED` — bezpieczne dla wielu workerów.

---

## TaskHashExistsException

**Wyjątek** — rzucany przez `TaskPublisher` gdy aktywny task z tym samym typem i hashem istnieje.

```java
public class TaskHashExistsException extends RuntimeException {}
```

---

## TaskSchedulingService

**Klasa** (`io.preboot.tasks.scheduling`) — zarządza worker threads dla TaskRunnera z auto-scalingiem (SLEEP/PARTIAL/FULL). Nie jest Spring `@Service` — tworzony per TaskRunner przez auto-configuration.

```java
public class TaskSchedulingService {
    public TaskSchedulingService(String schedulerName, TaskRunner taskRunner,
                                  TaskSchedulingConfiguration config);
    public void startWorkers();
    public void shutdown();
    public TaskSchedulerStatus getStatus();
    public String getSchedulerName();
    public TaskRunner getTaskRunner();
    public TaskSchedulingConfiguration getConfiguration();
}
```

Wewnętrznie zawiera `WorkerScalingManager` (prywatna klasa) zarządzającą skalowaniem:
- Workery z ID >= `activeLimit` parkują na `Condition.await()` (zero CPU)
- `onTaskFound()` eskaluje: SLEEP→PARTIAL→FULL, `signalAll()` budzi zaparkowane workery
- `onIdleCycle()` de-eskaluje po `idleTimeout`: FULL→PARTIAL→SLEEP
- `shouldWorkerBeActive(workerId)` — volatile read bez locka, hot path
- `wakeAllForShutdown()` — budzi wszystkie zaparkowane workery przed shutdown

### TaskSchedulerStatus

```java
public record TaskSchedulerStatus(
    String schedulerName, String runnerId, boolean hasPendingTasks,
    int activeWorkers, int maxConcurrentTasks, boolean isShuttingDown,
    ScalingState scalingState) {}
```

---

## TaskSchedulerRegistry

**Record** (`io.preboot.tasks.scheduling`) — rejestr wszystkich schedulerów. Immutable.

```java
public record TaskSchedulerRegistry(List<TaskSchedulingService> schedulers) {
    public Optional<TaskSchedulingService> getScheduler(String schedulerName);
    public Optional<TaskSchedulingService> getSchedulerByRunnerId(String runnerId);
    public List<TaskSchedulerStatus> getAllStatuses();
    public int getSchedulerCount();
    public int getTotalActiveWorkers();
    public boolean hasAnyPendingTasks();
    public boolean isAnySchedulerShuttingDown();
}
```

---

## TaskSchedulingConfiguration

**Record** (`io.preboot.tasks.scheduling`) — konfiguracja jednego schedulera.

```java
public record TaskSchedulingConfiguration(
    int maxConcurrentTasks, boolean autoStart,
    Duration heartbeatInterval, Duration stalledCheckInterval,
    Duration stalledThreshold, Duration shutdownTimeout,
    Duration cleanupInterval, Duration cleanupThreshold,
    Duration sleepInterval, Duration activeInterval,
    Duration idleTimeout, double wakeUpRatio, int sleepWorkers) {

    public static TaskSchedulingConfiguration defaults();
    public static Builder builder();
}
```

Defaults: 4 workerów, autoStart=true, heartbeat 3m, stalled check 15m, stalled threshold 5m, shutdown 60s, cleanup disabled, sleepInterval 5s, activeInterval 1s, idleTimeout 30s, wakeUpRatio 0.5, sleepWorkers 1.

Builder waliduje:
- `sleepWorkers >= 1` i `<= maxConcurrentTasks`
- `wakeUpRatio > 0.0` i `< 1.0`
- `sleepInterval`, `activeInterval`, `idleTimeout` — nie-null i pozytywne

---

## TaskSchedulingProperties

**Record** (`io.preboot.tasks.scheduling`) — Spring Boot properties (`preboot.tasks.scheduling.*`).

```java
@ConfigurationProperties(prefix = "preboot.tasks.scheduling")
public record TaskSchedulingProperties(
    Boolean enabled, SchedulerDefaults defaults,
    Map<String, SchedulerOverride> schedulers) {

    public TaskSchedulingConfiguration resolveConfiguration(String schedulerBeanName);
}
```

`SchedulerDefaults` i `SchedulerOverride` zawierają te same pola co `TaskSchedulingConfiguration` (13 pól), w tym 5 pól auto-scalingu: `sleepInterval`, `activeInterval`, `idleTimeout`, `wakeUpRatio` (boxed `Double`), `sleepWorkers` (boxed `Integer`).

Per-scheduler override: klucz w `schedulers` map = nazwa beana TaskRunnera. Merge: override != null → użyj override, inaczej → defaults.

---

## ScalingState

**Enum** (`io.preboot.tasks.scheduling`) — stany auto-scalingu workerów.

```java
public enum ScalingState {
    SLEEP,    // minimum workerów, zredukowany interwał pollingu
    PARTIAL,  // częściowo aktywni workerzy, normalny interwał
    FULL      // wszyscy workerzy aktywni, normalny interwał
}
```

Przejścia:
- SLEEP → PARTIAL → FULL (eskalacja po znalezieniu taska)
- FULL → PARTIAL → SLEEP (de-eskalacja po `idleTimeout`)
- Gdy `maxConcurrentTasks=1`: PARTIAL pominięty (SLEEP ↔ FULL)

---

## TaskSchedulingAutoConfiguration

**Klasa** — auto-configuration. Odkrywa `TaskRunner` beany, tworzy `TaskSchedulingService` dla każdego, zarządza lifecycle.

Aktywna gdy: `@ConditionalOnProperty(prefix = "preboot.tasks.scheduling", name = "enabled", havingValue = "true", matchIfMissing = true)`.

Tworzy bean: `TaskSchedulerRegistry`.

---

## @ExcludeFromTaskScheduling

**Adnotacja** (`io.preboot.tasks.scheduling`) — wyklucza `TaskRunner` z automatycznego schedulingu.

```java
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface ExcludeFromTaskScheduling {
    String reason() default "";
}
```

Stosuj na `@Bean` metodzie lub klasie TaskRunnera.
