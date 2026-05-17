"""Pathfinding — the A* algorithm.

A* (said "A-star") finds the SHORTEST route between two tiles on the grid.
Monsters use it to work out how to reach the heart through the dungeon.

How it works, in plain English:
  - Start at the monster's tile. Keep a list of tiles "to explore".
  - Always explore the most promising tile next. A tile is promising when
    (steps taken to reach it) + (rough guess of steps still to go) is small.
  - That guess is the HEURISTIC. Here it is the Manhattan distance — how
    many tiles away the goal is if you could only move up/down/left/right.
  - Remember which tile we came from for every tile we reach. Once we hit
    the goal, follow those "came from" links backwards to read the route.
"""

import heapq

from world import tile


def _heuristic(a, b):
    """Rough distance guess between tiles a and b (Manhattan distance)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbours(dungeon, position):
    """The up/down/left/right tiles a monster could step to from here."""
    (x, y) = position
    result = []
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx = x + dx
        ny = y + dy
        if dungeon.in_bounds(nx, ny):
            if not tile.blocks_path(dungeon.get_tile(nx, ny)):
                result.append((nx, ny))
    return result


def find_path(dungeon, start, goal):
    """Return the list of tiles from start to goal, or [] if none exists.

    The list includes both the start tile and the goal tile.
    """
    if start == goal:
        return [start]

    # The "to explore" list, kept sorted by most-promising-first.
    frontier = [(0, start)]
    # For each tile we reached, the tile we came from.
    came_from = {start: None}
    # For each tile we reached, how many steps it took to get there.
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in _neighbours(dungeon, current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + _heuristic(nxt, goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    if goal not in came_from:
        return []   # the goal could not be reached

    # Follow the "came from" links backwards from the goal to the start.
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path
