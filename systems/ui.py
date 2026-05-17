"""The HUD — the heads-up display drawn across the top of the screen.

The HUD shows the player's gold, the wave number and the heart's HP.
During the build phase it also shows the build menu (which buildable is
selected) and a hint about whatever the mouse is hovering over.

The HUD is a "view": it only READS from the game and draws — it never
changes anything.
"""

import math

import pygame

import settings


class HUD:
    """Draws the information panel at the top of the screen."""

    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface, game):
        """Draw the whole HUD for this frame."""
        building = game.phase == settings.PHASE_BUILD

        # A translucent panel sits behind the text so it stays readable.
        panel_height = 156 if building else 96
        panel = pygame.Surface((settings.SCREEN_WIDTH, panel_height),
                               pygame.SRCALPHA)
        panel.fill(settings.HUD_PANEL_COLOUR)
        surface.blit(panel, (0, 0))

        # Line 1 — the core stats.
        stats = (f"Gold: {game.economy.gold}        "
                 f"Wave: {game.wave_manager.wave_number}        "
                 f"Heart: {game.heart.hp} / {game.heart.max_hp}")
        self._text(surface, stats, (16, 12))

        # Line 2 — what is happening right now.
        if building:
            seconds = math.ceil(game.build_timer)
            next_wave = game.wave_manager.wave_number + 1
            self._text(
                surface,
                f"BUILD  -  wave {next_wave} starts in {seconds}s  "
                f"(press Enter to start now)",
                (16, 50),
            )
            self._draw_build_menu(surface, game)
        else:
            left = len(game.monsters) + game.wave_manager.to_spawn
            self._text(surface, f"DEFENSE  -  monsters left: {left}", (16, 50))

    def _draw_build_menu(self, surface, game):
        """Draw the two buildables, with the selected one highlighted."""
        tower_selected = game.selected_buildable == "tower"
        self._text(surface,
                   f"[1] Arrow Tower  {settings.TOWER_COST}g",
                   (16, 88), highlight=tower_selected)
        self._text(surface,
                   f"[2] Spike Trap  {settings.TRAP_COST}g",
                   (380, 88), highlight=not tower_selected)

        # A hint about whatever buildable the mouse is hovering over.
        hint = self._hover_hint(game)
        if hint is not None:
            self._text(surface, hint, (16, 122))

    def _hover_hint(self, game):
        """Describe the tower or trap under the mouse, or return None."""
        ts = settings.TILE_SIZE
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x = mouse_x // ts
        tile_y = mouse_y // ts

        tower = game.tower_at(tile_x, tile_y)
        if tower is not None:
            if tower.can_upgrade:
                return (f"Tower level {tower.level}  -  left-click: upgrade "
                        f"({tower.upgrade_cost}g),  right-click: sell")
            return f"Tower level {tower.level} (max)  -  right-click: sell"

        if game.trap_at(tile_x, tile_y) is not None:
            return "Spike Trap  -  right-click: sell"
        return None

    def _text(self, surface, text, position, highlight=False):
        """Draw one line of HUD text — yellow if highlighted, else white."""
        colour = (settings.HUD_SELECTED_COLOUR if highlight
                  else settings.HUD_TEXT_COLOUR)
        surface.blit(self.font.render(text, True, colour), position)
