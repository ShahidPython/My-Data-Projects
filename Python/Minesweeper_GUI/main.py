
#!/usr/bin/env python3
"""
Minesweeper Game - Main Entry Point
Provides a menu to choose between different game modes.
"""

import os
import sys
from pathlib import Path

# Add the minesweeper package to the path
sys.path.insert(0, str(Path(__file__).parent))

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a colorful banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎮 MINESWEEPER GAME 🎮                    ║
    ║                     Advanced Edition                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print("\033[1;36m" + banner + "\033[0m")

def print_menu():
    """Print the main menu options."""
    menu = """
    ┌──────────────────────────────────────────────────────────────┐
    │                      🎯 GAME MODES 🎯                        │
    ├──────────────────────────────────────────────────────────────┤
    │  1. 🖥️  CLI Mode (Terminal Interface)                        │
    │  2. 🪟 Tkinter GUI Mode (Classic Interface)                   │
    │  3. 🎨 Pygame GUI Mode (Modern Interface)                     │
    │  4. 🤖 AI CLI Mode (Watch AI Play in Terminal)               │
    │  5. 🧠 AI GUI Mode (Watch AI Play with Graphics)             │
    │  6. 👥 Multiplayer Mode (Play with Friends)                  │
    │  7. ❌ Exit                                                   │
    └──────────────────────────────────────────────────────────────┘
    """
    print("\033[1;33m" + menu + "\033[0m")

def get_user_choice():
    """Get and validate user's menu choice."""
    while True:
        try:
            choice = input("\033[1;32m    Enter your choice (1-7): \033[0m").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return int(choice)
            else:
                print("\033[1;31m    ❌ Invalid choice! Please enter a number between 1-7.\033[0m")
        except (ValueError, KeyboardInterrupt):
            print("\033[1;31m    ❌ Invalid input! Please enter a number between 1-7.\033[0m")

def main():
    """Main function to run the game."""
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = get_user_choice()
        
        try:
            if choice == 1:
                print("\033[1;35m    🖥️  Starting CLI Mode...\033[0m")
                from minesweeper.cli import main as cli_main
                cli_main()
                
            elif choice == 2:
                print("\033[1;35m    🪟 Starting Tkinter GUI Mode...\033[0m")
                from minesweeper.gui_tkinter import main as tk_main
                tk_main()
                
            elif choice == 3:
                print("\033[1;35m    🎨 Starting Pygame GUI Mode...\033[0m")
                from minesweeper.gui_pygame import main as pygame_main
                pygame_main()
                
            elif choice == 4:
                print("\033[1;35m    🤖 Starting AI CLI Mode...\033[0m")
                from minesweeper.ai_solver import run_ai_cli
                run_ai_cli()
                
            elif choice == 5:
                print("\033[1;35m    🧠 Starting AI GUI Mode...\033[0m")
                from minesweeper.ai_solver import run_ai_gui
                run_ai_gui()
                
            elif choice == 6:
                print("\033[1;35m    👥 Starting Multiplayer Mode...\033[0m")
                from minesweeper.multiplayer import main as multiplayer_main
                multiplayer_main()
                
            elif choice == 7:
                print("\033[1;32m    👋 Thanks for playing! Goodbye!\033[0m")
                sys.exit(0)
                
        except ImportError as e:
            print(f"\033[1;31m    ❌ Error loading module: {e}\033[0m")
            input("\033[1;33m    Press Enter to continue...\033[0m")
        except Exception as e:
            print(f"\033[1;31m    ❌ An error occurred: {e}\033[0m")
            input("\033[1;33m    Press Enter to continue...\033[0m")

if __name__ == "__main__":
    main()
