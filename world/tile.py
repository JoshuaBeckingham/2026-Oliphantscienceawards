"""Tile types for the dungeon grid.

A tile is just a number. The dungeon stores a big grid of these numbers,
which is much simpler (and faster) than storing a whole object per square.
"""

FLOOR = 0   # open ground — the hero and monsters can walk here
ROCK = 1    # natural rock — blocks movement, mined for stone (step 3)
WALL = 2    # a wall the player builds — blocks movement (step 3)

# Tile types in this set stop things from walking through them.
BLOCKING = {ROCK, WALL}


def blocks_movement(tile_type):
    """True if this kind of tile cannot be walked through."""
    return tile_type in BLOCKING
