"""Beautiful CLI to play with the AI."""
import os
import sys
import time
from .core import Hangman
from .ai_solver import AISolver

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_wordlist(path: str = None):
    # try to load from a file path if provided; otherwise return None to let Hangman use default
    if path:
        try:
            with open(path, 'r', encoding='utf8') as f:
                return [w.strip().lower() for w in f if w.strip()]
        except Exception as e:
            print(f"Could not load wordlist from {path}: {e}")
            return None
    return None

def print_header():
    """Print a beautiful header for the game."""
    clear_screen()
    print("""
    \033[1;36m
    ╔══════════════════════════════════════════════════════════╗
    ║                    HANGMAN AI GAME                       ║
    ║                 ──────────────────────                   ║
    ║      Try to guess the word before the man is hanged!     ║
    ╚══════════════════════════════════════════════════════════╝
    \033[0m
    """)

def print_hangman(lives, max_lives=7):
    """Print ASCII art of the hangman based on remaining lives."""
    stages = [
        """
           \033[1;31m-------
           |    |
           |    💀
           |   /|\\
           |   / \\
           |
        ---|--------\033[0m
        """,
        """
           \033[1;31m-------
           |    |
           |    😰
           |   /|\\
           |   /
           |
        ---|--------\033[0m
        """,
        """
           \033[1;33m-------
           |    |
           |    😥
           |   /|\\
           |
           |
        ---|--------\033[0m
        """,
        """
           \033[1;33m-------
           |    |
           |    😓
           |   /|
           |
           |
        ---|--------\033[0m
        """,
        """
           \033[1;33m-------
           |    |
           |    😐
           |    |
           |
           |
        ---|--------\033[0m
        """,
        """
           \033[1;32m-------
           |    |
           |    🙂
           |
           |
           |
        ---|--------\033[0m
        """,
        """
           \033[1;32m-------
           |    |
           |    
           |
           |
           |
        ---|--------\033[0m
        """,
        """
           \033[1;32m-------
           |    
           |    
           |
           |
           |
        ---|--------\033[0m
        """
    ]
    
    # Adjust index based on lives
    index = max_lives - lives
    if index < 0:
        index = 0
    if index >= len(stages):
        index = len(stages) - 1
    
    print(stages[index])

def human_vs_ai():
    words = load_wordlist() or None
    game = Hangman(wordlist=words)
    ai = AISolver(game.wordlist)
    
    print_header()
    
    while not game.is_finished():
        print(f"\n    \033[1;34mWord:\033[0m \033[1;36m{game.pattern}\033[0m")
        print(f"    \033[1;34mLives:\033[0m \033[1;{'31m' if game.lives < 3 else '33m' if game.lives < 5 else '32m'}{game.lives}/{game.max_lives}\033[0m")
        print(f"    \033[1;34mGuessed:\033[0m \033[1;35m{', '.join(sorted(game.guessed)) if game.guessed else 'None'}\033[0m")
        
        print_hangman(game.lives, game.max_lives)
        
        action = input("\n    \033[1;33mType a letter to guess, or 'ai' for a suggestion: \033[0m").strip().lower()
        
        if not action:
            continue
            
        if action == 'ai':
            suggestion = ai.next_guess(game.visible_pattern())
            print(f"\n    \033[1;35m🤖 AI suggests: {suggestion.upper()}\033[0m")
            time.sleep(1.5)
            print_header()
            continue
            
        ch = action[0]
        if not ch.isalpha():
            print("\n    \033[1;31m❌ Please enter a valid letter!\033[0m")
            time.sleep(1)
            print_header()
            continue
            
        if ch in game.guessed:
            print(f"\n    \033[1;31m❌ You've already guessed '{ch}'!\033[0m")
            time.sleep(1)
            print_header()
            continue
            
        ok = game.guess(ch)
        print_header()
        
        if ok:
            print(f"\n    \033[1;32m✅ Good guess: {ch.upper()} is in the word!\033[0m")
        else:
            print(f"\n    \033[1;31m❌ Sorry, {ch.upper()} is not in the word.\033[0m")
        
        time.sleep(1)
        print_header()
    
    # Game finished
    print(f"\n    \033[1;34mWord:\033[0m \033[1;36m{game.pattern}\033[0m")
    print_hangman(game.lives, game.max_lives)
    
    if game.is_won():
        print(f"\n    \033[1;32m🎉 Congratulations! You won!\033[0m")
        print(f"    \033[1;36mThe word was: {game.secret.upper()}\033[0m")
    else:
        print(f"\n    \033[1;31m💀 Game Over! You lost.\033[0m")
        print(f"    \033[1;36mThe word was: {game.secret.upper()}\033[0m")
    
    print("\n    \033[1;33mThanks for playing!\033[0m\n")
    
    # Ask if user wants to play again
    play_again = input("    \033[1;33mPlay again? (y/n): \033[0m").strip().lower()
    if play_again == 'y' or play_again == 'yes':
        human_vs_ai()

def ai_solve_interactive():
    words = load_wordlist() or None
    print_header()
    secret = input("    \033[1;33mEnter a secret word for the AI to solve (or leave blank for random): \033[0m").strip().lower()
    
    if secret:
        game = Hangman(word=secret, wordlist=words)
    else:
        game = Hangman(wordlist=words)
        
    ai = AISolver(game.wordlist)
    
    print(f"\n    \033[1;35m🤖 AI is solving a {len(game.secret)}-letter word...\033[0m")
    time.sleep(1.5)
    
    result = ai.solve(game.secret, max_lives=game.max_lives, verbose=True)
    
    print("\n    \033[1;36m" + "="*50 + "\033[0m")
    if result['solved']:
        print("    \033[1;32m✅ AI solved the word!\033[0m")
    else:
        print("    \033[1;31m❌ AI failed to solve the word!\033[0m")
        
    print(f"    \033[1;34mFinal pattern:\033[0m \033[1;36m{result['pattern']}\033[0m")
    print(f"    \033[1;34mLives left:\033[0m \033[1;{'32m' if result['lives_left'] > 3 else '33m' if result['lives_left'] > 0 else '31m'}{result['lives_left']}\033[0m")
    print(f"    \033[1;34mGuesses made:\033[0m \033[1;35m{', '.join(result['guesses'])}\033[0m")
    print(f"    \033[1;34mCandidates left:\033[0m \033[1;36m{result['candidates_left']}\033[0m")
    print("    \033[1;36m" + "="*50 + "\033[0m\n")
    
    # Ask if user wants to try another word
    another = input("    \033[1;33mTry another word? (y/n): \033[0m").strip().lower()
    if another == 'y' or another == 'yes':
        ai_solve_interactive()

def run_benchmarks():
    words = load_wordlist() or ['python','hangman','assistant','programming','developer','testing','algorithm','computer','software','hardware']
    from time import time
    ai = AISolver(words)
    wins = 0
    total_time = 0
    
    print_header()
    print("    \033[1;35mRunning benchmarks...\033[0m\n")
    
    for i, w in enumerate(words):
        start_time = time()
        r = ai.solve(w, max_lives=7, verbose=False)
        end_time = time()
        time_taken = end_time - start_time
        total_time += time_taken
        
        status = "\033[1;32m✅\033[0m" if r['solved'] else "\033[1;31m❌\033[0m"
        color = "\033[1;32m" if r['solved'] else "\033[1;31m"
        print(f"    {i+1:2d}. {w:12} {status} {color}{time_taken:.4f}s\033[0m")
        
        if r['solved']:
            wins += 1
        ai.reset()
    
    success_rate = (wins/len(words))*100
    color_rate = "\033[1;32m" if success_rate > 80 else "\033[1;33m" if success_rate > 60 else "\033[1;31m"
    
    print(f"\n    \033[1;34mSolved:\033[0m {wins}/{len(words)} words")
    print(f"    \033[1;34mSuccess rate:\033[0m {color_rate}{success_rate:.2f}%\033[0m")
    print(f"    \033[1;34mAverage time:\033[0m \033[1;36m{total_time/len(words):.4f}s\033[0m\n")
    
    # Ask if user wants to run benchmarks again
    again = input("    \033[1;33mRun benchmarks again? (y/n): \033[0m").strip().lower()
    if again == 'y' or again == 'yes':
        run_benchmarks()

if __name__ == '__main__':
    human_vs_ai()