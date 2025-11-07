"""Enhanced command-line interface for Rock, Paper, Scissors."""

import sys
import time
import os
from game import Game, Move

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_color(text, color, end='\n'):
    print(f"{color}{text}{Colors.END}", end=end)

def animate_text(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    """Display help information."""
    print_color("\n=== Rock Paper Scissors Help ===", Colors.CYAN + Colors.BOLD)
    print("Commands:")
    print_color("  rock, r, 🪨     - Choose rock", Colors.YELLOW)
    print_color("  paper, p, 📄    - Choose paper", Colors.YELLOW)
    print_color("  scissors, s, ✂️ - Choose scissors", Colors.YELLOW)
    print_color("  history, h      - Show game history", Colors.YELLOW)
    print_color("  scores          - Show current scores", Colors.YELLOW)
    print_color("  reset           - Reset the game", Colors.YELLOW)
    print_color("  help, ?         - Show this help", Colors.YELLOW)
    print_color("  quit, q, exit   - Exit the game", Colors.YELLOW)
    print("\nRules:")
    print("  - Rock beats Scissors")
    print("  - Paper beats Rock")
    print("  - Scissors beats Paper")
    print("  - Same selection results in a draw")

def run_cli():
    game = Game()
    
    clear_screen()
    print_color("=== 🪨 📄 ✂️  Rock • Paper • Scissors (CLI) ===", Colors.CYAN + Colors.BOLD)
    print()
    animate_text("Get ready to challenge the computer!", 0.02)
    print()
    print("Type 'help' or '?' for available commands.")
    print("=" * 50)

    while True:
        print()
        move = input(f"{Colors.BOLD}Your move > {Colors.END}").lower().strip()
        
        if move in ("quit", "exit", "q"):
            print_color("\nThanks for playing! Final scores:", Colors.YELLOW)
            print_color(f"Player: {game.scores['player']} | Computer: {game.scores['computer']} | Draws: {game.scores['draws']}", Colors.YELLOW)
            break
        
        if move in ("help", "?"):
            show_help()
            continue
        
        if move in ("history", "h"):
            if not game.history:
                print_color("No games played yet.", Colors.PURPLE)
            else:
                print_color("Game History:", Colors.PURPLE)
                for i, round_data in enumerate(game.history[-10:], 1):  # Show last 10 games
                    outcome = "Draw" if round_data["result"] == "draw" else \
                             "Win" if round_data["result"] == "player" else "Loss"
                    color = Colors.YELLOW if outcome == "Draw" else \
                           Colors.GREEN if outcome == "Win" else Colors.RED
                    print_color(f"Round {i}: You: {round_data['player']}, Computer: {round_data['computer']} -> {outcome}", color)
            continue
        
        if move == "scores":
            print_color(f"Current scores: Player: {game.scores['player']} | Computer: {game.scores['computer']} | Draws: {game.scores['draws']}", Colors.BLUE)
            continue
            
        if move == "reset":
            game.reset()
            print_color("Game has been reset. Scores cleared.", Colors.GREEN)
            continue

        # Validate and convert move
        try:
            if move in ("r", "rock", "🪨"):
                player_move = Move.ROCK
            elif move in ("p", "paper", "📄"):
                player_move = Move.PAPER
            elif move in ("s", "scissors", "✂️"):
                player_move = Move.SCISSORS
            else:
                raise ValueError("Invalid move")
        except ValueError:
            print_color("✖ Invalid move. Type 'help' for available commands.", Colors.RED)
            continue

        # Animate computer thinking
        print_color("Computer is thinking...", Colors.PURPLE)
        for i in range(3):
            emoji = "✂️" if i % 3 == 0 else "📄" if i % 3 == 1 else "🪨"
            print_color(emoji, Colors.CYAN, end=' ')
            time.sleep(0.5)
        print()

        # Play the round
        result = game.play_round(player_move)
        
        # Display result with appropriate colors
        player_emoji = "🪨" if result["player"] == "rock" else "📄" if result["player"] == "paper" else "✂️"
        computer_emoji = "🪨" if result["computer"] == "rock" else "📄" if result["computer"] == "paper" else "✂️"
        
        print(f"You: {player_emoji} {result['player']} {Colors.BOLD}vs{Colors.END} Computer: {computer_emoji} {result['computer']}")
        
        if result["result"] == "draw":
            print_color("→ It's a draw. 🤝", Colors.YELLOW)
        elif result["result"] == "player":
            print_color("→ You win this round! 🎉", Colors.GREEN)
        else:
            print_color("→ Computer wins this round. 🤖", Colors.RED)
            
        print_color(f"Scores: Player: {result['scores']['player']} | Computer: {result['scores']['computer']} | Draws: {result['scores']['draws']}", Colors.BLUE)