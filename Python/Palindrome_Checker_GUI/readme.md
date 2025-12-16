# Palindrome Checker

A professional-grade palindrome checker application with both command-line interface (CLI) and graphical user interface (GUI) implementations.

## Features

- **Advanced Text Normalization**: Ignores case, spaces, punctuation, and diacritics
- **Multiple Input Modes**: CLI arguments, interactive CLI, and GUI
- **Detailed Analysis**: Shows normalized text, length, and reversal
- **Substring Detection**: Finds palindromic substrings in non-palindromic text
- **History Tracking**: Maintains check history in both CLI and GUI
- **Unicode Support**: Properly handles international characters and diacritics
- **Comprehensive Testing**: Full test suite with pytest

## Installation

1. Clone or download this project
2. Ensure you have Python 3.6+ installed
3. Install dependencies: `pip install -r requirements.txt`

## Usage

### Main Menu
Run the main application to choose between modes:
```bash
python main.py
Command Line Interface
bash
# Check a specific text
python cli.py "A man, a plan, a canal: Panama"

# Detailed analysis
python cli.py --explain "Never odd or even"

# Find palindromic substrings
python cli.py --substrings "Palindrome"

# Interactive mode
python cli.py --interactive
Graphical Interface
bash
python gui.py
Or use the main menu to launch the GUI.

Direct Testing
Run the test suite:

bash
pytest test_core.py -v
Examples
Basic Check
text
Input: "RaceCar"
Output: ✓ PALINDROME
Detailed Analysis
text
Input: "A man, a plan, a canal: Panama"
Normalized: "amanaplanacanalpanama"
Length: 21 characters
Reversed: "amanaplanacanalpanama"
✓ The text reads the same forwards and backwards.
Substring Detection
text
Input: "Palindrome"
Normalized: "palindrome"
✗ The text does not read the same forwards and backwards.

Found 3 palindromic substring(s):
  'ili' (positions 3-5)
  'nd' (positions 6-7)
  'rom' (positions 4-6)
Project Structure
text
palindrome-checker/
├── main.py          # Main entry point with mode selection
├── core.py          # Core palindrome logic and algorithms
├── cli.py           # Command-line interface implementation
├── gui.py           # Graphical user interface (Tkinter)
├── test_core.py     # Comprehensive unit tests
├── requirements.txt # Python dependencies
└── README.md        # This documentation
Technical Details
Text Normalization
The application performs Unicode-aware normalization:

Removes diacritics using NFKD normalization

Filters to only alphanumeric characters

Converts to lowercase (by default)

Algorithms
Palindrome Check: Simple reverse comparison of normalized text

Substring Detection: Center-expansion algorithm to find all palindromic substrings

Dependencies
pytest: For testing framework only

Standard Library: All other functionality uses Python's standard library

Contributing
Fork the repository

Create a feature branch

Add tests for new functionality

Implement changes

Ensure all tests pass

Submit a pull request

License
This project is open source and available under the MIT License.