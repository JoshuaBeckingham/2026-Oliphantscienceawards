"""The high score — the best number of waves ever survived.

It is saved to a small text file (highscore.txt) next to the game, so
it is remembered the next time the game is opened.
"""

import pathlib

# The file lives in the project folder, alongside main.py. Building the
# path from __file__ means it works whatever folder the game is run from.
HIGH_SCORE_FILE = (pathlib.Path(__file__).resolve().parent.parent
                   / "highscore.txt")


def load_high_score():
    """Read the saved high score. Returns 0 if there is not one yet."""
    try:
        return int(HIGH_SCORE_FILE.read_text())
    except (OSError, ValueError):
        # No file yet, or the file is unreadable — start from zero.
        return 0


def save_high_score(score):
    """Write the high score to the file."""
    try:
        HIGH_SCORE_FILE.write_text(str(score))
    except OSError:
        # If the file cannot be written, the game just carries on.
        pass
