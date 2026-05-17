"""Monsters — creatures that walk to the heart and attack it.

`Monster` is the BASE class: it holds the shared behaviour (following an
A* path, then attacking the heart). `Goblin` and `Orc` INHERIT from it
and just fill in their own stats — size, speed, HP and colour. Writing
the walking-and-attacking code once, here, is what inheritance is for.

A monster does not work out collisions like the hero does. Instead it is
given a PATH (a list of tiles) and simply follows it, waypoint by
waypoint.
"""

import math

import pygame

import settings
from entities.entity import Entity


class Monster(Entity):
    """Base class for every monster. Follows a path, then attacks the heart."""

    def __init__(self, x, y, size, max_hp, speed, colour, dark_colour,
                 attack_damage=settings.MONSTER_ATTACK_DAMAGE):
        super().__init__(x, y, size, colour, max_hp)
        self.speed = speed
        self.dark_colour = dark_colour       # outline / shading colour
        self.attack_damage = attack_damage   # damage dealt to the heart
        self.path = []          # list of (tile_x, tile_y) to walk through
        self.path_index = 0     # which waypoint we are heading to now
        self.attack_timer = 0.0  # counts down to the next hit on the heart

    def set_path(self, tile_path):
        """Give the monster a new path to follow."""
        self.path = tile_path
        self.path_index = 0

    @property
    def reached_goal(self):
        """True once the monster has walked the whole path."""
        return self.path_index >= len(self.path)

    def update(self, dt, dungeon, heart):
        """Walk along the path, then attack the heart once it is reached."""
        if self.reached_goal:
            self._attack_heart(dt, heart)
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

    def _attack_heart(self, dt, heart):
        """Once at the heart, hit it every MONSTER_ATTACK_COOLDOWN seconds."""
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            heart.take_damage(self.attack_damage)
            self.attack_timer = settings.MONSTER_ATTACK_COOLDOWN

    def draw(self, surface):
        """Draw the monster as a round creature with glowing eyes."""
        centre = (round(self.x + self.size / 2),
                  round(self.y + self.size / 2))
        radius = self.size // 2

        # Body, with a darker outline.
        pygame.draw.circle(surface, self.colour, centre, radius)
        pygame.draw.circle(surface, self.dark_colour, centre, radius, 2)

        # Two small eyes near the top of the body.
        eye_offset_x = radius // 3
        eye_offset_y = radius // 4
        eye_radius = max(2, radius // 5)
        for side in (-1, 1):
            eye = (centre[0] + side * eye_offset_x, centre[1] - eye_offset_y)
            pygame.draw.circle(surface, settings.MONSTER_EYE_COLOUR,
                               eye, eye_radius)

        # A health bar floats above the monster once it has been hurt.
        self.draw_health_bar(surface)


class Goblin(Monster):
    """The basic monster — small, fast and weak."""

    def __init__(self, x, y, max_hp):
        super().__init__(
            x, y,
            settings.GOBLIN_SIZE,
            max_hp,
            settings.GOBLIN_SPEED,
            settings.GOBLIN_COLOUR,
            settings.GOBLIN_DARK_COLOUR,
        )


class Orc(Monster):
    """A bigger monster — slow, but tough. Appears in later waves."""

    def __init__(self, x, y, max_hp):
        super().__init__(
            x, y,
            settings.ORC_SIZE,
            max_hp,
            settings.ORC_SPEED,
            settings.ORC_COLOUR,
            settings.ORC_DARK_COLOUR,
        )


class Boss(Monster):
    """A huge, slow, very tough monster that arrives on boss waves."""

    def __init__(self, x, y, max_hp):
        super().__init__(
            x, y,
            settings.BOSS_SIZE,
            max_hp,
            settings.BOSS_SPEED,
            settings.BOSS_COLOUR,
            settings.BOSS_DARK_COLOUR,
            settings.BOSS_ATTACK_DAMAGE,
        )
