
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False,
        default="quality_engineer"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


# =========================================================
# INSPECTION
# =========================================================

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    image_path = Column(
        String(500),
        nullable=False
    )

    product_category = Column(
        String(100),
        nullable=False
    )

    prediction = Column(
        String(50),
        nullable=False
    )

    anomaly_score = Column(
        String(50),
        nullable=False
    )

    threshold = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )