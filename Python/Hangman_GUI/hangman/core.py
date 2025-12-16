from __future__ import annotations
import random
import string
from dataclasses import dataclass, field
from typing import Iterable, Set, List, Optional

DEFAULT_WORDS = [
    "python", "variable", "function", "iterator", "package", "library",
    "testing", "developer", "computer", "terminal", "interface", "socket",
    "network", "thread", "process", "module", "package", "context",
    "algorithm", "structure", "database", "version", "control", "commit",
    "virtual", "environment", "request", "response", "exception", "manager"
]

@dataclass
class HangmanGame:
    secret_word: str | None = None
    max_lives: int = 6
    words: List[str] = field(default_factory=lambda: DEFAULT_WORDS.copy())

    def __post_init__(self):
        if self.secret_word is None:
            self.secret_word = random.choice(self.words).lower()
        self.secret_word = "".join(ch for ch in self.secret_word.lower() if ch in string.ascii_lowercase)
        if not self.secret_word:
            raise ValueError("Secret word must contain at least one alphabetic character.")
        self._guessed: Set[str] = set()
        self._wrong: Set[str] = set()

    @property
    def lives_left(self) -> int:
        return self.max_lives - len(self._wrong)

    @property
    def guessed_letters(self) -> Set[str]:
        return set(self._guessed)

    @property
    def wrong_letters(self) -> Set[str]:
        return set(self._wrong)

    def masked_word(self) -> str:
        return " ".join([c if c in self._guessed else "_" for c in self.secret_word])

    def is_won(self) -> bool:
        return all(c in self._guessed for c in self.secret_word)

    def is_lost(self) -> bool:
        return self.lives_left <= 0 and not self.is_won()

    def is_over(self) -> bool:
        return self.is_won() or self.is_lost()

    def guess(self, letter: str) -> tuple[bool, str]:
        """Return (is_correct, message). Ignores non-alpha; handles repeats."""
        if not letter:
            return False, "Please enter a letter."
        ch = letter.lower().strip()
        if len(ch) != 1 or ch not in string.ascii_lowercase:
            return False, "Enter a single alphabetic letter (a-z)."
        if ch in self._guessed or ch in self._wrong:
            return False, f"You already guessed '{ch}'."
        if ch in self.secret_word:
            self._guessed.add(ch)
            if self.is_won():
                return True, "Correct! You've revealed the whole word!"
            return True, f"Good guess: '{ch}' is in the word."
        else:
            self._wrong.add(ch)
            if self.is_lost():
                return False, "Wrong guess and no lives left. Game over."
            return False, f"'{ch}' is not in the word. Lives left: {self.lives_left}"

    def reveal(self) -> str:
        return self.secret_word

    def reset(self, secret_word: str | None = None, words: Iterable[str] | None = None):
        if secret_word is not None:
            self.secret_word = str(secret_word).lower()
        elif words is not None:
            self.words = list(words)
            self.secret_word = random.choice(self.words).lower()
        else:
            self.secret_word = random.choice(self.words).lower()
        self.secret_word = "".join(ch for ch in self.secret_word.lower() if ch in string.ascii_lowercase)
        if not self.secret_word:
            raise ValueError("Secret word must contain at least one alphabetic character.")
        self._guessed.clear()
        self._wrong.clear()

    def get_hint(self) -> Optional[str]:
        """Get a hint (random unguessed letter) or None if no hints available"""
        unguessed = [c for c in self.secret_word if c not in self._guessed]
        return random.choice(unguessed) if unguessed else None

    def get_game_state(self) -> dict:
        """Return the current game state as a dictionary"""
        return {
            "secret_word": self.secret_word,
            "max_lives": self.max_lives,
            "guessed_letters": list(self._guessed),
            "wrong_letters": list(self._wrong),
            "lives_left": self.lives_left,
            "masked_word": self.masked_word(),
            "is_won": self.is_won(),
            "is_lost": self.is_lost(),
            "is_over": self.is_over()
        }

    def set_game_state(self, state: dict) -> bool:
        """Set the game state from a dictionary. Returns True if successful."""
        try:
            self.secret_word = state["secret_word"]
            self.max_lives = state["max_lives"]
            self._guessed = set(state["guessed_letters"])
            self._wrong = set(state["wrong_letters"])
            return True
        except (KeyError, TypeError):
            return False