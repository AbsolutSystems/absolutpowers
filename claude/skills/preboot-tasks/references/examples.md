# Przykłady — preboot-tasks

## Spis treści

- [Konfiguracja beanów](#konfiguracja-beanów)
- [Prosty handler (payload)](#prosty-handler-payload)
- [TaskContext handler z metadata](#taskcontext-handler-z-metadata)
- [Publish z priorytetem](#publish-z-priorytetem)
- [Deduplication z hash](#deduplication-z-hash)
- [Odpytywanie tasków (TaskQueryService)](#odpytywanie-tasków-taskqueryservice)
- [Cleanup starych tasków](#cleanup-starych-tasków)
- [BackOff i Dead Queue Policies](#backoff-i-dead-queue-policies)
- [Scheduling — konfiguracja YAML](#scheduling--konfiguracja-yaml)
- [@ExcludeFromTaskScheduling](#excludefromtaskscheduling)
- [Wiele kolejek w jednej aplikacji](#wiele-kolejek-w-jednej-aplikacji)
- [Monitoring i diagnostyka SQL](#monitoring-i-diagnostyka-sql)
- [Testowanie — integracyjne z PostgreSQL](#testowanie--integracyjne-z-postgresql)
- [Testowanie — unit test TaskContext](#testowanie--unit-test-taskcontext)
- [Integracja z preboot-eventbus](#integracja-z-preboot-eventbus)

---

## Konfiguracja beanów

### Minimalna konfiguracja

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

`TaskConfigFactory` jest auto-konfigurowany — wystarczy `JdbcTemplate` i `JsonMapper` w kontekście. Tabela, widok i indeksy tworzą się automatycznie.

### Konfiguracja z exponential backoff

```java
@Bean
TaskRunner taskRunner(
        TaskConfigFactory factory,
        EventPublisher eventPublisher,
        TaskRepository repo) {
    return factory.createTaskRunner(
        eventPublisher, repo,
        new TimeBasedDeadQueuePolicy(Duration.ofHours(12)),
        new ExpandingTimeOfBackOffPolicy(
            Duration.ofMinutes(1),  // początkowy backoff
            30,                     // random sekund (0-30)
            2,                      // mnożnik
            60                      // max backoff (minuty)
        )
    );
}
```

---

## Prosty handler (payload)

### Payload jako record

```java
public record SendEmailTask(String to, String subject, String body) {}
```

### Handler — prosty (backward-compatible)

```java
@Service
public class EmailHandler {

    private final EmailService emailService;

    public EmailHandler(EmailService emailService) {
        this.emailService = emailService;
    }

    @EventHandler
    public void handle(SendEmailTask task) {
        emailService.send(task.to(), task.subject(), task.body());
    }
}
```

### Publish

```java
@Service
public class NotificationService {

    private final TaskPublisher taskPublisher;

    public NotificationService(TaskPublisher taskPublisher) {
        this.taskPublisher = taskPublisher;
    }

    public void sendWelcomeEmail(String email) {
        UUID taskId = taskPublisher.publishTask(
            new SendEmailTask(email, "Welcome!", "Hello...")
        );
        // taskId — UUID do śledzenia statusu
    }
}
```

### Payload z @JsonCreator (klasy z konstruktorem)

```java
public class ProcessOrderTask {
    private final String orderId;
    private final BigDecimal amount;

    @JsonCreator
    public ProcessOrderTask(
            @JsonProperty("orderId") String orderId,
            @JsonProperty("amount") BigDecimal amount) {
        this.orderId = orderId;
        this.amount = amount;
    }

    public String getOrderId() { return orderId; }
    public BigDecimal getAmount() { return amount; }
}
```

---

## TaskContext handler z metadata

Handler z dostępem do metadata, taskId i failCount:

```java
@Service
public class OrderProcessingHandler {

    private final OrderService orderService;

    public OrderProcessingHandler(OrderService orderService) {
        this.orderService = orderService;
    }

    @EventHandler(typeParameter = ProcessOrderTask.class)
    public void handle(TaskContext<ProcessOrderTask> ctx) {
        ProcessOrderTask task = ctx.getPayload();

        // Dostęp do kontekstu
        UUID taskId = ctx.getTaskId();
        int failCount = ctx.getFailCount();
        Map<String, Object> currentMeta = ctx.getCurrentMetadata();

        // Przetwarzanie
        OrderResult result = orderService.process(task.getOrderId());

        // Zapis wyniku w metadata (pending — zapisane po sukcesie)
        ctx.setMetadata("result", result.status());
        ctx.setMetadata("processedAt", Instant.now().toString());
        ctx.setMetadata("attempt", failCount + 1);
    }
}
```

### Batch update metadata

```java
@EventHandler(typeParameter = ImportDataTask.class)
public void handle(TaskContext<ImportDataTask> ctx) {
    ImportResult result = importService.run(ctx.getPayload());

    ctx.updateMetadata(Map.of(
        "importedRows", result.rowCount(),
        "errors", result.errorCount(),
        "completedAt", Instant.now().toString()
    ));
}
```

---

## Publish z priorytetem

Wyższy priorytet = wcześniejsze wykonanie. Priorytet ustawia się przez metadata (klucz `"priority"`):

```java
// Priorytet jako int — wyższy = wcześniejszy
UUID highPriority = taskPublisher.publishTask(
    new CriticalTask(data),
    Map.of("priority", 10, "userId", "user123")
);

// Priorytet jako String — też działa
UUID mediumPriority = taskPublisher.publishTask(
    new NormalTask(data),
    Map.of("priority", "5")
);

// Bez priorytetu — default 0
UUID lowPriority = taskPublisher.publishTask(new BackgroundTask(data));
```

Sortowanie: `ORDER BY priority DESC, next_run_at`.

---

## Deduplication z hash

Hash zapobiega duplikatom aktywnych tasków tego samego typu:

```java
@Service
public class OrderTaskService {

    private final TaskPublisher taskPublisher;

    public void scheduleOrderProcessing(UUID orderId) {
        // Hash z parametrów taska — unikalny per typ + hash
        String hash = HashUtils.getHash(Map.of("orderId", orderId.toString()));

        try {
            taskPublisher.publishTask(
                new ProcessOrderTask(orderId),
                hash,
                Map.of("priority", 5)
            );
        } catch (TaskHashExistsException e) {
            // Aktywny task z tym typem i hashem już istnieje — ignoruj duplikat
            log.info("Task for order {} already scheduled", orderId);
        }
    }
}
```

Unikalność jest per typ taska + hash, tylko dla aktywnych tasków (nie completed/dead). Po zakończeniu taska hash jest zwolniony — można go użyć ponownie. Różne typy tasków mogą mieć ten sam hash.

---

## Odpytywanie tasków (TaskQueryService)

### Po UUID

```java
UUID taskId = taskPublisher.publishTask(new ProcessOrderTask(orderId));

// Później...
Optional<TaskStatus> status = taskQueryService.getTaskStatus(taskId);
if (status.isPresent()) {
    TaskState state = status.get().getState();      // PENDING, RUNNING, COMPLETED, FAILED, DEAD
    boolean done = status.get().isCompleted();
    boolean terminal = status.get().isTerminal();    // COMPLETED lub DEAD
    Duration duration = status.get().getExecutionDuration(); // czas wykonania
    Map<String, Object> meta = status.get().getMetadata();
}
```

### Po metadata (JSONB @> operator)

```java
// Jeden klucz-wartość
Optional<TaskStatus> task = taskQueryService.findTaskByMetadata("userId", "user123");

// Wiele kluczy (AND)
List<TaskStatus> tasks = taskQueryService.findTasksByMetadata(
    Map.of("team", "backend", "priority", "high")
);
```

### Po stanie

```java
List<TaskStatus> pending = taskQueryService.findTasksByState(TaskState.PENDING);
List<TaskStatus> failed = taskQueryService.findTasksByState(TaskState.FAILED);
List<TaskStatus> dead = taskQueryService.findTasksByState(TaskState.DEAD);
```

### Po typie

```java
List<TaskStatus> emailTasks = taskQueryService.findTasksByType(
    SendEmailTask.class.getName()
);
```

### Kombinowane filtry

```java
// Typ + metadata
List<TaskStatus> prodEmails = taskQueryService.findTasksByTypeAndMetadata(
    SendEmailTask.class.getName(),
    Map.of("environment", "prod")
);

// Stan + metadata
List<TaskStatus> failedImportant = taskQueryService.findTasksByStateAndMetadata(
    TaskState.FAILED,
    Map.of("category", "important")
);

// Stan + typ + metadata
List<TaskStatus> completedProdEmails = taskQueryService.findTasksByStateAndTypeAndMetadata(
    TaskState.COMPLETED,
    SendEmailTask.class.getName(),
    Map.of("region", "eu-west")
);
```

---

## Cleanup starych tasków

```java
// Usuń completed taski starsze niż 30 dni
int deleted = taskQueryService.cleanupCompletedTasks(
    Instant.now().minus(Duration.ofDays(30))
);
log.info("Cleaned up {} old completed tasks", deleted);
```

Automatyczny cleanup w schedulingu (YAML):

```yaml
preboot:
  tasks:
    scheduling:
      schedulers:
        myTaskRunner:
          cleanup-interval: 1h
          cleanup-threshold: 24h
```

---

## BackOff i Dead Queue Policies

### Stały czas między retry

```java
new ConstantBackOffPolicy(Duration.ofMinutes(5));
// Zawsze retry po 5 minutach
```

### Exponential backoff z randomizacją

```java
new ExpandingTimeOfBackOffPolicy(
    Duration.ofMinutes(1),  // początkowy backoff
    30,                     // random sekund (0-30)
    2,                      // mnożnik per fail
    60                      // max backoff (minuty)
);
// Formuła: now + 1min + random(0..30)s + min(failCount * 2, 60)min
```

### Dead queue — po czasie

```java
new TimeBasedDeadQueuePolicy(Duration.ofDays(1));
// Task dead gdy createdAt + 1 dzień < now
```

### Własna dead queue policy (np. po ilości prób)

```java
public class MaxRetriesDeadQueuePolicy implements DeadQueuePolicy {
    private final int maxRetries;

    public MaxRetriesDeadQueuePolicy(int maxRetries) {
        this.maxRetries = maxRetries;
    }

    @Override
    public boolean isDead(
            int failCount, String errorMessage, String errorStackTrace,
            String type, Instant createdAt) {
        return failCount >= maxRetries;
    }
}

// Użycie:
factory.createTaskRunner(
    eventPublisher, repo,
    new MaxRetriesDeadQueuePolicy(5),
    new ConstantBackOffPolicy(Duration.ofMinutes(10))
);
```

---

## Scheduling — konfiguracja YAML

### Domyślna konfiguracja

```yaml
preboot:
  tasks:
    scheduling:
      enabled: true                    # default: true
      defaults:
        max-concurrent-tasks: 4        # workerów na scheduler
        auto-start: true               # start przy starcie aplikacji
        heartbeat-interval: 3m         # co ile odświeżać heartbeat
        stalled-check-interval: 15m    # co ile sprawdzać stalled taski
        stalled-threshold: 5m         # po jakim czasie task jest stalled
        shutdown-timeout: 60s          # czas na graceful shutdown
        # Auto-scaling workerów
        sleep-interval: 5s             # interwał pollingu w SLEEP
        active-interval: 1s            # interwał pollingu w PARTIAL/FULL
        idle-timeout: 30s              # czas bez tasków do de-eskalacji
        wake-up-ratio: 0.5            # frakcja workerów w PARTIAL (0.0-1.0)
        sleep-workers: 1               # workerzy aktywni w SLEEP (min: 1)
```

### Per-scheduler override

Klucz = nazwa beana `TaskRunner`:

```yaml
preboot:
  tasks:
    scheduling:
      defaults:
        max-concurrent-tasks: 4
      schedulers:
        emailTaskRunner:              # nazwa @Bean
          max-concurrent-tasks: 8     # nadpisuje default
          sleep-workers: 2            # 2 workerów w SLEEP (szybsza reakcja)
          cleanup-interval: 1h
          cleanup-threshold: 24h
        lowPriorityRunner:
          max-concurrent-tasks: 2
          sleep-interval: 10s         # rzadszy polling w SLEEP
          idle-timeout: 10s           # szybsza de-eskalacja
```

### Przywrócenie zachowania sprzed auto-scalingu

```yaml
preboot:
  tasks:
    scheduling:
      defaults:
        active-interval: 100ms        # stary interwał 100ms
        sleep-workers: 4              # = max-concurrent-tasks → brak parkowania
        idle-timeout: 1s              # minimalny czas w zredukowanych stanach
```

### Wyłączenie schedulingu

```yaml
preboot:
  tasks:
    scheduling:
      enabled: false
```

---

## @ExcludeFromTaskScheduling

Wyklucz konkretnego TaskRunnera z automatycznego schedulingu:

```java
@Configuration
public class TasksConfig {

    @Bean
    TaskRunner emailTaskRunner(TaskConfigFactory factory, EventPublisher ep, TaskRepository repo) {
        return factory.createTaskRunner(ep, repo,
            new TimeBasedDeadQueuePolicy(Duration.ofDays(1)),
            new ConstantBackOffPolicy(Duration.ofMinutes(5)));
    }

    @Bean
    @ExcludeFromTaskScheduling(reason = "Custom scheduler with external trigger")
    TaskRunner manualTaskRunner(TaskConfigFactory factory, EventPublisher ep, TaskRepository repo) {
        return factory.createTaskRunner(ep, repo,
            new TimeBasedDeadQueuePolicy(Duration.ofHours(6)),
            new ConstantBackOffPolicy(Duration.ofMinutes(1)));
    }
}
```

`emailTaskRunner` będzie automatycznie schedulowany. `manualTaskRunner` nie — musisz sam wywoływać `runTask()`.

---

## Wiele kolejek w jednej aplikacji

Każda kolejka = osobna tabela, osobny `TaskRepository` + `TaskPublisher` + `TaskRunner`:

```java
@Configuration
public class MultiQueueConfig {

    // --- Kolejka e-maili ---

    @Bean
    TaskRepository emailTaskRepository(TaskConfigFactory factory) {
        return factory.createTaskRepository("email_tasks");
    }

    @Bean
    TaskPublisher emailTaskPublisher(TaskConfigFactory factory, TaskRepository emailTaskRepository) {
        return factory.createTaskPublisher(emailTaskRepository);
    }

    @Bean
    TaskRunner emailTaskRunner(
            TaskConfigFactory factory, EventPublisher eventPublisher,
            TaskRepository emailTaskRepository) {
        return factory.createTaskRunner(
            eventPublisher, emailTaskRepository,
            new TimeBasedDeadQueuePolicy(Duration.ofDays(1)),
            new ConstantBackOffPolicy(Duration.ofMinutes(5)));
    }

    // --- Kolejka raportów ---

    @Bean
    TaskRepository reportTaskRepository(TaskConfigFactory factory) {
        return factory.createTaskRepository("report_tasks");
    }

    @Bean
    TaskPublisher reportTaskPublisher(TaskConfigFactory factory, TaskRepository reportTaskRepository) {
        return factory.createTaskPublisher(reportTaskRepository);
    }

    @Bean
    TaskRunner reportTaskRunner(
            TaskConfigFactory factory, EventPublisher eventPublisher,
            TaskRepository reportTaskRepository) {
        return factory.createTaskRunner(
            eventPublisher, reportTaskRepository,
            new TimeBasedDeadQueuePolicy(Duration.ofHours(6)),
            new ExpandingTimeOfBackOffPolicy(
                Duration.ofMinutes(1), 30, 2, 60));
    }
}
```

YAML per-scheduler:

```yaml
preboot:
  tasks:
    scheduling:
      schedulers:
        emailTaskRunner:
          max-concurrent-tasks: 8
        reportTaskRunner:
          max-concurrent-tasks: 2
```

---

## Monitoring i diagnostyka SQL

### Status schedulerów (Java)

```java
@RestController
@RequestMapping("/admin/tasks")
public class TaskMonitoringController {

    private final TaskSchedulerRegistry registry;
    private final TaskQueryService taskQueryService;

    @GetMapping("/schedulers")
    public List<TaskSchedulerStatus> getSchedulerStatuses() {
        return registry.getAllStatuses();
    }

    @GetMapping("/schedulers/summary")
    public Map<String, Object> getSummary() {
        return Map.of(
            "schedulerCount", registry.getSchedulerCount(),
            "totalActiveWorkers", registry.getTotalActiveWorkers(),
            "hasPendingTasks", registry.hasAnyPendingTasks(),
            "isAnyShuttingDown", registry.isAnySchedulerShuttingDown()
        );
    }

    @GetMapping("/schedulers/scaling")
    public List<Map<String, Object>> getScalingStates() {
        return registry.getAllStatuses().stream()
            .map(s -> Map.<String, Object>of(
                "scheduler", s.schedulerName(),
                "scalingState", s.scalingState().name(),
                "activeWorkers", s.activeWorkers(),
                "maxWorkers", s.maxConcurrentTasks()
            ))
            .toList();
    }
}
```

### Diagnostyka SQL (bezpośrednie queries)

Widok `_view` oblicza stan na podstawie kolumn:

```sql
-- Pending taski gotowe do uruchomienia
SELECT * FROM my_tasks_view
WHERE computed_state = 'PENDING'
AND next_run_at <= NOW()
ORDER BY priority DESC, next_run_at;

-- Failed taski z błędami
SELECT uuid, type, fail_count, error_message, created_at
FROM my_tasks_view
WHERE computed_state = 'FAILED'
ORDER BY fail_count DESC;

-- Dead taski
SELECT uuid, type, error_message, created_at
FROM my_tasks_view
WHERE computed_state = 'DEAD';

-- Running taski z heartbeat (stalled detection)
SELECT uuid, type, executor_instance_id, heartbeat, started_at
FROM my_tasks
WHERE started_at IS NOT NULL
AND completed = false AND dead = false;

-- Statystyki per typ
SELECT type,
    COUNT(*) FILTER (WHERE computed_state = 'PENDING') AS pending,
    COUNT(*) FILTER (WHERE computed_state = 'RUNNING') AS running,
    COUNT(*) FILTER (WHERE computed_state = 'COMPLETED') AS completed,
    COUNT(*) FILTER (WHERE computed_state = 'FAILED') AS failed,
    COUNT(*) FILTER (WHERE computed_state = 'DEAD') AS dead
FROM my_tasks_view
GROUP BY type;

-- Metadata query (JSONB containment operator)
SELECT * FROM my_tasks
WHERE metadata @> '{"userId": "user123"}'::jsonb;
```

---

## Testowanie — integracyjne z PostgreSQL

### Setup z Testcontainers

```java
@Testcontainers
class TaskIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    private JdbcTemplate jdbcTemplate;
    private TaskPublisher taskPublisher;
    private TaskRunner taskRunner;
    private TaskQueryService taskQueryService;
    private EventPublisher eventPublisher;

    @BeforeEach
    void setUp() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(postgres.getJdbcUrl());
        config.setUsername(postgres.getUsername());
        config.setPassword(postgres.getPassword());
        DataSource dataSource = new HikariDataSource(config);
        jdbcTemplate = new JdbcTemplate(dataSource);

        JsonMapper jsonMapper = JsonMapperFactory.createJsonMapper();

        // Tworzenie tabeli
        TaskTableInitializer initializer = new TaskTableInitializer(jdbcTemplate, "test_tasks");
        initializer.createTables();

        TaskRepository taskRepository = new TaskRepositoryPostgres(jdbcTemplate, "test_tasks");
        taskPublisher = new TaskPublisherImpl(taskRepository, jsonMapper);
        taskQueryService = new TaskQueryServiceImpl(taskRepository, jsonMapper);

        // Event publisher z handlerem
        ApplicationContext ctx = mock(ApplicationContext.class);
        MyHandler handler = new MyHandler();
        when(ctx.getBeanDefinitionNames()).thenReturn(new String[]{"handler"});
        when(ctx.getBean("handler")).thenReturn(handler);

        LocalEventHandlerRepository repo = new LocalEventHandlerRepository(ctx);
        eventPublisher = new LocalEventPublisher(repo);

        taskRunner = new TaskRunnerImpl(
            eventPublisher, taskRepository, jsonMapper,
            new TimeBasedDeadQueuePolicy(Duration.ofDays(1)),
            new ConstantBackOffPolicy(Duration.ofMinutes(5)));
    }

    @Test
    void shouldPublishAndRunTask() {
        // Publish
        UUID taskId = taskPublisher.publishTask(new MyTask("test-data"));

        // Run
        String taskType = taskRunner.runTask();
        assertThat(taskType).isEqualTo(MyTask.class.getName());

        // Verify completed
        Optional<TaskStatus> status = taskQueryService.getTaskStatus(taskId);
        assertThat(status).isPresent();
        assertThat(status.get().getState()).isEqualTo(TaskState.COMPLETED);
    }
}
```

---

## Testowanie — unit test TaskContext

### Test filtrowania po typeParameter

```java
class TaskContextHandlerTest {

    private LocalEventPublisher eventPublisher;
    private static int orderHandlerCalls;
    private static int paymentHandlerCalls;

    @BeforeEach
    void setUp() {
        ApplicationContext ctx = mock(ApplicationContext.class);
        OrderHandler orderHandler = new OrderHandler();
        PaymentHandler paymentHandler = new PaymentHandler();

        when(ctx.getBeanDefinitionNames()).thenReturn(new String[]{"o", "p"});
        when(ctx.getBean("o")).thenReturn(orderHandler);
        when(ctx.getBean("p")).thenReturn(paymentHandler);

        LocalEventHandlerRepository repo = new LocalEventHandlerRepository(ctx);
        eventPublisher = new LocalEventPublisher(repo);

        orderHandlerCalls = 0;
        paymentHandlerCalls = 0;
    }

    @Test
    void shouldRouteTaskContextToCorrectHandler() {
        // Symulacja TaskContext z OrderEvent payload
        Task mockTask = mock(Task.class);
        when(mockTask.getUuid()).thenReturn(UUID.randomUUID());
        when(mockTask.getType()).thenReturn("OrderEvent");
        when(mockTask.getCreatedAt()).thenReturn(Instant.now());
        when(mockTask.getStartedAt()).thenReturn(Instant.now());
        when(mockTask.getFailCount()).thenReturn(0);

        TaskContextImpl<OrderEvent> taskContext =
            new TaskContextImpl<>(mockTask, new OrderEvent("order-1"), mock(JsonMapper.class));

        // Publish — powinien trafić TYLKO do OrderHandler
        eventPublisher.publish(taskContext);

        assertThat(orderHandlerCalls).isEqualTo(1);
        assertThat(paymentHandlerCalls).isEqualTo(0);
    }

    // Handlers
    public static class OrderHandler {
        @EventHandler(typeParameter = OrderEvent.class)
        public void handle(TaskContext<OrderEvent> ctx) { orderHandlerCalls++; }
    }

    public static class PaymentHandler {
        @EventHandler(typeParameter = PaymentEvent.class)
        public void handle(TaskContext<PaymentEvent> ctx) { paymentHandlerCalls++; }
    }

    // Events
    public record OrderEvent(String orderId) {}
    public record PaymentEvent(String paymentId) {}
}
```

---

## Integracja z preboot-eventbus

### TaskRunner wymaga synchronicznego EventPublisher

```java
@Configuration
public class TasksConfig {

    @Bean
    TaskRunner taskRunner(
            TaskConfigFactory factory,
            EventPublisher eventPublisher, // domyślny = sync (@Primary)
            TaskRepository repo) {
        // OK — domyślny EventPublisher jest synchroniczny
        return factory.createTaskRunner(eventPublisher, repo,
            new TimeBasedDeadQueuePolicy(Duration.ofDays(1)),
            new ConstantBackOffPolicy(Duration.ofMinutes(5)));
    }

    // BŁĄD — to rzuci IllegalArgumentException:
    // @Bean
    // TaskRunner brokenRunner(
    //         TaskConfigFactory factory,
    //         @Qualifier("async") EventPublisher asyncPublisher,
    //         TaskRepository repo) {
    //     return factory.createTaskRunner(asyncPublisher, repo, ...);
    // }
}
```

### Dwa podejścia do handlerów

TaskRunner próbuje najpierw direct handler (sam payload), potem fallback do TaskContext handler:

```java
// 1. Direct handler — prosty, bez dostępu do kontekstu
@Service
public class SimpleEmailHandler {
    @EventHandler
    public void handle(SendEmailTask task) {
        // task = deserializowany payload
    }
}

// 2. TaskContext handler — pełny dostęp do metadata, taskId, failCount
@Service
public class RichEmailHandler {
    @EventHandler(typeParameter = SendEmailTask.class)
    public void handle(TaskContext<SendEmailTask> ctx) {
        SendEmailTask task = ctx.getPayload();
        ctx.setMetadata("sentAt", Instant.now().toString());
    }
}

// UWAGA: Nie definiuj obu na raz dla tego samego typu!
// Jeśli oba istnieją — direct handler jest preferowany.
```
