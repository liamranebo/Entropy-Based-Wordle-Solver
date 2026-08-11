"""Unit tests for Wordle.pattern()."""

GREEN, YELLOW, GREY = 1, 2, 0


def test_pattern_all_green_on_exact_match(make_wordle):
    wordle = make_wordle(["crane"], solution="crane", with_patterns=False)
    assert wordle.pattern("crane", "crane") == (GREEN,) * 5


def test_pattern_all_grey_on_disjoint_letters(make_wordle):
    # "briny" and "clamp" share no letters at all.
    wordle = make_wordle(["briny"], solution="clamp", with_patterns=False)
    assert wordle.pattern("briny", "clamp") == (GREY,) * 5


def test_pattern_mixed_green_yellow_grey(make_wordle):
    # crane vs trace: c(yellow) r(green) a(green) n(grey) e(green)
    wordle = make_wordle(["crane"], solution="trace", with_patterns=False)
    assert wordle.pattern("crane", "trace") == (YELLOW, GREEN, GREEN, GREY, GREEN)


def test_pattern_repeated_letters_sassy_vs_abyss(make_wordle):
    # Real Wordle behaviour for guessing SASSY against solution ABYSS:
    # - S(pos0): solution has 2 S's; the one at pos3 is consumed by the
    #   guess's own green S at pos3 first, leaving 1 S for pos0 -> yellow.
    # - A(pos1): A is in the solution (pos0) but not at pos1 -> yellow.
    # - S(pos2): both solution S's already consumed by pos3(green)/pos0(yellow) -> grey.
    # - S(pos3): matches solution's S at pos3 -> green.
    # - Y(pos4): Y is in the solution (pos2) but not at pos4 -> yellow.
    wordle = make_wordle(["sassy"], solution="abyss", with_patterns=False)
    assert wordle.pattern("sassy", "abyss") == (YELLOW, YELLOW, GREY, GREEN, YELLOW)


def test_pattern_repeated_letter_in_guess_only_one_present_in_solution(make_wordle):
    # guess has three E's, solution has only two E's -> only two can be marked.
    wordle = make_wordle(["eerie"], solution="crepe", with_patterns=False)
    pattern = wordle.pattern("eerie", "crepe")
    # crepe = c,r,e,p,e ; eerie = e,e,r,i,e
    # pos0 e vs c: mismatch -> index=[0]
    # pos1 e vs r: mismatch -> index=[0,1]
    # pos2 r vs e: mismatch -> index=[0,1,2]
    # pos3 i vs p: mismatch -> index=[0,1,2,3]
    # pos4 e vs e: green, remaining=[c,r,e,p,1]
    # i=0: 'e' in remaining -> yellow, consume idx2 -> [c,r,2,p,1]
    # i=1: 'e' in remaining? no e left -> grey
    # i=2: 'r' in remaining -> yellow, consume idx1 -> [c,2,2,p,1]
    # i=3: 'i' in remaining? no -> grey
    assert pattern == (YELLOW, GREY, YELLOW, GREY, GREEN)


def test_pattern_sets_pat_current_guess_only_for_last_guess(make_wordle):
    wordle = make_wordle(["crane"], solution="trace", with_patterns=False)
    wordle.word_list("crane")
    result = wordle.pattern("crane", "trace")
    assert wordle.pat_current_guess == result

    # A word that is NOT the last guess should not update pat_current_guess.
    wordle.pattern("trace", "trace")
    assert wordle.pat_current_guess == result