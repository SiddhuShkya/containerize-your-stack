-- init.sql
-- Runs once when the Postgres container starts for the first time.
-- Creates the tasks table and inserts the same seed rows as the old
-- in-memory repository, so the app is ready to use immediately.

CREATE TABLE IF NOT EXISTS tasks (
    id   SERIAL PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT FALSE
);  

-- Seed data (mirrors the original SEED_TASKS in the in-memory repo)
INSERT INTO tasks (title, done) VALUES
    ('Walk the dog',   TRUE),
    ('Watch a movie',  FALSE),
    ('Drink 1l water', FALSE)
ON CONFLICT DO NOTHING;
