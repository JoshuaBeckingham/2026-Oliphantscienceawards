# Dungeon Defenders

A 2D tower-defense roguelike where a hero explores a randomly generated dungeon, collects resources, builds defenses, and fights waves of monsters trying to destroy the heart of the dungeon.

Built in Python with Pygame. Prototyped on PC in VS Code, then ported to Raspberry Pi.

---

## The Game

You are the last defender of an ancient dungeon. Each round has two phases:

1. **Build Phase** — Explore the dungeon, mine rocks for stone, collect gold piles, and place walls, towers, and traps to funnel monsters into kill zones.
2. **Defense Phase** — A wave of monsters spawns at the dungeon entrance and marches toward the heart. Your hero fights alongside the defenses you built. Survive the wave and you earn gold, then back to building for the next, harder wave.

The game ends when the heart's HP reaches zero. Your score is the number of waves you survived.

---

## Game Elements

### The Hero (player)
- Moves with arrow keys, attacks with spacebar
- Has HP — respawns at the heart when killed (loses some gold as penalty)

### The Heart
- Sits in the centre of the dungeon
- Has HP — game over when it reaches zero
- This is what the monsters are trying to destroy

### Resources
- **Gold** — earned from killing monsters, spent on towers and traps
- **Stone** — mined from rocks during the build phase, used to build walls

### Buildables
- **Wall** — cheap, blocks the path, has HP. Used to shape where monsters walk.
- **Arrow Tower** — automatically shoots the nearest enemy
- **Spike Trap** — damages anything that walks over it

### Monsters
- **Goblin** — fast, weak (wave 1+)
- **Orc** — slow, tough (wave 3+)
- **Boss** — appears every 5th wave

Each wave has more monsters, more HP, and eventually new types.

---

## Project Structure

```
dungeon_defender/
├── main.py              # Entry point — starts the game
├── settings.py          # All tunable numbers (screen size, colours, speeds)
├── game.py              # Main game loop, manages phases
│
├── entities/            # Things that exist in the world
│   ├── entity.py        # Base class (position + HP)
│   ├── hero.py          # The player
│   ├── monster.py       # Goblin, orc, boss
│   ├── heart.py         # What you defend
│   └── projectile.py    # Arrows from towers
│
├── buildables/          # Things you place
│   ├── wall.py
│   ├── tower.py
│   └── trap.py
│
├── world/               # The dungeon itself
│   ├── dungeon.py       # Random map generator
│   ├── tile.py          # Floor, rock, wall tiles
│   └── pathfinding.py   # How monsters find the heart
│
├── systems/             # Background rules
│   ├── waves.py         # What spawns when
│   ├── economy.py       # Gold and stone tracking
│   └── ui.py            # HUD, build menu, wave counter
│
└── assets/              # Images and sounds (added later)
```

The folder layout itself is part of the lesson — *things that exist*, *things you build*, *rules that run in the background*.

---

## Build Roadmap

Each step ends in a working, playable game. Save a copy (or commit to Git) at the end of each step so progress is visible.

1. **Window, grid, hero that moves** — foundation
2. **Random dungeon with rocks and the heart** in the middle
3. **Rooms-and-corridors dungeon with doors** — explore, blocked by rock, open doors with E
4. **One monster spawns and walks toward the heart** (pathfinding!)
5. **Hero attacks monsters, monsters attack the heart**
6. **Wave system** — 3 monsters → next wave → 5 monsters → harder
7. **Gold drops + buy menu + arrow tower**
8. **Spike trap, orc enemy, HUD** (wave / gold / HP)
9. **Boss waves, game over screen, high score**
10. **Polish** — sprites, sounds, particle effects

Coloured squares are fine right up to step 10. Don't get distracted by art until the gameplay works.

---

## Tech Stack

- **Python 3.11+**
- **Pygame** — the standard Python 2D game library
- **VS Code** for development (Microsoft Python extension)
- **Git** for version control
- Target: **Raspberry Pi 4 / Pi 5** running Raspberry Pi OS

### Why this stack
Pygame is pure Python, so the game runs identically on Windows, Mac, Linux, and the Pi. "Porting" is really just copying the folder across.

---

## Setup (Development Machine)

```bash
# In the project folder
python -m venv venv

# Activate the virtual environment
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows

# Install dependencies
pip install pygame

# Run the game
python main.py
```

In VS Code: open the project folder, select the `venv` interpreter (bottom-right of the window), and press **F5** to run with the debugger.

---

## Porting to Raspberry Pi

```bash
# On the Pi
sudo apt update
sudo apt install python3-pygame git

# Get the project
git clone <your-repo>     # or copy via USB / scp
cd dungeon_defender
python3 main.py
```

### Portability rules (follow from day one)
- Use **relative paths** only: `assets/hero.png`, never `C:/Users/...`
- Use `os.path.join` or `pathlib.Path` for file paths
- Don't hard-code screen size to a specific monitor
- Keep a `requirements.txt` so the Pi install is one command

---

## Computer Science Concepts (for the science project writeup)

Three big ideas, all visible in the running game:

1. **Procedural Generation** — the dungeon is built by an algorithm with rules, so every game is different
2. **Pathfinding (A\*)** — how monsters figure out the shortest route to the heart
3. **State Machines** — the game switches between Build Phase and Defense Phase based on simple rules

Bonus concepts that show up naturally:
- **Object-oriented programming** — entities inherit from a base class
- **Modular code** — each concept lives in its own file
- **Version control** — Git history shows the project growing step by step

---

## Controls (planned)

| Key | Action |
|-----|--------|
| Arrow keys | Move hero |
| Space | Attack |
| 1 / 2 / 3 | Select wall / tower / trap (build phase) |
| Left click | Place selected buildable |
| E | Open / close a door (when next to one) |
| Enter | End build phase early, start the wave |
| Esc | Pause / quit |

---

## Status

🛠️ **In development** — Steps 1–3 complete (window, procedural dungeon, doors). Step 4 next: a monster that pathfinds to the heart.
