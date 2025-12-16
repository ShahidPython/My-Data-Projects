🎲 Dice Roller

A colorful, terminal-based dice rolling application with ASCII art and visual effects.
Features

    Visual Dice Display: Beautiful ASCII art representation of dice faces

    Color-Coded Dots: Each number (1-6) has a unique color:

        1 dot = 🔴 Red

        2 dots = 🔵 Blue

        3 dots = 🟡 Yellow

        4 dots = 🟢 Green

        5 dots = 🟣 Magenta (orange substitute)

        6 dots = ⚪ White (brown substitute)

    Smooth Animation: Dramatic rolling effect with timing

    Simple Controls: Press Enter to roll, 'q' to quit

Requirements

    Python 3.x

    colorama library

Installation

    Clone or download the project files

    Install required dependencies:
    bash

pip install colorama

Usage

Run the application:
bash

python dice_roller.py

Controls:

    Press ENTER to roll the dice

    Type q and press ENTER to quit

How It Works

The program:

    Generates random numbers between 1-6

    Displays corresponding ASCII dice art

    Uses color coding for easy number recognition

    Provides a brief rolling animation for realism

Project Structure

    dice_roller.py - Main application file

    Uses ASCII box-drawing characters for clean dice borders

    Color mapping system for consistent dot colors

    Pre-defined dot layouts for each dice face

Example Output
text

🎲 DICE ROLLER 🎲
Press ENTER to roll, 'q' to quit

> 

Rolling the dice...

    ┌───────┐
    │ ●   ● │
    │   ●   │
    │ ●   ● │
    └───────┘

→ You rolled a 5!

Customization

You can easily modify:

    Colors in the DOT_COLORS dictionary

    Dice appearance in the DICE_TEMPLATE

    Dot layouts in DOT_LAYOUT

    Rolling delay time in time.sleep()

License

Free to use and modify for personal projects.

Enjoy rolling! 🎯