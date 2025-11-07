#!/usr/bin/env python3
"""
Odd or Even Checker - Main Entry Point
"""

import sys
from odd_even_checker import __version__


def print_welcome():
    """Print welcome message."""
    print(f"\n🔢 Odd or Even Checker v{__version__}")
    print("=" * 30)


def main():
    """Main entry point for the application."""
    print_welcome()
    
    while True:
        print("\nChoose mode:")
        print("1) Command Line Interface (CLI)")
        print("2) Graphical User Interface (GUI)")
        print("3) Exit")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            from odd_even_checker.cli import main as cli_main
            cli_main()
        elif choice == "2":
            from odd_even_checker.gui import main as gui_main
            gui_main()
        elif choice in ["3", "exit", "quit"]:
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    