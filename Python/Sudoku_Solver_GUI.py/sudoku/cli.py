from __future__ import annotations
from .board import Board
from .solver import solve, SolveStats
import sys
import os

def run_cli(args) -> None:
    try:
        board = _load_board(args)
    except Exception as e:
        print(f"❌ Error loading puzzle: {e}", file=sys.stderr)
        sys.exit(1)

    # Show the loaded puzzle and ask if user wants to solve it
    print("\n" + "="*50)
    print("           SUDOKU SOLVER - CLI MODE")
    print("="*50)
    print("Loaded puzzle:\n")
    print(board)
    
    # Ask if user wants to solve
    while True:
        choice = input("\nDo you want to solve this puzzle? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            break
        elif choice in ['n', 'no']:
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Please enter 'y' or 'n'.")

    print("\n" + "="*50)
    print("Solving...\n")

    stats = SolveStats()
    solved = solve(board, stats)

    if solved is None:
        print("❌ No solution found or puzzle invalid.")
        sys.exit(1)
    else:
        print("✅ Solved puzzle:\n")
        print(solved)
        print(f"\n" + "="*50)
        print(f"Nodes explored: {stats.nodes}")
        print(f"Time elapsed: {stats.elapsed:.4f} seconds")
        print("="*50)
        sys.exit(0)

def _load_board(args) -> Board:
    # If arguments were provided via command line
    if getattr(args, "puzzle", None):
        return Board.from_flat_string(args.puzzle)
    if getattr(args, "infile", None):
        if not os.path.exists(args.infile):
            raise FileNotFoundError(f"File '{args.infile}' not found.")
        with open(args.infile, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return Board.from_lines(lines)
    
    # If no arguments provided, show interactive menu
    print("\nPlease provide the Sudoku puzzle:")
    print("1. Enter as 81-character string")
    print("2. Use built-in example puzzle")
    print("3. Exit")
    
    while True:
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            while True:
                puzzle = input("Enter 81-character string (0 for empty cells): ").strip()
                if len(puzzle) != 81:
                    print("❌ Input must be exactly 81 characters. Try again.")
                    continue
                if not all(c in "0123456789" for c in puzzle):
                    print("❌ Input must contain only digits 0-9. Try again.")
                    continue
                try:
                    return Board.from_flat_string(puzzle)
                except Exception as e:
                    print(f"❌ Error: {e}. Try again.")
            
        elif choice == "2":
            # Provide some built-in examples
            print("\nChoose an example puzzle:")
            print("1. Easy puzzle")
            print("2. Hard puzzle")
            print("3. Very hard puzzle")
            print("4. Go back")
            
            example_choice = input("Choose example (1-4): ").strip()
            
            if example_choice == "1":
                # Easy puzzle
                return Board.from_flat_string("530070000600195000098000060800060003400803001700020006060000280000419005000080079")
            elif example_choice == "2":
                # Hard puzzle
                return Board.from_flat_string("000000907000420180000705026100904000050000040000507009920108000034059000507000000")
            elif example_choice == "3":
                # Very hard puzzle
                return Board.from_flat_string("800000000003600000070090200050007000000045700000100030001000068008500010090000400")
            else:
                continue
                
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please try again.")

def run_cli_demo():
    """Run a demo with a built-in puzzle for testing"""
    print("\n" + "="*50)
    print("        SUDOKU SOLVER - DEMO MODE")
    print("="*50)
    
    # Use a built-in puzzle
    puzzle = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
    board = Board.from_flat_string(puzzle)
    
    print("Using built-in example puzzle:\n")
    print(board)
    
    # Ask if user wants to solve
    while True:
        choice = input("\nDo you want to solve this puzzle? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            break
        elif choice in ['n', 'no']:
            print("Goodbye!")
            return
        else:
            print("Please enter 'y' or 'n'.")

    print("\n" + "="*50)
    print("Solving...\n")

    stats = SolveStats()
    solved = solve(board, stats)

    if solved is None:
        print("❌ No solution found or puzzle invalid.")
    else:
        print("✅ Solved puzzle:\n")
        print(solved)
        print(f"\n" + "="*50)
        print(f"Nodes explored: {stats.nodes}")
        print(f"Time elapsed: {stats.elapsed:.4f} seconds")
        print("="*50)