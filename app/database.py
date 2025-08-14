from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite. The database file will be named "app.db".
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Create the SQLAlchemy engine.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session local class to manage database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models.
Base = declarative_base()

# Dependency to get a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()