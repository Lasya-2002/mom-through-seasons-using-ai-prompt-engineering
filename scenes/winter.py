import pygame
import math
import random
from settings import *

# ─────────────────────────────────────────────────────────────────────────────
#  scenes/winter.py  —  "Mom Through Seasons"
#
#  The final scene. Still. Peaceful. Coming home.
#  Elements:
#    • Deep midnight blue → soft blue-grey sky
#    • Snow-covered rolling hills (white, rounded)
#    • Bare trees with snow caps on every branch
#    • Slow peaceful snowfall — large lazy flakes
#    • Warm glowing lantern in background
#    • Soft star field with gentle twinkle
#    • Faint aurora wisps in the sky
#    • Mother and daughter walking side by side, together
#    • Sparkling snow motes on the ground
#    • Three-part text: poem → Happy Mother's Day → closing line
#    • Fade in from black, hold, fade out
# ─────────────────────────────────────────────────────────────────────────────

FONT_PATH = "C:/Users/mvsla/OneDrive/Desktop/Mother's day gift/assets/fonts/GreatVibes-Regular.ttf"
GROUND_Y  = HEIGHT - 80

# ── Palette ───────────────────────────────────────────────────────────────────
SKY_TOP       = ( 10,  15,  40)   # deep midnight blue
SKY_MID       = ( 30,  45,  80)   # mid blue
SKY_HORIZON   = ( 80,  95, 130)   # soft blue-grey horizon
HILL_FAR      = (200, 215, 230)   # far snow hill — almost white
HILL_MID_COL  = (220, 232, 242)   # mid
HILL_NEAR_COL = (235, 245, 252)   # near — brightest
GROUND_COL    = (240, 248, 255)   # ground snow
SILHOUETTE    = ( 15,  10,  20)   # cold near-black


# ─────────────────────────────────────────────────────────────────────────────
#  SKY
# ─────────────────────────────────────────────────────────────────────────────
def draw_winter_sky(surface, width, height, ground_y):
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
#  STARS
# ─────────────────────────────────────────────────────────────────────────────
class StarField:
    def __init__(self, width, height, ground_y, count=120):
        self.stars = []
        for _ in range(count):
            x     = random.uniform(0, width)
            y     = random.uniform(0, ground_y * 0.88)
            size  = random.choice([1, 1, 1, 2])
            phase = random.uniform(0, math.pi * 2)
            freq  = random.uniform(0.3, 1.1)
            base_a= random.randint(140, 220)
            self.stars.append((x, y, size, phase, freq, base_a))

    def draw(self, surface, elapsed):
        for x, y, size, phase, freq, base_a in self.stars:
            twinkle = math.sin(elapsed * freq + phase)
            a = int(base_a + twinkle * 40)
            a = max(60, min(255, a))
            s = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 230, 255, a), (size*2, size*2), size)
            surface.blit(s, (int(x) - size*2, int(y) - size*2))


# ─────────────────────────────────────────────────────────────────────────────
#  AURORA
# ─────────────────────────────────────────────────────────────────────────────
class Aurora:
    """Faint slow-moving aurora bands in the upper sky."""
    def __init__(self, width, height, ground_y):
        self.w  = width
        self.h  = height
        self.gy = ground_y
        # Each band: (y_base, color, phase, amplitude, frequency)
        self.bands = [
            (height * 0.10, ( 40, 160,  80, 18), 0.0,       22, 0.18),
            (height * 0.16, ( 80,  60, 160, 14), math.pi,   18, 0.22),
            (height * 0.08, ( 20, 120, 100, 12), math.pi/2, 26, 0.15),
            (height * 0.20, ( 60,  40, 140, 10), 1.2,       20, 0.20),
        ]

    def draw(self, surface, elapsed):
        for y_base, color, phase, amp, freq in self.bands:
            pts_top, pts_bot = [], []
            steps = self.w // 6
            for i in range(steps + 1):
                x  = i * 6
                dy = math.sin(x * 0.008 + elapsed * freq + phase) * amp
                pts_top.append((x, int(y_base + dy - 8)))
                pts_bot.append((x, int(y_base + dy + 8)))

            # Draw as a soft filled band
            all_pts = pts_top + pts_bot[::-1]
            if len(all_pts) >= 3:
                s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                pygame.draw.polygon(s, color, all_pts)
                surface.blit(s, (0, 0))


# ─────────────────────────────────────────────────────────────────────────────
#  HILLS (snow-covered)
# ─────────────────────────────────────────────────────────────────────────────
def make_snow_hill(width, ground_y, amplitude, frequency, y_offset, phase=0):
    pts = [(0, ground_y)]
    for i in range(width // 3 + 1):
        x = i * 3
        y = y_offset + math.sin((x/width)*math.pi*frequency + phase)*amplitude
        pts.append((x, y))
    pts.append((width, ground_y))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
#  SNOW TREE
# ─────────────────────────────────────────────────────────────────────────────
class SnowTree:
    def __init__(self, x, ground_y, height):
        self.x        = x
        self.ground_y = ground_y
        self.height   = height
        self.trunk_w  = max(3, int(height * 0.050))
        self.branches = self._make_branches()
        # Pre-bake snow cap positions
        self.snow_caps = []
        for x1, y1, x2, y2, w, depth in self.branches:
            if depth <= 2:
                cap_w = max(4, int(w * 3.5 - depth * 2))
                cap_h = max(2, cap_w // 3)
                self.snow_caps.append((x2, y2, cap_w, cap_h))

    def _make_branches(self):
        branches = []
        def add(x1, y1, angle, length, depth, width):
            if depth == 0 or length < 4:
                return
            x2 = x1 + math.sin(angle) * length
            y2 = y1 - math.cos(angle) * length
            branches.append((x1, y1, x2, y2, width, depth))
            spread  = random.uniform(0.32, 0.52)
            spread2 = random.uniform(0.32, 0.52)
            add(x2, y2, angle - spread,  length*random.uniform(0.62,0.72),
                depth-1, max(1,width-1))
            add(x2, y2, angle + spread2, length*random.uniform(0.62,0.72),
                depth-1, max(1,width-1))
            if depth > 2 and random.random() < 0.40:
                add(x2, y2, angle+random.uniform(-0.18,0.18),
                    length*0.52, depth-2, max(1,width-1))

        trunk_top = self.ground_y - self.height * 0.36
        add(self.x, trunk_top, 0, self.height*0.30, depth=5,
            width=max(2, self.trunk_w-2))
        return branches

    def draw(self, surface):
        # Trunk
        trunk_top = int(self.ground_y - self.height * 0.36)
        pygame.draw.line(surface, SILHOUETTE,
                         (int(self.x), int(self.ground_y)),
                         (int(self.x), trunk_top), self.trunk_w)
        # Branches
        for x1, y1, x2, y2, w, depth in self.branches:
            pygame.draw.line(surface, SILHOUETTE,
                             (int(x1),int(y1)), (int(x2),int(y2)), w)
        # Snow caps on branch tips
        for sx, sy, cw, ch in self.snow_caps:
            pygame.draw.ellipse(surface, (240, 248, 255),
                                (int(sx-cw//2), int(sy-ch//2), cw, ch))


# ─────────────────────────────────────────────────────────────────────────────
#  LANTERN
# ─────────────────────────────────────────────────────────────────────────────
class Lantern:
    def __init__(self, x, ground_y):
        self.x       = x
        self.ground_y= ground_y
        self.pole_h  = 110
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt

    def draw(self, surface):
        t  = self.elapsed
        cx = int(self.x)
        by = int(self.ground_y)
        ty = by - self.pole_h

        # Pole
        pygame.draw.line(surface, SILHOUETTE, (cx, by), (cx, ty), 3)
        # Arm
        arm_end_x = cx + 22
        arm_end_y = ty + 18
        pygame.draw.line(surface, SILHOUETTE, (cx, ty), (arm_end_x, arm_end_y), 2)

        # Glow — pulsing warm amber light
        pulse = (math.sin(t * 1.4) + 1) / 2
        lx, ly = arm_end_x + 2, arm_end_y + 14

        for radius, alpha in [
            (55, int(12 + pulse * 6)),
            (38, int(22 + pulse * 10)),
            (24, int(40 + pulse * 18)),
            (14, int(70 + pulse * 30)),
            ( 7, int(130 + pulse * 60)),
        ]:
            gs = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 200, 80, alpha), (radius, radius), radius)
            surface.blit(gs, (lx - radius, ly - radius))

        # Lantern body (small box)
        box_w, box_h = 10, 14
        pygame.draw.rect(surface, SILHOUETTE,
                         (lx - box_w//2, ly - box_h//2, box_w, box_h), 2)
        # Warm fill
        inner = pygame.Surface((box_w-2, box_h-2), pygame.SRCALPHA)
        inner.fill((255, 200, 80, int(160 + pulse*60)))
        surface.blit(inner, (lx - box_w//2 + 1, ly - box_h//2 + 1))


# ─────────────────────────────────────────────────────────────────────────────
#  SNOWFLAKE
# ─────────────────────────────────────────────────────────────────────────────
class Snowflake:
    def __init__(self, width, height, ground_y, initial=False):
        self.w  = width
        self.h  = height
        self.gy = ground_y
        self._reset(initial)

    def _reset(self, initial=False):
        self.x    = random.uniform(0, self.w)
        self.y    = random.uniform(-20, -2) if not initial \
                    else random.uniform(-20, self.gy)
        # Slow, peaceful fall
        self.vy   = random.uniform(18, 45)
        self.vx   = random.uniform(-8, 8)
        self.rot  = random.uniform(0, 360)
        self.rot_v= random.uniform(-20, 20)   # slow lazy spin
        self.size = random.uniform(3, 9)
        self.alpha= random.randint(160, 230)
        self.drift_phase = random.uniform(0, math.pi*2)
        self.drift_freq  = random.uniform(0.3, 0.8)
        self.kind = random.choice(["dot", "dot", "dot", "star", "star"])

    def update(self, dt):
        t = pygame.time.get_ticks() / 1000
        # Gentle horizontal drift (lazy float)
        drift = math.sin(t * self.drift_freq + self.drift_phase) * 12
        self.x += (self.vx + drift * 0.04) * dt
        self.y += self.vy * dt
        self.rot += self.rot_v * dt
        if self.y > self.gy + 10 or self.x < -30 or self.x > self.w + 30:
            self._reset()

    def draw(self, surface):
        if self.kind == "dot":
            # Soft circular flake
            s = pygame.Surface((int(self.size)*4, int(self.size)*4), pygame.SRCALPHA)
            r = int(self.size)
            pygame.draw.circle(s, (240, 248, 255, self.alpha),
                               (r*2, r*2), r)
            # Soft inner highlight
            if r > 2:
                pygame.draw.circle(s, (255, 255, 255, min(255, self.alpha + 40)),
                                   (r*2, r*2), max(1, r//2))
            surface.blit(s, (int(self.x) - r*2, int(self.y) - r*2))
        else:
            # Six-pointed star flake
            angle = math.radians(self.rot)
            cx, cy = self.x, self.y
            s = self.size
            for i in range(6):
                a  = angle + i * math.pi / 3
                ex = cx + math.cos(a) * s
                ey = cy + math.sin(a) * s
                surf = pygame.Surface((int(s*4)+4, int(s*4)+4), pygame.SRCALPHA)
                pygame.draw.line(surf, (240, 248, 255, self.alpha),
                                 (int(s*2), int(s*2)),
                                 (int(s*2 + math.cos(a)*s),
                                  int(s*2 + math.sin(a)*s)), 1)
                surface.blit(surf, (int(cx-s*2-2), int(cy-s*2-2)))
            # Center dot
            pygame.draw.circle(surface, (255,255,255,self.alpha),
                               (int(cx), int(cy)), max(1, int(s*0.28)))


# ─────────────────────────────────────────────────────────────────────────────
#  GROUND SPARKLES
# ─────────────────────────────────────────────────────────────────────────────
class GroundSparkle:
    def __init__(self, width, ground_y):
        self.w  = width
        self.gy = ground_y
        self.sparkles = [
            (random.uniform(0, width),
             random.uniform(ground_y, ground_y + 60),
             random.uniform(0, math.pi*2),
             random.uniform(0.5, 2.0),
             random.randint(1, 3))
            for _ in range(60)
        ]

    def draw(self, surface, elapsed):
        for x, y, phase, freq, size in self.sparkles:
            blink = (math.sin(elapsed * freq + phase) + 1) / 2
            if blink < 0.4:
                continue
            a = int(blink * 200)
            s = pygame.Surface((size*6, size*6), pygame.SRCALPHA)
            # Diamond sparkle shape
            cx, cy = size*3, size*3
            pts = [
                (cx,        cy - size*2.5),
                (cx + size, cy),
                (cx,        cy + size*2.5),
                (cx - size, cy),
            ]
            pygame.draw.polygon(s, (255, 255, 255, a), [(int(p[0]),int(p[1])) for p in pts])
            surface.blit(s, (int(x)-size*3, int(y)-size*3))


# ─────────────────────────────────────────────────────────────────────────────
#  WINTER FIGURES — mother and daughter TOGETHER, side by side
# ─────────────────────────────────────────────────────────────────────────────
COL = SILHOUETTE

def _poly(surface, pts):
    if len(pts) >= 3:
        pygame.draw.polygon(surface, COL, [(int(x),int(y)) for x,y in pts])

def _circle(surface, cx, cy, r):
    pygame.draw.circle(surface, COL, (int(cx),int(cy)), max(1,int(r)))

def _line(surface, x1, y1, x2, y2, w):
    pygame.draw.line(surface, COL,
                     (int(x1),int(y1)), (int(x2),int(y2)), max(1,int(w)))

def _ellipse(surface, cx, cy, w, h):
    rect = (int(cx-w/2), int(cy-h/2), int(w), int(h))
    if rect[2] > 0 and rect[3] > 0:
        pygame.draw.ellipse(surface, COL, rect)


def _draw_long_hair(surface, cx, head_top, head_r, walk_t):
    length    = head_r * 3.8
    width_top = head_r * 1.05
    left_pts, right_pts = [], []
    for i in range(12):
        t      = i / 11
        billow = math.sin(t * math.pi) * head_r * 0.55
        wave   = math.sin(walk_t * 0.4 + t * math.pi) * (head_r*0.08 + t*head_r*0.25)
        lx = cx - width_top - billow*0.85 + wave*0.20
        rx = cx + width_top*0.28 + billow*0.15 + wave*0.10
        left_pts.append((lx, head_top + t*length))
        right_pts.append((rx, head_top + t*length))
    crown   = [(cx-width_top, head_top),(cx+width_top*0.28, head_top)]
    _poly(surface, crown + right_pts[::-1] + left_pts[::-1])


def _draw_medium_hair(surface, cx, head_top, head_r, walk_t):
    length    = head_r * 3.0
    width_top = head_r * 1.08
    left_pts, right_pts = [], []
    for i in range(11):
        t      = i / 10
        billow = math.sin(t * math.pi) * head_r * 0.48
        wave   = math.sin(walk_t * 0.35 + t * math.pi) * (head_r*0.06 + t*head_r*0.22)
        lx = cx - width_top - billow*0.80 + wave*0.18
        rx = cx + width_top*0.30 + billow*0.16 + wave*0.10
        left_pts.append((lx, head_top + t*length))
        right_pts.append((rx, head_top + t*length))
    crown   = [(cx-width_top, head_top),(cx+width_top*0.30, head_top)]
    _poly(surface, crown + right_pts[::-1] + left_pts[::-1])


def _draw_skirt(surface, cx, waist_y, skirt_len, waist_w, hem_w, walk_t):
    hem_y   = waist_y + skirt_len
    ripple  = math.sin(walk_t * 1.6) * 3
    ripple2 = math.sin(walk_t * 1.6 + 1.0) * 2
    drift   = math.sin(walk_t * 0.7) * 2
    pts = [
        (cx - waist_w,                    waist_y),
        (cx + waist_w,                    waist_y),
        (cx + hem_w + ripple2 + drift,    hem_y + ripple*0.3),
        (cx + drift*0.3,                  hem_y - skirt_len*0.04),
        (cx - drift*0.2,                  hem_y - skirt_len*0.05),
        (cx - hem_w + ripple + drift*0.4, hem_y - ripple2*0.25),
    ]
    _poly(surface, pts)


class WinterDaughter:
    """Walks beside mother — calm, peaceful, present."""
    HEIGHT    = 110
    SPEED     = 30
    STEP_FREQ = 1.5

    def __init__(self, x, ground_y):
        self.x        = float(x)
        self.ground_y = float(ground_y)
        self.elapsed  = 0.0
        h = self.HEIGHT
        self.head_r    = h * 0.115
        self.neck_h    = h * 0.038
        self.torso_h   = h * 0.215
        self.skirt_h   = h * 0.210
        self.upper_leg = h * 0.205
        self.lower_leg = h * 0.195
        self.upper_arm = h * 0.160
        self.lower_arm = h * 0.130
        self.body_w    = h * 0.088

    def update(self, dt):
        self.elapsed += dt
        self.x       += self.SPEED * dt

    def draw(self, surface, mother_cx):
        cx    = self.x
        t     = self.elapsed * self.STEP_FREQ * math.pi * 2
        bounce= abs(math.sin(t)) * 1.6
        walk_t= self.elapsed * self.STEP_FREQ

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce*0.28
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r

        # ── LEGS ─────────────────────────────────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.38
            knee_b = abs(math.sin(t + phase)) * 0.22
            kx = cx + math.sin(leg_a) * self.upper_leg * 0.68
            ky = hip_y + math.cos(leg_a) * self.upper_leg
            lower_a = leg_a + knee_b
            fx = kx + math.sin(lower_a) * self.lower_leg * 0.84
            fy = ky + self.lower_leg * math.cos(lower_a) * 0.88
            _line(surface, cx, hip_y, kx, ky, self.body_w*1.10)
            _line(surface, kx, ky, fx, fy, self.body_w*0.86)
            shoe_d = 1 if math.sin(t+phase) > 0 else -1
            shoe_pts = [
                (fx, fy),
                (fx + shoe_d*self.body_w*0.42, fy - self.body_w*0.26),
                (fx + shoe_d*self.body_w*1.85, fy),
                (fx + shoe_d*self.body_w*1.70, fy + self.body_w*0.40),
                (fx - shoe_d*self.body_w*0.16, fy + self.body_w*0.40),
            ]
            _poly(surface, shoe_pts)

        # ── SKIRT ─────────────────────────────────────────────────────────────
        _draw_skirt(surface, cx, waist_y, self.skirt_h,
                    self.body_w*1.08, self.body_w*2.10, walk_t)

        # ── TORSO ─────────────────────────────────────────────────────────────
        _poly(surface, [
            (cx - self.body_w*1.0,  waist_y),
            (cx + self.body_w*1.0,  waist_y),
            (cx + self.body_w*0.80, chest_y),
            (cx - self.body_w*0.80, chest_y),
        ])

        # ── ARMS ──────────────────────────────────────────────────────────────
        shoulder_y = chest_y + self.head_r*0.15

        # Outer arm — normal gentle swing
        arm_a  = math.sin(t + math.pi) * 0.22
        elbow_x= cx - math.sin(arm_a) * self.upper_arm * 0.80
        elbow_y= shoulder_y + self.upper_arm * 0.78
        hand_x = elbow_x - math.sin(arm_a*0.5) * self.lower_arm * 0.75
        hand_y = elbow_y + self.lower_arm * 0.70
        _line(surface, cx, shoulder_y, elbow_x, elbow_y, self.body_w*0.75)
        _line(surface, elbow_x, elbow_y, hand_x, hand_y, self.body_w*0.58)
        _circle(surface, hand_x, hand_y, self.body_w*0.40)

        # Inner arm — reaches toward mother, hands close together
        inner_reach = math.sin(self.elapsed * 0.6) * 0.08   # tiny gentle sway
        reach_a = 0.32 + inner_reach   # toward mother (left side)
        elbow_ix= cx - math.sin(reach_a) * self.upper_arm * 0.88
        elbow_iy= shoulder_y + self.upper_arm * 0.72
        hand_ix = elbow_ix - math.sin(reach_a + 0.18) * self.lower_arm * 0.85
        hand_iy = elbow_iy + self.lower_arm * 0.65
        _line(surface, cx, shoulder_y, elbow_ix, elbow_iy, self.body_w*0.75)
        _line(surface, elbow_ix, elbow_iy, hand_ix, hand_iy, self.body_w*0.58)
        _circle(surface, hand_ix, hand_iy, self.body_w*0.42)

        # ── HEAD — slight lean toward mother ──────────────────────────────────
        lean_x = cx - 3   # head leans slightly left toward mom
        _line(surface, cx, neck_y, lean_x, neck_y + self.neck_h, self.body_w*0.50)
        _circle(surface, lean_x, head_cy, self.head_r)

        # ── LONG HAIR ─────────────────────────────────────────────────────────
        _draw_long_hair(surface, lean_x, head_cy - self.head_r*0.93,
                        self.head_r, walk_t)


class WinterMother:
    """Walks beside daughter — one arm around her, serene and complete."""
    HEIGHT    = 130
    SPEED     = 30
    STEP_FREQ = 1.5

    def __init__(self, x, ground_y):
        self.x        = float(x)
        self.ground_y = float(ground_y)
        self.elapsed  = 0.0
        h = self.HEIGHT
        self.head_r    = h * 0.112
        self.neck_h    = h * 0.038
        self.torso_h   = h * 0.235
        self.skirt_h   = h * 0.345
        self.upper_leg = h * 0.178
        self.lower_leg = h * 0.175
        self.upper_arm = h * 0.168
        self.lower_arm = h * 0.148
        self.body_w    = h * 0.082

    def update(self, dt):
        self.elapsed += dt
        self.x       += self.SPEED * dt

    def draw(self, surface, daughter_cx):
        cx    = self.x
        t     = self.elapsed * self.STEP_FREQ * math.pi * 2
        bounce= abs(math.sin(t)) * 1.4
        walk_t= self.elapsed * self.STEP_FREQ

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce*0.25
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r
        hem_y   = waist_y + self.skirt_h

        # ── LEGS ─────────────────────────────────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.33
            kx = cx + math.sin(leg_a) * self.upper_leg*0.50
            ky = hip_y + self.upper_leg
            lower_a = leg_a * 0.48
            fx = kx + math.sin(lower_a)*self.lower_leg*0.78
            fy = ky + self.lower_leg*0.84
            if fy > hem_y - 6:
                _line(surface, kx, max(ky,hem_y-4), fx, fy, self.body_w*0.90)
                shoe_d = 1 if math.sin(t+phase) > 0 else -1
                shoe_pts = [
                    (fx, fy),
                    (fx+shoe_d*self.body_w*0.36, fy-self.body_w*0.20),
                    (fx+shoe_d*self.body_w*1.75, fy-self.body_w*0.06),
                    (fx+shoe_d*self.body_w*1.75, fy+self.body_w*0.36),
                    (fx-shoe_d*self.body_w*0.08, fy+self.body_w*0.36),
                    (fx-shoe_d*self.body_w*0.26, fy+self.body_w*0.50),
                    (fx-shoe_d*self.body_w*0.52, fy+self.body_w*0.50),
                    (fx-shoe_d*self.body_w*0.52, fy+self.body_w*0.12),
                ]
                _poly(surface, shoe_pts)

        # ── LONG SKIRT ────────────────────────────────────────────────────────
        _draw_skirt(surface, cx, waist_y, self.skirt_h,
                    self.body_w*1.12, self.body_w*3.20, walk_t)

        # ── TORSO ─────────────────────────────────────────────────────────────
        _poly(surface, [
            (cx - self.body_w*1.04, waist_y),
            (cx + self.body_w*1.04, waist_y),
            (cx + self.body_w*0.82, chest_y),
            (cx - self.body_w*0.82, chest_y),
        ])

        # ── ARMS ──────────────────────────────────────────────────────────────
        shoulder_y = chest_y + self.head_r*0.18

        # Outer arm — gentle normal swing
        arm_a  = math.sin(t + math.pi) * 0.22
        elbow_x= cx + math.sin(arm_a)*self.upper_arm*0.80
        elbow_y= shoulder_y + self.upper_arm*0.75
        hand_x = elbow_x + math.sin(arm_a*0.5)*self.lower_arm*0.72
        hand_y = elbow_y + self.lower_arm*0.68
        _line(surface, cx, shoulder_y, elbow_x, elbow_y, self.body_w*0.78)
        _line(surface, elbow_x, elbow_y, hand_x, hand_y, self.body_w*0.60)
        _circle(surface, hand_x, hand_y, self.body_w*0.42)

        # Inner arm — wraps around daughter's shoulder
        wrap_sway = math.sin(self.elapsed * 0.5) * 0.05
        wrap_a    = 0.38 + wrap_sway
        elbow_wx  = cx + math.sin(wrap_a)*self.upper_arm*0.95
        elbow_wy  = shoulder_y + self.upper_arm*0.55
        # Hand rests at daughter's shoulder height
        daughter_shoulder_y = chest_y + 12
        hand_wx   = daughter_cx - 8
        hand_wy   = daughter_shoulder_y + 5
        _line(surface, cx, shoulder_y, elbow_wx, elbow_wy, self.body_w*0.78)
        _line(surface, elbow_wx, elbow_wy, hand_wx, hand_wy, self.body_w*0.60)
        _circle(surface, hand_wx, hand_wy, self.body_w*0.42)

        # ── HEAD ──────────────────────────────────────────────────────────────
        lean_x = cx + 3   # gentle lean toward daughter
        _line(surface, cx, neck_y, lean_x, neck_y + self.neck_h, self.body_w*0.50)
        _circle(surface, lean_x, head_cy, self.head_r)

        # ── MEDIUM HAIR ───────────────────────────────────────────────────────
        _draw_medium_hair(surface, lean_x, head_cy - self.head_r*0.92,
                          self.head_r, walk_t)

        # ── EARRING ───────────────────────────────────────────────────────────
        ear_x = lean_x + self.head_r*0.88
        ear_y = head_cy + self.head_r*0.28
        _circle(surface, ear_x, ear_y, max(1, int(self.head_r*0.12)))
        _line(surface, ear_x, ear_y+self.head_r*0.12,
              ear_x, ear_y+self.head_r*0.40, max(1,int(self.head_r*0.09)))
        _circle(surface, ear_x, ear_y+self.head_r*0.50,
                max(1, int(self.head_r*0.15)))


class WinterFigures:
    """Mother and daughter walk side by side — together at last."""
    GAP = 55   # close together, shoulder to shoulder

    def __init__(self, screen_w, ground_y):
        self.sw = screen_w
        fig_y   = ground_y - 2
        # Mother on left, daughter just to the right
        self.mother   = WinterMother  (x=-160,            ground_y=fig_y)
        self.daughter = WinterDaughter(x=-160 + self.GAP, ground_y=fig_y)

    def update(self, dt):
        self.mother.update(dt)
        self.daughter.update(dt)
        if self.mother.x > self.sw + 200:
            self.mother.x   = -170
            self.daughter.x = -170 + self.GAP

    def draw(self, surface):
        # Draw mother first so her arm-wrap appears behind daughter's body
        self.mother.draw(surface, daughter_cx=self.daughter.x)
        self.daughter.draw(surface, mother_cx=self.mother.x)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE TEXT — three waves
# ─────────────────────────────────────────────────────────────────────────────
class WinterText:
    # Wave 1
    LINE1 = "Love became quiet."
    LINE2 = "But it never became small."
    # Wave 2
    LINE3 = "Happy Mother's Day Amma"
    # Wave 3
    LINE4 = "Thank you for being every season of home. I love you so much."

    def __init__(self, width, height, font_path, appear_after=5.0):
        self.cx      = width // 2
        self.elapsed = 0.0
        self.appear  = appear_after
        self.a1 = 0.0   # wave 1
        self.a2 = 0.0   # wave 2
        self.a3 = 0.0   # wave 3
        spd = 45

        try:
            font_xl = pygame.font.Font(font_path, 52)
            font_l  = pygame.font.Font(font_path, 46)
            font_m  = pygame.font.Font(font_path, 64)   # Happy Mother's Day — largest
            font_s  = pygame.font.Font(font_path, 42)
        except FileNotFoundError:
            font_xl = pygame.font.SysFont("serif", 52)
            font_l  = pygame.font.SysFont("serif", 46)
            font_m  = pygame.font.SysFont("serif", 64)
            font_s  = pygame.font.SysFont("serif", 42)

        # Soft cream — readable on dark blue sky
        col_poem  = (220, 235, 255)
        col_title = (255, 230, 160)   # warm gold for "Happy Mother's Day"
        col_sub   = (220, 235, 255)
        glow_poem = ( 80, 110, 180)
        glow_title= (200, 150,  40)
        glow_sub  = ( 60,  90, 150)

        self.s1 = font_xl.render(self.LINE1, True, col_poem)
        self.s2 = font_l .render(self.LINE2, True, col_poem)
        self.s3 = font_m .render(self.LINE3, True, col_title)
        self.s4 = font_s .render(self.LINE4, True, col_sub)
        self.g1 = font_xl.render(self.LINE1, True, glow_poem)
        self.g2 = font_l .render(self.LINE2, True, glow_poem)
        self.g3 = font_m .render(self.LINE3, True, glow_title)
        self.g4 = font_s .render(self.LINE4, True, glow_sub)

        self.spd = spd
        lh = int(52 * 1.20)
        gap= int(52 * 0.70)

        self.y1 = int(height * 0.16)
        self.y2 = self.y1 + lh
        self.y3 = self.y2 + int(46*1.20) + gap
        self.y4 = self.y3 + int(68*1.20) + int(gap*0.5)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.appear:
            self.a1 = min(255, self.a1 + self.spd * dt)
        if self.elapsed > self.appear + 4.0:
            self.a2 = min(255, self.a2 + self.spd * dt)
        if self.elapsed > self.appear + 8.5:
            self.a3 = min(255, self.a3 + self.spd * dt)

    def _blit(self, surface, surf, glow, x, y, alpha):
        if alpha <= 0:
            return
        a  = int(alpha)
        if alpha >= 255:
            a = max(0, min(255, 255 + int(math.sin(self.elapsed*0.5)*5)))
        ga = max(0, a - 120)
        if ga > 0:
            glow.set_alpha(ga // 4)
            for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
                surface.blit(glow, (x+ox, y+oy))
        surf.set_alpha(a)
        surface.blit(surf, (x, y))

    def draw(self, surface):
        for surf, glow, y, alpha in [
            (self.s1, self.g1, self.y1, self.a1),
            (self.s2, self.g2, self.y2, self.a1),
            (self.s3, self.g3, self.y3, self.a2),
            (self.s4, self.g4, self.y4, self.a3),
        ]:
            x = self.cx - surf.get_width()//2
            self._blit(surface, surf, glow, x, y, alpha)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN SCENE CLASS
# ─────────────────────────────────────────────────────────────────────────────
class Winter:
    SCENE_DURATION = 26.0    # longest scene — three text waves need room
    FADE_DURATION  = 3.5     # slow, gentle fade at the end

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self._build()

    def _build(self):
        # Static sky
        self.sky_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_winter_sky(self.sky_surf, WIDTH, HEIGHT, GROUND_Y)

        # Stars
        self.stars = StarField(WIDTH, HEIGHT, GROUND_Y, count=140)

        # Aurora
        self.aurora = Aurora(WIDTH, HEIGHT, GROUND_Y)

        # Snow hills
        self.hill_far  = make_snow_hill(WIDTH,GROUND_Y,55,2.0,GROUND_Y-180,phase=0.4)
        self.hill_mid  = make_snow_hill(WIDTH,GROUND_Y,42,1.7,GROUND_Y-125,phase=1.3)
        self.hill_near = make_snow_hill(WIDTH,GROUND_Y,30,2.5,GROUND_Y- 78,phase=2.1)

        # Snow ground fill
        self.ground_rect = pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT-GROUND_Y)

        # Trees with snow
        self.trees = [
            SnowTree(int(WIDTH*0.07), GROUND_Y-55, height=120),
            SnowTree(int(WIDTH*0.16), GROUND_Y-45, height=100),
            SnowTree(int(WIDTH*0.74), GROUND_Y-50, height=115),
            SnowTree(int(WIDTH*0.83), GROUND_Y-42, height= 95),
            SnowTree(int(WIDTH*0.93), GROUND_Y-48, height=108),
            SnowTree(int(WIDTH*0.54), GROUND_Y-38, height= 90),
        ]

        # Lantern — left side, warm anchor
        self.lantern = Lantern(int(WIDTH*0.22), GROUND_Y)

        # Snowflakes — slow and peaceful
        self.snowflakes = [
            Snowflake(WIDTH, HEIGHT, GROUND_Y, initial=True)
            for _ in range(120)
        ]

        # Ground sparkles
        self.sparkles = GroundSparkle(WIDTH, GROUND_Y)

        # Figures — together
        self.figures = WinterFigures(WIDTH, ground_y=GROUND_Y)

        # Text
        self.text = WinterText(WIDTH, HEIGHT, FONT_PATH, appear_after=5.0)

        # Fade
        self.fade_surf  = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surf.fill((0, 0, 0))
        self.fade_alpha = 0
        self.elapsed    = 0.0
        self.fading_out = False
        self._fade_start= 0.0

        # Fade in
        self.fade_in     = True
        self.fade_in_dur = 2.5

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
                self.fade_alpha = max(0, int(255*(1-self.elapsed/self.fade_in_dur)))
                if self.elapsed >= self.fade_in_dur:
                    self.fade_in    = False
                    self.fade_alpha = 0

            # Fade out
            if self.elapsed >= self.SCENE_DURATION and not self.fading_out:
                self.fading_out  = True
                self._fade_start = self.elapsed
            if self.fading_out:
                p = (self.elapsed - self._fade_start) / self.FADE_DURATION
                self.fade_alpha = min(255, int(p*255))
                if self.fade_alpha >= 255:
                    running = False

            # Update
            self.lantern.update(dt)
            for flake in self.snowflakes:
                flake.update(dt)
            self.figures.update(dt)
            self.text.update(dt)

            self._draw()

        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def _draw(self):
        # 1. Sky
        self.screen.blit(self.sky_surf, (0, 0))

        # 2. Aurora (subtle, behind stars)
        self.aurora.draw(self.screen, self.elapsed)

        # 3. Stars
        self.stars.draw(self.screen, self.elapsed)

        # 4. Snow hills far → near
        pygame.draw.polygon(self.screen, HILL_FAR,      self.hill_far)
        pygame.draw.polygon(self.screen, HILL_MID_COL,  self.hill_mid)
        pygame.draw.polygon(self.screen, HILL_NEAR_COL, self.hill_near)

        # 5. Snow ground
        pygame.draw.rect(self.screen, GROUND_COL, self.ground_rect)

        # 6. Trees
        for tree in self.trees:
            tree.draw(self.screen)

        # 7. Lantern
        self.lantern.draw(self.screen)

        # 8. Figures
        self.figures.draw(self.screen)

        # 9. Snowflakes (in front of everything)
        for flake in self.snowflakes:
            flake.draw(self.screen)

        # 10. Ground sparkles
        self.sparkles.draw(self.screen, self.elapsed)

        # 11. Text
        self.text.draw(self.screen)

        # 12. Fade overlay
        if self.fade_alpha > 0:
            self.fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surf, (0, 0))

        pygame.display.update()