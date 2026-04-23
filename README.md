# PawPrints 2.0

Student Government President Ashley Carrington and Vice President Tyler Pierce (2014-2015) sought to improve engagement of RIT Students through a Petition site. The site creates a place for the RIT community to converse on important issues.

PawPrints 2.0 is a modernized rebuild of that platform, improving on the original with better feature additions, maintainability, testing, and overall design.

## Features

- Create, browse, and sign petitions
- Track petition status through its lifecycle (Active → Charged → Responded / Expired)
- Committee integration and filtering
- Role-based access control and admin management
- Image/media uploads via S3-compatible storage
- SAML 2.0 authentication (RIT Shibboleth)

## Architecture

| Component  | Technology              | Default Port |
|------------|-------------------------|--------------|
| Frontend   | Next.js 16 / TypeScript | 3000         |
| Backend    | FastAPI / Python 3.11+  | 8000         |
| Database   | PostgreSQL              | 5432         |
| Storage    | MinIO (S3-compatible)   | 9000 / 9001  |
| pgAdmin    | pgAdmin 4               | 8080         |

For detailed architecture documentation, refer to the project wiki.

## Prerequisites

**Recommended (Docker):** Docker and Docker Compose

**Manual setup:** Node.js 18+, Python 3.11+, PostgreSQL, MinIO

## Environment Setup

Copy the example env files and fill in your values:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### Key backend variables (`backend/.env`)

| Variable | Description |
|---|---|
| `MODE` | `DEV` or `PROD` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database credentials |
| `POSTGRES_HOST` | `postgres` for Docker, `localhost` for manual |
| `JWT_SECRET` / `SECRET_KEY` | Secure random strings for token signing |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | MinIO credentials |
| `FRONTEND_URL` | URL of the frontend (e.g. `http://localhost:3000`) |
| `DEV_USERNAME` | Username used in DEV mode to bypass SAML auth |
| `ENTRY_POINT` / `IDP_METADATA_PATH` | SAML IdP configuration (production only) |

### Key frontend variables (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend URL (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_ALWAYS_LOGGED_IN` | Set `true` in dev to skip auth |
| `APP_COOKIE` | Cookie name (must match `AUTH_COOKIE_NAME` in backend) |

## Running with Docker Compose (Recommended)

```bash
cd backend
docker compose up
```

This starts the backend, frontend, PostgreSQL, MinIO, and pgAdmin together. The frontend will be available at `http://localhost:3000`.

## Running Manually

### Backend

```bash
cd backend
uv sync --all-groups       # install dependencies
uvicorn pawprints.main:app --reload --port 8001
```

API docs (DEV mode only): `http://localhost:8001/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`.

## Authentication (SAML)

In `DEV` mode, SAML is bypassed — set `DEV_USERNAME` in `backend/.env` to the username you want to log in as, and `NEXT_PUBLIC_ALWAYS_LOGGED_IN=true` in the frontend env.

For production, SAML certificates and IdP metadata are required. See [`backend/README.md`](backend/README.md) for certificate generation instructions.

## Useful Commands

### Backend

```bash
make fmt      # format code (ruff + black)
make lint     # lint with ruff
make test     # run test suite
make check    # run all pre-commit checks
```

### Frontend

```bash
npm run dev     # development server
npm run build   # production build
npm run lint    # lint
```
