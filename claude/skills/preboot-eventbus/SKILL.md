---
name: preboot-eventbus
description: "Skill do używania biblioteki preboot-eventbus. Użyj tego skilla zawsze gdy użytkownik chce implementować event bus, event-driven architecture, publishować eventy, obsługiwać zdarzenia, tworzyć event handlery, lub pracuje z komunikacją między komponentami. Obejmuje: EventPublisher, EventHandler, GenericEvent, AsynchronousEventPublisher, ExceptionIfNoHandler, LocalEventPublisher, LocalAsynchronousEventPublisher. Triggeruje się na: event bus, event publisher, event handler, publish event, zdarzenia, eventy, komunikacja między komponentami, event-driven, fire and forget, async events, synchronous events, handler priority, generic events, Spring events, domain events publishing, @EventHandler."
---

# preboot-eventbus

Lekki, Spring Boot-kompatybilny event bus — synchroniczny i asynchroniczny publishing eventów z automatycznym odkrywaniem handlerów.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-eventbus</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

Wymaga `preboot-core` (transitive dependency). Opcjonalnie `spring-boot-starter-json` (dla Spring DevTools ClassLoader mismatch support).

## Szybki start

### 1. Stwórz event

```java
public record UserCreatedEvent(String username, LocalDateTime createdAt) {}
```

### 2. Stwórz handler

```java
@Service
public class UserEventHandler {

    @EventHandler
    public void onUserCreated(UserCreatedEvent event) {
        // obsłuż event
    }
}
```

### 3. Publishuj event

```java
@Service
public class UserService {
    private final EventPublisher eventPublisher;

    public UserService(EventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void createUser(String username) {
        // logika biznesowa...
        eventPublisher.publish(new UserCreatedEvent(username, LocalDateTime.now()));
    }
}
```

Zero konfiguracji — auto-configuration rejestruje `EventPublisher` (synchroniczny, `@Primary`) i `AsynchronousEventPublisher` (`@Qualifier("async")`, virtual threads).

## Główne koncepty

### Architektura

```
EventPublisher (interfejs)
├── LocalEventPublisher           — synchroniczny, @Primary, domyślny
└── LocalAsynchronousEventPublisher  — asynchroniczny, @Qualifier("async"), virtual threads

AsynchronousEventPublisher extends EventPublisher  — marker interfejs

LocalEventHandlerRepository      — skanuje beany po @EventHandler, lazy init, thread-safe
EventBusAutoConfiguration        — auto-konfiguruje wszystkie beany
```

### Auto-konfiguracja

Po dodaniu zależności Spring Boot automatycznie tworzy:

| Bean | Typ | Kwalifikator | Opis |
|------|-----|-------------|------|
| `eventPublisher` | `LocalEventPublisher` | `@Primary`, `@Qualifier("sync")` | Synchroniczny, blokujący |
| `asyncEventPublisher` | `LocalAsynchronousEventPublisher` | `@Qualifier("async")` | Asynchroniczny, virtual threads |
| `localEventHandlerRepository` | `LocalEventHandlerRepository` | — | Rejestr handlerów |

### Wstrzykiwanie publisherów

```java
// Domyślny — synchroniczny (@Primary)
@Autowired EventPublisher eventPublisher;

// Jawnie synchroniczny
@Autowired @Qualifier("sync") EventPublisher syncPublisher;

// Asynchroniczny — virtual threads
@Autowired @Qualifier("async") EventPublisher asyncPublisher;
```

### Adnotacja @EventHandler

Oznacza metodę jako handler eventów. Wymagania:
- Klasa musi być **public** i zarządzana przez Springa (bean)
- Metoda musi mieć **dokładnie jeden parametr** (typ eventu)
- Metoda musi być **public**

Atrybuty:
- `priority` (int, default 0) — wyższy = wcześniejsze wywołanie
- `typeParameter` (Class, default void.class) — filtr dla `GenericEvent<T>`

### Generic Events

Eventy z typem generycznym — implementuj `GenericEvent<T>`:

```java
public record DataEvent<T>(T data) implements GenericEvent<T> {
    @Override
    public T getTypeParameter() {
        return data;
    }
}
```

Handler filtruje po `typeParameter`:

```java
@EventHandler(typeParameter = String.class)
public void handleStringData(DataEvent<String> event) { ... }

@EventHandler(typeParameter = Integer.class)
public void handleIntegerData(DataEvent<Integer> event) { ... }
```

### Obsługa brakujących handlerów

Domyślnie brak handlera = warning w logach. Aby wymusić wyjątek, oznacz event:

```java
@ExceptionIfNoHandler
public record CriticalEvent(String data) {}
```

Teraz `publish(new CriticalEvent(...))` rzuci `NoEventHandlerException` jeśli brak handlera.

### Priorytety handlerów

Wyższy `priority` = handler wykonany wcześniej:

```java
@EventHandler(priority = 100)  // wykonany pierwszy
public void highPriority(MyEvent event) { ... }

@EventHandler(priority = 0)    // wykonany drugi (default)
public void normalPriority(MyEvent event) { ... }
```

### Zależności od innych modułów PreBoot

- **preboot-core** (wymagane) — transitive dependency, dostarcza `JsonMapper` dla DevTools support

## Typowe przepływy

### Synchroniczny event (domyślny, zalecany)

```java
@Service
public class OrderService {
    private final EventPublisher eventPublisher;

    public void placeOrder(Order order) {
        // ... logika zapisu
        eventPublisher.publish(new OrderPlacedEvent(order.getId()));
        // handler wykonany ZANIM ta linia się uruchomi
    }
}
```

### Asynchroniczny event (fire-and-forget)

```java
@Service
public class NotificationService {
    private final EventPublisher asyncPublisher;

    public NotificationService(@Qualifier("async") EventPublisher asyncPublisher) {
        this.asyncPublisher = asyncPublisher;
    }

    public void notifyAll(String message) {
        asyncPublisher.publish(new BroadcastEvent(message));
        // handler uruchomiony na virtual thread, publish() wraca natychmiast
    }
}
```

### Wiele handlerów na jeden event

```java
@Service
public class AuditHandler {
    @EventHandler(priority = 50)
    public void audit(OrderPlacedEvent event) { /* logowanie */ }
}

@Service
public class InventoryHandler {
    @EventHandler(priority = 100)
    public void reserveStock(OrderPlacedEvent event) { /* priorytet wyższy → pierwszy */ }
}
```

### Sprawdzenie czy handler istnieje

```java
if (eventPublisher.hasHandler(myEvent)) {
    eventPublisher.publish(myEvent);
} else {
    // fallback
}
```

### Obsługa eventów z proxy Spring (np. @Transactional)

Handlery za Spring AOP proxy (np. `@Transactional`) są automatycznie wykrywane — żadna dodatkowa konfiguracja nie jest potrzebna.

## Synchroniczny vs asynchroniczny — kiedy użyć

### Synchroniczny (domyślny — `EventPublisher`)

- Task execution systems (np. preboot-tasks) — **wymagany**
- Operacje bazodanowe wymagające spójności
- Przepływy biznesowe wymagające ukończenia handlerów
- Gdy wyjątki muszą propagować do callera

### Asynchroniczny (`@Qualifier("async")`)

- Notyfikacje real-time (WebSocket, UI)
- Fire-and-forget: logi, audyt, cache invalidation
- Non-critical side effects
- High-throughput gdy błędy handlerów są akceptowalne

### UWAGA: NIE używaj async z preboot-tasks

Asynchroniczny publisher łamie error handling, retry logic i zarządzanie stanem tasków. Zawsze używaj domyślnego (synchronicznego) publishera z preboot-tasks.

## Pułapki i częste błędy

1. **Klasa handlera nie jest public** — handler nie zostanie zarejestrowany. Klasa MUSI być public.

2. **Metoda handlera z wieloma parametrami** — handler musi mieć dokładnie JEDEN parametr (typ eventu).

3. **Publishowanie payloadu zamiast wrappera GenericEvent** — `publish(data)` zamiast `publish(new DataEvent<>(data))`. Handler na `DataEvent<String>` nie złapie samego `String`.

4. **Async publisher z task systems** — łamie retry i error handling. Zawsze używaj domyślnego publishera.

5. **Zapomniany `@Service`/`@Component` na klasie handlera** — handler nie będzie Spring beanem i nie zostanie odkryty.

6. **Overriding beana z błędną nazwą** — sync: `"eventPublisher"`, async: `"asyncEventPublisher"`. Inna nazwa = auto-config nadal tworzy domyślny bean.

7. **Brak handlera bez `@ExceptionIfNoHandler`** — event jest po cichu ignorowany (tylko warning w logach). Dodaj adnotację jeśli chcesz wyjątek.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury metod, parametry, wyjątki, wszystkie publiczne klasy/interfejsy
- **examples.md** — kompletne przykłady: generic events, priority, custom configuration, overriding auto-config, testowanie
