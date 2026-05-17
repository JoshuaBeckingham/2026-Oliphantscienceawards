"""The Monster — a creature that walks through the dungeon to the heart.

For now there is just one kind of monster and it only walks. Attacking
the heart comes in the next step; more monster types come later.

The monster does not work out collisions like the hero does. Instead it
is given a PATH (a list of tiles found by A* pathfinding) and simply
follows it, waypoint by waypoint.
"""

import math

import pygame

import settings
from entities.entity import Entity


class Monster(Entity):
    """A monster that follows a pre-planned path of tiles to the heart."""

    def __init__(self, x, y):
        super().__init__(
            x, y,
            settings.MONSTER_SIZE,
            settings.MONSTER_COLOUR,
            settings.MONSTER_MAX_HP,
        )
        self.speed = settings.MONSTER_SPEED
        self.path = []          # list of (tile_x, tile_y) to walk through
        self.path_index = 0     # which waypoint we are heading to now

    def set_path(self, tile_path):
        """Give the monster a new path to follow."""
        self.path = tile_path
        self.path_index = 0

    @property
    def reached_goal(self):
        """True once the monster has walked the whole path."""
        return self.path_index >= len(self.path)

    def update(self, dt, dungeon):
        """Walk a little way along the path toward the next waypoint."""
        if self.reached_goal:
            return

        # Where is the next waypoint, in pixels?
        target_tile = self.path[self.path_index]
        target_x, target_y = dungeon.tile_centre_pixels(*target_tile)

        # Where is the monster's own centre right now?
        centre_x = self.x + self.size / 2
        centre_y = self.y + self.size / 2

        # The straight-line gap to the waypoint.
        gap_x = target_x - centre_x
        gap_y = target_y - centre_y
        distance = math.hypot(gap_x, gap_y)

        step = self.speed * dt
        if distance <= step or distance == 0:
            # Close enough — snap onto the waypoint and aim at the next one.
            self.x = target_x - self.size / 2
            self.y = target_y - self.size / 2
            self.path_index += 1
            # A monster shoves any closed door open as it passes through.
            dungeon.open_door_at(*target_tile)
        else:
            # Move part of the way toward the waypoint.
            self.x += gap_x / distance * step
            self.y += gap_y / distance * step

    def draw(self, surface):
        """Draw the monster as a round green creature with glowing eyes."""
        centre = (round(self.x + self.size / 2),
                  round(self.y + self.size / 2))
        radius = self.size // 2

        # Body, with a darker outline.
        pygame.draw.circle(surface, settings.MONSTER_COLOUR, centre, radius)
        pygame.draw.circle(surface, settings.MONSTER_DARK_COLOUR, centre,
                           radius, 2)

        # Two small eyes near the top of the body.
        eye_offset_x = radius // 3
        eye_offset_y = radius // 4
        eye_radius = max(2, radius // 5)
        for side in (-1, 1):
            eye = (centre[0] + side * eye_offset_x, centre[1] - eye_offset_y)
            pygame.draw.circle(surface, settings.MONSTER_EYE_COLOUR,
                               eye, eye_radius)
