import pytest
from hangman.core import HangmanGame

def test_initial_mask():
    game = HangmanGame(secret_word="apple", max_lives=6)
    assert game.masked_word().replace(" ", "") == "_____"
    assert game.lives_left == 6

def test_correct_guess_and_win():
    game = HangmanGame(secret_word="go", max_lives=6)
    ok, _ = game.guess("g")
    assert ok
    ok, _ = game.guess("o")
    assert ok
    assert game.is_won()
    assert not game.is_lost()
    assert game.is_over()

def test_incorrect_guesses_and_loss():
    game = HangmanGame(secret_word="hi", max_lives=2)
    ok, _ = game.guess("a")
    assert not ok and game.lives_left == 1
    ok, _ = game.guess("b")
    assert not ok
    assert game.is_lost()
    assert game.is_over()

def test_repeat_guess_rejected():
    game = HangmanGame(secret_word="cat")
    ok, _ = game.guess("c")
    assert ok
    ok, msg = game.guess("c")
    assert not ok and "already" in msg.lower()

def test_non_alpha_rejected():
    game = HangmanGame(secret_word="test")
    ok, msg = game.guess("3")
    assert not ok and "single alphabetic" in msg.lower()

def test_empty_guess_rejected():
    game = HangmanGame(secret_word="test")
    ok, msg = game.guess("")
    assert not ok and "enter a letter" in msg.lower()

def test_reset_changes_word_and_state():
    game = HangmanGame(secret_word="one", max_lives=6)
    game.guess("o")
    game.guess("x")
    game.reset(secret_word="two")
    assert game.masked_word().replace(" ", "") == "___"
    assert game.lives_left == 6
    assert "o" not in game.guessed_letters
    assert "x" not in game.wrong_letters

def test_hint_function():
    game = HangmanGame(secret_word="test")
    hint = game.get_hint()
    assert hint in "test"
    
    # After guessing all letters, hint should be None
    for letter in "test":
        game.guess(letter)
    assert game.get_hint() is None

def test_game_reset_with_hint():
    game = HangmanGame(secret_word="first")
    game.guess("f")
    game.reset(secret_word="second")
    assert game.get_hint() in "second"

def test_get_game_state():
    game = HangmanGame(secret_word="test", max_lives=5)
    game.guess("t")
    game.guess("x")
    
    state = game.get_game_state()
    
    assert state["secret_word"] == "test"
    assert state["max_lives"] == 5
    assert state["lives_left"] == 4
    assert "t" in state["guessed_letters"]
    assert "x" in state["wrong_letters"]
    assert state["masked_word"] == "t _ _ t"
    assert state["is_won"] is False
    assert state["is_lost"] is False
    assert state["is_over"] is False

def test_set_game_state():
    game = HangmanGame(secret_word="initial", max_lives=10)
    
    # Set up a new state
    new_state = {
        "secret_word": "python",
        "max_lives": 6,
        "guessed_letters": ["p", "y"],
        "wrong_letters": ["x", "z"],
        "lives_left": 4,  # This should be recalculated, not used from state
        "masked_word": "p y _ _ _ _",  # This should be recalculated, not used from state
        "is_won": False,  # This should be recalculated, not used from state
        "is_lost": False,  # This should be recalculated, not used from state
        "is_over": False   # This should be recalculated, not used from state
    }
    
    success = game.set_game_state(new_state)
    assert success is True
    
    # Verify the state was set correctly
    assert game.secret_word == "python"
    assert game.max_lives == 6
    assert game.guessed_letters == {"p", "y"}
    assert game.wrong_letters == {"x", "z"}
    assert game.lives_left == 4  # max_lives (6) - wrong_letters (2) = 4
    assert game.masked_word() == "p y _ _ _ _"
    assert game.is_won() is False
    assert game.is_lost() is False
    assert game.is_over() is False

def test_set_game_state_invalid():
    game = HangmanGame(secret_word="test")
    
    # Test with invalid state (missing required keys)
    invalid_state = {"secret_word": "test"}
    success = game.set_game_state(invalid_state)
    assert success is False
    
    # Test with None state
    success = game.set_game_state(None)
    assert success is False

def test_word_with_non_alpha_characters():
    game = HangmanGame(secret_word="test-word123")
    # Non-alpha characters should be stripped
    assert game.secret_word == "testword"
    
    # Test guessing works correctly
    ok, _ = game.guess("t")
    assert ok
    assert game.masked_word().replace(" ", "") == "t__t____"

def test_custom_word_list():
    custom_words = ["apple", "banana", "cherry"]
    game = HangmanGame(words=custom_words)
    
    # The secret word should be one of our custom words
    assert game.secret_word in custom_words

def test_empty_word_list():
    with pytest.raises(ValueError):
        HangmanGame(words=[])

def test_all_non_alpha_word():
    with pytest.raises(ValueError):
        HangmanGame(secret_word="123!@#")

def test_case_insensitive_guessing():
    game = HangmanGame(secret_word="Test")
    
    # Upper case guess should work
    ok, _ = game.guess("T")
    assert ok
    assert "t" in game.guessed_letters
    
    # Lower case guess should also work
    ok, _ = game.guess("E")
    assert ok
    assert "e" in game.guessed_letters

def test_win_condition_with_multiple_occurrences():
    game = HangmanGame(secret_word="banana")
    
    # Guess all unique letters
    for letter in "ban":
        ok, _ = game.guess(letter)
        assert ok
    
    assert game.is_won()

def test_game_state_after_win():
    game = HangmanGame(secret_word="hi")
    game.guess("h")
    game.guess("i")
    
    state = game.get_game_state()
    assert state["is_won"] is True
    assert state["is_over"] is True
    assert state["is_lost"] is False

def test_game_state_after_loss():
    game = HangmanGame(secret_word="hi", max_lives=2)
    game.guess("a")
    game.guess("b")
    
    state = game.get_game_state()
    assert state["is_won"] is False
    assert state["is_over"] is True
    assert state["is_lost"] is True

def test_reset_with_custom_words():
    game = HangmanGame(secret_word="first")
    custom_words = ["apple", "banana", "cherry"]
    game.reset(words=custom_words)
    
    assert game.secret_word in custom_words

def test_reset_with_specific_word():
    game = HangmanGame(secret_word="first")
    game.reset(secret_word="specific")
    
    assert game.secret_word == "specific"

def test_multibyte_characters():
    # Test that the game handles non-ASCII characters correctly
    game = HangmanGame(secret_word="café")
    # Non-ASCII characters should be stripped
    assert game.secret_word == "caf"
    
    ok, _ = game.guess("c")
    assert ok
    assert game.masked_word().replace(" ", "") == "c__"