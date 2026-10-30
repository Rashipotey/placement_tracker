# IntelliSQL / Placement Tracker — Architecture

> **Scope:** This document describes the *current verified architecture* of the `placement_tracker` repository and proposes a *target architecture* for the approved enhancements (Application + Company CRUD, status tracking, minimal UI integration readiness).
>
> **Non-scope:** This repository is not IntelliSQL (Streamlit/SQLite/Gemini). The documents below apply to `placement_tracker` (FastAPI + SQLAlchemy + Postgres + JWT) as verified from the repo.

---

## 1. Repository verification

- **Repository:** `Rashipotey/placement_tracker`
- **Default branch:** `main`
- **Existing working branch:** `feature/auth` (contains auth + models)
- **Design branch for this proposal:** `feature/design-approved-enhancements`

---

## 2. Current architecture (verified)

### 2.1 System context

- **Client(s):** API clients via HTTP (Swagger UI at `/docs`, curl, Postman). No frontend code in repo.
- **Backend:** FastAPI application serving REST endpoints.
- **Database:** PostgreSQL via SQLAlchemy ORM.
- **Authentication:** JWT bearer token.

### 2.2 Verified technology stack

From `requirements.txt` and code:

- **Python** (runtime not pinned in repo)
- **FastAPI**
- **Uvicorn**
- **SQLAlchemy**
- **psycopg2-binary** (Postgres driver)
- **python-jose** (JWT)
- **passlib[bcrypt]** (password hashing)
- **pydantic / pydantic-settings** (configuration is present but not fully used consistently)

### 2.3 Code structure (as-is)

- `app/main.py`
  - Creates `FastAPI()` app
  - Calls `Base.metadata.create_all(bind=engine)`
  - Includes routers: `auth`, `users`
- `app/database/connection.py`
  - Loads `.env` via `dotenv`
  - Builds SQLAlchemy `engine` and `SessionLocal`
- `app/models/*`
  - SQLAlchemy models: `User`, `Company`, `Application`, `Round`
- `app/auth/*`
  - `router.py`: `/auth/register`, `/auth/login`
  - `dependencies.py`: resolves current user from JWT
  - `jwt_handler.py`: creates/decodes JWT (currently contains a hardcoded secret)
  - `security.py`: password hashing utilities
- `app/schemas/*`
  - `auth.py`, `user.py` exist
  - `company.py` and `application.py` are empty (incomplete)

### 2.4 Current data model (verified)

- `User`
  - `id: UUID` (primary key)
  - `name: str`
  - `email: str` (unique)
  - `hashed_password: str`
- `Company`
  - `id: UUID`
  - `name: str`
  - `role: str`
  - `location: str | None`
  - `package_lpa: float | None`
  - `application_link: str | None`
- `Application`
  - `id: UUID`
  - `user_id: UUID` (FK -> `users.id`)
  - `company_id: UUID` (FK -> `companies.id`)
  - `status: str` default `"APPLIED"`
  - `notes: str | None`
- `Round`
  - `id: UUID`
  - `application_id: UUID` (FK -> `applications.id`)
  - `round_name: str`
  - `status: str` default `"PENDING"`
  - `feedback: str | None`

### 2.5 Current request/response flow

1. **Register** `POST /auth/register`
   - Validates email uniqueness
   - Hashes password
   - Inserts user
2. **Login** `POST /auth/login`
   - Verifies password
   - Returns access token (JWT)
3. **Authenticated endpoint** `GET /users/me`
   - Reads JWT from Authorization header
   - Loads user from DB

### 2.6 Identified limitations (current)

- **Missing CRUD APIs** for Company and Application.
- **Empty schema modules** (`app/schemas/company.py`, `app/schemas/application.py`), so payload validation and response shaping for those domains is absent.
- **JWT config inconsistency**:
  - `jwt_handler.py` has hardcoded `SECRET_KEY` and `ALGORITHM`.
  - `database/connection.py` has `JWT_ALGORITHM` env variable but it is not used by JWT handler.
- **No authorization/ownership enforcement** beyond `users/me`.
- **No CORS middleware** for browser-based frontend integration.
- **No DB migrations**: `Base.metadata.create_all` is used on startup; schema evolution is manual.

---

## 3. Proposed target architecture (for approved enhancements)

### 3.1 Architectural goals

- Add **Company + Application CRUD** endpoints.
- Enforce **Application ownership** via `user_id` and JWT-based authentication.
- Implement **status validation** via a constrained set of allowed values.
- Keep stack consistent with existing implementation (FastAPI + SQLAlchemy + Postgres + JWT).
- Enable minimal frontend integration via **CORS** and stable API contracts.

### 3.2 Target component diagram

```mermaid
flowchart LR
  subgraph Client
    B[Browser / API Client]
  end

  subgraph API[FastAPI Backend]
    R1[Auth Router\n/register /login]
    R2[Users Router\n/me]
    R3[Companies Router\nCRUD]
    R4[Applications Router\nCRUD + ownership]

    S1[Auth Dependencies\nget_current_user]
    S2[Domain Services (thin)\nvalidation + policies]
    P1[Pydantic Schemas\nrequest/response]
    D1[SQLAlchemy Session\nSessionLocal]
    M1[ORM Models\nUser/Company/Application]
  end

  subgraph DB[PostgreSQL]
    T1[(users)]
    T2[(companies)]
    T3[(applications)]
  end

  B -->|HTTP JSON + Bearer JWT| API
  R1 --> D1
  R2 --> S1 --> D1
  R3 --> S1 --> D1
  R4 --> S1 --> S2 --> D1

  D1 --> M1 --> DB
  DB --> M1

  R3 --> P1
  R4 --> P1
```

### 3.3 Runtime behavior highlights

- **All Company/Application endpoints** require Authorization header: `Bearer <token>`.
- **Ownership rule**: For reads/writes on an application, require `application.user_id == current_user.id`.
- **Status policy**: Application `status` must be one of approved values (e.g., `APPLIED`, `INTERVIEW`, `OFFER`, `REJECTED`).

---

## 4. Component responsibilities

### 4.1 Routers (API layer)

- **Auth Router**
  - Registration: validate unique email, hash password, create user.
  - Login: verify password, issue JWT.
- **Users Router**
  - `GET /users/me`: return profile for authenticated user.
- **Companies Router (new)**
  - Create/list companies required to create applications.
- **Applications Router (new)**
  - CRUD for applications.
  - Enforce ownership and status validation.

### 4.2 Schemas (contract layer)

- Define request/response models to:
  - Normalize error responses
  - Ensure API contract is stable for future UI
  - Prevent clients from setting `user_id`

### 4.3 Services (policy/validation)

- Keep services thin:
  - Validate status transitions (optional for MVP)
  - Centralize ownership checks
  - Centralize company existence checks

### 4.4 Persistence (SQLAlchemy)

- Use `SessionLocal` per-request.
- DB schema managed via current `create_all` approach (no migrations in scope).

---

## 5. Security considerations

- **Authentication:** JWT bearer token required for protected endpoints.
- **Authorization:**
  - Application endpoints must enforce owner checks.
  - Company endpoints: current model lacks `user_id`; by default companies are global. If per-user company isolation is required, it becomes a schema change (out of scope for this design doc unless approved).
- **JWT secret management:**
  - Remove hardcoded secret in production; load from environment.
  - Maintain consistent algorithm configuration.
- **Password hashing:** `bcrypt` via passlib.
- **Input validation:** Pydantic schemas + status enum.
- **CORS:** enable allowlist for frontend dev origin(s) only.

---

## 6. Observability & operations (minimal)

- Log authentication failures and authorization denials at INFO/WARN (avoid logging secrets).
- Return standard HTTP errors (401/403/404/422).

---

## 7. Out of scope (explicit)

- Implementing Round tracking endpoints.
- DB migrations (Alembic).
- Multi-tenant data separation for Company (requires schema change).
- UI implementation (this repo currently contains backend only; wireframes provided separately for planned UI).
