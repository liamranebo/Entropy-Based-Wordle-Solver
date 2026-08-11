# Wordle Solver

A Wordle solver and player built around an information-theory (entropy)
guessing strategy, with both a Tkinter GUI and a command-line interface.

<img width="905" height="796" alt="image" src="https://github.com/user-attachments/assets/dcc53a35-7fbe-4cf9-a644-e0cbb103b809" />

## How it works

Each candidate guess is scored by the Shannon entropy of the distribution
of green/yellow/grey feedback patterns it would produce across every word
still consistent with the clues so far. The guess expected to narrow down
the remaining possibilities the most is suggested first. The opening move
is precomputed (scoring the full ~13,000-word dictionary live would be
slow) using values from `run_wordle.py`'s reference report.

The game defaults to **hard mode**: every guess must be consistent with
all information revealed by previous guesses.

## Features

- Entropy-ranked suggestions, live-updated after every guess
- Hard mode enforced by narrowing the valid-guess list, not just a UI hint
- GUI (`wordle_gui.py`): type letters straight into the tile grid, colored
  feedback, a ranked "Suggested guesses" panel with entropy bars
- CLI (`run_wordle.py`): play interactively, watch the solver play itself,
  or benchmark opening words across every possible solution
- Test suite covering the core solving logic, hard-mode enforcement, and
  an end-to-end scripted game

## Installation

```bash
git clone <this-repo-url>
cd "Wordle solver"
python -m venv .venv
.venv\Scripts\activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
```

## Usage

```bash
python wordle_gui.py     # GUI
python run_wordle.py     # CLI
```

## Running the tests

```bash
pip install -r requirements-test.txt
pytest -n auto
```

## Project structure

```
wordle_solver.py     Core Wordle class: pattern scoring, hard-mode
                      filtering, entropy calculation
run_wordle.py         CLI: play interactively, self-play, or benchmark
                      openers across every solution
wordle_gui.py         Tkinter GUI
tests/                pytest suite (unit + integration)
*.ipynb                Exploratory notebooks used to develop and analyse
                      the solver (word frequency preprocessing,
                      distribution analysis, opener benchmarking)
*.txt                  Word lists and alphabet data used by the solver
```

## License

MIT
