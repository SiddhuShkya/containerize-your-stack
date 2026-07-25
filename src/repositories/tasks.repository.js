// tasks.repository.js — Postgres implementation.
// Implements the exact same interface as the original in-memory repository
// (findAll, findById, create, update, remove, reset) but persists data in
// Postgres. All functions are async because pg queries are async.

const pool = require('../db');

// Seed rows — mirrors SEED_TASKS from the old in-memory repository.
// Used by reset() to restore the table to its original state.
const SEED_TASKS = [
    { title: 'Walk the dog',   done: true  },
    { title: 'Watch a movie',  done: false },
    { title: 'Drink 1l water', done: false },
];

async function findAll() {
    const { rows } = await pool.query('SELECT * FROM tasks ORDER BY id');
    return rows;
}

async function findById(id) {
    const { rows } = await pool.query('SELECT * FROM tasks WHERE id = $1', [id]);
    return rows[0] ?? null;
}

async function create({ title, done }) {
    const { rows } = await pool.query(
        'INSERT INTO tasks (title, done) VALUES ($1, $2) RETURNING *',
        [title, done]
    );
    return rows[0];
}

async function update(id, change) {
    // Build SET clause dynamically from whatever keys are in change.
    const fields = Object.keys(change);
    if (fields.length === 0) return findById(id);

    const setClauses = fields.map((f, i) => `${f} = $${i + 1}`).join(', ');
    const values = fields.map((f) => change[f]);
    values.push(id); // last placeholder is the WHERE id

    const { rows } = await pool.query(
        `UPDATE tasks SET ${setClauses} WHERE id = $${values.length} RETURNING *`,
        values
    );
    return rows[0] ?? null;
}

async function remove(id) {
    const { rowCount } = await pool.query('DELETE FROM tasks WHERE id = $1', [id]);
    return rowCount > 0;
}

async function reset() {
    // Truncate and re-seed, resetting the serial sequence too.
    await pool.query('TRUNCATE TABLE tasks RESTART IDENTITY');
    for (const task of SEED_TASKS) {
        await pool.query(
            'INSERT INTO tasks (title, done) VALUES ($1, $2)',
            [task.title, task.done]
        );
    }
    return findAll();
}

module.exports = {
    findAll,
    findById,
    create,
    update,
    remove,
    reset,
};
