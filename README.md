# Task Management API (Assignment 2)

PostgreSQL-backed REST API for managing tasks, built with **FastAPI**, **SQLModel**, and **Uvicorn**.

This repository is **Assignment 2** of the FlyRank Backend AI Engineering track.  
It was started by cloning the **Assignment 1** in-memory Task API into a **separate repository**, then replacing process memory with a real **PostgreSQL** database while keeping the same HTTP API.

Containerization (Docker) is **not** part of this assignment — that is **Assignment A3**.

---

## Why this assignment exists

In Assignment 1, tasks lived in a Python dict and disappeared whenever the server restarted.

Assignment 2 keeps the same endpoints and JSON shapes, but stores rows in PostgreSQL so data survives restarts.

> APIs describe **what** the application does. Databases describe **where** it stores data.

---

## Why PostgreSQL

PostgreSQL was chosen for this submission because:

- It is a production-grade relational database used widely in real backend systems
- It supports the SQL CRUD patterns from the assignment (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `COUNT`, `ILIKE`)
- Moving from an in-memory list → PostgreSQL reinforces the same lesson as the brief: the storage layer can change without changing the API

---

## Where the database lives

| Item | Value |
|---|---|
| Engine | Local PostgreSQL (installed on your machine) |
| Host | `localhost` |
| Port | `5432` (default) |
| Database name | `tasks` |
| Default URL | `postgresql+psycopg://postgres:postgres@localhost:5432/tasks` |

On first API startup the app:

1. connects to PostgreSQL using `DATABASE_URL`
2. creates the `tasks` table if it does not exist
3. inserts three example tasks **only when the table is empty**

---

## Project Overview

- Same CRUD API as Assignment 1
- Persistence in PostgreSQL via SQLModel / SQLAlchemy
- Optional extras: `?done=`, `?search=`, `GET /stats`, `POST /reset`
- Thin routes + service layer
- pytest coverage
- Swagger UI at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | FastAPI |
| ORM | SQLModel |
| Database | PostgreSQL (local) |
| Driver | psycopg 3 |
| Server | Uvicorn |
| Validation | Pydantic v2 |
| Tests | pytest + httpx |

---

## Folder Structure

```text
.
├── app/
│   ├── main.py                 # FastAPI app, lifespan DB bootstrap
│   ├── core/
│   │   ├── config.py           # Settings + DATABASE_URL
│   │   └── exceptions.py
│   ├── db/
│   │   └── session.py          # Engine, sessions, create_all
│   ├── models/
│   │   └── task.py             # SQLModel Task table
│   ├── schemas/
│   │   └── task.py
│   ├── services/
│   │   └── task_service.py     # SQL-backed business logic
│   └── routes/
│       ├── health.py
│       └── tasks.py
├── docs/
│   └── sql-exploration.md
├── scripts/
│   └── setup_postgres.sql      # One-time local DB create helper
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## How to start the project

### 1. Clone this Assignment 2 repository

```bash
cd Assignment_2
```

### 2. Install and prepare local PostgreSQL

1. Install PostgreSQL for your OS if it is not already installed.
2. Make sure the server is running on port `5432`.
3. Create the `tasks` database (as the `postgres` superuser):

```bash
psql -U postgres -c "CREATE DATABASE tasks;"
```

Or use the helper script:

```bash
psql -U postgres -f scripts/setup_postgres.sql
```

Update the username/password in `.env` if your local install differs from the defaults.

### 3. Create a virtual environment and install dependencies

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure the connection

```bash
cp .env.example .env
```

Default URL (edit if your local password is different):

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tasks
```

### 5. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Someone cloning this repository can install PostgreSQL, create the `tasks` database, install requirements, and run the app; the table and seed data are created automatically on first boot.

---

## Running Tests

PostgreSQL must already be running with a `tasks` database.

```bash
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## API Endpoints

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/` | 200 | Welcome message |
| `GET` | `/health` | 200 | Health check |
| `GET` | `/tasks` | 200 | List all tasks |
| `GET` | `/tasks/{id}` | 200 / 404 | Get one task |
| `POST` | `/tasks` | 201 / 400 | Create a task |
| `PUT` | `/tasks/{id}` | 200 / 400 / 404 | Update a task |
| `DELETE` | `/tasks/{id}` | 204 / 404 | Delete a task |
| `GET` | `/tasks?done=true` | 200 | Filter by completion (SQL `WHERE`) |
| `GET` | `/tasks?search=text` | 200 | Search titles (SQL `ILIKE`) |
| `GET` | `/stats` | 200 | Aggregate counts (SQL `COUNT`) |
| `POST` | `/reset` | 200 | Restore seed tasks |

### Seed data

Inserted only when `tasks` is empty:

| id | title | done |
|---|---|---|
| 1 | Buy groceries | `false` |
| 2 | Write documentation | `true` |
| 3 | Review pull request | `false` |

### Error format

```json
{
  "error": "Task 99 not found"
}
```

---

## Example SQL query executed

```sql
SELECT * FROM tasks WHERE done = true;
```

More queries: [`docs/sql-exploration.md`](docs/sql-exploration.md)

### Database viewer screenshot

Open the `tasks` database with any PostgreSQL client (pgAdmin, DBeaver, TablePlus, VS Code PostgreSQL extension) using your local connection settings, then add a screenshot here:

![PostgreSQL tasks table](docs/database-viewer.png)

*(Add `docs/database-viewer.png` after capturing your local viewer.)*

---

## Example curl commands

```bash
curl http://localhost:8000/tasks

curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Ship feature\"}"

curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Buy organic groceries\", \"done\": true}"

curl -X DELETE http://localhost:8000/tasks/1

curl "http://localhost:8000/tasks?done=true"
curl "http://localhost:8000/tasks?search=doc"
curl http://localhost:8000/stats
curl -X POST http://localhost:8000/reset
```

---

## Suggested commit history (Assignment 2)

| Stage | Suggested commit message |
|---|---|
| Stage 0 | `Stage 0: create PostgreSQL database` |
| Stage 1 | `Stage 1: database read endpoints` |
| Stage 2 | `Stage 2: insert into database` |
| Stage 3 | `Stage 3: update and delete with SQL` |
| Stage 4 | `Stage 4: explored SQL` |
| Extras | `Extras: SQL filter, search, stats, reset` |
| Stage 5 | `Stage 5: database documentation` |

---

## Assignment checklist

- [x] Same CRUD API as Assignment 1
- [x] Tasks stored in PostgreSQL instead of memory
- [x] Data survives server restarts
- [x] Table auto-created if missing
- [x] Three example tasks inserted only on first run (empty table)
- [x] CRUD operations use SQL via SQLModel
- [x] Unknown ids return 404
- [x] Invalid requests return 400
- [x] Extras: `?done=`, `?search=`, `GET /stats`, `POST /reset`
- [x] README explains Assignment 1 → Assignment 2 split and local PostgreSQL setup
- [x] No Docker in this assignment (reserved for A3)
- [x] Separate repository for Assignment 2

---

## License

Created for the FlyRank backend assignment.
