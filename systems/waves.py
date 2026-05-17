"""The wave system — decides what monsters spawn, and when.

Monsters arrive in WAVES. Each wave has more monsters than the last, and
they are tougher (more HP). The monsters of a wave are spawned a few at a
time, so they trickle into the dungeon instead of appearing in one clump.
"""

import random

import settings
from entities.monster import Monster
from world import pathfinding


class WaveManager:
    """Keeps track of the current wave and spawns its monsters over time."""

    def __init__(self, dungeon):
        self.dungeon = dungeon
        self.wave_number = 0     # 0 means no wave has started yet
        self.to_spawn = 0        # how many monsters still to appear this wave
        self.spawn_timer = 0.0   # seconds until the next monster appears

        # Which room the next wave's monsters come from. Picked fresh each
        # wave so they arrive from a different direction every time.
        self.spawn_tile = None
        self.choose_spawn_room()

    def choose_spawn_room(self):
        """Pick the room the next wave's monsters will come from.

        A different room from the last wave, whenever there is a choice.
        """
        options = self.dungeon.spawn_tiles
        fresh = [tile for tile in options if tile != self.spawn_tile]
        self.spawn_tile = random.choice(fresh if fresh else options)

    def monsters_in_wave(self, wave):
        """How many monsters wave number `wave` contains."""
        return (settings.WAVE_BASE_MONSTERS
                + (wave - 1) * settings.WAVE_MONSTER_STEP)

    def monster_hp_for_wave(self, wave):
        """How much HP each monster in wave number `wave` has."""
        return settings.MONSTER_MAX_HP + (wave - 1) * settings.WAVE_HP_STEP

    def start_wave(self):
        """Begin the next wave."""
        self.wave_number += 1
        self.to_spawn = self.monsters_in_wave(self.wave_number)
        self.spawn_timer = 0.0   # the first monster appears straight away

    @property
    def wave_fully_spawned(self):
        """True once every monster in the wave has been spawned."""
        return self.to_spawn <= 0

    def update(self, dt, monsters):
        """Drip-feed the wave's monsters into the `monsters` list."""
        if self.wave_fully_spawned:
            return
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            monsters.append(self._make_monster())
            self.to_spawn -= 1
            self.spawn_timer = settings.WAVE_SPAWN_GAP

    def _make_monster(self):
        """Create one monster at the spawn point, with a path to the heart."""
        spawn_tile = self.spawn_tile
        spawn_x, spawn_y = self.dungeon.tile_centre_pixels(*spawn_tile)
        hp = self.monster_hp_for_wave(self.wave_number)
        monster = Monster(
            spawn_x - settings.MONSTER_SIZE // 2,
            spawn_y - settings.MONSTER_SIZE // 2,
            hp,
        )
        path = pathfinding.find_path(
            self.dungeon, spawn_tile, self.dungeon.heart_tile,
        )
        monster.set_path(path)
        return monster
