# preboot-files — API Reference

## Spis treści

- [FileStorageService](#filestorageservice)
- [FileMetadata](#filemetadata)
- [FileContent](#filecontent)
- [FileTTLMetadata](#filettlmetadata)
- [FileFilter](#filefilter)
- [TenantProvider](#tenantprovider)
- [FileStorageException](#filestorageexception)
- [TTLOperationException](#ttloperationexception)
- [Eventy](#eventy)
- [UserFileController (REST)](#userfilecontroller-rest)
- [S3FileStorageProperties](#s3filestorageproperties)
- [FileTTLCleanupService](#filettlcleanupservice)
- [TTLCleanupTask](#ttlcleanuptask)

---

## FileStorageService

**Pakiet:** `io.preboot.files.api`
**Przeznaczenie:** Główny interfejs do operacji na plikach. Wszystkie metody zwracają `CompletableFuture`. Dwie implementacje: `InMemoryFileStorageService` (dev) i `S3FileStorageService` (produkcja).

### Operacje podstawowe

```java
CompletableFuture<FileMetadata> storeFile(
    String fileName, String contentType, InputStream content, UUID authorId, UUID tenantId)
```
Zapisuje plik permanentny (bez TTL).

**Parametry:**
- `fileName` — nazwa pliku (np. `"report.pdf"`)
- `contentType` — MIME type (np. `"application/pdf"`)
- `content` — strumień z danymi pliku
- `authorId` — UUID autora
- `tenantId` — UUID tenanta (izolacja multi-tenant)

**Zwraca:** `FileMetadata` z wygenerowanym `fileId`

---

```java
CompletableFuture<FileMetadata> storeFile(
    String fileName, String contentType, InputStream content,
    UUID authorId, UUID tenantId, Map<String, String> customAttributes)
```
Zapisuje plik permanentny z custom atrybutami.

**Parametry dodatkowe:**
- `customAttributes` — mapa klucz-wartość (np. `Map.of("category", "invoice")`)

---

```java
CompletableFuture<Optional<FileContent>> retrieveFile(UUID fileId, UUID tenantId)
```
Pobiera plik. Zwraca `Optional.empty()` jeśli nie istnieje.

**UWAGA:** `FileContent` implementuje `AutoCloseable` — zawsze zamykaj po użyciu.

---

```java
CompletableFuture<Boolean> deleteFile(UUID fileId, UUID tenantId)
```
Usuwa plik. Zwraca `true` jeśli usunięto, `false` jeśli nie istniał.

---

```java
CompletableFuture<Optional<FileMetadata>> getFileMetadata(UUID fileId, UUID tenantId)
```
Pobiera metadane pliku bez treści.

---

```java
CompletableFuture<List<FileMetadata>> listFiles(UUID tenantId, FileFilter filter)
```
Lista plików tenanta pasujących do filtra.

---

```java
CompletableFuture<Long> getTotalStorageUsed(UUID tenantId)
```
Łączny rozmiar plików tenanta w bajtach.

---

```java
CompletableFuture<List<FileMetadata>> getFilesByAuthor(UUID authorId, UUID tenantId)
```
Pliki konkretnego autora w tenancie.

### Streaming upload

```java
default CompletableFuture<FileMetadata> storeFileStreaming(
    String fileName, String contentType, InputStream content, UUID authorId, UUID tenantId)
```
Upload z niskim zużyciem pamięci (S3 multipart). Domyślna implementacja deleguje do `storeFile()`.

---

```java
default CompletableFuture<FileMetadata> storeFileStreaming(
    String fileName, String contentType, InputStream content,
    UUID authorId, UUID tenantId, Map<String, String> customAttributes)
```
Streaming upload z custom atrybutami.

---

```java
default CompletableFuture<FileMetadata> storeFileStreamingWithTTL(
    String fileName, String contentType, InputStream content,
    Duration ttl, UUID authorId, UUID tenantId)
```
Streaming upload z TTL. Dodaje atrybut `ttl-expires-at` automatycznie.

**Rzuca:** `IllegalArgumentException` jeśli `ttl` jest null, zero lub ujemny.

### Operacje TTL

```java
CompletableFuture<FileMetadata> storeFileWithTTL(
    String fileName, String contentType, InputStream content,
    Duration ttl, UUID authorId, UUID tenantId)
```
Zapisuje plik z automatycznym wygasaniem.

---

```java
CompletableFuture<FileMetadata> updateFileTTL(UUID fileId, Duration ttl, UUID tenantId)
```
Zmienia TTL istniejącego pliku. Można też dodać TTL do pliku permanentnego.

---

```java
CompletableFuture<FileMetadata> removeFileTTL(UUID fileId, UUID tenantId)
```
Usuwa TTL — plik staje się permanentny.

---

```java
CompletableFuture<List<FileTTLMetadata>> getFilesTTLInfo(UUID tenantId)
```
Wszystkie pliki z TTL w tenancie.

---

```java
CompletableFuture<List<FileTTLMetadata>> getExpiredFiles(UUID tenantId)
```
Pliki z przekroczonym TTL (czekające na cleanup).

---

```java
CompletableFuture<List<FileTTLMetadata>> getFilesExpiringSoon(UUID tenantId, Duration threshold)
```
Pliki wygasające w ciągu `threshold`.

---

```java
CompletableFuture<Optional<FileTTLMetadata>> getFileTTLInfo(UUID fileId, UUID tenantId)
```
TTL info dla konkretnego pliku. `Optional.empty()` jeśli plik nie ma TTL.

---

## FileMetadata

**Pakiet:** `io.preboot.files.model`
**Typ:** `record`

```java
public record FileMetadata(
    UUID fileId,
    String fileName,
    String contentType,
    long fileSize,
    UUID authorId,
    UUID tenantId,
    Instant createdAt,
    Instant lastModified,
    Map<String, String> customAttributes)
```

### Fabryka

```java
public static FileMetadata create(
    String fileName, String contentType, long fileSize, UUID authorId, UUID tenantId)
```
Tworzy metadata z losowym `fileId`, `createdAt = Instant.now()`, pustą mapą atrybutów.

---

## FileContent

**Pakiet:** `io.preboot.files.model`
**Typ:** `record`, implementuje `AutoCloseable`

```java
public record FileContent(FileMetadata metadata, InputStream contentStream)
    implements AutoCloseable
```

### Metody

```java
public byte[] toByteArray() throws IOException
```
Konsumuje cały strumień do tablicy bajtów. Zamyka strumień wewnętrzny.

```java
public void close() throws Exception
```
Zamyka `contentStream`. Zawsze wywołuj w try-with-resources.

---

## FileTTLMetadata

**Pakiet:** `io.preboot.files.model`
**Typ:** `record`

```java
public record FileTTLMetadata(UUID fileId, Instant expiresAt, UUID tenantId)
```

### Fabryki

```java
public static FileTTLMetadata create(UUID fileId, Duration ttlDuration, UUID tenantId)
```
Tworzy z `expiresAt = Instant.now() + ttlDuration`.

```java
public static FileTTLMetadata withExpiration(UUID fileId, Instant expiresAt, UUID tenantId)
```
Tworzy z konkretnym momentem wygaśnięcia.

### Metody

```java
public boolean isExpired()
```
Czy plik już wygasł (`Instant.now() > expiresAt`).

```java
public boolean isExpiringWithin(Duration threshold)
```
Czy plik wygaśnie w ciągu `threshold`.

```java
public Duration getRemainingTime()
```
Czas do wygaśnięcia. `Duration.ZERO` jeśli już wygasł.

```java
public FileTTLMetadata withUpdatedTTL(Duration newTtlDuration)
```
Nowa instancja z zaktualizowanym `expiresAt`.

---

## FileFilter

**Pakiet:** `io.preboot.files.api`
**Typ:** `interface` (functional)

```java
public interface FileFilter {
    boolean matches(FileMetadata metadata);
}
```

### Fabryki statyczne

```java
static FileFilter byContentType(String contentType)
static FileFilter byAuthor(UUID authorId)
static FileFilter byDateRange(Instant from, Instant to)
static FileFilter byCustomAttribute(String key, String value)
```

### Kompozycja

```java
default FileFilter and(FileFilter other)
default FileFilter or(FileFilter other)
```

**Przykład:**
```java
FileFilter filter = FileFilter.byContentType("application/pdf")
    .and(FileFilter.byCustomAttribute("status", "approved"))
    .or(FileFilter.byAuthor(adminId));
```

---

## TenantProvider

**Pakiet:** `io.preboot.files.api`
**Przeznaczenie:** Discovery tenantów dla TTL cleanup. Domyślna implementacja (`S3TenantProvider`) skanuje S3 bucket. Zaimplementuj własną dla lepszej wydajności.

```java
public interface TenantProvider {
    List<UUID> getAllTenantIds();
    default boolean isTenantActive(UUID tenantId);
}
```

---

## FileStorageException

**Pakiet:** `io.preboot.files.api`
**Typ:** `RuntimeException`

Bazowy wyjątek dla operacji na plikach.

```java
public class FileStorageException extends RuntimeException {
    public FileStorageException(String message)
    public FileStorageException(String message, Throwable cause)
    public FileStorageException(Throwable cause)
}
```

---

## TTLOperationException

**Pakiet:** `io.preboot.files.api`
**Typ:** extends `FileStorageException`

Wyjątek specyficzny dla operacji TTL. Zawiera nazwę operacji i opcjonalnie `fileId`.

```java
public class TTLOperationException extends FileStorageException {
    public TTLOperationException(String operation, UUID fileId, String message)
    public TTLOperationException(String operation, UUID fileId, String message, Throwable cause)
    public TTLOperationException(String operation, String message, Throwable cause)
    
    public String getOperation()
    public UUID getFileId()  // może być null
}
```

---

## Eventy

**Pakiet:** `io.preboot.files.events`

Publikowane przez `EventPublisher` (preboot-eventbus). Obsługuj za pomocą `@EventHandler`.

```java
public record FileStoredEvent(FileMetadata metadata) {}
public record FileDeletedEvent(UUID fileId, UUID tenantId, UUID authorId) {}
public record FileAccessedEvent(UUID fileId, UUID tenantId, UUID accessorId, Instant accessTime) {}
```

---

## UserFileController (REST)

**Pakiet:** `io.preboot.files.rest`
**Moduł:** `preboot-files-rest`
**Base path:** `/api/files`
**Wymaga:** `preboot-securedata` (SecurityContextProvider), `preboot-auth-api`

| Metoda | Path | Opis | Response |
|--------|------|------|----------|
| POST | `/api/files` | Upload pliku (multipart/form-data) | 201 + Location header |
| GET | `/api/files/{fileId}` | Download pliku | 200 + Content-Disposition |
| GET | `/api/files/{fileId}/metadata` | Metadane pliku | 200 + JSON |
| DELETE | `/api/files/{fileId}` | Usunięcie pliku | 204 No Content |
| GET | `/api/files` | Lista plików użytkownika | 200 + JSON |

### Query params dla GET /api/files

| Param | Opis | Przykład |
|-------|------|---------|
| `contentType` | Filtruj po MIME type | `?contentType=application/pdf` |
| `metadata` | Filtruj po custom attribute (KEY=VALUE) | `?metadata=category=invoice` |

### Bezpieczeństwo

Controller sprawdza `SecurityContextProvider.getCurrentContext()` — zwraca 401 jeśli brak kontekstu. Download i delete weryfikują ownership (authorId + tenantId) — zwraca 403 jeśli plik należy do innego użytkownika.

### Obsługa błędów (FileRestExceptionHandler)

| Wyjątek | HTTP Status |
|---------|-------------|
| `FileStorageException` | 400 Bad Request |
| `MaxUploadSizeExceededException` | 413 Payload Too Large |
| `MethodArgumentNotValidException` | 400 + field errors |
| Inne | 500 Internal Server Error |

---

## S3FileStorageProperties

**Pakiet:** `io.preboot.files.s3`
**Prefix:** `preboot.files.s3`

| Pole | Typ | Domyślnie | Opis |
|------|-----|-----------|------|
| `bucket-name` | String | **wymagane** | Nazwa bucketa S3 |
| `region` | String | `us-east-1` | Region AWS |
| `endpoint-url` | String | null | Custom endpoint (MinIO, OVH) |
| `access-key-id` | String | null | AWS access key (null = IAM role) |
| `secret-access-key` | String | null | AWS secret key |
| `max-file-size` | long | 52428800 (50MB) | Maks. rozmiar pliku w bajtach |
| `path-style-access-enabled` | boolean | false | Path-style access (true dla MinIO) |
| `multipart-part-size` | long | 10485760 (10MB) | Rozmiar chunka multipart (min 5MB) |

### TTL Config (`preboot.files.s3.ttl`)

| Pole | Typ | Domyślnie | Opis |
|------|-----|-----------|------|
| `enabled` | boolean | true | Włącz TTL |
| `cleanup-interval` | String (cron) | `0 0 2 * * ?` | Harmonogram cleanup |
| `max-concurrent-tenants` | int | 5 | Limit równoległych tenantów w cleanup |
| `max-cleanup-per-run` | int | 1000 | Limit plików per tenant per run |
| `default-ttl` | Duration | 30d | Domyślny TTL |
| `max-ttl` | Duration | 365d | Maksymalny dozwolony TTL |
| `expiring-soon-threshold` | Duration | 1d | Próg "wygasa wkrótce" |
| `cleanup-timeout` | Duration | 5m | Timeout per plik w cleanup |
| `continue-on-error` | boolean | true | Kontynuuj mimo błędów |
| `verbose-logging` | boolean | false | Szczegółowe logi cleanup |

### Temp Config (`preboot.files.s3.ttl.temp`)

| Pole | Typ | Domyślnie | Opis |
|------|-----|-----------|------|
| `enabled` | boolean | false | Włącz serwis plików tymczasowych |
| `default-ttl` | Duration | 1h | Domyślny TTL temp |
| `upload-ttl` | Duration | 30m | TTL uploadów w trakcie przetwarzania |
| `processing-ttl` | Duration | 2h | TTL plików pośrednich |
| `export-ttl` | Duration | 24h | TTL eksportów do pobrania |
| `preview-ttl` | Duration | 15m | TTL podglądów/miniatur |

### Session Config (`preboot.files.s3.ttl.session`)

| Pole | Typ | Domyślnie | Opis |
|------|-----|-----------|------|
| `enabled` | boolean | false | Włącz serwis plików sesyjnych |
| `default-ttl` | Duration | 2h | Domyślny TTL sesji |
| `max-ttl` | Duration | 8h | Maksymalny TTL sesji |
| `inactive-ttl` | Duration | 30m | TTL nieaktywnych sesji |
| `auto-extend` | boolean | true | Auto-przedłużanie przy dostępie |
| `extension-threshold` | Duration | 15m | Przedłuż jeśli zostało mniej niż |
| `max-files-per-session` | int | 100 | Limit plików per sesja |

---

## FileTTLCleanupService

**Pakiet:** `io.preboot.files.s3.cleanup`
**Przeznaczenie:** Cleanup wygasłych plików. Używa virtual threads dla concurrent tenant processing.

### Metody

```java
CleanupResult cleanupExpiredFiles(UUID tenantId)
```
Cleanup dla jednego tenanta. Przetwarza max `maxCleanupPerRun` plików.

```java
OverallCleanupResult cleanupAllExpiredFiles(List<UUID> tenantIds)
```
Cleanup dla wielu tenantów równolegle (limitowane semaforem `maxConcurrentTenants`).

```java
List<FileTTLMetadata> getFilesExpiringSoon(UUID tenantId)
```
Pliki wygasające w ciągu `expiringSoonThreshold`.

```java
TTLStatistics getTTLStatistics(UUID tenantId)
```
Statystyki TTL: total, expired, expiring soon, active.

### Typy wynikowe

```java
record CleanupResult(UUID tenantId, boolean success, int deletionOperationsPerformed,
    int errors, Duration duration, String errorMessage)

record OverallCleanupResult(int tenantsProcessed, int totalDeletionOperationsPerformed,
    int totalErrors, List<UUID> failedTenants, Duration totalDuration)

record TTLStatistics(UUID tenantId, int totalTtlFiles, int expiredFiles,
    int expiringSoonFiles, int activeFiles)
```

---

## TTLCleanupTask

**Pakiet:** `io.preboot.files.s3.cleanup`
**Przeznaczenie:** Scheduled task uruchamiający cleanup wg crona.

```java
@Scheduled(cron = "${preboot.files.s3.ttl.cleanup-interval}")
public void runScheduledCleanup()
```
Automatyczny cleanup — pobiera tenantów z `TenantProvider`, deleguje do `FileTTLCleanupService`.

```java
public OverallCleanupResult runManualCleanup(UUID tenantId)
```
Ręczny trigger cleanup dla jednego tenanta.

```java
public Map<UUID, TTLStatistics> getAllTenantStatistics()
```
Statystyki TTL per tenant (monitoring).
