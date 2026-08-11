from wordle_solver import Wordle
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt
import time


# Precomputed top 10 initial guesses for 5-letter words (from the report, Figure 11).
# Shown before your very first guess, since calculating this live against the full
# 12972-word dictionary would take a long
# time. From guess 2 onward, suggestions
# are calculated live from the shrunken list of remaining possible words.
TOP_10_OPENERS_5LETTER = [
    ("tares", 6.1940), ("lares", 6.1499), ("rales", 6.1143), ("rates", 6.0962),
    ("teras", 6.0766), ("nares", 6.0668), ("soare", 6.0614), ("tales", 6.0550),
    ("reais", 6.0498), ("tears", 6.0323),
]


def print_top_entropy_words(wordle, n=10, precomputed=None):
    """
    Prints the top n words ranked by average entropy from the words still
    allowed as guesses (wordle.language). If fewer than n words remain,
    prints all of them. If `precomputed` is given, prints that list instead
    of calculating live (used for the very first guess).
    """
    if precomputed is not None:
        print("\nTop {} suggested guesses (precomputed, highest entropy first):".format(len(precomputed)))
        for word, bits in precomputed:
            print("  {:<10} {:.4f} bits".format(word, bits))
        print()
        return

    remaining = len(wordle.language)
    if remaining == 0:
        return
    if remaining == 1:
        print("\nOnly one possible word left: {}\n".format(wordle.language[0]))
        return

    print("\nCalculating suggested guesses from {} remaining words...".format(remaining))
    wordle.max_entropy_guess  # populates wordle.dict_bits, sorted highest entropy first
    top_items = list(wordle.dict_bits.items())[:n]
    print("Top {} suggested guesses (highest entropy first):".format(len(top_items)))
    for word, bits in top_items:
        print("  {:<10} {:.4f} bits".format(word, bits))
    print()


def play_wordle(alphabet, data_set_words, data_set_answers, sol, length=5, attempts=6, mode="hard"):
    """
    alphabet          - set of symbols allowed
    data_set_words    - set of valid guesses L
    data_set_answers  - set of solutions S
    sol               - the solution to be played
    length            - length of the word
    attempts          - maximum number of allowed attempts
    mode              - difficulty ("normal" or "hard")
    """
    if sol not in data_set_answers:
        print("That is not a valid solution")
        return None
    if length < 1 or attempts < 1:
        print("The length of the words and the number of maximum attempts must be Natural numbers.")
        return None

    wordle = Wordle(alphabet, data_set_words, sol, length, attempts)
    wordle.all_patterns
    print("Welcome to Wordle!")
    print('Remember that you must enter a valid {} letter word.\n'.format(length))

    first_guess = True

    while wordle.continue_playing:
        if first_guess:
            if length == 5:
                print_top_entropy_words(wordle, precomputed=TOP_10_OPENERS_5LETTER)
            else:
                print_top_entropy_words(wordle)  # no precomputed list for other word lengths
        first_guess = False

        y = input("Type your guess: ")
        if wordle.valid_word(wordle.language, y) == False:
            print('This is not a valid input.')
            print('You must enter a valid {} letter word.'.format(length))
            continue
        wordle.word_list(y)
        if wordle.you_win == True:
            print("You guessed the word!")
            return None
        wordle.pattern_print(y, sol)
        print("You've got {} attempts left. \n".format(wordle.Num_attempts - len(wordle.guesses)))
        if mode == "hard":
            wordle.classification_words
            wordle.partition
            print_top_entropy_words(wordle)
        else:
            print("(Live suggestions only update turn-to-turn in hard mode. "
                  "Switch mode to \"hard\" to see them narrow down each guess.)\n")

    if wordle.you_win == False:
        print("You failed to solve the puzzle. Good luck next time!")
    return None


def random_wordle(alphabet, data_set_words, data_set_answers, sol, length=5, attempts=6, mode="hard"):
    """
    Same as play_wordle, but guesses are chosen at random from data_set_words
    instead of being typed in by a human player.
    """
    if sol not in data_set_answers:
        print("That is not a valid solution")
        return None
    if length < 1 or attempts < 1:
        print("The length of the words and the number of maximum attempts must be Natural numbers.")
        return None

    wordle = Wordle(alphabet, data_set_words, sol, length, attempts)
    wordle.all_patterns
    print("Welcome to Wordle!")
    print('Remember that you must enter a valid {} letter word.\n'.format(length))

    while wordle.continue_playing:
        y = data_set_words[np.random.randint(len(data_set_words))]
        if wordle.valid_word(wordle.language, y) == False:
            print('This is not a valid input.')
            print('You must enter a valid {} letter word.'.format(length))
            continue
        wordle.word_list(y)
        if wordle.you_win == True:
            print("You guessed the word!")
            return None
        wordle.pattern_print(y, sol)
        print("You've got {} attempts left. \n".format(wordle.Num_attempts - len(wordle.guesses)))
        if mode == "hard":
            wordle.classification_words
            wordle.partition

    if wordle.you_win == False:
        print("You failed to solve the puzzle. Good luck next time!")
    return None


def top_10_init(alphabet, data_set_words, length=5):
    # compute the top 10 initial guesses (based on entropy) in the input set
    wordle = Wordle(alphabet, data_set_words, data_set_words[0], length)
    wordle.all_patterns
    wordle.best_opening_guess
    return None


def wordle_solver(alphabet, data_set_words, sol, openers, length=5, attempts=20, plot="Yes"):
    """
    Run the entropy-based algorithm in hard mode.

    alphabet         - set of symbols allowed
    data_set_words   - set of valid guesses L
    sol              - set of games (solutions) to be played
    openers          - list of words to use as initial guesses / score
    length           - length of the word
    attempts         - maximum number of allowed attempts
    plot             - "Yes"/"No", whether to generate score histograms
    """
    if length < 1 or attempts < 1:
        print("The length of the words and the number of maximum attempts must be Natural numbers.")
        return None

    scores = np.zeros(len(openers))
    wordle = Wordle(alphabet, data_set_words, data_set_words[0], length, attempts)
    wordle.all_patterns

    for opener in openers:
        print(opener)
        wins = 0
        Total_attempts = 0
        best_initial_guess = opener
        list_number_attempts = []
        start = time.time()

        for solution in tqdm(sol):
            attempt = 1
            Total_attempts += 1
            wordle.new_game(solution, data_set_words)
            while wordle.continue_playing:
                wordle.bits_uncertainty
                if len(wordle.language) == len(data_set_words):
                    y = best_initial_guess
                wordle.word_list(y)
                if wordle.you_win == True:
                    if attempt <= 6:
                        wins += 1
                    break
                wordle.pattern(y, solution)
                wordle.classification_words
                wordle.partition
                Total_attempts += 1
                attempt += 1
                y = wordle.max_entropy_guess
            list_number_attempts.append(attempt)

        end = time.time()
        print("\nThe algorithm needed {} seconds to play all games in the list sol.".format(end - start))
        average = wins * 100 / len(sol)
        print("The algorithm won {} games out of {} ({:.5}%).".format(wins, len(sol), average))
        average_guesses = Total_attempts / len(sol)
        scores[openers.index(opener)] = average_guesses

        attemps_eachtype = []
        for i in range(1, 11):
            attemps_eachtype.append(list_number_attempts.count(i))
        print(attemps_eachtype)
        print("The average number of guesses is {:.5}.".format(average_guesses))

        if plot == "Yes":
            x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            y_vals = attemps_eachtype
            plt.bar(x, y_vals, align='center')
            plt.title('Starter: {}. Score = {:.4}'.format(best_initial_guess, average_guesses))
            plt.xlabel('Number of attempts')
            plt.ylabel('Frequency')
            plt.show()

    print(scores)
    return None


def plot_scores(openers, scores):
    # plot words in `openers` (ranked by entropy) against their average scores
    x = [i for i in range(1, len(openers) + 1)]
    plt.stem(x, scores)
    plt.ylim((min(scores) - 0.15, max(scores) + 0.025))
    plt.xlabel('Ranked words based on entropy')
    plt.ylabel('Average score over all possible games')
    plt.show()
    return None


def main():
    # Load the set of valid guesses, the set of solutions and the alphabet.
    # These three files must be in the SAME FOLDER as this script.
    data_set_words = np.genfromtxt('valid-wordle-words.txt', delimiter='\n', dtype=str)
    data_set_answers = np.genfromtxt('wordle-nyt-answers-alphabetical.txt', delimiter='\n', dtype=str)
    alphabet = np.genfromtxt('english_alphabet.txt', delimiter='\n', dtype=str)

    # ------------------------------------------------------------------
    # DEFAULT: play a game yourself, HARD mode, random daily solution.
    # Hard mode is required for the entropy suggestions to update each turn.
    # ------------------------------------------------------------------
    sol = np.random.choice(data_set_answers)
    play_wordle(alphabet, data_set_words, data_set_answers, sol, 5, 6, 'hard')

    # --- Other things you can try instead (comment the block above, uncomment one below) ---

    # Play a specific word, e.g. "zebra":
    # sol = "zebra"
    # play_wordle(alphabet, data_set_words, data_set_answers, sol, 5, 6, 'hard')

    # Watch the entropy-based solver play a single game against you (no typing needed):
    # openers = ["tales"]
    # sol = ["zebra"]
    # wordle_solver(alphabet, data_set_words, sol, openers, length=5, attempts=20, plot="No")

    # See the computer's top 10 best opening guesses:
    # top_10_init(alphabet, data_set_words, 5)


if __name__ == "__main__":
    main()
