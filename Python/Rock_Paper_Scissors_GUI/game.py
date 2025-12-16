"""Core game logic for Rock, Paper, Scissors."""

import random
from enum import Enum
import json
import os

class Move(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

WIN_MAP = {
    Move.ROCK: Move.SCISSORS,
    Move.SCISSORS: Move.PAPER,
    Move.PAPER: Move.ROCK
}

class Game:
    def __init__(self):
        self.scores = {"player": 0, "computer": 0, "draws": 0}
        self.history = []
        self.load_stats()

    def cpu_move(self):
        """Return a random move for the computer."""
        return random.choice(list(Move))

    def play_round(self, player_move: Move):
        """Play one round of the game."""
        computer_move = self.cpu_move()

        if player_move == computer_move:
            self.scores["draws"] += 1
            result = "draw"
        elif WIN_MAP[player_move] == computer_move:
            self.scores["player"] += 1
            result = "player"
        else:
            self.scores["computer"] += 1
            result = "computer"

        round_result = {
            "player": player_move.value,
            "computer": computer_move.value,
            "result": result,
            "scores": self.scores.copy(),
        }
        
        self.history.append(round_result)
        self.save_stats()
        return round_result

    def reset(self):
        """Reset the game state."""
        self.scores = {"player": 0, "computer": 0, "draws": 0}
        self.history = []
        self.save_stats()

    def save_stats(self):
        """Save game statistics to a file."""
        stats = {
            "scores": self.scores,
            "history": self.history
        }
        try:
            with open("rps_stats.json", "w") as f:
                json.dump(stats, f)
        except Exception:
            pass  # Silently fail if we can't save stats

    def load_stats(self):
        """Load game statistics from a file."""
        try:
            if os.path.exists("rps_stats.json"):
                with open("rps_stats.json", "r") as f:
                    stats = json.load(f)
                    self.scores = stats.get("scores", {"player": 0, "computer": 0, "draws": 0})
                    self.history = stats.get("history", [])
        except Exception:
            # If there's any error loading stats, reset to default
            self.scores = {"player": 0, "computer": 0, "draws": 0}
            self.history = []