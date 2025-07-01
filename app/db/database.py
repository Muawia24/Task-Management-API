from sqlmodel import Session, select
from app.models.Task import Task
from app.schemas import task
from typing import Optional, List
from app.schemas.task import TaskCreate, TaskUpdate
from datetime import datetime, timezone


class DB:
    def __init__(self, session: Session):
        """Instatiate the engine """
        self.__session = session
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Add task object to current database session"""
        db_task = Task(**task_data.model_dump())
        self.__session.add(db_task)
        self.__session.commit()
        self.__session.refresh(db_task)
        return db_task

    def get_tasks(self, skip: int = 0, limit: int = 10) -> List[Task]:
        """Query all tasks objects for curent session"""
        statement = select(Task).offset(skip).limit(limit)
        return self.__session.exec(statement).all()

    def get_task(self, task_id: int) -> Optional[Task]:
        """Query task object in tasks based on task_id"""
        return self.__session.get(Task, task_id)

    def update_task(self, task_id: int, updates: TaskUpdate) -> Optional[Task]:
        """Query and update task object based on task_id"""
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        for key, val in update_data.items():
            setattr(db_task, key, val)
        
        self.__session.add(db_task)
        self.__session.commit()
        self.__session.refresh(db_task)

        return db_task

    def delete_task(self, task_id: int) -> bool:
        """Delete object from the current database session"""
        db_task = self.get_task(task_id)
        if not db_task:
            return False
        
        self.__session.delete(db_task)
        self.__session.commit()

        return True

    def filter_by_status(self, status: str) -> List[Task]:
        """Fetches the tasks based on thier status"""
        statement = select(Task).where(Task.status == status)
        return self.__session.exec(statement).all()

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Fetches the tasks based on the priority of each task"""
        statement = select(Task).where(Task.priority == priority)
        return self.__session.exec(statement).all()