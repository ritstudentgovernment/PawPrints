# Pawprints 2.0

Pawprints 2.0 is the next-generation platform for student government and campus engagement.
This repository contains the backend API, frontend application, and supporting services defined with Docker Compose.

UI Mockup: [Figma Prototype](https://www.figma.com/file/vKb2d7fARDnBXGfJfpmX0k/Pawprints-Mockup?type=design&node-id=0%3A1&mode=design&t=Aw7fPVgIAC5MhxBS-1)

---

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd pawprints2
````

### 2. Configure environment variables

Copy the example `.env` file and update it with your project-specific values:

```bash
cp .env.example .env
```

---

## Running the Project

This project uses Docker Compose to orchestrate services.

To build and start all containers:

```bash
docker compose up --build
```

Available services:

* **Postgres** – database (`localhost:5432`)
* **API** – FastAPI backend (`localhost:8000`)
* **Frontend** – Next.js frontend (`localhost:80`)

---

## Certificate Setup

Some integrations (such as SAML) require certificates.

### Install OpenSSL

* **Linux (Debian/Ubuntu)**

  ```bash
  sudo apt-get update
  sudo apt-get install openssl
  ```
* **Windows**

  1. Install [Git Bash](https://git-scm.com/downloads)
  2. Install [OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html)

### Generate Certificates

Create a directory and generate a new certificate:

```bash
mkdir -p cert/ssl
openssl req -x509 -newkey rsa:4096 -keyout cert/ssl/saml.key -out cert/ssl/saml.crt -nodes -days 900
```

When prompted, enter your organization details. Example:

```
Country Name (2 letter code): US
State or Province Name: California
Locality Name: San Francisco
Organization Name: ExampleCorp
Organizational Unit Name: IT
Common Name: example.com
Email Address: admin@example.com
```

Result:

* `cert/ssl/saml.key` – private key
* `cert/ssl/saml.crt` – self-signed certificate

### IdP Certificate

If using SAML, extract your Identity Provider (IdP) certificate:

1. Download IdP metadata (XML).
2. Copy the contents of the `<ds:X509Certificate>` tag.
3. Save it as `cert/ssl/cert_idp.pem` with the following format:

   ```
   -----BEGIN CERTIFICATE-----
   <certificate-contents-here>
   -----END CERTIFICATE-----
   ```



---

## Development Workflow

We use `pre-commit` hooks for code quality checks, including `ruff`, `black`, `detect-secrets`, and other standard linters.

### Local setup

```bash
pip install pre-commit ruff black detect-secrets
pre-commit install
pre-commit run --all-files
```

### Makefile commands

Common developer tasks are available via `make`:

* `make fmt` – auto-format code with ruff and black
* `make lint` – run ruff lint and hygiene checks
* `make check` – run all pre-commit hooks (CI equivalent)
* `make secrets-scan` – check repo for secrets
* `make docker-up` – run project with Docker Compose
* `make docker-down` – stop and clean containers

---

## Code Style and Contribution

* Python code is formatted with **black** and linted with **ruff**.
* Pre-commit ensures consistent quality for every commit.
* Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening pull requests.

---

## License

[MIT License](LICENSE)
