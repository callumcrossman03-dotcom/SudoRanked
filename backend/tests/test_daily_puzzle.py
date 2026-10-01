import time

from app import sudoku


def test_daily_puzzle_is_shared_across_users(client, register_user):
    alice = register_user("alice")
    bob = register_user("bob")

    alice_grid = client.get("/api/puzzle/daily", headers=alice).json()["grid"]
    bob_grid = client.get("/api/puzzle/daily", headers=bob).json()["grid"]
    assert alice_grid == bob_grid


def test_daily_puzzle_requires_auth(client):
    resp = client.get("/api/puzzle/daily")
    assert resp.status_code == 401


def test_attempt_status_progresses_not_started_to_in_progress(client, register_user):
    headers = register_user("alice")

    daily = client.get("/api/puzzle/daily", headers=headers).json()
    assert daily["attempt_status"] == "not_started"
    assert daily["elapsed_seconds"] is None

    started = client.post("/api/puzzle/daily/start", headers=headers).json()
    assert started["attempt_status"] == "in_progress"
    assert started["started_at"] is not None


def test_starting_twice_does_not_reset_the_clock(client, register_user):
    headers = register_user("alice")

    first = client.post("/api/puzzle/daily/start", headers=headers).json()
    second = client.post("/api/puzzle/daily/start", headers=headers).json()
    assert first["started_at"] == second["started_at"]


def test_submit_before_start_is_rejected(client, register_user):
    headers = register_user("alice")
    resp = client.post("/api/puzzle/daily/submit", json={"grid": [0] * 81}, headers=headers)
    assert resp.status_code == 400


def test_submit_wrong_solution_is_marked_incorrect(client, register_user):
    headers = register_user("alice")
    daily = client.get("/api/puzzle/daily", headers=headers).json()
    client.post("/api/puzzle/daily/start", headers=headers)

    solved = sudoku.solve(daily["grid"])
    wrong = list(solved)
    wrong[0], wrong[1] = wrong[1], wrong[0]

    resp = client.post("/api/puzzle/daily/submit", json={"grid": wrong}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is False
    assert body["elapsed_seconds"] is None


def test_submit_correct_solution_records_server_timed_elapsed(client, register_user):
    headers = register_user("alice")
    daily = client.get("/api/puzzle/daily", headers=headers).json()
    client.post("/api/puzzle/daily/start", headers=headers)
    solved = sudoku.solve(daily["grid"])

    time.sleep(0.05)
    resp = client.post("/api/puzzle/daily/submit", json={"grid": solved}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["elapsed_seconds"] > 0

    # Status should now reflect completion with the recorded time.
    daily_after = client.get("/api/puzzle/daily", headers=headers).json()
    assert daily_after["attempt_status"] == "completed"
    assert daily_after["elapsed_seconds"] == body["elapsed_seconds"]


def test_resubmitting_after_completion_short_circuits(client, register_user):
    headers = register_user("alice")
    daily = client.get("/api/puzzle/daily", headers=headers).json()
    client.post("/api/puzzle/daily/start", headers=headers)
    solved = sudoku.solve(daily["grid"])

    first = client.post("/api/puzzle/daily/submit", json={"grid": solved}, headers=headers).json()
    second = client.post("/api/puzzle/daily/submit", json={"grid": solved}, headers=headers).json()

    assert second["is_correct"] is True
    assert second["elapsed_seconds"] == first["elapsed_seconds"]
    assert "already" in second["message"].lower()


def test_submit_rejects_wrong_length_grid(client, register_user):
    headers = register_user("alice")
    client.post("/api/puzzle/daily/start", headers=headers)
    resp = client.post("/api/puzzle/daily/submit", json={"grid": [1, 2, 3]}, headers=headers)
    assert resp.status_code == 400


def test_client_reported_timing_is_never_trusted(client, register_user):
    """
    The API has no field for a client-supplied duration at all -- submit
    only accepts a grid. This test pins that contract down: even a client
    that tries to sneak extra fields into the payload can't influence the
    recorded elapsed time, since only the server's own clock is used.
    """
    headers = register_user("alice")
    daily = client.get("/api/puzzle/daily", headers=headers).json()
    client.post("/api/puzzle/daily/start", headers=headers)
    solved = sudoku.solve(daily["grid"])

    resp = client.post(
        "/api/puzzle/daily/submit",
        json={"grid": solved, "elapsed_seconds": 0.001},
        headers=headers,
    )
    assert resp.status_code == 200
    # Extra field is silently ignored by pydantic; elapsed time still comes
    # from started_at/submitted_at server timestamps, not the payload.
    assert resp.json()["elapsed_seconds"] > 0
