"""
app/db.py — Auth Service
─────────────────────────
Database setup and ORM models.
SQLite for development; swap DATABASE_URL in .env for Postgres in production.
"""
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

#Engine
DATABASE_URL = "sqlite:///./auth.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
#Base
class Base(DeclarativeBase):
    pass

#User table
class UserRecord(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
#Refresh token table
class RefreshTokenRecord(Base):
    __tablename__ = "refresh_tokens"
    token_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
#DB init
def init_db() -> None:
    """Create all tables if they don't exist. Called once at startup."""
    Base.metadata.create_all(bind=engine)
#Dependency
def get_db() -> Session:
    """
    FastAPI dependency. Yields a DB session and ensures it closes
    after the request completes, even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()