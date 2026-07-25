# Containerize Your Stack 🐳🐘

A production-ready Node.js Express Task Management API backed by **PostgreSQL**, fully containerised using Docker and Docker Compose.

---

## 🚀 Quick Start

Run the entire application stack (Node.js API + PostgreSQL database) with a single command:

```bash
# 1. Clone the repository & navigate into project directory
cd "Containerize your stack"

# 2. Copy environment configuration file
cp .env.example .env

# 3. Build and launch the container stack
docker compose up --build
```

- **API Base URL:** `http://localhost:3000`
- **Health Check:** `http://localhost:3000/health`
- **Interactive Swagger Docs:** `http://localhost:3000/docs`

---

## 🏛️ Architecture & Layering

The application strictly follows a layered architecture to decouple business logic from data storage:

```
HTTP Request
    │
    ▼
┌───────────────────────────────────────┐
│  src/routes/tasks.routes.js           │  <-- Route (HTTP) Layer: Parses requests & status codes
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  src/services/tasks.service.js        │  <-- Service Layer: Enforces business logic & validation
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  src/repositories/tasks.repository.js │  <-- Repository Layer: Swapped from In-Memory to PostgreSQL!
└───────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────┐
│  PostgreSQL 16 (Docker Container)    │  <-- Database: Persisted via Docker Volume
└───────────────────────────────────────┘
```

### 🔄 How the Repository Was Swapped

1. **Interface Contract:** The original repository stored tasks in a local JavaScript array and exposed `findAll()`, `findById()`, `create()`, `update()`, `remove()`, and `reset()`.
2. **Postgres Implementation:** The new `tasks.repository.js` implements the exact same 6 functions using parameterized SQL queries (`pg.Pool`).
3. **Zero Business Logic Changes:** `tasks.service.js` and `tasks.routes.js` remain completely unchanged in terms of business rules, validation, status codes, and HTTP responses. The only modification was making caller methods `async`/`await` to handle asynchronous database I/O.

---

## ⚙️ Environment Configuration

All environment variables are loaded securely from `.env` (gitignored). A committed `.env.example` file is provided for reference:

| Variable | Description | Default / Example Value |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL superuser username | `siddhu` |
| `POSTGRES_PASSWORD` | PostgreSQL superuser password | `shakya2830` |
| `POSTGRES_DB` | PostgreSQL database name | `appdb` |
| `POSTGRES_PORT` | Host port for PostgreSQL | `5432` |
| `POSTGRES_HOST` | Hostname (`postgres` inside Docker Compose, `localhost` for native dev) | `postgres` |
| `DATABASE_URL` | Full PostgreSQL connection string | `postgresql://siddhu:shakya2830@postgres:5432/appdb` |
| `PORT` | Application server port | `3000` |

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API Metadata & available endpoints list |
| `GET` | `/health` | Service health status check (`{"status": "ok"}`) |
| `GET` | `/docs` | Interactive OpenAPI / Swagger documentation |
| `GET` | `/tasks` | List tasks (supports `?done=true/false` & `?search=term`) |
| `POST` | `/tasks` | Create a new task (`{"title": "..."}`) |
| `GET` | `/tasks/:id` | Get details for a specific task |
| `PUT` | `/tasks/:id` | Update task title and/or completed status |
| `DELETE` | `/tasks/:id` | Delete a task by ID |
| `GET` | `/stats` | Aggregate task stats (`{ total, done, open }`) |
| `POST` | `/reset` | Truncate database and restore initial seed tasks |

---

## 🧪 Proof of Data Persistence

Data is stored in a dedicated named Docker Volume (`postgres_data`) mapped to `/var/lib/postgresql/data`. This ensures data persists across container shutdowns, code changes, and application restarts.

### Verification Steps Taken:

```bash
# 1. Start the stack in background
docker compose up --build -d

# 2. Add a new task via API
curl -s -X POST http://localhost:3000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Verify persistent volume"}'

# 3. Verify the new task is returned
curl -s http://localhost:3000/tasks

# 4. Stop and remove containers (Volume remains intact)
docker compose down

# 5. Restart the container stack
docker compose up -d

# 6. Query tasks again — the task created in Step 2 is still present!
curl -s http://localhost:3000/tasks
```

---

## 📁 Project Structure

```
.
├── db/
│   └── init.sql            # Table schema & initial seed data script
├── src/
│   ├── app.js              # Express app setup & middleware configuration
│   ├── db.js               # PostgreSQL connection pool instance (pg)
│   ├── errors.js           # Domain error classes (NotFoundError, ValidationError)
│   ├── middleware/
│   │   └── error-handler.js# Global HTTP error handler middleware
│   ├── repositories/
│   │   └── tasks.repository.js  # PostgreSQL repository implementation
│   ├── routes/
│   │   ├── meta.routes.js       # Health and metadata routes
│   │   └── tasks.routes.js      # Task HTTP endpoints
│   └── services/
│       └── tasks.service.js     # Task business logic
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── index.js
├── openapi.json
├── package.json
└── README.md
```
