from fastapi import FastAPI
from app.routers import task_routes
from app.db.session import create_db_and_tables

app = FastAPI(title="Task Management API")

@app.on_event("startup")
def on_startup():
    '''
    Initializes components at application startup
    '''
    create_db_and_tables()

app.include_router(task_routes.router)

@app.get("/")
def read_root():
    '''
    Return: API information and available endpoints.
    '''
    return {"message": "Task Management API", "endpoints": ["/tasks", "/health"]}

@app.get("/health")
def check_health():
    '''
    Return API health status
    '''
    return {"status": "OK"}