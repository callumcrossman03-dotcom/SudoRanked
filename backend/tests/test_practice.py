from app import sudoku


def test_new_practice_puzzle_default_difficulty(client):
    resp = client.post("/api/practice/new")
    assert resp.status_code == 200
    body = resp.json()
    assert body["difficulty"] == "medium"
    clues = sum(1 for v in body["grid"] if v != 0)
    assert clues == sudoku.DIFFICULTY_CLUES["medium"]


def test_new_practice_puzzle_respects_requested_difficulty(client):
    resp = client.post("/api/practice/new", params={"difficulty": "hard"})
    body = resp.json()
    assert body["difficulty"] == "hard"
    clues = sum(1 for v in body["grid"] if v != 0)
    assert clues == sudoku.DIFFICULTY_CLUES["hard"]


def test_new_practice_puzzle_falls_back_on_unknown_difficulty(client):
    resp = client.post("/api/practice/new", params={"difficulty": "extreme"})
    assert resp.json()["difficulty"] == "medium"


def test_practice_puzzle_does_not_require_auth(client):
    # Practice mode is explicitly unranked and open -- no login needed.
    resp = client.post("/api/practice/new")
    assert resp.status_code == 200


def test_check_practice_puzzle_correct_solution(client):
    puzzle = client.post("/api/practice/new", params={"difficulty": "easy"}).json()
    solved = sudoku.solve(puzzle["grid"])

    resp = client.post(f"/api/practice/{puzzle['id']}/check", json={"grid": solved})
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["incorrect_cells"] == []


def test_check_practice_puzzle_wrong_solution_lists_incorrect_cells(client):
    puzzle = client.post("/api/practice/new", params={"difficulty": "easy"}).json()
    solved = sudoku.solve(puzzle["grid"])
    wrong = list(solved)
    wrong[0] = wrong[0] % 9 + 1  # guaranteed to differ

    resp = client.post(f"/api/practice/{puzzle['id']}/check", json={"grid": wrong})
    body = resp.json()
    assert body["is_correct"] is False
    assert 0 in body["incorrect_cells"]


def test_check_practice_puzzle_missing_id_returns_404(client):
    resp = client.post("/api/practice/999999/check", json={"grid": [0] * 81})
    assert resp.status_code == 404


def test_check_practice_puzzle_rejects_wrong_length_grid(client):
    puzzle = client.post("/api/practice/new").json()
    resp = client.post(f"/api/practice/{puzzle['id']}/check", json={"grid": [1, 2, 3]})
    assert resp.status_code == 400
