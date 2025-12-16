import os
import time
from guessing_game import cli, gui

def print_banner():
    """Print a styled banner for the game."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;36m")  # Bold cyan
    print("╔══════════════════════════════════════════════════╗")
    print("║               NUMBER GUESSING GAME               ║")
    print("║                   🎯 🎮 🎲                       ║")
    print("╚══════════════════════════════════════════════════╝")
    print("\033[0m")  # Reset colors

def animate_text(text, delay=0.03):
    """Animate text printing."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def main():
    """Main entry point with enhanced UI."""
    print_banner()
    animate_text("Welcome to the Number Guessing Game!", 0.05)
    time.sleep(1)
    
    while True:
        print("\n\033[1;33mChoose an interface:\033[0m")
        print("1. Command Line Interface (CLI)")
        print("2. Graphical User Interface (GUI)")
        print("3. Exit")
        
        choice = input("\n\033[1;34mEnter your choice (1-3): \033[0m").strip()
        
        if choice == "1":
            cli.main()
        elif choice == "2":
            gui.main()
        elif choice == "3":
            print("\n\033[1;32mThanks for playing! Goodbye! 👋\033[0m")
            break
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")
            time.sleep(1)
            print_banner()

if __name__ == "__main__":
    main()