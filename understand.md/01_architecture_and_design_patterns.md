# Architecture and Design Patterns

## Layered Clean Architecture

The system follows a four-tier clean architecture:

```text
Client Request
     │
     ▼
Route Layer (FastAPI APIRouter)
     │ - Path & query parameters
     │ - Request body validation (Pydantic)
     │ - HTTP status codes & response models
     ▼
Service Layer (Business Logic)
     │ - Business validation rules
     │ - Workflow coordination & timestamps
     │ - DTO mapping (BSON dict <-> Pydantic)
     ▼
Repository Layer (Data Access)
     │ - Encapsulates PyMongo AsyncCollection queries
     │ - BSON type conversions (Decimal128, datetime, ObjectId)
     ▼
Database (MongoDB & Redis)
```

## Schemas vs Models

- Schemas (`DB/schemas.py`): Pydantic models for API request validation and response serialization over HTTP.
- Models (`DB/models.py`): Document definitions and enumerations stored in MongoDB.

### Data Flow Example
```text
POST /medicines -> CreateMedicine (Schema) -> MedicineService -> MedicineRepository -> MongoDB Document
```

## Layer Responsibilities

| Layer | Responsibility | Example |
| :--- | :--- | :--- |
| Route | HTTP contract, URL endpoints, request parsing | `medicine_routes.py` |
| Service | Business rules, orchestration, exception triggers | `medicine_services.py` |
| Repository | Database query execution, BSON formatting | `medicine_repository.py` |
| Database | Data persistence | MongoDB `hospital_db` |

## Refactoring Tradeoffs

### Previous Pattern
- Services queried PyMongo collections directly.
- Testing required mocking database drivers directly in service unit tests.

### Current Pattern
- Services interact strictly with Repository abstractions.
- Repositories are injected via FastAPI dependencies.
- Unit tests mock Repository methods instead of database driver internals.
