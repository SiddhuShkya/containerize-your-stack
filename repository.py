from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class TaskRepository(ABC):

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get(self, task_id: int) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def create(self, task: str, status: bool) -> Dict[str, Any]:
        ...

    @abstractmethod
    def update(self, task_id: int, task: Optional[str] = None, status: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        ...
