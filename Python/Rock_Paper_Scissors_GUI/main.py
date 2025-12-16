"""Entry point to run CLI or GUI."""

import argparse
from cli import run_cli
from gui import run_gui

def main():
    parser = argparse.ArgumentParser(description="Rock Paper Scissors Game")
    parser.add_argument("--mode", choices=["cli", "gui"], help="Choose interface mode")
    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    elif args.mode == "gui":
        run_gui()
    else:
        # Interactive mode selection
        print("Choose a mode:")
        print("1) CLI (Command Line Interface)")
        print("2) GUI (Graphical User Interface)")
        print("3) Quit")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice == "1":
                run_cli()
                break
            elif choice == "2":
                run_gui()
                break
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()