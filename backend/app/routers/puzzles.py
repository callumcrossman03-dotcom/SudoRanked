import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, models, schemas, services, sudoku
from ..database import get_db

router = APIRouter(prefix="/api/puzzle", tags=["daily puzzle"])


def _today():
    return datetime.date.today()


@router.get("/daily", response_model=schemas.DailyPuzzleOut)
def get_daily_puzzle(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    daily = services.get_or_create_daily_puzzle(db, _today())
    grid = json.loads(daily.puzzle_json)

    attempt = (
        db.query(models.DailyAttempt)
        .filter(
            models.DailyAttempt.user_id == current_user.id,
            models.DailyAttempt.daily_puzzle_id == daily.id,
        )
        .first()
    )

    if attempt is None:
        status_str = "not_started"
        elapsed = None
    elif attempt.is_correct:
        status_str = "completed"
        elapsed = attempt.elapsed_seconds
    else:
        status_str = "in_progress"
        elapsed = None

    return schemas.DailyPuzzleOut(
        puzzle_date=daily.puzzle_date,
        difficulty=daily.difficulty,
        grid=grid,
        attempt_status=status_str,
        elapsed_seconds=elapsed,
        started_at=attempt.started_at if attempt else None,
    )


@router.post("/daily/start", response_model=schemas.DailyPuzzleOut)
def start_daily_puzzle(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    daily = services.get_or_create_daily_puzzle(db, _today())

    attempt = (
        db.query(models.DailyAttempt)
        .filter(
            models.DailyAttempt.user_id == current_user.id,
            models.DailyAttempt.daily_puzzle_id == daily.id,
        )
        .first()
    )

    if attempt is None:
        # Server stamps the start time -- the client never supplies this.
        attempt = models.DailyAttempt(
            user_id=current_user.id,
            daily_puzzle_id=daily.id,
            started_at=datetime.datetime.utcnow(),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    elif attempt.is_correct:
        raise HTTPException(status_code=400, detail="You already completed today's puzzle")
    # If already started but not finished, just fall through and return
    # current state (idempotent -- refreshing the page shouldn't reset the clock).

    grid = json.loads(daily.puzzle_json)
    return schemas.DailyPuzzleOut(
        puzzle_date=daily.puzzle_date,
        difficulty=daily.difficulty,
        grid=grid,
        attempt_status="completed" if attempt.is_correct else "in_progress",
        elapsed_seconds=attempt.elapsed_seconds,
        started_at=attempt.started_at,
    )


@router.post("/daily/submit", response_model=schemas.SubmitResult)
def submit_daily_puzzle(
    payload: schemas.SubmitGrid,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    daily = services.get_or_create_daily_puzzle(db, _today())

    attempt = (
        db.query(models.DailyAttempt)
        .filter(
            models.DailyAttempt.user_id == current_user.id,
            models.DailyAttempt.daily_puzzle_id == daily.id,
        )
        .first()
    )
    if attempt is None or attempt.started_at is None:
        raise HTTPException(
            status_code=400, detail="You must start today's puzzle before submitting"
        )
    if attempt.is_correct:
        return schemas.SubmitResult(
            is_correct=True,
            elapsed_seconds=attempt.elapsed_seconds,
            message="Already completed today's puzzle.",
        )

    if len(payload.grid) != 81:
        raise HTTPException(status_code=400, detail="Grid must contain 81 cells")

    solution = json.loads(daily.solution_json)
    is_correct = sudoku.matches_solution(payload.grid, solution)

    attempt.attempt_count = (attempt.attempt_count or 0) + 1

    if is_correct:
        # Server stamps submit time; elapsed is computed server-side only.
        submitted_at = datetime.datetime.utcnow()
        attempt.submitted_at = submitted_at
        attempt.elapsed_seconds = (submitted_at - attempt.started_at).total_seconds()
        attempt.is_correct = True

    db.commit()

    return schemas.SubmitResult(
        is_correct=is_correct,
        elapsed_seconds=attempt.elapsed_seconds if is_correct else None,
        message="Correct! Time recorded." if is_correct else "Not quite -- keep trying.",
    )
