# Containerize Your Stack - Project Instructions

This document provides clear, step-by-step instructions for both AI agents and human developers to complete the "Containerize your stack" assignment.

## Project Goal
Run Postgres in Docker, connect the existing service to it by swapping the in-memory store for a real Postgres repository, and start both the application and database together using one command (`docker compose up`).

## Core Principles & Architecture
- **Layering & Architecture Proving:** The service and route layers MUST NOT change. Only a new Postgres repository should be implemented and swapped in for the in-memory repository.
- **Persistence:** Data must survive a complete stack restart (both app and container).
- **Environment Configuration:** Sensitive information like connection strings must be kept in `.env` (which must be gitignored) with a corresponding `.env.example` committed to the repository.

---

## Execution Stages

### Stage 1: Setup Dockerized Postgres
- [ ] Create a `docker-compose.yml` file in the project root.
- [ ] Add a `postgres` service to the `docker-compose.yml`.
- [ ] Configure the Postgres service to use a named volume to ensure data persistence across restarts.
- [ ] Set appropriate environment variables for Postgres (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

### Stage 2: Environment Configuration
- [ ] Create a `.env` file and add the Postgres connection string (e.g., `DATABASE_URL`).
- [ ] Ensure `.env` is added to `.gitignore`.
- [ ] Create a `.env.example` file with placeholder values for the connection string and commit it to the repository.

### Stage 3: Database Initialization
- [ ] Create an SQL initialization script or file to create the necessary table for your data.
- [ ] Ensure the table schema matches the data structure expected by your application.
- [ ] (If applicable) Configure `docker-compose.yml` to run this initialization script when the database container starts.

### Stage 4: Implement Postgres Repository
- [ ] Install necessary Postgres driver dependencies for your application.
- [ ] Create a new repository file/class that interacts with Postgres using the connection string from `.env`.
- [ ] Ensure this new Postgres repository implements the **exact same interface** as the existing in-memory repository.

### Stage 5: Swap Repository & Dockerize App
- [ ] In the application's configuration or dependency injection setup, replace the in-memory repository with the new Postgres repository.
- [ ] **CRITICAL:** Verify that service logic and route definitions remain completely untouched.
- [ ] Add the application as a service in `docker-compose.yml` (building from a `Dockerfile`), ensuring it depends on the Postgres service being ready.
- [ ] Set up the application to run automatically when using `docker compose up`.

### Stage 6: Documentation and Verification
- [ ] Run `docker compose up` to start the entire stack.
- [ ] Test the API endpoints to create data rows.
- [ ] Restart the application and container (`docker compose down` followed by `docker compose up`).
- [ ] Retrieve the data to verify that the created rows are still present (proving volume persistence).
- [ ] Update the `README.md` to explicitly state:
  1. How the Postgres repository was swapped in while leaving services and routes unchanged.
  2. The exact steps taken to prove data persistence across restarts.

---

## Stretch Goals (Optional)

### Stretch 1: Redis Integration
- [ ] Add a Redis service to the `docker-compose.yml` file.
- [ ] Add code in the application to successfully connect to and ping the Redis service on startup.

### Stretch 2: Database Profiling
- [ ] Add an index to the Postgres table created in Stage 3.
- [ ] Seed the table with a substantial amount of data.
- [ ] Run an `EXPLAIN ANALYZE` query before and after adding the index, and document the performance differences.
