from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
        description="Unique task identifier"
    )
    title: str = Field(max_length=200, description="Task title")
    description: Optional[str] = Field(
        max_length=1000,
        description="Task description"
    )
    status: TaskStatus = Field(
        default=TaskStatus.pending,
        description="Task status"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        description="Task priority"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task deadline"
    )
    assigned_to: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Assignee name"
    )
    author: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Author name"
    )