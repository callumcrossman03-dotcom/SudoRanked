import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Overridable so the test suite can point at an isolated in-memory database
# instead of the real dev file (see backend/tests/conftest.py).
SQLALCHEMY_DATABASE_URL = os.environ.get("SUDORANK_DATABASE_URL", "sqlite:///./sudorank.db")

engine_kwargs = {"connect_args": {"check_same_thread": False}}
if SQLALCHEMY_DATABASE_URL == "sqlite:///:memory:":
    # A plain in-memory sqlite db is per-connection -- without a shared
    # StaticPool, each new session would see a blank database.
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
