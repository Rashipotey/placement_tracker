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

3. Copy `.env.example` to `.env` and fill in the values:

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
