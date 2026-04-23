# Contributing to Pawprints 2.0

---

## Development Setup

1. Clone the repository
   ```bash
   git clone <repo-url>
   cd pawprints2
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Install pre-commit

   ```bash
   pip install pre-commit ruff black detect-secrets pytest
   pre-commit install
   ```

---

## Pre-Commit Hooks

This project uses `pre-commit` to enforce consistent style and quality.

Hooks include:

* **ruff** – linting and import sorting
* **black** – code formatting
* **pyupgrade** – modern Python syntax
* **detect-secrets** – secret scanning
* **trailing-whitespace / end-of-file-fixer** – code hygiene
* **codespell** – spell checking
* **hadolint / shellcheck** – Dockerfile and shell script linting

Run hooks on all files before committing:

```bash
pre-commit run --all-files
```

---

## Workflow

1. **Create a branch** for your work:

   ```bash
   git checkout -b feature/your-feature
   ```

2. **Format and lint**:

   ```bash
   make fmt
   make lint
   ```

3. **Run tests** (when applicable):

   ```bash
   pytest
   ```

4. **Commit with hooks enabled**:

   ```bash
   git add .
   git commit -m "Add feature: your-feature"
   ```

5. **Open a Pull Request** against `main`.

---

## Pull Request Guidelines

* Keep PRs small and focused.
* Include tests where relevant.
* Ensure CI passes (pre-commit, build, tests).
* Add documentation for new features or changes.

---

## Certificate Setup

If your contribution involves SAML configuration, ensure certificates are set correctly:

* Service Provider certs: `cert/ssl/saml.key` and `cert/ssl/saml.crt`
* Identity Provider cert: `cert/ssl/cert_idp.pem`

For reference, see `certificate.png` in this repository.

---

## Questions

If you encounter issues, please open a GitHub issue or reach out via the project maintainers.
