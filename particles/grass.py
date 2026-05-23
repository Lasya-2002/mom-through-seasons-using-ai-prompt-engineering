import pygame
import math
import random

# ─────────────────────────────────────────────────────────────────────────────
#  particles/grass.py
#
#  Usage in main.py:
#      from particles.grass import GrassLayer
#      grass = GrassLayer(WIDTH, HEIGHT, ground_y=HEIGHT - 40)
#      grass.draw(screen)          # draw every frame (no update needed)
#      grass.update(dt)            # optional — animates gentle wind sway
# ─────────────────────────────────────────────────────────────────────────────


class GrassBlade:
    """One blade of grass drawn as a curved Bézier-approximated arc."""

    def __init__(self, x, ground_y, layer):
        self.base_x   = x
        self.ground_y = ground_y
        self.layer    = layer   # 0 = back (shorter, darker), 1 = front (taller, brighter)

        # Geometry
        self.height   = random.randint(12, 32) if layer == 0 else random.randint(22, 48)
        self.lean     = random.uniform(-0.5, 0.5)   # natural lean angle in radians
        self.thickness = 1 if layer == 0 else random.choice([1, 2])

        # Color — back layer darker, front lighter
        if layer == 0:
            g = random.randint(90, 130)
            self.color = (20, g, 30)
            self.tip_color = (40, g + 20, 50)
        else:
            g = random.randint(130, 180)
            self.color = (30, g, 50)
            self.tip_color = (80, g + 30, 80)

        # Wind sway
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_amp   = random.uniform(0.05, 0.18)   # extra lean from wind
        self.sway_freq  = random.uniform(0.5, 1.2)

    def draw(self, surface, wind_time):
        """Draw this blade with a simple 3-segment approximation of a curve."""
        # Total lean = natural + wind
        wind_lean = math.sin(wind_time * self.sway_freq + self.sway_phase) * self.sway_amp
        total_lean = self.lean + wind_lean

        h  = self.height
        bx = self.base_x
        by = self.ground_y

        # Compute tip
        tip_x = bx + math.sin(total_lean) * h
        tip_y = by - math.cos(total_lean) * h

        # Control point for the curve (mid-point pushed in lean direction)
        ctrl_x = bx + math.sin(total_lean) * h * 0.55 + math.cos(total_lean) * h * 0.18
        ctrl_y = by - math.cos(total_lean) * h * 0.55 + math.sin(total_lean) * h * 0.10

        # 6-segment Bézier approximation
        steps = 6
        prev  = (bx, by)
        for i in range(1, steps + 1):
            t  = i / steps
            # Quadratic Bézier
            x  = (1-t)**2 * bx + 2*(1-t)*t * ctrl_x + t**2 * tip_x
            y  = (1-t)**2 * by + 2*(1-t)*t * ctrl_y + t**2 * tip_y
            # Blend color from base → tip
            r  = int(self.color[0] + (self.tip_color[0] - self.color[0]) * t)
            g  = int(self.color[1] + (self.tip_color[1] - self.color[1]) * t)
            b  = int(self.color[2] + (self.tip_color[2] - self.color[2]) * t)
            pygame.draw.line(surface, (r, g, b),
                             (int(prev[0]), int(prev[1])),
                             (int(x), int(y)), self.thickness)
            prev = (x, y)


class GrassLayer:
    """
    Two layers of grass blades packed along the ground line.
    Back layer: shorter, denser, darker (creates depth).
    Front layer: taller, sparser, brighter.
    Also draws a solid ground strip below ground_y.
    """

    def __init__(self, screen_w, screen_h, ground_y):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.ground_y = ground_y
        self.elapsed  = 0.0

        # Ground strip colors
        self.ground_top    = (30, 100, 40)
        self.ground_bottom = (15,  55, 20)

        # Back layer — dense
        spacing_back = 5
        self.back_blades = [
            GrassBlade(x + random.randint(-3, 3), ground_y, layer=0)
            for x in range(0, screen_w, spacing_back)
        ]

        # Front layer — sparser, taller
        spacing_front = 9
        self.front_blades = [
            GrassBlade(x + random.randint(-4, 4), ground_y, layer=1)
            for x in range(0, screen_w, spacing_front)
        ]

    def update(self, dt):
        self.elapsed += dt

    def draw(self, surface):
        # ── Ground fill strip ──────────────────────────────────────────────
        strip_h = self.screen_h - self.ground_y
        for y in range(strip_h):
            t = y / max(strip_h - 1, 1)
            r = int(self.ground_top[0] + (self.ground_bottom[0] - self.ground_top[0]) * t)
            g = int(self.ground_top[1] + (self.ground_bottom[1] - self.ground_top[1]) * t)
            b = int(self.ground_top[2] + (self.ground_bottom[2] - self.ground_top[2]) * t)
            pygame.draw.line(surface, (r, g, b),
                             (0, self.ground_y + y),
                             (self.screen_w, self.ground_y + y))

        wt = self.elapsed   # wind time

        # ── Back blades (drawn first — behind flowers) ─────────────────────
        for blade in self.back_blades:
            blade.draw(surface, wt)

        # ── Front blades (drawn after flowers — in front) ──────────────────
        # Call draw_front() separately from main.py if you want flowers
        # sandwiched between layers. For simplicity, all grass draws here.
        for blade in self.front_blades:
            blade.draw(surface, wt)
