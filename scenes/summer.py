import pygame
import math
import random
from settings import *
from particles.figures import Figures

# ─────────────────────────────────────────────────────────────────────────────
#  scenes/summer.py  —  "Mom Through Seasons"
#
#  Self-contained Summer scene.
#  Called from main.py:
#      from scenes.summer import Summer
#      Summer(screen, clock).run()
#
#  Elements:
#    • Golden-hour sky gradient (blue → amber → gold at horizon)
#    • Rolling layered hills
#    • Glowing sun with slowly rotating rays
#    • Heat shimmer at horizon
#    • Lazy warm clouds
#    • Tall swaying grass + wheat stalks
#    • Sunflowers blooming along ground
#    • Floating golden pollen/dust motes
#    • Fireflies blinking softly
#    • Scene message in Great Vibes font
#    • Fade in from black, fade out to black
# ─────────────────────────────────────────────────────────────────────────────

FONT_PATH  = "C:/Users/mvsla/OneDrive/Desktop/Mother's day gift/assets/fonts/GreatVibes-Regular.ttf"
GROUND_Y   = HEIGHT - 60

# ── Palette ───────────────────────────────────────────────────────────────────
SKY_TOP      = ( 80, 140, 210)   # warm sky blue
SKY_MID      = (200, 160,  80)   # amber band
SKY_HORIZON  = (255, 210,  80)   # golden horizon
HILL_BACK    = ( 60, 120,  60)   # far hills (muted)
HILL_MID     = ( 50, 140,  55)   # mid hills
HILL_FRONT   = ( 40, 110,  40)   # near hills
GROUND_TOP   = ( 80, 150,  50)
GROUND_BOT   = ( 30,  80,  20)


# ─────────────────────────────────────────────────────────────────────────────
#  SKY
# ─────────────────────────────────────────────────────────────────────────────
def draw_summer_sky(surface, width, height, ground_y):
    """Three-stop gradient: blue top → amber mid → gold at horizon."""
    mid = int(ground_y * 0.55)

    for y in range(mid):
        t = y / mid
        r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    for y in range(mid, ground_y):
        t = (y - mid) / max(ground_y - mid, 1)
        r = int(SKY_MID[0] + (SKY_HORIZON[0] - SKY_MID[0]) * t)
        g = int(SKY_MID[1] + (SKY_HORIZON[1] - SKY_MID[1]) * t)
        b = int(SKY_MID[2] + (SKY_HORIZON[2] - SKY_MID[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


# ─────────────────────────────────────────────────────────────────────────────
#  SUN
# ─────────────────────────────────────────────────────────────────────────────
class Sun:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius     = 48
        self.ray_angle  = 0.0        # rotates slowly
        self.ray_count  = 12
        self.elapsed    = 0.0

    def update(self, dt):
        self.elapsed   += dt
        self.ray_angle += dt * 0.18  # slow rotation

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        t = self.elapsed

        # ── Outer glow rings ──────────────────────────────────────────────────
        for r, a in [(90, 18), (72, 30), (60, 50)]:
            glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 80, a), (r, r), r)
            surface.blit(glow, (cx - r, cy - r))

        # ── Rays ──────────────────────────────────────────────────────────────
        for i in range(self.ray_count):
            base_angle = self.ray_angle + (2 * math.pi / self.ray_count) * i
            # Rays pulse slightly in length
            ray_len = 62 + math.sin(t * 1.5 + i * 0.8) * 8

            inner = self.radius + 6
            ox = cx + math.cos(base_angle) * inner
            oy = cy + math.sin(base_angle) * inner
            ex = cx + math.cos(base_angle) * (inner + ray_len)
            ey = cy + math.sin(base_angle) * (inner + ray_len)

            # Taper: draw 3 lines of decreasing width
            for w, a in [(3, 60), (2, 100), (1, 160)]:
                ray_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 230, 100, a),
                                 (int(ox), int(oy)), (int(ex), int(ey)), w)
                surface.blit(ray_surf, (0, 0))

        # ── Sun body ──────────────────────────────────────────────────────────
        pygame.draw.circle(surface, (255, 220,  60), (cx, cy), self.radius)
        pygame.draw.circle(surface, (255, 240, 140), (cx, cy), int(self.radius * 0.65))
        pygame.draw.circle(surface, (255, 255, 220), (cx, cy), int(self.radius * 0.35))


# ─────────────────────────────────────────────────────────────────────────────
#  ROLLING HILLS
# ─────────────────────────────────────────────────────────────────────────────
def make_hill_points(width, ground_y, amplitude, frequency, y_offset, phase=0):
    """Generate a hill silhouette as a closed polygon."""
    pts = [(0, ground_y)]
    steps = width // 4
    for i in range(steps + 1):
        x = i * 4
        y = y_offset + math.sin((x / width) * math.pi * frequency + phase) * amplitude
        pts.append((x, y))
    pts.append((width, ground_y))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
#  LAZY CLOUDS (warm-tinted for summer)
# ─────────────────────────────────────────────────────────────────────────────
class SummerCloud:
    def __init__(self, screen_w, ground_y, spawn_offscreen=False):
        self.sw = screen_w
        self.gy = ground_y
        self._randomize(spawn_offscreen)

    def _randomize(self, offscreen=False):
        self.y     = int(self.gy * random.uniform(0.05, 0.30))
        self.speed = random.uniform(6, 16)
        self.alpha = random.randint(130, 180)
        self.puffs = []
        n = random.randint(4, 7)
        base_w = random.randint(80, 150)
        for i in range(n):
            ox = i * int(base_w * 0.52) + random.randint(-8, 8)
            oy = random.randint(-10, 10)
            rw = random.randint(int(base_w * 0.5), int(base_w * 0.8))
            rh = random.randint(int(rw * 0.4), int(rw * 0.6))
            self.puffs.append((ox, oy, rw, rh))
        total_w = max(p[0] + p[2] for p in self.puffs)
        self.x = -total_w - 20 if offscreen else random.randint(-total_w, self.sw)
        self.total_w = total_w
        # Warm cream-gold tint
        self.color = (255, random.randint(230, 248), random.randint(190, 220))

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > self.sw + 20:
            self._randomize(offscreen=True)

    def draw(self, surface):
        for ox, oy, rw, rh in self.puffs:
            cx = int(self.x + ox + rw // 2)
            cy = int(self.y + oy)
            s = pygame.Surface((rw * 2, rh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*self.color, self.alpha), (0, 0, rw * 2, rh * 2))
            surface.blit(s, (cx - rw, cy - rh))


# ─────────────────────────────────────────────────────────────────────────────
#  TALL GRASS + WHEAT
# ─────────────────────────────────────────────────────────────────────────────
class SummerGrassBlade:
    def __init__(self, x, ground_y, kind="grass"):
        self.base_x   = x
        self.ground_y = ground_y
        self.kind     = kind   # "grass" or "wheat"

        if kind == "wheat":
            self.height    = random.randint(55, 90)
            self.thickness = random.choice([1, 2])
            self.color     = (random.randint(180, 220), random.randint(150, 180), 40)
            self.tip_color = (240, 210, 80)
        else:
            self.height    = random.randint(25, 55)
            self.thickness = 1
            g = random.randint(120, 180)
            self.color     = (20, g, 30)
            self.tip_color = (60, g + 30, 50)

        self.lean       = random.uniform(-0.4, 0.4)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_amp   = random.uniform(0.08, 0.22)
        self.sway_freq  = random.uniform(0.5, 1.0)

    def draw(self, surface, wind_t):
        wind   = math.sin(wind_t * self.sway_freq + self.sway_phase) * self.sway_amp
        lean   = self.lean + wind
        h      = self.height
        bx, by = self.base_x, self.ground_y

        tip_x  = bx + math.sin(lean) * h
        tip_y  = by - math.cos(lean) * h
        ctrl_x = bx + math.sin(lean) * h * 0.5 + math.cos(lean) * h * 0.15
        ctrl_y = by - math.cos(lean) * h * 0.5

        steps = 7
        prev  = (bx, by)
        for i in range(1, steps + 1):
            t  = i / steps
            x  = (1-t)**2 * bx + 2*(1-t)*t * ctrl_x + t**2 * tip_x
            y  = (1-t)**2 * by + 2*(1-t)*t * ctrl_y + t**2 * tip_y
            r  = int(self.color[0] + (self.tip_color[0] - self.color[0]) * t)
            g  = int(self.color[1] + (self.tip_color[1] - self.color[1]) * t)
            b  = int(self.color[2] + (self.tip_color[2] - self.color[2]) * t)
            pygame.draw.line(surface, (r, g, b),
                             (int(prev[0]), int(prev[1])),
                             (int(x), int(y)), self.thickness)
            prev = (x, y)

        # Wheat head — small oval at the tip
        if self.kind == "wheat":
            pygame.draw.ellipse(surface, (220, 190, 60),
                                (int(tip_x) - 3, int(tip_y) - 8, 6, 14))


class SummerGround:
    def __init__(self, width, height, ground_y):
        self.width    = width
        self.height   = height
        self.ground_y = ground_y
        self.elapsed  = 0.0

        # Mix grass and wheat
        blades = []
        for x in range(0, width, 5):
            kind = "wheat" if random.random() < 0.18 else "grass"
            blades.append(SummerGrassBlade(x + random.randint(-3, 3), ground_y, kind))
        random.shuffle(blades)
        self.blades = blades

        # Ground strip
        self.ground_top = (60, 130, 40)
        self.ground_bot = (25,  70, 15)

    def update(self, dt):
        self.elapsed += dt

    def draw(self, surface):
        # Ground fill
        strip = self.height - self.ground_y
        for y in range(strip):
            t = y / max(strip - 1, 1)
            r = int(self.ground_top[0] + (self.ground_bot[0] - self.ground_top[0]) * t)
            g = int(self.ground_top[1] + (self.ground_bot[1] - self.ground_top[1]) * t)
            b = int(self.ground_top[2] + (self.ground_bot[2] - self.ground_top[2]) * t)
            pygame.draw.line(surface, (r, g, b),
                             (0, self.ground_y + y), (self.width, self.ground_y + y))
        for blade in self.blades:
            blade.draw(surface, self.elapsed)


# ─────────────────────────────────────────────────────────────────────────────
#  SUNFLOWER
# ─────────────────────────────────────────────────────────────────────────────
class Sunflower:
    def __init__(self, x, ground_y):
        self.root_x   = x
        self.ground_y = ground_y
        self.stem_h_max = random.randint(100, 160)
        self.stem_h     = 0.0
        self.stem_speed = random.uniform(40, 65)
        self.lean       = random.uniform(-12, 12)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_amp   = random.uniform(0.02, 0.05)
        self.sway_freq  = random.uniform(0.4, 0.8)

        # Petals
        self.n_petals     = random.choice([13, 16, 18])
        self.petal_len    = random.randint(18, 26)
        self.petal_w      = random.randint(7, 11)
        self.petal_progs  = [0.0] * self.n_petals
        bloom_start       = self.stem_h_max / self.stem_speed
        self.petal_delays = [bloom_start + i * 0.06 + random.uniform(0, 0.08)
                             for i in range(self.n_petals)]
        self.petal_speed  = random.uniform(1.0, 1.6)

        # Center disk
        self.disk_r_max   = random.randint(14, 20)
        self.disk_prog    = 0.0

        # Leaf
        self.leaf_side    = random.choice([-1, 1])
        self.leaf_at_h    = self.stem_h_max * random.uniform(0.40, 0.55)
        self.leaf_prog    = 0.0

        self.elapsed = 0.0

    def _tip(self, sway):
        lean = math.radians(self.lean) + sway
        tx   = self.root_x + math.sin(lean) * self.stem_h
        ty   = self.ground_y - math.cos(lean) * self.stem_h
        return tx, ty

    def update(self, dt):
        self.elapsed += dt
        if self.stem_h < self.stem_h_max:
            self.stem_h = min(self.stem_h_max, self.stem_h + self.stem_speed * dt)
        if self.stem_h >= self.leaf_at_h:
            self.leaf_prog = min(1.0, self.leaf_prog + dt * 1.0)
        for i in range(self.n_petals):
            if self.elapsed > self.petal_delays[i]:
                self.petal_progs[i] = min(1.0,
                    (self.elapsed - self.petal_delays[i]) * self.petal_speed)
        bloom_start = self.stem_h_max / self.stem_speed
        if self.elapsed > bloom_start:
            self.disk_prog = min(1.0, self.disk_prog + dt * 1.2)

    def _draw_petal(self, surface, cx, cy, angle, progress):
        if progress <= 0:
            return
        length = self.petal_len * progress
        width  = self.petal_w  * progress
        offset = length * 0.52
        px = cx + math.cos(angle) * offset
        py = cy + math.sin(angle) * offset

        cos_a, sin_a = math.cos(angle), math.sin(angle)
        n = 18
        pts = []
        for i in range(n):
            t  = 2 * math.pi * i / n
            lx = length * 0.5 * math.cos(t)
            ly = width  * 0.5 * math.sin(t)
            rx = lx * cos_a - ly * sin_a + px
            ry = lx * sin_a + ly * cos_a + py
            pts.append((int(rx), int(ry)))
        if len(pts) >= 3:
            pygame.draw.polygon(surface, (255, 190, 20), pts)
            # Inner lighter stripe
            pts2 = []
            for i in range(n):
                t  = 2 * math.pi * i / n
                lx = length * 0.28 * math.cos(t)
                ly = width  * 0.35 * math.sin(t)
                ipx = cx + math.cos(angle) * offset * 0.4
                ipy = cy + math.sin(angle) * offset * 0.4
                rx  = lx * cos_a - ly * sin_a + ipx
                ry  = lx * sin_a + ly * cos_a + ipy
                pts2.append((int(rx), int(ry)))
            if len(pts2) >= 3:
                pygame.draw.polygon(surface, (255, 220, 80), pts2)

    def _draw_leaf(self, surface, stem_x, stem_y, sway):
        p = self.leaf_prog
        if p <= 0:
            return
        lean = math.radians(self.lean) + sway
        perp = lean + math.pi / 2 * self.leaf_side
        size = 22 * p
        tip_x = stem_x + math.cos(perp) * size * 1.9
        tip_y = stem_y + math.sin(perp) * size * 1.9
        pts = []
        for i in range(9):
            t = i / 8
            ix = stem_x + (tip_x - stem_x) * t
            iy = stem_y + (tip_y - stem_y) * t
            bulge = math.sin(t * math.pi) * size * 0.5
            nx = math.cos(perp + math.pi/2) * bulge
            ny = math.sin(perp + math.pi/2) * bulge
            pts.append((ix + nx, iy + ny))
        for i in range(9, 0, -1):
            t = i / 9
            ix = stem_x + (tip_x - stem_x) * t
            iy = stem_y + (tip_y - stem_y) * t
            bulge = math.sin(t * math.pi) * size * 0.5
            nx = math.cos(perp - math.pi/2) * bulge
            ny = math.sin(perp - math.pi/2) * bulge
            pts.append((ix + nx, iy + ny))
        if len(pts) >= 3:
            pygame.draw.polygon(surface, (40, 120, 30), pts)
            pygame.draw.line(surface, (25, 90, 20),
                             (int(stem_x), int(stem_y)),
                             (int(tip_x), int(tip_y)), 1)

    def draw(self, surface):
        t     = pygame.time.get_ticks() / 1000
        sway  = math.sin(t * self.sway_freq + self.sway_phase) * self.sway_amp
        lean  = math.radians(self.lean) + sway
        tx, ty = self._tip(sway)

        # Stem (shadow + main + highlight)
        rx, ry = self.root_x, self.ground_y
        ctrl_x = rx + math.sin(lean) * self.stem_h * 0.5
        ctrl_y = ry - math.cos(lean) * self.stem_h * 0.5

        steps = 20
        prev  = (rx, ry)
        for i in range(1, steps + 1):
            t2 = i / steps
            sx = (1-t2)**2 * rx + 2*(1-t2)*t2 * ctrl_x + t2**2 * tx
            sy = (1-t2)**2 * ry + 2*(1-t2)*t2 * ctrl_y + t2**2 * ty
            pygame.draw.line(surface, (35, 100, 30),
                             (int(prev[0]+1), int(prev[1]+1)),
                             (int(sx+1), int(sy+1)), 5)
            pygame.draw.line(surface, (55, 140, 40),
                             (int(prev[0]), int(prev[1])),
                             (int(sx), int(sy)), 4)
            pygame.draw.line(surface, (90, 180, 60),
                             (int(prev[0]-1), int(prev[1])),
                             (int(sx-1), int(sy)), 1)
            prev = (sx, sy)

        # Leaf
        leaf_y = ry - math.cos(lean) * self.leaf_at_h
        leaf_x = rx + math.sin(lean) * self.leaf_at_h
        self._draw_leaf(surface, leaf_x, leaf_y, sway)

        # Petals
        for i in range(self.n_petals):
            angle = (2 * math.pi / self.n_petals) * i
            self._draw_petal(surface, tx, ty, angle, self.petal_progs[i])

        # Center disk — brown rings + dark core
        if self.disk_prog > 0:
            dr = int(self.disk_r_max * self.disk_prog)
            if dr > 0:
                pygame.draw.circle(surface, (120, 70, 20), (int(tx), int(ty)), dr)
                pygame.draw.circle(surface, ( 80, 40, 10), (int(tx), int(ty)), max(1, int(dr*0.65)))
                pygame.draw.circle(surface, ( 50, 20,  5), (int(tx), int(ty)), max(1, int(dr*0.35)))
                # Tiny stamen dots
                for j in range(16):
                    a2  = 2 * math.pi * j / 16
                    ddx = int(tx + math.cos(a2) * dr * 0.78)
                    ddy = int(ty + math.sin(a2) * dr * 0.78)
                    pygame.draw.circle(surface, (160, 100, 30), (ddx, ddy), 1)
                # Highlight
                pygame.draw.circle(surface, (160, 100, 40),
                                   (int(tx) - 3, int(ty) - 3), max(1, dr//4))


# ─────────────────────────────────────────────────────────────────────────────
#  GOLDEN DUST / POLLEN MOTES
# ─────────────────────────────────────────────────────────────────────────────
class DustMote:
    def __init__(self, width, height, ground_y):
        self.w = width
        self.h = height
        self.gy = ground_y
        self._reset(initial=True)

    def _reset(self, initial=False):
        self.x     = random.uniform(0, self.w)
        self.y     = random.uniform(self.gy * 0.1, self.gy * 0.95) if initial \
                     else random.uniform(self.gy * 0.6, self.gy * 0.95)
        self.vy    = random.uniform(-18, -6)    # drifts upward
        self.vx    = random.uniform(-8, 8)
        self.alpha = random.randint(80, 200)
        self.size  = random.choice([1, 1, 2])
        self.life  = random.uniform(3.0, 8.0)
        self.age   = 0.0
        # Warm gold tones
        self.color = (
            random.randint(220, 255),
            random.randint(180, 220),
            random.randint(40, 100),
        )

    def update(self, dt):
        self.age += dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        self.vx  += random.uniform(-4, 4) * dt   # gentle wander
        self.vx   = max(-12, min(12, self.vx))
        if self.age > self.life or self.y < 0 or self.x < 0 or self.x > self.w:
            self._reset()

    def draw(self, surface):
        # Fade in/out over lifetime
        t = self.age / self.life
        fade = math.sin(t * math.pi)
        a    = int(self.alpha * fade)
        if a <= 0:
            return
        s = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a),
                           (self.size*2, self.size*2), self.size)
        surface.blit(s, (int(self.x) - self.size*2, int(self.y) - self.size*2))


# ─────────────────────────────────────────────────────────────────────────────
#  FIREFLIES
# ─────────────────────────────────────────────────────────────────────────────
class Firefly:
    def __init__(self, width, height, ground_y):
        self.w  = width
        self.h  = height
        self.gy = ground_y
        self._reset(initial=True)

    def _reset(self, initial=False):
        self.x      = random.uniform(0, self.w)
        self.y      = random.uniform(self.gy * 0.4, self.gy * 0.92)
        self.vx     = random.uniform(-20, 20)
        self.vy     = random.uniform(-12, 12)
        # Blink cycle
        self.blink_freq  = random.uniform(0.5, 1.5)
        self.blink_phase = random.uniform(0, math.pi * 2)
        self.color  = random.choice([
            (180, 255, 120),   # warm green-yellow
            (220, 255, 100),   # golden yellow
            (160, 240, 100),   # soft green
        ])
        self.size   = random.choice([2, 2, 3])
        self.life   = random.uniform(5, 14)
        self.age    = random.uniform(0, 5) if initial else 0.0

    def update(self, dt):
        self.age += dt
        self.x   += self.vx * dt + random.uniform(-0.5, 0.5)
        self.y   += self.vy * dt + random.uniform(-0.3, 0.3)
        self.vx  *= 0.995
        self.vy  *= 0.995
        if (self.age > self.life or self.x < 0 or self.x > self.w
                or self.y < 0 or self.y > self.gy):
            self._reset()

    def draw(self, surface):
        t     = self.age
        blink = (math.sin(t * self.blink_freq * math.pi * 2 + self.blink_phase) + 1) / 2
        if blink < 0.35:
            return   # off
        a    = int(blink * 220)
        size = self.size
        # Glow
        for gr, ga in [(size*5, a//6), (size*3, a//3), (size, a)]:
            gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*self.color, ga), (gr, gr), gr)
            surface.blit(gs, (int(self.x) - gr, int(self.y) - gr))


# ─────────────────────────────────────────────────────────────────────────────
#  HEAT SHIMMER
# ─────────────────────────────────────────────────────────────────────────────
class HeatShimmer:
    """
    Draws a wavy distortion band near the horizon by sampling and redrawing
    a thin horizontal strip with a sine offset.
    """
    def __init__(self, width, ground_y):
        self.w        = width
        self.y        = ground_y - 18   # just above the ground
        self.elapsed  = 0.0
        self.band_h   = 14

    def update(self, dt):
        self.elapsed += dt

    def draw(self, surface):
        t = self.elapsed
        # Sample the strip, shift each column by a small sine offset
        strip = surface.subsurface(
            pygame.Rect(0, self.y, self.w, self.band_h)
        ).copy()
        for x in range(0, self.w, 3):
            shift = int(math.sin(x * 0.04 + t * 3.2) * 2.5)
            col   = strip.subsurface(pygame.Rect(
                min(x, self.w - 3), 0, 3, self.band_h)).copy()
            surface.blit(col, (x, self.y + shift))


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE TEXT
# ─────────────────────────────────────────────────────────────────────────────
class SummerText:
    LINE1 = "Even when I ran toward the world,"
    LINE2 = "you stayed behind me like sunlight."

    def __init__(self, width, height, font_path, appear_after=5.0):
        self.cx           = width // 2
        self.appear_after = appear_after
        self.elapsed      = 0.0
        self.alpha        = 0.0
        self.fade_speed   = 55

        try:
            font_l = pygame.font.Font(font_path, 52)
            font_s = pygame.font.Font(font_path, int(52 * 0.78))
        except FileNotFoundError:
            font_l = pygame.font.SysFont("serif", 52)
            font_s = pygame.font.SysFont("serif", int(52 * 0.78))

        # Deep warm brown — readable on golden sky
        col   = (40, 20, 5)
        glow  = (180, 100, 20)

        self.surf1 = font_l.render(self.LINE1, True, col)
        self.surf2 = font_s.render(self.LINE2, True, col)
        self.glow1 = font_l.render(self.LINE1, True, glow)
        self.glow2 = font_s.render(self.LINE2, True, glow)

        self.y1 = int(height * 0.20)
        self.y2 = self.y1 + int(52 * 1.15)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.appear_after:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)

    def draw(self, surface):
        if self.alpha <= 0:
            return
        a = int(self.alpha)
        if self.alpha >= 255:
            a = max(0, min(255, 255 + int(math.sin(self.elapsed * 0.5) * 5)))

        for surf, glow, y in [(self.surf1, self.glow1, self.y1),
                               (self.surf2, self.glow2, self.y2)]:
            x = self.cx - surf.get_width() // 2
            ga = max(0, a - 120)
            if ga > 0:
                glow.set_alpha(ga // 4)
                for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
                    surface.blit(glow, (x+ox, y+oy))
            surf.set_alpha(a)
            surface.blit(surf, (x, y))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN SCENE CLASS
# ─────────────────────────────────────────────────────────────────────────────
class Summer:
    SCENE_DURATION = 15.0
    FADE_DURATION  = 2.5

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self._build()

    def _build(self):
        # Static sky surface
        self.sky_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_summer_sky(self.sky_surf, WIDTH, HEIGHT, GROUND_Y)

        # Pre-bake hill polygons
        self.hill_back  = make_hill_points(WIDTH, GROUND_Y, 55, 2.2,
                                           GROUND_Y - 160, phase=0.3)
        self.hill_mid   = make_hill_points(WIDTH, GROUND_Y, 45, 1.8,
                                           GROUND_Y - 110, phase=1.1)
        self.hill_front = make_hill_points(WIDTH, GROUND_Y, 30, 2.8,
                                           GROUND_Y - 70,  phase=2.0)

        # Sun (upper-right, warm position)
        self.sun = Sun(WIDTH * 0.78, HEIGHT * 0.14)

        # Clouds
        self.clouds = [SummerCloud(WIDTH, GROUND_Y) for _ in range(6)]

        # Ground + grass
        self.ground = SummerGround(WIDTH, HEIGHT, GROUND_Y)

        # Sunflowers spread across the width
        configs = [
            WIDTH * 0.04, WIDTH * 0.10, WIDTH * 0.16, WIDTH * 0.23,
            WIDTH * 0.29, WIDTH * 0.35, WIDTH * 0.42, WIDTH * 0.48,
            WIDTH * 0.54, WIDTH * 0.60, WIDTH * 0.67, WIDTH * 0.73,
            WIDTH * 0.79, WIDTH * 0.85, WIDTH * 0.91, WIDTH * 0.97,
        ]
        offsets = [0, 8, -6, 4, 0, -10, 6, 0, -4, 10, 0, -8, 5, 0, -5, 8]
        self.sunflowers = [
            Sunflower(int(x), int(GROUND_Y + offsets[i]))
            for i, x in enumerate(configs)
        ]

        # Dust motes
        self.motes = [DustMote(WIDTH, HEIGHT, GROUND_Y) for _ in range(60)]

        # Fireflies
        self.fireflies = [Firefly(WIDTH, HEIGHT, GROUND_Y) for _ in range(18)]

        # Heat shimmer
        self.shimmer = HeatShimmer(WIDTH, GROUND_Y)

        # Figures — daughter running, mother following
        self.figures = Figures(WIDTH, HEIGHT, ground_y=GROUND_Y)

        # Text
        self.text = SummerText(WIDTH, HEIGHT, FONT_PATH, appear_after=5.0)

        # Fade
        self.fade_surf  = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surf.fill((0, 0, 0))
        self.fade_alpha = 0
        self.elapsed    = 0.0
        self.fading_out = False
        self._fade_start = 0.0

        # Fade IN from black
        self.fade_in     = True
        self.fade_in_dur = 1.8

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit(); raise SystemExit

            # Fade in
            if self.fade_in:
                self.fade_alpha = max(0, int(255 * (1 - self.elapsed / self.fade_in_dur)))
                if self.elapsed >= self.fade_in_dur:
                    self.fade_in    = False
                    self.fade_alpha = 0

            # Trigger fade out
            if self.elapsed >= self.SCENE_DURATION and not self.fading_out:
                self.fading_out  = True
                self._fade_start = self.elapsed

            if self.fading_out:
                p = (self.elapsed - self._fade_start) / self.FADE_DURATION
                self.fade_alpha = min(255, int(p * 255))
                if self.fade_alpha >= 255:
                    running = False

            # Update
            self.sun.update(dt)
            for c in self.clouds:
                c.update(dt)
            self.ground.update(dt)
            for sf in self.sunflowers:
                sf.update(dt)
            for m in self.motes:
                m.update(dt)
            for f in self.fireflies:
                f.update(dt)
            self.shimmer.update(dt)
            self.text.update(dt)
            self.figures.update(dt)

            self._draw()

        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def _draw(self):
        # 1. Sky
        self.screen.blit(self.sky_surf, (0, 0))

        # 2. Sun (behind hills)
        self.sun.draw(self.screen)

        # 3. Hills back → front
        pygame.draw.polygon(self.screen, HILL_BACK,  self.hill_back)
        pygame.draw.polygon(self.screen, HILL_MID,   self.hill_mid)
        pygame.draw.polygon(self.screen, HILL_FRONT, self.hill_front)

        # 4. Clouds
        for c in self.clouds:
            c.draw(self.screen)

        # 5. Ground + grass
        self.ground.draw(self.screen)

        # 6. Sunflowers
        for sf in self.sunflowers:
            sf.draw(self.screen)

        # 7. Figures (between sunflowers and shimmer — mid-ground)
        self.figures.draw(self.screen)

        # 8. Heat shimmer (applied AFTER ground is drawn)
        self.shimmer.draw(self.screen)

        # 8. Dust motes
        for m in self.motes:
            m.draw(self.screen)

        # 9. Fireflies
        for f in self.fireflies:
            f.draw(self.screen)

        # 10. Text
        self.text.draw(self.screen)

        # 11. Fade overlay
        if self.fade_alpha > 0:
            self.fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surf, (0, 0))

        pygame.display.update()