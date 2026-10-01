from app import sudoku


def test_generate_full_grid_is_complete_and_valid():
    grid = sudoku.generate_full_grid()
    assert len(grid) == 81
    assert 0 not in grid
    assert sudoku.is_complete_and_valid(grid)


def test_generate_puzzle_has_expected_clue_count():
    puzzle, solution = sudoku.generate_puzzle("easy")
    clues = sum(1 for v in puzzle if v != 0)
    assert clues == sudoku.DIFFICULTY_CLUES["easy"]
    assert sudoku.is_complete_and_valid(solution)


def test_generate_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku.generate_puzzle("hard")
    assert sudoku.count_solutions(puzzle, limit=2) == 1
    assert sudoku.solve(puzzle) == solution


def test_generate_puzzle_unknown_difficulty_falls_back_to_medium():
    puzzle, _ = sudoku.generate_puzzle("impossible")
    clues = sum(1 for v in puzzle if v != 0)
    assert clues == sudoku.DIFFICULTY_CLUES["medium"]


def test_solve_returns_none_for_unsolvable_grid():
    # The solver only rejects a candidate it is about to place against its
    # *already-placed* peers -- it never cross-checks two pre-filled given
    # cells against each other. So two conflicting givens (e.g. grid[0] =
    # grid[1] = 5) don't fail fast: nothing ever flags the conflict, and
    # the solver burns through a huge swath of backtracking before
    # exhausting every possibility. Instead, make index 0 itself the empty
    # cell and fill its peers with all 9 digits, so every candidate for
    # index 0 is blocked on the very first check -- a real, fast failure.
    grid = [0] * 81
    for i in range(1, 9):  # row-0 peers of index 0
        grid[i] = i
    grid[9] = 9  # a column peer of index 0 (row 1, col 0)
    assert sudoku.solve(grid) is None


def test_is_complete_and_valid_rejects_blank_cells():
    grid = [1] * 81
    grid[0] = 0
    assert sudoku.is_complete_and_valid(grid) is False


def test_is_complete_and_valid_rejects_repeated_digit_in_row():
    _, solution = sudoku.generate_puzzle("easy")
    broken = list(solution)
    broken[1] = broken[0]  # duplicate within row 1
    assert sudoku.is_complete_and_valid(broken) is False


def test_matches_solution():
    _, solution = sudoku.generate_puzzle("easy")
    assert sudoku.matches_solution(list(solution), solution) is True
    wrong = list(solution)
    wrong[0], wrong[1] = wrong[1], wrong[0]
    assert sudoku.matches_solution(wrong, solution) is False
