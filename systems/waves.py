"""The wave system — decides what monsters spawn, and when.

Monsters arrive in WAVES. Each wave has more monsters than the last, and
they are tougher (more HP). From ORC_FIRST_WAVE onward, some of the
monsters are orcs instead of goblins. The monsters of a wave are spawned
a few at a time, so they trickle into the dungeon instead of appearing
all at once.
"""

import random

import settings
from entities.monster import Goblin, Orc
from world import pathfinding


class WaveManager:
    """Keeps track of the current wave and spawns its monsters over time."""

    def __init__(self, dungeon):
        self.dungeon = dungeon
        self.wave_number = 0       # 0 means no wave has started yet
        self.spawn_queue = []      # the monster kinds still to appear
        self.spawn_timer = 0.0     # seconds until the next monster appears

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

    @property
    def to_spawn(self):
        """How many monsters of this wave have not appeared yet."""
        return len(self.spawn_queue)

    @property
    def wave_fully_spawned(self):
        """True once every monster in the wave has been spawned."""
        return not self.spawn_queue

    def start_wave(self):
        """Begin the next wave: build its list of monsters to spawn."""
        self.wave_number += 1
        self.spawn_queue = self._build_wave(self.wave_number)
        self.spawn_timer = 0.0   # the first monster appears straight away

    def _build_wave(self, wave):
        """Decide the kind of each monster in the wave (goblin or orc)."""
        queue = []
        for i in range(self.monsters_in_wave(wave)):
            # From ORC_FIRST_WAVE on, every third monster is an orc.
            if wave >= settings.ORC_FIRST_WAVE and i % 3 == 2:
                queue.append("orc")
            else:
                queue.append("goblin")
        return queue

    def update(self, dt, monsters):
        """Drip-feed the wave's monsters into the `monsters` list."""
        if self.wave_fully_spawned:
            return
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            kind = self.spawn_queue.pop(0)
            monsters.append(self._make_monster(kind))
            self.spawn_timer = settings.WAVE_SPAWN_GAP

    def _make_monster(self, kind):
        """Create one monster of the given kind, with a path to the heart."""
        spawn_x, spawn_y = self.dungeon.tile_centre_pixels(*self.spawn_tile)
        # Later waves make every monster tougher.
        hp_bonus = (self.wave_number - 1) * settings.WAVE_HP_STEP

        if kind == "orc":
            size = settings.ORC_SIZE
            monster = Orc(spawn_x - size // 2, spawn_y - size // 2,
                          settings.ORC_MAX_HP + hp_bonus)
        else:
            size = settings.GOBLIN_SIZE
            monster = Goblin(spawn_x - size // 2, spawn_y - size // 2,
                             settings.GOBLIN_MAX_HP + hp_bonus)

        path = pathfinding.find_path(
            self.dungeon, self.spawn_tile, self.dungeon.heart_tile,
        )
        monster.set_path(path)
        return monster
