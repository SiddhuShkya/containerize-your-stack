# Containerize Your Stack

A FastAPI to-do API originally built with an in-memory store, now backed by
Postgres — both running together via Docker Compose.

## Project Description

This project takes the CRUD API from the earlier "Build your first CRUD API"
assignment and containerizes the whole stack:

- **Postgres** runs in Docker with a named volume, so data survives restarts.
- **The app** runs in its own container, built from a `Dockerfile`.
- **`docker compose up`** starts both together — one command, whole stack.

### Architecture note: how the repository was swapped

The original app manipulated a global `tasks_db` list directly inside
`main.py`. To swap in Postgres without touching the routes or business logic,
the data-access layer was pulled out behind an interface:

- **`repository.py`** — abstract `TaskRepository` interface (`list_all`,
  `get`, `create`, `update`, `delete`).
- **`repositories/in_memory_repository.py`** — the original in-memory logic, now
  implementing that interface. Behavior is identical to before.
- **`repositories/postgres_repository.py`** — a Postgres implementation of the exact same
  interface, using `psycopg` and the `DATABASE_URL` connection string.

`main.py`'s routes call `repo.list_all()`, `repo.get()`, etc. instead of
touching a list directly — the route handlers, status codes, and validation
logic are unchanged from the original. The only "switch" is in `main.py`:

```python
if os.environ.get("DATABASE_URL"):
    repo = PostgresTaskRepository()
else:
    repo = InMemoryTaskRepository()
```

That's the whole swap — proof that the layering actually works.

## Project Structure

```text
.
├── main.py                        # FastAPI app + routes (unchanged logic)
├── repository.py                  # Abstract repository interface
├── in_memory_repository.py        # Original in-memory implementation
├── postgres_repository.py         # Postgres implementation (Stage 4)
├── Dockerfile                     # Builds the app image
├── docker-compose.yml             # Postgres + app services
├── init-db/
│   └── 001_create_todos_table.sql # Table schema, auto-run on first init
├── requirements.txt               # Python dependencies
├── .env.example                   # Placeholder env vars (committed)
├── .env                           # Real env vars (gitignored, you create this)
└── .gitignore
```

## Prerequisites

- **Docker Desktop** (or Docker Engine + Compose plugin) installed and running.
- **Port 5432** and **port 8000** free on your machine (see Troubleshooting
  below if they're not).
- Git, to clone the repo.

## Setup and Run Instructions

### 1. Clone the repo

```bash
git clone https://github.com/SiddhuShkya/containerize-your-stack.git
cd containerize-your-stack
```

### 2. Create your `.env` file

Copy the example file and fill in real values:

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
POSTGRES_USER=appuser
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=appdb
POSTGRES_PORT=5432
POSTGRES_HOST=localhost
DATABASE_URL=postgresql://appuser:your_password_here@localhost:5432/appdb
```

**Important:** avoid special characters like `@` in `POSTGRES_PASSWORD` —
see Troubleshooting below for why.

`.env` is gitignored and never committed. `.env.example` (placeholders only)
is committed so anyone cloning the repo knows what to configure.

### 3. Make sure port 5432 is free

If you have a local (non-Docker) Postgres installation already running, it
will conflict with the containerized one. Check and stop it if needed — see
Troubleshooting below.

### 4. Start the whole stack

```bash
docker compose up -d --build
```

This will:
- Pull the `postgres:16-alpine` image and start Postgres with a named volume.
- Run the SQL script in `init-db/` automatically on first startup, creating
  the `todos` table.
- Build the app image from the `Dockerfile` and start it.
- Wait for Postgres to report healthy before starting the app
  (`depends_on: condition: service_healthy`).

### 5. Verify everything is running

```bash
docker compose ps
```

You should see both `postgres_db` and `task_api` with status `Up`/`healthy`.

### 6. Test the API

```bash
curl http://localhost:8000/
curl http://localhost:8000/tasks
```

Or open the interactive docs in your browser: `http://localhost:8000/docs`

## Endpoints

| CRUD operation | HTTP method | Endpoint | Meaning |
|---|---|---|---|
| Read | GET | `/` | API metadata |
| Read | GET | `/tasks` | List all tasks |
| Read | GET | `/tasks/{task_id}` | Get a single task by ID |
| Create | POST | `/tasks` | Create a new task (body: `{"task": "...", "status": false}`) |
| Update | PUT | `/tasks/{task_id}` | Update an existing task |
| Delete | DELETE | `/tasks/{task_id}` | Delete a task |

## Proving Data Persistence

To confirm data survives a full stack restart:

```bash
# 1. Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "Persistence test", "status": false}'

# 2. Confirm it's there
curl http://localhost:8000/tasks

# 3. Restart the entire stack (app + database container)
docker compose down
docker compose up -d

# 4. Confirm the task is still there
curl http://localhost:8000/tasks
```

The task created in step 1 is still present after the restart in step 3,
because Postgres data lives in the named volume (`postgres_data`), which is
not removed by `docker compose down` (only `docker compose down -v` removes
volumes).

## Stopping the Stack

```bash
docker compose down          # stop containers, keep data
docker compose down -v       # stop containers AND delete the volume (data loss)
```

## Troubleshooting — issues encountered while building this

### 1. Docker Desktop was out of date

`dpkg -l | grep docker-desktop` showed an old version (`4.43.2`), and
`sudo apt install --only-upgrade docker-desktop` reported it was already the
newest version — because Docker Desktop wasn't registered as an apt
repository on this machine (only a stale `docker.list.distUpgrade` backup
file existed, not an active source). apt had no way to see newer releases.

**Fix:** downloaded the latest `.deb` package directly and installed it over
the existing version:

```bash
cd ~/Downloads
wget https://desktop.docker.com/linux/main/amd64/docker-desktop-amd64.deb
sudo apt-get update
sudo apt install ./docker-desktop-amd64.deb
```

(A `pkgAcquire::Run (13: Permission denied)` message appears at the end of
this — it's expected and can be ignored.) Docker Desktop was then fully
quit and reopened to run the new version.

### 2. Port 5432 already in use

`docker compose up` failed with:

```
Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:5432 -> 127.0.0.1:0: listen tcp 0.0.0.0:5432: bind: address already in use
```

Diagnosed with:

```bash
sudo lsof -i :5432
```

This revealed a **locally installed Postgres service** (not Docker) already
listening on port 5432 — likely installed via apt at some earlier point,
running as a systemd service.

**Fix:** stopped and disabled the native service so Docker could bind to the
port instead:

```bash
sudo systemctl stop postgresql
sudo systemctl disable postgresql
```

### 3. Password containing `@` broke the connection string

Using a `POSTGRES_PASSWORD` containing an `@` character (e.g. `pass@word`)
caused the app to fail with:

```
psycopg.OperationalError: failed to resolve host '...@postgres': Name or service not known
```

Since a Postgres connection string has the form
`postgresql://user:password@host:port/db`, an unescaped `@` inside the
password is indistinguishable from the separator before the hostname —
psycopg ended up trying to resolve part of the password as if it were the
host.

**Fix:** changed `POSTGRES_PASSWORD` to an alphanumeric value with no
special characters, and reset the database volume so the new credentials
took effect on a fresh initialization:

```bash
docker compose down -v
docker compose up -d --build
```

(Postgres only reads `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
on first initialization of an empty data directory — changing `.env` alone
does not update credentials on an already-initialized volume.)

### 4. `localhost` vs. the `postgres` service name inside Docker

Early on, `DATABASE_URL` used `localhost` as the host — correct for tools
like pgAdmin running on the host machine, but wrong for the `app` container
itself, since `localhost` inside a container refers to that container, not
the Postgres one. Docker Compose gives each service a DNS name matching its
service key, so the `app` service overrides `DATABASE_URL` at the
compose level to use `postgres` (the service name) as the host:

```yaml
environment:
  DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
```