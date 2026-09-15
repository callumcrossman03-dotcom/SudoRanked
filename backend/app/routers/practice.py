import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, sudoku
from ..database import get_db

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.post("/new", response_model=schemas.PracticePuzzleOut)
def new_practice_puzzle(difficulty: str = "medium", db: Session = Depends(get_db)):
    if difficulty not in sudoku.DIFFICULTY_CLUES:
        difficulty = "medium"

    puzzle, solution = sudoku.generate_puzzle(difficulty)
    row = models.PracticePuzzle(
        puzzle_json=json.dumps(puzzle),
        solution_json=json.dumps(solution),
        difficulty=difficulty,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return schemas.PracticePuzzleOut(id=row.id, difficulty=row.difficulty, grid=puzzle)


@router.post("/{practice_id}/check", response_model=schemas.PracticeCheckResult)
def check_practice_puzzle(
    practice_id: int, payload: schemas.SubmitGrid, db: Session = Depends(get_db)
):
    row = db.query(models.PracticePuzzle).filter(models.PracticePuzzle.id == practice_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Practice puzzle not found")

    if len(payload.grid) != 81:
        raise HTTPException(status_code=400, detail="Grid must contain 81 cells")

    solution = json.loads(row.solution_json)
    incorrect = [i for i in range(81) if payload.grid[i] != solution[i]]

    return schemas.PracticeCheckResult(is_correct=len(incorrect) == 0, incorrect_cells=incorrect)
