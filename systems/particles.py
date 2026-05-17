"""Particle effects — short-lived specks that add visual 'juice'.

A particle is just a tiny coloured dot that flies outward, shrinks and
fades away. Bursts of them are spawned when monsters die or arrows hit.
Particles are purely decorative — they never affect the game.
"""

import math
import random

import pygame


class Particle:
    """One short-lived speck flying in a straight line."""

    def __init__(self, x, y, vx, vy, life, colour, size):
        self.x = x
        self.y = y
        self.vx = vx          # speed sideways, in pixels per second
        self.vy = vy          # speed up/down
        self.life = life      # seconds of life remaining
        self.max_life = life
        self.colour = colour
        self.size = size

    @property
    def alive(self):
        """True while the particle still has life left."""
        return self.life > 0

    def update(self, dt):
        """Drift along, and use up a little life."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        """Draw the particle — it shrinks as its life runs out."""
        fraction = self.life / self.max_life
        radius = max(1, int(self.size * fraction))
        pygame.draw.circle(surface, self.colour,
                           (int(self.x), int(self.y)), radius)


class ParticleSystem:
    """Holds all the particles and updates / draws them together."""

    def __init__(self):
        self.particles = []

    def burst(self, x, y, colour, count=12, speed=160, life=0.5, size=5):
        """Spawn `count` particles flying outward from the point (x, y)."""
        for _ in range(count):
            # A random direction, and a random speed up to `speed`.
            angle = random.uniform(0, 2 * math.pi)
            this_speed = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * this_speed
            vy = math.sin(angle) * this_speed
            this_life = life * random.uniform(0.6, 1.0)
            self.particles.append(
                Particle(x, y, vx, vy, this_life, colour, size))

    def update(self, dt):
        """Move every particle and forget the ones that have faded away."""
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        """Draw every particle."""
        for particle in self.particles:
            particle.draw(surface)
