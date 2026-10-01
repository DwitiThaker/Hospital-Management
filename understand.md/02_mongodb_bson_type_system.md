# 🍃 MongoDB BSON Type System & Data Converters

## 1. The Problem: Python Types vs BSON Representation

MongoDB stores data as **BSON** (Binary JSON). While Python native types map directly to JSON/BSON in most cases (e.g., `int`, `str`, `list`), certain core business data types require explicit conversion:

| Python Type | Native BSON Support? | Issue / Consequence | Solution / BSON Equivalent |
| :--- | :---: | :--- | :--- |
| `Decimal` | ❌ No | Python `decimal.Decimal` raises BSON encoding error when passed to PyMongo. | `bson.decimal128.Decimal128` |
| `date` | ❌ No | Python `datetime.date` cannot be directly encoded by BSON serializer. | `datetime.datetime` (combined with `time.min` & UTC timezone) |
| `ObjectId` | ⚠️ BSON Native | Mongo uses 12-byte `ObjectId` internally, but HTTP APIs expect a 24-character hexadecimal `str`. | `str(object_id)` $\leftrightarrow$ `ObjectId(id_str)` |

---

## 2. Type Conversion at the Repository Boundary

To maintain clean architecture, **database type conversions occur strictly within the Repository layer**.

### Write Operations (Python $\rightarrow$ BSON)
When writing data into MongoDB (`create`, `update`):

```python
# Repositories/medicine_repository.py

if "price" in medicine_data:
    # Convert Python Decimal to BSON Decimal128
    medicine_data["price"] = Decimal128(medicine_data["price"])

if "expiry" in medicine_data and medicine_data["expiry"] is not None:
    # Convert Python date to UTC datetime
    medicine_data["expiry"] = datetime.combine(
        medicine_data["expiry"],
        time.min,
        tzinfo=timezone.utc,
    )
```

### Read Operations (BSON $\rightarrow$ Python DTO)
When converting raw BSON documents returned by MongoDB into Pydantic Schemas (`Service` layer):

```python
# Services/medicine_services.py

@staticmethod
def _to_read_schema(medicine: dict) -> ReadMedicine:
    return ReadMedicine(
        id=str(medicine["_id"]),                            # ObjectId -> str
        name=medicine.get("name", ""),
        quantity=medicine.get("quantity", 0),
        price=medicine["price"].to_decimal(),                # Decimal128 -> Decimal
        expiry=medicine["expiry"].date(),                    # datetime -> date
        created_at=medicine.get("created_at"),
        updated_at=medicine.get("updated_at"),
    )
```

---

## 3. Why Keep Conversions at the Database Boundary?

```text
Route Layer  ──►  Service Layer  ──►  Repository Layer  ──►  MongoDB
 (HTTP JSON)     (Python Types:       (BSON Converters:        (BSON Storage)
                 Decimal, date)       Decimal128, datetime)
```

**Architectural Rationale:**
1. **Domain Purity**: The Service layer remains completely independent of database driver specifics (`bson.decimal128`).
2. **Prevent Leakage**: If MongoDB is replaced by PostgreSQL in the future, only the Repository layer changes; business services continue working with `decimal.Decimal` without modification.
3. **Safety**: Invalid string format conversions (e.g., malformed `ObjectId` strings) are caught early and translated to custom domain exceptions (`InvalidMedicineIdError`).
