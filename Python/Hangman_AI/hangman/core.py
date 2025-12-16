"""Core hangman game logic."""
import random
from typing import List, Set

class Hangman:
    def __init__(self, word: str = None, wordlist: List[str] = None, max_lives: int = 7):
        if wordlist is None:
            # fallback wordlist
            self.wordlist = ["python","hangman","challenge","testing","assistant","programming","developer"]
        else:
            self.wordlist = wordlist

        self.secret = (word or random.choice(self.wordlist)).lower()
        self.max_lives = max_lives
        self.lives = max_lives
        self.guessed: Set[str] = set()

    @property
    def pattern(self) -> str:
        # spaced pattern for display, e.g. "_ _ a _"
        return ' '.join([c if c in self.guessed else '_' for c in self.secret])

    def visible_pattern(self) -> str:
        # compact pattern without spaces, useful for AI: " _ _ a _ " -> "__a_"
        return ''.join([c if c in self.guessed else '_' for c in self.secret])

    def guess(self, ch: str) -> bool:
        ch = ch.lower()
        if not ch or len(ch) != 1 or not ch.isalpha():
            return False
        if ch in self.guessed:
            return False
        self.guessed.add(ch)
        if ch not in self.secret:
            self.lives -= 1
            return False
        return True

    def is_won(self) -> bool:
        return all(c in self.guessed for c in self.secret)

    def is_lost(self) -> bool:
        return self.lives <= 0

    def is_finished(self) -> bool:
        return self.is_won() or self.is_lost()
