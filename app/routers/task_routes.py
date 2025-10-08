from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.Task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskBulkUpdateRequest, TaskBulkDeleteRequest
from app.db.database import DB
from app.db.dependancies import get_db
from typing import List, Optional

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    response_description="The created task"
)
def creat_task(task: TaskCreate, db: DB = Depends(get_db)) -> TaskResponse:
    """Create a new task with all the information"""
    try:
        return db.create_task(task)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get(
    "/",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks with pagination and filters",
    response_description="List of paginated and filterd tasks"
)
def all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    priority: Optional[TaskPriority] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    db: DB = Depends(get_db)) -> List[TaskResponse]:
    """
    Retrieve a list of tasks with pagination:

    - **skip**: number of items to skip (default 0)
    - **limit**: maximum number of items to return (default 10)
    """
    try:
        return db.get_tasks_pagination_and_filter(skip, limit, priority, status)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
        "/search",
        response_model=List[TaskResponse],
        status_code=status.HTTP_200_OK,
        summary="Search tasks by text in title or description with pagination",
        response_description="List of tasks matching the search criteria with pagination"
    )
def search_tasks(
    text: str = Query(..., description="Text to search in title / description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: DB = Depends(get_db)
    ) -> List[TaskResponse]:
    """
    Search tasks by text in title or description with pagination:
    - **text**: text to search for (required)
    - **skip**: number of items to skip (default 0) 
    - **limit**: maximum number of items to return (default 10)
    """
    try:
        return db.search_tasks(text, skip, limit)
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server error"
        ) from e


@router.put(
        "/bulk-update",
        status_code=status.HTTP_200_OK,
        summary="Bulk update tasks",
        response_description="Number of tasks updated"
)
def bulk_update_tasks(
    payload: TaskBulkUpdateRequest,
    db: DB = Depends(get_db)
) -> dict:
    """
    Bulk update multiple tasks at once.
    - **task_ids**: List of task IDs to update
    - **updates**: Fields to update (all optional)
    """
    try:
        if not payload.updates:
            raise HTTPException(status_code=400, detail="No tasks provided for bulk update.")
        
        # Convert list of TaskUpdate to list of dicts, excluding unset fields
        tasks = [task.model_dump(exclude_unset=True) for task in payload.updates]
        updated_count = db.bulk_update_tasks(tasks)

        return {"updated_count": updated_count}
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server error"
        ) from e


@router.delete(
        "/bulk-delete",
        status_code=status.HTTP_200_OK,
        summary="Bulk delete tasks",
        response_description="Number of tasks deleted"
)
def bulk_delete_tasks(
    payload: TaskBulkDeleteRequest,
    db: DB = Depends(get_db)    
):
    """
    Bulk delete multiple tasks at once.
    - **task_ids**: List of task IDs to delete
    """
    try:
        count_deleted = db.bulk_delete_tasks(payload.task_ids)

        return {"deleted": count_deleted}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Server error"
        ) from e


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    response_description="The requested task"
)
def task_by_id(task_id: int, db: DB = Depends(get_db)) -> TaskResponse:
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
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    response_description="The updated task"
)
def update_task(task_id: int, updates: TaskUpdate,
                db: DB = Depends(get_db)) -> TaskResponse:
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
def delete_task(task_id: int, db: DB = Depends(get_db)) -> None:
    """
    Delete an existing task:

    - **task_id**: the ID of task to delete
    """
    if not db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    return None


@router.get("/sort-by/{field}", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def sort_tasks(field: str, db: DB = Depends(get_db)) -> List[TaskResponse]:
    """
    Sort tasks by a specified field:
    - **field**: the field to sort by (e.g., 'priority', 'due_date')
    """
    try:
        return db.sort_tasks(field)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error") from e