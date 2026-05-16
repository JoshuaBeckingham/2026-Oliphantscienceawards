"""The base class for everything that exists in the dungeon.

The hero, monsters, the heart and projectiles will all inherit from Entity.
That is object-oriented programming: shared behaviour written once, here.
"""

import pygame


class Entity:
    """A thing with a position, a size, a colour and HP (health points)."""

    def __init__(self, x, y, size, colour, max_hp):
        self.x = x              # pixel position of the top-left corner
        self.y = y
        self.size = size        # width and height in pixels (a square)
        self.colour = colour
        self.max_hp = max_hp
        self.hp = max_hp        # start at full health

    @property
    def rect(self):
        """A pygame Rect for this entity — used for drawing and collisions."""
        return pygame.Rect(self.x, self.y, self.size, self.size)

    @property
    def is_alive(self):
        """True while the entity still has health left."""
        return self.hp > 0

    def update(self, dt):
        """Move and think. Subclasses override this.

        dt is 'delta time': the number of seconds since the last frame.
        Multiplying by dt makes movement smooth and speed-consistent.
        """
        pass

    def draw(self, surface):
        """Draw the entity as a coloured square (real art comes in step 10)."""
        pygame.draw.rect(surface, self.colour, self.rect)
