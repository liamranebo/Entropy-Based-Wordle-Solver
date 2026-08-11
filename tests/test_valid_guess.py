"""Unit tests for Wordle.valid_guess().

Scenario shared by all cases: solution is "trace", the last (and only)
guess played was "crane", which scores (yellow, green, green, grey, green)
i.e. c is present-but-misplaced, r/a/e are in the right spot, n is absent.
"""

import pytest


@pytest.fixture
def wordle_after_crane(make_wordle):
    wordle = make_wordle(["crane"], solution="trace", with_patterns=False)
    wordle.word_list("crane")
    wordle.pattern("crane", "trace")  # sets pat_current_guess since it's the last guess
    return wordle


@pytest.mark.parametrize(
    "candidate, expected",
    [
        ("trace", True),   # the true solution must always remain valid
        ("grace", True),   # has required 'c' (not at pos0), no 'n', matches greens
        ("trice", False),  # wrong letter at a known-green position (pos2 must be 'a')
        ("nrace", False),  # contains the known-absent letter 'n'
        ("urate", False),  # missing the required yellow letter 'c' entirely
        ("crace", False),  # has 'c', but at the exact position yellow ruled out
    ],
)
def test_valid_guess_cases(wordle_after_crane, candidate, expected):
    pat = wordle_after_crane.pattern(candidate, wordle_after_crane.solution)
    assert wordle_after_crane.valid_guess(candidate, pat) is expected