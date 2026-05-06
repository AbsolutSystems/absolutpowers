# API Reference — preboot-eventbus

Pakiet: `io.preboot.eventbus`

## Spis treści

- [EventPublisher (interfejs)](#eventpublisher)
- [AsynchronousEventPublisher (interfejs)](#asynchronouseventpublisher)
- [LocalEventPublisher (klasa)](#localeventpublisher)
- [LocalAsynchronousEventPublisher (klasa)](#localasynchronouseventpublisher)
- [LocalEventHandlerRepository (klasa)](#localeventhandlerrepository)
- [@EventHandler (adnotacja)](#eventhandler)
- [GenericEvent\<T\> (interfejs)](#genericevent)
- [@ExceptionIfNoHandler (adnotacja)](#exceptionifnohandler)
- [EventBusAutoConfiguration (klasa)](#eventbusautoconfiguration)
- [EventPublishException (wyjątek)](#eventpublishexception)
- [NoEventHandlerException (wyjątek)](#noeventhandlerexception)
- [ReDeserializable (interfejs wewnętrzny)](#redeserializable)

---

## EventPublisher

**Interfejs** — główny kontrakt do publishowania eventów.

```java
public interface EventPublisher {
    <T> void publish(T event);
    default <T> boolean hasHandler(T event);
}
```

### Metody

#### `publish(T event)`
Publishuje event do zarejestrowanych handlerów.

| Parametr | Typ | Opis |
|----------|-----|------|
| `event` | `T` | Obiekt eventu do opublikowania |

**Rzuca:**
- `NoEventHandlerException` — jeśli event ma `@ExceptionIfNoHandler` i brak handlera
- `EventPublishException` — jeśli handler rzuci wyjątek (w trybie synchronicznym)

#### `hasHandler(T event)`
Sprawdza czy istnieje handler dla danego eventu.

| Parametr | Typ | Opis |
|----------|-----|------|
| `event` | `T` | Event do sprawdzenia |

**Zwraca:** `boolean` — `true` jeśli handler istnieje

**Uwaga:** Domyślna implementacja rzuca `RuntimeException("Not implemented")`. Zaimplementowane w `LocalEventPublisher` i `LocalAsynchronousEventPublisher`.

---

## AsynchronousEventPublisher

**Interfejs** — marker interfejs dla asynchronicznych publisherów.

```java
public interface AsynchronousEventPublisher extends EventPublisher {}
```

Rozszerza `EventPublisher` bez dodatkowych metod. Służy do type-safe rozróżnienia sync vs async publisherów.

---

## LocalEventPublisher

**Klasa** — synchroniczna implementacja `EventPublisher`.

```java
public class LocalEventPublisher implements EventPublisher
```

### Konstruktor

```java
public LocalEventPublisher(LocalEventHandlerRepository localEventHandlerRepository)
```

| Parametr | Typ | Opis |
|----------|-----|------|
| `localEventHandlerRepository` | `LocalEventHandlerRepository` | Repozytorium handlerów |

### Zachowanie `publish()`

1. Sprawdza czy handler istnieje
2. Jeśli brak handlera:
   - Event ma `@ExceptionIfNoHandler` → rzuca `NoEventHandlerException`
   - Inaczej → loguje warning i wraca
3. Wywołuje handlery **synchronicznie** na wątku callera
4. Wyjątki handlerów propagują jako `EventPublishException`

---

## LocalAsynchronousEventPublisher

**Klasa** — asynchroniczna implementacja `EventPublisher`.

```java
public class LocalAsynchronousEventPublisher implements AsynchronousEventPublisher
```

### Konstruktor

```java
public LocalAsynchronousEventPublisher(
    LocalEventHandlerRepository localEventHandlerRepository,
    Executor executor)
```

| Parametr | Typ | Opis |
|----------|-----|------|
| `localEventHandlerRepository` | `LocalEventHandlerRepository` | Repozytorium handlerów |
| `executor` | `java.util.concurrent.Executor` | Executor do asynchronicznego uruchamiania handlerów |

### Zachowanie `publish()`

1. Sprawdza czy handler istnieje (synchronicznie)
2. Jeśli brak handlera — zachowanie identyczne jak `LocalEventPublisher`
3. Deleguje wykonanie handlerów do `executor` (asynchronicznie)
4. `publish()` wraca natychmiast po zleceniu do executora
5. Rzuca `IllegalStateException` jeśli executor jest null

**Uwaga:** Wyjątki handlerów NIE propagują do callera (wykonanie asynchroniczne).

---

## LocalEventHandlerRepository

**Klasa** — skanuje Spring ApplicationContext i zarządza handlerami eventów.

```java
public class LocalEventHandlerRepository implements ApplicationContextAware
```

### Konstruktory

```java
@Deprecated
public LocalEventHandlerRepository(ApplicationContext applicationContext)
```
Bez Spring DevTools support. Użyj konstruktora z `JsonMapper`.

```java
public LocalEventHandlerRepository(ApplicationContext applicationContext, JsonMapper jsonMapper)
```

| Parametr | Typ | Opis |
|----------|-----|------|
| `applicationContext` | `ApplicationContext` | Kontekst Springa do skanowania beanów |
| `jsonMapper` | `JsonMapper` (nullable) | Mapper JSON do re-deserializacji przy ClassLoader mismatch (DevTools). `null` = wyłączone |

### Metody publiczne

#### `publish(Object event)`
Publishuje event bezpośrednio do handlerów (bez sprawdzania `@ExceptionIfNoHandler`).

Inicjalizuje handlery przy pierwszym wywołaniu (lazy init). Wspiera:
- Bezpośrednie dopasowanie typów
- Dopasowanie po interfejsach i superklasach
- Filtrowanie po `typeParameter` dla `GenericEvent`
- Automatyczna re-deserializacja przy ClassLoader mismatch

**Rzuca:** `EventPublishException` — jeśli handler rzuci wyjątek

#### `isHandlerMissing(T event)`
Sprawdza czy brak handlera dla danego eventu.

| Parametr | Typ | Opis |
|----------|-----|------|
| `event` | `T` | Event do sprawdzenia |

**Zwraca:** `boolean` — `true` jeśli brak handlera, `false` jeśli handler istnieje

### Zachowanie wewnętrzne

- **Lazy initialization** — skanowanie beanów odroczone do pierwszego `publish()` lub `isHandlerMissing()`
- **Thread-safe** — double-checked locking z `ReentrantLock`
- **Proxy support** — wykrywa handlery za Spring AOP proxy (np. `@Transactional`) przez `AopUtils.getTargetClass()`
- **Polimorfizm** — handler na `BaseEvent` obsłuży też `DerivedEvent extends BaseEvent`
- **Priority sorting** — handlery posortowane malejąco po priority przy rejestracji

---

## @EventHandler

**Adnotacja** — oznacza metodę jako handler eventów.

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface EventHandler {
    int priority() default 0;
    Class<?> typeParameter() default void.class;
}
```

### Atrybuty

| Atrybut | Typ | Default | Opis |
|---------|-----|---------|------|
| `priority` | `int` | `0` | Priorytet — wyższy = wykonany wcześniej |
| `typeParameter` | `Class<?>` | `void.class` | Filtr typu generycznego dla `GenericEvent<T>`. `void.class` = brak filtra |

### Wymagania dla metody

- Klasa musi być **public**
- Metoda musi mieć **dokładnie 1 parametr** (typ eventu)
- Klasa musi być **Spring beanem** (`@Service`, `@Component`, itp.)

---

## GenericEvent\<T\>

**Interfejs** — marker dla eventów z typem generycznym, umożliwia filtrowanie runtime po typie parametru.

```java
public interface GenericEvent<T> {
    T getTypeParameter();
}
```

### Metody

#### `getTypeParameter()`
Zwraca instancję typu parametru generycznego (zazwyczaj payload eventu).

**Zwraca:** `T` — instancja typu parametru, używana do runtime type filtering

### Użycie

Zaimplementuj w evencie, a handler filtruj przez `@EventHandler(typeParameter = ...)`:

```java
public record DataEvent<T>(T data) implements GenericEvent<T> {
    @Override
    public T getTypeParameter() { return data; }
}
```

---

## @ExceptionIfNoHandler

**Adnotacja** — nakładana na **klasę eventu**. Powoduje rzucenie `NoEventHandlerException` jeśli brak handlera.

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface ExceptionIfNoHandler {}
```

Domyślne zachowanie (bez adnotacji): brak handlera = warning w logach, event ignorowany.

---

## EventBusAutoConfiguration

**Klasa** — Spring Boot auto-konfiguracja. Rejestrowana przez `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.

```java
@AutoConfiguration
public class EventBusAutoConfiguration
```

### Tworzone beany

| Bean name | Typ | Warunek | Kwalifikator |
|-----------|-----|---------|-------------|
| `localEventHandlerRepository` | `LocalEventHandlerRepository` | `@ConditionalOnMissingBean(LocalEventHandlerRepository.class)` | — |
| `eventPublisher` | `LocalEventPublisher` | `@ConditionalOnMissingBean(name = "eventPublisher")` | `@Primary`, `@Qualifier("sync")` |
| `asyncEventPublisher` | `LocalAsynchronousEventPublisher` | `@ConditionalOnMissingBean(name = "asyncEventPublisher")` | `@Qualifier("async")` |

Async publisher używa `Executors.newVirtualThreadPerTaskExecutor()` (Java 21+ virtual threads).

### Overriding

Zdefiniuj bean z odpowiednią nazwą aby nadpisać auto-konfigurację:
- Sync: bean o nazwie `"eventPublisher"`
- Async: bean o nazwie `"asyncEventPublisher"`
- Repository: bean typu `LocalEventHandlerRepository`

---

## EventPublishException

**Wyjątek** — opakowuje wyjątki rzucone przez handlery.

```java
public class EventPublishException extends RuntimeException {
    public EventPublishException(Throwable cause)
}
```

Rzucany przez `LocalEventHandlerRepository.publish()` gdy `handler.method().invoke()` rzuci wyjątek.

---

## NoEventHandlerException

**Wyjątek** — brak handlera dla eventu oznaczonego `@ExceptionIfNoHandler`.

```java
public class NoEventHandlerException extends RuntimeException {
    public <T> NoEventHandlerException(T event)
}
```

Wiadomość: `"No event handler found for event: " + event`

---

## ReDeserializable

**Interfejs wewnętrzny** — NIE implementuj w kodzie aplikacyjnym.

```java
public interface ReDeserializable {
    Object withReDeserializedPayload(JsonMapper jsonMapper, ClassLoader targetClassLoader);
}
```

Używany wewnętrznie przez `LocalEventHandlerRepository` do obsługi Spring DevTools ClassLoader mismatch. Eventy implementujące ten interfejs mogą efektywnie re-deserializować payload bez pełnej serializacji JSON.
