"""Pixel-art sprite for the hero knight.

The knight is a tiny picture made of letters — each letter is one pixel.
KNIGHT_PALETTE says what colour each letter is. A '.' means "leave this
pixel see-through (transparent)".

Want to change how the knight looks? Just edit the picture below. Keep
every row the same width (18 characters) so the grid stays rectangular.
"""

import pygame

# The knight: 18 pixels wide, 20 pixels tall.
#   o = dark outline   s = steel    l = light steel   d = dark steel
#   g = gold           b = sword blade                c = shield (teal)
KNIGHT_PIXELS = [
    "...bb.............",
    "..obbo............",
    "..obbo............",
    "..obbo.oooooo.....",
    "..obbo.ollsso.....",
    "..obbo.odggdo.....",
    "..obbo.oggggo.....",
    "..obbo.odggdo.....",
    ".oggggoosddso.....",
    "..ossoollssllo....",
    "...ossoslsssoogggo",
    "...ossosslssoocgco",
    "...ossossslsoogggo",
    "......ogggggoocgco",
    "......odsssdo.ogo.",
    "......oso.oso..o..",
    "......oso.oso.....",
    "......olo.olo.....",
    ".....odso.osdo....",
    ".....oooo.oooo....",
]

# Which real colour each letter stands for (Red, Green, Blue).
KNIGHT_PALETTE = {
    "o": (26, 26, 34),      # near-black outline
    "s": (111, 125, 140),   # steel armour
    "l": (170, 182, 194),   # bright steel highlight
    "d": (63, 74, 87),      # steel shadow
    "g": (217, 161, 58),    # gold trim and crosses
    "b": (205, 214, 221),   # sword blade
    "c": (47, 79, 74),      # shield field (dark teal)
}


def build_surface():
    """Turn the letter-picture into a pygame image (a Surface).

    Done once when the hero is created — not every frame — so it's fast.
    """
    height = len(KNIGHT_PIXELS)
    width = max(len(row) for row in KNIGHT_PIXELS)

    # SRCALPHA lets the picture have see-through pixels.
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for row_index, row in enumerate(KNIGHT_PIXELS):
        for col_index, char in enumerate(row):
            colour = KNIGHT_PALETTE.get(char)
            if colour is not None:          # '.' is not in the palette
                surface.set_at((col_index, row_index), colour)

    return surface
