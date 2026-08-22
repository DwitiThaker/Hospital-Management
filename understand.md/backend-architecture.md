
# Backend Architecture

## 1. Models vs Schemas

### Models

Describe how data is stored in MongoDB.

```text
models/
├── User
├── Medicine
└── Prescription
````

### Schemas

Describe the data coming into or going out of the API.

```text
schemas/
├── CreateMedicine
├── ReadMedicine
├── CreatePrescription
└── ...
```

Example:

```text
POST /medicines
      ↓
CreateMedicine        ← API input
      ↓
Medicine Service
      ↓
MongoDB document      ← stored data
```

**Remember:**

> Schema → API
> Model → Database

---

## 2. Application Flow

### Current

```text
Route
  ↓
Service
  ↓
MongoDB
```

### Target

```text
Route
  ↓
Service
  ↓
Repository
  ↓
MongoDB
```

---

## 3. Separation of Responsibilities

### Route

> **"How do I expose this through HTTP?"**

Handles:

* URL
* HTTP method
* request/response
* dependencies

---

### Service

> **"What should the application do?"**

Handles:

* business logic
* validation of business rules
* combining multiple operations

---

### Repository

> **"How do I get/store this data?"**

Handles:

* MongoDB queries
* insert
* find
* update
* delete
* aggregation

---

### Simple Mental Model

```text
Route
  ↓
What does the client ask for?

Service
  ↓
What should the application do?

Repository
  ↓
How do I get/store the data?

MongoDB
  ↓
Where is the data?
```

**Rule:**

- Route = HTTP
- Service = Business Logic
- Repository = Database Access
- MongoDB = Storage


