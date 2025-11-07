
"""
Difficulty settings for Minesweeper with life system configuration.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Difficulty:
    """Difficulty configuration including life system."""
    name: str
    rows: int
    cols: int
    mines: int
    lives: int
    description: str
    
    def __str__(self) -> str:
        return f"{self.name} ({self.rows}x{self.cols}, {self.mines} mines, {self.lives} lives)"

# Predefined difficulty levels
BEGINNER = Difficulty(
    name="Beginner",
    rows=9,
    cols=9, 
    mines=10,
    lives=3,
    description="Perfect for new players with 3 lives"
)

INTERMEDIATE = Difficulty(
    name="Intermediate", 
    rows=16,
    cols=16,
    mines=40,
    lives=10,
    description="Moderate challenge with 10 lives"
)

EXPERT = Difficulty(
    name="Expert",
    rows=16,
    cols=30,
    mines=99,
    lives=15,
    description="Maximum challenge with 15 lives"
)

HARDCORE = Difficulty(
    name="Hardcore",
    rows=20,
    cols=30,
    mines=150,
    lives=0,
    description="No lives - one mistake and you're out!"
)

# List of all difficulties for easy iteration
ALL_DIFFICULTIES = [BEGINNER, INTERMEDIATE, EXPERT, HARDCORE]

def get_difficulty_by_name(name: str) -> Difficulty:
    """Get difficulty by name, case insensitive."""
    name_lower = name.lower()
    for diff in ALL_DIFFICULTIES:
        if diff.name.lower() == name_lower:
            return diff
    return BEGINNER  # Default fallback

def create_custom_difficulty(rows: int, cols: int, mines: int, lives: int = 0) -> Difficulty:
    """Create a custom difficulty configuration."""
    # Ensure valid parameters
    max_mines = max(1, rows * cols - 9)  # Leave space for first click
    mines = min(mines, max_mines)
    lives = max(0, lives)
    
    # Calculate lives based on difficulty if not specified
    if lives == 0:
        mine_density = mines / (rows * cols)
        if mine_density < 0.15:
            lives = max(1, mines // 5)  # Easy
        elif mine_density < 0.25:
            lives = max(3, mines // 8)  # Medium
        else:
            lives = max(5, mines // 12)  # Hard
    
    return Difficulty(
        name="Custom",
        rows=rows,
        cols=cols,
        mines=mines,
        lives=lives,
        description=f"Custom game: {rows}x{cols} with {mines} mines and {lives} lives"
    )
