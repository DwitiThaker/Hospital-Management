
# Sync vs Async — A Practical Guide

Understanding when to use synchronous vs asynchronous code is one of the most important concepts in backend development.

A common misconception is:

> **"Async is faster, so I should always use async."**

That's not correct.

The real question is:

> **What is my application doing while it waits?**

To understand this, let's start with a practical example.

---

# 1. A Simple Real-World Example

Imagine an online shopping website.

Two users are using the website at almost the same time.

### User A

User A searches for:

```text
"Black running shoes"
````

The backend needs to query a database.

For some reason, the database takes **2 seconds** to return the results.

### User B

At the same time, User B opens:

```text
"My Orders"
```

Their database query takes only **100 ms**.

Now we have two users competing for the server's attention.

This is where the difference between synchronous and asynchronous execution becomes important.

---

# 2. Synchronous Approach

A simplified synchronous backend might look like:

```text
Client
  ↓
API
  ↓
Sync Python
  ↓
MongoDB
```

Suppose User A's request reaches the server first.

```text
User A
   ↓
GET /products
   ↓
MongoDB
   ↓
WAIT 2 seconds
   ↓
Response
```

While the database operation is blocking that execution flow, User B's request may have to wait for an available worker/thread depending on the server configuration.

Conceptually:

```text
Time ───────────────────────────────────────>

User A:
Request
  │
  ├──────── Waiting for MongoDB ────────────┤
  │                                         │
  └────────────── Response ─────────────────┘

User B:
       Request
          │
          ├── waits for available execution
          │
          ├── MongoDB ──┤
          │             │
          └── Response ─┘
```

### Important

This does **not** mean that synchronous code always makes User B wait.

For example, a production server can use multiple threads or worker processes and handle other requests concurrently.

The important point is:

> A synchronous I/O operation blocks the current execution flow while it waits.

How much that matters depends on the server architecture, number of workers, traffic, and workload.

---

# 3. Asynchronous Approach

Now suppose we use:

```text
FastAPI
   ↓
Async Python
   ↓
Async MongoDB client
```

User A starts the database operation:

```text
User A
   ↓
GET /products
   ↓
await MongoDB
```

Instead of sitting there doing nothing while MongoDB responds, the asynchronous execution can suspend that task.

The server can work on other requests.

Conceptually:

```text
Time ───────────────────────────────────────>

User A:
Request
  │
  └──── await MongoDB ──────────────────────┐
                                            │
                                            │
User B:                                    │
       Request                              │
          │                                 │
          ├── MongoDB ──┤                   │
          │             │                   │
          └── Response ─┘                   │
                                            │
                                            ↓
                                  User A resumes
                                            │
                                            ↓
                                         Response
```

The important idea is:

> **While User A is waiting for I/O, the server can make progress on other work.**

---

# 4. What Does `await` Actually Mean?

Consider:

```python
async def get_products():
    products = await db.products.find(...)
    return products
```

The word `await` does **not** mean:

> "Stop the entire server."

It means roughly:

> "This task needs to wait for this asynchronous operation. While it is waiting, the event loop can work on other tasks."

Conceptually:

```text
Task A
  ↓
await database
  ↓
Task A pauses
  ↓
Task B runs
  ↓
Task C runs
  ↓
Database finishes
  ↓
Task A resumes
```

This is why async is useful for high-concurrency I/O-heavy applications.

---

# 5. What Is I/O?

I/O means **Input/Output**.

In backend development, common I/O operations include:

### Database

```text
MongoDB
PostgreSQL
MySQL
```

### Network

```text
HTTP APIs
Payment services
Authentication providers
```

### Storage

```text
S3
File systems
Object storage
```

### Other services

```text
Redis
Kafka
RabbitMQ
Email services
```

These operations often involve waiting for another system.

For example:

```text
FastAPI
   ↓
"Give me this user's data"
   ↓
MongoDB
   ↓
             WAIT
             WAIT
             WAIT
             ↓
"Here is the data"
```

The CPU isn't necessarily doing useful work during that waiting period.

Async allows the application to use that time more efficiently when there are other tasks to run.

---

# 6. What Is CPU-Bound Work?

CPU-bound work is different.

Here the application is actively using the CPU for computation.

Examples:

```text
Image processing
Video encoding
Large mathematical calculations
Machine learning inference
Large data transformations
Compression
```

For example:

```text
User A
  ↓
POST /process-video
  ↓
Decode video
  ↓
Process millions of frames
  ↓
Encode video
```

Suppose this takes 5 seconds because the CPU is busy.

Making the function:

```python
async def process_video():
    ...
```

does **not** automatically make it faster.

The problem isn't that we're waiting for I/O.

The CPU is actually busy.

For CPU-heavy work, we may instead use:

```text
API
 ↓
Task Queue
 ↓
Worker Process
 ↓
CPU-heavy work
```

---

# 7. The Most Important Difference

Do not remember:

```text
Sync = slow
Async = fast
```

That is an oversimplification.

Instead remember:

```text
SYNC

Start operation
      ↓
Wait for it to finish
      ↓
Continue
```

Whereas:

```text
ASYNC

Start operation
      ↓
Await I/O
      ↓
Do other useful work
      ↓
Return when I/O is ready
      ↓
Continue
```

The individual database query does not necessarily become faster just because it is asynchronous.

The benefit is **concurrency**.

---

# 8. One User vs Many Users

This is an important way to understand async.

Suppose there is only one user:

```text
User A
  ↓
MongoDB
  ↓
500 ms
  ↓
Response
```

Sync:

```text
~500 ms
```

Async:

```text
~500 ms
```

Async did not magically reduce the database's 500 ms response time.

Now imagine:

```text
User A
User B
User C
User D
...
User 10,000
```

and most requests are waiting for databases, APIs, Redis, or other network services.

Now asynchronous I/O can become much more valuable because the server can keep making progress on other requests while individual requests are waiting.

---

# 9. A More Realistic Example

Consider an e-commerce checkout.

User A clicks:

```text
"Place Order"
```

The backend may need to communicate with several systems:

```text
FastAPI
   │
   ├── MongoDB → check order
   │
   ├── Inventory Service → reserve item
   │
   ├── Payment API → process payment
   │
   └── Email Service → send confirmation
```

These are mostly I/O operations.

At the same time, User B might be:

```text
Browsing products
```

and User C might be:

```text
Checking order history
```

An asynchronous architecture is attractive because the application spends a lot of time waiting for external systems.

---

# 10. Async Does Not Mean "Everything Must Be Async"

This is another common mistake.

You might have:

```text
FastAPI
   │
   ├── Async MongoDB
   ├── Async Redis
   ├── Async HTTP client
   │
   └── Background Worker
          ↓
       CPU-heavy task
```

This is perfectly reasonable.

Different types of work can use different execution models.

---

# 11. Common Architectures

## Fully synchronous

```text
API
 ↓
Sync Service
 ↓
Sync Database
```

Good when:

* The application is relatively simple.
* Concurrency requirements are modest.
* Most dependencies are synchronous.
* Async would add complexity without solving an actual problem.

---

## Async API + Async I/O

```text
FastAPI
   ↓
Async Services
   ↓
Async MongoDB
Async Redis
Async HTTP
```

Good when:

* The application is I/O-heavy.
* There can be many concurrent requests.
* Most important dependencies have good async support.
* Efficient I/O concurrency matters.

---

## Async API + Background Workers

```text
             FastAPI
                │
        ┌───────┴────────┐
        ↓                ↓
    Async I/O          Queue
                          ↓
                       Worker
                          ↓
                   Heavy processing
```

Good when:

* API requests need to remain responsive.
* Some work is long-running.
* Some work is CPU-heavy.
* Tasks can be processed separately from the request.

---

# 12. How Do Senior Engineers Decide?

A senior engineer usually doesn't start with:

> "Should we use async?"

They start with:

> **"What problem are we solving?"**

Then they investigate.

### 1. What is the workload?

Is it:

```text
CPU-bound?
I/O-bound?
```

### 2. How much concurrency do we need?

Ask:

```text
How many simultaneous requests?
How many users?
How many database connections?
What traffic do we expect?
```

### 3. Where is the bottleneck?

Measure before optimizing.

Possible bottlenecks:

```text
CPU
Database
Network
External API
Memory
Disk
Lock contention
```

### 4. How much time is spent waiting?

If requests spend a large amount of time waiting for network I/O, async becomes more attractive.

### 5. Do our dependencies support async?

For example:

```text
MongoDB      → async client available
Redis       → async clients available
HTTP        → async clients available
```

If critical dependencies are synchronous, that affects the decision.

### 6. Is the added complexity worth it?

Async introduces concepts such as:

```text
event loop
coroutines
await
async context managers
blocking calls
cancellation
timeouts
```

If the application is tiny and low-traffic, this complexity may not be justified.

### 7. What will the system look like at 10× the current scale?

A design should consider realistic growth, but shouldn't be over-engineered for imaginary traffic.

---

# 13. A Practical Decision Tree

Use this as a quick reference:

```text
                 What does my application do?
                           │
             ┌─────────────┴─────────────┐
             ↓                           ↓
        Mostly CPU work             Mostly I/O work
             │                           │
             ↓                           ↓
       Optimize CPU              How much concurrency?
                                         │
                              ┌──────────┴──────────┐
                              ↓                     ↓
                         Low / Moderate            High
                              │                     │
                              ↓                     ↓
                         Sync may be            Async may be
                         sufficient             beneficial
```

Then ask:

```text
Do the important dependencies
support async properly?
            │
       ┌────┴────┐
       ↓         ↓
      Yes       No
       │         │
       ↓         ↓
     Async    Reconsider
```

Finally:

```text
Does async solve a real problem?
            │
       ┌────┴────┐
       ↓         ↓
      Yes       No
       │         │
       ↓         ↓
     Use it   Keep it simple
```

---

# 14. Quick Comparison

| Question                     | Sync                     | Async                    |
| ---------------------------- | ------------------------ | ------------------------ |
| Simple application?          | Excellent                | May be unnecessary       |
| Low concurrency?             | Usually sufficient       | May be unnecessary       |
| I/O-heavy workload?          | Can work                 | Often attractive         |
| High concurrent I/O?         | Requires careful scaling | Strong fit               |
| CPU-heavy work?              | Not necessarily better   | Not a solution by itself |
| Easy to understand?          | Generally simpler        | More concepts            |
| Async dependencies required? | No                       | Yes, ideally             |
| Main advantage               | Simplicity               | I/O concurrency          |

---

# 15. Applying This to Our Hospital Management Project

Our project is evolving toward:

```text
FastAPI
   │
   ├── MongoDB
   ├── Redis
   ├── Google OAuth
   ├── S3
   ├── Email service
   ├── Notifications
   └── Background workers
```

A significant part of the application will involve network I/O.

For example:

```text
Patient books appointment
        │
        ├── MongoDB
        │
        ├── Redis
        │
        ├── Notification service
        │
        └── Email service
```

Therefore, an asynchronous FastAPI application with asynchronous I/O clients is a reasonable choice.

But if we later have:

```text
Generate a large medical report
        ↓
Heavy processing
        ↓
PDF generation
```

we shouldn't simply make that function `async`.

We may instead use:

```text
FastAPI
   ↓
Queue
   ↓
Background Worker
   ↓
Generate report
```

The important thing is that **we choose the execution model based on the work being performed.**

---
