import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    attempts = relationship("DailyAttempt", back_populates="user")


class DailyPuzzle(Base):
    """
    One shared puzzle per calendar day (server-generated lazily on first
    request for that date, then reused by every player).
    """

    __tablename__ = "daily_puzzles"

    id = Column(Integer, primary_key=True, index=True)
    puzzle_date = Column(Date, unique=True, index=True, nullable=False)
    puzzle_json = Column(String, nullable=False)  # 81 ints, 0 = blank
    solution_json = Column(String, nullable=False)  # never sent to the client
    difficulty = Column(String, default="medium")
    created_at = Column(DateTime, default=utcnow)

    attempts = relationship("DailyAttempt", back_populates="daily_puzzle")


class DailyAttempt(Base):
    """
    A single user's attempt at a single day's puzzle. Timing is entirely
    server-stamped: `started_at` is set when the server processes the
    /start call, `submitted_at` when it processes /submit. The client never
    supplies elapsed time directly.
    """

    __tablename__ = "daily_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "daily_puzzle_id", name="uq_user_daily_puzzle"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    daily_puzzle_id = Column(Integer, ForeignKey("daily_puzzles.id"), nullable=False)

    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    elapsed_seconds = Column(Float, nullable=True)
    is_correct = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=0)  # number of submit attempts made

    user = relationship("User", back_populates="attempts")
    daily_puzzle = relationship("DailyPuzzle", back_populates="attempts")


class PracticePuzzle(Base):
    """
    Unlimited, unranked puzzles. Same generation pipeline as daily puzzles,
    just not tied to a date or a leaderboard.
    """

    __tablename__ = "practice_puzzles"

    id = Column(Integer, primary_key=True, index=True)
    puzzle_json = Column(String, nullable=False)
    solution_json = Column(String, nullable=False)
    difficulty = Column(String, default="medium")
    created_at = Column(DateTime, default=utcnow)
