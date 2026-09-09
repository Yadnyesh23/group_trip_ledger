from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings 


engine = create_engine(
    settings.DATABASE_URL,
    )

sessionLocal = sessionmaker(
    autocommit = False, 
    autoflush = False, 
    bind = engine
    )

def get_db():
    session = sessionLocal()
    try:
        yield session
    finally:
        session.close()
    
class Base(DeclarativeBase):
    pass


