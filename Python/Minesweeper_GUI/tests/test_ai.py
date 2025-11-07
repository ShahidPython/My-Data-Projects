
"""
Unit tests for the AI solver.
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from minesweeper.core import Minesweeper, GameState
from minesweeper.ai_solver import MinesweeperAI
from minesweeper.difficulty import BEGINNER

class TestMinesweeperAI(unittest.TestCase):
    """Test cases for Minesweeper AI solver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = Minesweeper(9, 9, 10, 0, seed=42)  # Fixed seed for reproducible tests
        self.ai = MinesweeperAI(self.game, verbose=False)
        
    def test_ai_initialization(self):
        """Test AI initialization."""
        self.assertEqual(self.ai.moves_made, 0)
        self.assertEqual(self.ai.logical_moves, 0)
        self.assertEqual(self.ai.guess_moves, 0)
        self.assertFalse(self.ai.verbose)
        
    def test_get_neighbors(self):
        """Test AI neighbor calculation."""
        # Test corner
        neighbors = self.ai.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)
        
        # Test center
        neighbors = self.ai.get_neighbors(4, 4)
        self.assertEqual(len(neighbors), 8)
        
        # Test edge
        neighbors = self.ai.get_neighbors(0, 4)
        self.assertEqual(len(neighbors), 5)
        
    def test_analyze_cell(self):
        """Test cell analysis logic."""
        # Place mines manually for testing
        self.game.place_mines(0, 0)
        
        # Find a revealed cell with a number
        self.game.reveal_cell(0, 0)  # Reveal starting position
        
        # Look for a cell with neighbors to analyze
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if (self.game.revealed[row][col] and 
                    self.game.numbers[row][col] > 0):
                    
                    safe_cells, mine_cells = self.ai.analyze_cell(row, col)
                    
                    # Results should be lists
                    self.assertIsInstance(safe_cells, list)
                    self.assertIsInstance(mine_cells, list)
                    
                    # All returned cells should be valid positions
                    for r, c in safe_cells + mine_cells:
                        self.assertTrue(self.game.is_valid_position(r, c))
                    
                    return  # Test passed
                    
    def test_make_logical_move(self):
        """Test logical move making."""
        # Start game
        self.game.reveal_cell(4, 4)
        
        initial_moves = self.ai.moves_made
        
        # Try to make logical moves
        progress = self.ai.make_logical_move()
        
        # Should be boolean
        self.assertIsInstance(progress, bool)
        
        # If progress was made, moves should increase
        if progress:
            self.assertGreater(self.ai.moves_made, initial_moves)
            
    def test_make_educated_guess(self):
        """Test educated guessing."""
        # Start game
        self.game.reveal_cell(4, 4)
        
        initial_moves = self.ai.moves_made
        
        # Make a guess
        success = self.ai.make_educated_guess()
        
        # Should return boolean
        self.assertIsInstance(success, bool)
        
        # Should have made a move
        self.assertGreater(self.ai.moves_made, initial_moves)
        self.assertGreater(self.ai.guess_moves, 0)
        
    def test_solve_step(self):
        """Test single solving step."""
        initial_state = self.game.state
        
        # Should be able to make a step
        result = self.ai.solve_step()
        
        # Should return boolean
        self.assertIsInstance(result, bool)
        
        # If game was playing, should have made a move
        if initial_state == GameState.PLAYING and result:
            self.assertGreater(self.ai.moves_made, 0)
            
    def test_solve_complete_simple(self):
        """Test complete solving on a simple game."""
        # Create a very simple game
        simple_game = Minesweeper(5, 5, 3, 0, seed=123)
        simple_ai = MinesweeperAI(simple_game, verbose=False)
        
        # Try to solve completely
        result = simple_ai.solve_complete(max_steps=100)
        
        # Should return boolean
        self.assertIsInstance(result, bool)
        
        # Game should be finished
        self.assertIn(simple_game.state, [GameState.WON, GameState.LOST])
        
        # Should have made some moves
        self.assertGreater(simple_ai.moves_made, 0)
        
    def test_get_statistics(self):
        """Test statistics generation."""
        # Make some moves
        self.ai.solve_step()
        
        stats = self.ai.get_statistics()
        
        # Check required fields
        required_fields = ['total_moves', 'logical_moves', 'guess_moves', 
                          'success_rate', 'game_state']
        for field in required_fields:
            self.assertIn(field, stats)
            
        # Check types
        self.assertIsInstance(stats['total_moves'], int)
        self.assertIsInstance(stats['logical_moves'], int)
        self.assertIsInstance(stats['guess_moves'], int)
        self.assertIsInstance(stats['success_rate'], float)
        self.assertIsInstance(stats['game_state'], GameState)
        
        # Check logical constraints
        self.assertEqual(stats['total_moves'], self.ai.moves_made)
        self.assertEqual(stats['logical_moves'], self.ai.logical_moves)
        self.assertEqual(stats['guess_moves'], self.ai.guess_moves)
        self.assertEqual(stats['total_moves'], 
                        stats['logical_moves'] + stats['guess_moves'])
        self.assertTrue(0.0 <= stats['success_rate'] <= 1.0)
        
    def test_ai_no_moves_on_finished_game(self):
        """Test AI doesn't make moves on finished game."""
        # Force game to end
        self.game.state = GameState.WON
        
        initial_moves = self.ai.moves_made
        
        # Try to make moves
        result = self.ai.solve_step()
        
        # Should not make moves
        self.assertFalse(result)
        self.assertEqual(self.ai.moves_made, initial_moves)

class TestAIPerformance(unittest.TestCase):
    """Test AI performance on different difficulties."""
    
    def test_ai_on_beginner(self):
        """Test AI performance on beginner difficulty."""
        wins = 0
        total_games = 5
        
        for _ in range(total_games):
            game = Minesweeper(BEGINNER.rows, BEGINNER.cols, BEGINNER.mines, 0)
            ai = MinesweeperAI(game, verbose=False)
            
            success = ai.solve_complete(max_steps=200)
            if success:
                wins += 1
                
        # AI should win at least some beginner games
        win_rate = wins / total_games
        self.assertGreater(win_rate, 0.0)  # Should win at least some games
        
        # Print result for information
        print(f"AI won {wins}/{total_games} beginner games ({win_rate:.1%})")

if __name__ == '__main__':
    unittest.main()
