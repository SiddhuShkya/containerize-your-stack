# Containerize Your Stack

A Node.js task API backed by **PostgreSQL**, containerised with Docker Compose.

## Quick start

```bash
# Copy environment config
cp .env.example .env   # edit credentials if you like

# Start the whole stack (Postgres + app)
docker compose up --build
```

The API is available at **http://localhost:3000**.  
Swagger docs: **http://localhost:3000/docs**

---

## Architecture

```
HTTP request
    ↓
routes/tasks.routes.js     (translate HTTP ↔ service calls)
    ↓
services/tasks.service.js  (business logic, validation, error types)
    ↓
repositories/tasks.repository.js  ← **only this file changed**
    ↓
PostgreSQL (Docker)
```

### How the repository was swapped

The original `tasks.repository.js` held data in a JavaScript array. It exported six functions: `findAll`, `findById`, `create`, `update`, `remove`, `reset`.

The new version implements the **exact same six functions** using `pg.Pool` queries against a Postgres `tasks` table. Because the interface is identical, **`tasks.service.js` and `tasks.routes.js` required no business-logic changes** — only the addition of `async/await` to propagate the Promises that a real database introduces.

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List all tasks (`?done=true/false`, `?search=...`) |
| POST | `/tasks` | Create a task |
| GET | `/tasks/:id` | Get a single task |
| PUT | `/tasks/:id` | Update a task |
| DELETE | `/tasks/:id` | Delete a task |
| GET | `/stats` | `{ total, done, open }` |
| POST | `/reset` | Restore seed data |

---

## Proving persistence

Steps taken to verify that data survives a full restart:

```bash
# 1. Start the stack
docker compose up --build -d

# 2. Create a new task
curl -s -X POST http://localhost:3000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Persist me"}' | jq

# 3. Confirm it exists
curl -s http://localhost:3000/tasks | jq

# 4. Full stack restart (removes containers, keeps volume)
docker compose down
docker compose up -d

# 5. Task still there ✓
curl -s http://localhost:3000/tasks | jq
```

The named Docker volume `postgres_data` stores the Postgres data directory, so rows survive `docker compose down && docker compose up`.

---

## Project structure

```
.
├── db/
│   └── init.sql            # Table creation + seed rows (runs once on first start)
├── src/
│   ├── db.js               # Singleton pg.Pool connection pool
│   ├── repositories/
│   │   └── tasks.repository.js   # ← swapped from memory to Postgres
│   ├── services/
│   │   └── tasks.service.js      # unchanged (business logic)
│   └── routes/
│       └── tasks.routes.js       # unchanged (HTTP layer)
├── Dockerfile
├── docker-compose.yml
├── .env                    # gitignored — real credentials
└── .env.example            # committed — placeholder values
```
