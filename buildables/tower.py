"""Buildable: the Arrow Tower.

The player places arrow towers on floor tiles during the build phase.
On its own, a tower watches for monsters within range and shoots an
arrow at the nearest one every TOWER_COOLDOWN seconds.
"""

import math

import pygame

import settings
from entities.projectile import Projectile


class ArrowTower:
    """A tower that automatically shoots arrows at nearby monsters."""

    def __init__(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y

        # The tower's pixel centre — the middle of its tile.
        ts = settings.TILE_SIZE
        self.x = tile_x * ts + ts // 2
        self.y = tile_y * ts + ts // 2

        self.range = settings.TOWER_RANGE
        self.cooldown = 0.0   # seconds until the tower can shoot again

    def update(self, dt, monsters):
        """Count down, then shoot the nearest monster in range.

        Returns a new Projectile if it shot, or None if it did not.
        """
        self.cooldown -= dt
        if self.cooldown > 0:
            return None

        target = self._nearest_monster(monsters)
        if target is None:
            return None

        self.cooldown = settings.TOWER_COOLDOWN
        return Projectile(self.x, self.y, target)

    def _nearest_monster(self, monsters):
        """Find the closest monster within range, or None if there is none."""
        closest = None
        closest_distance = self.range
        for monster in monsters:
            monster_x, monster_y = monster.rect.center
            distance = math.hypot(monster_x - self.x, monster_y - self.y)
            if distance <= closest_distance:
                closest = monster
                closest_distance = distance
        return closest

    def draw(self, surface):
        """Draw the tower: a stone base with a wooden turret on top."""
        ts = settings.TILE_SIZE
        tile_rect = pygame.Rect(self.tile_x * ts, self.tile_y * ts, ts, ts)
        base = tile_rect.inflate(-8, -8)
        pygame.draw.rect(surface, settings.TOWER_BASE_COLOUR, base)
        pygame.draw.rect(surface, settings.TOWER_TRIM_COLOUR, base, 3)
        pygame.draw.circle(surface, settings.TOWER_TURRET_COLOUR,
                           (self.x, self.y), ts // 4)

    def draw_range(self, surface):
        """Draw a faint circle showing how far this tower can shoot."""
        reach = self.range
        circle = pygame.Surface((reach * 2, reach * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle, settings.TOWER_RANGE_COLOUR,
                           (reach, reach), reach)
        surface.blit(circle, (self.x - reach, self.y - reach))
