"""The HUD — the heads-up display drawn across the top of the screen.

The HUD shows the player's gold, the wave number and the heart's HP.
During the build phase it also shows the build menu (which buildable is
selected) and a hint about whatever the mouse is hovering over.

The HUD is a "view": it only READS from the game and draws — it never
changes anything.
"""

import math

import pygame

import assets
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

        trap = game.trap_at(tile_x, tile_y)
        if trap is not None:
            if trap.can_upgrade:
                return (f"Spike Trap level {trap.level}  -  left-click: "
                        f"upgrade ({trap.upgrade_cost}g),  right-click: sell")
            return (f"Spike Trap level {trap.level} (max)  -  "
                    f"right-click: sell")
        return None

    def _text(self, surface, text, position, highlight=False):
        """Draw one line of HUD text — yellow if highlighted, else white."""
        colour = (settings.HUD_SELECTED_COLOUR if highlight
                  else settings.HUD_TEXT_COLOUR)
        surface.blit(self.font.render(text, True, colour), position)


class SettingsMenu:
    """The gear icon in the top-right, and the pause menu it opens.

    Clicking the gear pauses the game and shows a panel of buttons.
    The panel and gear positions are worked out once, in __init__.
    """

    def __init__(self):
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 40)

        # The gear icon sits in the top-right corner.
        size = 56
        margin = 10
        self.gear_rect = pygame.Rect(
            settings.SCREEN_WIDTH - size - margin, margin, size, size)

        # The pause panel, centred on the screen.
        panel_w, panel_h = 440, 392
        panel_x = (settings.SCREEN_WIDTH - panel_w) // 2
        panel_y = (settings.SCREEN_HEIGHT - panel_h) // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Four buttons, stacked inside the panel.
        button_w, button_h = 360, 56
        button_x = panel_x + (panel_w - button_w) // 2
        self.resume_rect = pygame.Rect(button_x, panel_y + 92,
                                       button_w, button_h)
        self.grid_rect = pygame.Rect(button_x, panel_y + 164,
                                     button_w, button_h)
        self.ranges_rect = pygame.Rect(button_x, panel_y + 236,
                                       button_w, button_h)
        self.quit_rect = pygame.Rect(button_x, panel_y + 308,
                                     button_w, button_h)

    def handle_click(self, pos, game):
        """React to a left-click. Returns True if the menu used the click."""
        if self.gear_rect.collidepoint(pos):
            game.paused = not game.paused
            return True

        # While the menu is closed, the gear is the only thing it owns.
        if not game.paused:
            return False

        # While the menu is open it swallows every click, so the player
        # cannot accidentally build a tower behind the panel.
        if self.resume_rect.collidepoint(pos):
            game.paused = False
        elif self.grid_rect.collidepoint(pos):
            game.show_grid = not game.show_grid
        elif self.ranges_rect.collidepoint(pos):
            game.show_ranges = not game.show_ranges
        elif self.quit_rect.collidepoint(pos):
            game.running = False
        return True

    def draw(self, surface, game):
        """Draw the pause panel (if open), then the gear icon on top."""
        if game.paused:
            self._draw_panel(surface, game)
        self._draw_gear(surface)

    def _draw_gear(self, surface):
        """Draw a simple cog: eight teeth, a body, and a centre hole."""
        centre_x, centre_y = self.gear_rect.center
        radius = 17
        for i in range(8):
            angle = math.pi * 2 * i / 8
            tooth = pygame.Rect(0, 0, 11, 11)
            tooth.center = (centre_x + math.cos(angle) * radius,
                            centre_y + math.sin(angle) * radius)
            pygame.draw.rect(surface, settings.GEAR_COLOUR, tooth)
        pygame.draw.circle(surface, settings.GEAR_COLOUR,
                           (centre_x, centre_y), radius)
        pygame.draw.circle(surface, settings.GEAR_DARK_COLOUR,
                           (centre_x, centre_y), radius // 2)

    def _draw_panel(self, surface, game):
        """Dim the screen and draw the pause panel with its buttons."""
        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.MENU_OVERLAY_COLOUR)
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, settings.MENU_PANEL_COLOUR,
                         self.panel_rect, border_radius=12)
        pygame.draw.rect(surface, settings.MENU_BORDER_COLOUR,
                         self.panel_rect, 3, border_radius=12)

        title = self.title_font.render("Settings", True,
                                       settings.MENU_TEXT_COLOUR)
        surface.blit(title, title.get_rect(
            center=(self.panel_rect.centerx, self.panel_rect.top + 40)))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(surface, self.resume_rect, "Resume", mouse_pos)
        grid_text = "Tile grid: ON" if game.show_grid else "Tile grid: OFF"
        self._draw_button(surface, self.grid_rect, grid_text, mouse_pos)
        ranges_text = ("Tower ranges: ON" if game.show_ranges
                       else "Tower ranges: OFF")
        self._draw_button(surface, self.ranges_rect, ranges_text, mouse_pos)
        self._draw_button(surface, self.quit_rect, "Quit game", mouse_pos)

    def _draw_button(self, surface, rect, text, mouse_pos):
        """Draw one menu button, brighter when the mouse is over it."""
        if rect.collidepoint(mouse_pos):
            colour = settings.MENU_BUTTON_HOVER_COLOUR
        else:
            colour = settings.MENU_BUTTON_COLOUR
        pygame.draw.rect(surface, colour, rect, border_radius=8)
        pygame.draw.rect(surface, settings.MENU_BORDER_COLOUR, rect, 2,
                         border_radius=8)
        label = self.font.render(text, True, settings.MENU_TEXT_COLOUR)
        surface.blit(label, label.get_rect(center=rect.center))


class GameOverScreen:
    """The screen shown when the heart is destroyed.

    It shows the score (waves survived) and the best score, with a
    'Play again' button and a 'Quit' button.
    """

    def __init__(self):
        self.title_font = pygame.font.Font(None, 96)
        self.score_font = pygame.font.Font(None, 52)
        self.button_font = pygame.font.Font(None, 40)

        # A panel centred on the screen.
        panel_w, panel_h = 620, 400
        panel_x = (settings.SCREEN_WIDTH - panel_w) // 2
        panel_y = (settings.SCREEN_HEIGHT - panel_h) // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Two buttons side by side near the bottom of the panel.
        button_w, button_h, gap = 220, 60, 28
        total = button_w * 2 + gap
        button_x = panel_x + (panel_w - total) // 2
        button_y = panel_y + panel_h - 86
        self.again_rect = pygame.Rect(button_x, button_y,
                                      button_w, button_h)
        self.quit_rect = pygame.Rect(button_x + button_w + gap, button_y,
                                     button_w, button_h)

    def handle_click(self, pos, game):
        """React to a left-click on the game-over screen."""
        if self.again_rect.collidepoint(pos):
            game.new_game()
        elif self.quit_rect.collidepoint(pos):
            game.running = False

    def draw(self, surface, game):
        """Dim the screen and draw the game-over panel."""
        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(settings.MENU_OVERLAY_COLOUR)
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, settings.MENU_PANEL_COLOUR,
                         self.panel_rect, border_radius=14)
        pygame.draw.rect(surface, settings.MENU_BORDER_COLOUR,
                         self.panel_rect, 3, border_radius=14)

        centre_x = self.panel_rect.centerx

        # The title says YOU WIN! for a victory, GAME OVER for a loss.
        if game.won:
            title_text, title_colour = "YOU WIN!", settings.WIN_COLOUR
        else:
            title_text, title_colour = "GAME OVER", settings.GAME_OVER_COLOUR
        title = self.title_font.render(title_text, True, title_colour)
        surface.blit(title, title.get_rect(
            center=(centre_x, self.panel_rect.top + 70)))

        score = self.score_font.render(
            f"Waves survived: {game.waves_cleared}", True,
            settings.MENU_TEXT_COLOUR)
        surface.blit(score, score.get_rect(
            center=(centre_x, self.panel_rect.top + 160)))

        best = self.score_font.render(
            f"Best: {game.high_score}", True, settings.MENU_TEXT_COLOUR)
        surface.blit(best, best.get_rect(
            center=(centre_x, self.panel_rect.top + 215)))

        # Celebrate a brand-new record.
        if game.waves_cleared > 0 and game.waves_cleared == game.high_score:
            new_best = self.button_font.render("New best!", True,
                                               settings.HUD_SELECTED_COLOUR)
            surface.blit(new_best, new_best.get_rect(
                center=(centre_x, self.panel_rect.top + 258)))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(surface, self.again_rect, "Play again", mouse_pos)
        self._draw_button(surface, self.quit_rect, "Quit", mouse_pos)

    def _draw_button(self, surface, rect, text, mouse_pos):
        """Draw one button, brighter when the mouse is over it."""
        if rect.collidepoint(mouse_pos):
            colour = settings.MENU_BUTTON_HOVER_COLOUR
        else:
            colour = settings.MENU_BUTTON_COLOUR
        pygame.draw.rect(surface, colour, rect, border_radius=8)
        pygame.draw.rect(surface, settings.MENU_BORDER_COLOUR, rect, 2,
                         border_radius=8)
        label = self.button_font.render(text, True, settings.MENU_TEXT_COLOUR)
        surface.blit(label, label.get_rect(center=rect.center))


class TitleScreen:
    """The screen shown when the game first opens, before playing."""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 116)
        self.text_font = pygame.font.Font(None, 40)
        self.button_font = pygame.font.Font(None, 44)

        # The knight sprite, large, as decoration.
        self.knight = assets.load_sprite("knight.png", 230)

        # Two buttons side by side near the bottom.
        button_w, button_h, gap = 220, 64, 32
        total = button_w * 2 + gap
        button_x = (settings.SCREEN_WIDTH - total) // 2
        button_y = 660
        self.play_rect = pygame.Rect(button_x, button_y,
                                     button_w, button_h)
        self.quit_rect = pygame.Rect(button_x + button_w + gap, button_y,
                                     button_w, button_h)

    def handle_click(self, pos, game):
        """React to a left-click on the title screen."""
        if self.play_rect.collidepoint(pos):
            game.start_playing()
        elif self.quit_rect.collidepoint(pos):
            game.running = False

    def draw(self, surface, game):
        """Draw the title screen — name, knight, best score and buttons."""
        surface.fill(settings.TITLE_BG_COLOUR)
        centre_x = settings.SCREEN_WIDTH // 2

        title = self.title_font.render("DUNGEON DEFENDERS", True,
                                       settings.TITLE_COLOUR)
        surface.blit(title, title.get_rect(center=(centre_x, 110)))

        surface.blit(self.knight,
                     self.knight.get_rect(center=(centre_x, 350)))

        best = self.text_font.render(
            f"Best: {game.high_score} waves survived", True,
            settings.HUD_TEXT_COLOUR)
        surface.blit(best, best.get_rect(center=(centre_x, 525)))

        controls = self.text_font.render(
            "Arrow keys: move    Space: attack    "
            "E: doors    Click: build", True, settings.HUD_TEXT_COLOUR)
        surface.blit(controls, controls.get_rect(center=(centre_x, 580)))

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(surface, self.play_rect, "Play", mouse_pos)
        self._draw_button(surface, self.quit_rect, "Quit", mouse_pos)

    def _draw_button(self, surface, rect, text, mouse_pos):
        """Draw one button, brighter when the mouse is over it."""
        if rect.collidepoint(mouse_pos):
            colour = settings.MENU_BUTTON_HOVER_COLOUR
        else:
            colour = settings.MENU_BUTTON_COLOUR
        pygame.draw.rect(surface, colour, rect, border_radius=8)
        pygame.draw.rect(surface, settings.MENU_BORDER_COLOUR, rect, 2,
                         border_radius=8)
        label = self.button_font.render(text, True, settings.MENU_TEXT_COLOUR)
        surface.blit(label, label.get_rect(center=rect.center))
