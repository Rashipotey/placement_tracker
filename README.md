# Placement Tracker

FastAPI + SQLAlchemy + PostgreSQL backend for tracking job applications.

## Local setup

1. Create a PostgreSQL database (for example `placement_tracker`).
2. Create and activate a virtual environment, then install dependencies:

   ```
   python -m venv .venv
   .venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on Linux/macOS
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the repository root with these values (never commit it):

   | Variable | Description |
   |---|---|
   | `DATABASE_URL` | SQLAlchemy URL of the PostgreSQL database |
   | `JWT_SECRET_KEY` | Secret used to sign JWTs (required, never commit it) |
   | `JWT_ALGORITHM` | JWT algorithm (default `HS256`) |
   | `JWT_EXPIRE_MINUTES` | Token lifetime in minutes (default `60`) |
   | `CORS_ORIGINS` | Comma-separated allowed browser origins (default `http://localhost:5173,http://localhost:3000`) |

4. Run the API:

   ```
   uvicorn app.main:app --reload
   ```

   Tables are created on startup. Interactive API docs: http://localhost:8000/docs

## Upgrading an existing database

`Base.metadata.create_all` creates missing tables but does not add columns to existing ones. A database created before `applications.round_id` (the application's current round) existed needs this additive, non-destructive change (safe to run more than once; Alembic migrations are out of scope):

```sql
ALTER TABLE applications ADD COLUMN IF NOT EXISTS round_id UUID;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_applications_round_id') THEN
    ALTER TABLE applications ADD CONSTRAINT fk_applications_round_id
      FOREIGN KEY (round_id) REFERENCES rounds (id) ON DELETE SET NULL;
  END IF;
END $$;
```

Adding the user role column (roles `USER` / `ADMIN`; existing accounts become `USER`):

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'USER';

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_users_role') THEN
    ALTER TABLE users ADD CONSTRAINT ck_users_role CHECK (role IN ('USER', 'ADMIN'));
  END IF;
END $$;
```

## Roles and the first administrator

Public registration always creates a `USER`. Only an `ADMIN` can create, edit or delete companies; every authenticated user can list and select them. Admins get no extra access to other users' applications or rounds. The role is stored in the database and checked on every request (the JWT also carries a `role` claim for the UI, but it is not trusted for authorization), and `GET /users/me` returns it.

There is no HTTP endpoint that grants admin rights. To make an existing account an administrator, run this on the server (it needs the same `.env`/database access as the API), using the email you registered with:

```
python -m app.scripts.bootstrap_admin you@example.com
```

Log in again afterwards to get a token with the new role.

## Login contract

`POST /auth/login` takes a JSON body `{"email": "...", "password": "..."}` and returns `{"access_token": "...", "token_type": "bearer"}`; wrong credentials return 401.

## Tests

```
pip install -r requirements.txt
pytest
```

The tests use the database from `DATABASE_URL` in `.env` (there is no separate test database). Every record they create carries a unique `pytest_<random>_` prefix and only those records are deleted at the end of the run, so do not point `DATABASE_URL` at a database where that is unacceptable. If `JWT_SECRET_KEY` is not set, the tests use a fixed test-only value.

Browser end-to-end tests (Selenium with Edge; the driver is fetched by Selenium Manager) are opt-in and start the API on port 8000 and the Vite dev server on port 5173 (both must be free; override with `E2E_API_PORT` / `E2E_WEB_PORT`):

```
E2E=1 pytest tests/e2e
```

The browser tests create a prefixed test admin by updating the database directly. On Windows PowerShell use `$env:E2E=1; pytest tests/e2e`. `npm install` must have been run in `frontend/` first.

## Frontend

```
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build
```

The API URL defaults to `http://localhost:8000`; override it with `VITE_API_URL` (see `frontend/.env.example`). The backend must allow the frontend origin via `CORS_ORIGINS`.
