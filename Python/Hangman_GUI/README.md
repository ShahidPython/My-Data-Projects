# Hangman (CLI + GUI)

A clean, testable Hangman game implemented in Python with:
- **Core game logic** isolated in `hangman/core.py`
- **CLI** interface in `hangman/cli.py`
- **Tkinter GUI** in `hangman/gui.py`
- **Single entrypoint** via `main.py`
- **Unit tests** for core logic

## Features
- Configurable lives
- Repeated guess protection
- Win/lose detection
- Random word selection from a curated list
- Clean separation of concerns

## Quick Start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
Run (CLI)
python main.py --mode cli
Run (GUI)
python main.py --mode gui
Run Tests
pytest -q
Project Structure
css
Copy
Edit
hangman-cli-gui/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ requirements.txt
├─ main.py
├─ hangman/
│  ├─ __init__.py
│  ├─ core.py
│  ├─ cli.py
│  └─ gui.py
└─ tests/
   └─ test_core.py
Notes
The game uses a built-in word list (no internet/files required).

You can inject your own word list by passing words=[...] to HangmanGame.

License
MIT