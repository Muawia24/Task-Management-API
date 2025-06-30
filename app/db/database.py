from sqlmodel import Session
from app.models.Task import Task
from app.schemas import task
from typing import Optional, List


class DB:
    def __init__(self, session: Session):
        """Instatiate the engine """
        self.session = session
    
    def create_task(self, task: TaskCreate) -> Task:
        """Add task object to current database session"""
        pass

    def get_tasks(self, skip: int = 0, limit: int = 10) -> List[Task]:
        """Query all tasks objects for curent session"""
        pass

    def get_task(self, task_id: int) -> Optional[Task]:
        """Query task object in tasks based on task_id"""
        pass

    def update_task(self, task_id: int, task: TaskUpdate) -> Optional[Task]:
        """Query and update task object based on task_id"""
        pass

    def delete_task(self, task_id: int) -> bool:
        """Delete object from the current database session"""
        pass

    def filter_by_status(self, status: str) -> List[Task]:
        """Fetches the tasks based on thier status"""
        pass

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Fetches the tasks based on the priority of each task"""
        pass