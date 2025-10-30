# Advanced Binary Search Variants

A comprehensive Python application demonstrating various binary search algorithms with both CLI and GUI interfaces.

## Features

### Search Algorithms
- **First Occurrence** - Find first occurrence of target
- **Last Occurrence** - Find last occurrence of target  
- **Lower Bound** - Find first element >= target
- **Upper Bound** - Find first element > target
- **Count Occurrences** - Count total occurrences of target
- **Square Root** - Calculate integer square root using binary search
- **Find Rotation Point** - Find pivot in rotated sorted array
- **Search Rotated Array** - Search in rotated sorted array

### Interfaces
- **Command Line Interface (CLI)** - Terminal-based with colorful output
- **Graphical User Interface (GUI)** - Modern Tkinter-based desktop app

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

CLI Mode
python main.py

Then select option 1 for command line interface.

GUI Mode
python main.py

Then select option 2 for graphical interface.
Examples
Basic Usage

    Input array: 1 2 2 3 4 5

    Target: 2

    First occurrence: index 1

    Last occurrence: index 2

    Count: 2 occurrences

Advanced Usage

    Rotated array: 4 5 6 7 0 1 2

    Find rotation point: index 4 (value 0)

    Search for 5: found at index 1

Project Structure
```
binary-search-project/
├── main.py              # Main entry point
├── requirements.txt     # Dependencies
├── readme.md           # This file
├── variants/           # Core implementation
│   ├── __init__.py
│   ├── core.py         # Search algorithms
│   ├── cli.py          # Command line interface
│   └── gui.py          # Graphical interface
└── tests/
    └── test_core.py    # Unit tests
```
Algorithms Complexity

All binary search variants maintain O(log n) time complexity with O(1) space complexity.
Contributing

Feel free to submit issues and enhancement requests!