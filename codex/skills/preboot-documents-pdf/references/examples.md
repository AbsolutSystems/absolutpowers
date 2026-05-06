# Przykłady — preboot-documents-pdf

## Spis treści

- [Podstawowe użycie (classpath)](#podstawowe-użycie)
- [Zewnętrzne szablony (byte[] / InputStream)](#zewnętrzne-szablony)
- [POJO context](#pojo-context)
- [Pętle (repeatTableRow / repeatDocPart)](#pętle)
- [Warunki (displayParagraphIf / displayTableRowIf)](#warunki)
- [SpEL expressions](#spel-expressions)
- [Dynamiczne obrazki](#dynamiczne-obrazki)
- [Ekstrakcja placeholderów](#ekstrakcja-placeholderów)
- [Wielowątkowe generowanie](#wielowątkowe-generowanie)
- [Limitowanie współbieżności](#limitowanie-współbieżności)
- [Async processing](#async-processing)
- [Integracja z preboot-tasks](#integracja-z-preboot-tasks)

---

## Podstawowe użycie

### Prosty szablon z classpath

```java
@Service
@RequiredArgsConstructor
public class InvoiceService {

    private final DocumentGenerator pdfGenerator;

    public byte[] generateInvoice(String invoiceNumber, String customer, BigDecimal amount) {
        Map<String, Object> data = Map.of(
            "invoiceNumber", invoiceNumber,
            "customerName", customer,
            "invoiceDate", LocalDate.now(),
            "amount", amount.toString()
        );
        return pdfGenerator.generate("invoice", data);
    }
}
```

### Zagnieżdżone obiekty

```java
Employee employee = new Employee("John", "Doe", "john@example.com");
employee.setAddress(new Address("Main St", "New York", "10001"));

Company company = new Company("TechCorp", "Silicon Valley");

Map<String, Object> data = Map.of("employee", employee, "company", company);
byte[] pdf = pdfGenerator.generate("employee-profile", data);
```

Szablon:
```
${employee.firstName} ${employee.lastName}
${employee.address.city}, ${employee.address.zipCode}
Firma: ${company.name}
```

### Formatowanie walut i dat w Javie

```java
BigDecimal salary = new BigDecimal("75000.00");
LocalDate startDate = LocalDate.of(2025, 11, 1);

Map<String, Object> data = Map.of(
    "salary", NumberFormat.getCurrencyInstance(new Locale("pl", "PL")).format(salary),
    "startDate", startDate.format(DateTimeFormatter.ofPattern("dd MMMM yyyy", new Locale("pl")))
);
// salary = "75 000,00 zł", startDate = "01 listopada 2025"
```

---

## Zewnętrzne szablony

### Z bazy danych (byte[])

```java
@Service
@RequiredArgsConstructor
public class DynamicDocumentService {

    private final DocumentGenerator pdfGenerator;
    private final TemplateRepository templateRepo;

    public byte[] generateFromStoredTemplate(Long templateId, Map<String, Object> data) {
        byte[] templateBytes = templateRepo.findContentById(templateId);
        return pdfGenerator.generate(templateBytes, data);
    }
}
```

### Z S3 (InputStream)

```java
public byte[] generateFromS3(String bucketName, String key, Map<String, Object> data) {
    GetObjectRequest request = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    try (InputStream templateStream = s3Client.getObject(request)) {
        return pdfGenerator.generate(templateStream, data);
    } catch (IOException e) {
        throw new RuntimeException("Failed to read template from S3", e);
    }
}
```

### Walidacja szablonu z bazy przed generowaniem

```java
public byte[] generateWithValidation(Long templateId, Map<String, Object> data) {
    byte[] templateBytes = templateRepo.findContentById(templateId);

    // Sprawdź jakie placeholdery wymaga szablon
    Set<String> required = pdfGenerator.extractPlaceholders(templateBytes);

    // Sprawdź czy wszystkie top-level klucze są w data
    Set<String> topLevelKeys = required.stream()
        .map(p -> p.contains(".") ? p.substring(0, p.indexOf('.')) : p)
        .collect(Collectors.toSet());

    Set<String> missing = new HashSet<>(topLevelKeys);
    missing.removeAll(data.keySet());
    if (!missing.isEmpty()) {
        throw new IllegalArgumentException("Missing data keys: " + missing);
    }

    return pdfGenerator.generate(templateBytes, data);
}
```

---

## POJO context

### Record jako context

```java
record ContractContext(Employee employee, Contract contract, LocalDate generatedDate) {}

ContractContext ctx = new ContractContext(employee, contract, LocalDate.now());
byte[] pdf = pdfGenerator.generate("employment-contract", ctx);
```

Szablon:
```
${employee.firstName} ${employee.lastName}
${contract.position} — ${contract.salary}
Data: ${generatedDate}
```

### POJO z byte[] szablonem

```java
byte[] templateBytes = templateRepo.findContent(templateId);
ContractContext ctx = new ContractContext(employee, contract, LocalDate.now());
byte[] pdf = pdfGenerator.generate(templateBytes, (Object) ctx);
```

**Uwaga:** cast `(Object)` potrzebny aby uniknąć ambiguity z `generate(byte[], Map)`.

---

## Pętle

### repeatTableRow — powtarzanie wiersza tabeli

Szablon DOCX: tabela z wierszem danych. Na wiersz danych dodaj komentarz Word: `repeatTableRow(items)`

```
| Nazwa           | Ilość           | Cena             |
|-----------------|-----------------|------------------|
| ${item.name}    | ${item.quantity}| ${item.price}    |
```

```java
record Item(String name, int quantity, String price) {}

Map<String, Object> data = Map.of("items", List.of(
    new Item("Widget", 5, "49.95 zł"),
    new Item("Gadget", 3, "74.97 zł"),
    new Item("Doohickey", 1, "19.99 zł")
));
byte[] pdf = pdfGenerator.generate("invoice-with-items", data);
```

### repeatDocPart — powtarzanie bloku dokumentu

Komentarz Word `repeatDocPart(sections)` na bloku tekstu:

```
${section.title}
${section.content}
```

```java
record Section(String title, String content) {}

Map<String, Object> data = Map.of("sections", List.of(
    new Section("Wstęp", "Opis projektu..."),
    new Section("Zakres prac", "Implementacja modułu...")
));
byte[] pdf = pdfGenerator.generate("report", data);
```

---

## Warunki

### displayParagraphIf — warunkowy akapit

Komentarz Word `displayParagraphIf(showDetails)` na akapicie:

```java
Map<String, Object> data = Map.of(
    "name", "Klient Premium",
    "showDetails", true,
    "details", "Rabat 20%, darmowa dostawa"
);
byte[] pdf = pdfGenerator.generate("customer-summary", data);
```

### displayTableRowIf — warunkowy wiersz tabeli

Komentarz Word `displayTableRowIf(showDiscount)` na wierszu tabeli:

```java
Map<String, Object> data = Map.of(
    "showDiscount", order.hasDiscount(),
    "discountAmount", order.getDiscountFormatted()
);
```

---

## SpEL expressions

### Metody na obiektach

```
Klient: ${customerName.toUpperCase()}
Email: ${employee.email.toLowerCase()}
Ilość pozycji: ${items.size()}
```

### Ternary

```
Status: ${active ? 'Aktywny' : 'Nieaktywny'}
Typ: ${premium ? 'Premium' : 'Standard'}
```

### Bezpieczeństwo SpEL

Office-stamper sandboxuje niebezpieczne konstrukty (type references, constructors). Mimo to, szablony z byte[]/InputStream z user uploads powinny być walidowane — SpEL może wywoływać metody na obiektach kontekstu.

---

## Dynamiczne obrazki

```java
import io.preboot.documents.Image;

// Z bytes
byte[] logoBytes = Files.readAllBytes(Path.of("logo.png"));
Image logo = Image.fromBytes(logoBytes, 200, 60, "image/png");

// Z InputStream
Image logo = Image.fromInputStream(
    getClass().getResourceAsStream("/assets/logo.png"),
    200, 60, "image/png"
);

Map<String, Object> data = Map.of(
    "logo", logo,
    "signature", Image.fromBytes(signatureBytes, 150, 50)
);
byte[] pdf = pdfGenerator.generate("branded-document", data);
```

W szablonie: `${logo}` i `${signature}` — zamienione na obrazy.

---

## Ekstrakcja placeholderów

### Z classpath

```java
Set<String> placeholders = pdfGenerator.extractPlaceholders("employment-contract");
// ["employee.firstName", "employee.lastName", "contract.position",
//  "displayParagraphIf(showDetails)", "repeatTableRow(items)"]
```

### Z byte[] (walidacja szablonu z bazy)

```java
byte[] templateBytes = templateRepo.findContent(templateId);
Set<String> placeholders = pdfGenerator.extractPlaceholders(templateBytes);
```

### Z InputStream

```java
try (InputStream stream = s3Client.getObject(request)) {
    Set<String> placeholders = pdfGenerator.extractPlaceholders(stream);
}
```

---

## Wielowątkowe generowanie

```java
@Service
@RequiredArgsConstructor
public class BulkDocumentService {

    private final DocumentGenerator pdfGenerator;

    public List<byte[]> generateBulk(String template, List<Map<String, Object>> dataList) {
        return dataList.parallelStream()
            .map(data -> pdfGenerator.generate(template, data))
            .toList();
    }
}
```

Thread-safe — każde wywołanie używa niezależnego szablonu i stampera.

---

## Limitowanie współbieżności

```java
@Service
public class ThrottledDocumentService {

    private final DocumentGenerator pdfGenerator;
    private final Semaphore semaphore = new Semaphore(5); // max 5 równoległych

    public byte[] generate(String template, Map<String, Object> data) throws InterruptedException {
        try {
            semaphore.acquire();
            return pdfGenerator.generate(template, data);
        } finally {
            semaphore.release();
        }
    }
}
```

---

## Async processing

```java
@Service
@RequiredArgsConstructor
public class AsyncDocumentService {

    private final DocumentGenerator pdfGenerator;

    @Async
    public CompletableFuture<byte[]> generateAsync(String template, Map<String, Object> data) {
        return CompletableFuture.completedFuture(pdfGenerator.generate(template, data));
    }
}
```

---

## Integracja z preboot-tasks

Generowanie PDF jako background task z retry:

```java
@Service
@RequiredArgsConstructor
public class DocumentTaskService {

    private final TaskPublisher taskPublisher;

    public void scheduleGeneration(Long templateId, Map<String, Object> data) {
        taskPublisher.publishTask(
            "generate-pdf",
            Map.of("templateId", templateId, "data", data)
        );
    }
}

@Component
public class PdfGenerationTaskRunner implements TaskRunner {

    private final DocumentGenerator pdfGenerator;
    private final TemplateRepository templateRepo;
    private final DocumentStorageService storage;

    @Override
    public String getTaskType() { return "generate-pdf"; }

    @Override
    public void run(TaskContext context) {
        Long templateId = context.getMetadata("templateId", Long.class);
        Map<String, Object> data = context.getMetadata("data", Map.class);

        byte[] templateBytes = templateRepo.findContentById(templateId);
        byte[] pdf = pdfGenerator.generate(templateBytes, data);
        storage.save(context.getTaskId(), pdf);
    }
}
```
