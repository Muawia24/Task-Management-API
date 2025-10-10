# Task Management API

A comprehensive task management API built with FastAPI, SQLModel, and SQLite. This API provides full CRUD operations for managing tasks with features like filtering, pagination, and data validation.

## Features

- **Full CRUD Operations**: Create, Read, Update, and Delete tasks
- **Data Validation**: Comprehensive input validation using Pydantic
- **Filtering**: Filter tasks by `status` and `priority` query parameters
- **Pagination**: Support for `skip`/`limit` query parameters
- **Sorting**: Sort tasks by `title`, `created_at`, `due_date`, `priority`, `status`
- **Full-text Search**: Search tasks by text across `title` and `description`
- **Bulk Operations**: Bulk update and bulk delete tasks
- **Author Tracking**: Optional `author` field on tasks
- **Database Integration**: SQLModel/SQLAlchemy with SQLite
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Error Handling**: Proper error responses with meaningful messages
- **CORS Support**: Cross-origin requests enabled

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases in Python, designed for simplicity, compatibility, and robustness
- **SQLite** - Lightweight, serverless database
- **Pydantic** - Data validation and settings management using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Muawia24/Task-Management-API
cd Task-Management-API
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Using Python module
```bash
python -m app.main
```

### Method 2: Using Uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using Docker

#### Build and run with Docker
```bash
docker build -t task-management-api .
docker run -p 8000:8000 task-management-api
```

#### Using Docker Compose (Production)
```bash
docker-compose up -d
```

#### Using Docker Compose (Development with hot reload)
```bash
docker-compose --profile dev up task-api-dev
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Docker Health Check
The Docker container includes a health check that monitors the `/health` endpoint. You can check container health with:
```bash
docker ps
```

## API Endpoints

### Root & Health
- `GET /` - API information and available endpoints
- `GET /health` - API health status

### Task Management
- `POST /tasks/` - Create a new task
- `GET /tasks/` - List all tasks (with pagination)
- `GET /tasks/{task_id}` - Get a specific task by ID
- `PUT /tasks/{task_id}` - Update an existing task
- `DELETE /tasks/{task_id}` - Delete a task
- `PUT /tasks/bulk-update` - Bulk update multiple tasks
- `DELETE /tasks/bulk-delete` - Bulk delete multiple tasks

### Sorting
- `GET /tasks/sort-by/{field}` - Sort tasks by a field
  - Valid fields: `title`, `created_at`, `due_date`, `priority`, `status`
  - `priority` order: urgent > high > medium > low
  - `status` order: pending > in_progress > completed > cancelled

### Search
- `GET /tasks/search?text=...&skip=0&limit=10` - Search in `title` and `description` with pagination

### Filtering (via query parameters)
- `GET /tasks/?status={status}` - Filter tasks by status
- `GET /tasks/?priority={priority}` - Filter tasks by priority
- Both filters can be combined with pagination: `GET /tasks/?status={status}&priority={priority}&skip=0&limit=10`

### Bulk Operations
- `PUT /tasks/bulk-update` - Update multiple tasks in one request
  - Body: `{ "updates": [{ "id": 1, "status": "completed", ... }, ...] }`
  - Returns: `{ "updated_count": <number> }`
  - Validation: 400 for empty updates, 404 if any ID is not found, 422 for invalid data
- `DELETE /tasks/bulk-delete` - Delete multiple tasks in one request
  - Body: `{ "task_ids": [1, 2, 3] }`
  - Returns: `{ "deleted": <number> }`

## Data Models

### Task Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| title | String | Required, Max 200 chars | Task title |
| description | String | Optional, Max 1000 chars | Task description |
| status | Enum | Required, Default: "pending" | Task status |
| priority | Enum | Required, Default: "medium" | Task priority |
| created_at | DateTime | Auto-generated | Creation timestamp |
| updated_at | DateTime | Optional | Last update timestamp |
| due_date | DateTime | Optional | Task deadline |
| assigned_to | String | Optional, Max 100 chars | Assignee name |
| author | String | Optional, Max 100 chars | Author name |

### Enums

**TaskStatus:**
- `pending`
- `in_progress`
- `completed`
- `cancelled`

**TaskPriority:**
- `low`
- `medium`
- `high`
- `urgent`

## Example API Calls

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Complete project documentation",
       "description": "Write comprehensive documentation for the project",
       "priority": "high",
       "assigned_to": "John Doe",
       "author": "Alice"
     }'
```

### Get All Tasks
```bash
curl "http://localhost:8000/tasks/"
```

### Get Tasks with Pagination
```bash
curl "http://localhost:8000/tasks/?skip=0&limit=5"
```

### Filter Tasks by Status and/or Priority
```bash
curl "http://localhost:8000/tasks/?status=pending"
curl "http://localhost:8000/tasks/?priority=high"
curl "http://localhost:8000/tasks/?status=in_progress&priority=urgent&skip=0&limit=10"
```

### Sort Tasks
```bash
curl "http://localhost:8000/tasks/sort-by/title"
curl "http://localhost:8000/tasks/sort-by/priority"
```

### Search Tasks
```bash
curl "http://localhost:8000/tasks/search?text=report&skip=0&limit=10"
```

### Get a Specific Task
```bash
curl "http://localhost:8000/tasks/1"
```

### Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "in_progress",
       "assigned_to": "Jane Smith"
     }'
```

### Bulk Update Tasks
```bash
curl -X PUT "http://localhost:8000/tasks/bulk-update" \
     -H "Content-Type: application/json" \
     -d '{
       "updates": [
         { "id": 1, "status": "completed" },
         { "id": 2, "priority": "urgent", "due_date": "2030-01-01T00:00:00Z" }
       ]
     }'
```

### Bulk Delete Tasks
```bash
curl -X DELETE "http://localhost:8000/tasks/bulk-delete" \
     -H "Content-Type: application/json" \
     -d '{
       "task_ids": [1, 2, 3]
     }'
```

### Notes on Search
- Case-insensitive search across `title` and `description`
- Empty `text` returns `400`
- No matches return `404`

### Delete a Task
```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## Data Validation

The API includes comprehensive validation:

- **Title Validation**: Cannot be empty or whitespace only, automatically trimmed
- **Due Date Validation**: Must be in the future if provided
- **Field Length Validation**: Enforced maximum lengths for string fields
- **Enum Validation**: Status and priority must be valid enum values

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Successful retrieval/update
- `201` - Successful creation
- `204` - Successful deletion
- `400` - Bad request/validation error
- `404` - Resource not found
- `422` - Unprocessable entity (validation error)

## Database

The application uses SQLite for data storage. The database file (`db.sqlite3`) is automatically created when the application starts. Tables are created automatically based on the SQLModel definitions.

### Database Migrations (Alembic)

This project uses Alembic for schema migrations. Existing migrations are stored under `migrations/versions/` (e.g., the migration adding the `author` field).

#### Apply existing migrations
```bash
alembic upgrade head
```

#### Create a new migration after model changes
1. Update your SQLModel definitions (e.g., in `app/models/Task.py`).
2. Generate a migration script:
```bash
alembic revision --autogenerate -m "describe your change"
```
3. Review the generated file in `migrations/versions/` and adjust if needed.
4. Apply the migration:
```bash
alembic upgrade head
```

#### Downgrade (rollback) a migration
```bash
alembic downgrade -1
```

Notes:
- On Windows/PowerShell inside the provided `venv`, use the bundled `alembic.exe` or run `python -m alembic ...`.
- With SQLite, some operations (e.g., dropping columns) may require Alembic to emit batch operations; check the generated script before applying.

## Development

### Project Structure
```
Task-Management-API/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # Database operations
│   │   ├── dependancies.py  # Database dependencies
│   │   └── session.py       # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── Task.py          # SQLModel task model
│   ├── routers/
│   │   ├── __init__.py
│   │   └── task_routes.py   # API route definitions
│   └── schemas/
│       ├── __init__.py
│       └── task.py          # Pydantic schemas
├── tests/
│   └── __init__.py
├── requirements.txt
├── README.md
└── todo.md
```

### Running Tests
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of a FastAPI assessment and is intended for educational purposes.

## Contact

For questions or issues, please open an issue on the GitHub repository.