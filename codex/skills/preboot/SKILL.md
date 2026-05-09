---
name: preboot
description: >
  General PreBoot library guardrail and documentation router. Use whenever the
  user mentions PreBoot/preboot, the codebase contains PreBoot dependencies or
  imports, or the task references known PreBoot APIs such as TTLMap,
  RateLimiter, AccessSynchronizer, FilterableRepository, SearchParams,
  FilterCriteria, SecureRepository, @Tenant, @SecureAccess, EventPublisher,
  @EventHandler, AggregateRoot, AggregateRepository, TaskPublisher, TaskRunner,
  @Saga, SagaRunner, CompensationHandler, FileStorageService, SequenceApi,
  DocumentGenerator, or PdfDocumentGenerator. Do not trigger on generic domain
  wording unless an explicit PreBoot dependency/import/API signal is present.
---

# PreBoot

Use this skill when working with the PreBoot library ecosystem.

This skill does not contain PreBoot API documentation. The project is the source
of truth and must provide local docs under `./preboot-docs/`.

## Hard Rule

If the task requires PreBoot API knowledge, do not guess the API.

Before advising or editing code:
1. Detect the relevant PreBoot module or candidate modules.
2. Read the matching local documentation file under `./preboot-docs/`.
3. Only then answer, plan, or implement.

If the required local documentation is missing, stop and tell the user exactly
which file is missing.

## Documentation Contract

Expected project structure:

```text
preboot-docs/
├── index.md
├── preboot-core.md
├── preboot-query.md
├── preboot-securedata.md
├── preboot-eventbus.md
├── preboot-ddd.md
├── preboot-tasks.md
├── preboot-saga.md
├── preboot-files.md
├── preboot-sequence.md
└── preboot-documents-pdf.md
```

`index.md` is optional but recommended as a module/version map. Module files are
required when the corresponding PreBoot API is needed.

## Module Routing

Use this map to choose docs:

| Signals | Read |
|---------|------|
| `preboot-core`, `TTLMap`, `AccessSynchronizer`, `RateLimiter`, `TransactionWrapper`, `HashUtils`, `BeanValidator`, `JsonMapperFactory`, Jackson auto-configuration | `./preboot-docs/preboot-core.md` |
| `preboot-query`, `FilterableRepository`, `FilterableUuidRepository`, `FilterCriteria`, `SearchParams`, `SearchRequest`, `FilterableController`, dynamic filtering, pagination, sorting, CSV/XLSX export | `./preboot-docs/preboot-query.md` |
| `preboot-securedata`, `SecureRepository`, `SecureUuidRepository`, `@Tenant`, `@SecureAccess`, `@AccessRule`, `@CreatedBy`, `@CreatedAt`, `@ModifiedBy`, `@ModifiedAt`, tenant isolation, RBAC, audit fields | `./preboot-docs/preboot-securedata.md` |
| `preboot-eventbus`, `EventPublisher`, `@EventHandler`, `GenericEvent`, synchronous/asynchronous event publishing, handler priority | `./preboot-docs/preboot-eventbus.md` |
| `preboot-ddd`, `AggregateRoot`, `AggregateRepository`, `AggregateMapper`, `SoftDeletable`, domain events, snapshot pattern, aggregate persistence | `./preboot-docs/preboot-ddd.md` |
| `preboot-tasks`, `TaskPublisher`, `TaskRunner`, `TaskContext`, `BackOffPolicy`, `DeadQueuePolicy`, background jobs, persistent task queue, worker scaling | `./preboot-docs/preboot-tasks.md` |
| `preboot-saga`, `@Saga`, `@SagaStart`, `@SagaEventHandler`, `@CompensationHandler`, `SagaRunner`, `SagaPublisher`, `SagaContext`, compensation, orchestration | `./preboot-docs/preboot-saga.md` |
| `preboot-files`, `FileStorageService`, `FileContent`, `FileMetadata`, `FileFilter`, S3/MinIO/OVH object storage, file TTL, file REST API | `./preboot-docs/preboot-files.md` |
| `preboot-sequence`, `SequenceApi`, `SequenceTenantProvider`, `SequenceCounter`, document numbering, invoice number, contract number, masks, counters | `./preboot-docs/preboot-sequence.md` |
| `preboot-documents-pdf`, `DocumentGenerator`, `PdfDocumentGenerator`, DOCX to PDF, template stamping, placeholders, office-stamper, docx4j | `./preboot-docs/preboot-documents-pdf.md` |

If a task crosses modules, read every matching module file before acting.

## Detection

PreBoot is considered detected when at least one of these is true:
- the user explicitly mentions PreBoot or a `preboot-*` module
- build files contain a PreBoot dependency
- source code imports or references PreBoot packages, annotations, classes, or APIs
- the task references a known PreBoot class, annotation, or module name from the routing table

Avoid false positives:
- Generic words like `task`, `file`, `sequence`, `event`, `cache`, `document`, or `PDF` are not enough by themselves.
- For those generic words, require a PreBoot dependency/import/API signal before applying this skill.

## Missing Docs Response

If docs are missing, respond in this form and stop:

```text
Wykryłem użycie PreBoot (`[signal]`), ale nie znalazłem lokalnej dokumentacji:
`./preboot-docs/[module].md`.

Nie będę zgadywał API PreBoot. Dodaj ten plik albo wskaż właściwą dokumentację.
```

If multiple module docs are missing, list all missing files.

## Working Rules

- Read `./preboot-docs/index.md` first when it exists.
- Read the specific module docs before changing or recommending PreBoot code.
- Treat local docs as authoritative even if they differ from prior knowledge.
- Do not use old bundled module docs; they are intentionally not part of this skill.
- Do not create `preboot-docs/` automatically.
- Do not invent API names, Maven coordinates, configuration keys, annotations, or method signatures.
- If documentation is ambiguous, ask for clarification or inspect existing project usage.
