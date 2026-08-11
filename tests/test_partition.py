"""Unit tests for the Wordle.partition property.

Reuses the same "crane" -> "trace" scenario verified by hand in
test_valid_guess.py: only "trace" and "grace" should survive.
"""


def test_partition_narrows_language_to_consistent_words(make_wordle):
    words = ["crane", "trace", "grace", "trice", "nrace", "urate", "crace"]
    wordle = make_wordle(words, solution="trace", length=5)

    wordle.word_list("crane")
    wordle.pattern("crane", "trace")  # sets pat_current_guess

    wordle.classification_words
    wordle.partition

    assert wordle.language == ["trace", "grace"]


def test_partition_excludes_the_word_just_guessed(make_wordle):
    words = ["trace", "crane"]
    wordle = make_wordle(words, solution="trace", length=5)

    wordle.word_list("crane")
    wordle.pattern("crane", "trace")

    wordle.classification_words
    wordle.partition

    assert "crane" not in wordle.language