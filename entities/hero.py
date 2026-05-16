"""The hero — the character the player controls with the arrow keys."""

import pygame

import assets
import settings
from entities.entity import Entity


class Hero(Entity):
    """The player. For now it just moves; attacking arrives in step 5."""

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

    def update(self, dt, dungeon):
        """Read the arrow keys and move the hero, bumping into rocks."""
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

        # Move one axis at a time. Doing them separately lets the hero
        # slide smoothly along a rock instead of getting stuck on it.
        # Multiplying by dt keeps the speed the same on any computer.
        self._move(dx * self.speed * dt, 0, dungeon)
        self._move(0, dy * self.speed * dt, dungeon)

        self._stay_on_screen()

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
        """Draw the knight sprite, centred on the hero's collision box."""
        sprite_rect = self.sprite.get_rect(center=self.rect.center)
        surface.blit(self.sprite, sprite_rect)
