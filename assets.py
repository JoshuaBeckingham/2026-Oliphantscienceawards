"""Loading image files (sprites) from the Art folder.

Paths are built relative to THIS file, so the game works no matter which
folder it is launched from — important when the project moves to the Pi.
"""

import pathlib

import pygame

# The Art folder sits next to this file, in the project root.
ART_DIR = pathlib.Path(__file__).resolve().parent / "Art"


def load_sprite(filename, height):
    """Load Art/<filename> and scale it to `height` pixels tall.

    The width is scaled to match, so the picture keeps its proportions.
    """
    path = ART_DIR / filename
    image = pygame.image.load(str(path)).convert_alpha()
    scale = height / image.get_height()
    width = round(image.get_width() * scale)
    return pygame.transform.scale(image, (width, height))
