
"""
Enhanced CLI interface for Minesweeper with beautiful design and life system.
"""
import os
import sys
from typing import Optional
from .core import Minesweeper, GameState
from .difficulty import ALL_DIFFICULTIES, get_difficulty_by_name, create_custom_difficulty

class Colors:
    """ANSI color codes for terminal styling."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the game header."""
    header = f"""
{Colors.BRIGHT_CYAN}┌{'─' * 68}┐
│{' ' * 20}🎮 MINESWEEPER CLI MODE 🎮{' ' * 19}│
└{'─' * 68}┘{Colors.RESET}
"""
    print(header)

def print_game_info(game: Minesweeper):
    """Print game information."""
    time_str = f"{game.get_game_time():.1f}s"
    lives_str = f"❤️ {game.current_lives}" if game.max_lives > 0 else "💀 Hardcore"
    
    info = f"""
{Colors.BRIGHT_YELLOW}┌─ Game Info ─────────────────────────────────────────────────┐
│ ⏱️  Time: {time_str:<10} 💣 Mines: {game.get_remaining_mines():<10} {lives_str:<15} │
└─────────────────────────────────────────────────────────────┘{Colors.RESET}
"""
    print(info)

def get_cell_color(game: Minesweeper, row: int, col: int) -> str:
    """Get color for a specific cell."""
    if game.flagged[row][col]:
        return Colors.BRIGHT_RED + Colors.BOLD
    elif not game.revealed[row][col]:
        return Colors.DIM + Colors.WHITE
    elif game.board[row][col]:
        return Colors.BRIGHT_RED + Colors.BG_RED + Colors.BOLD
    else:
        num = game.numbers[row][col]
        if num == 0:
            return Colors.DIM
        elif num == 1:
            return Colors.BRIGHT_BLUE + Colors.BOLD
        elif num == 2:
            return Colors.BRIGHT_GREEN + Colors.BOLD
        elif num == 3:
            return Colors.BRIGHT_RED + Colors.BOLD
        elif num == 4:
            return Colors.BLUE + Colors.BOLD
        elif num == 5:
            return Colors.RED + Colors.BOLD
        elif num == 6:
            return Colors.CYAN + Colors.BOLD
        elif num == 7:
            return Colors.MAGENTA + Colors.BOLD
        else:
            return Colors.YELLOW + Colors.BOLD

def print_board(game: Minesweeper):
    """Print the game board with beautiful formatting."""
    print(f"\n{Colors.BRIGHT_CYAN}   ", end="")
    
    # Column headers
    for col in range(game.cols):
        print(f"{col:2}", end=" ")
    print(f"\n   {'─' * (game.cols * 3)}{Colors.RESET}")
    
    # Board rows
    for row in range(game.rows):
        print(f"{Colors.BRIGHT_CYAN}{row:2}│{Colors.RESET}", end="")
        
        for col in range(game.cols):
            cell_color = get_cell_color(game, row, col)
            cell_char = game.get_cell_display(row, col)
            if cell_char == ".":
                cell_char = "▓"  # Unreveled cell
            elif cell_char == "F":
                cell_char = "🚩"  # Flag
            elif cell_char == "*":
                cell_char = "💥"  # Mine
            elif cell_char == " ":
                cell_char = "·"  # Empty revealed cell
                
            print(f"{cell_color}{cell_char:2}{Colors.RESET} ", end="")
        print()
    
    print(f"{Colors.BRIGHT_CYAN}   {'─' * (game.cols * 3)}{Colors.RESET}")

def print_controls():
    """Print game controls."""
    controls = f"""
{Colors.BRIGHT_GREEN}┌─ Controls ──────────────────────────────────────────────────┐
│ 📍 Reveal: r <row> <col>    🚩 Flag: f <row> <col>         │
│ 🔄 New Game: n              ❌ Quit: q                      │
└─────────────────────────────────────────────────────────────┘{Colors.RESET}
"""
    print(controls)

def choose_difficulty():
    """Let user choose difficulty level."""
    clear_screen()
    print_header()
    
    print(f"\n{Colors.BRIGHT_YELLOW}Select Difficulty:{Colors.RESET}")
    for i, diff in enumerate(ALL_DIFFICULTIES, 1):
        print(f"{Colors.BRIGHT_WHITE}{i}.{Colors.RESET} {Colors.CYAN}{diff}{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}{len(ALL_DIFFICULTIES) + 1}.{Colors.RESET} {Colors.CYAN}Custom{Colors.RESET}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BRIGHT_GREEN}Enter choice (1-{len(ALL_DIFFICULTIES) + 1}): {Colors.RESET}").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(ALL_DIFFICULTIES):
                return ALL_DIFFICULTIES[choice_num - 1]
            elif choice_num == len(ALL_DIFFICULTIES) + 1:
                return get_custom_difficulty()
            else:
                print(f"{Colors.BRIGHT_RED}Invalid choice! Please try again.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Please enter a valid number.{Colors.RESET}")

def get_custom_difficulty():
    """Get custom difficulty parameters."""
    print(f"\n{Colors.BRIGHT_YELLOW}Custom Difficulty Setup:{Colors.RESET}")
    
    while True:
        try:
            rows = int(input(f"{Colors.CYAN}Rows (5-30): {Colors.RESET}"))
            if 5 <= rows <= 30:
                break
            print(f"{Colors.BRIGHT_RED}Rows must be between 5 and 30.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Please enter a valid number.{Colors.RESET}")
    
    while True:
        try:
            cols = int(input(f"{Colors.CYAN}Columns (5-50): {Colors.RESET}"))
            if 5 <= cols <= 50:
                break
            print(f"{Colors.BRIGHT_RED}Columns must be between 5 and 50.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Please enter a valid number.{Colors.RESET}")
    
    max_mines = rows * cols - 9
    while True:
        try:
            mines = int(input(f"{Colors.CYAN}Mines (1-{max_mines}): {Colors.RESET}"))
            if 1 <= mines <= max_mines:
                break
            print(f"{Colors.BRIGHT_RED}Mines must be between 1 and {max_mines}.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Please enter a valid number.{Colors.RESET}")
    
    while True:
        try:
            lives = int(input(f"{Colors.CYAN}Lives (0 for hardcore): {Colors.RESET}"))
            if lives >= 0:
                break
            print(f"{Colors.BRIGHT_RED}Lives must be 0 or greater.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Please enter a valid number.{Colors.RESET}")
    
    return create_custom_difficulty(rows, cols, mines, lives)

def play_game(difficulty):
    """Main game loop."""
    game = Minesweeper(difficulty.rows, difficulty.cols, difficulty.mines, difficulty.lives)
    
    while True:
        clear_screen()
        print_header()
        print_game_info(game)
        print_board(game)
        print_controls()
        
        # Check game state
        if game.state == GameState.WON:
            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}🎉 CONGRATULATIONS! YOU WON! 🎉{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Time: {game.get_game_time():.1f} seconds{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
            return
        elif game.state == GameState.LOST:
            game.reveal_all_mines()
            clear_screen()
            print_header()
            print_game_info(game)
            print_board(game)
            print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}💥 GAME OVER! 💥{Colors.RESET}")
            if game.max_lives > 0:
                print(f"{Colors.BRIGHT_RED}You ran out of lives!{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_RED}You hit a mine!{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
            return
        
        # Get user input
        try:
            command = input(f"\n{Colors.BRIGHT_GREEN}Enter command: {Colors.RESET}").strip().lower()
            
            if command == 'q':
                return
            elif command == 'n':
                break  # Start new game
            
            parts = command.split()
            if len(parts) == 3:
                action, row_str, col_str = parts
                try:
                    row, col = int(row_str), int(col_str)
                    
                    if action == 'r':
                        success = game.reveal_cell(row, col)
                        if not success and game.current_lives > 0:
                            print(f"\n{Colors.BRIGHT_RED}💥 You hit a mine! Lives remaining: {game.current_lives}{Colors.RESET}")
                            input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
                    elif action == 'f':
                        game.toggle_flag(row, col)
                    else:
                        print(f"{Colors.BRIGHT_RED}Invalid action! Use 'r' for reveal or 'f' for flag.{Colors.RESET}")
                        input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
                        
                except ValueError:
                    print(f"{Colors.BRIGHT_RED}Invalid coordinates! Use numbers only.{Colors.RESET}")
                    input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_RED}Invalid command format! Use: action row col{Colors.RESET}")
                input(f"{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.BRIGHT_YELLOW}Game interrupted. Goodbye!{Colors.RESET}")
            return

def main():
    """Main CLI entry point."""
    while True:
        difficulty = choose_difficulty()
        play_game(difficulty)
        
        # Ask if player wants to play again
        while True:
            play_again = input(f"\n{Colors.BRIGHT_GREEN}Play again? (y/n): {Colors.RESET}").strip().lower()
            if play_again in ['y', 'yes']:
                break
            elif play_again in ['n', 'no']:
                print(f"\n{Colors.BRIGHT_CYAN}Thanks for playing! 👋{Colors.RESET}")
                return
            else:
                print(f"{Colors.BRIGHT_RED}Please enter 'y' or 'n'.{Colors.RESET}")

if __name__ == "__main__":
    main()
