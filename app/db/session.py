from sqlmodel import SQLModel, create_engin, Session

DATABASE_URL = "sqlite:///./db.sqlite3"

engin = create_engin(DATABASE_URL, echo=True)

def create_db_and_tables():
    '''
    Create database tables
    '''
    SQLModel.metadata.create_all(engin)

def get_session():
    '''
    Dependency for FastAPI routes
    '''
    with Session(engin) as session:
        yield session