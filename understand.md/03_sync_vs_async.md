# Sync vs Async Concurrency Model

## Core Distinction

Synchronous and asynchronous models differ in how execution handles I/O waiting time (database queries, network requests, file I/O).

| Execution Mode | I/O Waiting Behavior | Worker Model |
| :--- | :--- | :--- |
| Synchronous | Blocks executing thread until I/O completes. | Requires multiple worker processes/threads (e.g. gunicorn workers). |
| Asynchronous | Yields control back to event loop during I/O. | Single-threaded event loop handles thousands of concurrent connections. |

## FastAPI Event Loop Mechanics

FastAPI runs on `uvicorn` (ASGI server) backed by an `asyncio` event loop.

- `async def` endpoints: Run directly on the event loop. Non-blocking async DB calls (`await collection.find_one()`) yield control to handle other incoming HTTP requests.
- `def` (sync) endpoints: Executed in an external thread pool by FastAPI to prevent blocking the main event loop.

## PyMongo Async Driver (`AsyncMongoClient`)

```python
# Non-blocking async MongoDB read
async def get_by_id(self, medicine_id: ObjectId) -> Optional[dict]:
    return await self.collection.find_one({"_id": medicine_id})
```

- When `await` is hit, python yields execution.
- The event loop processes other pending requests while waiting for MongoDB socket response.
