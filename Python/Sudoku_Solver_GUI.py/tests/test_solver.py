from sudoku.board import Board
from sudoku.solver import solve, SolveStats

def _solve_ok(puzzle_lines):
    b = Board.from_lines(puzzle_lines)
    stats = SolveStats()
    res = solve(b, stats)
    assert res is not None, "Puzzle should be solvable"
    assert res.is_complete()
    for r in range(9):
        assert set(res.grid[r]) == set(range(1,10))

def test_easy():
    _solve_ok([
        "530070000",
        "600195000",
        "098000060",
        "800060003",
        "400803001",
        "700020006",
        "060000280",
        "000419005",
        "000080079",
    ])

def test_hard():
    _solve_ok([
        "000000907",
        "000420180",
        "000705026",
        "100904000",
        "050000040",
        "000507009",
        "920108000",
        "034059000",
        "507000000",
    ])
