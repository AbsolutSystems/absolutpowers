# preboot-ddd — API Reference

## Spis treści

- [Core Layer](#core-layer)
  - [AggregateRoot\<ID\>](#aggregaterootid)
  - [AggregateRepository\<A, ID\>](#aggregaterepositoryaid)
  - [AggregateMapper\<A, S, ID\>](#aggregatemapperasid)
  - [SoftDeletable](#softdeletable)
- [Infrastructure Layer](#infrastructure-layer)
  - [AbstractAggregateRepository\<A, S, ID\>](#abstractaggregaterepositoryasid)
  - [AbstractPersistentTaskRepository\<A, S, ID\>](#abstractpersistenttaskrepositoryasid)

---

## Core Layer

Pakiet: `io.preboot.ddd.core`

### AggregateRoot\<ID\>

**Typ:** Klasa abstrakcyjna
**Przeznaczenie:** Bazowa klasa dla wszystkich agregatów DDD. Zarządza cyklem życia domain events za pomocą wzorca "register-then-pull".

**Parametry generyczne:**
- `ID` — typ identyfikatora agregatu (np. `UUID`, `Long`)

#### Metody

| Metoda | Opis |
|--------|------|
| `abstract ID getId()` | Zwraca unikalny identyfikator agregatu. **Musi być zaimplementowana** przez każdy agregat. |
| `protected void registerEvent(Object event)` | Rejestruje domain event. Wywoływana z metod biznesowych agregatu. Event trafia do wewnętrznej listy transient. |
| `Collection<Object> getEvents()` | Zwraca **niemodyfikowalną** kopię zarejestrowanych eventów. **NIE czyści** listy. Do testów i inspekcji. |
| `Collection<Object> pullEvents()` | Zwraca eventy **i czyści** wewnętrzną listę. Używane przez repozytorium po zapisie do publishingu. |

**Ważne szczegóły:**
- Lista eventów jest `transient` — nie jest serializowana
- Eventy zachowują kolejność rejestracji
- Nie jest thread-safe — agregaty powinny być używane w single-threaded context
- `getEvents()` zwraca kopię (modyfikacja zwróconej kolekcji nie wpływa na agregat)

---

### AggregateRepository\<A, ID\>

**Typ:** Interfejs
**Pakiet:** `io.preboot.ddd.core`
**Przeznaczenie:** Interfejs repozytorium w warstwie domenowej. Reprezentuje Collection Pattern z DDD. Zapewnia Persistence Ignorance — domena nie wie jak agregaty są przechowywane.

**Parametry generyczne:**
- `A` — typ agregatu (extends `AggregateRoot`)
- `ID` — typ identyfikatora (np. `UUID`, `Long`)

#### Metody

| Metoda | Opis |
|--------|------|
| `Optional<A> findById(ID id)` | Ładuje agregat z persystencji po ID. Zwraca `Optional.empty()` jeśli nie istnieje. Nie rzuca wyjątku dla brakujących agregatów. |
| `void save(A aggregate)` | Zapisuje stan agregatu i publishuje domain events. Sekwencja: walidacja → konwersja → zapis → pull events → publish. |
| `void delete(A aggregate)` | **Hard delete** — permanentne usunięcie. Operacja infrastrukturalna, **BEZ eventów**. |
| `void deleteById(ID id)` | **Hard delete** po ID. Permanentne usunięcie, **BEZ eventów**. |
| `boolean existsById(ID id)` | Sprawdza czy agregat istnieje. Lekka operacja (np. `SELECT 1`), nie ładuje pełnego agregatu. |

**Wyjątki rzucane przez `save()`:**
- `IllegalArgumentException` — jeśli aggregate jest null lub aggregate.getId() jest null
- `OptimisticLockingFailureException` — konflikt wersji (jeśli skonfigurowane)
- `DataAccessException` — błędy bazodanowe

**Wyjątki rzucane przez `delete()` / `deleteById()`:**
- `IllegalArgumentException` — jeśli argument jest null

---

### AggregateMapper\<A, S, ID\>

**Typ:** Interfejs
**Pakiet:** `io.preboot.ddd.core`
**Przeznaczenie:** Konwersja między agregatami domenowymi a snapshotami bazodanowymi.

**Parametry generyczne:**
- `A` — typ agregatu (extends `AggregateRoot<ID>`)
- `S` — typ snapshota (typically record lub POJO)
- `ID` — typ identyfikatora

#### Metody

| Metoda | Opis |
|--------|------|
| `A toDomain(S snapshot)` | Konwertuje snapshot bazodanowy na agregat domenowy. Powinien zwrócić `null` jeśli snapshot jest `null`. NIE rejestruje żadnych domain events. |
| `S toSnapshot(A aggregate)` | Konwertuje agregat na snapshot do persystencji. Powinien zwrócić `null` jeśli aggregate jest `null`. NIE zawiera domain events (eventy są transient). |

**Zasady implementacji:**
- **Bezstanowy** — brak pól, cała logika w metodach
- **Czysta translacja** — żadnej logiki biznesowej
- **Null-safe** — obsłuż null na wejściu (zwróć null)
- **Konwersje typów** — np. `String` → `Enum` w `toDomain()`, `Enum` → `String` w `toSnapshot()`
- Użyj `@Component` do auto-discovery przez Spring

---

### SoftDeletable

**Typ:** Interfejs
**Pakiet:** `io.preboot.ddd.core`
**Przeznaczenie:** Marker interface dla agregatów wspierających soft delete. Soft delete to **operacja domenowa** (w przeciwieństwie do hard delete, który jest operacją infrastrukturalną).

#### Metody

| Metoda | Opis |
|--------|------|
| `boolean isDeleted()` | Sprawdza czy agregat jest oznaczony jako usunięty. |
| `LocalDateTime getDeletedAt()` | Zwraca timestamp usunięcia. `null` jeśli agregat nie jest usunięty. |
| `void markAsDeleted()` | Oznacza agregat jako usunięty. Powinien: ustawić `deleted=true`, `deletedAt=now()`, zarejestrować event, rzucić `IllegalStateException` jeśli już usunięty. |
| `void restore()` | Przywraca soft-deleted agregat. Powinien: ustawić `deleted=false`, `deletedAt=null`, zarejestrować event, rzucić `IllegalStateException` jeśli nie jest usunięty. |

**Wzorzec implementacji `markAsDeleted()`:**
```java
public void markAsDeleted() {
    if (this.deleted) {
        throw new IllegalStateException("Already deleted");
    }
    this.deleted = true;
    this.deletedAt = LocalDateTime.now();
    registerEvent(new ProductDeleted(getId(), deletedAt));
}
```

**Wzorzec implementacji `restore()`:**
```java
public void restore() {
    if (!this.deleted) {
        throw new IllegalStateException("Not deleted");
    }
    this.deleted = false;
    this.deletedAt = null;
    registerEvent(new ProductRestored(getId()));
}
```

**Interakcja z repozytorium:**
- `findById()` — zwraca agregat **nawet jeśli** jest soft-deleted
- `findActiveById()` — zwraca `Optional.empty()` jeśli jest soft-deleted
- Po `markAsDeleted()` / `restore()` trzeba wywołać `save()` aby zpersystować zmiany i opublikować eventy

---

## Infrastructure Layer

Pakiet: `io.preboot.ddd.infrastructure`

### AbstractAggregateRepository\<A, S, ID\>

**Typ:** Klasa abstrakcyjna (public)
**Extends:** `AbstractBaseRepository<A, S, ID>` (package-private)
**Implements:** `AggregateRepository<A, ID>`
**Przeznaczenie:** Standardowa implementacja repozytorium agregatów z **synchronicznym** in-memory event publishing przez `EventPublisher`.

**Parametry generyczne:**
- `A` — typ agregatu (extends `AggregateRoot<ID>`)
- `S` — typ snapshota
- `ID` — typ identyfikatora

#### Konstruktor

```java
protected AbstractAggregateRepository(
    CrudRepository<S, ID> snapshotRepository,
    AggregateMapper<A, S, ID> mapper,
    EventPublisher eventPublisher
)
```

| Parametr | Opis |
|----------|------|
| `snapshotRepository` | Spring Data `CrudRepository` do persystencji snapshotów |
| `mapper` | Mapper agregat ↔ snapshot |
| `eventPublisher` | Z `preboot-eventbus`, publishuje eventy synchronicznie |

#### Odziedziczone metody (z AbstractBaseRepository)

| Metoda | Opis |
|--------|------|
| `Optional<A> findById(ID id)` | Ładuje snapshot z DB → konwertuje mapperem → zwraca agregat |
| `void save(A aggregate)` | Walidacja → `toSnapshot()` → `snapshotRepository.save()` → `pullEvents()` → `eventPublisher.publish()` dla każdego eventu |
| `void delete(A aggregate)` | Deleguje do `deleteById(aggregate.getId())` |
| `void deleteById(ID id)` | `snapshotRepository.deleteById(id)`, bez eventów |
| `boolean existsById(ID id)` | `snapshotRepository.existsById(id)` |
| `Optional<A> findActiveById(ID id)` | `findById(id)` filtrujący soft-deleted agregaty (jeśli implementują `SoftDeletable`) |

**Charakterystyka event publishing:**
- Synchroniczny — handlery wywoływane natychmiast w tym samym wątku/transakcji
- In-memory — eventy **nie są persystowane**, tracone przy restarcie aplikacji
- Idealny do prostych aplikacji z natychmiastowym przetwarzaniem

---

### AbstractPersistentTaskRepository\<A, S, ID\>

**Typ:** Klasa abstrakcyjna (public)
**Extends:** `AbstractBaseRepository<A, S, ID>` (package-private)
**Implements:** `AggregateRepository<A, ID>`
**Przeznaczenie:** Alternatywna implementacja repozytorium z **asynchronicznym** persistent task publishing przez `TaskPublisher`. Wymaga modułu `preboot-tasks`.

**Parametry generyczne:**
- `A` — typ agregatu (extends `AggregateRoot<ID>`)
- `S` — typ snapshota
- `ID` — typ identyfikatora

#### Konstruktor

```java
protected AbstractPersistentTaskRepository(
    CrudRepository<S, ID> snapshotRepository,
    AggregateMapper<A, S, ID> mapper,
    TaskPublisher taskPublisher
)
```

| Parametr | Opis |
|----------|------|
| `snapshotRepository` | Spring Data `CrudRepository` do persystencji snapshotów |
| `mapper` | Mapper agregat ↔ snapshot |
| `taskPublisher` | Z `preboot-tasks`, publishuje eventy jako persistent tasks |

#### Odziedziczone metody

Identyczne jak `AbstractAggregateRepository` — różni się wyłącznie mechanizmem publishingu eventów.

**Charakterystyka event publishing:**
- Asynchroniczny — taski przetwarzane w tle przez workery
- Persistent — taski zapisywane do DB, przeżywają restart aplikacji
- Automatyczny retry z exponential backoff
- Dead letter queue dla trwale nieudanych tasków
- Deduplikacja
- Wymaga aby event handlery były **idempotentne** (taski mogą być powtórzone)

**Wymagana dodatkowa zależność:**
```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-tasks</artifactId>
</dependency>
```

**Migracja z `AbstractAggregateRepository`:**
1. Zmień klasę bazową z `AbstractAggregateRepository` na `AbstractPersistentTaskRepository`
2. W konstruktorze wstrzyknij `TaskPublisher` zamiast `EventPublisher`
3. Upewnij się że event handlery są idempotentne
