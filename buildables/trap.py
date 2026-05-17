"""Buildable: the Spike Trap.

A spike trap is placed on a floor tile during the build phase. It does
not block movement — monsters walk straight over it. While a monster is
standing on the trap, the spikes strike every TRAP_COOLDOWN seconds,
damaging everything on the tile. It is cheaper than a tower but only
hurts monsters that pass over its one tile.
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

        self.cooldown = 0.0     # seconds until the spikes can strike again
        self.flash_timer = 0.0  # seconds left showing the "struck" look

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
                monster.take_damage(settings.TRAP_DAMAGE)
                struck = True

        # Only go on cooldown if the spikes actually hit something —
        # otherwise the trap stays armed, ready for the next monster.
        if struck:
            self.cooldown = settings.TRAP_COOLDOWN
            self.flash_timer = settings.TRAP_FLASH_TIME

    def draw(self, surface):
        """Draw the trap: a dark base with a row of spikes."""
        # The recessed base.
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
