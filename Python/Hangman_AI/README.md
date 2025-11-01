# Hangman AI-based (Advanced)

A Hangman game with an AI solver.

Files:
- `hangman/core.py` — game logic (word selection, guesses, lives).
- `hangman/ai_solver.py` — AI that guesses letters using frequency + pattern filtering.
- `hangman/cli.py` — command line interface to play vs AI or let AI solve a secret word.
- `hangman/gui.py` — simple Tkinter GUI to play against the AI (optional).
- `tests/test_ai_solver.py` — basic tests for the solver.

## Install & run

Create venv and install:
```bash
python -m venv venv
# activate venv (Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

Run CLI:

python main.py --mode play


Let AI solve an entered word:

python main.py --mode ai


Run tests:

pytest -q

Notes

AISolver is frequency + pattern filtering based and easy to extend; swap internals for ML-based ranking.

To use a bigger wordlist, provide a path in CLI functions or replace the builtin list in core.py.