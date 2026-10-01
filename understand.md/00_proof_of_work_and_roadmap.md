# Hospital Management Backend - System Overview & Development Roadmap

## System Scope
- Healthcare backend managing Patient profiles, Medicine inventory, Doctor prescriptions, and Staff authentication.
- Stack: FastAPI, Async PyMongo (MongoDB), Redis, Pydantic v2, Pytest.

## Implemented Architecture
- Layered Separation: Route -> Service -> Repository -> Database.
- Data Access Layer: Encapsulates AsyncCollection operations and handles BSON type conversions (Decimal128, datetime, ObjectId) at the repository boundary.
- Exception Handling: Domain exceptions raised in services and mapped to HTTP status codes via FastAPI global exception handlers.
- Security: OAuth2 JWT token verification, bcrypt password hashing, role-based route access decorators.

## Current System Status
- Domain Endpoints: Patients, Medicines, Prescriptions, Staff/Users.
- Repository Isolation: Queries decoupled from business logic and HTTP routing.
- Service Layer: Business validations, timestamp generation, conversion between BSON dicts and Pydantic DTOs.
- Test Coverage: Pytest async test suite targeting repositories and service methods with mock fixtures.

## Engineering Roadmap & Next Tasks

### 1. Database Indexing & Query Optimization
- Enforce unique index on medicine name at MongoDB level.
- Create compound index on patient_id and issued_at for prescription search performance.
- Analyze query execution plans using explain() to ensure index hits.

### 2. API Pagination
- Add offset pagination (skip and limit parameters) to list endpoints.
- Transition high-volume reads to cursor-based pagination using ObjectId.

### 3. Caching & State Management (Redis)
- Implement cache-aside pattern for GET /medicines/{id}.
- Set key expiration (TTL) for cached reads.
- Implement cache invalidation on update and delete operations.

### 4. API Security & Rate Limiting
- Implement custom ASGI middleware for rate limiting using Redis.
- Use sliding window algorithm per client IP and authenticated user token.

### 5. Data Integrity & Audit History
- Implement soft delete pattern (deleted_at field) for patient and medicine records.
- Update repository queries to filter out soft-deleted documents by default.

### 6. Asynchronous Task Processing
- Offload non-blocking tasks (notifications, reports) to background workers.
