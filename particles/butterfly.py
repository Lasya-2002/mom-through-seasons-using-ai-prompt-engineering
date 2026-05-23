import pygame
import math
import random

class Butterfly:
    """
    A small delicate butterfly that:
      • Wanders lazily across the screen in a sine-wave path
      • Flaps wings with a smooth open/close cycle
      • Has two wing pairs (upper larger, lower smaller) with subtle vein lines
      • Wraps around screen edges
    """

    # Wing color palettes  (upper_outer, upper_inner, lower_outer, body)
    PALETTES = [
        # Monarch-ish warm
        ((255, 160,  60), (255, 210, 120), (220, 120,  40), ( 40,  20,  10)),
        # Soft pink
        ((255, 180, 200), (255, 220, 230), (230, 140, 170), ( 80,  30,  50)),
        # Blue morpho-ish
        ((120, 180, 255), (180, 220, 255), ( 80, 140, 220), ( 20,  20,  60)),
        # Lavender
        ((200, 160, 230), (230, 200, 250), (170, 120, 200), ( 60,  20,  80)),
        # Pale yellow
        ((240, 230, 120), (255, 245, 180), (210, 190,  80), ( 50,  40,  10)),
        # White
        ((240, 240, 250), (255, 255, 255), (210, 210, 230), ( 60,  60,  80)),
    ]

    def __init__(self, screen_w, screen_h, ground_y=None):
        self.sw = screen_w
        self.sh = screen_h
        # Butterflies fly in the upper 2/3 of screen, above the flowers
        self.ground_y = ground_y if ground_y else int(screen_h * 0.72)

        self._reset(initial=True)

    def _reset(self, initial=False):
        self.x = random.uniform(0, self.sw)
        if initial:
            self.y = random.uniform(self.sh * 0.10, self.ground_y - 60)
        else:
            # Re-enter from a random edge
            edge = random.choice(["left", "right", "top"])
            if edge == "left":
                self.x, self.y = -20, random.uniform(self.sh * 0.08, self.ground_y - 60)
            elif edge == "right":
                self.x, self.y = self.sw + 20, random.uniform(self.sh * 0.08, self.ground_y - 60)
            else:
                self.x, self.y = random.uniform(0, self.sw), -20

        # Flight direction & speed
        self.speed     = random.uniform(38, 75)
        self.dir_angle = random.uniform(0, math.pi * 2)   # radians
        # Gentle wandering
        self.wander_speed = random.uniform(0.4, 0.9)   # rad/s turn rate
        self.wander_phase = random.uniform(0, math.pi * 2)

        # Vertical sine bob
        self.bob_amp   = random.uniform(6, 16)
        self.bob_freq  = random.uniform(1.2, 2.2)
        self.bob_phase = random.uniform(0, math.pi * 2)
        self.base_y    = self.y

        # Wing flap
        self.flap_freq  = random.uniform(3.0, 5.5)   # flaps per second
        self.flap_phase = random.uniform(0, math.pi * 2)
        self.flap_angle = 0.0   # 0 = fully open, pi/2 = closed

        # Size
        self.scale = random.uniform(0.7, 1.3)

        # Palette
        pal = random.choice(self.PALETTES)
        self.col_uo = pal[0]   # upper outer
        self.col_ui = pal[1]   # upper inner
        self.col_lo = pal[2]   # lower outer
        self.col_bd = pal[3]   # body

        self.elapsed = 0.0

    # ── helpers ──────────────────────────────────────────────────────────────

    def _wing_polygon(self, cx, cy, side, flap_cos, scale,
                      upper=True):
        """
        Build one wing (upper or lower) on the given side (-1=left, +1=right).
        flap_cos: cosine of flap angle — controls how open the wing is.
        Returns a list of (x, y) integer tuples.
        """
        # Wing is an ellipse-ish shape; we build it in local space then transform.
        # Upper wing: larger teardrop
        # Lower wing: smaller rounded triangle

        if upper:
            pts_local = [
                ( 0,  0),
                ( 2, -8),
                ( 7,-14),
                (13,-14),
                (17, -9),
                (17, -2),
                (14,  5),
                ( 8,  8),
                ( 2,  5),
            ]
            # Scale
            pts_local = [(p[0]*scale*1.6, p[1]*scale*1.6) for p in pts_local]
        else:
            pts_local = [
                ( 0,  0),
                ( 2,  4),
                ( 8, 10),
                (13, 10),
                (15,  5),
                (13,  0),
                ( 7, -3),
            ]
            pts_local = [(p[0]*scale*1.3, p[1]*scale*1.3) for p in pts_local]

        # Flip x for left side
        if side == -1:
            pts_local = [(-p[0], p[1]) for p in pts_local]

        # Apply flap: compress x by flap_cos (wing folds toward center)
        pts_local = [(p[0] * abs(flap_cos), p[1]) for p in pts_local]

        # Translate to butterfly center
        return [(int(cx + p[0]), int(cy + p[1])) for p in pts_local]

    def _lerp_color(self, c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    # ── public API ───────────────────────────────────────────────────────────

    def update(self, dt):
        self.elapsed += dt

        # Wandering direction change
        wander = math.sin(self.elapsed * self.wander_speed + self.wander_phase)
        self.dir_angle += wander * 1.2 * dt

        # Move
        self.x += math.cos(self.dir_angle) * self.speed * dt
        # Vertical bob relative to a slowly drifting base_y
        self.base_y += math.sin(self.dir_angle) * self.speed * 0.3 * dt
        self.base_y  = max(self.sh * 0.06, min(self.ground_y - 50, self.base_y))
        self.y = self.base_y + math.sin(
            self.elapsed * self.bob_freq + self.bob_phase) * self.bob_amp

        # Wing flap angle
        self.flap_angle = self.elapsed * self.flap_freq * math.pi * 2 + self.flap_phase

        # Wrap / reset when offscreen
        if self.x < -60 or self.x > self.sw + 60 or self.y < -60:
            self._reset(initial=False)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        flap_cos = math.cos(self.flap_angle)
        sc = self.scale

        # Draw both sides
        for side in (-1, 1):
            # Upper wing
            upper_pts = self._wing_polygon(cx, cy, side, flap_cos, sc, upper=True)
            if len(upper_pts) >= 3:
                pygame.draw.polygon(surface, self.col_uo, upper_pts)
                # Inner lighter patch
                inner_pts = self._wing_polygon(cx, cy, side, flap_cos * 0.85,
                                               sc * 0.55, upper=True)
                if len(inner_pts) >= 3:
                    pygame.draw.polygon(surface, self.col_ui, inner_pts)
                # Outline
                pygame.draw.polygon(surface, self.col_bd, upper_pts, 1)

            # Lower wing
            lower_pts = self._wing_polygon(cx, cy, side, flap_cos, sc, upper=False)
            if len(lower_pts) >= 3:
                pygame.draw.polygon(surface, self.col_lo, lower_pts)
                pygame.draw.polygon(surface, self.col_bd, lower_pts, 1)

        # Body — thin oval
        body_h = int(10 * sc)
        body_w = max(2, int(2.5 * sc))
        pygame.draw.ellipse(surface, self.col_bd,
                            (cx - body_w, cy - body_h // 2,
                             body_w * 2, body_h))

        # Antennae
        ant_len = int(7 * sc)
        for side in (-1, 1):
            tip_x = cx + side * int(3 * sc * abs(flap_cos))
            tip_y = cy - body_h // 2 - ant_len
            pygame.draw.line(surface, self.col_bd,
                             (cx, cy - body_h // 2),
                             (tip_x, tip_y), 1)
            # Tiny dot at tip
            pygame.draw.circle(surface, self.col_bd, (tip_x, tip_y), max(1, int(1.5 * sc)))
