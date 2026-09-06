# MongoDB Type Conversion

## What happened?

Our API uses normal Python types:

```text
price  → Decimal
expiry → date
```

But MongoDB/BSON cannot directly store these Python types.

So we got:

```text
Decimal → ❌ MongoDB
date    → ❌ MongoDB
```

`datetime` was already working, so we didn't change it.

## What did we do?

We convert the types in the **Repository**, because the Repository talks to MongoDB.

### Price

```text
Decimal → Decimal128
```

### Expiry

```text
date → datetime
```

MongoDB stores both successfully.

When reading the data back, we convert them back:

```text
Decimal128 → Decimal
datetime   → date
```

## Why Repository?

Our architecture is:

```text
Route → Service → Repository → MongoDB
```

The Service works with normal Python types.

The Repository handles MongoDB-specific types.

**Remember:**
Keep database-specific conversions at the database boundary.
