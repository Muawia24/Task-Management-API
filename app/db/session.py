from sqlmodel import SQLModel, create_engin, Session

DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engin(DATABASE_URL, echo=True)

def create_db_and_tables():
    '''
    Create database tables
    '''
    SQLModel.metadata.create_all(engine)

def get_session():
    '''
    Dependency for FastAPI routes
    '''
    with Session(engine) as session:
        yield session