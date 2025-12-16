import pytest
from hangman.ai_solver import AISolver

@pytest.fixture()
def sample_wordlist():
    return ['python','hangman','testing','programming','developer','assistant']

def test_next_guess_reduces_candidates(sample_wordlist):
    ai = AISolver(sample_wordlist)
    pattern = '_______'  # 7-letter pattern
    g = ai.next_guess(pattern)
    assert g is not None
    assert g in ai.guessed

def test_solve_known_word(sample_wordlist):
    ai = AISolver(sample_wordlist)
    res = ai.solve('hangman', max_lives=10)
    assert isinstance(res, dict)
    assert 'solved' in res
