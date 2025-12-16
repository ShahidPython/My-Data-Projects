
"""
Core Minesweeper game logic with enhanced features including life system.
"""
import random
import time
from typing import List, Tuple, Set, Optional
from enum import Enum

class GameState(Enum):
    """Game state enumeration."""
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    PAUSED = "paused"

class Minesweeper:
    """
    Enhanced Minesweeper game with life system and advanced features.
    """
    
    def __init__(self, rows: int = 9, cols: int = 9, mines: int = 10, 
                 lives: int = 0, seed: Optional[int] = None):
        """
        Initialize the Minesweeper game.
        
        Args:
            rows: Number of rows
            cols: Number of columns  
            mines: Number of mines
            lives: Number of lives (0 means no lives system)
            seed: Random seed for reproducible games
        """
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.max_lives = lives
        self.current_lives = lives
        self.seed = seed
        
        # Game state
        self.state = GameState.PLAYING
        self.first_click = True
        self.start_time = None
        self.end_time = None
        
        # Initialize game board
        self.reset_game()
        
    def reset_game(self):
        """Reset the game to initial state."""
        self.state = GameState.PLAYING
        self.first_click = True
        self.current_lives = self.max_lives
        self.start_time = None
        self.end_time = None
        
        # Initialize boards
        self.board = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Mine placement will happen on first click
        self.mines_placed = False
        
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols
        
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all valid neighbor positions."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if self.is_valid_position(new_row, new_col):
                    neighbors.append((new_row, new_col))
        return neighbors
        
    def place_mines(self, first_click_row: int, first_click_col: int):
        """Place mines on the board, avoiding the first click position."""
        if self.mines_placed:
            return
            
        random.seed(self.seed)
        
        # Get all positions except first click and its neighbors
        forbidden_positions = set()
        forbidden_positions.add((first_click_row, first_click_col))
        forbidden_positions.update(self.get_neighbors(first_click_row, first_click_col))
        
        available_positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in forbidden_positions:
                    available_positions.append((r, c))
        
        # Place mines randomly
        mine_positions = random.sample(available_positions, 
                                     min(self.total_mines, len(available_positions)))
        
        for row, col in mine_positions:
            self.board[row][col] = True
            
        # Calculate numbers
        self._calculate_numbers()
        self.mines_placed = True
        
    def _calculate_numbers(self):
        """Calculate numbers for each cell."""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.board[row][col]:  # Not a mine
                    count = 0
                    for neighbor_row, neighbor_col in self.get_neighbors(row, col):
                        if self.board[neighbor_row][neighbor_col]:
                            count += 1
                    self.numbers[row][col] = count
                    
    def reveal_cell(self, row: int, col: int) -> bool:
        """
        Reveal a cell and return True if successful, False if hit mine.
        """
        if not self.is_valid_position(row, col):
            return False
            
        if self.revealed[row][col] or self.flagged[row][col]:
            return True
            
        if self.state != GameState.PLAYING:
            return False
            
        # Handle first click
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()
            
        # Reveal the cell
        self.revealed[row][col] = True
        
        # Check if it's a mine
        if self.board[row][col]:
            if self.max_lives > 0:  # Lives system enabled
                self.current_lives -= 1
                if self.current_lives > 0:
                    # Still have lives, don't end game
                    return False  # Indicate mine hit but game continues
                else:
                    # No more lives
                    self.state = GameState.LOST
                    self.end_time = time.time()
                    return False
            else:
                # No lives system, game over immediately
                self.state = GameState.LOST
                self.end_time = time.time()
                return False
                
        # If it's a zero, reveal neighbors automatically
        if self.numbers[row][col] == 0:
            for neighbor_row, neighbor_col in self.get_neighbors(row, col):
                if not self.revealed[neighbor_row][neighbor_col]:
                    self.reveal_cell(neighbor_row, neighbor_col)
                    
        # Check win condition
        self._check_win_condition()
        return True
        
    def toggle_flag(self, row: int, col: int) -> bool:
        """Toggle flag on a cell."""
        if not self.is_valid_position(row, col):
            return False
            
        if self.revealed[row][col] or self.state != GameState.PLAYING:
            return False
            
        self.flagged[row][col] = not self.flagged[row][col]
        self._check_win_condition()
        return True
        
    def _check_win_condition(self):
        """Check if the player has won."""
        if self.state != GameState.PLAYING:
            return
            
        # Count revealed non-mine cells
        revealed_count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.revealed[row][col] and not self.board[row][col]:
                    revealed_count += 1
                    
        # Win if all non-mine cells are revealed
        total_non_mines = self.rows * self.cols - self.total_mines
        if revealed_count == total_non_mines:
            self.state = GameState.WON
            self.end_time = time.time()
            
    def get_remaining_mines(self) -> int:
        """Get the number of remaining mines (total mines - flags placed)."""
        flag_count = sum(sum(row) for row in self.flagged)
        return max(0, self.total_mines - flag_count)
        
    def get_game_time(self) -> float:
        """Get the current game time in seconds."""
        if self.start_time is None:
            return 0.0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.time() - self.start_time
        
    def get_cell_display(self, row: int, col: int) -> str:
        """Get display string for a cell."""
        if not self.is_valid_position(row, col):
            return " "
            
        if self.flagged[row][col]:
            return "F"
        elif not self.revealed[row][col]:
            return "."
        elif self.board[row][col]:
            return "*"
        elif self.numbers[row][col] == 0:
            return " "
        else:
            return str(self.numbers[row][col])
            
    def reveal_all_mines(self):
        """Reveal all mines (for game over display)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col]:
                    self.revealed[row][col] = True
                    
    def get_board_state(self) -> dict:
        """Get complete board state for external interfaces."""
        return {
            'rows': self.rows,
            'cols': self.cols,
            'total_mines': self.total_mines,
            'remaining_mines': self.get_remaining_mines(),
            'state': self.state,
            'current_lives': self.current_lives,
            'max_lives': self.max_lives,
            'game_time': self.get_game_time(),
            'board': self.board,
            'revealed': self.revealed,
            'flagged': self.flagged,
            'numbers': self.numbers
        }

# Compatibility aliases
def neighbors(game, row, col):
    """Legacy compatibility function."""
    return game.get_neighbors(row, col)
