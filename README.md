# SudoRank

A competitive daily Sudoku app. Everyone gets the same puzzle each day; the
server times how long it takes you to solve it, and a leaderboard ranks
players by speed. There's also an unlimited, unranked practice mode.


## Project structure

```
sudorank/
  backend/                 FastAPI + SQLAlchemy + SQLite API
    app/
      main.py               app entrypoint, CORS, router wiring
      database.py            SQLAlchemy engine/session setup
      models.py               ORM tables: User, DailyPuzzle, DailyAttempt, PracticePuzzle
      schemas.py                Pydantic request/response shapes
      auth.py                    password hashing (bcrypt) + JWT issuing/verification
      sudoku.py                   puzzle generator, solution counter, solver, validator
      services.py                  lazy daily-puzzle creation + scoring/ranking logic
      routers/
        auth_router.py             /api/auth/*  (register, login, me)
        puzzles.py                  /api/puzzle/*  (daily puzzle, start, submit)
        leaderboard.py                /api/leaderboard/*  (daily, all-time)
        practice.py                    /api/practice/*  (unlimited unranked puzzles)
    tests/                     pytest suite (auth, daily puzzle, leaderboard, practice, sudoku)
    test_e2e.py               manual end-to-end smoke test (see below)
    requirements.txt
    requirements-dev.txt      requirements.txt + pytest/httpx for testing
  frontend/                FastAPI's counterpart: React 19 + Vite
    src/
      api.js                  fetch wrapper for the backend
      App.jsx                  view routing (daily / practice / leaderboard / auth)
      components/
        NavBar.jsx, AuthPanel.jsx, DailyPuzzle.jsx, Leaderboard.jsx,
        Practice.jsx, SudokuBoard.jsx (+ matching .css files)
```

## Running it locally

You need Python 3.10+ and Node 18+.

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```
This starts the API at `http://127.0.0.1:8000` and creates `sudorank.db`
(SQLite) on first run. Interactive API docs are at
`http://127.0.0.1:8000/docs`.

**Frontend** (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```
This starts the app at `http://localhost:5173`. It expects the backend to be
running at `http://127.0.0.1:8000` by default -- copy `.env.example` to
`.env` if you need to point it somewhere else.

## Running the backend tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

39 tests cover auth, the daily-puzzle start/submit/timing flow, leaderboard
ranking and points, practice mode, and the sudoku generator/solver directly.
They run against an isolated in-memory SQLite database (see
`backend/tests/conftest.py`), not the real `sudorank.db`.

`test_e2e.py` still exists separately as a manual smoke test against an
actual *running* server (`python3 test_e2e.py` with the backend up) --
useful for a quick sanity check of the full stack, but the pytest suite is
the real regression coverage now.

## What's working (Sprint 2 MVP)

- Register / log in (hashed passwords, JWT session)
- A single shared puzzle generated per calendar day, lazily on first request
  (guaranteed to have exactly one solution -- see `app/sudoku.py`)
- Start / submit a daily attempt, with the **server** stamping start and
  submit times and computing elapsed time -- the client never reports its
  own timing, so it can't be spoofed by editing the page
- Daily leaderboard, ranked by solve time, with a simple points curve
- All-time leaderboard, summing points across every day played
- Unlimited practice mode (any difficulty, not tied to the leaderboard)

## What's not built yet

- Password reset / account recovery
- Deployment config (this currently only runs locally)
- Visual polish pass, mobile keyboard input refinements, accessibility audit
- Difficulty selection for the *daily* puzzle (practice mode already
  supports it; the daily is fixed at "medium" for now)

See the Engineering Notebook for the fuller Sprint 2 write-up.
