# preboot-core — API Reference

## Spis treści

- [TTLMap](#ttlmap)
- [AccessSynchronizer](#accesssynchronizer)
- [RateLimiter](#ratelimiter)
- [TransactionWrapper](#transactionwrapper)
- [HashUtils](#hashutils)
- [BeanValidator](#beanvalidator)
- [JsonMapperFactory](#jsonmapperfactory)
- [JacksonCustomizerAutoConfiguration](#jacksoncustomizerautoconfiguration)
- [JsonMapperAutoConfiguration](#jsonmapperautoconfiguration)
- [PreBootAutoConfiguration](#prebootautoconfiguration)

---

## TTLMap

**Pakiet:** `io.preboot.core.colections`
**Przeznaczenie:** Thread-safe mapa z automatycznym wygasaniem wpisów po określonym czasie (TTL). Wpisy usuwane w tle co 1 sekundę przez współdzielony `ScheduledExecutorService`.

### Konstruktory

```java
public TTLMap(long defaultTTLSeconds)
```
Tworzy mapę z domyślnym TTL. Brak eviction callback.

**Parametry:**
- `defaultTTLSeconds` — domyślny czas życia wpisu w sekundach

```java
public TTLMap(long defaultTTLSeconds, BiConsumer<K, V> evictionCallback)
```
Tworzy mapę z domyślnym TTL i callbackiem wywoływanym przy wygaśnięciu wpisu.

**Parametry:**
- `defaultTTLSeconds` — domyślny czas życia wpisu w sekundach
- `evictionCallback` — `BiConsumer<K, V>` wywoływany gdy wpis wygasa (klucz, wartość)

### Metody

```java
public void put(K key, V value)
```
Dodaje wpis z domyślnym TTL.

```java
public void put(K key, V value, long ttlSeconds)
```
Dodaje wpis z niestandardowym TTL.

**Parametry:**
- `key` — klucz
- `value` — wartość
- `ttlSeconds` — czas życia w sekundach (nadpisuje domyślny)

```java
public V get(K key)
```
Zwraca wartość lub `null` jeśli klucz nie istnieje lub wpis wygasł. Wygasłe wpisy usuwane leniwie przy dostępie (eviction callback wywoływany).

**Zwraca:** `V` lub `null`

```java
public void remove(K key)
```
Usuwa wpis. Eviction callback **wywoływany** przy usunięciu.

```java
public boolean containsKey(K key)
```
Sprawdza czy klucz istnieje i wpis nie wygasł.

**Zwraca:** `true` jeśli klucz istnieje i wpis aktualny

```java
public void clear()
```
Usuwa wszystkie wpisy. Eviction callback **wywoływany** dla każdego wpisu.

```java
public int size()
```
Zwraca liczbę wpisów (włącznie z wygasłymi, które jeszcze nie zostały usunięte przez background cleanup).

**Zwraca:** `int`

```java
public void close()
```
Wyrejestrowuje mapę z background cleanup service. Należy wywołać gdy mapa nie jest już potrzebna.

```java
public static void shutdownCleanupService()
```
Statyczny. Zamyka współdzielony cleanup executor. Automatycznie wywoływany przez shutdown hook — **nie wywoływać ręcznie** chyba że masz pewność, że żadna instancja TTLMap nie jest aktywna.

### Typy wewnętrzne

```java
record TimedEntry<V>(V value, Instant expiryTime) {
    boolean isExpired()
}
```

---

## AccessSynchronizer

**Pakiet:** `io.preboot.core.concurent`
**Przeznaczenie:** Synchronizacja dostępu do zasobów po kluczu. Zapobiega race conditions gdy wiele wątków operuje na tym samym zasobie identyfikowanym kluczem. Używa `ReentrantLock` (kompatybilny z virtual threads).

### Metody

```java
public <K, V> V synchronize(K key, Supplier<V> supplier)
```
Wykonuje operację pod lockiem dla danego klucza. Zwraca wynik operacji.

**Parametry:**
- `key` — klucz synchronizacji (dowolny obiekt z poprawnym `hashCode`/`equals`)
- `supplier` — operacja do wykonania

**Zwraca:** `V` — wynik supplier

```java
public <K> void synchronizeVoid(K key, Runnable runnable)
```
Wykonuje operację pod lockiem bez zwracania wyniku.

**Parametry:**
- `key` — klucz synchronizacji
- `runnable` — operacja do wykonania

```java
public static CompositeKey compositeKey(Object... values)
```
Tworzy klucz złożony z wielu wartości.

**Parametry:**
- `values` — wartości składowe klucza

**Zwraca:** `CompositeKey`

### CompositeKey (klasa wewnętrzna)

```java
public static class CompositeKey {
    @Override public int hashCode()
    @Override public boolean equals(Object obj)
}
```

Klucz złożony z poprawną implementacją `hashCode` i `equals` opartą na `Arrays.hashCode`/`Arrays.equals`. Używany z `compositeKey()`.

### Szczegóły implementacji

- Locki tworzone on-demand, usuwane gdy żaden wątek ich nie używa (reference counting z `AtomicInteger`)
- Fair locks (`new ReentrantLock(true)`) — zapobiega starvation
- `ConcurrentHashMap<Object, CounterLock>` jako storage

---

## RateLimiter

**Pakiet:** `io.preboot.core.concurent`
**Przeznaczenie:** Ograniczanie częstotliwości operacji per klient. Implementacja token bucket — tokeny uzupełniane proporcjonalnie do upływu czasu.

### Konstruktor

```java
public RateLimiter(int defaultRateLimit)
```

**Parametry:**
- `defaultRateLimit` — domyślna liczba żądań na sekundę

### Metody

```java
public void acquire(String clientId) throws InterruptedException
```
Blokująca akwizycja tokenu. Czeka (z `Thread.sleep(100ms)` w pętli) aż token będzie dostępny.

**Parametry:**
- `clientId` — identyfikator klienta

**Rzuca:** `InterruptedException`

```java
public boolean tryAcquire(String clientId)
```
Nieblokująca akwizycja. Zwraca `false` jeśli brak tokenów.

**Parametry:**
- `clientId` — identyfikator klienta

**Zwraca:** `true` jeśli token przyznany

```java
public <T> T executeWithRateLimit(String clientId, Supplier<T> operation) throws InterruptedException
```
Akwizycja tokenu + wykonanie operacji. Blokująca.

**Zwraca:** `T` — wynik operacji

```java
public void executeWithRateLimit(String clientId, Runnable operation) throws InterruptedException
```
Akwizycja tokenu + wykonanie operacji (void). Blokująca.

```java
public void setRateLimit(String clientId, int rateLimit)
```
Ustawia niestandardowy limit dla klienta. Nadpisuje domyślny.

**Parametry:**
- `clientId` — identyfikator klienta
- `rateLimit` — limit żądań na sekundę

### Szczegóły implementacji

- Token bucket per `clientId` w `ConcurrentHashMap`
- Refill: `elapsed_seconds × rate_limit` tokenów, max = rate_limit
- `ReentrantLock` per bucket
- Logging: SLF4J DEBUG przy rate limiting events

---

## TransactionWrapper

**Pakiet:** `io.preboot.core.transaction`
**Przeznaczenie:** Interfejs do programowego zarządzania transakcjami Spring. Przydatny gdy potrzebujesz transakcji wewnątrz metody (nie na całej metodzie) lub gdy musisz wymusić nową transakcję.

### Metody

```java
<T> T doInTransaction(Supplier<T> action)
```
Wykonuje akcję w transakcji. Propagacja: `REQUIRED` (używa istniejącej lub tworzy nową).

**Zwraca:** `T` — wynik akcji

```java
void doInTransaction(Runnable action)
```
Jak wyżej, bez zwracania wyniku.

```java
<T> T doAlwaysInNewTransaction(Supplier<T> action)
```
Wykonuje akcję zawsze w **nowej** transakcji. Propagacja: `REQUIRES_NEW`.

**Zwraca:** `T` — wynik akcji

```java
void doAlwaysInNewTransaction(Runnable action)
```
Jak wyżej, bez zwracania wyniku.

### Implementacja

`TransactionWrapperImpl` — package-private `@Service`. Automatycznie rejestrowany przez component scan. Nie trzeba ręcznie konfigurować.

Wymaga: `spring-tx` na classpath (dostarczone jako `provided` dependency przez preboot-core).

---

## HashUtils

**Pakiet:** `io.preboot.core.util`
**Przeznaczenie:** Generowanie deterministycznych hashy SHA-1 z parametrów mapy. Hash niezależny od kolejności kluczy.

### Metody

```java
public static <T> String getHash(Map<String, T> params)
```

**Parametry:**
- `params` — mapa parametrów do zahashowania. Klucze `String`, wartości dowolne (używane `toString()`)

**Zwraca:** `String` — hex-encoded SHA-1 hash, lub `"-"` dla pustej/null mapy

**Gwarancje:**
- Ten sam zestaw par klucz-wartość zawsze daje ten sam hash
- Kolejność wstawiania do mapy nie wpływa na hash (sortowanie po kluczach)
- Pusta mapa i null zwracają stałą `"-"`

**Rzuca:** `RuntimeException` jeśli SHA-1 niedostępny (nie powinno wystąpić)

---

## BeanValidator

**Pakiet:** `io.preboot.core.validation`
**Przeznaczenie:** Statyczna walidacja obiektów przy użyciu Jakarta Bean Validation API. Przydatny poza kontekstem Spring (np. w testach, CLI tools).

### Metody

```java
public static <T> void validate(T object)
```

**Parametry:**
- `object` — obiekt do walidacji (musi mieć adnotacje Jakarta Validation: `@NotNull`, `@Min`, `@Size`, etc.)

**Rzuca:** `ConstraintViolationException` jeśli walidacja nie przejdzie

**Uwaga:** Tworzy `ValidatorFactory` przy każdym wywołaniu (try-with-resources). Dla masowej walidacji rozważ cache'owanie.

---

## JsonMapperFactory

**Pakiet:** `io.preboot.core.json`
**Przeznaczenie:** Fabryka preconfigurowanego `JsonMapper` (Jackson 3).

### Metody

```java
public static JsonMapper createJsonMapper()
```

**Zwraca:** `JsonMapper` z następującą konfiguracją:
- `FAIL_ON_NULL_FOR_PRIMITIVES` — **wyłączone** (Jackson 3 domyślnie włącza)
- JavaTimeModule, ParameterNamesModule, Jdk8Module — wbudowane w Jackson 3
- `WRITE_DATES_AS_TIMESTAMPS: false` — daty w ISO-8601
- `FAIL_ON_UNKNOWN_PROPERTIES: false` — Jackson 3 default

---

## JacksonCustomizerAutoConfiguration

**Pakiet:** `io.preboot.core`
**Przeznaczenie:** Auto-konfiguracja Spring Boot — customizuje Jackson builder.

**Warunek aktywacji:** `JsonMapper.class` i `JsonMapperBuilderCustomizer.class` na classpath.

**Efekt:** Rejestruje bean `JsonMapperBuilderCustomizer` wyłączający `FAIL_ON_NULL_FOR_PRIMITIVES`.

---

## JsonMapperAutoConfiguration

**Pakiet:** `io.preboot.core`
**Przeznaczenie:** Rejestruje domyślny `JsonMapper` bean.

**Warunki aktywacji:**
- `JsonMapper.class` na classpath
- Brak istniejącego beanu `JsonMapper` (`@ConditionalOnMissingBean`)

**Efekt:** Tworzy `JsonMapper` przez `JsonMapperFactory.createJsonMapper()`.

---

## PreBootAutoConfiguration

**Pakiet:** `io.preboot.core`
**Przeznaczenie:** Główna auto-konfiguracja PreBoot — włącza component scan.

**Efekt:** `@ComponentScan("io.preboot")` — skanuje wszystkie moduły preboot w classpath.
