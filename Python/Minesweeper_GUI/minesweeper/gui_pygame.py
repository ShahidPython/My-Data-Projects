"""
Ultra-compatible Pygame GUI for Minesweeper
"""
import pygame
import os
import sys
from pathlib import Path

# Set environment variables for maximum compatibility
os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'

# Add parent directory to path to fix import issues
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from minesweeper.core import Minesweeper, GameState
    from minesweeper.difficulty import BEGINNER
except ImportError:
    # Fallback imports if package structure fails
    class GameState:
        PLAYING = "playing"
        WON = "won"
        LOST = "lost"
    
    class Minesweeper:
        def __init__(self, rows=9, cols=9, mines=10, lives=0):
            self.rows = rows
            self.cols = cols
            self.total_mines = mines
            self.max_lives = lives
            self.current_lives = lives
            self.state = GameState.PLAYING
            self.first_click = True
            self.start_time = None
            self.reset_game()
        
        def reset_game(self):
            self.board = [[False for _ in range(self.cols)] for _ in range(self.rows)]
            self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
            self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
            self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            self.state = GameState.PLAYING
            self.first_click = True
            self.current_lives = self.max_lives
        
        def reveal_cell(self, row, col):
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                return False
            if self.revealed[row][col] or self.flagged[row][col]:
                return True
            if self.state != GameState.PLAYING:
                return False
            
            # Simple mine placement on first click
            if self.first_click:
                import random
                positions = []
                for r in range(self.rows):
                    for c in range(self.cols):
                        if abs(r - row) > 1 or abs(c - col) > 1:
                            positions.append((r, c))
                
                mine_positions = random.sample(positions, min(self.total_mines, len(positions)))
                for r, c in mine_positions:
                    self.board[r][c] = True
                
                # Calculate numbers
                for r in range(self.rows):
                    for c in range(self.cols):
                        if not self.board[r][c]:
                            count = 0
                            for dr in [-1, 0, 1]:
                                for dc in [-1, 0, 1]:
                                    if dr == 0 and dc == 0:
                                        continue
                                    nr, nc = r + dr, c + dc
                                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                        if self.board[nr][nc]:
                                            count += 1
                            self.numbers[r][c] = count
                
                self.first_click = False
                self.start_time = pygame.time.get_ticks() / 1000
            
            self.revealed[row][col] = True
            
            if self.board[row][col]:
                if self.max_lives > 0:
                    self.current_lives -= 1
                    if self.current_lives <= 0:
                        self.state = GameState.LOST
                else:
                    self.state = GameState.LOST
                return False
            
            # Auto-reveal zeros
            if self.numbers[row][col] == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                                self.reveal_cell(nr, nc)
            
            # Check win condition
            self._check_win()
            return True
        
        def toggle_flag(self, row, col):
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                return False
            if self.revealed[row][col] or self.state != GameState.PLAYING:
                return False
            self.flagged[row][col] = not self.flagged[row][col]
            self._check_win()
            return True
        
        def _check_win(self):
            revealed_safe = 0
            total_safe = self.rows * self.cols - self.total_mines
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.revealed[r][c] and not self.board[r][c]:
                        revealed_safe += 1
            if revealed_safe == total_safe:
                self.state = GameState.WON
        
        def get_remaining_mines(self):
            flags = sum(sum(row) for row in self.flagged)
            return max(0, self.total_mines - flags)
        
        def get_game_time(self):
            if self.start_time is None:
                return 0
            if self.state != GameState.PLAYING:
                return self.end_time if hasattr(self, 'end_time') else 0
            return pygame.time.get_ticks() / 1000 - self.start_time
    
    BEGINNER = type('Difficulty', (), {
        'rows': 9, 
        'cols': 9, 
        'mines': 10, 
        'lives': 3,
        'name': 'Beginner'
    })()

class UltraSimpleMinesweeperGUI:
    def __init__(self):
        # Use a very small window to avoid display issues
        self.screen_width = 600
        self.screen_height = 500
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minesweeper")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Start with beginner difficulty
        self.game = Minesweeper(BEGINNER.rows, BEGINNER.cols, BEGINNER.mines, BEGINNER.lives)
        self.cell_size = 30
        self.board_x = 50
        self.board_y = 80
        
        self.running = True
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart_game()
    
    def handle_click(self, event):
        x, y = event.pos
        
        # Check if click is on board
        if (self.board_x <= x < self.board_x + self.game.cols * self.cell_size and
            self.board_y <= y < self.board_y + self.game.rows * self.cell_size):
            
            col = (x - self.board_x) // self.cell_size
            row = (y - self.board_y) // self.cell_size
            
            if event.button == 1:  # Left click - reveal
                self.game.reveal_cell(row, col)
            elif event.button == 3:  # Right click - flag
                self.game.toggle_flag(row, col)
    
    def restart_game(self):
        self.game = Minesweeper(BEGINNER.rows, BEGINNER.cols, BEGINNER.mines, BEGINNER.lives)
    
    def draw(self):
        # Clear screen with dark background
        self.screen.fill((40, 44, 52))
        
        # Draw title
        title = self.font.render("Minesweeper", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # Draw game info
        info_text = f"Mines: {self.game.get_remaining_mines()} | Time: {int(self.game.get_game_time())}s"
        if self.game.max_lives > 0:
            info_text += f" | Lives: {self.game.current_lives}"
        
        info = self.small_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info, (20, 50))
        
        # Draw board background
        board_width = self.game.cols * self.cell_size
        board_height = self.game.rows * self.cell_size
        pygame.draw.rect(self.screen, (60, 60, 60), 
                        (self.board_x - 5, self.board_y - 5, 
                         board_width + 10, board_height + 10))
        
        # Draw cells
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self.draw_cell(row, col)
        
        # Draw game state
        if self.game.state == GameState.WON:
            state_text = self.font.render("You Win! Press R to restart", True, (100, 255, 100))
            self.screen.blit(state_text, (self.screen_width // 2 - 120, self.screen_height - 40))
        elif self.game.state == GameState.LOST:
            state_text = self.font.render("Game Over! Press R to restart", True, (255, 100, 100))
            self.screen.blit(state_text, (self.screen_width // 2 - 120, self.screen_height - 40))
        
        # Draw controls
        controls = self.small_font.render("Left: Reveal | Right: Flag | R: Restart | ESC: Quit", 
                                         True, (150, 150, 150))
        self.screen.blit(controls, (20, self.screen_height - 25))
    
    def draw_cell(self, row, col):
        x = self.board_x + col * self.cell_size
        y = self.board_y + row * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        
        # Determine cell color
        if self.game.flagged[row][col]:
            color = (255, 100, 100)  # Red for flags
        elif not self.game.revealed[row][col]:
            color = (150, 150, 150)  # Gray for hidden
        else:
            if self.game.board[row][col]:
                color = (255, 50, 50)  # Red for mines
            else:
                color = (200, 200, 200)  # Light gray for revealed
        
        # Draw cell
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (80, 80, 80), rect, 1)  # Border
        
        # Draw cell content
        if self.game.revealed[row][col] and self.game.board[row][col]:
            # Mine
            text = self.small_font.render("X", True, (0, 0, 0))
            self.screen.blit(text, (x + 10, y + 8))
        elif self.game.revealed[row][col] and self.game.numbers[row][col] > 0:
            # Number
            number_colors = [
                (0, 0, 0), (0, 0, 255), (0, 128, 0), (255, 0, 0),
                (0, 0, 128), (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)
            ]
            color_idx = min(self.game.numbers[row][col], len(number_colors) - 1)
            text = self.small_font.render(str(self.game.numbers[row][col]), True, number_colors[color_idx])
            self.screen.blit(text, (x + 10, y + 8))
        elif self.game.flagged[row][col]:
            # Flag
            text = self.small_font.render("F", True, (255, 255, 255))
            self.screen.blit(text, (x + 10, y + 8))
    
    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.draw()
                pygame.display.flip()
                self.clock.tick(60)
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            pygame.quit()

def main():
    """Main entry point - with maximum error handling"""
    try:
        print("Initializing Pygame...")
        pygame.init()
        print("Pygame initialized successfully!")
        
        game = UltraSimpleMinesweeperGUI()
        print("Starting game loop...")
        game.run()
        
    except pygame.error as e:
        print(f"Pygame error: {e}")
        print("Try running with: export SDL_VIDEODRIVER=x11")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        pygame.quit()
        print("Game closed.")

if __name__ == "__main__":
    main()