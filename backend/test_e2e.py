"""
Manual end-to-end smoke test against a running local server -- exercises
the whole user flow the way the frontend will. The real regression suite
is pytest-based now (see backend/tests/); this script is still handy as a
quick sanity check against an actual running server.
"""
import sys
import time

import requests

sys.path.insert(0, ".")
from app import sudoku  # noqa: E402

BASE = "http://127.0.0.1:8000"


def register_and_login(username, password="hunter22"):
    requests.post(f"{BASE}/api/auth/register", json={"username": username, "password": password})
    resp = requests.post(
        f"{BASE}/api/auth/login",
        data={"username": username, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    alice_token = register_and_login("alice_e2e")
    bob_token = register_and_login("bob_e2e")

    # --- Alice's flow ---
    resp = requests.get(f"{BASE}/api/puzzle/daily", headers=auth_header(alice_token))
    resp.raise_for_status()
    daily = resp.json()
    print("Daily puzzle fetched. attempt_status:", daily["attempt_status"])
    assert daily["attempt_status"] == "not_started"

    resp = requests.post(f"{BASE}/api/puzzle/daily/start", headers=auth_header(alice_token))
    resp.raise_for_status()
    print("Alice started. status:", resp.json()["attempt_status"])

    puzzle_grid = daily["grid"]
    solved = sudoku.solve(puzzle_grid)
    assert solved is not None, "solver failed on served puzzle -- bug!"

    # Submit an intentionally wrong grid first.
    wrong_grid = list(solved)
    wrong_grid[0], wrong_grid[1] = wrong_grid[1], wrong_grid[0]
    resp = requests.post(
        f"{BASE}/api/puzzle/daily/submit", json={"grid": wrong_grid}, headers=auth_header(alice_token)
    )
    resp.raise_for_status()
    result = resp.json()
    print("Alice wrong submission ->", result)
    assert result["is_correct"] is False

    time.sleep(1.2)  # simulate solve time so elapsed_seconds is meaningfully > 0

    resp = requests.post(
        f"{BASE}/api/puzzle/daily/submit", json={"grid": solved}, headers=auth_header(alice_token)
    )
    resp.raise_for_status()
    result = resp.json()
    print("Alice correct submission ->", result)
    assert result["is_correct"] is True
    assert result["elapsed_seconds"] > 1.0

    # Re-submitting after completion should short-circuit cleanly.
    resp = requests.post(
        f"{BASE}/api/puzzle/daily/submit", json={"grid": solved}, headers=auth_header(alice_token)
    )
    print("Alice re-submit after completion ->", resp.json())

    # --- Bob's flow: starts later, finishes faster than Alice's total elapsed ---
    resp = requests.post(f"{BASE}/api/puzzle/daily/start", headers=auth_header(bob_token))
    resp.raise_for_status()
    time.sleep(0.3)
    resp = requests.post(
        f"{BASE}/api/puzzle/daily/submit", json={"grid": solved}, headers=auth_header(bob_token)
    )
    result = resp.json()
    print("Bob correct submission ->", result)
    assert result["elapsed_seconds"] < 1.0

    # --- Leaderboards ---
    resp = requests.get(f"{BASE}/api/leaderboard/daily")
    resp.raise_for_status()
    print("Daily leaderboard:", resp.json())
    board = resp.json()
    assert board[0]["username"] == "bob_e2e", "bob should rank #1 (faster time)"
    assert board[0]["points"] == 100
    assert board[1]["points"] == 90

    resp = requests.get(f"{BASE}/api/leaderboard/alltime")
    resp.raise_for_status()
    print("All-time leaderboard:", resp.json())

    # --- Practice mode ---
    resp = requests.post(f"{BASE}/api/practice/new", params={"difficulty": "easy"})
    resp.raise_for_status()
    practice = resp.json()
    print("Practice puzzle id:", practice["id"], "clues:", sum(1 for v in practice["grid"] if v))

    practice_solved = sudoku.solve(practice["grid"])
    resp = requests.post(
        f"{BASE}/api/practice/{practice['id']}/check", json={"grid": practice_solved}
    )
    resp.raise_for_status()
    print("Practice check (correct solution) ->", resp.json())
    assert resp.json()["is_correct"] is True

    bad = list(practice_solved)
    bad[0] = bad[0] % 9 + 1  # guaranteed to differ mod 9 arithmetic
    resp = requests.post(f"{BASE}/api/practice/{practice['id']}/check", json={"grid": bad})
    print("Practice check (wrong solution) ->", resp.json())

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
