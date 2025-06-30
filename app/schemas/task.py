from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from models.Task import TaskStatus, TaskPriority
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, max_length=100)

    @field_validator('title')
    @classmethod
    def validate_title(cls, val: str) -> str:
         """Ensure title is not empty"""
         if not val.strip():
              raise ValueError("Title can not be empty")
         return val
    @field_validator('due_date')
    @classmethod
    def validate_deadline(cls, val: Optional[datetime]) -> Optional[datetime]:
         """Ensure deadline is in the future"""
         if val and val <= datetime.now():
              raise ValueError('Due date must be in the future')
         return val

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, max_length=100)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('title')
    @classmethod
    def validate_title(cls, val: Optional[str]) -> Optional[str]:
         """Ensure title is not empty if provided"""
         if val is not None and not val.strip():
              raise ValueError("Title can not be empty")
         return val
    
    @field_validator('due_date')
    @classmethod
    def validate_deadline(cls, val: Optional[datetime]) -> Optional[datetime]:
         """Ensure deadline is in the future"""
         if val and val <= datetime.now():
              raise ValueError('Due date must be in the future')
         return val

class TaskResponse(TaskCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True, 
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Enum: lambda v: v.value
        }
    )