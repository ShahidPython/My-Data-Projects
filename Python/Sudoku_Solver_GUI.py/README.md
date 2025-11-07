# 🧩 Sudoku Solver (CLI + Tkinter GUI)

A clean, professional Python project that solves 9×9 Sudoku puzzles with a fast backtracking solver enhanced by MRV (minimum remaining values) and forward-checking. Includes both a **CLI** and an enhanced **Tkinter GUI** with modern styling.

![Sudoku Solver](https://img.shields.io/badge/Python-3.8%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features
- Deterministic, correct solver for standard 9×9 Sudoku
- Heuristics: **MRV** + **forward checking**
- **CLI** for batch or file-based solving
- **Enhanced Tkinter GUI** with modern colors, conflict highlighting, load/save, and status bar
- Unit tests using **pytest**

## 🚀 Quick Start

### 1) Create a virtual environment & install dependencies
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
2) Run the application
GUI Mode (Recommended)

bash
python main.py --mode gui
CLI Mode

bash
python main.py --mode cli --in tests/puzzles/easy.sdk
# or pass a flat string of 81 digits (0 for empty)
python main.py --mode cli --puzzle 530070000600195000098000060800060003400803001700020006060000280000419005000080079
3) Run tests
bash
pytest -q
📁 Input Format
Text files with 9 lines of 9 digits each (0 for empty) are supported (e.g., tests/puzzles/easy.sdk).

CLI also accepts a single 81-character string of digits.

🎨 Enhanced GUI Features
Modern color scheme with subtle gradients

Visual feedback for conflicts and solutions

Responsive design with improved spacing

Status updates with timing information

Intuitive controls with hover effects

🗂️ Project Layout
text
sudoku-solver/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ requirements.txt
├─ main.py
├─ sudoku/
│  ├─ __init__.py
│  ├─ board.py
│  ├─ solver.py
│  ├─ cli.py
│  └─ gui.py
└─ tests/
   ├─ test_board.py
   ├─ test_solver.py
   └─ puzzles/
      ├─ easy.sdk
      ├─ hard.sdk
      └─ evil.sdk
📝 Notes
Tkinter ships with Python. If your Python build lacks it, install a Tk-enabled build.

The solver is aimed at correctness and cleanliness. It is not a human-style explainable solver.

📄 License: MIT