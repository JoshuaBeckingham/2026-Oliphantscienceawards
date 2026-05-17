"""Buildable: the Spike Trap.

A spike trap is placed on a floor tile during the build phase. It does
not block movement — monsters walk straight over it. While a monster is
standing on the trap, the spikes strike every so often, damaging
everything on the tile.

Like a tower, a trap can be UPGRADED (up to TRAP_MAX_LEVEL). Each level
makes it hit harder and strike faster. The damage and strike delay are
worked out from the level with @property, so they are always correct.
"""

import pygame

import settings


class SpikeTrap:
    """A floor trap that damages monsters standing on it."""

    def __init__(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y

        # The trap covers exactly its one tile.
        ts = settings.TILE_SIZE
        self.rect = pygame.Rect(tile_x * ts, tile_y * ts, ts, ts)

        self.level = 1
        self.cooldown = 0.0     # seconds until the spikes can strike again
        self.flash_timer = 0.0  # seconds left showing the "struck" look

    # --- Stats that depend on the trap's level ------------------------

    @property
    def damage(self):
        """How much damage the spikes do, at this trap's current level."""
        return (settings.TRAP_DAMAGE
                + (self.level - 1) * settings.TRAP_UPGRADE_DAMAGE)

    @property
    def strike_delay(self):
        """Seconds between strikes — smaller (faster) at higher levels."""
        return (settings.TRAP_COOLDOWN
                - (self.level - 1) * settings.TRAP_UPGRADE_SPEED)

    @property
    def can_upgrade(self):
        """True if the trap has not yet reached the maximum level."""
        return self.level < settings.TRAP_MAX_LEVEL

    @property
    def upgrade_cost(self):
        """Gold needed to upgrade the trap one more level."""
        return settings.TRAP_UPGRADE_COST * self.level

    def upgrade(self):
        """Raise the trap one level (the caller checks the cost first)."""
        self.level += 1

    # --- Striking -----------------------------------------------------

    def update(self, dt, monsters):
        """If the spikes are ready and monsters are on the trap, strike."""
        self.cooldown -= dt
        self.flash_timer -= dt
        if self.cooldown > 0:
            return

        # Hurt every monster overlapping the trap's tile.
        struck = False
        for monster in monsters:
            if monster.rect.colliderect(self.rect):
                monster.take_damage(self.damage)
                struck = True

        # Only go on cooldown if the spikes actually hit something —
        # otherwise the trap stays armed, ready for the next monster.
        if struck:
            self.cooldown = self.strike_delay
            self.flash_timer = settings.TRAP_FLASH_TIME

    # --- Drawing ------------------------------------------------------

    def draw(self, surface):
        """Draw the trap: a dark base, a row of spikes, and level dots."""
        base = self.rect.inflate(-6, -6)
        pygame.draw.rect(surface, settings.TRAP_BASE_COLOUR, base)

        # The spikes look bright orange for a moment after they strike.
        if self.flash_timer > 0:
            spike_colour = settings.TRAP_SPIKE_FIRED_COLOUR
        else:
            spike_colour = settings.TRAP_SPIKE_COLOUR

        # Three triangular spikes pointing up, side by side.
        spike_count = 3
        spacing = base.width // spike_count
        for i in range(spike_count):
            left = base.left + i * spacing
            tip_x = left + spacing // 2
            points = [
                (left + 2, base.bottom - 4),            # bottom-left
                (left + spacing - 2, base.bottom - 4),  # bottom-right
                (tip_x, base.top + 4),                  # tip
            ]
            pygame.draw.polygon(surface, spike_colour, points)

        # One dot per level, in a row along the bottom of the trap.
        gap = 9
        first_x = self.rect.centerx - gap * (self.level - 1) / 2
        pip_y = base.bottom - 5
        for i in range(self.level):
            pip_x = int(first_x + i * gap)
            pygame.draw.circle(surface, settings.TOWER_PIP_COLOUR,
                               (pip_x, pip_y), 3)
