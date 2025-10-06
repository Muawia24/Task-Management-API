from typing import Optional
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.db.dependancies import get_db
from app.models.Task import Task, TaskPriority, TaskStatus


@pytest.fixture
def client():
    """Create a test client."""
    # Create test database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    def get_test_db():
        with Session(engine) as session:
            # Simple DB class for testing
            class TestDB:
                def create_task(self, task_data):
                    db_task = Task(**task_data.model_dump())
                    session.add(db_task)
                    session.commit()
                    session.refresh(db_task)
                    return db_task
                
                def get_tasks_pagination_and_filter(self, skip=0, limit=10, priority=None, status=None):
                    from sqlmodel import select
                    statement = select(Task).offset(skip).limit(limit)
                    if not priority and not status:
                        return session.exec(statement).all()

                    if priority and not status:
                        statement = statement.where(Task.priority == priority)
                        
                    if status and not priority:
                        statement = statement.where(Task.status == status)

                    statement = statement.where(Task.priority == priority, Task.status == status)
                    return session.exec(statement).all()
                
                def get_task(self, task_id):
                    return session.get(Task, task_id)
                
                def update_task(self, task_id, updates):
                    from datetime import datetime
                    db_task = session.get(Task, task_id)
                    if not db_task:
                        return None
                    
                    update_data = updates.model_dump(exclude_unset=True)
                    update_data["updated_at"] = datetime.utcnow()
                    
                    for key, val in update_data.items():
                        setattr(db_task, key, val)
                    
                    session.add(db_task)
                    session.commit()
                    session.refresh(db_task)
                    return db_task
                
                def delete_task(self, task_id):
                    db_task = session.get(Task, task_id)
                    if not db_task:
                        return False
                    session.delete(db_task)
                    session.commit()
                    return True
                
                def filter_by_status(self, status):
                    from sqlmodel import select
                    statement = select(Task).where(Task.status == status)
                    return session.exec(statement).all()
                
                def filter_by_priority(self, priority):
                    from sqlmodel import select
                    statement = select(Task).where(Task.priority == priority)
                    return session.exec(statement).all()
            
            return TestDB()
    
    app.dependency_overrides[get_db] = get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()