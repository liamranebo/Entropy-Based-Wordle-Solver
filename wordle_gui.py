"""
Tkinter GUI for the Wordle solver.

Reuses the Wordle class from wordle_solver.py
for all game/entropy logic. Picks a random solution from the answers list
(same as run_wordle.py's default) and lets you play against it in hard mode,
with a live "Suggested guesses" panel ranked by entropy.
"""

import tkinter as tk
from tkinter import messagebox

import numpy as np

from wordle_solver import Wordle

WORD_LENGTH = 5
NUM_ATTEMPTS = 6

GREEN = "#6aaa64"
YELLOW = "#c9b458"
GREY = "#787c7e"
EMPTY_BG = "#ffffff"
EMPTY_BORDER = "#d3d6da"
TYPED_BORDER = "#878a8c"
TEXT_LIGHT = "#ffffff"
TEXT_DARK = "#1a1a1b"

BG_COLOR = "#e8e8ea"
SIDE_BG = "#f1f1f3"
NOTE_FG = "#5a5c5e"

SUBMIT_BG = "#6aaa64"
SUBMIT_HOVER = "#599354"
NEW_GAME_BG = "#878a8c"
NEW_GAME_HOVER = "#717477"

SIDE_BORDER = "#dcdcdf"
NUM_SUGGESTIONS = 10

BAR_WIDTH = 64
BAR_HEIGHT = 10
BAR_TRACK = "#e2e2e5"
BAR_FILL = "#6aaa64"
BAR_MIN_FRAC = 0.06  # smallest stretched bar still shows a visible sliver
BAR_STRETCH = 0.25   # how much of the full min-max exaggeration to apply


def rank_suggestions(items, min_frac=BAR_MIN_FRAC, stretch=BAR_STRETCH):
    """Rank (word, bits) pairs for the suggestions panel, returning
    (word, bits, bar_fraction) tuples where bar_fraction in [0, 1] is how
    wide that word's entropy bar should render.

    bar_fraction blends between raw bits/max_bits (stretch=0) and fully
    min-max normalized against the displayed range (stretch=1), since the
    top 10 entropy values are often clustered close together (e.g.
    6.0-6.2) and pure absolute scaling would render them all near-full.
    No Tkinter dependency, so this is unit-testable without a display.
    """
    bits_values = [bits for _, bits in items]
    max_bits = max(bits_values) if bits_values else 0
    min_bits = min(bits_values) if bits_values else 0
    spread = max_bits - min_bits

    ranked = []
    for word, bits in items:
        absolute_frac = bits / max_bits if max_bits > 0 else 0.0
        if spread > 0:
            stretched_frac = min_frac + (1 - min_frac) * (bits - min_bits) / spread
        else:
            stretched_frac = 1.0
        frac = (1 - stretch) * absolute_frac + stretch * stretched_frac
        ranked.append((word, bits, frac))
    return ranked


class RoundedButton(tk.Canvas):
    """A flat, rounded-corner button (tk.Button can't do rounded corners)."""

    def __init__(self, parent, text, command, bg, hover_bg, fg="white",
                 width=150, height=42, radius=16, font=("Helvetica", 12, "bold")):
        super().__init__(parent, width=width, height=height, highlightthickness=0,
                          bg=parent.cget("bg"), takefocus=0, cursor="hand2")
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg
        self.shape = self._round_rect(1, 1, width - 1, height - 1, radius, fill=bg, outline=bg)
        self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, _event):
        if self.command:
            self.command()

    def _on_enter(self, _event):
        self.itemconfig(self.shape, fill=self.hover_color, outline=self.hover_color)

    def _on_leave(self, _event):
        self.itemconfig(self.shape, fill=self.bg_color, outline=self.bg_color)

# Precomputed top 10 initial guesses for 5-letter words (from the report, Figure 11).
# Shown before the very first guess instead of calculating live against the
# full ~13000-word dictionary.
TOP_10_OPENERS_5LETTER = [
    ("tares", 6.1940), ("lares", 6.1499), ("rales", 6.1143), ("rates", 6.0962),
    ("teras", 6.0766), ("nares", 6.0668), ("soare", 6.0614), ("tales", 6.0550),
    ("reais", 6.0498), ("tears", 6.0323),
]


class WordleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Solver")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.data_set_words = np.genfromtxt('valid-wordle-words.txt', delimiter='\n', dtype=str)
        self.data_set_answers = np.genfromtxt('wordle-nyt-answers-alphabetical.txt', delimiter='\n', dtype=str)
        self.alphabet = np.genfromtxt('english_alphabet.txt', delimiter='\n', dtype=str)

        self.mode = "hard"
        self.game_over = False
        self.current_row = 0
        self.wordle = None

        self._build_layout()
        self._new_game()

    def _build_layout(self):
        left_frame = tk.Frame(self.root, bg=BG_COLOR)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        note = tk.Label(
            left_frame, text="Hard Mode — every guess must use all clues revealed so far.",
            font=("Helvetica", 10, "italic"), bg=BG_COLOR, fg=NOTE_FG,
        )
        note.grid(row=0, column=0, pady=(0, 12))

        self.board_frame = tk.Frame(left_frame, bg=BG_COLOR)
        self.board_frame.grid(row=1, column=0)

        self.tiles = []
        for r in range(NUM_ATTEMPTS):
            row_tiles = []
            for c in range(WORD_LENGTH):
                lbl = tk.Label(
                    self.board_frame, text="", width=2, height=1,
                    font=("Helvetica", 24, "bold"), bg=EMPTY_BG, fg=TEXT_DARK,
                    relief="solid", bd=1,
                    highlightbackground=EMPTY_BORDER, highlightcolor=EMPTY_BORDER,
                    highlightthickness=2,
                )
                lbl.grid(row=r, column=c, padx=4, pady=4, ipadx=12, ipady=8)
                row_tiles.append(lbl)
            self.tiles.append(row_tiles)

        gap = 20

        button_frame = tk.Frame(left_frame, bg=BG_COLOR)
        button_frame.grid(row=2, column=0, pady=(gap, 0))

        self.submit_btn = RoundedButton(button_frame, "Submit", self._try_submit_guess,
                                         bg=SUBMIT_BG, hover_bg=SUBMIT_HOVER, width=140, height=42)
        self.submit_btn.grid(row=0, column=0)

        self.status_var = tk.StringVar(value="")

        self.new_game_btn = RoundedButton(left_frame, "New Game", self._new_game,
                                           bg=NEW_GAME_BG, hover_bg=NEW_GAME_HOVER, width=140, height=38)
        self.new_game_btn.grid(row=3, column=0, pady=(gap, 0))

        self.root.bind("<Key>", self._on_key)

        side_frame = tk.Frame(self.root, bg=SIDE_BG, bd=0, relief="flat",
                               highlightthickness=1, highlightbackground=SIDE_BORDER)
        side_frame.grid(row=0, column=1, sticky="n", padx=(0, 20), pady=20)

        title = tk.Label(side_frame, text="Suggested guesses", font=("Helvetica", 13, "bold"),
                          bg=SIDE_BG)
        title.pack(padx=18, pady=(15, 10))

        self.suggestions_frame = tk.Frame(side_frame, bg=SIDE_BG)
        self.suggestions_frame.pack(padx=18, pady=(0, 15))

        self.suggestion_rows = []
        for _ in range(NUM_SUGGESTIONS):
            row = tk.Frame(self.suggestions_frame, bg=SIDE_BG)
            row.pack(fill="x", pady=3)
            word_lbl = tk.Label(row, text="", font=("Helvetica", 12, "bold"), bg=SIDE_BG,
                                 width=7, anchor="w")
            word_lbl.pack(side="left", padx=(2, 8), pady=4)

            bar_canvas = tk.Canvas(row, width=BAR_WIDTH, height=BAR_HEIGHT,
                                    bg=SIDE_BG, highlightthickness=0)
            bar_canvas.pack(side="left", pady=4)
            bar_canvas.create_rectangle(0, 0, BAR_WIDTH, BAR_HEIGHT, fill=BAR_TRACK, outline=BAR_TRACK)
            bar_fill = bar_canvas.create_rectangle(0, 0, 0, BAR_HEIGHT, fill=BAR_FILL, outline=BAR_FILL)

            bits_lbl = tk.Label(row, text="", font=("Helvetica", 11), bg=SIDE_BG, fg="#565758")
            bits_lbl.pack(side="left", padx=(8, 0), pady=4)
            self.suggestion_rows.append((row, word_lbl, bar_canvas, bar_fill, bits_lbl))

        # The right-hand suggestions panel is shorter than the board/buttons
        # column, leaving clear space below it — put the error message there
        # instead of near the buttons, where it would sit behind them.
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bg=BG_COLOR,
                                      font=("Helvetica", 11, "bold"), fg="#b3261e",
                                      wraplength=220, justify="center")
        self.status_label.place(in_=side_frame, relx=0.5, rely=1.0, y=16, anchor="n")

    def _new_game(self):
        self.game_over = False
        self.current_row = 0
        self.current_col = 0
        self.status_var.set("")

        sol = np.random.choice(self.data_set_answers)
        self.wordle = Wordle(self.alphabet, list(self.data_set_words), sol, WORD_LENGTH, NUM_ATTEMPTS)
        self.wordle.all_patterns

        for row_tiles in self.tiles:
            for lbl in row_tiles:
                lbl.config(text="", bg=EMPTY_BG, fg=TEXT_DARK, highlightbackground=EMPTY_BORDER)

        self._show_opening_suggestions()
        self.root.focus_set()

    def _show_opening_suggestions(self):
        self._fill_suggestion_labels(TOP_10_OPENERS_5LETTER)

    def _update_suggestions(self):
        remaining = len(self.wordle.language)
        if remaining == 0:
            self._fill_suggestion_labels([])
            return
        if remaining == 1:
            only_word = self.wordle.language[0]
            self.wordle.dict_bits = {only_word: 0.0}
        else:
            self.wordle.max_entropy_guess  # populates self.wordle.dict_bits, sorted desc
        top_items = list(self.wordle.dict_bits.items())[:10]
        self._fill_suggestion_labels(top_items)

    def _fill_suggestion_labels(self, items):
        ranked = rank_suggestions(items)
        for i, (row, word_lbl, bar_canvas, bar_fill, bits_lbl) in enumerate(self.suggestion_rows):
            if i < len(ranked):
                word, bits, frac = ranked[i]
                fill_width = BAR_WIDTH * frac
                word_lbl.config(text=word.upper())
                bar_canvas.coords(bar_fill, 0, 0, fill_width, BAR_HEIGHT)
                bits_lbl.config(text="{:.4f} bits".format(bits))
            else:
                word_lbl.config(text="")
                bar_canvas.coords(bar_fill, 0, 0, 0, BAR_HEIGHT)
                bits_lbl.config(text="")

    def _on_key(self, event):
        if self.game_over or self.wordle is None:
            return
        if event.keysym == "BackSpace":
            self._backspace()
        elif event.keysym == "Return":
            self._try_submit_guess()
        elif len(event.char) == 1 and event.char.isalpha():
            self._type_letter(event.char)

    def _type_letter(self, char):
        if self.current_col >= WORD_LENGTH:
            return
        lbl = self.tiles[self.current_row][self.current_col]
        lbl.config(text=char.upper(), highlightbackground=TYPED_BORDER)
        self.current_col += 1
        self.status_var.set("")

    def _backspace(self):
        if self.current_col == 0:
            return
        self.current_col -= 1
        lbl = self.tiles[self.current_row][self.current_col]
        lbl.config(text="", highlightbackground=EMPTY_BORDER)
        self.status_var.set("")

    def _try_submit_guess(self):
        if self.game_over or self.wordle is None:
            return

        if self.current_col != WORD_LENGTH:
            self.status_var.set("Guess must be {} letters.".format(WORD_LENGTH))
            return

        guess = "".join(
            self.tiles[self.current_row][c].cget("text") for c in range(WORD_LENGTH)
        ).lower()
        self.status_var.set("")

        if not self.wordle.valid_word(self.wordle.language, guess):
            self.status_var.set("'{}' is not a valid guess.".format(guess.upper()))
            return

        self.wordle.word_list(guess)
        pattern = self.wordle.pattern(guess, self.wordle.solution)
        self._color_row(self.current_row, guess, pattern)

        if self.wordle.you_win:
            self.game_over = True
            messagebox.showinfo("Wordle Solver",
                                 "You guessed it! The word was {}.".format(self.wordle.solution.upper()))
            return

        self.current_row += 1
        self.current_col = 0

        if not self.wordle.remaining_attempts:
            self.game_over = True
            messagebox.showinfo("Wordle Solver",
                                 "Out of attempts! The word was {}.".format(self.wordle.solution.upper()))
            return

        if self.mode == "hard":
            self.wordle.classification_words
            self.wordle.partition

        self._update_suggestions()

    def _color_row(self, row, guess, pattern):
        colors = {1: GREEN, 2: YELLOW, 0: GREY}
        for c in range(WORD_LENGTH):
            lbl = self.tiles[row][c]
            lbl.config(text=guess[c].upper(), bg=colors[pattern[c]], fg=TEXT_LIGHT)


def main():

    root = tk.Tk()
    WordleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()