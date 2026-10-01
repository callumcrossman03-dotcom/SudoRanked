import time

from app import services, sudoku


def test_points_for_rank_curve():
    assert services.points_for_rank(1) == 100
    assert services.points_for_rank(2) == 90
    assert services.points_for_rank(3) == 80
    assert services.points_for_rank(10) == 10
    assert services.points_for_rank(50) == 10  # floors at 10, never negative


def _solve_and_finish(client, headers, daily_grid, delay=0.0):
    client.post("/api/puzzle/daily/start", headers=headers)
    if delay:
        time.sleep(delay)
    solved = sudoku.solve(daily_grid)
    return client.post("/api/puzzle/daily/submit", json={"grid": solved}, headers=headers).json()


def test_daily_leaderboard_empty_before_any_submissions(client):
    resp = client.get("/api/leaderboard/daily")
    assert resp.status_code == 200
    assert resp.json() == []


def test_daily_leaderboard_ranks_by_speed(client, register_user):
    alice = register_user("alice")
    bob = register_user("bob")

    daily_grid = client.get("/api/puzzle/daily", headers=alice).json()["grid"]

    # Alice takes longer than Bob.
    _solve_and_finish(client, alice, daily_grid, delay=0.1)
    _solve_and_finish(client, bob, daily_grid, delay=0.0)

    board = client.get("/api/leaderboard/daily").json()
    assert [entry["username"] for entry in board] == ["bob", "alice"]
    assert board[0]["rank"] == 1
    assert board[0]["points"] == 100
    assert board[1]["rank"] == 2
    assert board[1]["points"] == 90


def test_daily_leaderboard_excludes_incorrect_and_unfinished_attempts(client, register_user):
    alice = register_user("alice")
    bob = register_user("bob")
    daily = client.get("/api/puzzle/daily", headers=alice).json()

    # Alice solves correctly.
    _solve_and_finish(client, alice, daily["grid"])

    # Bob starts but never submits.
    client.post("/api/puzzle/daily/start", headers=bob)

    board = client.get("/api/leaderboard/daily").json()
    assert [entry["username"] for entry in board] == ["alice"]


def test_alltime_leaderboard_sums_points_and_days_played(client, register_user):
    alice = register_user("alice")
    bob = register_user("bob")
    daily_grid = client.get("/api/puzzle/daily", headers=alice).json()["grid"]

    _solve_and_finish(client, bob, daily_grid, delay=0.0)
    _solve_and_finish(client, alice, daily_grid, delay=0.1)

    board = client.get("/api/leaderboard/alltime").json()
    assert board[0]["username"] == "bob"
    assert board[0]["total_points"] == 100
    assert board[0]["days_played"] == 1
    assert board[1]["username"] == "alice"
    assert board[1]["total_points"] == 90
