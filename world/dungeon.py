"""The dungeon — a randomly generated grid of rooms, corridors and doors.

This is PROCEDURAL GENERATION. The algorithm:
  1. Fill the whole map with solid rock.
  2. Carve out several rooms (rectangles) that do not overlap.
  3. Join the rooms together with 1-tile-wide corridors.
  4. Drop a door wherever a corridor punches through a room wall.
Every run gives a different dungeon.
"""

import random

import pygame

import settings
from world import tile


def _between(a, b):
    """Every whole number from a to b, in order — works either direction."""
    if a <= b:
        return range(a, b + 1)
    return range(a, b - 1, -1)


def _tile_distance_squared(p, q):
    """Rough distance between two tiles (skips the slow square root)."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


class Room:
    """A rectangle of floor inside the dungeon."""

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def centre(self):
        """The middle tile of the room, as (x, y)."""
        return (self.x + self.w // 2, self.y + self.h // 2)

    def contains(self, tx, ty):
        """True if tile (tx, ty) is inside this room."""
        return (self.x <= tx < self.x + self.w
                and self.y <= ty < self.y + self.h)

    def overlaps(self, other, padding=1):
        """True if this room is too close to another room.

        padding keeps a gap of solid rock between rooms, so they get walls.
        """
        return (self.x - padding < other.x + other.w
                and self.x + self.w + padding > other.x
                and self.y - padding < other.y + other.h
                and self.y + self.h + padding > other.y)


class Dungeon:
    """Holds the tile grid and knows how to build, query and draw it."""

    def __init__(self):
        self.width = settings.GRID_WIDTH
        self.height = settings.GRID_HEIGHT
        self.rooms = []
        self.grid = self._generate()

        # The heart sits in the middle of the first (central) room.
        self.heart_tile = self.rooms[0].centre
        # The hero starts a couple of tiles from the heart, on open floor.
        hx, hy = self.heart_tile
        self.spawn_tile = (hx - 2, hy)

    # --- Building the map ---------------------------------------------

    def _generate(self):
        """Build a fresh random dungeon and return its tile grid."""
        # 1. Solid rock everywhere.
        grid = [[tile.ROCK for _ in range(self.width)]
                for _ in range(self.height)]

        # 2a. A fixed central room — this is the heart's room.
        cx = self.width // 2
        cy = self.height // 2
        self.rooms.append(Room(cx - 3, cy - 2, 7, 5))

        # 2b. Try to drop more rooms at random spots without overlapping.
        for _ in range(settings.ROOM_ATTEMPTS):
            if len(self.rooms) >= settings.MAX_ROOMS:
                break
            w = random.randint(settings.ROOM_MIN_SIZE, settings.ROOM_MAX_SIZE)
            h = random.randint(settings.ROOM_MIN_SIZE, settings.ROOM_MAX_SIZE)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            room = Room(x, y, w, h)
            if not any(room.overlaps(other) for other in self.rooms):
                self.rooms.append(room)

        # 3. Carve every room's floor.
        for room in self.rooms:
            for ty in range(room.y, room.y + room.h):
                for tx in range(room.x, room.x + room.w):
                    grid[ty][tx] = tile.FLOOR

        # 4. Join each room to the nearest earlier room with a corridor.
        connections = []
        for i in range(1, len(self.rooms)):
            room = self.rooms[i]
            nearest = min(
                self.rooms[:i],
                key=lambda r: _tile_distance_squared(r.centre, room.centre),
            )
            path = self._corridor_path(nearest.centre, room.centre)
            for (tx, ty) in path:
                if grid[ty][tx] == tile.ROCK:
                    grid[ty][tx] = tile.FLOOR
            connections.append((path, nearest, room))

        # 5. Place a door where each corridor leaves / enters a room.
        for path, room_a, room_b in connections:
            for (dx, dy) in self._doorway_tiles(path, room_a, room_b):
                if grid[dy][dx] == tile.FLOOR:
                    grid[dy][dx] = tile.DOOR_CLOSED

        return grid

    def _corridor_path(self, start, end):
        """An ordered list of tiles forming an L-shaped path start -> end."""
        (ax, ay) = start
        (bx, by) = end
        path = []
        if random.random() < 0.5:
            # Go across first, then down.
            for x in _between(ax, bx):
                path.append((x, ay))
            for y in _between(ay, by):
                path.append((bx, y))
        else:
            # Go down first, then across.
            for y in _between(ay, by):
                path.append((ax, y))
            for x in _between(ax, bx):
                path.append((x, by))
        return path

    def _doorway_tiles(self, path, room_a, room_b):
        """Find where a corridor crosses each room's wall — the door spots."""
        doors = []
        # Walking out of room A: the first path tile that is outside A.
        for (tx, ty) in path:
            if not room_a.contains(tx, ty):
                doors.append((tx, ty))
                break
        # Walking in from room B's end: the first tile outside B.
        for (tx, ty) in reversed(path):
            if not room_b.contains(tx, ty):
                doors.append((tx, ty))
                break
        return doors

    # --- Asking questions about the map -------------------------------

    def in_bounds(self, x, y):
        """True if tile (x, y) is actually on the map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x, y):
        """The tile type at (x, y). Anything off the map counts as rock."""
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return tile.ROCK

    def is_blocked(self, rect):
        """True if a pixel rectangle overlaps any blocking tile.

        Used for collision: the hero asks "if I move here, do I hit a wall?"
        """
        ts = settings.TILE_SIZE
        left = rect.left // ts
        right = (rect.right - 1) // ts
        top = rect.top // ts
        bottom = (rect.bottom - 1) // ts
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if tile.blocks_movement(self.get_tile(tx, ty)):
                    return True
        return False

    def tile_centre_pixels(self, tx, ty):
        """The pixel position of the centre of tile (tx, ty)."""
        ts = settings.TILE_SIZE
        return (tx * ts + ts // 2, ty * ts + ts // 2)

    # --- Doors --------------------------------------------------------

    def toggle_door_near(self, px, py):
        """Open or close a door next to pixel point (px, py).

        Only the four tiles beside the point are checked — never the tile
        the point is on — so the hero can't shut a door on top of himself.
        Returns True if a door was toggled.
        """
        ts = settings.TILE_SIZE
        here_x = px // ts
        here_y = py // ts
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx = here_x + dx
            ty = here_y + dy
            if not self.in_bounds(tx, ty):
                continue
            current = self.grid[ty][tx]
            if current == tile.DOOR_CLOSED:
                self.grid[ty][tx] = tile.DOOR_OPEN
                return True
            if current == tile.DOOR_OPEN:
                self.grid[ty][tx] = tile.DOOR_CLOSED
                return True
        return False

    # --- Drawing ------------------------------------------------------

    def draw(self, surface):
        """Draw every rock, wall and door. Floor is left as the background."""
        ts = settings.TILE_SIZE
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.grid[y][x]
                if tile_type == tile.FLOOR:
                    continue   # nothing to draw — the background is floor

                rect = pygame.Rect(x * ts, y * ts, ts, ts)
                if tile_type == tile.ROCK:
                    pygame.draw.rect(surface, settings.ROCK_COLOUR, rect)
                    pygame.draw.rect(surface, settings.ROCK_EDGE_COLOUR, rect, 2)
                elif tile_type == tile.WALL:
                    pygame.draw.rect(surface, settings.WALL_COLOUR, rect)
                elif tile_type == tile.DOOR_CLOSED:
                    self._draw_door(surface, rect, is_open=False)
                elif tile_type == tile.DOOR_OPEN:
                    self._draw_door(surface, rect, is_open=True)

    def _draw_door(self, surface, rect, is_open):
        """Draw a door tile: a stone frame with the wooden door inside it."""
        # The dark stone frame fills the whole tile.
        pygame.draw.rect(surface, settings.DOOR_FRAME_COLOUR, rect)
        inner = rect.inflate(-6, -6)

        if is_open:
            # Floor shows through, with the door folded thin against one side.
            pygame.draw.rect(surface, settings.FLOOR_COLOUR, inner)
            leaf = pygame.Rect(inner.x, inner.y, 6, inner.height)
            pygame.draw.rect(surface, settings.DOOR_WOOD_COLOUR, leaf)
        else:
            # A solid wooden door, with a little handle near one edge.
            pygame.draw.rect(surface, settings.DOOR_WOOD_COLOUR, inner)
            pygame.draw.rect(surface, settings.DOOR_FRAME_COLOUR, inner, 2)
            handle = (inner.right - 7, inner.centery)
            pygame.draw.circle(surface, settings.DOOR_HANDLE_COLOUR, handle, 3)
