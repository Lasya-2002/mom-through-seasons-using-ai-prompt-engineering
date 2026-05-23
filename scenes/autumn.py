import pygame
import math
import random
from settings import *

# ─────────────────────────────────────────────────────────────────────────────
#  scenes/autumn.py  —  "Mom Through Seasons"
#
#  The emotional core of the experience.
#  Elements:
#    • Moody amber → grey-purple sky gradient
#    • Layered hills in rust/brown tones
#    • Bare & half-bare trees with branching arms
#    • Dozens of rotating falling leaves
#    • Subtle diagonal rain streaks
#    • Wind wisps streaking across screen
#    • Dry sparse autumn grass
#    • Daughter walking away, mother reaching forward (silhouettes)
#    • Two-part message fading in sequence
#    • Fade in from black, fade out to black
# ─────────────────────────────────────────────────────────────────────────────

FONT_PATH = "C:/Users/mvsla/OneDrive/Desktop/Mother's day gift/assets/fonts/GreatVibes-Regular.ttf"
GROUND_Y  = HEIGHT - 60

# ── Palette ───────────────────────────────────────────────────────────────────
SKY_TOP      = ( 60,  50,  75)   # dusty purple-grey
SKY_MID      = (130,  80,  40)   # amber band
SKY_HORIZON  = (190, 110,  40)   # warm rust at horizon
HILL_FAR     = ( 80,  55,  30)   # distant muted brown
HILL_MID_COL = ( 65,  48,  25)
HILL_NEAR    = ( 50,  38,  18)
GROUND_TOP   = ( 55,  45,  20)
GROUND_BOT   = ( 30,  22,  10)
SILHOUETTE   = ( 18,  12,   6)


# ─────────────────────────────────────────────────────────────────────────────
#  SKY
# ─────────────────────────────────────────────────────────────────────────────
def draw_autumn_sky(surface, width, height, ground_y):
    mid = int(ground_y * 0.52)
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
#  HILLS
# ─────────────────────────────────────────────────────────────────────────────
def make_hill(width, ground_y, amplitude, frequency, y_offset, phase=0):
    pts = [(0, ground_y)]
    for i in range(width // 3 + 1):
        x = i * 3
        y = y_offset + math.sin((x / width) * math.pi * frequency + phase) * amplitude
        pts.append((x, y))
    pts.append((width, ground_y))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
#  TREE
# ─────────────────────────────────────────────────────────────────────────────
class Tree:
    def __init__(self, x, ground_y, height, bare_ratio):
        """
        bare_ratio: 0.0 = full leaves, 1.0 = completely bare
        """
        self.x          = x
        self.ground_y   = ground_y
        self.height     = height
        self.bare_ratio = bare_ratio
        self.trunk_w    = max(4, int(height * 0.055))
        self.branches   = self._make_branches()

        # Pre-bake leaf cluster data so colors don't randomize every frame
        LEAF_PALETTE = [
            (160,  70,  20),
            (190,  90,  25),
            (140,  50,  15),
            (180, 120,  30),
            (120,  40,  10),
        ]
        self.leaf_clusters = []
        for x1, y1, x2, y2, w, depth in self.branches:
            if depth == 1 and random.random() > bare_ratio:
                self.leaf_clusters.append((
                    x2, y2,
                    random.choice(LEAF_PALETTE),
                    random.randint(8, 16)
                ))

    def _make_branches(self):
        """Recursively generate branch segments."""
        branches = []
        def add_branch(x1, y1, angle, length, depth, width):
            if depth == 0 or length < 4:
                return
            x2 = x1 + math.sin(angle) * length
            y2 = y1 - math.cos(angle) * length
            branches.append((x1, y1, x2, y2, width, depth))
            # Left branch
            spread = random.uniform(0.3, 0.55)
            add_branch(x2, y2, angle - spread, length * random.uniform(0.62, 0.72),
                       depth - 1, max(1, width - 1))
            # Right branch
            spread2 = random.uniform(0.3, 0.55)
            add_branch(x2, y2, angle + spread2, length * random.uniform(0.62, 0.72),
                       depth - 1, max(1, width - 1))
            # Occasional mid branch
            if depth > 2 and random.random() < 0.45:
                add_branch(x2, y2, angle + random.uniform(-0.2, 0.2),
                           length * 0.55, depth - 2, max(1, width - 1))

        trunk_top_y = self.ground_y - self.height * 0.38
        add_branch(self.x, trunk_top_y, 0,
                   self.height * 0.32, depth=5,
                   width=max(2, self.trunk_w - 2))
        return branches

    def draw(self, surface):
        # Trunk
        trunk_top = int(self.ground_y - self.height * 0.38)
        pygame.draw.line(surface, SILHOUETTE,
                         (int(self.x), int(self.ground_y)),
                         (int(self.x), trunk_top), self.trunk_w)

        # Branches
        for x1, y1, x2, y2, w, depth in self.branches:
            pygame.draw.line(surface, SILHOUETTE,
                             (int(x1), int(y1)), (int(x2), int(y2)), w)

        # Static leaf clusters (pre-baked, no randomness per frame)
        for lx, ly, col, r in self.leaf_clusters:
            pygame.draw.circle(surface, col, (int(lx), int(ly)), r)


# ─────────────────────────────────────────────────────────────────────────────
#  FALLING LEAF
# ─────────────────────────────────────────────────────────────────────────────
LEAF_COLORS = [
    (180,  65,  20),   # deep rust
    (210,  90,  25),   # orange
    (155,  45,  15),   # dark red-brown
    (200, 140,  30),   # golden amber
    (140,  35,  10),   # dark rust
    (220, 110,  20),   # bright orange
    (170,  80,  30),   # warm brown
    (130,  55,  20),   # chestnut
]

class FallingLeaf:
    def __init__(self, width, height, ground_y, initial=False):
        self.w  = width
        self.h  = height
        self.gy = ground_y
        self._reset(initial)

    def _reset(self, initial=False):
        self.x     = random.uniform(0, self.w)
        self.y     = random.uniform(-40, -5) if not initial \
                     else random.uniform(-40, self.gy * 0.9)
        self.vy    = random.uniform(28, 65)     # fall speed
        self.vx    = random.uniform(-22, 22)    # drift
        self.rot   = random.uniform(0, 360)
        self.rot_v = random.uniform(-90, 90)    # rotation speed deg/sec
        self.color = random.choice(LEAF_COLORS)
        self.size  = random.uniform(5, 11)
        # Wind gust phase
        self.gust_phase = random.uniform(0, math.pi * 2)
        self.gust_freq  = random.uniform(0.6, 1.8)

    def update(self, dt, wind_strength):
        gust     = math.sin(self.gust_phase + pygame.time.get_ticks()/1000 * self.gust_freq)
        self.x  += (self.vx + gust * wind_strength * 18) * dt
        self.y  += self.vy * dt
        self.rot += self.rot_v * dt

        if self.y > self.gy + 10 or self.x < -30 or self.x > self.w + 30:
            self._reset()

    def draw(self, surface):
        angle = math.radians(self.rot)
        s = self.size
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Leaf shape: pointed oval rotated
        def rot_pt(lx, ly):
            rx = lx * cos_a - ly * sin_a + self.x
            ry = lx * sin_a + ly * cos_a + self.y
            return (int(rx), int(ry))

        pts = []
        n = 10
        for i in range(n):
            t   = i / n
            # Ellipse with pointed tips
            lx  = math.sin(t * math.pi * 2) * s * 0.55
            ly  = math.cos(t * math.pi * 2) * s
            pts.append(rot_pt(lx, ly))

        if len(pts) >= 3:
            pygame.draw.polygon(surface, self.color, pts)
            # Midrib vein
            tip1 = rot_pt(0,  s * 0.92)
            tip2 = rot_pt(0, -s * 0.92)
            vein_col = tuple(max(0, c - 35) for c in self.color)
            pygame.draw.line(surface, vein_col, tip1, tip2, 1)


# ─────────────────────────────────────────────────────────────────────────────
#  RAIN
# ─────────────────────────────────────────────────────────────────────────────
class RainDrop:
    def __init__(self, width, height):
        self.w  = width
        self.h  = height
        self._reset(initial=True)

    def _reset(self, initial=False):
        self.x   = random.uniform(0, self.w)
        self.y   = random.uniform(-self.h * 0.5, 0) if not initial \
                   else random.uniform(0, self.h)
        self.vy  = random.uniform(280, 420)
        self.len = random.uniform(8, 18)
        self.a   = random.randint(50, 110)   # alpha

    def update(self, dt):
        self.x -= self.vy * 0.18 * dt   # diagonal
        self.y += self.vy * dt
        if self.y > self.h + 20:
            self._reset()

    def draw(self, surface, rain_surf):
        ex = self.x - self.len * 0.18
        ey = self.y + self.len
        pygame.draw.line(rain_surf, (180, 190, 210, self.a),
                         (int(self.x), int(self.y)),
                         (int(ex), int(ey)), 1)


# ─────────────────────────────────────────────────────────────────────────────
#  WIND WISPS
# ─────────────────────────────────────────────────────────────────────────────
class WindWisp:
    def __init__(self, width, height, ground_y):
        self.w  = width
        self.h  = height
        self.gy = ground_y
        self._reset(initial=True)

    def _reset(self, initial=False):
        self.y      = random.uniform(self.gy * 0.2, self.gy * 0.85)
        self.x      = -random.uniform(50, 200) if not initial \
                      else random.uniform(-200, self.w)
        self.speed  = random.uniform(180, 340)
        self.length = random.uniform(60, 160)
        self.alpha  = random.randint(25, 65)
        self.wave_a = random.uniform(0, math.pi * 2)
        self.thick  = random.choice([1, 1, 2])

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > self.w + 50:
            self._reset()

    def draw(self, surface):
        # Draw as a wavy horizontal streak
        pts = []
        steps = 16
        for i in range(steps + 1):
            t  = i / steps
            px = self.x + t * self.length
            py = self.y + math.sin(t * math.pi * 3 + self.wave_a) * 3
            pts.append((int(px), int(py)))
        if len(pts) >= 2:
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.lines(s, (220, 200, 180, self.alpha), False, pts, self.thick)
            surface.blit(s, (0, 0))


# ─────────────────────────────────────────────────────────────────────────────
#  AUTUMN GRASS
# ─────────────────────────────────────────────────────────────────────────────
class AutumnGrassBlade:
    def __init__(self, x, ground_y):
        self.bx     = x
        self.gy     = ground_y
        self.h      = random.randint(14, 38)
        self.lean   = random.uniform(-0.5, 0.5)
        self.thick  = 1
        self.sway_p = random.uniform(0, math.pi * 2)
        self.sway_f = random.uniform(0.8, 1.6)
        # Dry autumn colors
        g = random.randint(60, 100)
        self.color     = (g + random.randint(20, 50), g, random.randint(5, 20))
        self.tip_color = (self.color[0] + 20, self.color[1] + 10, 10)

    def draw(self, surface, wind_t):
        wind  = math.sin(wind_t * self.sway_f + self.sway_p) * 0.25
        lean  = self.lean + wind
        h     = self.h
        bx, by= self.bx, self.gy

        tip_x  = bx + math.sin(lean) * h
        tip_y  = by - math.cos(lean) * h
        ctrl_x = bx + math.sin(lean) * h * 0.5 + math.cos(lean) * h * 0.12
        ctrl_y = by - math.cos(lean) * h * 0.5

        steps = 5
        prev  = (bx, by)
        for i in range(1, steps + 1):
            t  = i / steps
            x  = (1-t)**2*bx + 2*(1-t)*t*ctrl_x + t**2*tip_x
            y  = (1-t)**2*by + 2*(1-t)*t*ctrl_y + t**2*tip_y
            r  = int(self.color[0] + (self.tip_color[0]-self.color[0])*t)
            g  = int(self.color[1] + (self.tip_color[1]-self.color[1])*t)
            b  = int(self.color[2] + (self.tip_color[2]-self.color[2])*t)
            pygame.draw.line(surface, (r, g, b),
                             (int(prev[0]), int(prev[1])),
                             (int(x), int(y)), self.thick)
            prev = (x, y)


class AutumnGround:
    def __init__(self, width, height, ground_y):
        self.width   = width
        self.height  = height
        self.gy      = ground_y
        self.elapsed = 0.0
        # Sparse dry blades
        self.blades  = [
            AutumnGrassBlade(x + random.randint(-4, 4), ground_y)
            for x in range(0, width, 8)
        ]

    def update(self, dt):
        self.elapsed += dt

    def draw(self, surface):
        strip = self.height - self.gy
        for y in range(strip):
            t = y / max(strip - 1, 1)
            r = int(GROUND_TOP[0] + (GROUND_BOT[0]-GROUND_TOP[0])*t)
            g = int(GROUND_TOP[1] + (GROUND_BOT[1]-GROUND_TOP[1])*t)
            b = int(GROUND_TOP[2] + (GROUND_BOT[2]-GROUND_TOP[2])*t)
            pygame.draw.line(surface, (r, g, b),
                             (0, self.gy+y), (self.width, self.gy+y))
        for blade in self.blades:
            blade.draw(surface, self.elapsed)


# ─────────────────────────────────────────────────────────────────────────────
#  AUTUMN FIGURES
#  Daughter walks ahead, slightly turned away.
#  Mother walks behind, one arm gently reaching forward.
# ─────────────────────────────────────────────────────────────────────────────
COL = SILHOUETTE

def _poly(surface, pts):
    if len(pts) >= 3:
        pygame.draw.polygon(surface, COL, [(int(x), int(y)) for x, y in pts])

def _circle(surface, cx, cy, r):
    pygame.draw.circle(surface, COL, (int(cx), int(cy)), max(1, int(r)))

def _line(surface, x1, y1, x2, y2, w):
    pygame.draw.line(surface, COL,
                     (int(x1), int(y1)), (int(x2), int(y2)), max(1, int(w)))

def _ellipse(surface, cx, cy, w, h):
    rect = (int(cx-w/2), int(cy-h/2), int(w), int(h))
    if rect[2] > 0 and rect[3] > 0:
        pygame.draw.ellipse(surface, COL, rect)


def _draw_long_hair(surface, cx, head_top, head_r, walk_t, sway):
    length    = head_r * 4.0
    width_top = head_r * 1.05
    left_pts, right_pts = [], []
    for i in range(13):
        t      = i / 12
        billow = math.sin(t * math.pi) * head_r * 0.65
        wave   = math.sin(walk_t * 0.6 + t * math.pi * 1.3) * (head_r*0.12 + t*head_r*0.45)
        lx = cx - width_top - billow * 0.88 + wave * 0.30
        rx = cx + width_top * 0.28 + billow * 0.18 + wave * 0.14
        y  = head_top + t * length
        left_pts.append((lx, y))
        right_pts.append((rx, y))
    crown   = [(cx - width_top, head_top), (cx + width_top * 0.28, head_top)]
    all_pts = crown + right_pts[::-1] + left_pts[::-1]
    _poly(surface, all_pts)


def _draw_medium_hair(surface, cx, head_top, head_r, walk_t, sway):
    length    = head_r * 3.2
    width_top = head_r * 1.10
    left_pts, right_pts = [], []
    for i in range(11):
        t      = i / 10
        billow = math.sin(t * math.pi) * head_r * 0.50
        wave   = math.sin(walk_t * 0.45 + t * math.pi) * (head_r*0.08 + t*head_r*0.28)
        lx = cx - width_top - billow * 0.82 + wave * 0.22
        rx = cx + width_top * 0.32 + billow * 0.18 + wave * 0.12
        y  = head_top + t * length
        left_pts.append((lx, y))
        right_pts.append((rx, y))
    crown   = [(cx - width_top, head_top), (cx + width_top * 0.32, head_top)]
    all_pts = crown + right_pts[::-1] + left_pts[::-1]
    _poly(surface, all_pts)


def _draw_skirt(surface, cx, waist_y, skirt_len, waist_w, hem_w, walk_t):
    hem_y   = waist_y + skirt_len
    ripple  = math.sin(walk_t * 2.0) * 4
    ripple2 = math.sin(walk_t * 2.0 + 1.1) * 3
    drift   = math.sin(walk_t * 0.9) * 3
    pts = [
        (cx - waist_w,                     waist_y),
        (cx + waist_w,                     waist_y),
        (cx + hem_w + ripple2 + drift,     hem_y + ripple * 0.35),
        (cx + drift * 0.3,                 hem_y - skirt_len*0.04 + ripple*0.18),
        (cx - drift * 0.2,                 hem_y - skirt_len*0.05 - ripple2*0.18),
        (cx - hem_w + ripple + drift*0.4,  hem_y - ripple2 * 0.28),
    ]
    _poly(surface, pts)


class AutumnDaughter:
    """Walks ahead, slightly hunched, turned away — distant."""
    HEIGHT    = 110
    SPEED     = 42
    STEP_FREQ = 1.8

    def __init__(self, x, ground_y):
        self.x        = float(x)
        self.ground_y = float(ground_y)
        self.elapsed  = 0.0
        h = self.HEIGHT
        self.head_r    = h * 0.115
        self.neck_h    = h * 0.038
        self.torso_h   = h * 0.215
        self.skirt_h   = h * 0.200
        self.upper_leg = h * 0.205
        self.lower_leg = h * 0.195
        self.upper_arm = h * 0.160
        self.lower_arm = h * 0.130
        self.body_w    = h * 0.088

    def update(self, dt):
        self.elapsed += dt
        self.x       += self.SPEED * dt

    def draw(self, surface):
        cx    = self.x
        t     = self.elapsed * self.STEP_FREQ * math.pi * 2
        # Slower, heavier walk — less bounce
        bounce= abs(math.sin(t)) * 2.0
        walk_t= self.elapsed * self.STEP_FREQ

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce * 0.3
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r

        # ── LEGS ─────────────────────────────────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.42
            knee_b = abs(math.sin(t + phase)) * 0.28
            kx = cx + math.sin(leg_a) * self.upper_leg * 0.70
            ky = hip_y + math.cos(leg_a) * self.upper_leg
            lower_a = leg_a + knee_b
            fx = kx + math.sin(lower_a) * self.lower_leg * 0.85
            fy = ky + self.lower_leg * math.cos(lower_a) * 0.90
            _line(surface, cx, hip_y, kx, ky, self.body_w * 1.12)
            _line(surface, kx, ky, fx, fy,   self.body_w * 0.88)
            shoe_d = 1 if math.sin(t+phase) > 0 else -1
            shoe_pts = [
                (fx, fy),
                (fx + shoe_d*self.body_w*0.45, fy - self.body_w*0.28),
                (fx + shoe_d*self.body_w*1.90, fy),
                (fx + shoe_d*self.body_w*1.75, fy + self.body_w*0.42),
                (fx - shoe_d*self.body_w*0.18, fy + self.body_w*0.42),
            ]
            _poly(surface, shoe_pts)

        # ── SKIRT ─────────────────────────────────────────────────────────────
        _draw_skirt(surface, cx, waist_y, self.skirt_h,
                    self.body_w*1.08, self.body_w*2.20, walk_t)

        # ── TORSO (slight forward hunch) ──────────────────────────────────────
        torso_pts = [
            (cx - self.body_w*1.0,  waist_y),
            (cx + self.body_w*1.0,  waist_y),
            (cx + self.body_w*0.88, chest_y + 2),
            (cx - self.body_w*0.72, chest_y + 2),
        ]
        _poly(surface, torso_pts)

        # ── ARMS — both angled slightly downward/forward ───────────────────────
        shoulder_y = chest_y + self.head_r * 0.15
        for side, phase in [(1, 0), (-1, math.pi)]:
            arm_a  = math.sin(t + phase + math.pi) * 0.30
            # Arms hang lower — tired, withdrawn
            arm_a_adj = arm_a - 0.25
            elbow_x = cx + math.sin(arm_a_adj) * self.upper_arm * 0.80
            elbow_y = shoulder_y + self.upper_arm * 0.85
            fore_a  = arm_a_adj + 0.15
            hand_x  = elbow_x + math.sin(fore_a) * self.lower_arm * 0.78
            hand_y  = elbow_y + self.lower_arm * 0.75
            _line(surface, cx, shoulder_y, elbow_x, elbow_y, self.body_w*0.75)
            _line(surface, elbow_x, elbow_y, hand_x, hand_y, self.body_w*0.58)
            _circle(surface, hand_x, hand_y, self.body_w*0.40)

        # ── HEAD (slightly bowed) ─────────────────────────────────────────────
        _line(surface, cx, neck_y, cx, neck_y + self.neck_h, self.body_w*0.50)
        _circle(surface, cx, head_cy + 2, self.head_r)   # +2 = slight bow

        # ── LONG HAIR ─────────────────────────────────────────────────────────
        _draw_long_hair(surface, cx, head_cy - self.head_r*0.93 + 2,
                        self.head_r, walk_t,
                        sway=math.sin(self.elapsed*0.9)*0.18)


class AutumnMother:
    """Follows behind, one arm reaching forward toward the daughter."""
    HEIGHT    = 130
    SPEED     = 36
    STEP_FREQ = 1.6

    def __init__(self, x, ground_y):
        self.x        = float(x)
        self.ground_y = float(ground_y)
        self.elapsed  = 0.0
        h = self.HEIGHT
        self.head_r    = h * 0.112
        self.neck_h    = h * 0.038
        self.torso_h   = h * 0.235
        self.skirt_h   = h * 0.340
        self.upper_leg = h * 0.178
        self.lower_leg = h * 0.175
        self.upper_arm = h * 0.168
        self.lower_arm = h * 0.148
        self.body_w    = h * 0.082

    def update(self, dt):
        self.elapsed += dt
        self.x       += self.SPEED * dt

    def draw(self, surface):
        cx    = self.x
        t     = self.elapsed * self.STEP_FREQ * math.pi * 2
        bounce= abs(math.sin(t)) * 1.5
        walk_t= self.elapsed * self.STEP_FREQ

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce * 0.25
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r
        hem_y   = waist_y + self.skirt_h

        # ── LEGS (beneath long skirt) ─────────────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.35
            kx = cx + math.sin(leg_a) * self.upper_leg * 0.52
            ky = hip_y + self.upper_leg
            lower_a = leg_a * 0.50
            fx = kx + math.sin(lower_a) * self.lower_leg * 0.80
            fy = ky + self.lower_leg * 0.86
            if fy > hem_y - 6:
                draw_from_y = max(ky, hem_y - 4)
                _line(surface, kx, draw_from_y, fx, fy, self.body_w * 0.92)
                shoe_d = 1 if math.sin(t+phase) > 0 else -1
                shoe_pts = [
                    (fx, fy),
                    (fx + shoe_d*self.body_w*0.38, fy - self.body_w*0.22),
                    (fx + shoe_d*self.body_w*1.80, fy - self.body_w*0.08),
                    (fx + shoe_d*self.body_w*1.80, fy + self.body_w*0.38),
                    (fx - shoe_d*self.body_w*0.10, fy + self.body_w*0.38),
                    (fx - shoe_d*self.body_w*0.28, fy + self.body_w*0.52),
                    (fx - shoe_d*self.body_w*0.55, fy + self.body_w*0.52),
                    (fx - shoe_d*self.body_w*0.55, fy + self.body_w*0.14),
                ]
                _poly(surface, shoe_pts)

        # ── LONG SKIRT ────────────────────────────────────────────────────────
        _draw_skirt(surface, cx, waist_y, self.skirt_h,
                    self.body_w*1.12, self.body_w*3.30, walk_t)

        # ── TORSO ─────────────────────────────────────────────────────────────
        torso_pts = [
            (cx - self.body_w*1.04, waist_y),
            (cx + self.body_w*1.04, waist_y),
            (cx + self.body_w*0.82, chest_y),
            (cx - self.body_w*0.82, chest_y),
        ]
        _poly(surface, torso_pts)

        # ── ARMS ──────────────────────────────────────────────────────────────
        shoulder_y = chest_y + self.head_r * 0.18

        # Left arm — normal swing
        arm_a_l  = math.sin(t + math.pi) * 0.28
        elbow_lx = cx + math.sin(arm_a_l) * self.upper_arm * 0.82
        elbow_ly = shoulder_y + self.upper_arm * 0.74
        fore_l   = arm_a_l + 0.16
        hand_lx  = elbow_lx + math.sin(fore_l) * self.lower_arm * 0.78
        hand_ly  = elbow_ly + self.lower_arm * 0.70
        _line(surface, cx, shoulder_y, elbow_lx, elbow_ly, self.body_w*0.78)
        _line(surface, elbow_lx, elbow_ly, hand_lx, hand_ly, self.body_w*0.60)
        _circle(surface, hand_lx, hand_ly, self.body_w*0.42)

        # RIGHT arm — reaching forward toward daughter (key emotional gesture)
        reach_progress = (math.sin(self.elapsed * 0.8) + 1) / 2
        reach_angle    = 0.55 + reach_progress * 0.25   # reaches forward (positive = toward daughter ahead)
        elbow_rx = cx + math.sin(reach_angle) * self.upper_arm * 1.05
        elbow_ry = shoulder_y + self.upper_arm * 0.55
        fore_r   = reach_angle + 0.30
        hand_rx  = elbow_rx + math.sin(fore_r) * self.lower_arm * 1.05
        hand_ry  = elbow_ry + self.lower_arm * 0.52
        _line(surface, cx, shoulder_y, elbow_rx, elbow_ry, self.body_w*0.78)
        _line(surface, elbow_rx, elbow_ry, hand_rx, hand_ry, self.body_w*0.60)
        _circle(surface, hand_rx, hand_ry, self.body_w*0.42)

        # ── HEAD ──────────────────────────────────────────────────────────────
        _line(surface, cx, neck_y, cx, neck_y + self.neck_h, self.body_w*0.50)
        _circle(surface, cx, head_cy, self.head_r)

        # ── MEDIUM HAIR ───────────────────────────────────────────────────────
        _draw_medium_hair(surface, cx, head_cy - self.head_r*0.93,
                          self.head_r, walk_t,
                          sway=math.sin(self.elapsed*0.75)*0.18)

        # ── EARRING ───────────────────────────────────────────────────────────
        ear_x = cx + self.head_r * 0.88
        ear_y = head_cy + self.head_r * 0.28
        _circle(surface, ear_x, ear_y, max(1, int(self.head_r*0.12)))
        _line(surface, ear_x, ear_y + self.head_r*0.12,
              ear_x, ear_y + self.head_r*0.40, max(1, int(self.head_r*0.09)))
        _circle(surface, ear_x, ear_y + self.head_r*0.50,
                max(1, int(self.head_r*0.15)))


class AutumnFigures:
    DAUGHTER_LEAD = 130   # daughter further ahead — more distance between them

    def __init__(self, screen_w, ground_y):
        fig_y = ground_y - 2
        self.sw       = screen_w
        self.mother   = AutumnMother  (x=-150,                       ground_y=fig_y)
        self.daughter = AutumnDaughter(x=-150 + self.DAUGHTER_LEAD,  ground_y=fig_y)

    def update(self, dt):
        self.mother.update(dt)
        self.daughter.update(dt)
        if self.mother.x > self.sw + 180:
            self.mother.x   = -160
            self.daughter.x = -160 + self.DAUGHTER_LEAD

    def draw(self, surface):
        self.mother.draw(surface)
        self.daughter.draw(surface)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE TEXT  (two lines, staggered appearance)
# ─────────────────────────────────────────────────────────────────────────────
class AutumnText:
    LINE1 = "Even in the seasons where I lost myself,"
    LINE2 = "you never stopped finding me.."
    LINE3 = "The older I grow,"
    LINE4 = "the more I understand the quiet ways you loved me."

    def __init__(self, width, height, font_path, appear_after=5.0):
        self.cx    = width // 2
        self.w     = width
        self.h     = height
        self.elapsed   = 0.0
        self.appear    = appear_after
        self.alpha1    = 0.0   # lines 1+2
        self.alpha2    = 0.0   # lines 3+4 (appear later)
        self.fade_spd  = 48

        try:
            font_l = pygame.font.Font(font_path, 48)
            font_s = pygame.font.Font(font_path, int(48 * 0.76))
        except FileNotFoundError:
            font_l = pygame.font.SysFont("serif", 48)
            font_s = pygame.font.SysFont("serif", int(48 * 0.76))

        col  = (30, 18, 8)     # deep warm charcoal
        glow = (100, 55, 20)   # amber glow

        self.s1 = font_l.render(self.LINE1, True, col)
        self.s2 = font_s.render(self.LINE2, True, col)
        self.s3 = font_l.render(self.LINE3, True, col)
        self.s4 = font_s.render(self.LINE4, True, col)
        self.g1 = font_l.render(self.LINE1, True, glow)
        self.g2 = font_s.render(self.LINE2, True, glow)
        self.g3 = font_l.render(self.LINE3, True, glow)
        self.g4 = font_s.render(self.LINE4, True, glow)

        line_h  = int(48 * 1.18)
        small_h = int(48 * 0.76 * 1.18)
        gap     = int(48 * 0.6)   # gap between the two pairs

        # Position first pair in upper third
        self.y1 = int(height * 0.18)
        self.y2 = self.y1 + line_h
        # Second pair below with gap
        self.y3 = self.y2 + small_h + gap
        self.y4 = self.y3 + line_h

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.appear:
            self.alpha1 = min(255, self.alpha1 + self.fade_spd * dt)
        # Second pair appears 4 seconds after first
        if self.elapsed > self.appear + 4.0:
            self.alpha2 = min(255, self.alpha2 + self.fade_spd * dt)

    def _blit_line(self, surface, surf, glow, x, y, alpha):
        if alpha <= 0:
            return
        a = int(alpha)
        if alpha >= 255:
            a = max(0, min(255, 255 + int(math.sin(self.elapsed * 0.55) * 5)))
        ga = max(0, a - 130)
        if ga > 0:
            glow.set_alpha(ga // 4)
            for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
                surface.blit(glow, (x+ox, y+oy))
        surf.set_alpha(a)
        surface.blit(surf, (x, y))

    def draw(self, surface):
        for surf, glow, y, alpha in [
            (self.s1, self.g1, self.y1, self.alpha1),
            (self.s2, self.g2, self.y2, self.alpha1),
            (self.s3, self.g3, self.y3, self.alpha2),
            (self.s4, self.g4, self.y4, self.alpha2),
        ]:
            x = self.cx - surf.get_width() // 2
            self._blit_line(surface, surf, glow, x, y, alpha)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN SCENE CLASS
# ─────────────────────────────────────────────────────────────────────────────
class Autumn:
    SCENE_DURATION = 20.0    # longer — two text pairs need time
    FADE_DURATION  = 2.8

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self._build()

    def _build(self):
        # Static sky
        self.sky_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_autumn_sky(self.sky_surf, WIDTH, HEIGHT, GROUND_Y)

        # Hills
        self.hill_far  = make_hill(WIDTH, GROUND_Y, 60, 2.0, GROUND_Y-170, phase=0.5)
        self.hill_mid  = make_hill(WIDTH, GROUND_Y, 48, 1.6, GROUND_Y-120, phase=1.4)
        self.hill_near = make_hill(WIDTH, GROUND_Y, 32, 2.4, GROUND_Y- 75, phase=2.2)

        # Trees — mix of bare and half-bare, positioned on hills
        self.trees = [
            Tree(int(WIDTH * 0.08), GROUND_Y - 58, height=130, bare_ratio=0.85),
            Tree(int(WIDTH * 0.18), GROUND_Y - 48, height=110, bare_ratio=0.55),
            Tree(int(WIDTH * 0.72), GROUND_Y - 52, height=125, bare_ratio=0.70),
            Tree(int(WIDTH * 0.82), GROUND_Y - 44, height=100, bare_ratio=0.40),
            Tree(int(WIDTH * 0.92), GROUND_Y - 50, height=115, bare_ratio=0.90),
            Tree(int(WIDTH * 0.55), GROUND_Y - 40, height= 95, bare_ratio=0.60),
        ]

        # Ground
        self.ground = AutumnGround(WIDTH, HEIGHT, GROUND_Y)

        # Leaves
        self.leaves = [FallingLeaf(WIDTH, HEIGHT, GROUND_Y, initial=True)
                       for _ in range(80)]

        # Rain
        self.raindrops = [RainDrop(WIDTH, HEIGHT) for _ in range(200)]
        self.rain_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Wind wisps
        self.wisps = [WindWisp(WIDTH, HEIGHT, GROUND_Y) for _ in range(10)]

        # Wind strength varies over time
        self.wind_t   = 0.0
        self.wind_str = 1.0   # updated each frame

        # Figures
        self.figures = AutumnFigures(WIDTH, ground_y=GROUND_Y)

        # Text
        self.text = AutumnText(WIDTH, HEIGHT, FONT_PATH, appear_after=5.0)

        # Fade
        self.fade_surf  = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surf.fill((0, 0, 0))
        self.fade_alpha = 0
        self.elapsed    = 0.0
        self.fading_out = False
        self._fade_start= 0.0

        # Fade in
        self.fade_in     = True
        self.fade_in_dur = 2.0

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
                self.fade_alpha = max(0, int(255*(1 - self.elapsed/self.fade_in_dur)))
                if self.elapsed >= self.fade_in_dur:
                    self.fade_in    = False
                    self.fade_alpha = 0

            # Fade out
            if self.elapsed >= self.SCENE_DURATION and not self.fading_out:
                self.fading_out  = True
                self._fade_start = self.elapsed
            if self.fading_out:
                p = (self.elapsed - self._fade_start) / self.FADE_DURATION
                self.fade_alpha = min(255, int(p * 255))
                if self.fade_alpha >= 255:
                    running = False

            # Wind strength — gusts every ~5 seconds
            self.wind_t   += dt
            self.wind_str  = 0.6 + math.sin(self.wind_t * 0.38) * 0.4 \
                           + abs(math.sin(self.wind_t * 0.9)) * 0.6

            # Update
            self.ground.update(dt)
            for leaf in self.leaves:
                leaf.update(dt, self.wind_str)
            for drop in self.raindrops:
                drop.update(dt)
            for wisp in self.wisps:
                wisp.update(dt)
            self.figures.update(dt)
            self.text.update(dt)

            self._draw()

        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def _draw(self):
        # 1. Sky
        self.screen.blit(self.sky_surf, (0, 0))

        # 2. Hills far → near
        pygame.draw.polygon(self.screen, HILL_FAR,     self.hill_far)
        pygame.draw.polygon(self.screen, HILL_MID_COL, self.hill_mid)
        pygame.draw.polygon(self.screen, HILL_NEAR,    self.hill_near)

        # 3. Trees (behind ground)
        for tree in self.trees:
            tree.draw(self.screen)

        # 4. Ground + dry grass
        self.ground.draw(self.screen)

        # 5. Figures
        self.figures.draw(self.screen)

        # 6. Falling leaves (in front of figures)
        for leaf in self.leaves:
            leaf.draw(self.screen)

        # 7. Wind wisps
        for wisp in self.wisps:
            wisp.draw(self.screen)

        # 8. Rain overlay
        self.rain_surf.fill((0, 0, 0, 0))
        for drop in self.raindrops:
            drop.draw(self.screen, self.rain_surf)
        self.screen.blit(self.rain_surf, (0, 0))

        # 9. Text
        self.text.draw(self.screen)

        # 10. Fade overlay
        if self.fade_alpha > 0:
            self.fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surf, (0, 0))

        pygame.display.update()