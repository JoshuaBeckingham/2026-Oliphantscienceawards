"""Buildable: the Arrow Tower.

The player places arrow towers on floor tiles during the build phase.
On its own, a tower watches for monsters within range and shoots an
arrow at the nearest one every TOWER_COOLDOWN seconds.

A tower can also be UPGRADED (up to TOWER_MAX_LEVEL). Each level adds
damage and range. The damage and range are worked out from the level
with @property, so they are always correct after an upgrade.
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

        self.level = 1
        self.cooldown = 0.0   # seconds until the tower can shoot again

    # --- Stats that depend on the tower's level -----------------------

    @property
    def damage(self):
        """How much damage this tower's arrows do, at its current level."""
        return (settings.TOWER_DAMAGE
                + (self.level - 1) * settings.TOWER_UPGRADE_DAMAGE)

    @property
    def range(self):
        """How far this tower can shoot, at its current level."""
        return (settings.TOWER_RANGE
                + (self.level - 1) * settings.TOWER_UPGRADE_RANGE)

    @property
    def shots(self):
        """How many arrows the tower fires at once.

        A fully-upgraded (level 3) tower fires one extra arrow.
        """
        return 2 if self.level >= 3 else 1

    @property
    def can_upgrade(self):
        """True if the tower has not yet reached the maximum level."""
        return self.level < settings.TOWER_MAX_LEVEL

    @property
    def upgrade_cost(self):
        """Gold needed to upgrade the tower one more level."""
        return settings.TOWER_UPGRADE_COST * self.level

    def upgrade(self):
        """Raise the tower one level (the caller checks the cost first)."""
        self.level += 1

    # --- Shooting -----------------------------------------------------

    def update(self, dt, monsters, dungeon):
        """Count down, then shoot the nearest monster(s) in range and sight.

        Returns a list of new Projectiles — it may be empty. A level-3
        tower fires two arrows, so the list can hold two.
        """
        self.cooldown -= dt
        if self.cooldown > 0:
            return []

        targets = self._pick_targets(monsters, dungeon)
        if not targets:
            return []

        # If there are fewer monsters than arrows, the spare arrows are
        # aimed at the nearest monster as well.
        while len(targets) < self.shots:
            targets.append(targets[0])

        self.cooldown = settings.TOWER_COOLDOWN
        return [Projectile(self.x, self.y, target, self.damage)
                for target in targets]

    def _pick_targets(self, monsters, dungeon):
        """The nearest monsters in range with a clear line of sight.

        Returns at most `self.shots` of them. A monster behind a wall is
        skipped, so the tower never shoots an arrow through rock.
        """
        in_sight = []
        for monster in monsters:
            monster_x, monster_y = monster.rect.center
            distance = math.hypot(monster_x - self.x, monster_y - self.y)
            if distance > self.range:
                continue
            if not dungeon.has_line_of_sight(self.x, self.y,
                                             monster_x, monster_y):
                continue
            in_sight.append((distance, monster))

        # Sort nearest-first, then keep only as many as the tower can fire.
        in_sight.sort(key=lambda pair: pair[0])
        return [monster for (distance, monster) in in_sight[:self.shots]]

    # --- Drawing ------------------------------------------------------

    def draw(self, surface):
        """Draw the tower: a stone base, a turret, and level dots."""
        ts = settings.TILE_SIZE
        tile_rect = pygame.Rect(self.tile_x * ts, self.tile_y * ts, ts, ts)
        base = tile_rect.inflate(-8, -8)
        pygame.draw.rect(surface, settings.TOWER_BASE_COLOUR, base)
        pygame.draw.rect(surface, settings.TOWER_TRIM_COLOUR, base, 3)
        pygame.draw.circle(surface, settings.TOWER_TURRET_COLOUR,
                           (self.x, self.y), ts // 4)

        # One dot per level, in a row below the turret.
        spacing = 9
        first_x = self.x - spacing * (self.level - 1) / 2
        pip_y = self.y + ts // 4 + 4
        for i in range(self.level):
            pip_x = int(first_x + i * spacing)
            pygame.draw.circle(surface, settings.TOWER_PIP_COLOUR,
                               (pip_x, pip_y), 3)

    def draw_range(self, surface):
        """Draw a faint circle showing how far this tower can shoot."""
        reach = self.range
        circle = pygame.Surface((reach * 2, reach * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle, settings.TOWER_RANGE_COLOUR,
                           (reach, reach), reach)
        surface.blit(circle, (self.x - reach, self.y - reach))
