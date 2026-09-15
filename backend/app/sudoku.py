"""
Sudoku generation and validation engine.

Design (per Sprint 1 Software Design Plan):
- Backtracking / constraint-satisfaction generator.
- Every generated puzzle is verified to have a UNIQUE solution before it is
  handed back to the caller (a puzzle with multiple solutions isn't fair for
  a competitive, ranked mode).

A "grid" is always a flat list of 81 ints, row-major, 0 = blank.
"""

import random

SIZE = 9
BOX = 3


def _row_col_box(index: int):
    row = index // SIZE
    col = index % SIZE
    box = (row // BOX) * BOX + (col // BOX)
    return row, col, box


# Precompute which cell indices share a row/col/box with each index, for speed.
_PEERS = []
for i in range(SIZE * SIZE):
    r, c, b = _row_col_box(i)
    peers = set()
    for j in range(SIZE * SIZE):
        rj, cj, bj = _row_col_box(j)
        if j != i and (rj == r or cj == c or bj == b):
            peers.add(j)
    _PEERS.append(peers)


def is_valid_placement(grid, index, value):
    for p in _PEERS[index]:
        if grid[p] == value:
            return False
    return True


def _find_empty(grid):
    # Simple first-empty heuristic is fine at 9x9 scale.
    for i, v in enumerate(grid):
        if v == 0:
            return i
    return -1


def generate_full_grid():
    """Produce a complete, valid, randomly-shuffled 9x9 Sudoku solution grid."""
    grid = [0] * (SIZE * SIZE)

    def backtrack(pos=0):
        if pos == SIZE * SIZE:
            return True
        if grid[pos] != 0:
            return backtrack(pos + 1)
        candidates = list(range(1, 10))
        random.shuffle(candidates)
        for val in candidates:
            if is_valid_placement(grid, pos, val):
                grid[pos] = val
                if backtrack(pos + 1):
                    return True
                grid[pos] = 0
        return False

    backtrack(0)
    return grid


def count_solutions(grid, limit=2):
    """
    Count solutions to `grid`, stopping early once `limit` is reached.
    Used to verify a carved puzzle has exactly one solution, without paying
    the cost of finding every solution to a puzzle that's actually ambiguous.
    """
    work = list(grid)
    count = 0

    def backtrack():
        nonlocal count
        if count >= limit:
            return
        idx = _find_empty(work)
        if idx == -1:
            count += 1
            return
        for val in range(1, 10):
            if is_valid_placement(work, idx, val):
                work[idx] = val
                backtrack()
                work[idx] = 0
                if count >= limit:
                    return

    backtrack()
    return count


def solve(grid):
    """Return a solved copy of grid (assumes exactly one solution), or None."""
    work = list(grid)

    def backtrack():
        idx = _find_empty(work)
        if idx == -1:
            return True
        for val in range(1, 10):
            if is_valid_placement(work, idx, val):
                work[idx] = val
                if backtrack():
                    return True
                work[idx] = 0
        return False

    if backtrack():
        return work
    return None


DIFFICULTY_CLUES = {
    "easy": 42,
    "medium": 34,
    "hard": 28,
}


def generate_puzzle(difficulty="medium"):
    """
    Generate a (puzzle, solution) pair. `puzzle` has `target_clues` filled
    cells and is guaranteed to have exactly one solution.
    """
    target_clues = DIFFICULTY_CLUES.get(difficulty, DIFFICULTY_CLUES["medium"])
    solution = generate_full_grid()
    puzzle = list(solution)

    cell_order = list(range(SIZE * SIZE))
    random.shuffle(cell_order)

    clues_remaining = SIZE * SIZE
    for idx in cell_order:
        if clues_remaining <= target_clues:
            break
        removed_value = puzzle[idx]
        puzzle[idx] = 0

        if count_solutions(puzzle, limit=2) != 1:
            # Removing this cell made the puzzle ambiguous; put it back.
            puzzle[idx] = removed_value
        else:
            clues_remaining -= 1

    return puzzle, solution


def is_complete_and_valid(grid):
    """True if grid has no blanks and every row/col/box is a valid 1-9 set."""
    if any(v == 0 for v in grid):
        return False
    full_set = set(range(1, 10))
    for r in range(SIZE):
        row = grid[r * SIZE:(r + 1) * SIZE]
        if set(row) != full_set:
            return False
    for c in range(SIZE):
        col = [grid[r * SIZE + c] for r in range(SIZE)]
        if set(col) != full_set:
            return False
    for br in range(0, SIZE, BOX):
        for bc in range(0, SIZE, BOX):
            box = [grid[(br + dr) * SIZE + (bc + dc)] for dr in range(BOX) for dc in range(BOX)]
            if set(box) != full_set:
                return False
    return True


def matches_solution(submitted_grid, solution_grid):
    return submitted_grid == solution_grid
