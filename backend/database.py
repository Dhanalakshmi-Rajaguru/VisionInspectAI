import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load variables from .env
load_dotenv()

# Read the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Make sure DATABASE_URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()