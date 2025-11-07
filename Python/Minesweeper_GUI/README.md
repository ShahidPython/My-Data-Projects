# Minesweeper in Python 🎮

All-in-one Minesweeper project showing progression:
- CLI (terminal)
- GUI (Tkinter)
- GUI (PyGame)
- AI Solver (logic-based)
- Multiplayer (local hot-seat)
- Difficulty levels (Beginner / Intermediate / Expert + Custom)

## Features
- Multiple interfaces: CLI, Tkinter GUI, PyGame GUI
- AI solver with logic-based gameplay
- Hot-seat multiplayer mode
- Custom difficulty settings
- Sound effects (optional)
- Comprehensive test suite

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
Assets
Put your assets in assets/ folder:

icon.png (window icon)

click.wav (short tick sound)

explosion.wav (boom when a mine is hit)

win.wav (victory sound)

Controls
CLI:
Reveal: r row col

Flag: f row col

Chord (reveal neighbors): c row col

Quit: q

Tkinter GUI:
Left-click: reveal

Right-click: flag/unflag

Middle-click: chord (reveal neighbors of numbered cells)

PyGame GUI:
Left-click: reveal

Right-click: flag/unflag

Middle-click: chord (reveal neighbors of numbered cells)

R: restart

Esc: quit

Notes
Sounds are optional. If missing, the game still runs.

Tkinter uses pygame.mixer for sounds if available (gracefully degrades).

The AI solver uses deterministic rules with random guessing as fallback.

Project Structure
text
minesweeper/
├── main.py              # Main menu
├── minesweeper/         # Package directory
│   ├── __init__.py     # Package initialization
│   ├── core.py         # Core game logic
│   ├── cli.py          # Command-line interface
│   ├── gui_tkinter.py  # Tkinter GUI
│   ├── gui_pygame.py   # PyGame GUI
│   ├── ai_solver.py    # AI solver
│   ├── multiplayer.py  # Multiplayer mode
│   └── difficulty.py   # Difficulty selection
├── tests/              # Test suite
│   ├── test_core.py
│   ├── test_ai.py
│   └── test_difficulty.py
├── assets/             # Game assets (optional)
│   ├── icon.png
│   ├── click.wav
│   ├── explosion.wav
│   └── win.wav
├── requirements.txt    # Dependencies
└── README.md          # This file
License
MIT - see LICENSE file for details.