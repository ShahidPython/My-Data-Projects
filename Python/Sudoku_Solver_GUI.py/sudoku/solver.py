from __future__ import annotations
from typing import Optional
import time
from .board import Board

class SolveStats:
    def __init__(self):
        self.nodes = 0
        self.start = time.perf_counter()
        self.end = None

    @property
    def elapsed(self) -> float:
        return (self.end or time.perf_counter()) - self.start

def solve(board: Board, stats: Optional[SolveStats] = None) -> Optional[Board]:
    """Solve the Sudoku using backtracking with MRV and forward-checking.
    Returns a solved Board or None if unsolvable.
    """
    stats = stats or SolveStats()

    if not board.is_valid():
        stats.end = time.perf_counter()
        return None

    if board.is_complete():
        stats.end = time.perf_counter()
        return board

    mrv = board.find_mrv_cell()
    if mrv is None:
        stats.end = time.perf_counter()
        return board if board.is_valid() else None

    r, c, cand = mrv
    if len(cand) == 0:
        return None

    for v in sorted(cand):
        if board.is_valid_move(r, c, v):
            stats.nodes += 1
            board.grid[r][c] = v
            if _forward_check(board, r, c):
                res = solve(board, stats)
                if res is not None:
                    return res
            board.grid[r][c] = 0

    if stats.end is None:
        stats.end = time.perf_counter()
    return None

def _forward_check(board: Board, rr: int, cc: int) -> bool:
    """After placing at (rr,cc), ensure no other empty cell has zero candidates."""
    for r in range(9):
        for c in range(9):
            if board.grid[r][c] == 0:
                if len(board.candidates(r, c)) == 0:
                    return False
    return True