---
name: preboot-tasks
description: "Skill do używania biblioteki preboot-tasks. Użyj tego skilla zawsze gdy użytkownik chce implementować persistent task queue, background jobs, asynchroniczne zadania z bazą danych, retry z backoff, dead letter queue, task scheduling, kolejkowanie zadań, worker auto-scaling, lub pracuje z przetwarzaniem zadań w tle. Obejmuje: TaskPublisher, TaskRunner, TaskContext, TaskQueryService, TaskConfigFactory, BackOffPolicy, DeadQueuePolicy, TaskSchedulingService, TaskSchedulerRegistry, ExcludeFromTaskScheduling, TaskState, TaskStatus, ScalingState, WorkerScalingManager. Triggeruje się na: task queue, background jobs, persistent tasks, retry, backoff, dead letter queue, task scheduling, kolejka zadań, przetwarzanie w tle, worker threads, heartbeat, stalled tasks, task metadata, task priority, deduplication, idempotentność, task status, job queue, scheduled tasks, TaskPublisher, TaskRunner, publishTask, auto-scaling, worker scaling, sleep workers, idle timeout, scaling state."
---

# preboot-tasks

Moduł persistent task queue dla frameworka PreBoot.io — bazodanowa kolejka zadań z PostgreSQL, retry, dead letter queue, priorytetami, automatycznym schedulingiem na virtual threads i auto-scalingiem workerów (sleep/partial/full).

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-tasks</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Wymaga: `preboot-core`, `preboot-eventbus` (transitive), `spring-boot-starter-data-jdbc`, `spring-boot-starter-json`, `postgresql`.

## Szybki start

### 1. Skonfiguruj beany

```java
@Configuration
public class TasksConfig {

    @Bean
    TaskRepository taskRepository(TaskConfigFactory factory) {
        return factory.createTaskRepository("my_tasks"); // nazwa tabeli PostgreSQL
    }

    @Bean
    TaskPublisher taskPublisher(TaskConfigFactory factory, TaskRepository repo) {
        return factory.createTaskPublisher(repo);
    }

    @Bean
    TaskRunner taskRunner(
            TaskConfigFactory factory,
            EventPublisher eventPublisher, // MUSI być synchroniczny!
            TaskRepository repo) {
        return factory.createTaskRunner(
            eventPublisher, repo,
            new TimeBasedDeadQueuePolicy(Duration.ofDays(1)),
            new ConstantBackOffPolicy(Duration.ofMinutes(5))
        );
    }

    @Bean
    TaskQueryService taskQueryService(TaskConfigFactory factory, TaskRepository repo) {
        return factory.createTaskQueryService(repo);
    }
}
```

`TaskConfigFactory` jest auto-konfigurowany — wystarczy mieć `JdbcTemplate` i `JsonMapper` w kontekście. Tabela i indeksy tworzą się automatycznie.

### 2. Stwórz payload taska

```java
public record SendEmailTask(String to, String subject, String body) {}
```

### 3. Stwórz handler

Dwa sposoby — prosty (backward-compatible) lub z `TaskContext`:

```java
// Sposób 1: Prosty handler — otrzymuje sam payload
@Service
public class EmailHandler {
    @EventHandler
    public void handle(SendEmailTask task) {
        emailService.send(task.to(), task.subject(), task.body());
    }
}

// Sposób 2: TaskContext handler — dostęp do metadata, taskId, failCount
@Service
public class EmailContextHandler {
    @EventHandler(typeParameter = SendEmailTask.class)
    public void handle(TaskContext<SendEmailTask> ctx) {
        SendEmailTask task = ctx.getPayload();
        emailService.send(task.to(), task.subject(), task.body());

        // Zapisz wynik w metadata
        ctx.setMetadata("sentAt", Instant.now().toString());
        ctx.setMetadata("status", "delivered");
    }
}
```

### 4. Publishuj task

```java
@Service
public class NotificationService {
    private final TaskPublisher taskPublisher;

    public void sendWelcomeEmail(String email) {
        UUID taskId = taskPublisher.publishTask(
            new SendEmailTask(email, "Welcome!", "Hello...")
        );
        // taskId — UUID do śledzenia statusu
    }
}
```

### 5. Scheduling działa automatycznie

Po zdefiniowaniu `TaskRunner` jako beana, auto-configuration tworzy `TaskSchedulingService` z virtual threads. Nie musisz pisać `@Scheduled` — workerzy odpytują bazę automatycznie.

Konfiguracja w `application.yml`:

```yaml
preboot:
  tasks:
    scheduling:
      enabled: true
      defaults:
        max-concurrent-tasks: 4
        auto-start: true
```

## Główne koncepty

### Architektura

```
TaskPublisher → PostgreSQL → TaskRunner → EventPublisher(sync) → @EventHandler
                   ↑                              ↓
                   └── retry/dead ←── fail ←──────┘
```

1. `TaskPublisher.publishTask()` → serializuje payload do JSON → zapisuje w PostgreSQL
2. `TaskRunner.runTask()` → pobiera najstarszy pending task (z `FOR UPDATE SKIP LOCKED`)
3. Deserializuje payload → publishuje przez `EventPublisher` (synchroniczny!) → handler obsługuje
4. Sukces → `markAsCompleted()` | Porażka → `BackOffPolicy` → retry lub `DeadQueuePolicy` → dead

### Kluczowe klasy

| Klasa | Rola |
|-------|------|
| `TaskPublisher` | Publishuje taski do bazy — zwraca UUID |
| `TaskRunner` | Pobiera i wykonuje taski, zarządza retry/dead |
| `TaskContext<T>` | Wrapper z metadanymi — używany w handlerach TaskContext |
| `TaskQueryService` | Odpytywanie tasków po UUID, state, type, metadata |
| `TaskStatus` | DTO ze stanem taska (PENDING/RUNNING/COMPLETED/FAILED/DEAD) |
| `TaskConfigFactory` | Fabryka — tworzy TaskRepository, TaskPublisher, TaskRunner, TaskQueryService |
| `BackOffPolicy` | Oblicza czas następnego retry |
| `DeadQueuePolicy` | Decyduje kiedy task trafia do dead queue |
| `TaskSchedulingService` | Zarządza worker threads (virtual) dla TaskRunnera z auto-scalingiem |
| `TaskSchedulerRegistry` | Rejestr wszystkich schedulerów — monitoring |
| `ScalingState` | Enum: SLEEP, PARTIAL, FULL — stan auto-scalingu workerów |

### Cykl życia taska

```
PENDING → RUNNING → COMPLETED
    ↓         ↓
  FAILED ← ───┘
    ↓
   DEAD (po przekroczeniu polityki)
```

- **PENDING**: czeka na wykonanie (`next_run_at <= now`, `started_at IS NULL`)
- **RUNNING**: w trakcie (`started_at IS NOT NULL`, nie completed, nie dead)
- **COMPLETED**: ukończony pomyślnie (`completed = true`)
- **FAILED**: nieudany, będzie retry (`fail_count > 0`, nie dead, nie completed)
- **DEAD**: permanentnie nieudany, brak retry (`dead = true`)

### Priorytety tasków

Wyższy priorytet = wcześniejsze wykonanie. Priorytet ustawiasz przez metadata:

```java
UUID taskId = taskPublisher.publishTask(payload, Map.of(
    "priority", 10,    // wyższy = wcześniejszy
    "userId", "user1"
));
```

Sortowanie: `ORDER BY priority DESC, next_run_at`.

### Deduplication

Hash zapobiega duplikatom aktywnych tasków tego samego typu:

```java
String hash = HashUtils.getHash(Map.of("orderId", order.getId()));
try {
    taskPublisher.publishTask(payload, hash);
} catch (TaskHashExistsException e) {
    // aktywny task z tym hashem już istnieje
}
```

Unikalność jest per typ taska + hash, tylko dla aktywnych tasków (nie completed/dead).

### BackOff Policies

```java
// Stały czas między retry
new ConstantBackOffPolicy(Duration.ofMinutes(5));

// Exponential backoff z randomizacją
new ExpandingTimeOfBackOffPolicy(
    Duration.ofMinutes(1),  // początkowy backoff
    30,                     // random sekund
    2,                      // mnożnik
    60                      // max backoff (minuty)
);
```

### Dead Queue Policies

```java
// Task dead po 24h od utworzenia
new TimeBasedDeadQueuePolicy(Duration.ofDays(1));
```

Możesz implementować własne `DeadQueuePolicy` (np. po ilości prób).

### Auto-scheduling

Auto-configuration tworzy `TaskSchedulingService` dla każdego `TaskRunner` beana:
- Virtual threads (Java 21+)
- Automatyczny heartbeat, stalled task recovery, cleanup
- Konfiguracja per-scheduler w YAML
- Auto-scaling workerów (SLEEP → PARTIAL → FULL)

Wyłączenie konkretnego runnera:

```java
@Bean
@ExcludeFromTaskScheduling(reason = "Custom scheduler")
TaskRunner myRunner(...) { ... }
```

### Auto-scaling workerów

Workerzy automatycznie skalują się w 3 stanach:

| Stan | Aktywni workerzy | Interwał pollingu |
|------|-----------------|-------------------|
| **SLEEP** | `sleepWorkers` (default: 1) | `sleepInterval` (default: 5s) |
| **PARTIAL** | `floor(max * wakeUpRatio)` | `activeInterval` (default: 1s) |
| **FULL** | `maxConcurrentTasks` | `activeInterval` (default: 1s) |

Przejścia:
- **W górę**: gdy worker znajdzie task → SLEEP→PARTIAL→FULL
- **W dół**: gdy idle dłużej niż `idleTimeout` → FULL→PARTIAL→SLEEP
- **maxConcurrentTasks=1**: PARTIAL pominięty, SLEEP↔FULL

Nieaktywni workerzy parkują na `Condition.await()` — zero CPU.

Konfiguracja YAML:

```yaml
preboot:
  tasks:
    scheduling:
      defaults:
        sleep-interval: 5s        # interwał w SLEEP
        active-interval: 1s       # interwał w PARTIAL/FULL
        idle-timeout: 30s         # czas do de-eskalacji
        wake-up-ratio: 0.5        # frakcja workerów w PARTIAL
        sleep-workers: 1          # workerzy aktywni w SLEEP
```

Przywrócenie starego zachowania (100ms polling, brak scalingu):

```yaml
preboot:
  tasks:
    scheduling:
      defaults:
        active-interval: 100ms
        sleep-workers: 4          # = max-concurrent-tasks → wszystko aktywne
```

### Zależności od innych modułów PreBoot

- **preboot-core** (wymagane) — `JsonMapper`, `HashUtils`
- **preboot-eventbus** (wymagane) — `EventPublisher`, `@EventHandler`, `GenericEvent`

## Typowe przepływy

### Publish + query statusu

```java
UUID taskId = taskPublisher.publishTask(new ProcessOrderTask(orderId));

// Później...
Optional<TaskStatus> status = taskQueryService.getTaskStatus(taskId);
if (status.isPresent() && status.get().isCompleted()) {
    Map<String, Object> metadata = status.get().getMetadata();
    // odczytaj wyniki z metadata
}
```

### Publish z metadata i priorytetem

```java
Map<String, Object> meta = Map.of(
    "priority", 10,
    "userId", "user123",
    "department", "sales"
);
UUID taskId = taskPublisher.publishTask(new CriticalTask(data), meta);
```

### Handler z TaskContext — zapis wyniku

```java
@EventHandler(typeParameter = ProcessOrderTask.class)
public void handle(TaskContext<ProcessOrderTask> ctx) {
    ProcessOrderTask task = ctx.getPayload();
    OrderResult result = orderService.process(task);

    ctx.setMetadata("result", result.status());
    ctx.setMetadata("processedAt", Instant.now().toString());
    // metadata zostanie zapisana do bazy po sukcesie
}
```

### Filtrowanie tasków po metadata

```java
// Wszystkie taski danego użytkownika
List<TaskStatus> userTasks = taskQueryService.findTasksByMetadata(
    Map.of("userId", "user123")
);

// Failed taski wysokiego priorytetu
List<TaskStatus> critical = taskQueryService.findTasksByStateAndMetadata(
    TaskState.FAILED, Map.of("priority", "10")
);
```

### Cleanup starych tasków

```java
int deleted = taskQueryService.cleanupCompletedTasks(
    Instant.now().minus(Duration.ofDays(30))
);
```

## Konfiguracja schedulerów (YAML)

```yaml
preboot:
  tasks:
    scheduling:
      enabled: true
      defaults:
        max-concurrent-tasks: 4
        auto-start: true
        heartbeat-interval: 3m
        stalled-check-interval: 15m
        stalled-threshold: 5m
        shutdown-timeout: 60s
        sleep-interval: 5s          # interwał pollingu w SLEEP
        active-interval: 1s         # interwał pollingu w PARTIAL/FULL
        idle-timeout: 30s           # czas bez tasków do de-eskalacji
        wake-up-ratio: 0.5          # frakcja workerów w PARTIAL
        sleep-workers: 1            # workerzy aktywni w SLEEP
      schedulers:
        emailTaskRunner:
          max-concurrent-tasks: 8
          sleep-workers: 2
          cleanup-interval: 1h
          cleanup-threshold: 24h
        lowPriorityRunner:
          max-concurrent-tasks: 2
```

## Pułapki i częste błędy

1. **Async EventPublisher z TaskRunner** — `TaskRunnerImpl` rzuci `IllegalArgumentException` przy starcie. TaskRunner **wymaga** synchronicznego `EventPublisher`. Asynchroniczność jest realizowana przez worker threads, nie async publishing.

2. **Brak JdbcTemplate / DataSource** — moduł wymaga PostgreSQL. Bez skonfigurowanego `spring.datasource` aplikacja nie wystartuje.

3. **Payload nie-serializowalny do JSON** — payload musi być serializowalny przez Jackson. Użyj `@JsonCreator`/`@JsonProperty` lub records.

4. **Zapomniany bean TaskRunner** — bez `TaskRunner` beana auto-scheduling nie wystartuje (ale `TaskPublisher` będzie działać).

5. **Handler z błędnym `typeParameter`** — `@EventHandler(typeParameter = MyTask.class)` musi wskazywać na typ payloadu, nie na `TaskContext`.

6. **Metadata query z typem numerycznym** — priorytet w metadata jest serializowany do JSON. Filtruj jako string: `Map.of("priority", "10")`.

7. **Stream z TaskRepository nie zamknięty** — `findByMetadata()` itp. zwracają `Stream<Task>` — zamykaj je w `try-with-resources`.

8. **Nadpisanie nazwy beana** — auto-scheduling rozpoznaje TaskRunnery po nazwie beana. Override sync: `"eventPublisher"`, async: `"asyncEventPublisher"`.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury metod, parametry, wyjątki wszystkich publicznych klas
- **examples.md** — kompletne przykłady: konfiguracja, handlery, TaskContext, scheduling, testowanie, monitoring SQL
