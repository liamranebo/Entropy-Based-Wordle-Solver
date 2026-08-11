"""Unit tests for the simple state properties: you_win, continue_playing,
remaining_attempts, bits_uncertainty."""

import math


def test_you_win_false_before_any_guess(make_wordle):
    wordle = make_wordle(["crane"], solution="crane", with_patterns=False)
    assert wordle.you_win is False


def test_you_win_true_after_correct_guess(make_wordle):
    wordle = make_wordle(["crane"], solution="crane", with_patterns=False)
    wordle.word_list("crane")
    assert wordle.you_win is True


def test_you_win_false_after_incorrect_guess(make_wordle):
    wordle = make_wordle(["crane", "trace"], solution="trace", with_patterns=False)
    wordle.word_list("crane")
    assert wordle.you_win is False


def test_remaining_attempts(make_wordle):
    wordle = make_wordle(["aaaaa"], solution="aaaaa", num_attempts=6, with_patterns=False)
    for _ in range(5):
        wordle.word_list("bbbbb")
    assert wordle.remaining_attempts is True  # 6 - 5 = 1 > 0

    wordle.word_list("bbbbb")
    assert wordle.remaining_attempts is False  # 6 - 6 = 0, not > 0


def test_continue_playing_true_with_attempts_left_and_no_win(make_wordle):
    wordle = make_wordle(["aaaaa", "bbbbb"], solution="aaaaa", num_attempts=6, with_patterns=False)
    wordle.word_list("bbbbb")
    assert wordle.continue_playing is True


def test_continue_playing_false_when_attempts_exhausted(make_wordle):
    wordle = make_wordle(["bbbbb"], solution="aaaaa", num_attempts=2, with_patterns=False)
    wordle.word_list("bbbbb")
    wordle.word_list("bbbbb")
    assert wordle.continue_playing is False


def test_continue_playing_false_once_won_even_with_attempts_left(make_wordle):
    wordle = make_wordle(["aaaaa"], solution="aaaaa", num_attempts=6, with_patterns=False)
    wordle.word_list("aaaaa")
    assert wordle.continue_playing is False


def test_bits_uncertainty_matches_log2_of_remaining_language(make_wordle):
    words = ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8"]
    wordle = make_wordle(words, solution="w1", length=2, with_patterns=False)
    assert wordle.bits_uncertainty == math.log2(8) == 3.0


def test_bits_uncertainty_is_recomputed_live(make_wordle):
    words = ["w1"]
    wordle = make_wordle(words, solution="w1", length=2, with_patterns=False)
    assert wordle.bits_uncertainty == 0.0

    wordle.language = ["w1", "w2", "w3", "w4"]
    assert wordle.bits_uncertainty == math.log2(4) == 2.0