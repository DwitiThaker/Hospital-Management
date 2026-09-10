# GitHub Actions Workflows — What We Learned

## 1. What is CI?

**Continuous Integration (CI)** means automatically checking our code when changes are pushed to GitHub.

Our basic flow is:

```text
Change code
   ↓
Commit
   ↓
Push to GitHub
   ↓
GitHub Actions runs
   ↓
Check the code
   ↓
Pass / Fail
```

---

## 2. What is a GitHub Actions Workflow?

A **workflow** is a set of instructions that tells GitHub:

> When something happens, run these steps.

Workflow files are stored inside:

```text
.github/workflows/
```

Our first workflow is:

```text
.github/workflows/ci.yml
```

---

## 3. `name`

```yaml
name: CI
```

This is simply the name GitHub displays for the workflow.

It does not control how the workflow runs.

---

## 4. `on`

```yaml
on:
  push:
```

`on` defines **when the workflow should run**.

Our first workflow runs whenever code is pushed to GitHub.

We also learned that we can later add:

```yaml
on:
  push:
  pull_request:
```

to run CI for both pushes and pull requests.

---

## 5. `jobs`

```yaml
jobs:
  checks:
```

A **job** is one unit of work inside a workflow.

A workflow can contain multiple jobs:

```text
CI
├── checks
├── tests
└── build
```

Our current workflow has one job called `checks`.

---

## 6. `runs-on`

```yaml
runs-on: ubuntu-latest
```

This tells GitHub which **runner** should execute the job.

GitHub creates a temporary Ubuntu machine for the job.

```text
GitHub
   ↓
Temporary Ubuntu runner
   ↓
Run our workflow
   ↓
Runner is discarded
```

This is why CI needs to explicitly prepare its environment.

---

## 7. `steps`

```yaml
steps:
```

A job is made up of individual **steps**.

Our workflow currently performs:

```text
Checkout code
      ↓
Set up Python
      ↓
Install dependencies
      ↓
Check Python syntax
```

---

## 8. `uses`

Example:

```yaml
uses: actions/checkout@v4
```

`uses` means:

> Use an existing GitHub Action.

We used:

```yaml
actions/checkout@v4
```

to get our repository's code onto the GitHub runner.

We also used:

```yaml
actions/setup-python@v5
```

to configure Python.

---

## 9. `run`

Example:

```yaml
run: pip install -r requirements.txt
```

`run` means:

> Execute this command on the runner.

We used it to install our project's dependencies.

---

## 10. Python setup

Our project uses Python 3.14, so CI uses:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.14"
```

This keeps the CI Python version aligned with our development environment.

---

## 11. `requirements.txt`

We created:

```text
requirements.txt
```

using our existing environment.

CI uses it with:

```yaml
- name: Install dependencies
  run: pip install -r requirements.txt
```

This gives the fresh runner the Python packages our project needs.

---

## 12. Checking Python syntax

Our first automated check is:

```yaml
- name: Check Python syntax
  run: python -m compileall .
```

`compileall` checks that Python files can be compiled successfully.

If there is a syntax error, the CI job fails.

This is a **basic check**, not a replacement for proper automated tests.

---

## 13. Our current workflow

At this stage, our `ci.yml` looks like:

```yaml
name: CI

on:
  push:

jobs:
  checks:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Check Python syntax
        run: python -m compileall .
```

---

## 14. The most important concepts

Remember these five:

| Concept | Meaning |
|---|---|
| `workflow` | The complete automation |
| `on` | When it runs |
| `job` | A unit of work |
| `step` | One action/command inside a job |
| `runner` | The machine executing the job |

And remember:

```yaml
uses:
```

→ use an existing action

```yaml
run:
```

→ execute a command

---

## What we built

We now have a working GitHub Actions CI pipeline that:

1. Starts when we push code.
2. Creates a fresh Ubuntu runner.
3. Checks out our repository.
4. Sets up Python 3.14.
5. Installs our dependencies.
6. Checks Python syntax.
7. Reports whether the workflow passed or failed.

Next, we can make the workflow more professional by adding **Pull Request triggers and branch rules**, and later build toward Docker and CD.
