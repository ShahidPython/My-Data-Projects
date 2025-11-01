# main.py — Enhanced entry point with better UX

from cli import run_interactive_cli, app
from gui import run_gui
import typer

def main():
    print("=== Professional Flashcard App ===")
    print("\nChoose mode:")
    print("1) 📝 Interactive CLI Menu")
    print("2) 🖥️  Graphical Interface (GUI)")
    print("3) 💻 Advanced CLI Commands")
    print("4) ℹ️  Help")
    
    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        # Launch our enhanced interactive CLI
        run_interactive_cli()
    elif choice == "2":
        # Launch Tkinter GUI
        run_gui()
    elif choice == "3":
        # Directly run Typer CLI
        print("\nRunning advanced CLI. Use --help to see available commands.")
        app()
    elif choice == "4":
        print("""
        Flashcard App Help:
        
        - Interactive CLI Menu: User-friendly text interface
        - Graphical Interface: Modern desktop application
        - Advanced CLI: Command-line interface for power users
        
        Features:
        - Create, read, update, delete flashcards
        - Organize by categories
        - Study mode with self-assessment
        - Search and filter functionality
        - Statistics and progress tracking
        """)
    else:
        print("Invalid choice. Please run again and select 1-4.")

if __name__ == "__main__":
    main()