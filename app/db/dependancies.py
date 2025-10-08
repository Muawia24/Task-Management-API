from fastapi import Depends
from sqlmodel import Session
from .session import get_session
from .database import DB


def get_db(session: Session = Depends(get_session)) -> DB:
    """Dependency that returns DB instance"""
    return DB(session)