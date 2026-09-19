# Industry-Standard CI/CD Workflow for Our FastAPI Project

## 1. Goal

Our Hospital Management project is a FastAPI backend using MongoDB, Docker, and GitHub.

We want CI/CD to eventually automate this flow:

```text
Developer
   ↓
Feature branch
   ↓
Pull Request → main
   ↓
CI
   ├── install dependencies
   ├── code quality checks
   ├── tests
   └── build Docker image
   ↓
Merge to main
   ↓
CD
   ├── build production image
   ├── push image to container registry
   └── deploy to AWS
```

The important idea is:

- **CI** validates the code.
- **CD** delivers validated code to an environment.

GitHub Actions workflows live under:

```text
.github/workflows/
```

---

# 2. Recommended Repository Structure

Our project should eventually look roughly like:

```text
Hospital-Management/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── DB/
├── MongoDB/
├── Repositories/
├── Services/
├── Routes/
├── exceptions/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── ...
```

We do not need to create every part immediately. We will build the pipeline incrementally.

---

# 3. Branching Workflow

A practical workflow for this project:

```text
main
 │
 ├── feature/medicine
 ├── feature/prescription
 ├── feature/auth
 └── feature/billing
```

Development happens on a feature branch.

```text
feature branch
      ↓
     push
      ↓
Pull Request → main
      ↓
     CI
      ↓
  checks pass
      ↓
   merge
      ↓
    main
```

The `main` branch should be treated as the stable branch.

---

# 4. CI — Continuous Integration

CI answers:

> "Is this change safe to merge?"

For our FastAPI project, CI should eventually perform:

```text
Checkout code
      ↓
Set up Python
      ↓
Install dependencies
      ↓
Lint / format checks
      ↓
Automated tests
      ↓
Build Docker image
```

Not every check has to be added immediately. We should add them as the project matures.

---

# 5. Workflow Triggers

A basic CI workflow can run on:

```yaml
on:
  push:
  pull_request:
```

This means CI runs when:

- code is pushed
- a Pull Request is opened or updated

For a production-oriented workflow, we can later restrict Pull Requests to the `main` branch:

```yaml
on:
  push:
    branches:
      - main

  pull_request:
    branches:
      - main
```

GitHub Actions supports branch and path filters for workflow triggers.

---

# 6. Jobs and Runners

A workflow contains jobs:

```yaml
jobs:
  checks:
```

A job runs on a runner:

```yaml
runs-on: ubuntu-latest
```

Conceptually:

```text
GitHub
   ↓
creates temporary runner
   ↓
checkout repository
   ↓
prepare environment
   ↓
run job
   ↓
job finishes
   ↓
runner is discarded
```

This is why CI must explicitly prepare its environment.

---

# 7. Python Environment

Our project currently uses Python 3.14.

We should explicitly configure that in CI:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.14"
```

GitHub recommends using `setup-python` to make the Python version explicit and consistent.

When the project eventually standardizes its Python version in a project configuration file, CI should use that same source of truth.

---

# 8. Dependency Installation

We created:

```text
requirements.txt
```

CI installs it with:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

The important principle is:

> CI should install the dependencies declared by the project rather than maintaining a second dependency list inside the workflow.

---

# 9. Dependency Caching

Once the basic workflow is stable, we can enable pip caching through `setup-python`:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.14"
    cache: "pip"
```

This can make repeated workflow runs faster.

We should add caching after the basic pipeline is understood and working.

---

# 10. Code Quality

Before running tests, CI should eventually check code quality.

For example, we can use Ruff:

```text
ruff check
ruff format --check
```

The goal is to catch:

- unused imports
- common Python errors
- inconsistent formatting
- style problems

This is different from testing.

```text
Linting
→ Is the code written correctly according to our rules?

Testing
→ Does the application behave correctly?
```

---

# 11. Automated Tests

Our current pipeline deliberately does not depend on tests yet.

When we add pytest, CI should run something like:

```yaml
- name: Run tests
  run: pytest
```

Eventually:

```text
CI
├── lint
├── format check
├── tests
└── Docker build
```

A failed check should fail the workflow.

---

# 12. Docker Build

Our project already uses Docker, so Docker should become part of CI.

Eventually CI should verify that the application can actually be packaged:

```yaml
- name: Build Docker image
  run: docker build -t hospital-management .
```

This catches problems that Python-only checks cannot catch.

For example:

```text
Python code works locally
        ↓
Dockerfile is broken
        ↓
deployment would fail
```

CI should catch that before deployment.

---

# 13. CD — Continuous Delivery / Deployment

CD starts after CI.

Conceptually:

```text
Pull Request
     ↓
CI
     ↓
merge to main
     ↓
CD
     ↓
Docker image
     ↓
Container registry
     ↓
AWS
```

CI asks:

> "Can we safely ship this?"

CD asks:

> "How do we reliably ship it?"

---

# 14. Container Registry

The production Docker image should eventually be pushed to a container registry.

For example:

```text
GitHub
   ↓
Docker build
   ↓
Container image
   ↓
Container Registry
   ↓
AWS
```

For AWS, a natural choice is **Amazon ECR**.

The registry stores versioned container images that our deployment environment can pull.

---

# 15. AWS Deployment

The eventual deployment architecture could be:

```text
GitHub
   ↓
GitHub Actions
   ↓
CI checks
   ↓
Docker build
   ↓
Amazon ECR
   ↓
AWS deployment target
   ↓
FastAPI container
   ↓
MongoDB
```

The exact AWS service should be chosen later based on the project's requirements. We should not choose a deployment service simply because it is common.

---

# 16. Secrets and Environment Variables

Secrets must not be hard-coded in:

- Python code
- `ci.yml`
- Dockerfiles
- Git history

Examples include:

```text
MONGO_URI
JWT_SECRET
AWS credentials
API keys
```

GitHub Actions can access repository/environment secrets through:

```yaml
${{ secrets.SECRET_NAME }}
```

For production deployment, we should use the minimum permissions required.

---

# 17. Permissions

Workflows should follow the principle of least privilege.

For example:

```yaml
permissions:
  contents: read
```

This gives the workflow only the repository content permission it needs for a read-only CI job.

When CD is introduced, its permissions should be deliberately scoped to the deployment requirements.

---

# 18. Branch Protection

Eventually `main` should be protected.

A professional workflow is:

```text
Developer
   ↓
feature branch
   ↓
Pull Request
   ↓
CI
   ↓
all required checks pass
   ↓
review
   ↓
merge to main
```

The important distinction is:

```text
CI check
→ reports whether the code passes

Branch protection
→ can prevent merging when required checks fail
```

This turns CI into an actual quality gate.

---

# 19. Environments

For a more mature project, use separate environments:

```text
development
staging
production
```

A typical flow:

```text
feature branch
      ↓
CI
      ↓
main
      ↓
staging deployment
      ↓
verification
      ↓
production deployment
```

Production secrets should be separated from development/staging secrets.

---

# 20. What Our CI Should Become

We currently have a basic working workflow.

The target CI workflow is:

```text
Trigger
  ↓
Checkout
  ↓
Python 3.14
  ↓
Install dependencies
  ↓
Lint
  ↓
Format check
  ↓
Tests
  ↓
Docker build
  ↓
✅ Ready to merge
```

We should add these pieces incrementally rather than copying the entire workflow at once.

---

# 21. What Our CD Should Become

The eventual CD workflow:

```text
main
 ↓
CI passes
 ↓
Build Docker image
 ↓
Tag image
 ↓
Push to Amazon ECR
 ↓
Deploy to AWS
 ↓
Health check
 ↓
Deployment complete
```

A production system should also have a rollback strategy.

---

# 22. Current Project vs Target

### We have now

```text
GitHub Actions
      ↓
push / pull request
      ↓
Ubuntu runner
      ↓
Python 3.14
      ↓
requirements.txt
      ↓
Python syntax check
      ↓
✅
```

### We will build toward

```text
PR
 ↓
CI
 ├── lint
 ├── format
 ├── tests
 └── Docker build
 ↓
merge to main
 ↓
CD
 ├── Docker image
 ├── ECR
 └── AWS deployment
```

---

# 23. Learning Order

For this project, the recommended order is:

1. **Basic GitHub Actions workflow** — done
2. **Push + Pull Request triggers** — done
3. **Branch protection / required checks**
4. **Linting and formatting**
5. **Automated tests**
6. **Docker build in CI**
7. **Docker image tagging**
8. **Container registry**
9. **GitHub Actions secrets / permissions**
10. **AWS deployment**
11. **Staging / production environments**
12. **Health checks and rollback**

This keeps each new concept understandable and prevents the workflow from becoming a large YAML file that we don't understand.

---

## Key principle

Do not think of CI/CD as "a GitHub Actions YAML file."

Think of it as an engineering pipeline:

```text
Code
 ↓
Validate
 ↓
Test
 ↓
Package
 ↓
Publish
 ↓
Deploy
 ↓
Verify
```

GitHub Actions is simply the automation platform executing that pipeline.
