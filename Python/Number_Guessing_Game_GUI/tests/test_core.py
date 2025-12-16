import pytest
from guessing_game.core import NumberGuessingGame, Difficulty

def test_game_correct_guess():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 5  # override for testing
    result = game.guess(5)
    assert result["message"] == "Correct! 🎉"
    assert result["attempts"] == 1
    assert result["win"] == True
    assert result["game_over"] == True

def test_game_too_low():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 7
    result = game.guess(3)
    assert "Too low!" in result["message"]
    assert result["attempts"] == 1
    assert result["win"] == False
    assert result["game_over"] == False

def test_game_too_high():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 4
    result = game.guess(8)
    assert "Too high!" in result["message"]
    assert result["attempts"] == 1
    assert result["win"] == False
    assert result["game_over"] == False

def test_game_max_attempts():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 10
    
    # Use all attempts with wrong guesses
    for _ in range(game.max_attempts - 1):
        game.guess(1)
    
    # Last attempt should end the game
    result = game.guess(2)
    assert result["game_over"] == True
    assert result["win"] == False

def test_hint_even():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 10  # even number
    assert "even" in game.get_hint()

def test_hint_odd():
    game = NumberGuessingGame(Difficulty.EASY)
    game.secret_number = 7  # odd number
    assert "odd" in game.get_hint()

def test_custom_difficulty():
    custom_range = (10, 50, 5)
    game = NumberGuessingGame(Difficulty.CUSTOM, custom_range)
    assert game.lower == 10
    assert game.upper == 50
    assert game.max_attempts == 5