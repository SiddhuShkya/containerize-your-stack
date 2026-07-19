import os
from typing import Optional, List, Dict, Any

import psycopg
from psycopg.rows import dict_row

from repository import TaskRepository


class PostgresTaskRepository(TaskRepository):
    
    def __init__(self, connection_string: Optional[str] = None):
        self._conn_string = connection_string or os.environ["DATABASE_URL"]

    def _connect(self):
        return psycopg.connect(self._conn_string, row_factory=dict_row)

    def list_all(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, task, status FROM todos ORDER BY id;")
                return cur.fetchall()

    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, task, status FROM todos WHERE id = %s;", (task_id,))
                return cur.fetchone()

    def create(self, task: str, status: bool) -> Dict[str, Any]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO todos (task, status) VALUES (%s, %s) RETURNING id, task, status;",
                    (task, status),
                )
                row = cur.fetchone()
                conn.commit()
                return row

    def update(self, task_id: int, task: Optional[str] = None, status: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        existing = self.get(task_id)
        if not existing:
            return None

        new_task = task if task is not None else existing["task"]
        new_status = status if status is not None else existing["status"]

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE todos SET task = %s, status = %s WHERE id = %s RETURNING id, task, status;",
                    (new_task, new_status, task_id),
                )
                row = cur.fetchone()
                conn.commit()
                return row

    def delete(self, task_id: int) -> bool:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM todos WHERE id = %s;", (task_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
