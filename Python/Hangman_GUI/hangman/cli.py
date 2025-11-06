from __future__ import annotations
from .core import HangmanGame
import os
import sys

HANGMAN_PICS = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    ========="""
]

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_hangman(lives_left: int, max_lives: int) -> str:
    index = max_lives - lives_left
    index = max(0, min(index, len(HANGMAN_PICS) - 1))
    return HANGMAN_PICS[index]

def print_colored(text, color_code):
    """Print colored text in terminal"""
    print(f"\033[{color_code}m{text}\033[0m")

def run_cli():
    clear_screen()
    print_colored("\n" + "="*50, "1;36")
    print_colored("           HANGMAN - CLI EDITION", "1;36")
    print_colored("="*50, "1;36")
    
    game = HangmanGame()
    
    while not game.is_over():
        print("\n")
        print_colored(draw_hangman(game.lives_left, game.max_lives), "33")
        print()
        print_colored(f"WORD:   {game.masked_word()}", "1;32")
        print_colored(f"WRONG:  {', '.join(sorted(game.wrong_letters)) or '-'}", "1;31")
        print_colored(f"LIVES:  {game.lives_left}", "1;34")
        print()

        guess = input("Enter a letter (or '!' to give up, '?' for hint): ").strip().lower()
        
        if guess == "!":
            print_colored(f"\nYou gave up. The word was: {game.reveal()}", "1;31")
            break
        elif guess == "?":
            # Hint: reveal a random unguessed letter
            unguessed = [c for c in game.secret_word if c not in game.guessed_letters]
            if unguessed:
                hint = unguessed[0]
                print_colored(f"Hint: Try the letter '{hint}'", "1;35")
                continue
            else:
                print_colored("No hints needed! You've guessed all letters.", "1;35")
                continue

        ok, msg = game.guess(guess)
        
        if ok:
            print_colored(msg, "1;32")  # Green for correct
        else:
            print_colored(msg, "1;31")  # Red for incorrect

    # Game over message
    if game.is_won():
        print_colored("\n" + "🎉" * 20, "1;32")
        print_colored("CONGRATULATIONS! YOU WON! 🎉", "1;32")
        print_colored(f"The word was: {game.reveal()}", "1;32")
        print_colored("🎉" * 20, "1;32")
    elif game.is_lost():
        print_colored("\n" + "💀" * 20, "1;31")
        print_colored("GAME OVER! YOU LOST! 💀", "1;31")
        print_colored(f"The word was: {game.reveal()}", "1;31")
        print_colored("💀" * 20, "1;31")
    
    # Ask to play again
    play_again = input("\nWould you like to play again? (y/n): ").strip().lower()
    if play_again in ['y', 'yes']:
        run_cli()
    else:
        print_colored("Thanks for playing!", "1;36")