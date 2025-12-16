import os
import time
from typing import Optional
from guessing_game.core import NumberGuessingGame, Difficulty, GameMode

# ANSI color codes for terminal styling
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a styled game header."""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════╗")
    print("║               NUMBER GUESSING GAME               ║")
    print("║                   CLI Edition                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

def animate_text(text, delay=0.03):
    """Animate text printing."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_win_banner(attempts):
    """Print a winning banner."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔══════════════════════════════════════════════════╗")
    print("║                  CONGRATULATIONS!                ║")
    print("║                   YOU WIN! 🎉                    ║")
    print(f"║           Attempts: {attempts:2}                           ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

def print_game_over_banner(secret_number):
    """Print a game over banner."""
    print(f"\n{Colors.BOLD}{Colors.RED}")
    print("╔══════════════════════════════════════════════════╗")
    print("║                   GAME OVER!                     ║")
    print("║               Better luck next time!             ║")
    print(f"║           The number was: {secret_number:3}                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

def select_difficulty():
    """Let the user select a difficulty level."""
    print(f"\n{Colors.BOLD}Select Difficulty:{Colors.END}")
    print(f"{Colors.YELLOW}1. Easy (1-50, 10 attempts)")
    print(f"2. Medium (1-100, 7 attempts)")
    print(f"3. Hard (1-200, 5 attempts)")
    print(f"4. Custom{Colors.END}")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BLUE}Enter your choice (1-4): {Colors.END}"))
            if choice == 1:
                return Difficulty.EASY
            elif choice == 2:
                return Difficulty.MEDIUM
            elif choice == 3:
                return Difficulty.HARD
            elif choice == 4:
                lower = int(input("Enter lower bound: "))
                upper = int(input("Enter upper bound: "))
                max_attempts = int(input("Enter maximum attempts: "))
                return (Difficulty.CUSTOM, (lower, upper, max_attempts))
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number.{Colors.END}")

def play_game():
    """Main game loop."""
    # Setup game
    difficulty_choice = select_difficulty()
    
    if isinstance(difficulty_choice, tuple):
        difficulty, custom_range = difficulty_choice
        game = NumberGuessingGame(difficulty, custom_range)
    else:
        game = NumberGuessingGame(difficulty_choice)
    
    print_header()
    print(f"{Colors.BOLD}I'm thinking of a number between {game.lower} and {game.upper}.")
    print(f"You have {game.max_attempts} attempts to guess it.{Colors.END}\n")
    
    # Game loop
    while not game.game_over:
        try:
            guess = int(input(f"{Colors.BLUE}Enter your guess: {Colors.END}"))
            result = game.guess(guess)
            
            # Check if guess is out of range
            if "valid" in result and not result["valid"]:
                print(f"{Colors.RED}{result['message']}{Colors.END}")
                continue
                
            print(f"{Colors.YELLOW}{result['message']}{Colors.END}")
            
            # Display guess history
            if len(result["history"]) > 1:
                print(f"{Colors.CYAN}Previous guesses: {result['history'][:-1]}{Colors.END}")
            
            # Offer hint after 3 failed attempts
            if result["attempts"] == 3 and not result["game_over"]:
                hint_choice = input(f"{Colors.MAGENTA}Would you like a hint? (y/n): {Colors.END}")
                if hint_choice.lower() == 'y':
                    print(f"{Colors.MAGENTA}{game.get_hint()}{Colors.END}")
                    
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
    
    # Game over message
    if game.win:
        print_win_banner(game.attempts)
    else:
        print_game_over_banner(game.secret_number)
    
    # Play again option
    play_again = input(f"\n{Colors.BLUE}Would you like to play again? (y/n): {Colors.END}")
    if play_again.lower() == 'y':
        play_game()
    else:
        print(f"\n{Colors.GREEN}Thanks for playing! 👋{Colors.END}")

def main():
    """Main CLI entry point."""
    print_header()
    animate_text("Welcome to the Number Guessing Game!", 0.05)
    time.sleep(1)
    play_game()