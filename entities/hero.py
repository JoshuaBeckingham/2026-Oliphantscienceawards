"""The hero — the character the player controls with the arrow keys."""

import math

import pygame

import assets
import settings
from entities.entity import Entity


class Hero(Entity):
    """The player: moves with the arrow keys, attacks with the spacebar."""

    def __init__(self, x, y):
        # Build the Entity part of the hero (position, size, colour, HP).
        super().__init__(
            x, y,
            settings.HERO_SIZE,
            settings.HERO_COLOUR,
            settings.HERO_MAX_HP,
        )
        self.speed = settings.HERO_SPEED

        # Load the knight sprite once, scaled to the hero's on-screen size.
        self.sprite = assets.load_sprite("knight.png", settings.HERO_SPRITE_HEIGHT)

        # Attack timers (in seconds). attack_timer counts down until the
        # next swing is allowed; swing_timer counts down the swing flash.
        self.attack_timer = 0.0
        self.swing_timer = 0.0

        # The direction the knight is facing, as a unit vector. The sword
        # swing happens in this direction. Starts off facing downward.
        self.facing = (0.0, 1.0)

    def update(self, dt, dungeon, monsters):
        """Read the keys: move the hero, and swing the sword with Space."""
        keys = pygame.key.get_pressed()

        # Work out the direction: -1, 0 or +1 on each axis.
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        # If the hero is moving, remember the direction as a unit vector
        # so the sword swing knows which way to face.
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            self.facing = (dx / length, dy / length)

        # Move one axis at a time. Doing them separately lets the hero
        # slide smoothly along a rock instead of getting stuck on it.
        # Multiplying by dt keeps the speed the same on any computer.
        self._move(dx * self.speed * dt, 0, dungeon)
        self._move(0, dy * self.speed * dt, dungeon)

        self._stay_on_screen()

        # Count the timers down towards zero.
        self.attack_timer -= dt
        self.swing_timer -= dt

        # Swing the sword while Space is held — but only as fast as the
        # cooldown allows, so you can't hit every single frame.
        if keys[pygame.K_SPACE] and self.attack_timer <= 0:
            self._attack(monsters)

    def _attack(self, monsters):
        """Swing the sword: hurt monsters within range AND inside the arc.

        A monster counts as "in the arc" if the direction to it is within
        half the arc angle of the way the knight is facing.
        """
        self.attack_timer = settings.HERO_ATTACK_COOLDOWN
        self.swing_timer = settings.HERO_SWING_TIME

        centre_x, centre_y = self.rect.center
        facing_x, facing_y = self.facing
        # cos of the half-arc: a bigger dot product means a smaller angle.
        # The tiny 1e-6 makes a monster exactly on the arc edge count.
        half_arc = math.radians(settings.HERO_ATTACK_ARC / 2)
        min_dot = math.cos(half_arc) - 1e-6

        for monster in monsters:
            monster_x, monster_y = monster.rect.center
            gap_x = monster_x - centre_x
            gap_y = monster_y - centre_y
            distance = math.hypot(gap_x, gap_y)
            if distance > settings.HERO_ATTACK_RANGE:
                continue
            if distance == 0:
                # Monster is right on top of the hero — always a hit.
                monster.take_damage(settings.HERO_ATTACK_DAMAGE)
                continue
            # Dot product of facing with the (unit) direction to the
            # monster tells us the angle between them.
            dot = (gap_x * facing_x + gap_y * facing_y) / distance
            if dot >= min_dot:
                monster.take_damage(settings.HERO_ATTACK_DAMAGE)

    def _move(self, dx, dy, dungeon):
        """Move by (dx, dy), but undo it if we would end up inside a rock."""
        self.x += dx
        self.y += dy
        if dungeon.is_blocked(self.rect):
            self.x -= dx
            self.y -= dy

    def _stay_on_screen(self):
        """Stop the hero walking off the edge of the window."""
        max_x = settings.SCREEN_WIDTH - self.size
        max_y = settings.SCREEN_HEIGHT - self.size
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def draw(self, surface):
        """Draw the knight sprite, plus the swing flash if attacking."""
        if self.swing_timer > 0:
            self._draw_swing(surface)

        sprite_rect = self.sprite.get_rect(center=self.rect.center)
        surface.blit(self.sprite, sprite_rect)

    def _draw_swing(self, surface):
        """Draw a translucent wedge showing the arc the sword swept."""
        reach = settings.HERO_ATTACK_RANGE
        # A separate see-through surface, so the flash blends with the scene.
        flash = pygame.Surface((reach * 2, reach * 2), pygame.SRCALPHA)
        centre = (reach, reach)

        # Build a pie-slice: the centre point, then points along the arc
        # from one edge of the swing to the other.
        facing_angle = math.atan2(self.facing[1], self.facing[0])
        half_arc = math.radians(settings.HERO_ATTACK_ARC / 2)
        points = [centre]
        segments = 12
        for i in range(segments + 1):
            angle = facing_angle - half_arc + (2 * half_arc) * i / segments
            points.append((centre[0] + math.cos(angle) * reach,
                           centre[1] + math.sin(angle) * reach))
        pygame.draw.polygon(flash, settings.HERO_SWING_COLOUR, points)

        surface.blit(flash, (self.rect.centerx - reach,
                             self.rect.centery - reach))
