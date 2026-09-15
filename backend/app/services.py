import datetime
import json

from sqlalchemy.orm import Session

from . import models, sudoku


def get_or_create_daily_puzzle(db: Session, for_date: datetime.date) -> models.DailyPuzzle:
    """
    Lazy generation: look up today's puzzle; if it doesn't exist yet
    (i.e. nobody has requested it today), generate one and store it so every
    subsequent player that day gets the exact same puzzle.
    """
    existing = (
        db.query(models.DailyPuzzle)
        .filter(models.DailyPuzzle.puzzle_date == for_date)
        .first()
    )
    if existing:
        return existing

    puzzle, solution = sudoku.generate_puzzle("medium")
    row = models.DailyPuzzle(
        puzzle_date=for_date,
        puzzle_json=json.dumps(puzzle),
        solution_json=json.dumps(solution),
        difficulty="medium",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# Simple, transparent scoring curve for the MVP: 1st place gets 100 points,
# decreasing by 10 per rank down to a floor of 10 points for finishing.
# This can be revisited/tuned in a later sprint.
def points_for_rank(rank: int) -> int:
    return max(10, 100 - (rank - 1) * 10)


def rank_daily_attempts(db: Session, daily_puzzle_id: int):
    """
    Return correct attempts for a given daily puzzle, ordered by elapsed
    time ascending (fastest first), each annotated with rank + points.
    """
    attempts = (
        db.query(models.DailyAttempt)
        .filter(
            models.DailyAttempt.daily_puzzle_id == daily_puzzle_id,
            models.DailyAttempt.is_correct.is_(True),
            models.DailyAttempt.elapsed_seconds.isnot(None),
        )
        .order_by(models.DailyAttempt.elapsed_seconds.asc())
        .all()
    )
    results = []
    for idx, attempt in enumerate(attempts):
        rank = idx + 1
        results.append((rank, attempt, points_for_rank(rank)))
    return results
