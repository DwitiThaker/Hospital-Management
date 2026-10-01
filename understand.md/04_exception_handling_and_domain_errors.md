# 🚨 Custom Exception Handling & Domain Error Mapping

## 1. The Strategy: Domain Errors over Generic HTTP Exceptions

In generic FastAPI applications, developer code often raises `HTTPException` directly inside business services:

```python
# ❌ Anti-pattern: Business logic tied directly to HTTP details
if not medicine:
    raise HTTPException(status_code=404, detail="Medicine not found")
```

**Why is this an anti-pattern?**
- Business services become tightly coupled to the HTTP protocol.
- Business logic cannot be reused in non-HTTP contexts (e.g., CLI tools, background workers, gRPC services).
- HTTP response formatting is scattered across service methods instead of centralized.

### Our Strategy: Custom Domain Exceptions

```python
# ✅ Recommended pattern: Business logic raises clean domain exceptions
if not medicine:
    raise MedicineNotFoundError(medicine_id)
```

---

## 2. Exception Hierarchy & Structure

Domain exceptions are defined in `exceptions/`:

```text
exceptions/
├── medicine.py     -> MedicineNotFoundError, InvalidMedicineIdError, EmptyMedicineUpdateError
├── patient.py      -> PatientNotFoundError, InvalidPatientIdError, EmptyPatientUpdateError
├── prescription.py -> PrescriptionNotFoundError, InvalidPrescriptionIdError, EmptyPrescriptionUpdateError
└── handlers.py     -> FastAPI Exception Handler Functions
```

### Domain Exception Definition Example
```python
# exceptions/medicine.py

class MedicineNotFoundError(Exception):
    def __init__(self, medicine_id: str):
        self.medicine_id = medicine_id
        super().__init__(f"Medicine with id '{medicine_id}' not found")
```

---

## 3. Centralized Exception Mapping (`exceptions/handlers.py`)

Centralized handler functions convert domain exceptions into structured JSON HTTP responses:

```python
# exceptions/handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def medicine_not_found_handler(request: Request, exc: MedicineNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Medicine with id '{exc.medicine_id}' not found"},
    )

async def invalid_medicine_id_handler(request: Request, exc: InvalidMedicineIdError):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Invalid ObjectId format: '{exc.medicine_id}'"},
    )
```

---

## 4. Handler Registration in `main.py`

Handlers are registered on the FastAPI app instance at startup:

```python
# main.py

app.add_exception_handler(MedicineNotFoundError, medicine_not_found_handler)
app.add_exception_handler(InvalidMedicineIdError, invalid_medicine_id_handler)
app.add_exception_handler(EmptyMedicineUpdateError, empty_medicine_update_handler)
```

---

## 5. Request-Response Lifecycle Flow

```text
HTTP Request (GET /medicines/invalid-id)
       │
       ▼
Route Layer (calls MedicineService.get_medicine("invalid-id"))
       │
       ▼
Service Layer (attempts ObjectId("invalid-id") -> catches InvalidId)
       │
       ▼
Raises InvalidMedicineIdError (Domain Exception)
       │
       ▼
FastAPI Exception Middleware (Intercepts exception)
       │
       ▼
Executes invalid_medicine_id_handler(request, exc)
       │
       ▼
HTTP Response (Status 400 BAD REQUEST, JSON: {"detail": "Invalid ObjectId format: 'invalid-id'"})
```
