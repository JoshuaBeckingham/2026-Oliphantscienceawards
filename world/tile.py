"""Tile types for the dungeon grid.

A tile is just a number. The dungeon stores a big grid of these numbers,
which is much simpler (and faster) than storing a whole object per square.
"""

FLOOR = 0         # open ground — the hero and monsters can walk here
ROCK = 1          # solid rock — blocks movement, cannot be passed
WALL = 2          # a wall the player builds — blocks movement (later step)
DOOR_CLOSED = 3   # a shut door — blocks movement until it is opened
DOOR_OPEN = 4     # an open door — can be walked through

# Tile types in this set stop things from walking through them.
BLOCKING = {ROCK, WALL, DOOR_CLOSED}

# The two states a door can be in.
DOORS = {DOOR_CLOSED, DOOR_OPEN}


def blocks_movement(tile_type):
    """True if this kind of tile cannot be walked through."""
    return tile_type in BLOCKING


def is_door(tile_type):
    """True if this tile is a door (open or closed)."""
    return tile_type in DOORS
