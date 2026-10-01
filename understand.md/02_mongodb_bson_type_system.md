# MongoDB BSON Type System and Data Converters

## Type Mapping Overview

MongoDB uses BSON for document storage. Standard Python types require conversion at the database boundary:

| Python Type | BSON Type | Conversion Reason |
| :--- | :--- | :--- |
| `decimal.Decimal` | `bson.decimal128.Decimal128` | PyMongo raises BSON encoding error for Python `Decimal`. |
| `datetime.date` | `datetime.datetime` | BSON serializer requires timezone-aware datetime objects. |
| `str` (hex string) | `bson.objectid.ObjectId` | MongoDB primary key `_id` is a 12-byte binary ObjectId. |

## Repository Boundary Conversions

All BSON type conversions are encapsulated within the Repository layer.

### Write Conversion (Python -> BSON)
```python
# Repositories/medicine_repository.py

if "price" in medicine_data:
    medicine_data["price"] = Decimal128(medicine_data["price"])

if "expiry" in medicine_data and medicine_data["expiry"] is not None:
    medicine_data["expiry"] = datetime.combine(
        medicine_data["expiry"],
        time.min,
        tzinfo=timezone.utc,
    )
```

### Read Conversion (BSON -> Python DTO)
```python
# Services/medicine_services.py

@staticmethod
def _to_read_schema(medicine: dict) -> ReadMedicine:
    return ReadMedicine(
        id=str(medicine["_id"]),
        name=medicine.get("name", ""),
        quantity=medicine.get("quantity", 0),
        price=medicine["price"].to_decimal(),
        expiry=medicine["expiry"].date(),
        created_at=medicine.get("created_at"),
        updated_at=medicine.get("updated_at"),
    )
```

## Architectural Rationale

- Service Layer Independence: Business logic works strictly with standard Python types (`Decimal`, `date`).
- Storage Decoupling: Database-specific driver types (`Decimal128`) do not leak into application logic or API schemas.
- Invalid ID Isolation: Malformed `ObjectId` strings raise domain-specific `InvalidId` exceptions handled before hitting database drivers.
