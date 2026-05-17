"""The Projectile — an arrow shot by a tower at a monster.

The arrow "homes in": every frame it steers straight at its target's
current position, so it always lands. When it reaches the monster it
deals damage and is finished. If the target dies first, the arrow
simply fizzles out.
"""

import math

import pygame

import settings


class Projectile:
    """An arrow flying from a tower toward one monster."""

    def __init__(self, x, y, target):
        self.x = float(x)
        self.y = float(y)
        self.target = target          # the monster this arrow chases
        self.speed = settings.PROJECTILE_SPEED
        self.damage = settings.TOWER_DAMAGE
        self.done = False             # True once it has hit or fizzled

        # Direction of travel, as a unit vector — used for drawing.
        self.dir_x = 0.0
        self.dir_y = 0.0
        self._aim()

    def _aim(self):
        """Point the arrow at the target. Returns the distance to it."""
        target_x, target_y = self.target.rect.center
        gap_x = target_x - self.x
        gap_y = target_y - self.y
        distance = math.hypot(gap_x, gap_y)
        if distance > 0:
            self.dir_x = gap_x / distance
            self.dir_y = gap_y / distance
        return distance

    def update(self, dt):
        """Fly toward the target; deal damage once it is reached."""
        # If the monster is already dead, the arrow has nothing to hit.
        if not self.target.is_alive:
            self.done = True
            return

        distance = self._aim()
        step = self.speed * dt
        if distance <= step:
            # The arrow has caught up with the monster.
            self.target.take_damage(self.damage)
            self.done = True
        else:
            self.x += self.dir_x * step
            self.y += self.dir_y * step

    def draw(self, surface):
        """Draw the arrow as a short bright streak."""
        tail_x = self.x - self.dir_x * settings.PROJECTILE_LENGTH
        tail_y = self.y - self.dir_y * settings.PROJECTILE_LENGTH
        pygame.draw.line(surface, settings.PROJECTILE_COLOUR,
                         (self.x, self.y), (tail_x, tail_y), 3)
