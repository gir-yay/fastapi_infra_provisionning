from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_ROOT_USER}:{settings.DATABASE_ROOT_PASSWORD}@{settings.DATABASE_URL}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


