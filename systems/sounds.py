"""Sound effects — generated in code, so the game needs no audio files.

Each effect is a short tone built one sample at a time. A sound wave is
just numbers going up and down quickly; play 22050 of them a second and
the speaker makes a note. A tone can slide in pitch (a 'sweep'), and it
always fades out at the end so it does not click.
"""

import array
import math

import pygame

SAMPLE_RATE = 22050   # audio samples played per second


def _tone(frequency, duration, volume=0.4, sweep=0.0):
    """Build a Sound: a single tone lasting `duration` seconds.

    frequency — the starting pitch, in Hz (higher = higher note).
    sweep     — how far the pitch slides over the sound, in Hz.
    volume    — loudness, from 0.0 to 1.0.
    """
    sample_count = int(SAMPLE_RATE * duration)
    samples = array.array("h")   # 'h' = signed 16-bit whole numbers
    phase = 0.0
    for i in range(sample_count):
        progress = i / sample_count
        pitch = frequency + sweep * progress
        phase += 2 * math.pi * pitch / SAMPLE_RATE
        fade_out = 1.0 - progress           # quieter towards the end
        value = math.sin(phase) * volume * fade_out
        samples.append(int(value * 32767))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _sequence(notes):
    """Build one Sound that plays several notes one after another.

    notes — a list of (frequency, duration) pairs.
    """
    samples = array.array("h")
    for frequency, duration in notes:
        sample_count = int(SAMPLE_RATE * duration)
        phase = 0.0
        for i in range(sample_count):
            progress = i / sample_count
            phase += 2 * math.pi * frequency / SAMPLE_RATE
            fade_out = 1.0 - progress
            value = math.sin(phase) * 0.4 * fade_out
            samples.append(int(value * 32767))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class Sounds:
    """Builds the sound effects once, and plays them by name."""

    def __init__(self):
        # If the computer has no working audio, the mixer will not have
        # started — in that case the game simply runs silently.
        self.enabled = pygame.mixer.get_init() is not None
        self.effects = {}
        if not self.enabled:
            return

        self.effects = {
            "swing": _tone(620, 0.12, sweep=-340),     # sword swish
            "hit": _tone(240, 0.09, volume=0.5),       # an arrow lands
            "death": _tone(430, 0.22, sweep=-280),     # a monster dies
            "wave": _tone(320, 0.30, sweep=260),       # a wave begins
            "win": _sequence([(523, 0.15), (659, 0.15), (784, 0.32)]),
            "lose": _tone(300, 0.75, sweep=-170, volume=0.5),
        }

    def play(self, name):
        """Play the named sound effect, if sound is available."""
        sound = self.effects.get(name)
        if sound is not None:
            sound.play()
