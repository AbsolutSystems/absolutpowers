---
name: preboot-documents-pdf
description: "Skill do używania biblioteki preboot-documents-pdf. Użyj tego skilla zawsze gdy użytkownik chce generować PDF z szablonów DOCX, konwertować DOCX na PDF, wypełniać szablony danymi, używać placeholderów w dokumentach, pętli w tabelach, warunków wyświetlania, dynamicznych obrazków, ekstrakcji placeholderów, lub ładować szablony z bazy danych/S3/zewnętrznego źródła. Obejmuje: DocumentGenerator, PdfDocumentGenerator, Image, extractPlaceholders, generate, byte[] template, InputStream template, office-stamper, docx4j, PrebootDocumentsPdfAutoConfiguration. Triggeruje się na: PDF generation, DOCX to PDF, template stamping, document generation, placeholder replacement, SpEL expressions in templates, repeatTableRow, repeatDocPart, displayParagraphIf, displayTableRowIf, dynamic images, template validation, external templates, byte array template, InputStream template, database template, S3 template, preboot-documents-pdf, DocumentGenerator, PdfDocumentGenerator, office-stamper, docx4j, employment contract, invoice generation, document template, DOCX template, PDF conversion, generate PDF, template from database, template from storage."
---

# preboot-documents-pdf

Generowanie dokumentów PDF z szablonów DOCX. Używa office-stamper 2.8.x do wypełniania szablonów (placeholdery, SpEL, pętle, warunki, obrazki) i docx4j do konwersji na PDF. Szablony mogą pochodzić z classpath, byte[] lub InputStream.

## Zależność Maven

```xml
<dependency>
    <groupId>io.preboot</groupId>
    <artifactId>preboot-documents-pdf</artifactId>
</dependency>
```

Wersje zarządzane przez `preboot-bom` — nie podawaj `<version>`.

## Szybki start

### 1. Szablon DOCX z placeholderami

Utwórz plik `.docx` z placeholderami `${variable}`:
```
Umowa dla: ${employee.firstName} ${employee.lastName}
Stanowisko: ${contract.position}
Data: ${generatedDate}
```

Zapisz w `src/main/resources/docx-templates/employment-contract.docx`.

### 2. Generowanie PDF (classpath)

```java
@Service
@RequiredArgsConstructor
public class ContractService {

    private final DocumentGenerator pdfGenerator;

    public byte[] generateContract(Employee employee, Contract contract) {
        Map<String, Object> data = Map.of(
            "employee", employee,
            "contract", contract,
            "generatedDate", LocalDate.now()
        );
        return pdfGenerator.generate("employment-contract", data);
    }
}
```

### 3. Generowanie PDF (z bazy danych / zewnętrznego źródła)

```java
// Z byte[] (np. BLOB z bazy danych)
byte[] templateBytes = templateRepo.findContent(templateId);
byte[] pdf = pdfGenerator.generate(templateBytes, data);

// Z InputStream (np. S3)
try (InputStream stream = s3Client.getObject(request)) {
    byte[] pdf = pdfGenerator.generate(stream, data);
}
```

### 4. POJO context (zamiast Map)

```java
record ContractContext(Employee employee, Contract contract, LocalDate date) {}

ContractContext ctx = new ContractContext(employee, contract, LocalDate.now());
byte[] pdf = pdfGenerator.generate("employment-contract", ctx);
```

### 5. Ekstrakcja placeholderów (walidacja szablonu)

```java
Set<String> placeholders = pdfGenerator.extractPlaceholders("employment-contract");
// ["employee.firstName", "employee.lastName", "contract.position", ...]

// Działa też z byte[]/InputStream:
Set<String> placeholders = pdfGenerator.extractPlaceholders(templateBytes);
```

## Główne koncepty

### Auto-konfiguracja

Spring Boot automatycznie tworzy bean `PdfDocumentGenerator` gdy:
- `preboot-documents-pdf` jest na classpath
- brak innego beanu `DocumentGenerator`

```yaml
preboot:
  documents:
    pdf:
      template-base-path: /docx-templates/   # domyślnie
```

### Źródła szablonów

| Źródło | Metoda | Użycie |
|--------|--------|--------|
| Classpath (nazwa) | `generate(String, Map/Object)` | Szablony w JAR/WAR |
| byte[] | `generate(byte[], Map/Object)` | Szablony z bazy, REST API |
| InputStream | `generate(InputStream, Map/Object)` | Szablony z S3, filesystem |

**Uwaga:** `byte[]`/`InputStream` overloady na interfejsie `DocumentGenerator` rzucają `UnsupportedOperationException` domyślnie. Tylko `PdfDocumentGenerator` je implementuje.

### Thread safety

Klasa jest thread-safe. Każde wywołanie `generate()` ładuje świeży dokument i tworzy nową instancję `DocxStamper` (stamper ma mutable state w `ExpressionResolver` i `CommentProcessors`).

### Konteksty danych

- **Map context**: `generate(template, Map.of("employee", employee))` — klucze mapy = nazwy zmiennych
- **POJO context**: `generate(template, pojoContext)` — pola POJO dostępne przez SpEL
- Oba wspierają: zagnieżdżone obiekty (`${employee.address.city}`), SpEL (`${name.toUpperCase()}`), pętle, warunki

### Procesory Word (komentarze)

Dodaj komentarz Word do wiersza tabeli lub akapitu:

| Procesor | Działanie |
|----------|-----------|
| `repeatTableRow(items)` | Powtarza wiersz tabeli per element |
| `repeatDocPart(sections)` | Powtarza blok dokumentu per element |
| `displayParagraphIf(condition)` | Warunkowe wyświetlanie akapitu |
| `displayTableRowIf(condition)` | Warunkowe wyświetlanie wiersza |
| `displayTableIf(condition)` | Warunkowa cała tabela |

### Dynamiczne obrazki

```java
import io.preboot.documents.Image;

Image logo = Image.fromInputStream(inputStream, 240, 80, "image/png");
// lub: Image.fromBytes(bytes, 240, 80);

Map<String, Object> data = Map.of("logo", logo, "caption", "Logo firmy");
byte[] pdf = pdfGenerator.generate("branded-doc", data);
```

W szablonie: `${logo}` — zostanie zamieniony na obraz.

## Typowe przepływy

### Pętla w tabeli (repeatTableRow)

Szablon DOCX — wiersz tabeli z komentarzem Word `repeatTableRow(items)`:
```
| ${item.name} | ${item.quantity} | ${item.price} |
```

```java
record Item(String name, int quantity, BigDecimal price) {}

Map<String, Object> data = Map.of("items", List.of(
    new Item("Widget", 5, new BigDecimal("9.99")),
    new Item("Gadget", 3, new BigDecimal("24.99"))
));
byte[] pdf = pdfGenerator.generate("invoice", data);
```

### Warunek wyświetlania

Komentarz Word `displayParagraphIf(showDetails)` na akapicie:

```java
Map<String, Object> data = Map.of(
    "showDetails", true,
    "details", "Szczegóły klienta premium"
);
```

### Generowanie z szablonu z bazy + walidacja

```java
byte[] templateBytes = templateRepo.findContent(templateId);

// 1. Walidacja — sprawdź jakie dane potrzebuje szablon
Set<String> required = pdfGenerator.extractPlaceholders(templateBytes);

// 2. Przygotuj dane
Map<String, Object> data = buildDataMap(required, businessData);

// 3. Generuj PDF
byte[] pdf = pdfGenerator.generate(templateBytes, data);
```

## Pułapki i częste błędy

1. **Nie dodawaj `.docx` do nazwy szablonu** — `generate("contract", data)` nie `generate("contract.docx", data)`. Rozszerzenie jest dodawane automatycznie.

2. **Szablony z byte[]/InputStream nie rzucają TemplateNotFoundException** — zamiast tego `DocumentGenerationException` gdy bytes są uszkodzone.

3. **SpEL w szablonach = trusted code** — gdy używasz byte[]/InputStream z user-uploaded templates, pamiętaj że SpEL expressions mogą wywoływać metody na obiektach kontekstu. Waliduj szablony.

4. **InputStream jest konsumowany** — po wywołaniu `generate(inputStream, data)` strumień jest zużyty. Caller odpowiada za zamknięcie strumienia.

5. **PDF conversion jest CPU-intensive** — dla dużego wolumenu rozważ async processing lub Semaphore limiter.

6. **Fonty na macOS** — `SimpleFontMapper` filtruje problematyczne fonty systemowe. Używaj standardowych fontów (Arial, Times, Calibri).

7. **Kolejność: `generate(null, data)` jest ambiguous** — przy null wartościach rzutuj explicite: `generate((String) null, data)` lub `generate((byte[]) null, data)`.

## Kiedy sięgnąć do references/

- **api-reference.md** — pełne sygnatury wszystkich 9 metod `DocumentGenerator`, klasy wyjątków, `Image` API, konfiguracja auto-configuration
- **examples.md** — więcej przykładów: zagnieżdżone obiekty, SpEL expressions, formatowanie walut/dat, wielowątkowe generowanie, caching, async processing
