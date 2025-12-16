"""Entry point for hangman-ai."""
import argparse
import sys
from hangman import cli, gui

def print_welcome():
    """Print a beautiful welcome message."""
    print("""
    \033[1;36m
    ╔══════════════════════════════════════════════════════════╗
    ║                    HANGMAN AI GAME                       ║
    ║                 ──────────────────────                   ║
    ║          Welcome to the Ultimate Hangman Experience      ║
    ╚══════════════════════════════════════════════════════════╝
    \033[0m
    """)

def select_mode():
    """Let the user select the mode interactively."""
    print_welcome()
    
    while True:
        print("\n    \033[1;33mPlease select a mode:\033[0m")
        print("    \033[1;32m1. CLI Mode\033[0m - Command Line Interface with ASCII art")
        print("    \033[1;35m2. GUI Mode\033[0m - Graphical User Interface")
        print("    \033[1;34m3. AI Mode\033[0m  - Watch AI solve a word")
        print("    \033[1;36m4. Bench Mode\033[0m - Run performance tests")
        print("    \033[1;31m5. Exit\033[0m")
        
        choice = input("\n    \033[1;33mEnter your choice (1-5): \033[0m").strip()
        
        if choice == '1':
            return 'cli'
        elif choice == '2':
            return 'gui'
        elif choice == '3':
            return 'ai'
        elif choice == '4':
            return 'bench'
        elif choice == '5':
            print("\n    \033[1;36mThanks for playing! Goodbye! 👋\033[0m\n")
            sys.exit(0)
        else:
            print("\n    \033[1;31mInvalid choice! Please try again.\033[0m")

def main():
    # Check if mode was provided as argument
    if len(sys.argv) > 1 and any(arg in sys.argv for arg in ['--mode', '-m']):
        # Use argparse for command line arguments
        parser = argparse.ArgumentParser(description="Hangman AI project")
        parser.add_argument('--mode', '-m', choices=['cli','gui','ai','bench'], default='cli',
                           help='cli (command line interface), gui (graphical interface), ai (AI solves secret word), bench (run solver tests)')
        args = parser.parse_args()
        mode = args.mode
    else:
        # Interactive mode selection
        mode = select_mode()

    if mode == 'cli':
        cli.human_vs_ai()
    elif mode == 'gui':
        gui.run_gui()
    elif mode == 'ai':
        cli.ai_solve_interactive()
    else:
        cli.run_benchmarks()

if __name__ == '__main__':
    main()