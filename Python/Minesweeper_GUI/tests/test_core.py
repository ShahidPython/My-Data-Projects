
"""
Unit tests for the core Minesweeper game logic.
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from minesweeper.core import Minesweeper, GameState
from minesweeper.difficulty import BEGINNER

class TestMinesweeper(unittest.TestCase):
    """Test cases for Minesweeper core functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = Minesweeper(9, 9, 10, 3, seed=42)  # Fixed seed for reproducible tests
        
    def test_initialization(self):
        """Test game initialization."""
        self.assertEqual(self.game.rows, 9)
        self.assertEqual(self.game.cols, 9)
        self.assertEqual(self.game.total_mines, 10)
        self.assertEqual(self.game.max_lives, 3)
        self.assertEqual(self.game.current_lives, 3)
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertTrue(self.game.first_click)
        
    def test_board_dimensions(self):
        """Test board has correct dimensions."""
        self.assertEqual(len(self.game.board), 9)
        self.assertEqual(len(self.game.board[0]), 9)
        self.assertEqual(len(self.game.revealed), 9)
        self.assertEqual(len(self.game.flagged), 9)
        self.assertEqual(len(self.game.numbers), 9)
        
    def test_valid_position(self):
        """Test position validation."""
        self.assertTrue(self.game.is_valid_position(0, 0))
        self.assertTrue(self.game.is_valid_position(8, 8))
        self.assertFalse(self.game.is_valid_position(-1, 0))
        self.assertFalse(self.game.is_valid_position(0, -1))
        self.assertFalse(self.game.is_valid_position(9, 0))
        self.assertFalse(self.game.is_valid_position(0, 9))
        
    def test_neighbors(self):
        """Test neighbor calculation."""
        # Corner cell
        neighbors = self.game.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)
        self.assertIn((0, 1), neighbors)
        self.assertIn((1, 0), neighbors)
        self.assertIn((1, 1), neighbors)
        
        # Center cell
        neighbors = self.game.get_neighbors(4, 4)
        self.assertEqual(len(neighbors), 8)
        
        # Edge cell
        neighbors = self.game.get_neighbors(0, 4)
        self.assertEqual(len(neighbors), 5)
        
    def test_first_click_mine_placement(self):
        """Test that mines are placed after first click."""
        self.assertFalse(self.game.mines_placed)
        
        # First click should place mines
        self.game.reveal_cell(4, 4)
        self.assertTrue(self.game.mines_placed)
        self.assertFalse(self.game.first_click)
        
        # First click position should not be a mine
        self.assertFalse(self.game.board[4][4])
        
        # Should have correct number of mines
        mine_count = sum(sum(row) for row in self.game.board)
        self.assertEqual(mine_count, 10)
        
    def test_flag_toggle(self):
        """Test flag toggling."""
        # Should be able to flag unrevealed cell
        self.assertTrue(self.game.toggle_flag(0, 0))
        self.assertTrue(self.game.flagged[0][0])
        
        # Should be able to unflag
        self.assertTrue(self.game.toggle_flag(0, 0))
        self.assertFalse(self.game.flagged[0][0])
        
        # Should not be able to flag revealed cell
        self.game.reveal_cell(1, 1)  # This will place mines
        self.game.revealed[2][2] = True  # Manually reveal a cell
        self.assertFalse(self.game.toggle_flag(2, 2))
        
    def test_life_system(self):
        """Test life system when hitting mines."""
        self.game.reveal_cell(0, 0)  # Place mines
        
        # Find a mine and hit it
        mine_row, mine_col = None, None
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col]:
                    mine_row, mine_col = row, col
                    break
            if mine_row is not None:
                break
                
        self.assertIsNotNone(mine_row)
        
        # Hit mine - should lose life but continue playing
        initial_lives = self.game.current_lives
        success = self.game.reveal_cell(mine_row, mine_col)
        
        self.assertFalse(success)  # Should return False for mine hit
        self.assertEqual(self.game.current_lives, initial_lives - 1)
        self.assertEqual(self.game.state, GameState.PLAYING)  # Should still be playing
        
    def test_game_over_no_lives(self):
        """Test game over when lives run out."""
        self.game.current_lives = 1  # Set to 1 life
        self.game.reveal_cell(0, 0)  # Place mines
        
        # Find and hit a mine
        mine_row, mine_col = None, None
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col]:
                    mine_row, mine_col = row, col
                    break
            if mine_row is not None:
                break
                
        # Hit mine with last life
        self.game.reveal_cell(mine_row, mine_col)
        
        self.assertEqual(self.game.current_lives, 0)
        self.assertEqual(self.game.state, GameState.LOST)
        
    def test_remaining_mines_count(self):
        """Test remaining mines calculation."""
        initial_remaining = self.game.get_remaining_mines()
        self.assertEqual(initial_remaining, 10)
        
        # Place a flag
        self.game.toggle_flag(0, 0)
        self.assertEqual(self.game.get_remaining_mines(), 9)
        
        # Remove flag
        self.game.toggle_flag(0, 0)
        self.assertEqual(self.game.get_remaining_mines(), 10)
        
    def test_cell_display(self):
        """Test cell display strings."""
        # Unrevealed cell
        self.assertEqual(self.game.get_cell_display(0, 0), ".")
        
        # Flag cell
        self.game.toggle_flag(0, 0)
        self.assertEqual(self.game.get_cell_display(0, 0), "F")
        
        # Reveal cell (need to place mines first)
        self.game.reveal_cell(4, 4)  # Place mines
        
        # Find a non-mine cell and check its display
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.revealed[row][col] and not self.game.board[row][col]:
                    display = self.game.get_cell_display(row, col)
                    if self.game.numbers[row][col] == 0:
                        self.assertEqual(display, " ")
                    else:
                        self.assertEqual(display, str(self.game.numbers[row][col]))
                    return
                    
    def test_reset_game(self):
        """Test game reset functionality."""
        # Make some moves
        self.game.reveal_cell(0, 0)
        self.game.toggle_flag(1, 1)
        
        # Reset game
        self.game.reset_game()
        
        # Check everything is reset
        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertTrue(self.game.first_click)
        self.assertEqual(self.game.current_lives, self.game.max_lives)
        self.assertFalse(self.game.mines_placed)
        
        # Check boards are cleared
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self.assertFalse(self.game.revealed[row][col])
                self.assertFalse(self.game.flagged[row][col])
                self.assertFalse(self.game.board[row][col])
                self.assertEqual(self.game.numbers[row][col], 0)

class TestGameWithoutLives(unittest.TestCase):
    """Test game without lives system (hardcore mode)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = Minesweeper(9, 9, 10, 0, seed=42)  # No lives
        
    def test_immediate_game_over_on_mine(self):
        """Test that game ends immediately when hitting mine without lives."""
        self.game.reveal_cell(0, 0)  # Place mines
        
        # Find and hit a mine
        mine_row, mine_col = None, None
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.board[row][col]:
                    mine_row, mine_col = row, col
                    break
            if mine_row is not None:
                break
                
        # Hit mine - should end game immediately
        success = self.game.reveal_cell(mine_row, mine_col)
        
        self.assertFalse(success)
        self.assertEqual(self.game.state, GameState.LOST)

if __name__ == '__main__':
    unittest.main()
