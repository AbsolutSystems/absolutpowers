# API Reference — preboot-documents-pdf

## Spis treści

- [DocumentGenerator (interfejs)](#documentgenerator)
- [PdfDocumentGenerator](#pdfdocumentgenerator)
- [Image](#image)
- [Wyjątki](#wyjątki)
- [Auto-konfiguracja](#auto-konfiguracja)
- [Properties](#properties)

---

## DocumentGenerator

**Pakiet:** `io.preboot.documents`
**Typ:** Interfejs

Główny interfejs do generowania dokumentów z szablonów. Metody `String templateName` ładują z classpath. Metody `byte[]`/`InputStream` przyjmują surowe dane szablonu — rzucają `UnsupportedOperationException` domyślnie (implementacja musi je nadpisać).

### Metody — generowanie z classpath

```java
byte[] generate(String templateName, Map<String, Object> data)
```
- `templateName` — nazwa szablonu bez rozszerzenia (np. `"employment-contract"`)
- `data` — mapa danych do wypełnienia placeholderów
- Rzuca: `TemplateNotFoundException`, `DocumentGenerationException`, `IllegalArgumentException`

```java
default byte[] generate(String templateName, Object context)
```
- `context` — POJO lub Map, pola dostępne przez SpEL
- Domyślnie: `UnsupportedOperationException`

```java
default Set<String> extractPlaceholders(String templateName)
```
- Zwraca set nazw placeholderów i wyrażeń z komentarzy Word
- Domyślnie: `UnsupportedOperationException`

### Metody — generowanie z byte[]

```java
default byte[] generate(byte[] templateBytes, Map<String, Object> data)
```
- `templateBytes` — surowe bajty pliku .docx, nie null, nie empty
- Rzuca: `DocumentGenerationException`, `IllegalArgumentException`, `UnsupportedOperationException`

```java
default byte[] generate(byte[] templateBytes, Object context)
```

```java
default Set<String> extractPlaceholders(byte[] templateBytes)
```

### Metody — generowanie z InputStream

```java
default byte[] generate(InputStream templateStream, Map<String, Object> data)
```
- `templateStream` — strumień z zawartością .docx, nie null
- Caller odpowiada za zamknięcie strumienia po powrocie metody
- Rzuca: `DocumentGenerationException`, `IllegalArgumentException`, `UnsupportedOperationException`

```java
default byte[] generate(InputStream templateStream, Object context)
```

```java
default Set<String> extractPlaceholders(InputStream templateStream)
```

---

## PdfDocumentGenerator

**Pakiet:** `io.preboot.documents.pdf`
**Implementuje:** `DocumentGenerator`

Implementacja generująca PDF z szablonów DOCX. Obsługuje wszystkie 9 metod interfejsu (classpath, byte[], InputStream).

### Konstruktor

```java
public PdfDocumentGenerator(String templateBasePath)
```
- `templateBasePath` — ścieżka bazowa dla szablonów na classpath (np. `"/docx-templates/"`)
- Musi zaczynać się od `/` dla zasobów classpath
- Rzuca: `IllegalArgumentException` gdy null

### Thread safety

Klasa jest thread-safe. Każde wywołanie:
1. Ładuje świeży `WordprocessingMLPackage` (niezależna kopia szablonu)
2. Tworzy nowy `DocxStamper` (stamper ma mutable `ExpressionResolver` i `CommentProcessors`)
3. Konwertuje do PDF

### Pipeline generowania

1. `loadTemplate(source)` → `WordprocessingMLPackage`
2. `stampDocument(template, context)` → mutuje template in-place (nowy `DocxStamper` per call)
3. `convertToPdf(template)` → `byte[]` (docx4j + Apache FOP)

### Walidacja parametrów

| Parametr | Walidacja | Wyjątek |
|----------|-----------|---------|
| `templateName` = null | `IllegalArgumentException("Template name must not be null")` | |
| `data` = null | `IllegalArgumentException("Data map must not be null")` | |
| `context` = null | `IllegalArgumentException("Context must not be null")` | |
| `templateBytes` = null | `IllegalArgumentException("Template bytes must not be null")` | |
| `templateBytes` = empty | `IllegalArgumentException("Template bytes must not be empty")` | |
| `templateStream` = null | `IllegalArgumentException("Template stream must not be null")` | |

### Obsługa błędów szablonów

| Źródło | Brak szablonu | Uszkodzony szablon |
|--------|--------------|-------------------|
| Classpath (String) | `TemplateNotFoundException` | `DocumentGenerationException` |
| byte[] | n/a | `DocumentGenerationException("corrupted or invalid")` |
| InputStream | n/a | `DocumentGenerationException("corrupted or invalid")` |

---

## Image

**Pakiet:** `io.preboot.documents`

Wrapper na dane obrazu do dynamicznego wstawiania w szablony DOCX.

### Factory methods

```java
static Image fromBytes(byte[] data, int widthInPixels, int heightInPixels)
```
- MIME type domyślny: `"image/png"`

```java
static Image fromBytes(byte[] data, int widthInPixels, int heightInPixels, String mimeType)
```

```java
static Image fromInputStream(InputStream inputStream, int widthInPixels, int heightInPixels)
```

```java
static Image fromInputStream(InputStream inputStream, int widthInPixels, int heightInPixels, String mimeType)
```

### Getters

```java
byte[] getData()
int getWidthInPixels()
int getHeightInPixels()
String getMimeType()
```

### Użycie w szablonie

W szablonie DOCX: `${logo}` — placeholder zostanie zastąpiony obrazem o podanych wymiarach.

---

## Wyjątki

### TemplateNotFoundException

**Pakiet:** `io.preboot.documents`
**Extends:** `RuntimeException`

Rzucany gdy szablon nie został znaleziony na classpath. NIE rzucany dla byte[]/InputStream.

Message format: `"Template not found: <name> at path: <path>"`

### DocumentGenerationException

**Pakiet:** `io.preboot.documents`
**Extends:** `RuntimeException`

Rzucany gdy:
- Szablon jest uszkodzony lub nieprawidłowy
- Konwersja PDF się nie powiodła
- Błąd I/O podczas ładowania szablonu

---

## Auto-konfiguracja

### PrebootDocumentsPdfAutoConfiguration

**Pakiet:** `io.preboot.documents.pdf`

Automatycznie rejestrowana przez Spring Boot (META-INF/spring/AutoConfiguration.imports).

Tworzy bean `PdfDocumentGenerator` gdy:
- `@ConditionalOnMissingBean(DocumentGenerator.class)` — brak innego beanu DocumentGenerator

Konfiguracja przez `PrebootDocumentsPdfProperties`.

---

## Properties

### PrebootDocumentsPdfProperties

**Prefix:** `preboot.documents.pdf`

| Property | Typ | Domyślna wartość | Opis |
|----------|-----|-----------------|------|
| `template-base-path` | `String` | `/docx-templates/` | Ścieżka bazowa dla szablonów na classpath |

```yaml
preboot:
  documents:
    pdf:
      template-base-path: /my-templates/
```
