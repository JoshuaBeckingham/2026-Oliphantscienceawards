"""The Heart — the object at the centre of the dungeon that you defend.

The monsters are all trying to reach and destroy it. When its HP hits
zero, the game is over.
"""

import pygame

import settings
from entities.entity import Entity


class Heart(Entity):
    """A big red heart sitting on the centre tile of the dungeon."""

    def __init__(self, x, y):
        super().__init__(
            x, y,
            settings.HEART_SIZE,
            settings.HEART_COLOUR,
            settings.HEART_MAX_HP,
        )

    def draw(self, surface):
        """Draw a heart: two round humps on top, a triangle pointing down."""
        s = self.size
        x = self.x
        y = self.y

        # The triangle that forms the pointed bottom of the heart.
        triangle = [
            (x + 0.03 * s, y + 0.42 * s),   # top-left
            (x + 0.97 * s, y + 0.42 * s),   # top-right
            (x + 0.50 * s, y + 1.02 * s),   # bottom point
        ]
        pygame.draw.polygon(surface, self.colour, triangle)

        # The two round humps at the top.
        hump_radius = round(0.28 * s)
        left_hump = (round(x + 0.30 * s), round(y + 0.36 * s))
        right_hump = (round(x + 0.70 * s), round(y + 0.36 * s))
        pygame.draw.circle(surface, self.colour, left_hump, hump_radius)
        pygame.draw.circle(surface, self.colour, right_hump, hump_radius)

        # A small bright highlight, so the heart looks shiny.
        shine = (round(x + 0.34 * s), round(y + 0.30 * s))
        pygame.draw.circle(surface, settings.HEART_SHINE_COLOUR,
                           shine, round(0.10 * s))
