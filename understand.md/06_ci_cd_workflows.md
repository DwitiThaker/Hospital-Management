# CI/CD Pipeline and DevOps Workflows

## Workflow Overview

Continuous Integration and Continuous Deployment (CI/CD) automated via GitHub Actions workflows.

## Pipeline Architecture

```text
Git Push / Pull Request (main)
  │
  ├── Job 1: Code Quality & Linting (Flake8 / Black / Ruff)
  │
  ├── Job 2: Automated Testing (Pytest with Mock MongoDB/Redis)
  │
  └── Job 3: Build & Verification (Containerization check)
```

## GitHub Actions Job Definition (.github/workflows/ci.yml)

- Trigger: Push or Pull Request to `main` branch.
- Environment: Ubuntu-latest runner, Python 3.11+.
- Dependencies: Installed via `requirements.txt`.
- Verification Steps:
  1. Lint code formatting.
  2. Execute test suite: `pytest --maxfail=1 --disable-warnings`.
