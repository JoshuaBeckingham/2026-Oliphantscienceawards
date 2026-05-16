"""The dungeon — a randomly generated grid of tiles.

This is PROCEDURAL GENERATION: instead of designing one map by hand, an
algorithm builds a brand-new map every time the game runs. The rules here
are simple — a rock border, scattered rocks inside, a clear centre — but
they already make every game different.
"""

import random

import pygame

import settings
from world import tile


class Dungeon:
    """Holds the tile grid and knows how to build, query and draw it."""

    def __init__(self):
        self.width = settings.GRID_WIDTH
        self.height = settings.GRID_HEIGHT
        # The centre tile — this is where the heart will sit.
        self.centre = (self.width // 2, self.height // 2)
        self.grid = self._generate()

    # --- Building the map ---------------------------------------------

    def _generate(self):
        """Build a fresh random dungeon and return its tile grid."""
        # Start with every tile as open floor.
        grid = [[tile.FLOOR for _ in range(self.width)]
                for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                on_border = (x == 0 or y == 0
                             or x == self.width - 1
                             or y == self.height - 1)
                if on_border:
                    # A solid rock wall frames the whole dungeon.
                    grid[y][x] = tile.ROCK
                elif random.random() < settings.ROCK_DENSITY:
                    # Scatter rocks randomly across the inside.
                    grid[y][x] = tile.ROCK

        # Clear a calm zone around the centre so the heart has room and
        # the hero never spawns trapped inside a rock.
        cx, cy = self.centre
        r = settings.CLEAR_RADIUS
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if self.in_bounds(x, y):
                    grid[y][x] = tile.FLOOR

        return grid

    # --- Asking questions about the map -------------------------------

    def in_bounds(self, x, y):
        """True if tile (x, y) is actually on the map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x, y):
        """The tile type at (x, y). Anything off the map counts as rock."""
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return tile.ROCK

    def is_blocked(self, rect):
        """True if a pixel rectangle overlaps any blocking tile.

        Used for collision: the hero asks "if I move here, do I hit a rock?"
        """
        ts = settings.TILE_SIZE
        left = rect.left // ts
        right = (rect.right - 1) // ts
        top = rect.top // ts
        bottom = (rect.bottom - 1) // ts
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if tile.blocks_movement(self.get_tile(tx, ty)):
                    return True
        return False

    def tile_centre_pixels(self, tx, ty):
        """The pixel position of the centre of tile (tx, ty)."""
        ts = settings.TILE_SIZE
        return (tx * ts + ts // 2, ty * ts + ts // 2)

    # --- Drawing ------------------------------------------------------

    def draw(self, surface):
        """Draw every rock and wall. Floor is left as the background."""
        ts = settings.TILE_SIZE
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.grid[y][x]
                if tile_type == tile.FLOOR:
                    continue   # nothing to draw — the background is floor

                rect = pygame.Rect(x * ts, y * ts, ts, ts)
                if tile_type == tile.ROCK:
                    pygame.draw.rect(surface, settings.ROCK_COLOUR, rect)
                    pygame.draw.rect(surface, settings.ROCK_EDGE_COLOUR, rect, 2)
                elif tile_type == tile.WALL:
                    pygame.draw.rect(surface, settings.WALL_COLOUR, rect)
