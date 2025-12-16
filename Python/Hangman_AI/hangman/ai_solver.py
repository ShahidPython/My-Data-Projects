"""AI solver for Hangman.

The solver implements:
- wordlist filtering by known pattern and excluded letters
- letter frequency scoring across remaining candidates
- simple tie-breakers

This is intentionally lightweight so you can replace the internals with a ML model later.
"""
from collections import Counter
from typing import List, Set, Optional

class AISolver:
    def __init__(self, wordlist: List[str]):
        # normalize
        self.wordlist = [w.lower() for w in wordlist]
        self.candidates = list(self.wordlist)
        self.guessed: Set[str] = set()
        self.excluded: Set[str] = set()

    def reset(self):
        self.candidates = list(self.wordlist)
        self.guessed.clear()
        self.excluded.clear()

    def filter_candidates(self, pattern: str):
        # pattern: underscores for unknown, letters for known positions, no spaces
        new = []
        plen = len(pattern)
        pattern = pattern.lower()
        for w in self.candidates:
            if len(w) != plen:
                continue
            ok = True
            for i, ch in enumerate(pattern):
                if ch == '_':
                    # position unknown: if this word has a letter already guessed that contradicts
                    # (i.e., guessed letters that must appear in pattern elsewhere) we still allow;
                    # main check is that known letters must match.
                    continue
                else:
                    if w[i] != ch:
                        ok = False
                        break
            if not ok:
                continue
            # exclude words containing any excluded letters
            if any(x in w for x in self.excluded):
                continue
            # ensure that all revealed letters in pattern are indeed present in word (redundant due to position check)
            new.append(w)
        self.candidates = new

    def score_letters(self) -> Counter:
        cnt = Counter()
        for w in self.candidates:
            unique = set(w) - self.guessed
            cnt.update(unique)
        return cnt

    def next_guess(self, pattern: str, banned: Optional[Set[str]] = None) -> Optional[str]:
        if banned:
            self.excluded |= {b.lower() for b in banned}
        # normalize pattern remove spaces
        pattern = pattern.replace(' ', '')
        self.filter_candidates(pattern)
        scores = self.score_letters()
        if not scores:
            return None
        # choose highest frequency letter
        guess, _ = scores.most_common(1)[0]
        self.guessed.add(guess)
        return guess

    def solve(self, secret: str, max_lives: int = 7, verbose: bool = False) -> dict:
        self.reset()
        lives = max_lives
        # pattern as underscores
        pattern = '_' * len(secret)
        # We'll maintain guessed letters set to update pattern correctly
        while lives > 0 and '_' in pattern:
            g = self.next_guess(pattern)
            if g is None:
                break
            if g in secret:
                # reveal all positions of g
                pattern = ''.join([c if c == g or (pattern[i] != '_' and pattern[i] == c) else '_' for i, c in enumerate(secret)])
                # also reveal letters that have been guessed earlier
                pattern = ''.join([c if c in self.guessed else '_' for c in secret])
            else:
                lives -= 1
                self.excluded.add(g)
            if verbose:
                print(f"Guess: {g}, pattern: {' '.join(pattern)}, lives: {lives}")
        return {
            'solved': '_' not in pattern,
            'pattern': pattern,
            'lives_left': lives,
            'guesses': list(self.guessed),
            'candidates_left': len(self.candidates)
        }