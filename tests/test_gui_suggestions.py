"""Tests for wordle_gui's non-UI logic: rank_suggestions() and the
TOP_10_OPENERS_5LETTER constant. No Tk widgets/window are created here.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wordle_gui import TOP_10_OPENERS_5LETTER, rank_suggestions


def test_rank_suggestions_empty_list_returns_empty():
    assert rank_suggestions([]) == []


def test_rank_suggestions_single_item_gets_full_bar():
    ranked = rank_suggestions([("tares", 6.19)])
    assert ranked == [("tares", 6.19, 1.0)]


def test_rank_suggestions_all_equal_bits_get_full_bars():
    items = [("aaaaa", 5.0), ("bbbbb", 5.0), ("ccccc", 5.0)]
    ranked = rank_suggestions(items)
    assert all(frac == pytest.approx(1.0) for _, _, frac in ranked)


def test_rank_suggestions_best_word_always_gets_full_bar():
    items = [("tares", 6.19), ("lares", 6.15), ("rales", 6.11)]
    ranked = rank_suggestions(items)
    assert ranked[0][0] == "tares"
    assert ranked[0][2] == pytest.approx(1.0)


def test_rank_suggestions_fractions_are_monotonically_decreasing():
    items = [("tares", 6.19), ("lares", 6.15), ("rales", 6.11), ("rates", 6.00)]
    ranked = rank_suggestions(items)
    fracs = [frac for _, _, frac in ranked]
    assert fracs == sorted(fracs, reverse=True)
    assert len(set(fracs)) == len(fracs)  # distinct bits -> distinct fractions


def test_rank_suggestions_matches_blended_formula_by_hand():
    # Two words, clustered bits, default min_frac=0.06 / stretch=0.25.
    items = [("best", 6.0), ("worst", 5.0)]
    ranked = rank_suggestions(items, min_frac=0.06, stretch=0.25)

    # best: absolute=6/6=1.0, stretched=1.0 (it's the max) -> blended=1.0
    assert ranked[0] == ("best", 6.0, pytest.approx(1.0))

    # worst: absolute=5/6, stretched=min_frac=0.06 (it's the min)
    absolute = 5 / 6
    stretched = 0.06
    expected = (1 - 0.25) * absolute + 0.25 * stretched
    assert ranked[1] == ("worst", 5.0, pytest.approx(expected))


def test_rank_suggestions_stretch_zero_is_pure_absolute_scaling():
    items = [("best", 8.0), ("worst", 4.0)]
    ranked = rank_suggestions(items, stretch=0.0)
    assert ranked[0][2] == pytest.approx(8 / 8)
    assert ranked[1][2] == pytest.approx(4 / 8)


def test_rank_suggestions_stretch_one_is_full_min_max_normalization():
    items = [("best", 8.0), ("mid", 6.0), ("worst", 4.0)]
    ranked = rank_suggestions(items, min_frac=0.1, stretch=1.0)
    assert ranked[0][2] == pytest.approx(1.0)
    assert ranked[2][2] == pytest.approx(0.1)
    # mid is halfway between min and max bits -> halfway between 0.1 and 1.0
    assert ranked[1][2] == pytest.approx(0.1 + 0.9 * 0.5)


def test_top_10_openers_has_ten_words_sorted_by_descending_entropy():
    assert len(TOP_10_OPENERS_5LETTER) == 10
    words = [word for word, _ in TOP_10_OPENERS_5LETTER]
    assert len(set(words)) == 10  # no duplicates
    assert all(len(word) == 5 for word in words)

    bits = [b for _, b in TOP_10_OPENERS_5LETTER]
    assert bits == sorted(bits, reverse=True)
