# Hospital Management System - Technical Documentation Index

## Overview
Technical reference documentation for the Hospital Management System backend (FastAPI, Async MongoDB, Redis).

## Documentation Modules

- [00_proof_of_work_and_roadmap.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/00_proof_of_work_and_roadmap.md)
  System overview, current architectural status, and engineering roadmap.

- [01_architecture_and_design_patterns.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/01_architecture_and_design_patterns.md)
  Layered clean architecture breakdown, Repository pattern, and Schemas vs Models.

- [02_mongodb_bson_type_system.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/02_mongodb_bson_type_system.md)
  BSON type mapping (Decimal128, UTC datetime, ObjectId) and database boundary converters.

- [03_sync_vs_async.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/03_sync_vs_async.md)
  Asynchronous I/O execution model, event loops, and PyMongo AsyncCollection concurrency.

- [04_exception_handling_and_domain_errors.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/04_exception_handling_and_domain_errors.md)
  Custom domain exceptions and FastAPI exception handler registration.

- [05_authentication_and_rbac_middleware.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/05_authentication_and_rbac_middleware.md)
  JWT authentication, password hashing, and role-based access control decorators.

- [06_ci_cd_workflows.md](file:///c:/Users/Asus/Documents/fastapi/Hospital-Management/understand.md/06_ci_cd_workflows.md)
  GitHub Actions CI/CD pipeline, automated testing, and code quality workflows.
