"""The Game class — it owns the window and runs the main game loop.

Every game is the same three steps repeated very fast:
    1. handle events  (what did the player press?)
    2. update         (move everything a tiny bit)
    3. draw           (paint the new picture)
Do that 60 times a second and it looks like smooth motion.
"""

import pygame

import settings
from entities.hero import Hero
from entities.heart import Heart
from entities.monster import Monster
from world.dungeon import Dungeon
from world import pathfinding


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

        # Spawn one monster and use A* to plan its route to the heart.
        self.monsters = []
        self._spawn_monster()

        # The game ends when the heart is destroyed.
        self.game_over = False
        self.font = pygame.font.Font(None, 110)

    def _spawn_monster(self):
        """Create a monster at the spawn point and give it a path."""
        spawn = self.dungeon.monster_spawn_tile
        spawn_px, spawn_py = self.dungeon.tile_centre_pixels(*spawn)
        monster = Monster(
            spawn_px - settings.MONSTER_SIZE // 2,
            spawn_py - settings.MONSTER_SIZE // 2,
        )
        path = pathfinding.find_path(
            self.dungeon, spawn, self.dungeon.heart_tile,
        )
        monster.set_path(path)
        self.monsters.append(monster)

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

    def update(self, dt):
        """Move everything forward by one frame."""
        # Once the game is over, nothing moves any more.
        if self.game_over:
            return

        self.hero.update(dt, self.dungeon, self.monsters)
        for monster in self.monsters:
            monster.update(dt, self.dungeon, self.heart)

        # Forget any monsters the hero has killed.
        self.monsters = [m for m in self.monsters if m.is_alive]

        # If the heart's HP has run out, the game is over.
        if not self.heart.is_alive:
            self.game_over = True

    def draw(self):
        """Paint the whole screen for this frame."""
        self.screen.fill(settings.FLOOR_COLOUR)
        self._draw_grid()
        self.dungeon.draw(self.screen)    # rocks and doors on top of the grid
        self.heart.draw(self.screen)      # the heart at the centre
        for monster in self.monsters:     # monsters marching in
            monster.draw(self.screen)
        self.hero.draw(self.screen)       # the knight on top of everything

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()   # show the finished picture

    def _draw_game_over(self):
        """Cover the screen with a big 'GAME OVER' message."""
        text = self.font.render("GAME OVER", True, settings.GAME_OVER_COLOUR)
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
