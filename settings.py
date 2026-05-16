"""All the tunable numbers for Dungeon Defenders.

Change values HERE, not deep inside the code. This keeps the rest of the
game easy to read and easy to balance.
"""

# --- The grid ---
# The dungeon is a grid of square tiles. Everything lines up to this grid.
TILE_SIZE = 48        # how many pixels wide/tall one tile is
GRID_WIDTH = 25       # tiles across
GRID_HEIGHT = 18      # tiles down

# --- The window ---
# The screen is exactly big enough to hold the whole grid.
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH    # 48 x 25 = 1200
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT  # 48 x 18 = 864
FPS = 60                                 # frames drawn per second
TITLE = "Dungeon Defenders"

# --- Colours --- (Red, Green, Blue — each 0 to 255)
FLOOR_COLOUR = (40, 40, 50)      # dark dungeon floor
GRID_COLOUR = (55, 55, 68)       # faint lines between tiles
HERO_COLOUR = (80, 170, 240)     # fallback colour if the knight can't draw

# --- The hero ---
HERO_SPEED = 180      # pixels moved per second
HERO_MAX_HP = 100
HERO_SIZE = TILE_SIZE - 8   # slightly smaller than a tile, so the grid shows

# The knight is drawn from pixel art (see entities/knight_art.py).
# KNIGHT_SCALE blows the art up: each art pixel becomes a square this big.
# 2 means the 18x20 art is drawn at 36x40 pixels on screen.
KNIGHT_SCALE = 3

# --- The dungeon (procedural generation) ---
ROCK_DENSITY = 0.16      # chance (0.0-1.0) an inside tile starts as rock
CLEAR_RADIUS = 3         # tiles kept clear around the heart at the centre

ROCK_COLOUR = (92, 82, 80)        # natural rock — can be mined later
ROCK_EDGE_COLOUR = (58, 50, 48)   # darker outline drawn around each rock
WALL_COLOUR = (140, 124, 104)     # built walls (used from step 3)

# --- The heart (what you defend) ---
HEART_SIZE = TILE_SIZE - 6
HEART_MAX_HP = 500
HEART_COLOUR = (214, 48, 72)          # bright red heart
HEART_SHINE_COLOUR = (255, 150, 165)  # small highlight on the heart
