#!/usr/bin/env python3
"""Main entry point for Email Slicer application."""
import sys
import os
import questionary

# Add the current directory to Python path to find the email_slicer package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_welcome():
    """Display welcome banner."""
    print("┌────────────────────────────────────────────────────┐")
    print("│              EMAIL SLICER PRO v1.0.0              │")
    print("│      Advanced Email Parsing and Analysis Tool     │")
    print("└────────────────────────────────────────────────────┘")
    print()

def main_menu():
    """Display main menu and get user choice."""
    choice = questionary.select(
        "How would you like to use Email Slicer?",
        choices=[
            {"name": "🖥️  Graphical Interface (GUI)", "value": "gui"},
            {"name": "💻 Command Line Interface (CLI)", "value": "cli"},
            {"name": "❌ Exit", "value": "exit"}
        ]
    ).ask()
    
    return choice

def run_cli():
    """Run the CLI interface."""
    try:
        from email_slicer.cli import main as cli_main
        print("\nStarting Command Line Interface...")
        print("Type '--help' for available commands or press Ctrl+C to exit\n")
        cli_main()
    except ImportError as e:
        print(f"Error starting CLI: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

def run_gui():
    """Run the GUI interface."""
    try:
        from email_slicer.gui import main as gui_main
        print("\nStarting Graphical Interface...")
        gui_main()
    except ImportError as e:
        print(f"Error starting GUI: {e}")
        print("Make sure tkinter is installed on your system.")
        if sys.platform == "darwin":  # macOS
            print("On macOS, tkinter is usually included with Python.")
        elif sys.platform == "win32":  # Windows
            print("On Windows, tkinter should be included with Python installation.")
        else:  # Linux
            print("On Linux, install tkinter with: sudo apt-get install python3-tk")

def main():
    """Main entry point for the application."""
    # Check if command line arguments are provided (direct CLI mode)
    if len(sys.argv) > 1 and sys.argv[1] != '--gui':
        try:
            from email_slicer.cli import main as cli_main
            cli_main()
            return
        except ImportError as e:
            print(f"Error: {e}")
            print("Make sure all dependencies are installed: pip install -r requirements.txt")
            return
    
    # Interactive mode
    show_welcome()
    
    while True:
        try:
            choice = main_menu()
            
            if choice == "gui":
                run_gui()
                break
            elif choice == "cli":
                run_cli()
                break
            elif choice == "exit":
                print("👋 Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            if questionary.confirm("Try again?").ask():
                continue
            else:
                print("👋 Goodbye!")
                break

if __name__ == "__main__":
    main()