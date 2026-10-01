# 🏛️ Architecture & Design Patterns

## 1. Clean / Layered Architecture Overview

The backend uses a **Layered Architecture** (often referred to as Onion Architecture or Clean Architecture). The system is partitioned into clear, distinct layers, each with specific responsibilities and clear dependency directions.

```text
HTTP Request
     │
     ▼
┌────────────────────────────────────────────────────────┐
│ 1. Route Layer (FastAPI Routers)                       │
│    - Handles HTTP methods, query params, status codes  │
│    - Validates request body with Pydantic Schemas      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Service Layer (Business Logic)                      │
│    - Implements business rules & validation logic      │
│    - Orchestrates data flow & timestamping             │
│    - Converts DB dicts to Pydantic DTOs                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Repository Layer (Data Access Abstraction)          │
│    - Encapsulates database queries (PyMongo Async)     │
│    - Converts Python types to BSON (Decimal128, Date)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Storage Layer (MongoDB & Redis)                     │
│    - Async MongoDB collections & Redis Cache key-values│
└────────────────────────────────────────────────────────┘
```

---

## 2. Models vs Schemas

A foundational design principle in FastAPI applications is distinguishing **Database Models** from **API Schemas**.

### Schemas (`DB/schemas.py`)
Describes data passed over HTTP (API Request & Response DTOs). Uses Pydantic for automatic validation, type coercion, and JSON serialization.

- `CreateMedicine`: Input schema for POST `/medicines`
- `ReadMedicine`: Output schema for returning medicine records
- `UpdateMedicine`: Input schema for PATCH `/medicines/{id}` with optional fields (`exclude_unset=True`)

### Models (`DB/models.py` & MongoDB BSON Documents)
Describes data storage structures in MongoDB.

```text
POST /medicines
       │
       ▼
CreateMedicine (Schema: API Input)
       │
       ▼
MedicineService (Adds timestamps & validates)
       │
       ▼
MedicineRepository (Converts Decimal -> Decimal128, date -> datetime)
       │
       ▼
MongoDB Collection Document (Storage)
```

**Golden Rule:**
- **Schema** $\rightarrow$ API Boundary (HTTP Validation & Response Formatting)
- **Model / BSON Document** $\rightarrow$ Database Boundary (Persistence & Storage)

---

## 3. Separation of Responsibilities

| Component | Responsibility Question | Primary Responsibilities |
| :--- | :--- | :--- |
| **Route** | *"How do I expose this operation over HTTP?"* | URL routes, HTTP verbs, status codes, query/path parameter parsing, dependency injection. |
| **Service** | *"What business rules and logic apply to this operation?"* | Business validation, combining operations, computing fields, mapping DB models to DTOs. |
| **Repository** | *"How do I execute queries against MongoDB?"* | PyMongo query execution (`find_one`, `insert_one`), BSON type conversions (`Decimal128`). |
| **Database** | *"Where is data persisted?"* | Document storage, indexes, transaction logs. |

---

## 4. Evolution of Architecture (Refactoring Journey)

### Legacy Flow (Before Refactoring)
```text
Route  ──►  Service  ──►  MongoDB Collection
```
*Issue*: Services were directly tightly coupled to PyMongo collection queries, making unit testing difficult and spreading database query logic across business methods.

### Current Refactored Flow
```text
Route  ──►  Service  ──►  Repository  ──►  MongoDB Collection
```
*Benefit*:
1. **Testability**: Service unit tests mock `MedicineRepository` instead of mocking PyMongo database drivers.
2. **Maintainability**: If MongoDB queries need optimization or indexing, changes are restricted strictly to the Repository layer.
3. **Decoupling**: Business logic in Services relies only on Python standard data types (`Decimal`, `date`, `dict`).
