from typing import Optional, List, Dict, Any
from repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """Original in-memory storage, now behind the TaskRepository interface."""

    def __init__(self):
        self._tasks: List[Dict[str, Any]] = [
            {"id": 1, "task": "Read Documentation", "status": False},
            {"id": 2, "task": "Build CRUD API", "status": True},
            {"id": 3, "task": "Add tests", "status": False},
        ]

    def _find(self, task_id: int) -> Optional[Dict[str, Any]]:
        for t in self._tasks:
            if t["id"] == task_id:
                return t
        return None

    def _next_id(self) -> int:
        return max((t["id"] for t in self._tasks), default=0) + 1

    def list_all(self) -> List[Dict[str, Any]]:
        return self._tasks

    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        return self._find(task_id)

    def create(self, task: str, status: bool) -> Dict[str, Any]:
        new_task = {"id": self._next_id(), "task": task, "status": status}
        self._tasks.append(new_task)
        return new_task

    def update(self, task_id: int, task: Optional[str] = None, status: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        t = self._find(task_id)
        if not t:
            return None
        if task is not None:
            t["task"] = task
        if status is not None:
            t["status"] = status
        return t

    def delete(self, task_id: int) -> bool:
        t = self._find(task_id)
        if not t:
            return False
        self._tasks.remove(t)
        return True
