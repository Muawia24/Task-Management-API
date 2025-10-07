from fastapi import HTTPException
from sqlmodel import Session, select, case, func, or_, sa_func
from app.models.Task import Task, TaskPriority, TaskStatus
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

    def get_tasks_pagination_and_filter(self, skip: int = 0, limit: int = 10,
                  priority: Optional[TaskPriority] = None,
                  status: Optional[TaskStatus] = None) -> List[Task]:
        """

        """
        statement = select(Task).offset(skip).limit(limit)
        if not priority and not status:
            return self.__session.exec(statement).all()
        
        if priority and not status:
            statement = statement.where(Task.priority == priority)
            
        if status and not priority:
            statement = statement.where(Task.status == status)

        statement = statement.where(Task.priority == priority, Task.status == status)
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
    
    def sort_tasks(self, field: str) -> List[Task]:
        """Sort tasks based on a given field"""
        field = field.lower()
        valid_fields = {
            "title": Task.title,
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "status": Task.status
        }

        if field not in valid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid field '{field}' for sorting. Valid fields are: {', '.join(valid_fields.keys())}"
            )
        
        order_expr = valid_fields[field]

        if field == "priority":
            order_expr = case(
                (Task.priority == TaskPriority.urgent, 1),
                (Task.priority == TaskPriority.high, 2),
                (Task.priority == TaskPriority.medium, 3),
                (Task.priority == TaskPriority.low, 4),
                else_=5
            )
        
        elif field == "status":
            order_expr = case(
                (Task.status == TaskStatus.pending, 1),
                (Task.status == TaskStatus.in_progress, 2),
                (Task.status == TaskStatus.completed, 3),
                (Task.status == TaskStatus.cancelled, 4),
                else_=5
            )
        
        statement = select(Task).order_by(order_expr)
        sorted_tasks = self.__session.exec(statement).all()

        if not sorted_tasks:
            raise HTTPException(status_code=404, detail="No tasks found to sort.")
        
        return sorted_tasks
    
    def search_tasks(self, text: str, skip: int = 0, limit: int = 10) -> List[Task]:
        """
        Search tasks by text in title or description with pagination
        """
        if not text:
            raise HTTPException(status_code=400, detail="Search text cannot be empty.")
        
        from sqlalchemy import func as sa_func

        # Escape LIKE wildcards for literal search
        escaped_text = text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

        statement = (
            select(Task)
            .where(
                or_(
                    func.lower(Task.title).like(f"%{escaped_text.lower()}%", escape='\\'),
                    func.lower(sa_func.coalesce(Task.description, '')).like(f"%{escaped_text.lower()}%", escape='\\')
                )
            )
            .offset(skip)
            .limit(limit)
        )

        tasks = self.__session.exec(statment).all()

        if not tasks:
            raise HTTPException(status_code=404, detail="No Task Found")
        
        return tasks