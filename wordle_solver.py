import numpy as np
from math import log2
from tqdm import tqdm
import random
import itertools


class Wordle:
    Num_attempts = 20

    def __init__(self, alphabet, data_set_words, solution, length=5, Num_attempts=20):
        self.Num_attempts = Num_attempts
        self.length_word = length              # length of the word
        self.alphabet = alphabet                # considered alphabet
        self.solution = solution                # solution of the game
        self.guesses = []                       # list of guesses
        self.sol_letters = list(self.solution)  # letters of the solution
        self.pat_current_guess = []             # pattern of the last guess
        self.language = list(data_set_words)    # set of possible guesses
        self.class_pattern = []                 # sublists of indices per pattern
        pass

    def new_game(self, solution, data_set_words):
        # resets some attributes in order to play a new game
        self.solution = solution
        self.sol_letters = list(solution)
        self.language = data_set_words
        self.guesses = []
        self.pat_current_guess = []
        self.class_pattern = []
        return None

    def word_list(self, word):
        # add the last guess to the list of attempts
        return self.guesses.append(word)

    def valid_word(self, data_set_words, word):
        # checks whether the word is a valid input
        return word in data_set_words

    def countelements(self, word):
        # dictionary containing as keys the different elements in word and
        # as values how many times each one appears
        letters = list(word)
        dicts = {}
        keys = []
        values = []
        for i in range(len(word)):
            if letters[i] not in keys:
                keys.append(letters[i])
                number = letters.count(letters[i])
                values.append(number)
        keys = tuple(keys)
        for i in range(len(keys)):
            dicts[keys[i]] = values[i]
        return dicts

    def pattern(self, word, solution):
        # compare the guess with the solution and outputs the corresponding pattern
        new_list_letters = list(solution)
        index = []  # stores the indices of the letters that are not in the right position
        let_word = list(word)
        pattern = let_word.copy()
        for i in range(self.length_word):
            if let_word[i] == new_list_letters[i]:
                new_list_letters[i] = int(1)
                pattern[i] = 1
            else:
                index.append(i)
        for i in index:
            if let_word[i] in new_list_letters:
                ind = new_list_letters.index(let_word[i])
                pattern[i] = 2
                new_list_letters[ind] = 2
        for i in range(len(pattern)):
            if pattern[i] != 1 and pattern[i] != 2:
                pattern[i] = 0
        pattern = tuple(pattern)
        if self.guesses != [] and word == self.guesses[len(self.guesses) - 1]:
            self.pat_current_guess = pattern
        return pattern

    def pattern_print(self, word, solution):
        # same as pattern(), but also prints the information obtained
        new_list_letters = list(solution)
        info = [1] * self.length_word
        index = []
        let_word = list(word)
        pattern = let_word.copy()
        for i in range(self.length_word):
            if let_word[i] == new_list_letters[i]:
                new_list_letters[i] = int(1)
                letter_i = ("{} is in the right position".format(let_word[i]))
                info[i] = letter_i
                pattern[i] = 1
            else:
                index.append(i)
        for i in index:
            if let_word[i] in new_list_letters:
                letter_i = ("{} is in the solution but not in the right position".format(let_word[i]))
                ind = new_list_letters.index(let_word[i])
                pattern[i] = 2
                new_list_letters[ind] = 2
                info[i] = letter_i
            else:
                letter_i = ("{} is not in the solution".format(let_word[i]))
                info[i] = letter_i
        for i in range(len(pattern)):
            if pattern[i] != 1 and pattern[i] != 2:
                pattern[i] = 0
        pattern = tuple(pattern)
        if self.guesses != [] and word == self.guesses[len(self.guesses) - 1]:
            self.pat_current_guess = pattern
        print("\n".join(info))
        print("The obtained pattern is {}.".format(pattern))
        return pattern

    def indices(self, el, List):
        indices = []
        for t in range(len(List)):
            if List[t] == el:
                indices.append(t)
        return indices

    def valid_guess(self, word, pat):
        # returns True if the pattern of word is compatible with the information from the last guess
        current_guess = list(self.guesses[len(self.guesses) - 1])
        indices_green_word = [i for i, x in enumerate(pat) if x == 1]
        indices_guess_pat = [i for i, x in enumerate(self.pat_current_guess) if x == 1]
        word_list = list(word)

        if not all(item in indices_green_word for item in indices_guess_pat) == True:
            return False

        indices_green_guess = [i for i, x in enumerate(self.pat_current_guess)
                                if x == 1 and current_guess[i] == word[i]]
        for i in indices_green_guess:
            word_list[i] = 3

        indices_yellow_guess = [i for i, x in enumerate(self.pat_current_guess) if x == 2]
        for i in indices_yellow_guess:
            if current_guess[i] not in word_list or i in self.indices(current_guess[i], word_list):
                return False
            word_list[self.indices(current_guess[i], word_list)[-1]] = 3

        indices_grey_guess = [i for i, x in enumerate(self.pat_current_guess) if x == 0]
        for i in indices_grey_guess:
            if current_guess[i] in word_list:
                return False

        return True

    @property
    def partition(self):
        # compares the pattern of the current guess with the pattern of the words
        # in the language and reduces the space of possibilities
        words = list(self.dict_word_pattern.keys())
        patterns = list(self.dict_word_pattern.values())
        self.language = []
        for i in range(len(words)):
            if words[i] == self.guesses[len(self.guesses) - 1]:  # delete the word if it is the last guess
                continue
            if self.valid_guess(words[i], patterns[i]) == True:
                self.language.append(words[i])
        return None

    @property
    def all_patterns(self):
        # creates a list containing all the possible patterns for a word of a given length
        self.list_patterns = list(itertools.product(range(3), repeat=self.length_word))

    @property
    def classification_words(self):
        # creates a dictionary containing words with their respective pattern (wrt self.solution)
        self.class_pattern = [[] for _ in range(len(self.list_patterns))]
        self.dict_word_pattern = {}
        keys = self.language
        values = []
        for i in self.language:
            values.append(self.pattern(i, self.solution))
        values = tuple(values)
        for i in range(len(keys)):
            self.dict_word_pattern[keys[i]] = values[i]
        return None

    @property
    def max_entropy_guess(self):
        # returns the word from self.language with the highest average entropy
        self.dict_bits = {}
        keys_1 = tuple(self.language.copy())
        value_bits = []
        for word in self.language:
            dict_pattern_number = {}
            keys_2 = self.list_patterns.copy()
            for i in range(len(keys_2)):
                dict_pattern_number[keys_2[i]] = 0
            for r in self.language:
                pat = self.pattern(word, r)
                ind = keys_2.index(pat)
                dict_pattern_number[keys_2[ind]] += 1
            word_prob_dit = [p / len(self.language) for p in dict_pattern_number.values()]
            bits = self.entropy(word_prob_dit)
            value_bits.append(bits)
        for i in range(len(keys_1)):
            self.dict_bits[keys_1[i]] = value_bits[i]
        self.dict_bits = dict(sorted(self.dict_bits.items(), key=lambda item: item[1], reverse=True))
        return next(iter(self.dict_bits))

    def entropy(self, rv, Threshold=1e-15):
        return -sum([p * log2(p + Threshold) for p in rv])

    @property
    def best_opening_guess(self):
        # return the best opening guess and print the top 10 initial guesses (naive method)
        y = self.max_entropy_guess
        top_10 = {}
        keys = tuple(self.dict_bits.keys())
        values = list(self.dict_bits.values())
        for i in range(0, 10):
            top_10[keys[i]] = values[i]
        print("The best oppenning guess is {} with {:.6} bits of uncertainty.".format(y, self.dict_bits[y]))
        print("The top 10 best initial guesses based on entropy is:")
        print(top_10)
        return y

    @property  # so it can be called as a variable, not a function
    def you_win(self):
        # checks whether our last guess was correct
        return len(self.guesses) > 0 and self.guesses[-1] == self.solution

    @property
    def remaining_attempts(self):
        return self.Num_attempts - len(self.guesses) > 0

    @property
    def bits_uncertainty(self):
        # bits of uncertainty in the set of remaining possible guesses
        self.bits_un = log2(len(self.language))
        return self.bits_un

    @property
    def continue_playing(self):
        return self.remaining_attempts > 0 and not self.you_win

    def information_event(p):
        # amount of information of an event with probability p
        return -log2(p)
