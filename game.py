"""The Game class — it owns the window and runs the main game loop.

Every game is the same three steps repeated very fast:
    1. handle events  (what did the player press?)
    2. update         (move everything a tiny bit)
    3. draw           (paint the new picture)
Do that 60 times a second and it looks like smooth motion.

The game is also a STATE MACHINE: at any moment it is in exactly one
PHASE, and simple rules decide when to switch:
    BUILD phase   — a calm countdown; place towers, explore, open doors.
    DEFENSE phase — the wave's monsters attack; fight them off.
Clearing a wave switches BUILD <- DEFENSE; the countdown running out (or
pressing Enter) switches BUILD -> DEFENSE.
"""

import math

import pygame

import settings
from entities.hero import Hero
from entities.heart import Heart
from world.dungeon import Dungeon
from world import tile
from systems.waves import WaveManager
from systems.economy import Economy
from buildables.tower import ArrowTower

# The two phases the game switches between.
PHASE_BUILD = "build"
PHASE_DEFENSE = "defense"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Build the dungeon first — the heart and hero are placed inside it.
        self.dungeon = Dungeon()

        # The heart sits in the middle of the dungeon's central room.
        heart_px, heart_py = self.dungeon.tile_centre_pixels(
            *self.dungeon.heart_tile
        )
        self.heart = Heart(
            heart_px - settings.HEART_SIZE // 2,
            heart_py - settings.HEART_SIZE // 2,
        )

        # The hero starts beside the heart, on open floor.
        hero_px, hero_py = self.dungeon.tile_centre_pixels(
            *self.dungeon.spawn_tile
        )
        self.hero = Hero(
            hero_px - settings.HERO_SIZE // 2,
            hero_py - settings.HERO_SIZE // 2,
        )

        # Monsters in the dungeon, and the system that spawns them in waves.
        self.monsters = []
        self.wave_manager = WaveManager(self.dungeon)

        # Towers the player has built, and the arrows currently flying.
        self.towers = []
        self.projectiles = []

        # The player's gold.
        self.economy = Economy()

        # The game starts in the BUILD phase, counting down to wave 1.
        self.phase = PHASE_BUILD
        self.build_timer = settings.WAVE_BUILD_TIME

        # The game ends when the heart is destroyed.
        self.game_over = False
        self.big_font = pygame.font.Font(None, 110)
        self.hud_font = pygame.font.Font(None, 40)

    def run(self):
        """The main game loop. Keeps going until self.running becomes False."""
        while self.running:
            # tick() waits so the game runs at FPS. It returns the number of
            # milliseconds since the last frame; / 1000 turns it into seconds.
            dt = self.clock.tick(settings.FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_events(self):
        """Deal with key presses, mouse clicks and the close button."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_e:
                    # Open or close a door next to the hero.
                    self.dungeon.toggle_door_near(
                        self.hero.rect.centerx,
                        self.hero.rect.centery,
                    )
                elif event.key == pygame.K_RETURN:
                    # Skip the rest of the build countdown.
                    if self.phase == PHASE_BUILD and not self.game_over:
                        self._start_defense()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over:
                    if event.button == 1:    # left click — build or upgrade
                        self._left_click(event.pos)
                    elif event.button == 3:  # right click — sell a tower
                        self._try_sell_tower(event.pos)

    def update(self, dt):
        """Move everything forward by one frame."""
        # Once the game is over, nothing moves any more.
        if self.game_over:
            return

        # The hero can always move (and fight, during a wave).
        self.hero.update(dt, self.dungeon, self.monsters)

        if self.phase == PHASE_BUILD:
            self._update_build(dt)
        elif self.phase == PHASE_DEFENSE:
            self._update_defense(dt)

        # If the heart's HP has run out, the game is over.
        if not self.heart.is_alive:
            self.game_over = True

    def _update_build(self, dt):
        """Count down the calm phase; start the wave when it runs out."""
        self.build_timer -= dt
        if self.build_timer <= 0:
            self._start_defense()

    def _update_defense(self, dt):
        """Spawn and run the wave; return to BUILD once it is cleared."""
        self.wave_manager.update(dt, self.monsters)

        for monster in self.monsters:
            monster.update(dt, self.dungeon, self.heart)

        # Towers shoot — each one may fire a new arrow this frame.
        for tower in self.towers:
            arrow = tower.update(dt, self.monsters)
            if arrow is not None:
                self.projectiles.append(arrow)

        # Move the arrows; they damage monsters when they land.
        for projectile in self.projectiles:
            projectile.update(dt)
        self.projectiles = [p for p in self.projectiles if not p.done]

        # Forget any monsters that have been killed.
        self.monsters = [m for m in self.monsters if m.is_alive]

        # The wave is cleared once every monster is spawned AND gone.
        if self.wave_manager.wave_fully_spawned and not self.monsters:
            self._start_build()

    def _start_defense(self):
        """Switch to the DEFENSE phase and begin the next wave."""
        self.phase = PHASE_DEFENSE
        self.wave_manager.start_wave()

    def _start_build(self):
        """Reward the cleared wave, then switch back to the BUILD phase."""
        reward = (settings.WAVE_GOLD_BASE
                  + self.wave_manager.wave_number * settings.WAVE_GOLD_PER_WAVE)
        self.economy.earn(reward)

        self.phase = PHASE_BUILD
        self.build_timer = settings.WAVE_BUILD_TIME
        self.projectiles = []   # any leftover arrows are cleared

        # Decide which room the next wave comes from, so the player can
        # see the marker and build towers to meet it.
        self.wave_manager.choose_spawn_room()

    # --- Building towers ----------------------------------------------

    def _tower_at(self, tile_x, tile_y):
        """Return the tower standing on tile (tile_x, tile_y), or None."""
        for tower in self.towers:
            if (tower.tile_x, tower.tile_y) == (tile_x, tile_y):
                return tower
        return None

    def _can_place_tower(self, tile_x, tile_y):
        """True if an arrow tower may be placed on tile (tile_x, tile_y)."""
        if self.phase != PHASE_BUILD:
            return False
        if self.dungeon.get_tile(tile_x, tile_y) != tile.FLOOR:
            return False
        if (tile_x, tile_y) == self.dungeon.heart_tile:
            return False
        if self._tower_at(tile_x, tile_y) is not None:
            return False
        return self.economy.can_afford(settings.TOWER_COST)

    def _left_click(self, mouse_pos):
        """Left-click during build: upgrade the tower here, or build one."""
        if self.phase != PHASE_BUILD:
            return
        tile_x = mouse_pos[0] // settings.TILE_SIZE
        tile_y = mouse_pos[1] // settings.TILE_SIZE
        tower = self._tower_at(tile_x, tile_y)
        if tower is not None:
            self._try_upgrade_tower(tower)
        else:
            self._try_place_tower(tile_x, tile_y)

    def _try_place_tower(self, tile_x, tile_y):
        """Build a new tower on the tile, if that is allowed."""
        if not self._can_place_tower(tile_x, tile_y):
            return
        self.economy.spend(settings.TOWER_COST)
        self.towers.append(ArrowTower(tile_x, tile_y))

    def _try_upgrade_tower(self, tower):
        """Upgrade a tower one level, if it can be — and can be afforded."""
        if not tower.can_upgrade:
            return
        if self.economy.spend(tower.upgrade_cost):
            tower.upgrade()

    def _try_sell_tower(self, mouse_pos):
        """Sell the tower under the mouse, refunding part of its cost."""
        if self.phase != PHASE_BUILD:
            return
        tile_x = mouse_pos[0] // settings.TILE_SIZE
        tile_y = mouse_pos[1] // settings.TILE_SIZE
        tower = self._tower_at(tile_x, tile_y)
        if tower is None:
            return
        self.towers.remove(tower)
        self.economy.earn(self._tower_refund())

    def _tower_refund(self):
        """How much gold selling a tower gives back."""
        return int(settings.TOWER_COST * settings.TOWER_SELL_FRACTION)

    # --- Drawing ------------------------------------------------------

    def draw(self):
        """Paint the whole screen for this frame."""
        self.screen.fill(settings.FLOOR_COLOUR)
        self._draw_grid()
        self.dungeon.draw(self.screen)    # rocks and doors on top of the grid
        for tower in self.towers:
            tower.draw(self.screen)
        self.heart.draw(self.screen)      # the heart at the centre
        for monster in self.monsters:     # monsters marching in
            monster.draw(self.screen)
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        self.hero.draw(self.screen)       # the knight on top of everything

        if self.phase == PHASE_BUILD and not self.game_over:
            self._draw_spawn_marker()
            for tower in self.towers:
                tower.draw_range(self.screen)
            self._draw_placement_preview()

        self._draw_hud()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()   # show the finished picture

    def _draw_spawn_marker(self):
        """Mark the room the next wave's monsters will come from."""
        ts = settings.TILE_SIZE
        tile_x, tile_y = self.wave_manager.spawn_tile
        centre = self.dungeon.tile_centre_pixels(tile_x, tile_y)

        # A translucent red disc filling the spawn tile.
        marker = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.circle(marker, settings.SPAWN_MARKER_COLOUR,
                           (ts // 2, ts // 2), ts // 2)
        self.screen.blit(marker, (tile_x * ts, tile_y * ts))

        # A bright ring around it, with a label floating above.
        pygame.draw.circle(self.screen, settings.SPAWN_RING_COLOUR,
                           centre, ts // 2, 3)
        label = self.hud_font.render("Monsters spawn here", True,
                                     settings.SPAWN_RING_COLOUR)
        label_rect = label.get_rect(center=(centre[0], centre[1] - ts))
        self.screen.blit(label, label_rect)

    def _draw_placement_preview(self):
        """Highlight the tile under the mouse — green if a tower can go there."""
        ts = settings.TILE_SIZE
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x = mouse_x // ts
        tile_y = mouse_y // ts
        if self._tower_at(tile_x, tile_y) is not None:
            colour = settings.SELL_HIGHLIGHT_COLOUR   # right-click to sell
        elif self._can_place_tower(tile_x, tile_y):
            colour = settings.PLACE_OK_COLOUR
        else:
            colour = settings.PLACE_BAD_COLOUR
        highlight = pygame.Surface((ts, ts), pygame.SRCALPHA)
        highlight.fill(colour)
        self.screen.blit(highlight, (tile_x * ts, tile_y * ts))

    def _draw_hud(self):
        """Draw the gold, wave number and phase information as text."""
        self._blit_text(f"Gold: {self.economy.gold}", (16, 12))

        if self.phase == PHASE_BUILD:
            next_wave = self.wave_manager.wave_number + 1
            self._blit_text(f"Wave {next_wave} - get ready", (16, 46))
            self._blit_text(
                f"Left-click: build tower ({settings.TOWER_COST}g), "
                f"or upgrade the tower clicked",
                (16, 80),
            )
            self._blit_text(
                f"Right-click a tower: sell it ({self._tower_refund()}g back)",
                (16, 114),
            )
            tower_info = self._hovered_tower_info()
            if tower_info is not None:
                self._blit_text(tower_info, (16, 148))
            seconds = math.ceil(self.build_timer)
            prompt = f"Starts in {seconds}s   (press Enter to start now)"
            surface = self.hud_font.render(prompt, True,
                                           settings.HUD_TEXT_COLOUR)
            rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, 28))
            self.screen.blit(surface, rect)
        else:
            self._blit_text(f"Wave {self.wave_manager.wave_number}", (16, 46))
            left = len(self.monsters) + self.wave_manager.to_spawn
            self._blit_text(f"Monsters left: {left}", (16, 80))

    def _blit_text(self, text, position):
        """Draw a line of HUD text at the given screen position."""
        surface = self.hud_font.render(text, True, settings.HUD_TEXT_COLOUR)
        self.screen.blit(surface, position)

    def _hovered_tower_info(self):
        """A line of text describing the tower under the mouse, or None."""
        ts = settings.TILE_SIZE
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tower = self._tower_at(mouse_x // ts, mouse_y // ts)
        if tower is None:
            return None
        if tower.can_upgrade:
            return (f"Tower level {tower.level}  -  "
                    f"upgrade for {tower.upgrade_cost}g")
        return f"Tower level {tower.level}  (fully upgraded)"

    def _draw_game_over(self):
        """Cover the screen with a big 'GAME OVER' message."""
        text = self.big_font.render("GAME OVER", True,
                                    settings.GAME_OVER_COLOUR)
        text_rect = text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        )
        self.screen.blit(text, text_rect)

    def _draw_grid(self):
        """Draw faint lines so you can see the dungeon's tile grid."""
        for x in range(0, settings.SCREEN_WIDTH, settings.TILE_SIZE):
            pygame.draw.line(
                self.screen, settings.GRID_COLOUR,
                (x, 0), (x, settings.SCREEN_HEIGHT),
            )
        for y in range(0, settings.SCREEN_HEIGHT, settings.TILE_SIZE):
            pygame.draw.line(
                self.screen, settings.GRID_COLOUR,
                (0, y), (settings.SCREEN_WIDTH, y),
            )
