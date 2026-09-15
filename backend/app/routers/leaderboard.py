import datetime
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, services
from ..database import get_db

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/daily", response_model=list)
def daily_leaderboard(db: Session = Depends(get_db)):
    today = datetime.date.today()
    daily = (
        db.query(models.DailyPuzzle)
        .filter(models.DailyPuzzle.puzzle_date == today)
        .first()
    )
    if not daily:
        return []

    ranked = services.rank_daily_attempts(db, daily.id)
    return [
        {
            "rank": rank,
            "username": attempt.user.username,
            "elapsed_seconds": round(attempt.elapsed_seconds, 2),
            "points": points,
        }
        for rank, attempt, points in ranked
    ]


@router.get("/alltime", response_model=list)
def alltime_leaderboard(db: Session = Depends(get_db)):
    """
    Sums points earned across every daily puzzle's rankings. Recomputed on
    request rather than stored, which is fine at MVP scale (refresh-based
    leaderboard, per the Sprint 1 design) and avoids point totals ever
    drifting out of sync with the underlying attempts.
    """
    totals = defaultdict(int)
    days_played = defaultdict(int)

    all_daily_puzzles = db.query(models.DailyPuzzle).all()
    for daily in all_daily_puzzles:
        ranked = services.rank_daily_attempts(db, daily.id)
        for rank, attempt, points in ranked:
            totals[attempt.user.username] += points
            days_played[attempt.user.username] += 1

    leaderboard = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {
            "rank": i + 1,
            "username": username,
            "total_points": total,
            "days_played": days_played[username],
        }
        for i, (username, total) in enumerate(leaderboard)
    ]
