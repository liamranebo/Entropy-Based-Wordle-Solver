import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wordle_solver import Wordle

DUMMY_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


@pytest.fixture
def make_wordle():
    """Factory fixture: build a Wordle instance, populating all_patterns by default."""

    def _make(data_set_words, solution, length=5, num_attempts=6, with_patterns=True):
        wordle = Wordle(DUMMY_ALPHABET, list(data_set_words), solution, length, num_attempts)
        if with_patterns:
            wordle.all_patterns
        return wordle

    return _make