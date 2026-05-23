import pygame
import math
import random

# ─────────────────────────────────────────────────────────────────────────────
#  particles/spring_flower.py
#  Drop into your  particles/  folder.
#
#  Usage (already in your main.py):
#      from particles.spring_flower import SpringFlower
#      flowers = [SpringFlower(300, 500), SpringFlower(600, 450), ...]
#      flower.update()
#      flower.draw(screen)
# ─────────────────────────────────────────────────────────────────────────────


def _bezier_curve(p0, p1, p2, steps=18):
    """Return points along a quadratic Bézier p0→p1(control)→p2."""
    pts = []
    for i in range(steps + 1):
        t  = i / steps
        x  = (1 - t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y  = (1 - t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        pts.append((x, y))
    return pts


def _rotate(cx, cy, px, py, angle_rad):
    """Rotate point (px, py) around (cx, cy)."""
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    dx, dy = px - cx, py - cy
    return (cx + dx*cos_a - dy*sin_a,
            cy + dx*sin_a + dy*cos_a)


def _surface_to_points(cx, cy, rx, ry, n=24):
    """Ellipse polygon for petal surface."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


class SpringFlower:
    """
    A realistic blooming flower:
      • Curved Bézier stem with slight lean
      • Two teardrop leaves on alternating sides
      • 5–7 rounded petals drawn as layered ellipses with a gradient-like
        inner lighter band
      • Multi-ring center (stigma + stamen dots)
      • Gentle wind sway, staggered bloom timeline
    """

    # Variety presets  ── (outer_petal, inner_petal, center_ring, center_core)
    VARIETIES = {
        "sakura":  ((255, 182, 193), (255, 220, 230), (255, 240, 100), (220,  80,  80)),
        "daisy":   ((255, 250, 250), (240, 240, 255), (255, 220,  60), (200, 160,  30)),
        "tulip":   ((255, 100, 120), (255, 160, 150), (255, 200,  80), (180,  40,  60)),
        "lavender":((200, 160, 220), (230, 200, 240), (255, 220, 100), (130,  80, 160)),
        "sunface": ((255, 200,  60), (255, 230, 120), (120,  70,  20), ( 80,  40,  10)),
    }

    def __init__(self, x, ground_y, variety=None):
        self.root_x   = x
        self.ground_y = ground_y

        # Pick variety
        if variety is None:
            variety = random.choice(list(self.VARIETIES.keys()))
        cols = self.VARIETIES[variety]
        self.col_outer  = cols[0]
        self.col_inner  = cols[1]
        self.col_cring  = cols[2]
        self.col_core   = cols[3]

        # Stem
        self.stem_h_max   = random.randint(90, 140)
        self.stem_h       = 0.0
        self.stem_speed   = random.uniform(35, 60)   # px / sec
        self.lean         = random.uniform(-18, 18)  # degrees
        self.tip_x        = x + math.sin(math.radians(self.lean)) * self.stem_h_max
        self.tip_y        = ground_y - self.stem_h_max

        # Sway
        self.sway_phase   = random.uniform(0, math.pi * 2)
        self.sway_amp     = random.uniform(0.03, 0.07)   # radians
        self.sway_speed   = random.uniform(0.6, 1.1)

        # Leaves
        self.leaf_prog    = 0.0
        self.leaf_side    = random.choice([-1, 1])
        self.leaf_at_h    = self.stem_h_max * random.uniform(0.38, 0.52)
        self.leaf_size    = random.uniform(16, 24)

        # Petals
        n = random.choice([5, 6, 7])
        self.n_petals    = n
        self.petal_len   = random.randint(22, 34)
        self.petal_w     = int(self.petal_len * random.uniform(0.42, 0.56))
        self.petal_progs = [0.0] * n      # each blooms independently
        bloom_start      = self.stem_h_max / self.stem_speed
        self.petal_delays= [bloom_start + i * random.uniform(0.08, 0.18)
                            + random.uniform(0, 0.12) for i in range(n)]
        self.petal_speed = random.uniform(0.9, 1.4)

        # Center
        self.center_r_max = random.randint(7, 11)
        self.center_prog  = 0.0
        self.stamen_dots  = [(random.uniform(0, 2*math.pi),
                              random.uniform(0.4, 0.85)) for _ in range(12)]

        self.elapsed = 0.0

    # ── helpers ──────────────────────────────────────────────────────────────

    def _stem_tip(self, sway_angle=0.0):
        """Current tip of the stem, accounting for growth and sway."""
        h    = self.stem_h
        lean = math.radians(self.lean) + sway_angle
        tx   = self.root_x + math.sin(lean) * h
        ty   = self.ground_y - math.cos(lean) * h
        return tx, ty

    def _draw_stem(self, surface, sway_angle):
        """Draw a slightly curved stem using a Bézier."""
        h    = self.stem_h
        if h < 2:
            return
        lean = math.radians(self.lean) + sway_angle
        tx, ty = self._stem_tip(sway_angle)

        # Control point (bulges mid-stem slightly)
        ctrl_x = self.root_x + math.sin(lean) * h * 0.5 + math.cos(lean) * 6
        ctrl_y = self.ground_y - math.cos(lean) * h * 0.5

        pts = _bezier_curve(
            (self.root_x, self.ground_y),
            (ctrl_x, ctrl_y),
            (tx, ty), steps=20
        )
        # Draw thick (shadow) then thin (highlight)
        if len(pts) >= 2:
            pygame.draw.lines(surface, (50, 110, 50), False,
                              [(int(p[0]+1), int(p[1]+1)) for p in pts], 4)
            pygame.draw.lines(surface, (80, 160, 80), False,
                              [(int(p[0]), int(p[1])) for p in pts], 3)
            pygame.draw.lines(surface, (130, 200, 110), False,
                              [(int(p[0]-1), int(p[1])) for p in pts], 1)

    def _draw_leaf(self, surface, sway_angle):
        """Teardrop leaf as a polygon drawn on one side of the stem."""
        if self.leaf_prog <= 0:
            return
        prog = self.leaf_prog
        lean = math.radians(self.lean) + sway_angle
        h    = self.leaf_at_h

        # Leaf base on the stem
        bx = self.root_x + math.sin(lean) * h
        by = self.ground_y - math.cos(lean) * h

        side = self.leaf_side
        size = self.leaf_size * prog

        # Leaf grows outward perpendicular to the stem
        perp = lean + math.pi / 2 * side
        tip_x = bx + math.cos(perp) * size * 1.8
        tip_y = by + math.sin(perp) * size * 1.8

        # Build teardrop: 8-point polygon
        pts = []
        for i in range(9):
            t   = i / 8
            # Interpolate base→tip, with bulge in the middle
            ix  = bx + (tip_x - bx) * t
            iy  = by + (tip_y - by) * t
            bulge = math.sin(t * math.pi) * size * 0.45
            nx  = math.cos(perp + math.pi/2) * bulge
            ny  = math.sin(perp + math.pi/2) * bulge
            pts.append((ix + nx, iy + ny))
        for i in range(9, 0, -1):
            t   = i / 9
            ix  = bx + (tip_x - bx) * t
            iy  = by + (tip_y - by) * t
            bulge = math.sin(t * math.pi) * size * 0.45
            nx  = math.cos(perp - math.pi/2) * bulge
            ny  = math.sin(perp - math.pi/2) * bulge
            pts.append((ix + nx, iy + ny))

        if len(pts) >= 3:
            pygame.draw.polygon(surface, (60, 140, 70), pts)
            # Midrib line
            mid = len(pts) // 2
            p1 = (int(bx), int(by))
            p2 = (int(tip_x), int(tip_y))
            pygame.draw.line(surface, (40, 110, 50), p1, p2, 1)

    def _draw_petal(self, surface, cx, cy, angle_rad, progress):
        """
        One realistic petal:
          outer ellipse (full petal color) + inner ellipse (lighter inner glow)
          drawn rotated around the flower center.
        """
        if progress <= 0:
            return

        length = self.petal_len * progress
        width  = self.petal_w  * progress

        # Petal ellipse is offset from center along its angle
        offset = length * 0.52
        px = cx + math.cos(angle_rad) * offset
        py = cy + math.sin(angle_rad) * offset

        # -- Outer petal surface --
        pts_outer = _surface_to_points(0, 0, length * 0.5, width * 0.5, n=22)
        # Rotate & translate
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        def xform(p):
            rx = p[0]*cos_a - p[1]*sin_a + px
            ry = p[0]*sin_a + p[1]*cos_a + py
            return (int(rx), int(ry))
        outer = [xform(p) for p in pts_outer]
        pygame.draw.polygon(surface, self.col_outer, outer)

        # -- Inner lighter band (creates depth) --
        inner_len = length * 0.38
        inner_w   = width  * 0.55
        pts_inner = _surface_to_points(0, 0, inner_len * 0.5, inner_w * 0.5, n=18)
        # Shift inner ellipse slightly toward center for a real petal look
        inner_offset = offset * 0.35
        ipx = cx + math.cos(angle_rad) * inner_offset
        ipy = cy + math.sin(angle_rad) * inner_offset
        def xform_i(p):
            rx = p[0]*cos_a - p[1]*sin_a + ipx
            ry = p[0]*sin_a + p[1]*cos_a + ipy
            return (int(rx), int(ry))
        inner = [xform_i(p) for p in pts_inner]
        pygame.draw.polygon(surface, self.col_inner, inner)

        # -- Thin vein line down the center of the petal --
        vein_start = (int(cx + math.cos(angle_rad)*3),
                      int(cy + math.sin(angle_rad)*3))
        vein_end   = (int(cx + math.cos(angle_rad)*(length*0.85)),
                      int(cy + math.sin(angle_rad)*(length*0.85)))
        vein_col = tuple(max(0, c - 30) for c in self.col_outer)
        pygame.draw.line(surface, vein_col, vein_start, vein_end, 1)

    def _draw_center(self, surface, cx, cy):
        """Multi-ring center: stamen ring + stigma core + tiny dot stamens."""
        if self.center_prog <= 0:
            return
        prog = self.center_prog
        r    = self.center_r_max

        # Outer ring (stamen color)
        ring_r = int(r * prog)
        if ring_r > 0:
            pygame.draw.circle(surface, self.col_cring,
                               (int(cx), int(cy)), ring_r)

        # Core (stigma)
        core_r = max(1, int(r * 0.55 * prog))
        pygame.draw.circle(surface, self.col_core,
                           (int(cx), int(cy)), core_r)

        # Tiny stamen dots scattered in a ring
        if prog > 0.6:
            dot_alpha = (prog - 0.6) / 0.4
            for angle, dist in self.stamen_dots:
                dr   = (ring_r - core_r - 1) * dist + core_r
                dx   = int(cx + math.cos(angle) * dr)
                dy   = int(cy + math.sin(angle) * dr)
                dcol = tuple(int(self.col_core[i]*0.7 + self.col_cring[i]*0.3)
                             for i in range(3))
                pygame.draw.circle(surface, dcol, (dx, dy), 1)

        # Highlight
        hl = max(1, core_r // 3)
        pygame.draw.circle(surface, (255, 255, 220),
                           (int(cx) - hl, int(cy) - hl), hl)

    # ── public API ───────────────────────────────────────────────────────────

    def update(self, dt=None):
        """
        Call once per frame.
        Accepts optional dt (seconds). If omitted, assumes 60 fps (≈0.0167 s).
        """
        if dt is None:
            dt = 1 / 60

        self.elapsed += dt

        # Stem growth
        if self.stem_h < self.stem_h_max:
            self.stem_h = min(self.stem_h_max, self.stem_h + self.stem_speed * dt)

        # Leaf
        if self.stem_h >= self.leaf_at_h:
            self.leaf_prog = min(1.0, self.leaf_prog + dt * 1.0)

        # Petals — each blooms after its individual delay
        for i in range(self.n_petals):
            if self.elapsed > self.petal_delays[i]:
                active = self.elapsed - self.petal_delays[i]
                self.petal_progs[i] = min(1.0, active * self.petal_speed)

        # Center appears once first petals start opening
        if self.elapsed > self.petal_delays[0]:
            self.center_prog = min(1.0, self.center_prog + dt * 1.2)

    def draw(self, screen):
        # Current sway angle
        t     = pygame.time.get_ticks() / 1000
        sway  = math.sin(t * self.sway_speed + self.sway_phase) * self.sway_amp

        # Stem
        self._draw_stem(screen, sway)

        # Leaf
        self._draw_leaf(screen, sway)

        # Tip position (flower head)
        tx, ty = self._stem_tip(sway)

        # Petals (drawn back to front by splitting into two passes)
        for i in range(self.n_petals):
            angle = (2 * math.pi / self.n_petals) * i
            self._draw_petal(screen, tx, ty, angle, self.petal_progs[i])

        # Center
        self._draw_center(screen, tx, ty)