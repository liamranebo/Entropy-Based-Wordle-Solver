"""Integration tests for run_wordle.play_wordle: the CLI game loop wired
up against the real Wordle class, driven with scripted guesses instead of
live input()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from run_wordle import play_wordle

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


def test_play_wordle_reaches_win_with_correct_final_guess(monkeypatch, capsys):
    data_set_words = ["trace", "crane", "grace"]
    data_set_answers = ["trace"]
    guesses = iter(["trace"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(guesses))

    play_wordle(ALPHABET, data_set_words, data_set_answers, "trace",
                length=5, attempts=6, mode="hard")

    captured = capsys.readouterr()
    assert "You guessed the word!" in captured.out


def test_play_wordle_hard_mode_blocks_guess_that_ignores_known_information(monkeypatch, capsys):
    # Same "crane" -> "trace" scenario verified by hand in test_valid_guess.py
    # and test_partition.py: after guessing "crane", only "trace"/"grace"
    # remain possible, so "trice" (which ignores the revealed clues) must
    # be rejected by hard mode before the corrective "trace" guess wins.
    data_set_words = ["crane", "trace", "grace", "trice", "nrace", "urate", "crace"]
    data_set_answers = ["trace"]
    guesses = iter(["crane", "trice", "trace"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(guesses))

    play_wordle(ALPHABET, data_set_words, data_set_answers, "trace",
                length=5, attempts=6, mode="hard")

    captured = capsys.readouterr()
    assert "This is not a valid input." in captured.out
    assert "You guessed the word!" in captured.out