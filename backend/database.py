import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================================
# VALIDATE DATABASE CONFIGURATION
# ============================================================

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in backend/.env"
    )


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(DATABASE_URL)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()