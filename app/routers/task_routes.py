from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.db.database import DB
from app.db.dependancies import get_db
from typing import List

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    response_description="The created task"
)
def creat_task(task: TaskCreate, db: DB = Depends(get_db)):
    """Create a new task with all the information"""
    try:
        return db.create_task(task)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="List all tasks",
    response_description="List of tasks"
)
def all_tasks(skip: int = 0, limit: int = 10, db: DB = Depends(get_db)):
    """
    Retrieve a list of tasks with pagination:

    - **skip**: number of items to skip (default 0)
    - **limit**: maximum number of items to return (default 10)
    """
    return db.get_tasks(skip, limit)

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    response_description="The requested task"
)
def task_by_id(task_id: int, db: DB = Depends(get_db)):
    """
    Get a single task by its ID:

    - **task_id**: the ID of task to retrieve
    """
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    response_description="The updated task"
)
def update_task(task_id: int, updates: TaskUpdate, db: DB = Depends(get_db)):
    """
    Update an existing task:

    - **task_id**: the ID of task to update
    - **updates**: fields to update (all optional)
    """
    task = db.update_task(task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: DB = Depends(get_db)):
    """
    Delete an existing task:

    - **task_id**: the ID of task to delete
    """
    if not db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")