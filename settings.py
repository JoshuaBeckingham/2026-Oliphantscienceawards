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

# The hero is drawn using the sprite Art/knight.png, scaled to this
# height in pixels (the width follows automatically to keep its shape).
HERO_SPRITE_HEIGHT = 72

# --- The dungeon (procedural generation) ---
MAX_ROOMS = 9          # most rooms a dungeon can have (the centre counts)
ROOM_ATTEMPTS = 80     # how many times to try fitting a new random room
ROOM_MIN_SIZE = 4      # smallest room width/height, in tiles
ROOM_MAX_SIZE = 7      # largest room width/height, in tiles

ROCK_COLOUR = (92, 82, 80)        # solid rock — blocks movement
ROCK_EDGE_COLOUR = (58, 50, 48)   # darker outline drawn around each rock
WALL_COLOUR = (140, 124, 104)     # built walls (used in a later step)

DOOR_WOOD_COLOUR = (146, 96, 52)    # the wooden door itself
DOOR_FRAME_COLOUR = (70, 46, 30)    # dark stone frame around the doorway
DOOR_HANDLE_COLOUR = (224, 200, 96) # little gold handle on a closed door

# --- The heart (what you defend) ---
HEART_SIZE = TILE_SIZE - 6
HEART_MAX_HP = 1000
HEART_COLOUR = (214, 48, 72)          # bright red heart
HEART_SHINE_COLOUR = (255, 150, 165)  # small highlight on the heart

# --- Monsters ---
MONSTER_SIZE = TILE_SIZE - 16   # smaller than a tile, so it fits corridors
MONSTER_SPEED = 90              # pixels per second (slower than the hero)
MONSTER_MAX_HP = 30
MONSTER_COLOUR = (110, 170, 70)       # goblin green
MONSTER_DARK_COLOUR = (60, 100, 40)   # darker outline / shading
MONSTER_EYE_COLOUR = (240, 240, 120)  # glowing eyes

# --- Combat ---
# The hero's sword swing (press Space).
HERO_ATTACK_DAMAGE = 12
HERO_ATTACK_RANGE = 72         # pixels — how far the swing reaches
HERO_ATTACK_ARC = 90           # width of the swing, in degrees, facing the
                               # way the knight last moved (90 = a quarter)
HERO_ATTACK_COOLDOWN = 0.35    # seconds you must wait between swings
HERO_SWING_TIME = 0.12         # how long the swing flash stays on screen
HERO_SWING_COLOUR = (255, 255, 200, 90)   # translucent flash (R, G, B, alpha)

# How hard a monster hits the heart once it arrives.
MONSTER_ATTACK_DAMAGE = 20
MONSTER_ATTACK_COOLDOWN = 1.0  # seconds between the monster's hits

# Health bars floating above damaged monsters and the heart.
HP_BAR_HEIGHT = 6
HP_BAR_BACK_COLOUR = (60, 20, 20)     # empty part of the bar
HP_BAR_FILL_COLOUR = (70, 200, 80)    # remaining health

# The "GAME OVER" message shown when the heart is destroyed.
GAME_OVER_COLOUR = (235, 60, 60)

# --- Waves ---
# Monsters arrive in waves. Each wave is bigger and tougher than the last.
WAVE_BASE_MONSTERS = 3      # how many monsters wave 1 has
WAVE_MONSTER_STEP = 2       # extra monsters each wave (3, 5, 7, 9, ...)
WAVE_HP_STEP = 10           # extra HP each monster gains per wave
WAVE_SPAWN_GAP = 0.8        # seconds between each monster appearing
WAVE_BUILD_TIME = 8.0       # seconds of calm before a wave begins

# On-screen wave / phase text.
HUD_TEXT_COLOUR = (235, 235, 245)

# --- Gold (the economy) ---
STARTING_GOLD = 80
# Gold is earned by surviving a whole wave. The reward grows each wave:
# reward = WAVE_GOLD_BASE + wave_number * WAVE_GOLD_PER_WAVE
WAVE_GOLD_BASE = 40
WAVE_GOLD_PER_WAVE = 10

# --- Arrow tower (a buildable) ---
TOWER_COST = 50                # gold to place one tower
TOWER_SELL_FRACTION = 0.7      # fraction of the cost refunded when sold
TOWER_RANGE = 160              # pixels — how far a level-1 tower can shoot
TOWER_DAMAGE = 8               # damage of a level-1 tower's arrow
TOWER_COOLDOWN = 0.7           # seconds between shots

# Upgrading a tower (left-click an existing tower):
TOWER_MAX_LEVEL = 3
TOWER_UPGRADE_COST = 40        # cost = TOWER_UPGRADE_COST * the tower's level
TOWER_UPGRADE_DAMAGE = 6       # extra arrow damage gained per level
TOWER_UPGRADE_RANGE = 30       # extra range (pixels) gained per level

TOWER_BASE_COLOUR = (95, 90, 105)        # stone body of the tower
TOWER_TRIM_COLOUR = (145, 140, 160)      # lighter edge
TOWER_TURRET_COLOUR = (170, 120, 60)     # the wooden turret on top
TOWER_RANGE_COLOUR = (120, 160, 220, 40) # faint range circle (R,G,B,alpha)
TOWER_PIP_COLOUR = (245, 230, 150)       # level dots drawn on the tower

# Tile highlight shown under the mouse while building.
PLACE_OK_COLOUR = (90, 200, 90, 70)      # a tower can go here
PLACE_BAD_COLOUR = (200, 70, 70, 70)     # a tower cannot go here
SELL_HIGHLIGHT_COLOUR = (230, 170, 60, 90)  # hovering a tower (right-click sells)

# Marker showing which room the next wave's monsters will come from.
SPAWN_MARKER_COLOUR = (220, 60, 60, 70)   # translucent disc (R,G,B,alpha)
SPAWN_RING_COLOUR = (235, 90, 90)         # bright ring and label

# --- Projectiles (tower arrows) ---
PROJECTILE_SPEED = 420         # pixels per second
PROJECTILE_LENGTH = 14         # length of the arrow streak
PROJECTILE_COLOUR = (245, 230, 150)
