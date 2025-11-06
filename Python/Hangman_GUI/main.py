import argparse
from hangman.cli import run_cli
from hangman.gui import run_gui

def get_user_choice():
    """Display a menu for mode selection"""
    print("\n" + "="*40)
    print("        HANGMAN GAME")
    print("="*40)
    print("1. Command Line Interface (CLI)")
    print("2. Graphical User Interface (GUI)")
    print("3. Exit")
    print("="*40)
    
    while True:
        try:
            choice = input("Please select an option (1-3): ").strip()
            if choice == "1":
                return "cli"
            elif choice == "2":
                return "gui"
            elif choice == "3":
                print("Goodbye!")
                exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            exit(0)

def main():
    parser = argparse.ArgumentParser(description="Hangman (CLI + GUI)")
    parser.add_argument("--mode", choices=["cli", "gui"], 
                        help="Run mode: cli or gui (bypasses menu)")
    args = parser.parse_args()

    if args.mode:
        # Run directly with specified mode
        if args.mode == "cli":
            run_cli()
        else:
            run_gui()
    else:
        # Show interactive menu
        mode = get_user_choice()
        if mode == "cli":
            run_cli()
        else:
            run_gui()

if __name__ == "__main__":
    main()