# preboot-files — Przykłady użycia

## Spis treści

- [Podstawowe operacje — store, retrieve, delete](#podstawowe-operacje--store-retrieve-delete)
- [Custom attributes](#custom-attributes)
- [Filtrowanie plików](#filtrowanie-plików)
- [TTL — pliki tymczasowe](#ttl--pliki-tymczasowe)
- [TTL — monitoring i statystyki](#ttl--monitoring-i-statystyki)
- [Streaming upload dużych plików](#streaming-upload-dużych-plików)
- [Obsługa eventów](#obsługa-eventów)
- [Konfiguracja S3 — MinIO (dev)](#konfiguracja-s3--minio-dev)
- [Konfiguracja S3 — OVH Object Storage](#konfiguracja-s3--ovh-object-storage)
- [Konfiguracja S3 — AWS produkcja](#konfiguracja-s3--aws-produkcja)
- [Custom TenantProvider](#custom-tenantprovider)
- [Error handling](#error-handling)
- [Testy z LocalStack](#testy-z-localstack)
- [Testy z in-memory](#testy-z-in-memory)
- [REST API — curl przykłady](#rest-api--curl-przykłady)

---

## Podstawowe operacje — store, retrieve, delete

```java
import io.preboot.files.api.FileStorageService;
import io.preboot.files.model.FileContent;
import io.preboot.files.model.FileMetadata;

@Service
@RequiredArgsConstructor
public class DocumentService {
    private final FileStorageService fileStorageService;

    public FileMetadata uploadDocument(MultipartFile file, UUID userId, UUID tenantId) {
        try {
            return fileStorageService
                .storeFile(
                    file.getOriginalFilename(),
                    file.getContentType(),
                    file.getInputStream(),
                    userId,
                    tenantId)
                .join();
        } catch (IOException e) {
            throw new RuntimeException("Failed to read file", e);
        }
    }

    public byte[] downloadDocument(UUID fileId, UUID tenantId) {
        try (FileContent content = fileStorageService
                .retrieveFile(fileId, tenantId)
                .join()
                .orElseThrow(() -> new RuntimeException("File not found"))) {
            return content.toByteArray();
        } catch (Exception e) {
            throw new RuntimeException("Failed to download file", e);
        }
    }

    public void deleteDocument(UUID fileId, UUID tenantId) {
        boolean deleted = fileStorageService.deleteFile(fileId, tenantId).join();
        if (!deleted) {
            throw new RuntimeException("File not found or already deleted");
        }
    }

    public Optional<FileMetadata> getMetadata(UUID fileId, UUID tenantId) {
        return fileStorageService.getFileMetadata(fileId, tenantId).join();
    }
}
```

---

## Custom attributes

```java
// Store z atrybutami
Map<String, String> attrs = Map.of(
    "category", "invoice",
    "year", "2025",
    "department", "finance"
);

FileMetadata meta = fileStorageService
    .storeFile("faktura-001.pdf", "application/pdf", inputStream,
        userId, tenantId, attrs)
    .join();

// Odczyt atrybutów
String category = meta.customAttributes().get("category"); // "invoice"
```

---

## Filtrowanie plików

```java
import io.preboot.files.api.FileFilter;

// Po content type
FileFilter pdfFilter = FileFilter.byContentType("application/pdf");

// Po autorze
FileFilter myFiles = FileFilter.byAuthor(currentUserId);

// Po zakresie dat
FileFilter lastMonth = FileFilter.byDateRange(
    Instant.now().minus(Duration.ofDays(30)),
    Instant.now()
);

// Po custom attribute
FileFilter invoices = FileFilter.byCustomAttribute("category", "invoice");

// Kompozycja — PDF-y z kategorią "invoice" LUB pliki admina
FileFilter complex = FileFilter.byContentType("application/pdf")
    .and(FileFilter.byCustomAttribute("category", "invoice"))
    .or(FileFilter.byAuthor(adminId));

// Użycie
List<FileMetadata> results = fileStorageService.listFiles(tenantId, complex).join();

// Wszystkie pliki autora
List<FileMetadata> authorFiles = fileStorageService.getFilesByAuthor(userId, tenantId).join();

// Łączne użycie storage
long bytesUsed = fileStorageService.getTotalStorageUsed(tenantId).join();
```

---

## TTL — pliki tymczasowe

```java
// Upload z TTL 7 dni
FileMetadata temp = fileStorageService
    .storeFileWithTTL("raport-export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        inputStream, Duration.ofDays(7), userId, tenantId)
    .join();

// Sprawdź TTL
Optional<FileTTLMetadata> ttlInfo = fileStorageService
    .getFileTTLInfo(temp.fileId(), tenantId)
    .join();

ttlInfo.ifPresent(ttl -> {
    System.out.println("Expires at: " + ttl.expiresAt());
    System.out.println("Remaining: " + ttl.getRemainingTime());
    System.out.println("Is expired: " + ttl.isExpired());
    System.out.println("Expiring within 24h: " + ttl.isExpiringWithin(Duration.ofHours(24)));
});

// Przedłuż TTL
fileStorageService.updateFileTTL(temp.fileId(), Duration.ofDays(30), tenantId).join();

// Uczyń permanentnym (usuń TTL)
fileStorageService.removeFileTTL(temp.fileId(), tenantId).join();
```

---

## TTL — monitoring i statystyki

```java
// Wszystkie pliki z TTL w tenancie
List<FileTTLMetadata> allTtl = fileStorageService.getFilesTTLInfo(tenantId).join();

// Pliki już wygasłe (czekające na cleanup)
List<FileTTLMetadata> expired = fileStorageService.getExpiredFiles(tenantId).join();

// Pliki wygasające w ciągu 24h
List<FileTTLMetadata> expiringSoon = fileStorageService
    .getFilesExpiringSoon(tenantId, Duration.ofHours(24))
    .join();

// Statystyki (wymaga FileTTLCleanupService z preboot-files-s3)
@RequiredArgsConstructor
@Service
public class StorageMonitorService {
    private final FileTTLCleanupService cleanupService;

    public void reportStats(UUID tenantId) {
        var stats = cleanupService.getTTLStatistics(tenantId);
        log.info("Tenant {} TTL stats: total={}, expired={}, expiringSoon={}, active={}",
            tenantId, stats.totalTtlFiles(), stats.expiredFiles(),
            stats.expiringSoonFiles(), stats.activeFiles());
    }
}
```

---

## Streaming upload dużych plików

```java
// Zwykły upload (cały plik w pamięci)
fileStorageService.storeFile("small.txt", "text/plain", inputStream, userId, tenantId);

// Streaming upload (tylko 1 chunk 10MB w pamięci — dla plików > 10MB)
fileStorageService.storeFileStreaming("big-backup.zip", "application/zip",
    inputStream, userId, tenantId);

// Streaming z custom attributes
fileStorageService.storeFileStreaming("video.mp4", "video/mp4",
    inputStream, userId, tenantId, Map.of("quality", "1080p"));

// Streaming z TTL
fileStorageService.storeFileStreamingWithTTL("temp-export.csv", "text/csv",
    inputStream, Duration.ofHours(48), userId, tenantId);
```

---

## Obsługa eventów

```java
import io.preboot.eventbus.EventHandler;
import io.preboot.files.events.FileStoredEvent;
import io.preboot.files.events.FileDeletedEvent;
import io.preboot.files.events.FileAccessedEvent;

@Component
public class FileAuditHandler {

    @EventHandler
    public void onFileStored(FileStoredEvent event) {
        var meta = event.metadata();
        log.info("File uploaded: {} ({} bytes) by user {} in tenant {}",
            meta.fileName(), meta.fileSize(), meta.authorId(), meta.tenantId());
    }

    @EventHandler
    public void onFileDeleted(FileDeletedEvent event) {
        log.info("File deleted: {} by user {} in tenant {}",
            event.fileId(), event.authorId(), event.tenantId());
    }

    @EventHandler
    public void onFileAccessed(FileAccessedEvent event) {
        log.info("File accessed: {} by user {} at {}",
            event.fileId(), event.accessorId(), event.accessTime());
    }
}
```

---

## Konfiguracja S3 — MinIO (dev)

```yaml
# application-dev.yml
preboot:
  files:
    s3:
      bucket-name: dev-files
      region: us-east-1
      endpoint-url: http://localhost:9000
      access-key-id: minioadmin
      secret-access-key: minioadmin
      path-style-access-enabled: true   # wymagane dla MinIO
      ttl:
        enabled: true
        cleanup-interval: "0 */5 * * * ?"  # co 5 minut (dev)
```

Docker Compose dla MinIO:

```yaml
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
```

---

## Konfiguracja S3 — OVH Object Storage

```yaml
# application-prod-ovh.yml
preboot:
  files:
    s3:
      bucket-name: ${OVH_BUCKET_NAME}
      region: ${OVH_REGION:gra}
      endpoint-url: https://s3.${OVH_REGION:gra}.cloud.ovh.net
      access-key-id: ${OVH_ACCESS_KEY}
      secret-access-key: ${OVH_SECRET_KEY}
      path-style-access-enabled: false
```

---

## Konfiguracja S3 — AWS produkcja

```yaml
# application-prod.yml
preboot:
  files:
    s3:
      bucket-name: ${S3_BUCKET_NAME}
      region: ${AWS_REGION:eu-central-1}
      # NIE podawaj access-key — użyj IAM role (EC2/ECS/EKS)
      max-file-size: 104857600  # 100MB
      multipart-part-size: 20971520  # 20MB chunks
      ttl:
        enabled: true
        cleanup-interval: "0 0 3 * * ?"  # 3:00 AM
        max-concurrent-tenants: 10
        max-cleanup-per-run: 5000
```

---

## Custom TenantProvider

Domyślny `S3TenantProvider` skanuje cały bucket — wolne dla dużych bucketów. Lepiej pobrać tenantów z bazy:

```java
import io.preboot.files.api.TenantProvider;

@Component
public class DatabaseTenantProvider implements TenantProvider {
    private final JdbcTemplate jdbc;

    public DatabaseTenantProvider(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public List<UUID> getAllTenantIds() {
        return jdbc.queryForList(
            "SELECT id FROM tenants WHERE active = true",
            UUID.class
        );
    }

    @Override
    public boolean isTenantActive(UUID tenantId) {
        return Boolean.TRUE.equals(jdbc.queryForObject(
            "SELECT active FROM tenants WHERE id = ?",
            Boolean.class, tenantId
        ));
    }
}
```

Bean zostanie automatycznie użyty zamiast domyślnego (`@ConditionalOnMissingBean`).

---

## Error handling

```java
import io.preboot.files.api.FileStorageException;
import io.preboot.files.api.TTLOperationException;
import java.util.concurrent.CompletionException;

public void safeUpload(InputStream content, UUID userId, UUID tenantId) {
    try {
        fileStorageService.storeFile("file.pdf", "application/pdf",
            content, userId, tenantId).join();
    } catch (CompletionException e) {
        Throwable cause = e.getCause();
        if (cause instanceof FileStorageException fse) {
            log.error("Storage error: {}", fse.getMessage());
        } else {
            log.error("Unexpected error", cause);
        }
    }
}

public void safeTTLUpdate(UUID fileId, UUID tenantId) {
    try {
        fileStorageService.updateFileTTL(fileId, Duration.ofDays(7), tenantId).join();
    } catch (CompletionException e) {
        if (e.getCause() instanceof TTLOperationException ttlEx) {
            log.error("TTL operation '{}' failed for file {}: {}",
                ttlEx.getOperation(), ttlEx.getFileId(), ttlEx.getMessage());
        }
    }
}
```

---

## Testy z LocalStack

```java
import org.testcontainers.containers.localstack.LocalStackContainer;

@SpringBootTest
class FileStorageIntegrationTest {

    static final LocalStackContainer localstack = new LocalStackContainer(
            DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.S3);

    @DynamicPropertySource
    static void configure(DynamicPropertyRegistration registry) {
        localstack.start();
        registry.add("preboot.files.s3.bucket-name", () -> "test-bucket");
        registry.add("preboot.files.s3.region", () -> localstack.getRegion());
        registry.add("preboot.files.s3.endpoint-url",
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.S3).toString());
        registry.add("preboot.files.s3.access-key-id", localstack::getAccessKey);
        registry.add("preboot.files.s3.secret-access-key", localstack::getSecretKey);
        registry.add("preboot.files.s3.path-style-access-enabled", () -> "true");
    }

    @BeforeAll
    static void createBucket() {
        // Stwórz bucket w LocalStack przed testami
        S3Client s3 = S3Client.builder()
            .endpointOverride(localstack.getEndpointOverride(LocalStackContainer.Service.S3))
            .region(Region.of(localstack.getRegion()))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(localstack.getAccessKey(), localstack.getSecretKey())))
            .build();
        s3.createBucket(b -> b.bucket("test-bucket"));
    }

    @Autowired
    private FileStorageService fileStorageService;

    @Test
    void shouldStoreAndRetrieveFile() {
        UUID tenantId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();
        byte[] data = "Hello, World!".getBytes();

        FileMetadata meta = fileStorageService
            .storeFile("test.txt", "text/plain",
                new ByteArrayInputStream(data), userId, tenantId)
            .join();

        assertThat(meta.fileId()).isNotNull();
        assertThat(meta.fileName()).isEqualTo("test.txt");

        try (FileContent content = fileStorageService
                .retrieveFile(meta.fileId(), tenantId).join().orElseThrow()) {
            assertThat(content.toByteArray()).isEqualTo(data);
        }
    }
}
```

---

## Testy z in-memory

```java
// Nie wymaga żadnej konfiguracji S3 — in-memory jest domyślna
@SpringBootTest
class FileServiceTest {

    @Autowired
    private FileStorageService fileStorageService;

    @Test
    void shouldStoreAndListFiles() {
        UUID tenantId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();

        fileStorageService.storeFile("a.pdf", "application/pdf",
            new ByteArrayInputStream("pdf".getBytes()), userId, tenantId).join();
        fileStorageService.storeFile("b.txt", "text/plain",
            new ByteArrayInputStream("txt".getBytes()), userId, tenantId).join();

        List<FileMetadata> pdfs = fileStorageService
            .listFiles(tenantId, FileFilter.byContentType("application/pdf"))
            .join();

        assertThat(pdfs).hasSize(1);
        assertThat(pdfs.get(0).fileName()).isEqualTo("a.pdf");
    }
}
```

---

## REST API — curl przykłady

```bash
# Upload pliku
curl -X POST http://localhost:8080/api/files \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/document.pdf"

# Download pliku
curl -O http://localhost:8080/api/files/{fileId} \
  -H "Authorization: Bearer <token>"

# Metadane pliku
curl http://localhost:8080/api/files/{fileId}/metadata \
  -H "Authorization: Bearer <token>"

# Usunięcie pliku
curl -X DELETE http://localhost:8080/api/files/{fileId} \
  -H "Authorization: Bearer <token>"

# Lista plików z filtrem
curl "http://localhost:8080/api/files?contentType=application/pdf&metadata=category=invoice" \
  -H "Authorization: Bearer <token>"
```
