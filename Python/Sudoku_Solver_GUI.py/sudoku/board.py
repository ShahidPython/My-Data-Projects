from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Iterable

Grid = List[List[int]]

@dataclass
class Board:
    grid: Grid  # 9x9 list of ints (0..9), 0 means empty

    @staticmethod
    def from_lines(lines: Iterable[str]) -> "Board":
        rows = []
        for line in lines:
            s = ''.join(ch for ch in line.strip() if ch.isdigit())
            if not s:
                continue
            if len(s) != 9 or any(c not in "0123456789" for c in s):
                raise ValueError("Each non-empty line must contain exactly 9 digits (0-9).")
            rows.append([int(c) for c in s])
        if len(rows) != 9:
            raise ValueError("Expected 9 lines of 9 digits.")
        return Board(rows)

    @staticmethod
    def from_flat_string(s: str) -> "Board":
        s = ''.join(ch for ch in s.strip() if ch.isdigit())
        if len(s) != 81:
            raise ValueError("Flat puzzle must be 81 digits (0 for empty).")
        rows = [[int(s[r*9 + c]) for c in range(9)] for r in range(9)]
        return Board(rows)

    def clone(self) -> "Board":
        return Board([row[:] for row in self.grid])

    def is_complete(self) -> bool:
        return all(all(cell != 0 for cell in row) for row in self.grid) and self.is_valid()

    def row_values(self, r: int) -> set[int]:
        return set(v for v in self.grid[r] if v != 0)

    def col_values(self, c: int) -> set[int]:
        return set(self.grid[r][c] for r in range(9) if self.grid[r][c] != 0)

    def box_values(self, r: int, c: int) -> set[int]:
        br, bc = (r // 3) * 3, (c // 3) * 3
        vals = set()
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                v = self.grid[i][j]
                if v != 0:
                    vals.add(v)
        return vals

    def candidates(self, r: int, c: int) -> set[int]:
        if self.grid[r][c] != 0:
            return set()
        used = self.row_values(r) | self.col_values(c) | self.box_values(r, c)
        return set(range(1, 10)) - used

    def is_valid_move(self, r: int, c: int, v: int) -> bool:
        if v == 0:
            return True
        if v in self.row_values(r): return False
        if v in self.col_values(c): return False
        if v in self.box_values(r, c): return False
        return True

    def is_valid(self) -> bool:
        for r in range(9):
            vals = [v for v in self.grid[r] if v != 0]
            if len(vals) != len(set(vals)):
                return False
        for c in range(9):
            col = [self.grid[r][c] for r in range(9) if self.grid[r][c] != 0]
            if len(col) != len(set(col)):
                return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box = []
                for i in range(br, br+3):
                    for j in range(bc, bc+3):
                        v = self.grid[i][j]
                        if v != 0: box.append(v)
                if len(box) != len(set(box)):
                    return False
        return True

    def find_mrv_cell(self) -> Optional[Tuple[int, int, set[int]]]:
        """Find the empty cell with the fewest candidates (MRV)."""
        best: Optional[Tuple[int, int, set[int]]] = None
        min_count = 10
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    cand = self.candidates(r, c)
                    n = len(cand)
                    if n == 0:
                        return (r, c, set())
                    if n < min_count:
                        min_count = n
                        best = (r, c, cand)
                        if n == 1:
                            return best
        return best

    def __str__(self) -> str:
        lines = []
        for r in range(9):
            if r % 3 == 0 and r != 0:
                lines.append("------+-------+------")
            row = []
            for c in range(9):
                if c % 3 == 0 and c != 0:
                    row.append("|")
                v = self.grid[r][c]
                row.append(str(v) if v != 0 else ".")
            lines.append(" ".join(row))
        return "\n".join(lines)