
# Medicine Repository — Later Improvements

This file tracks improvements that are intentionally **not implemented yet**.

The current repository is kept simple while the project is being refactored.

---

## 1. Pagination for `get_all()`

### Current implementation

```python
def get_all(self) -> list[dict]:
    return list(self.collection.find())
````

This is acceptable while the medicine catalogue is small.

### Later

If the number of medicine documents becomes large, introduce pagination:

```python
def get_all(
    self,
    skip: int,
    limit: int,
) -> list[dict]:
    return list(
        self.collection
        .find()
        .skip(skip)
        .limit(limit)
    )
```

The API can eventually expose something like:

```text
GET /medicines?page=1&limit=20
```

### Why?

Fetching the entire collection into memory does not scale well.

We should introduce pagination when the application actually needs it rather than adding unnecessary complexity now.

---

## 2. Revisit MongoDB indexing and search

### Current implementation

Medicine search currently uses a case-insensitive regex:

```python
def search(self, query: str) -> list[dict]:
    return list(
        self.collection.find({
            "name": {
                "$regex": query,
                "$options": "i",
            }
        })
    )
```

This is acceptable for the current project size.

### Later

If the medicine catalogue becomes large, revisit how MongoDB indexing/search should work.

Possible areas to investigate:

* Indexing the `name` field
* Whether the current regex query can use an index efficiently
* MongoDB text indexes
* Prefix-search strategies
* Case-insensitive search
* Query performance using `explain()`
* Whether a dedicated search solution is actually necessary

### Important

Do **not** add indexes blindly.

First identify the actual query patterns and measure performance.

---

## 3. Revisit `get_by_name()` and uniqueness

### Current implementation

```python
def get_by_name(
    self,
    name: str,
) -> Optional[dict]:
    return self.collection.find_one({
        "name": name
    })
```

### Later

Consider enforcing medicine-name uniqueness at the MongoDB level with a unique index.

This is preferable to relying only on:

```text
check if exists
        ↓
insert
```

because two concurrent requests could both pass the existence check.

MongoDB should ultimately enforce the uniqueness constraint.

---

## 4. Revisit `delete()`

### Current implementation

```python
def delete(
    self,
    medicine_id: ObjectId,
) -> bool:

    result = self.collection.delete_one({
        "_id": medicine_id
    })

    return result.deleted_count > 0
```

This is acceptable for the current stage.

### Later

Once other parts of the application depend on Medicine records, reconsider whether physical deletion is appropriate.

Potential alternative:

```text
deactivate medicine
```

instead of permanently deleting the document.

This decision should be made when the Medicine entity becomes referenced by other domains.

---

## 5. Repository error handling

### Current approach

The repository allows meaningful database exceptions to propagate.

We should **not** add generic:

```python
try:
    ...
except Exception:
    ...
```

blocks around every repository method.

### Later

Introduce centralized database error handling if the application needs it.

The goal should be to distinguish:

```text
Database error
Validation error
Not found
Duplicate/conflict
Unexpected application error
```

without duplicating error-handling logic across repository methods.

---

## Current Repository Contract

For now, keep the repository limited to:

```text
MedicineRepository
├── create()
├── get_by_id()
├── get_by_name()
├── get_all()
├── search()
├── update()
└── delete()
```

Do not add additional methods unless a concrete application requirement requires them.

---

## Current Decision

The repository is intentionally simple.

We will revisit the improvements above when they become relevant instead of prematurely optimizing the Medicine module.



