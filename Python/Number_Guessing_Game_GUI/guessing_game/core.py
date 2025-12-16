import random
from enum import Enum

class Difficulty(Enum):
    EASY = (1, 50, 10)
    MEDIUM = (1, 100, 7)
    HARD = (1, 200, 5)
    CUSTOM = (0, 0, 0)

class GameMode(Enum):
    NORMAL = "normal"
    TIMED = "timed"
    LIMITED = "limited"

class NumberGuessingGame:
    def __init__(self, difficulty: Difficulty = Difficulty.MEDIUM, 
                 custom_range: tuple = None, mode: GameMode = GameMode.NORMAL):
        self.difficulty = difficulty
        self.mode = mode
        
        if difficulty == Difficulty.CUSTOM and custom_range:
            self.lower, self.upper, self.max_attempts = custom_range[0], custom_range[1], custom_range[2]
        else:
            self.lower, self.upper, self.max_attempts = difficulty.value
        
        self.secret_number = random.randint(self.lower, self.upper)
        self.attempts = 0
        self.guess_history = []
        self.game_over = False
        self.win = False
        
        # For timed mode
        self.start_time = None
        self.end_time = None

    def guess(self, number: int) -> dict:
        """Check the player's guess and return feedback with additional data."""
        if self.game_over:
            return {"message": "Game is already over!", "valid": False}
        
        self.attempts += 1
        self.guess_history.append(number)
        
        # Check if guess is out of range
        if number < self.lower or number > self.upper:
            return {"message": f"Guess out of range! Try between {self.lower} and {self.upper}.", "valid": False}
        
        # Check if guess is correct
        if number == self.secret_number:
            self.game_over = True
            self.win = True
            return {
                "message": "Correct! 🎉",
                "distance": 0,
                "attempts": self.attempts,
                "history": self.guess_history,
                "game_over": True,
                "win": True
            }
        
        # Check if maximum attempts reached
        if self.attempts >= self.max_attempts:
            self.game_over = True
            return {
                "message": f"Game over! The number was {self.secret_number}.",
                "distance": abs(number - self.secret_number),
                "attempts": self.attempts,
                "history": self.guess_history,
                "game_over": True,
                "win": False
            }
        
        # Provide feedback with distance
        distance = abs(number - self.secret_number)
        if distance <= 5:
            heat = "🔥 Very hot!"
        elif distance <= 15:
            heat = "☀️ Hot!"
        elif distance <= 30:
            heat = "🌤 Warm"
        else:
            heat = "❄️ Cold"
        
        direction = "Too low!" if number < self.secret_number else "Too high!"
        
        return {
            "message": f"{direction} {heat}",
            "distance": distance,
            "attempts": self.attempts,
            "history": self.guess_history,
            "game_over": False,
            "win": False
        }
    
    def get_hint(self) -> str:
        """Provide a hint about the secret number."""
        if self.secret_number % 2 == 0:
            return "Hint: The number is even."
        else:
            return "Hint: The number is odd."
    
    def reset(self):
        """Reset the game with a new secret number."""
        self.secret_number = random.randint(self.lower, self.upper)
        self.attempts = 0
        self.guess_history = []
        self.game_over = False
        self.win = False