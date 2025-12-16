import unittest
from unittest.mock import patch
from game import Game, Move

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_draw(self):
        with patch("game.random.choice", return_value=Move.ROCK):
            result = self.game.play_round(Move.ROCK)
            self.assertEqual(result["result"], "draw")
            self.assertEqual(self.game.scores["draws"], 1)

    def test_player_win_rock_vs_scissors(self):
        with patch("game.random.choice", return_value=Move.SCISSORS):
            result = self.game.play_round(Move.ROCK)
            self.assertEqual(result["result"], "player")
            self.assertEqual(self.game.scores["player"], 1)

    def test_computer_win_rock_vs_paper(self):
        with patch("game.random.choice", return_value=Move.PAPER):
            result = self.game.play_round(Move.ROCK)
            self.assertEqual(result["result"], "computer")
            self.assertEqual(self.game.scores["computer"], 1)

    def test_player_win_paper_vs_rock(self):
        with patch("game.random.choice", return_value=Move.ROCK):
            result = self.game.play_round(Move.PAPER)
            self.assertEqual(result["result"], "player")
            self.assertEqual(self.game.scores["player"], 1)

    def test_computer_win_paper_vs_scissors(self):
        with patch("game.random.choice", return_value=Move.SCISSORS):
            result = self.game.play_round(Move.PAPER)
            self.assertEqual(result["result"], "computer")
            self.assertEqual(self.game.scores["computer"], 1)

    def test_player_win_scissors_vs_paper(self):
        with patch("game.random.choice", return_value=Move.PAPER):
            result = self.game.play_round(Move.SCISSORS)
            self.assertEqual(result["result"], "player")
            self.assertEqual(self.game.scores["player"], 1)

    def test_computer_win_scissors_vs_rock(self):
        with patch("game.random.choice", return_value=Move.ROCK):
            result = self.game.play_round(Move.SCISSORS)
            self.assertEqual(result["result"], "computer")
            self.assertEqual(self.game.scores["computer"], 1)

    def test_history_recording(self):
        with patch("game.random.choice", return_value=Move.ROCK):
            initial_history_count = len(self.game.history)
            self.game.play_round(Move.ROCK)
            self.assertEqual(len(self.game.history), initial_history_count + 1)

    def test_reset_function(self):
        with patch("game.random.choice", return_value=Move.ROCK):
            self.game.play_round(Move.ROCK)
            self.game.reset()
            self.assertEqual(self.game.scores, {"player": 0, "computer": 0, "draws": 0})
            self.assertEqual(len(self.game.history), 0)

if __name__ == "__main__":
    unittest.main()