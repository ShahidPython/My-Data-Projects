from sudoku.cli import run_cli, run_cli_demo
from sudoku.gui import run_gui
import argparse

def main():
    parser = argparse.ArgumentParser(description="Sudoku Solver (CLI + GUI)", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
Examples:
  GUI Mode:     python main.py --mode gui
  CLI Solve:    python main.py --solve 530070000600195000098000060800060003400803001700020006060000280000419005000080079
  CLI Demo:     python main.py --demo
  Interactive:  python main.py
                                     """)
    parser.add_argument("--mode", choices=["cli", "gui"], help="Run in CLI or GUI mode")
    parser.add_argument("--in", dest="infile", help="Path to puzzle file (9 lines of 9 digits)")
    parser.add_argument("--solve", help="Solve a puzzle from 81-character string")
    parser.add_argument("--demo", action="store_true", help="Run CLI demo with built-in puzzle")
    args = parser.parse_args()

    if args.demo:
        run_cli_demo()
    elif args.solve:
        # Create a simple args object with the puzzle
        class SimpleArgs:
            def __init__(self, puzzle):
                self.puzzle = puzzle
                self.infile = None
        run_cli(SimpleArgs(args.solve))
    elif args.mode == "cli":
        run_cli(args)
    elif args.mode == "gui":
        run_gui()
    else:
        # Interactive mode selection
        print("\n" + "="*50)
        print("        SUDOKU SOLVER - MODE SELECTION")
        print("="*50)
        print("1. GUI Mode (Graphical Interface)")
        print("2. CLI Mode (Solve custom puzzle)")
        print("3. CLI Demo (Built-in puzzle)")
        print("4. Exit")
        print("="*50)
        
        choice = input("Please choose an option (1-4): ").strip()
        
        if choice == "1":
            print("Starting GUI mode...")
            run_gui()
        elif choice == "2":
            print("Starting CLI mode...")
            run_cli(args)
        elif choice == "3":
            print("Starting CLI demo mode...")
            run_cli_demo()
        else:
            print("Goodbye!")

if __name__ == "__main__":
    main()