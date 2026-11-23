# SchedulingSoftware

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-SQLAlchemy%202-D71F00)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

REST API for appointment management in service businesses (healthcare, beauty, logistics…): providers, services, availability schedules, customers, and appointments with a full status history.

It is built with a real product in mind, so the focus is on **data integrity** and **business rules**: an appointment is only created if the provider offers the service, is available at that time in the business's time zone, and capacity is not exceeded — even under concurrent bookings.

---

## Table of contents

- [Features](#features)
- [Key technical decisions](#key-technical-decisions)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Data model](#data-model)
- [API](#api)
- [Getting started](#getting-started)
- [Development](#development)
- [Roadmap](#roadmap)

---

## Features

- **Businesses** with their own time zone (IANA) and currency (COP / USD).
- **Users and roles:** a person can belong to several businesses with different roles (admin, provider, or both).
- **Services** with duration, price, and concurrent-appointment capacity, offered by one or more providers.
- **Weekly availability** per provider, in the business's local time, with no overlapping blocks.
- **Per-business customers**, with or without a user account, including a record of personal-data consent.
- **Appointment booking** with full validation (service, provider, availability, capacity, dates).
- **Appointment lifecycle** with controlled status transitions and a history entry for every change.
- **Human-readable booking code** (`K7M-29Q`) to share with the customer.

## Key technical decisions

| Problem | Solution |
|---|---|
| Two simultaneous bookings could exceed capacity (*overbooking*) | The provider row is locked with `SELECT … FOR UPDATE` before counting overlapping appointments, so concurrent bookings for the same provider are serialized. |
| Appointments are points in time, but schedules are local "wall-clock" time | Appointments are stored as `TIMESTAMPTZ` (UTC) and availability as local `TIME`. To validate, the appointment is converted to the business's time zone (`zoneinfo`), which handles daylight saving time and businesses in different countries. |
| An appointment and its first history row must be saved together | Both are inserted in a single transaction: either both are saved or neither is. |
| Validation rules drifting out of sync | Each rule lives in two layers that state the same thing: PostgreSQL constraints (`CHECK`, `UNIQUE`, `NOT NULL`) as a safety net, and Pydantic to return a clear `422` message. |
| Unhelpful uniqueness errors | `UNIQUE` violations are mapped to `409` by constraint name; any other integrity violation is not hidden, so missing validations surface immediately. |
| Records with history that must never be lost | Soft deletes (`active`) and `ON DELETE RESTRICT` foreign keys. |
| One business's resources reachable from another | Nested routes (`/business/{business_id}/…`) and an ownership check on every operation: a resource from another business returns `404`, exactly like a non-existent one. |
| Guessable identifiers | UUID primary keys; the readable booking code is a separate field generated with `secrets`. |
| Schema evolution | Alembic migrations, version-controlled from day one; downgrades that would lose data stop with a clear message instead of deleting it. |

The full design decision log, with the reasoning behind each choice, is in [`backend/docs/DECISIONES.md`](backend/docs/DECISIONES.md) (Spanish).

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | FastAPI |
| ORM and models | SQLModel (SQLAlchemy 2 + Pydantic 2) |
| Database | PostgreSQL 17 on Docker |
| Driver | psycopg 3 |
| Migrations | Alembic |
| Configuration | pydantic-settings |
| API documentation | OpenAPI + Scalar |
| Code quality | Ruff (linting and formatting), Pyright (static type checking) |

## Architecture

Layered architecture, with a single clear responsibility per layer:

```
Router (HTTP)  →  Service (business rules)  →  Repository (data access)  →  PostgreSQL
```

- **Router:** defines the endpoints, validates input with `Create` / `Update` models and output with `Public` models.
- **Service:** enforces business rules and decides HTTP status codes. Receives its repositories through dependency injection.
- **Repository:** encapsulates SQL queries behind an abstract interface (`ABC`), so the implementation can be swapped in tests.

```
backend/
├── main.py                  # FastAPI entry point
├── alembic/                 # migrations
├── docs/                    # context, design decisions, and backlog
└── App/
    ├── config.py            # settings from environment variables
    ├── db/models/           # SQLModel models (table + Create / Public / Update)
    ├── repositories/        # data access: abstract interface + SQL implementation
    ├── service/             # business logic
    ├── dependencies/        # FastAPI dependency injection
    └── routers/             # endpoints, one per entity
```

## Data model

```mermaid
erDiagram
    BUSINESSES ||--o{ BUSINESS_MEMBERS : "has"
    USERS ||--o{ BUSINESS_MEMBERS : "is member"
    BUSINESSES ||--o{ SERVICES : "offers"
    BUSINESSES ||--o{ CUSTOMERS : "serves"
    USERS |o--o{ CUSTOMERS : "optional account"
    BUSINESS_MEMBERS ||--o{ AVAILABILITIES : "defines"
    BUSINESS_MEMBERS ||--o{ PROVIDER_SERVICES : "provides"
    SERVICES ||--o{ PROVIDER_SERVICES : "provided by"
    CUSTOMERS ||--o{ APPOINTMENTS : "books"
    BUSINESS_MEMBERS ||--o{ APPOINTMENTS : "attends"
    SERVICES ||--o{ APPOINTMENTS : "of type"
    APPOINTMENTS ||--o{ APPOINTMENTS_STATUS_HISTORY : "records"
```

**Appointment states:**

```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> confirmed
    pending --> canceled
    confirmed --> completed
    confirmed --> canceled
    completed --> [*]
    canceled --> [*]
```

## API

Interactive documentation (OpenAPI) is available at `/scalar` once the application is running.

| Resource | Base path | Operations |
|---|---|---|
| Businesses | `/business` | create, list, get, update |
| Users | `/users` | create, list, get, update |
| Members | `/business/{business_id}/members` | create, list, get, update |
| Services | `/business/{business_id}/services` | create, list, get, update |
| Service providers | `/business/{business_id}/services/{service_id}/providers` | add, list, remove |
| Availability | `/business/{business_id}/members/{member_id}/availabilities` | create, list, get, update |
| Customers | `/business/{business_id}/customer` | create, list, get, update |
| Appointments | `/business/{business_id}/appointments` | create, list (filter by status), get, change status, edit notes, history |

**Conventions:**

- Updates use `PATCH`: only the fields sent are modified.
- Every list endpoint is paginated: `limit` (1–100, default 50) and `offset`, with stable ordering.
- Errors share a single format:

| Code | When |
|---|---|
| `404` | The resource does not exist or does not belong to the business in the URL |
| `409` | Conflict with the current state: duplicate, inactive resource, no capacity left, transition not allowed |
| `422` | Invalid data |

### Example: booking an appointment

```http
POST /business/{business_id}/appointments/
Content-Type: application/json

{
  "client_id": "6f1c…",
  "provider_id": "a2b9…",
  "service_id": "d47e…",
  "starts_at": "2026-12-01T15:00:00-05:00",
  "notes": "First visit"
}
```

```json
{
  "id": "0c8d…",
  "booking_code": "K7M-29Q",
  "starts_at": "2026-12-01T20:00:00Z",
  "ends_at": "2026-12-01T20:45:00Z",
  "status": "pending",
  "client_id": "6f1c…",
  "provider_id": "a2b9…",
  "service_id": "d47e…",
  "notes": "First visit",
  "created_at": "2026-11-23T14:02:11Z",
  "updated_at": "2026-11-23T14:02:11Z"
}
```

`ends_at` is computed by the server from the service duration. If the provider is not available at that time:

```json
{ "detail": { "Error": "Provider is not available at that time" } }
```

## Getting started

**Requirements:** Python 3.13 and Docker.

```bash
# 1. Clone
git clone https://github.com/TeitanG/SchedulingSoftware.git
cd SchedulingSoftware

# 2. Database (PostgreSQL on local port 5433)
docker compose up -d

# 3. Virtual environment and dependencies
cd backend
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**4. Configuration.** The application reads its settings from `backend/.env`, which is excluded from the repository. Create it from the provided template (from `backend/`):

```bash
cp .env.example .env              # Windows: Copy-Item .env.example .env
```

For local development, matching the database defined in `docker-compose.yml`:

```env
DATABASE_URL=postgresql+psycopg://app:app@localhost:5433/scheduling
SQL_ECHO=false
```

These are the development-only credentials already defined in `docker-compose.yml`. `DATABASE_URL` is required (the application will not start without it); `SQL_ECHO=true` logs every SQL statement.

```bash
# 5. Migrations
alembic upgrade head

# 6. Run
uvicorn main:app --reload
```

The API runs at `http://localhost:8000` and its documentation at `http://localhost:8000/scalar`.

## Development

Development tools (Ruff, Pyright) are kept separate from the runtime dependencies. From `backend/`, with the virtual environment active:

```bash
pip install -r requirements-dev.txt   # runtime dependencies + dev tools
```

```bash
ruff check App          # linting

ruff format App         # formatting
pyright App             # static type checking
alembic check           # verify that models and database schema match
```

## Roadmap

- [x] Relational data model and migrations
- [x] Businesses, users, members, services, and providers
- [x] Weekly availability with overlap detection
- [x] Customers
- [x] Appointments: validated booking, statuses, and history
- [ ] Authentication and authorization with JWT
- [ ] Available-slots endpoint for booking
- [ ] Automated tests with pytest and continuous integration
- [ ] Frontend with React + TypeScript + Vite
