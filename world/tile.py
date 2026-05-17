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

# Tiles that monster pathfinding must route around. Doors are NOT in here:
# monsters head straight for the heart and push through any door.
PATH_BLOCKING = {ROCK, WALL}

# Tiles that block a tower's line of sight, so arrows cannot fly through
# rock or walls. (Doorways are gaps — arrows can pass through them.)
SIGHT_BLOCKING = {ROCK, WALL}

# The two states a door can be in.
DOORS = {DOOR_CLOSED, DOOR_OPEN}


def blocks_movement(tile_type):
    """True if this kind of tile cannot be walked through."""
    return tile_type in BLOCKING


def blocks_path(tile_type):
    """True if monster pathfinding must route around this tile."""
    return tile_type in PATH_BLOCKING


def blocks_sight(tile_type):
    """True if this tile blocks a tower's line of sight (and its arrows)."""
    return tile_type in SIGHT_BLOCKING


def is_door(tile_type):
    """True if this tile is a door (open or closed)."""
    return tile_type in DOORS
