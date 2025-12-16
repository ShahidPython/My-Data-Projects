from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional
from .board import Board
from .solver import solve, SolveStats

CELL_W = 2
FONT = ("Segoe UI", 14, "bold")
BTN_FONT = ("Segoe UI", 10, "bold")
STATUS_FONT = ("Segoe UI", 9)

# Color scheme
BG_COLOR = "#f0f0f0"
CELL_BG = "#ffffff"
CELL_BG_ALT = "#f8f8f8"
BORDER_COLOR = "#cccccc"
HIGHLIGHT_COLOR = "#e6f3ff"
CONFLICT_COLOR = "#ffcccc"
SOLVED_COLOR = "#d4edda"
BTN_COLOR = "#4a7abc"
BTN_HOVER = "#3a6aac"
BTN_TEXT = "#ffffff"
STATUS_BG = "#e9ecef"
STATUS_TEXT = "#495057"

# Example puzzles for different difficulty levels
EXAMPLE_PUZZLES = {
    "Easy": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "Medium": "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
    "Hard": "800000000003600000070090200050007000000045700000100030001000068008500010090000400",
    "Expert": "100000000000000000000000000000000000000000000000000000000000000000000000000000000"
}

def run_gui():
    app = SudokuApp()
    app.mainloop()

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self, master=master, **kw)
        self.default_bg = self.cget("background")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(background=BTN_HOVER)

    def on_leave(self, e):
        self.config(background=BTN_COLOR)

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Solver")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        # Main frame
        main_frame = tk.Frame(self, bg=BG_COLOR, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="SUDOKU SOLVER", font=("Segoe UI", 16, "bold"), 
                        bg=BG_COLOR, fg="#2c3e50")
        title.grid(row=0, column=0, pady=(0, 10))
        
        # Difficulty selection frame
        diff_frame = tk.Frame(main_frame, bg=BG_COLOR)
        diff_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        
        tk.Label(diff_frame, text="Difficulty:", font=("Segoe UI", 10), 
                bg=BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
        
        self.difficulty_var = tk.StringVar(value="Easy")
        difficulty_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_var, 
                                       values=list(EXAMPLE_PUZZLES.keys()), 
                                       state="readonly", width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=(0, 10))
        difficulty_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)
        
        # Load example button
        load_example_btn = HoverButton(diff_frame, text="Load Example", command=self.on_load_example,
                                      font=BTN_FONT, bg="#28a745", fg=BTN_TEXT, relief="flat", 
                                      padx=10, pady=4, cursor="hand2")
        load_example_btn.pack(side=tk.LEFT)
        
        # Sudoku grid frame
        grid_frame = tk.Frame(main_frame, bg=BORDER_COLOR, padx=4, pady=4)
        grid_frame.grid(row=2, column=0, pady=(0, 15))
        
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        vcmd = (self.register(self._validate_digit), "%P")

        for r in range(9):
            for c in range(9):
                # Alternate cell background for visual grouping
                cell_bg = CELL_BG_ALT if (r // 3 + c // 3) % 2 == 0 else CELL_BG
                e = tk.Entry(grid_frame, width=CELL_W, justify="center", 
                            validate="key", validatecommand=vcmd, font=FONT,
                            bg=cell_bg, relief="solid", borderwidth=1,
                            highlightthickness=1, highlightcolor="#3498db")
                padx = (4, 6) if c % 3 == 2 and c != 8 else (4, 2)
                pady = (4, 6) if r % 3 == 2 and r != 8 else (4, 2)
                e.grid(row=r, column=c, padx=padx, pady=pady, ipady=5)
                self.entries[r][c] = e

        # Button frame
        btn_frame = tk.Frame(main_frame, bg=BG_COLOR, pady=10)
        btn_frame.grid(row=3, column=0, sticky="ew")
        
        buttons = [
            ("Solve", self.on_solve),
            ("Check", self.on_check),
            ("Clear", self.on_clear),
            ("Load", self.on_load),
            ("Save", self.on_save)
        ]
        
        for text, command in buttons:
            btn = HoverButton(btn_frame, text=text, command=command, font=BTN_FONT,
                            bg=BTN_COLOR, fg=BTN_TEXT, relief="flat", padx=12, pady=6,
                            cursor="hand2")
            btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        status_frame = tk.Frame(main_frame, bg=STATUS_BG, height=22)
        status_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        status_frame.grid_propagate(False)
        
        self.status = tk.StringVar(value="Ready. Enter a puzzle or load from file.")
        status_label = tk.Label(status_frame, textvariable=self.status, anchor="w", 
                               padx=10, font=STATUS_FONT, bg=STATUS_BG, fg=STATUS_TEXT)
        status_label.pack(fill=tk.X)

    def _validate_digit(self, P: str) -> bool:
        if P == "": return True
        if len(P) > 1: return False
        return P in "123456789"

    def on_difficulty_change(self, event):
        """When difficulty level is changed"""
        difficulty = self.difficulty_var.get()
        self.status.set(f"Selected difficulty: {difficulty}")

    def on_load_example(self):
        """Load an example puzzle based on selected difficulty"""
        difficulty = self.difficulty_var.get()
        if difficulty in EXAMPLE_PUZZLES:
            puzzle = EXAMPLE_PUZZLES[difficulty]
            board = Board.from_flat_string(puzzle)
            self._write_board(board)
            self._highlight_conflicts(board)
            self.status.set(f"Loaded {difficulty} example puzzle.")
        else:
            messagebox.showerror("Error", "Invalid difficulty level selected.")

    def on_clear(self):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].delete(0, tk.END)
                # Reset to original background
                cell_bg = CELL_BG_ALT if (r // 3 + c // 3) % 2 == 0 else CELL_BG
                self.entries[r][c].config(bg=cell_bg)
        self.status.set("Cleared. Ready for new puzzle.")

    def on_check(self):
        try:
            board = self._read_board()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        
        self._highlight_conflicts(board)
        if board.is_valid():
            self.status.set("✓ Board is valid so far.")
        else:
            self.status.set("✗ Conflicts found in the puzzle.")

    def on_solve(self):
        try:
            board = self._read_board()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not board.is_valid():
            messagebox.showerror("Invalid Puzzle", "Board has conflicts. Please fix them first.")
            return

        self.status.set("Solving...")
        self.update()
        
        stats = SolveStats()
        res = solve(board, stats)
        
        if res is None:
            messagebox.showinfo("No Solution", "No solution found for this puzzle.")
            self.status.set("No solution found.")
            return

        self._write_board(res)
        self._highlight_conflicts(res, solved=True)
        self.status.set(f"Solved! Time: {stats.elapsed:.3f}s, Nodes: {stats.nodes}")

    def on_load(self):
        path = filedialog.askopenfilename(
            title="Open Sudoku Puzzle", 
            filetypes=[("Sudoku files", "*.sdk *.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                board = Board.from_lines(f.readlines())
            self._write_board(board)
            self._highlight_conflicts(board)
            self.status.set(f"Loaded: {path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load puzzle: {str(e)}")

    def on_save(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".sdk", 
            filetypes=[("Sudoku file", "*.sdk"), ("Text file", "*.txt")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for r in range(9):
                    line = ''.join(self._cell_value_str(r,c) for c in range(9))
                    f.write(line + "\n")
            self.status.set(f"Saved: {path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save puzzle: {str(e)}")

    def _read_board(self) -> Board:
        rows = []
        for r in range(9):
            s = ''.join(self._cell_value_str(r, c) for c in range(9))
            rows.append(s)
        return Board.from_lines(rows)

    def _write_board(self, board: Board):
        for r in range(9):
            for c in range(9):
                e = self.entries[r][c]
                e.delete(0, tk.END)
                v = board.grid[r][c]
                if v != 0:
                    e.insert(0, str(v))

    def _cell_value_str(self, r: int, c: int) -> str:
        v = self.entries[r][c].get().strip()
        if v == "": return "0"
        if not v.isdigit(): return "0"
        d = int(v)
        if d < 0 or d > 9: return "0"
        return str(d)

    def _highlight_conflicts(self, board: Board, solved: bool = False):
        # Reset all cells to original background
        for r in range(9):
            for c in range(9):
                cell_bg = CELL_BG_ALT if (r // 3 + c // 3) % 2 == 0 else CELL_BG
                self.entries[r][c].config(bg=cell_bg)

        # Highlight conflicts
        for r in range(9):
            for c in range(9):
                v = board.grid[r][c]
                if v == 0:
                    continue
                board.grid[r][c] = 0
                ok = board.is_valid_move(r, c, v)
                board.grid[r][c] = v
                if not ok:
                    self.entries[r][c].config(bg=CONFLICT_COLOR)

        # Highlight solved cells
        if solved:
            for r in range(9):
                for c in range(9):
                    if board.grid[r][c] != 0 and self.entries[r][c]['bg'] not in [CONFLICT_COLOR]:
                        self.entries[r][c].config(bg=SOLVED_COLOR)