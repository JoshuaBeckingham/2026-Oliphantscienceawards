"""The Game class — it owns the window and runs the main game loop.

Every game is the same three steps repeated very fast:
    1. handle events  (what did the player press?)
    2. update         (move everything a tiny bit)
    3. draw           (paint the new picture)
Do that 60 times a second and it looks like smooth motion.

The game is also a STATE MACHINE: at any moment it is in exactly one
PHASE, and simple rules decide when to switch:
    BUILD phase   — a calm countdown before the wave; explore, open doors.
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
from systems.waves import WaveManager

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
        """Deal with key presses and the window's close button."""
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

        # Forget any monsters the hero has killed.
        self.monsters = [m for m in self.monsters if m.is_alive]

        # The wave is cleared once every monster is spawned AND gone.
        if self.wave_manager.wave_fully_spawned and not self.monsters:
            self._start_build()

    def _start_defense(self):
        """Switch to the DEFENSE phase and begin the next wave."""
        self.phase = PHASE_DEFENSE
        self.wave_manager.start_wave()

    def _start_build(self):
        """Switch back to the BUILD phase, counting down to the next wave."""
        self.phase = PHASE_BUILD
        self.build_timer = settings.WAVE_BUILD_TIME

    def draw(self):
        """Paint the whole screen for this frame."""
        self.screen.fill(settings.FLOOR_COLOUR)
        self._draw_grid()
        self.dungeon.draw(self.screen)    # rocks and doors on top of the grid
        self.heart.draw(self.screen)      # the heart at the centre
        for monster in self.monsters:     # monsters marching in
            monster.draw(self.screen)
        self.hero.draw(self.screen)       # the knight on top of everything
        self._draw_hud()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()   # show the finished picture

    def _draw_hud(self):
        """Draw the wave number and phase information as text."""
        if self.phase == PHASE_BUILD:
            next_wave = self.wave_manager.wave_number + 1
            self._blit_text(f"Wave {next_wave} - get ready", (16, 12))
            seconds = math.ceil(self.build_timer)
            prompt = f"Starts in {seconds}s   (press Enter to start now)"
            surface = self.hud_font.render(prompt, True,
                                           settings.HUD_TEXT_COLOUR)
            rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, 28))
            self.screen.blit(surface, rect)
        else:
            self._blit_text(f"Wave {self.wave_manager.wave_number}", (16, 12))
            left = len(self.monsters) + self.wave_manager.to_spawn
            self._blit_text(f"Monsters left: {left}", (16, 46))

    def _blit_text(self, text, position):
        """Draw a line of HUD text at the given screen position."""
        surface = self.hud_font.render(text, True, settings.HUD_TEXT_COLOUR)
        self.screen.blit(surface, position)

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
