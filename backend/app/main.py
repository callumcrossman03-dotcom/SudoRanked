from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import auth_router, leaderboard, practice, puzzles

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SudoRank API", version="0.1.0")

# Vite's default dev server ports. Loosen/tighten this once the frontend
# has a real deployed origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(puzzles.router)
app.include_router(leaderboard.router)
app.include_router(practice.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
