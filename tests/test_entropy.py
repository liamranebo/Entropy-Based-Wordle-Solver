"""Unit test for Wordle.max_entropy_guess, verified by hand.

Language: ["abc", "bac", "xyz"], length 3.

Guessing "abc" (or "bac") against each of the 3 words produces 3 distinct
patterns (one per word) -> a perfect 3-way split -> entropy = log2(3).

Guessing "xyz" against each of the 3 words collides "abc" and "bac" onto
the same all-grey pattern (xyz shares no letters with either), while only
"xyz" itself is all-green -> distribution {2/3, 1/3} ->
entropy = -(2/3*log2(2/3) + 1/3*log2(1/3)), which is strictly less than
log2(3).
"""

import math

import pytest


@pytest.fixture
def small_language_wordle(make_wordle):
    return make_wordle(["abc", "bac", "xyz"], solution="abc", length=3)


def test_max_entropy_guess_picks_the_best_split(small_language_wordle):
    best = small_language_wordle.max_entropy_guess
    assert best in ("abc", "bac")


def test_max_entropy_guess_bits_match_hand_calculation(small_language_wordle):
    small_language_wordle.max_entropy_guess  # populates dict_bits

    expected_best_bits = math.log2(3)
    expected_xyz_bits = -((2 / 3) * math.log2(2 / 3) + (1 / 3) * math.log2(1 / 3))

    assert small_language_wordle.dict_bits["abc"] == pytest.approx(expected_best_bits)
    assert small_language_wordle.dict_bits["bac"] == pytest.approx(expected_best_bits)
    assert small_language_wordle.dict_bits["xyz"] == pytest.approx(expected_xyz_bits)
    assert small_language_wordle.dict_bits["xyz"] < small_language_wordle.dict_bits["abc"]