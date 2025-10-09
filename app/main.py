from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import task_routes
from app.db.session import create_db_and_tables


app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management API built with FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_routes.router)


@app.get("/")
def read_root():
    '''
    Return: API information and available endpoints.
    '''
    return {
        "message": "Task Management API", 
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
def check_health():
    '''
    Return API health status
    '''
    return {"status": "OK", "message": "API is running successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)