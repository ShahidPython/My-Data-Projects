#!/usr/bin/env python3
"""
MadLibs - A fun word game where players fill in blanks to create stories.
"""

import sys
from madlibs.cli import mad_libs_cli
from madlibs.gui import run_gui

def main():
    print("=" * 50)
    print("          WELCOME TO MAD LIBS!")
    print("=" * 50)
    
    while True:
        print("\nPlease choose an option:")
        print("1. Command Line Interface (CLI)")
        print("2. Graphical Interface (GUI)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\nStarting CLI version...")
            mad_libs_cli()
        elif choice == "2":
            print("\nStarting GUI version...")
            run_gui()
            break
        elif choice == "3":
            print("\nThanks for playing Mad Libs! Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()