import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app  # assuming your FastAPI app instance is defined there
from app.db.database import DB
from app.models.Task import Task

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="session")
def session_fixture():
    """Create a new database session for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="db")
def db_fixture(session: Session):
    """Provide a DB instance using the test session."""
    return DB(session)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Provide a FastAPI test client using an in-memory DB."""
    # Dependency override for the FastAPI app
    def override_get_db():
        yield DB(session)
    app.dependency_overrides = { }
    from app.db.dependancies import get_db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
