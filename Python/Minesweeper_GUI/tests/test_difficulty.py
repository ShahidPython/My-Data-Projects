"""
Unit tests for the difficulty settings and configuration.
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from minesweeper.difficulty import (
    Difficulty, 
    BEGINNER, 
    INTERMEDIATE, 
    EXPERT, 
    HARDCORE, 
    ALL_DIFFICULTIES,
    get_difficulty_by_name,
    create_custom_difficulty
)

class TestDifficulty(unittest.TestCase):
    """Test cases for Difficulty class and related functions."""
    
    def test_difficulty_creation(self):
        """Test Difficulty class initialization."""
        diff = Difficulty(
            name="Test",
            rows=10,
            cols=10,
            mines=15,
            lives=5,
            description="Test difficulty"
        )
        
        self.assertEqual(diff.name, "Test")
        self.assertEqual(diff.rows, 10)
        self.assertEqual(diff.cols, 10)
        self.assertEqual(diff.mines, 15)
        self.assertEqual(diff.lives, 5)
        self.assertEqual(diff.description, "Test difficulty")
        
    def test_difficulty_string_representation(self):
        """Test Difficulty string representation."""
        diff = Difficulty(
            name="Test",
            rows=10,
            cols=10,
            mines=15,
            lives=5,
            description="Test difficulty"
        )
        
        expected_str = "Test (10x10, 15 mines, 5 lives)"
        self.assertEqual(str(diff), expected_str)
        
    def test_predefined_difficulties(self):
        """Test predefined difficulty configurations."""
        # Test Beginner
        self.assertEqual(BEGINNER.name, "Beginner")
        self.assertEqual(BEGINNER.rows, 9)
        self.assertEqual(BEGINNER.cols, 9)
        self.assertEqual(BEGINNER.mines, 10)
        self.assertEqual(BEGINNER.lives, 3)
        
        # Test Intermediate
        self.assertEqual(INTERMEDIATE.name, "Intermediate")
        self.assertEqual(INTERMEDIATE.rows, 16)
        self.assertEqual(INTERMEDIATE.cols, 16)
        self.assertEqual(INTERMEDIATE.mines, 40)
        self.assertEqual(INTERMEDIATE.lives, 10)
        
        # Test Expert
        self.assertEqual(EXPERT.name, "Expert")
        self.assertEqual(EXPERT.rows, 16)
        self.assertEqual(EXPERT.cols, 30)
        self.assertEqual(EXPERT.mines, 99)
        self.assertEqual(EXPERT.lives, 15)
        
        # Test Hardcore
        self.assertEqual(HARDCORE.name, "Hardcore")
        self.assertEqual(HARDCORE.rows, 20)
        self.assertEqual(HARDCORE.cols, 30)
        self.assertEqual(HARDCORE.mines, 150)
        self.assertEqual(HARDCORE.lives, 0)
        
    def test_all_difficulties_list(self):
        """Test ALL_DIFFICULTIES list contains all predefined difficulties."""
        self.assertEqual(len(ALL_DIFFICULTIES), 4)
        self.assertIn(BEGINNER, ALL_DIFFICULTIES)
        self.assertIn(INTERMEDIATE, ALL_DIFFICULTIES)
        self.assertIn(EXPERT, ALL_DIFFICULTIES)
        self.assertIn(HARDCORE, ALL_DIFFICULTIES)
        
    def test_get_difficulty_by_name(self):
        """Test getting difficulty by name."""
        # Test case insensitive matching
        self.assertEqual(get_difficulty_by_name("beginner"), BEGINNER)
        self.assertEqual(get_difficulty_by_name("BEGINNER"), BEGINNER)
        self.assertEqual(get_difficulty_by_name("Beginner"), BEGINNER)
        
        self.assertEqual(get_difficulty_by_name("intermediate"), INTERMEDIATE)
        self.assertEqual(get_difficulty_by_name("expert"), EXPERT)
        self.assertEqual(get_difficulty_by_name("hardcore"), HARDCORE)
        
        # Test fallback for unknown difficulty
        self.assertEqual(get_difficulty_by_name("unknown"), BEGINNER)
        
    def test_create_custom_difficulty(self):
        """Test creating custom difficulty."""
        # Test valid parameters
        custom = create_custom_difficulty(12, 12, 20, 5)
        
        self.assertEqual(custom.name, "Custom")
        self.assertEqual(custom.rows, 12)
        self.assertEqual(custom.cols, 12)
        self.assertEqual(custom.mines, 20)
        self.assertEqual(custom.lives, 5)
        self.assertIn("Custom game", custom.description)
        
    def test_create_custom_difficulty_with_mine_limit(self):
        """Test custom difficulty respects mine limit."""
        # Try to create with too many mines
        custom = create_custom_difficulty(5, 5, 25, 3)  # Max mines would be 5*5-9=16
        
        self.assertEqual(custom.mines, 16)  # Should be capped to max possible
        
    def test_create_custom_difficulty_with_auto_lives(self):
        """Test custom difficulty with automatic life calculation."""
        # Test with 0 lives specified (should auto-calculate)
        custom = create_custom_difficulty(10, 10, 20, 0)
        
        self.assertGreater(custom.lives, 0)  # Should have calculated lives
        
        # Test with different mine densities
        easy_custom = create_custom_difficulty(10, 10, 10, 0)   # Low density
        medium_custom = create_custom_difficulty(10, 10, 20, 0)  # Medium density
        hard_custom = create_custom_difficulty(10, 10, 30, 0)    # High density
        
        # Should have appropriate lives based on difficulty
        self.assertGreaterEqual(easy_custom.lives, medium_custom.lives)
        self.assertGreaterEqual(medium_custom.lives, hard_custom.lives)
        
    def test_difficulty_parameter_validation(self):
        """Test that difficulty parameters are validated."""
        # Test minimum values
        custom = create_custom_difficulty(5, 5, 1, 0)
        self.assertEqual(custom.rows, 5)
        self.assertEqual(custom.cols, 5)
        self.assertEqual(custom.mines, 1)
        
        # Test maximum values
        custom = create_custom_difficulty(30, 50, 1000, 10)  # Will be capped
        max_mines = 30 * 50 - 9  # Maximum possible mines
        self.assertEqual(custom.mines, max_mines)
        
    def test_difficulty_descriptions(self):
        """Test difficulty descriptions are appropriate."""
        self.assertIn("Perfect for new players", BEGINNER.description)
        self.assertIn("Moderate challenge", INTERMEDIATE.description)
        self.assertIn("Maximum challenge", EXPERT.description)
        self.assertIn("No lives", HARDCORE.description)

if __name__ == '__main__':
    unittest.main()