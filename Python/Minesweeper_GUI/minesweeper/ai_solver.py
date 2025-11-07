
"""
AI Solver for Minesweeper with both CLI and GUI visualization modes.
"""
import random
import time
import sys
import os
from typing import List, Tuple, Optional
from .core import Minesweeper, GameState
from .difficulty import BEGINNER, INTERMEDIATE, EXPERT

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class MinesweeperAI:
    """AI solver for Minesweeper using logical deduction."""
    
    def __init__(self, game: Minesweeper, verbose: bool = True):
        self.game = game
        self.verbose = verbose
        self.moves_made = 0
        self.logical_moves = 0
        self.guess_moves = 0
        
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid neighbors of a cell."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
                    neighbors.append((r, c))
        return neighbors
        
    def analyze_cell(self, row: int, col: int) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Analyze a revealed cell and return lists of cells that are definitely safe
        and definitely mines.
        """
        if not self.game.revealed[row][col] or self.game.numbers[row][col] == 0:
            return [], []
            
        neighbors = self.get_neighbors(row, col)
        hidden_neighbors = [(r, c) for r, c in neighbors 
                           if not self.game.revealed[r][c] and not self.game.flagged[r][c]]
        flagged_neighbors = [(r, c) for r, c in neighbors if self.game.flagged[r][c]]
        
        required_mines = self.game.numbers[row][col]
        found_mines = len(flagged_neighbors)
        remaining_mines = required_mines - found_mines
        
        safe_cells = []
        mine_cells = []
        
        # If we found all required mines, remaining hidden cells are safe
        if remaining_mines == 0:
            safe_cells = hidden_neighbors
        # If remaining hidden cells equals remaining mines, they're all mines
        elif len(hidden_neighbors) == remaining_mines:
            mine_cells = hidden_neighbors
            
        return safe_cells, mine_cells
        
    def make_logical_move(self) -> bool:
        """Make a logical move based on number constraints."""
        moves_made = False
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col] or self.game.numbers[row][col] == 0:
                    continue
                    
                safe_cells, mine_cells = self.analyze_cell(row, col)
                
                # Reveal safe cells
                for r, c in safe_cells:
                    if not self.game.revealed[r][c]:
                        if self.verbose:
                            print(f"AI: Revealing safe cell ({r}, {c})")
                        self.game.reveal_cell(r, c)
                        self.moves_made += 1
                        self.logical_moves += 1
                        moves_made = True
                        
                # Flag mine cells
                for r, c in mine_cells:
                    if not self.game.flagged[r][c]:
                        if self.verbose:
                            print(f"AI: Flagging mine at ({r}, {c})")
                        self.game.toggle_flag(r, c)
                        self.moves_made += 1
                        self.logical_moves += 1
                        moves_made = True
                        
        return moves_made
        
    def make_educated_guess(self) -> bool:
        """Make an educated guess when no logical moves are available."""
        # Find all unrevealed, unflagged cells
        candidates = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col] and not self.game.flagged[row][col]:
                    candidates.append((row, col))
                    
        if not candidates:
            return False
            
        # Choose a random candidate (could be improved with probability analysis)
        row, col = random.choice(candidates)
        
        if self.verbose:
            print(f"AI: Making educated guess at ({row}, {col})")
            
        success = self.game.reveal_cell(row, col)
        self.moves_made += 1
        self.guess_moves += 1
        
        return success
        
    def solve_step(self) -> bool:
        """Perform one solving step. Returns False if no moves possible."""
        if self.game.state != GameState.PLAYING:
            return False
            
        # First try logical moves
        if self.make_logical_move():
            return True
            
        # If no logical moves, make educated guess
        return self.make_educated_guess()
        
    def solve_complete(self, max_steps: int = 1000) -> bool:
        """Solve the game completely."""
        # Make initial random move
        if self.game.first_click:
            start_row = random.randint(0, self.game.rows - 1)
            start_col = random.randint(0, self.game.cols - 1)
            self.game.reveal_cell(start_row, start_col)
            self.moves_made += 1
            
        steps = 0
        while self.game.state == GameState.PLAYING and steps < max_steps:
            if not self.solve_step():
                break
            steps += 1
            
        return self.game.state == GameState.WON
        
    def get_statistics(self) -> dict:
        """Get solving statistics."""
        return {
            'total_moves': self.moves_made,
            'logical_moves': self.logical_moves,
            'guess_moves': self.guess_moves,
            'success_rate': self.logical_moves / max(1, self.moves_made),
            'game_state': self.game.state
        }

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ai_banner():
    """Print AI solver banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 AI MINESWEEPER SOLVER 🤖                ║
    ║                      Watch the AI Play                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print("\033[1;36m" + banner + "\033[0m")

def print_ai_board(game: Minesweeper):
    """Print the game board with beautiful AI formatting."""
    print(f"\n\033[1;33m   ", end="")
    
    # Column headers
    display_cols = min(game.cols, 20)  # Limit for readability
    for col in range(display_cols):
        print(f"{col:2}", end=" ")
    if game.cols > 20:
        print("...")
    else:
        print()
    print(f"   {'─' * (min(game.cols, 20) * 3)}\033[0m")
    
    # Board rows
    display_rows = min(game.rows, 15)  # Limit for readability
    for row in range(display_rows):
        print(f"\033[1;33m{row:2}│\033[0m", end="")
        
        for col in range(display_cols):
            if game.flagged[row][col]:
                print("\033[1;31m🚩\033[0m ", end=" ")
            elif not game.revealed[row][col]:
                print("\033[2;37m▓▓\033[0m ", end="")
            elif game.board[row][col]:
                print("\033[1;31m💥\033[0m ", end="")
            else:
                num = game.numbers[row][col]
                if num == 0:
                    print("\033[2;37m·\033[0m  ", end="")
                else:
                    colors = ["\033[0m", "\033[1;34m", "\033[1;32m", "\033[1;31m", 
                             "\033[1;35m", "\033[1;33m", "\033[1;36m", "\033[1;37m"]
                    color = colors[min(num, len(colors)-1)]
                    print(f"{color}{num}\033[0m  ", end="")
        
        if game.cols > 20:
            print("...")
        else:
            print()
    
    if game.rows > 15:
        print("   ...")

def print_ai_info(game: Minesweeper, ai: MinesweeperAI):
    """Print AI game information."""
    stats = ai.get_statistics()
    time_str = f"{game.get_game_time():.1f}s"
    
    info = f"""
\033[1;32m┌─ AI Game Status ──────────────────────────────────────────┐
│ ⏱️  Time: {time_str:<10} 💣 Mines: {game.get_remaining_mines():<10} State: {game.state.value:<8} │
│ 🎯 Moves: {stats['total_moves']:<10} 🧠 Logic: {stats['logical_moves']:<10} 🎲 Guess: {stats['guess_moves']:<8} │
│ 📊 Success Rate: {stats['success_rate']:.1%}                                   │
└──────────────────────────────────────────────────────────┘\033[0m
"""
    print(info)

def run_ai_cli():
    """Run AI solver in CLI mode with beautiful interface."""
    clear_screen()
    print_ai_banner()
    
    # Choose difficulty
    difficulties = [BEGINNER, INTERMEDIATE, EXPERT]
    print("\n\033[1;33mSelect Difficulty:\033[0m")
    for i, diff in enumerate(difficulties, 1):
        print(f"\033[1;37m{i}.\033[0m \033[1;36m{diff.name}\033[0m ({diff.rows}x{diff.cols}, {diff.mines} mines)")
        
    while True:
        try:
            choice = int(input("\n\033[1;32mEnter choice (1-3): \033[0m"))
            if 1 <= choice <= 3:
                difficulty = difficulties[choice - 1]
                break
            print("\033[1;31mInvalid choice!\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a number!\033[0m")
    
    print(f"\n\033[1;35m🤖 AI starting on {difficulty.name} difficulty...\033[0m")
    input("\033[1;33mPress Enter to begin...\033[0m")
    
    # Run AI game with visual updates
    wins = 0
    total_games = 5
    
    for game_num in range(total_games):
        clear_screen()
        print_ai_banner()
        print(f"\n\033[1;33m🎮 Game {game_num + 1}/{total_games}\033[0m")
        print("─" * 60)
        
        # Create game and AI
        game = Minesweeper(difficulty.rows, difficulty.cols, difficulty.mines, 0)
        ai = MinesweeperAI(game, verbose=False)
        
        # Make initial move
        start_row = random.randint(0, game.rows - 1)
        start_col = random.randint(0, game.cols - 1)
        game.reveal_cell(start_row, start_col)
        ai.moves_made = 1
        
        # Solve step by step with visual feedback
        step_count = 0
        while game.state == GameState.PLAYING and step_count < 200:
            # Update display every few steps
            if step_count % 3 == 0:
                clear_screen()
                print_ai_banner()
                print(f"\n\033[1;33m🎮 Game {game_num + 1}/{total_games} - Step {step_count}\033[0m")
                print_ai_info(game, ai)
                print_ai_board(game)
                time.sleep(0.5)  # Pause for visual effect
            
            if not ai.solve_step():
                break
            step_count += 1
        
        # Final display
        clear_screen()
        print_ai_banner()
        print(f"\n\033[1;33m🎮 Game {game_num + 1}/{total_games} - COMPLETE\033[0m")
        print_ai_info(game, ai)
        print_ai_board(game)
        
        # Show result
        if game.state == GameState.WON:
            print(f"\n\033[1;32m🎉 AI WON in {ai.moves_made} moves! 🎉\033[0m")
            wins += 1
        else:
            print(f"\n\033[1;31m💥 AI LOST after {ai.moves_made} moves 💥\033[0m")
        
        input("\n\033[1;36mPress Enter for next game...\033[0m")
    
    # Final statistics
    clear_screen()
    print_ai_banner()
    print(f"\n\033[1;32m🎯 FINAL RESULTS\033[0m")
    print("=" * 60)
    print(f"\033[1;37mDifficulty:\033[0m \033[1;36m{difficulty.name}\033[0m")
    print(f"\033[1;37mGames won:\033[0m \033[1;32m{wins}/{total_games}\033[0m ({wins/total_games:.1%})")
    
    if wins > 0:
        print(f"\n\033[1;33m🏆 AI Performance: {'Excellent' if wins >= 4 else 'Good' if wins >= 2 else 'Needs Improvement'}\033[0m")
    
    input("\n\033[1;36mPress Enter to return to main menu...\033[0m")

def run_ai_gui():
    """Run AI solver in GUI mode."""
    if not PYGAME_AVAILABLE:
        print("❌ Pygame not available! Cannot run AI GUI mode.")
        input("Press Enter to return to main menu...")
        return
        
    try:
        from .gui_pygame import COLORS
        pygame.init()
        
        # Choose difficulty
        print("\n🧠 AI Solver - GUI Mode")
        print("Select difficulty:")
        difficulties = [BEGINNER, INTERMEDIATE, EXPERT]
        for i, diff in enumerate(difficulties, 1):
            print(f"{i}. {diff.name}")
            
        while True:
            try:
                choice = int(input("Enter choice (1-3): "))
                if 1 <= choice <= 3:
                    difficulty = difficulties[choice - 1]
                    break
                print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
                
        # Setup display
        cell_size = 25
        margin = 50
        board_width = difficulty.cols * cell_size
        board_height = difficulty.rows * cell_size
        window_width = board_width + 2 * margin
        window_height = board_height + 2 * margin + 100
        
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(f"🧠 AI Solver - {difficulty.name}")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)
        
        # Create game and AI
        game = Minesweeper(difficulty.rows, difficulty.cols, difficulty.mines, 0)
        ai = MinesweeperAI(game, verbose=False)
        
        # Game state
        running = True
        paused = False
        ai_speed = 500  # ms between moves
        last_move_time = 0
        
        # Make initial move
        start_row = random.randint(0, game.rows - 1)
        start_col = random.randint(0, game.cols - 1)
        game.reveal_cell(start_row, start_col)
        
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        
            # AI move
            if (not paused and game.state == GameState.PLAYING and 
                current_time - last_move_time > ai_speed):
                ai.solve_step()
                last_move_time = current_time
                
            # Draw everything
            screen.fill(COLORS['bg'])
            
            # Draw title
            title_text = font.render(f"AI Solver - {difficulty.name}", True, COLORS['text_primary'])
            screen.blit(title_text, (margin, 10))
            
            # Draw info
            info_text = f"Moves: {ai.moves_made} | State: {game.state.value}"
            info_surface = font.render(info_text, True, COLORS['text_secondary'])
            screen.blit(info_surface, (margin, 35))
            
            # Draw controls
            controls_text = "SPACE: Pause/Resume | ESC: Exit"
            controls_surface = font.render(controls_text, True, COLORS['text_secondary'])
            screen.blit(controls_surface, (margin, window_height - 25))
            
            # Draw board
            board_y = margin + 60
            for row in range(game.rows):
                for col in range(game.cols):
                    x = margin + col * cell_size
                    y = board_y + row * cell_size
                    cell_rect = pygame.Rect(x, y, cell_size, cell_size)
                    
                    # Cell color
                    if game.flagged[row][col]:
                        color = COLORS['cell_flagged']
                        text = "F"
                    elif not game.revealed[row][col]:
                        color = COLORS['cell_hidden']
                        text = ""
                    else:
                        color = COLORS['cell_revealed']
                        if game.board[row][col]:
                            color = COLORS['cell_mine']
                            text = "*"
                        else:
                            num = game.numbers[row][col]
                            text = str(num) if num > 0 else ""
                            
                    pygame.draw.rect(screen, color, cell_rect)
                    pygame.draw.rect(screen, COLORS['text_secondary'], cell_rect, 1)
                    
                    if text:
                        text_color = COLORS['text_primary']
                        if text.isdigit():
                            num = int(text)
                            if num <= len(COLORS['number_colors']) - 1:
                                text_color = COLORS['number_colors'][num]
                                
                        text_surface = font.render(text, True, text_color)
                        text_rect = text_surface.get_rect(center=cell_rect.center)
                        screen.blit(text_surface, text_rect)
                        
            # Game over message
            if game.state != GameState.PLAYING:
                message = "🎉 AI WON!" if game.state == GameState.WON else "💥 AI LOST!"
                color = COLORS['success'] if game.state == GameState.WON else COLORS['danger']
                
                message_surface = font.render(message, True, color)
                message_rect = message_surface.get_rect(
                    center=(window_width // 2, window_height - 50)
                )
                screen.blit(message_surface, message_rect)
                
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        
    except Exception as e:
        print(f"Error running AI GUI: {e}")
        input("Press Enter to return to main menu...")

if __name__ == "__main__":
    print("Choose AI mode:")
    print("1. CLI Mode")
    print("2. GUI Mode")
    
    choice = input("Enter choice (1-2): ")
    if choice == "1":
        run_ai_cli()
    elif choice == "2":
        run_ai_gui()
    else:
        print("Invalid choice!")
