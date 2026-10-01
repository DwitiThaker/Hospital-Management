# Domain Exception Handling Strategy

## Strategy Overview

The application uses custom domain exceptions raised in business services instead of embedding `HTTPException` inside business logic.

## Exception Structure (`exceptions/`)

```text
exceptions/
├── medicine.py     # MedicineNotFoundError, InvalidMedicineIdError, EmptyMedicineUpdateError
├── patient.py      # PatientNotFoundError, InvalidPatientIdError, EmptyPatientUpdateError
├── prescription.py # PrescriptionNotFoundError, InvalidPrescriptionIdError, EmptyPrescriptionUpdateError
└── handlers.py     # Centralized FastAPI exception handlers
```

## Exception Definition Example
```python
# exceptions/medicine.py

class MedicineNotFoundError(Exception):
    def __init__(self, medicine_id: str):
        self.medicine_id = medicine_id
        super().__init__(f"Medicine with id '{medicine_id}' not found")
```

## Centralized Exception Handlers (`exceptions/handlers.py`)

Handlers transform domain exceptions into standard JSON HTTP responses:

```python
# exceptions/handlers.py

async def medicine_not_found_handler(request: Request, exc: MedicineNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Medicine with id '{exc.medicine_id}' not found"},
    )
```

## Handler Registration (`main.py`)

```python
# main.py

app.add_exception_handler(MedicineNotFoundError, medicine_not_found_handler)
app.add_exception_handler(InvalidMedicineIdError, invalid_medicine_id_handler)
```

## Execution Flow

```text
Request GET /medicines/{id}
  -> MedicineService.get_medicine()
  -> Raises MedicineNotFoundError(id)
  -> FastAPI exception middleware catches exception
  -> medicine_not_found_handler executes
  -> Returns HTTP 404 JSON response
```
