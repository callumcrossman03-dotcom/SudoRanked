import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---- Auth ----

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    # bcrypt has a hard 72-byte limit on the input secret.
    password: str = Field(min_length=6, max_length=72)


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Puzzle grids ----

GridType = List[int]  # length-81 list, 0 = blank


class DailyPuzzleOut(BaseModel):
    puzzle_date: datetime.date
    difficulty: str
    grid: GridType
    attempt_status: str  # "not_started" | "in_progress" | "completed"
    elapsed_seconds: Optional[float] = None
    started_at: Optional[datetime.datetime] = None  # for resuming the client-side timer display


class SubmitGrid(BaseModel):
    grid: GridType


class SubmitResult(BaseModel):
    is_correct: bool
    elapsed_seconds: Optional[float] = None
    message: str


class PracticePuzzleOut(BaseModel):
    id: int
    difficulty: str
    grid: GridType


class PracticeCheckResult(BaseModel):
    is_correct: bool
    incorrect_cells: List[int] = []


# ---- Leaderboards ----

class DailyLeaderboardEntry(BaseModel):
    rank: int
    username: str
    elapsed_seconds: float
    points: int


class AllTimeLeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_points: int
    days_played: int
