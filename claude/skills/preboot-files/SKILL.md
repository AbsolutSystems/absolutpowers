---
name: preboot-files
description: "Skill do używania biblioteki preboot-files. Użyj tego skilla zawsze gdy użytkownik chce przechowywanie plików, upload/download plików, file storage, integrację z S3/MinIO/OVH Object Storage, pliki tymczasowe z TTL, automatyczne usuwanie wygasłych plików, multi-tenant file storage, streaming upload dużych plików, REST API do plików, custom metadata na plikach, filtrowanie plików, lub pracuje z zarządzaniem plikami w aplikacji. Obejmuje: FileStorageService, FileContent, FileMetadata, FileTTLMetadata, FileFilter, TenantProvider, UserFileController, S3FileStorageService, InMemoryFileStorageService, FileTTLCleanupService, TTLCleanupTask, FileStoredEvent, FileDeletedEvent, FileAccessedEvent. Triggeruje się na: file storage, upload pliku, download pliku, S3, MinIO, OVH Object Storage, object storage, multipart upload, streaming upload, file TTL, wygasanie plików, temporary files, pliki tymczasowe, file metadata, custom attributes, content type filter, file listing, multi-tenant files, tenant isolation files, file cleanup, expired files, file events, file REST API, preboot-files, CompletableFuture files, async file operations, max file size, bucket configuration, S3 multipart."
---

# preboot-files

Moduł do przechowywania plików z multi-tenant isolation, TTL (automatyczne wygasanie), event-driven architecture i wsparciem dla S3/MinIO/OVH. Składa się z 4 sub-modułów: API (interfejsy), in-memory (dev/test), REST (endpointy HTTP), S3 (produkcja).

## Zależność Maven

Wybierz sub-moduły potrzebne w projekcie:

```xml
<!-- API + modele (zawsze potrzebne) -->
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-files-api</artifactId>
</dependency>

<!-- Implementacja S3 (produkcja) -->
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-files-s3</artifactId>
</dependency>

<!-- In-memory (dev/testy — domyślna jeśli brak S3) -->
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-files-in-memory</artifactId>
</dependency>

<!-- REST API (endpointy /api/files) -->
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-files-rest</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

## Szybki start

### 1. Upload i download pliku (programowo)

```java
@Service
@RequiredArgsConstructor
public class DocumentService {
    private final FileStorageService fileStorageService;

    public UUID uploadDocument(String fileName, InputStream content, UUID userId, UUID tenantId) {
        FileMetadata metadata = fileStorageService
            .storeFile(fileName, "application/pdf", content, userId, tenantId)
            .join();
        return metadata.fileId();
    }

    public byte[] downloadDocument(UUID fileId, UUID tenantId) {
        try (FileContent file = fileStorageService.retrieveFile(fileId, tenantId).join().orElseThrow()) {
            return file.toByteArray();
        }
    }
}
```

### 2. Plik z TTL (automatyczne usunięcie po 7 dniach)

```java
FileMetadata metadata = fileStorageService
    .storeFileWithTTL("export.csv", "text/csv", inputStream,
        Duration.ofDays(7), userId, tenantId)
    .join();
```

### 3. Konfiguracja S3 (application.yml)

```yaml
preboot:
  files:
    s3:
      bucket-name: my-app-files
      region: eu-central-1
      # credentials z IAM role (EC2/ECS) — nie podawaj access-key w YAML
```

Jeśli brak `bucket-name` → automatycznie używa implementacji in-memory.

## Główne koncepty

### Architektura modułów

```
preboot-files-api          ← interfejsy + modele (FileStorageService, FileMetadata, FileFilter)
├── preboot-files-in-memory  ← ConcurrentHashMap, brak TTL ops, do dev/testów
├── preboot-files-s3         ← AWS SDK v2, multipart upload, TTL w custom attributes S3
└── preboot-files-rest       ← Spring MVC controller /api/files (wymaga preboot-securedata)
```

### Kluczowe klasy

| Klasa | Rola |
|-------|------|
| `FileStorageService` | Główny interfejs — store, retrieve, delete, list, TTL |
| `FileMetadata` | Record z metadanymi pliku (id, name, size, author, tenant, custom attrs) |
| `FileContent` | Record = FileMetadata + InputStream (implements AutoCloseable) |
| `FileTTLMetadata` | Record z TTL info (fileId, expiresAt, tenantId) |
| `FileFilter` | Composable filter z fabrycznymi metodami (byContentType, byAuthor, byDateRange, byCustomAttribute) |
| `TenantProvider` | Interfejs do discovery tenantów dla cleanup (domyślnie skanuje S3 bucket) |

### Zależności na inne moduły preboot

| Sub-moduł | Zależności |
|-----------|-----------|
| `preboot-files-api` | `preboot-core` |
| `preboot-files-in-memory` | `preboot-eventbus` |
| `preboot-files-s3` | `preboot-eventbus` |
| `preboot-files-rest` | `preboot-securedata`, `preboot-auth-api` |

### Asynchroniczne API (CompletableFuture)

Wszystkie metody `FileStorageService` zwracają `CompletableFuture`. Użyj `.join()` dla synchronicznego wywołania lub `.thenApply()` dla async chain:

```java
// Synchronicznie
FileMetadata meta = fileStorageService.storeFile(...).join();

// Asynchronicznie
fileStorageService.storeFile(...)
    .thenApply(meta -> sendNotification(meta))
    .exceptionally(ex -> handleError(ex));
```

### Eventy (preboot-eventbus)

Każda operacja publikuje event:

| Event | Kiedy |
|-------|-------|
| `FileStoredEvent(metadata)` | Po zapisaniu pliku |
| `FileDeletedEvent(fileId, tenantId, authorId)` | Po usunięciu pliku |
| `FileAccessedEvent(fileId, tenantId, accessorId, accessTime)` | Po pobraniu pliku |

Obsługa eventów:

```java
@Component
public class FileAuditHandler {
    @EventHandler
    public void onFileStored(FileStoredEvent event) {
        log.info("File stored: {}", event.metadata().fileName());
    }
}
```

### Multi-tenancy

Tenant ID jest wymagany we wszystkich operacjach. Pliki jednego tenanta są niewidoczne dla innego. W S3 klucz ma format: `files/{tenantId}/{fileId}`.

## Typowe przepływy

### Store z custom attributes

```java
Map<String, String> attrs = Map.of("category", "invoice", "year", "2025");
FileMetadata meta = fileStorageService
    .storeFile("faktura.pdf", "application/pdf", content, userId, tenantId, attrs)
    .join();
```

### Filtrowanie plików

```java
FileFilter filter = FileFilter.byContentType("application/pdf")
    .and(FileFilter.byCustomAttribute("category", "invoice"));

List<FileMetadata> invoices = fileStorageService.listFiles(tenantId, filter).join();
```

### Streaming upload (duże pliki, mało RAM)

```java
// S3 multipart upload — tylko 1 chunk w pamięci (domyślnie 10MB)
FileMetadata meta = fileStorageService
    .storeFileStreaming("big-file.zip", "application/zip", inputStream, userId, tenantId)
    .join();
```

### TTL workflow — upload tymczasowy → przedłużenie → usunięcie TTL

```java
// 1. Upload z 1h TTL
FileMetadata temp = fileStorageService
    .storeFileWithTTL("draft.docx", "application/docx", content,
        Duration.ofHours(1), userId, tenantId)
    .join();

// 2. Użytkownik chce zachować → przedłuż TTL
fileStorageService.updateFileTTL(temp.fileId(), Duration.ofDays(30), tenantId).join();

// 3. Użytkownik finalizuje → uczyń permanentnym
fileStorageService.removeFileTTL(temp.fileId(), tenantId).join();
```

### Monitoring TTL

```java
// Pliki wygasające w ciągu 24h
List<FileTTLMetadata> expiringSoon = fileStorageService
    .getFilesExpiringSoon(tenantId, Duration.ofHours(24))
    .join();

for (FileTTLMetadata ttl : expiringSoon) {
    log.warn("File {} expires in {}", ttl.fileId(), ttl.getRemainingTime());
}
```

## Konfiguracja S3 — pełna

```yaml
preboot:
  files:
    s3:
      bucket-name: my-bucket              # wymagane
      region: eu-central-1                # domyślnie us-east-1
      endpoint-url: https://s3.example.com # opcjonalne, dla MinIO/OVH
      path-style-access-enabled: false     # true dla MinIO
      max-file-size: 52428800             # 50MB domyślnie
      multipart-part-size: 10485760       # 10MB, min 5MB (limit S3)
      
      ttl:
        enabled: true                       # domyślnie true
        cleanup-interval: "0 0 2 * * ?"     # cron, domyślnie 2:00 AM
        max-concurrent-tenants: 5           # paralelizm cleanup
        max-cleanup-per-run: 1000           # limit per tenant per run
        default-ttl: 30d                    # domyślny TTL
        max-ttl: 365d                       # maksymalny dozwolony TTL
        expiring-soon-threshold: 1d         # próg "wygasające wkrótce"
        continue-on-error: true             # kontynuuj cleanup mimo błędów
```

## Pułapki i częste błędy

1. **FileContent jest AutoCloseable** — zawsze zamykaj po użyciu (try-with-resources). Niezamknięty InputStream = wyciek połączeń S3.

2. **In-memory nie wspiera TTL** — `storeFileWithTTL()` rzuci `UnsupportedOperationException` w in-memory implementacji. Używaj S3 do testowania TTL (np. z LocalStack/MinIO).

3. **REST wymaga preboot-securedata** — `UserFileController` pobiera tenant/user z `SecurityContextProvider`. Bez security context dostaniesz 401.

4. **Streaming vs zwykły upload** — `storeFileStreaming()` jest istotne tylko dla S3 (multipart upload). In-memory ignoruje różnicę. Używaj streaming dla plików > 10MB.

5. **Custom attributes w S3** — przechowywane jako S3 user metadata. Klucze prefiksy `preboot-*` są zarezerwowane. Nie nadpisuj ich.

6. **TTL cleanup wymaga TenantProvider** — domyślny `S3TenantProvider` skanuje bucket. Dla lepszej wydajności zaimplementuj własny `TenantProvider` z bazy danych.

7. **CompletableFuture.join()** — rzuca `CompletionException` wrappującą oryginalny wyjątek. Obsługuj `FileStorageException` i `TTLOperationException`.

8. **Multipart part size minimum 5MB** — S3 wymaga minimum 5MB per part. Wartości < 5MB zostaną automatycznie ustawione na 10MB (default).

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury wszystkich metod `FileStorageService`, modeli, filtrów, eventów, wyjątków i konfiguracji S3
- **examples.md** — więcej przykładów: MinIO/OVH setup, LocalStack testy, custom TenantProvider, obsługa eventów, error handling, concurrent cleanup
