import pygame
import math

# ─────────────────────────────────────────────────────────────────────────────
#  particles/figures.py  —  "Mom Through Seasons"
#
#  Realistic silhouette figures: daughter and mother with open hair,
#  flowing skirts, shoes, earrings and detailed anatomy.
#
#  Drop into particles/figures.py — summer.py stays untouched.
# ─────────────────────────────────────────────────────────────────────────────

COL = (20, 12, 8)   # warm near-black silhouette


def _poly(surface, pts):
    if len(pts) >= 3:
        pygame.draw.polygon(surface, COL, [(int(x), int(y)) for x, y in pts])


def _circle(surface, cx, cy, r):
    pygame.draw.circle(surface, COL, (int(cx), int(cy)), max(1, int(r)))


def _line(surface, x1, y1, x2, y2, w):
    pygame.draw.line(surface, COL,
                     (int(x1), int(y1)), (int(x2), int(y2)), max(1, int(w)))


def _ellipse(surface, cx, cy, w, h):
    rect = (int(cx - w/2), int(cy - h/2), int(w), int(h))
    if rect[2] > 0 and rect[3] > 0:
        pygame.draw.ellipse(surface, COL, rect)


# ─────────────────────────────────────────────────────────────────────────────
#  HAIR
# ─────────────────────────────────────────────────────────────────────────────

def _draw_long_open_hair(surface, cx, head_top_y, head_r, sway, run_t):
    """
    Long hair flowing behind — wide at crown, tapers and waves at ends.
    Drawn as a filled polygon with a flowing silhouette.
    """
    length    = head_r * 4.2
    width_top = head_r * 1.08

    left_pts  = []
    right_pts = []
    steps = 14

    for i in range(steps + 1):
        t = i / steps
        # Hair billows outward near middle then tapers to end
        billow = math.sin(t * math.pi) * head_r * 0.7
        # Wind/motion wave — more pronounced at tips
        wave   = math.sin(run_t * 0.8 + t * math.pi * 1.4) * (head_r * 0.15 + t * head_r * 0.55)

        lx = cx - width_top - billow * 0.9 + wave * 0.35
        rx = cx + width_top * 0.25 + billow * 0.15 + wave * 0.15
        y  = head_top_y + t * length

        left_pts.append((lx, y))
        right_pts.append((rx, y))

    # Top of hair across crown
    crown = [
        (cx - width_top, head_top_y),
        (cx + width_top * 0.25, head_top_y),
    ]
    all_pts = crown + right_pts[::-1] + left_pts[::-1]
    _poly(surface, all_pts)


def _draw_medium_open_hair(surface, cx, head_top_y, head_r, sway, walk_t):
    """
    Medium-length open hair, shoulder-length, gentle wave.
    """
    length    = head_r * 3.4
    width_top = head_r * 1.12

    left_pts  = []
    right_pts = []
    steps = 12

    for i in range(steps + 1):
        t = i / steps
        billow = math.sin(t * math.pi) * head_r * 0.55
        wave   = math.sin(walk_t * 0.5 + t * math.pi) * (head_r * 0.10 + t * head_r * 0.30)

        lx = cx - width_top - billow * 0.85 + wave * 0.25
        rx = cx + width_top * 0.30 + billow * 0.20 + wave * 0.12
        y  = head_top_y + t * length

        left_pts.append((lx, y))
        right_pts.append((rx, y))

    crown   = [(cx - width_top, head_top_y), (cx + width_top * 0.30, head_top_y)]
    all_pts = crown + right_pts[::-1] + left_pts[::-1]
    _poly(surface, all_pts)


# ─────────────────────────────────────────────────────────────────────────────
#  SKIRT
# ─────────────────────────────────────────────────────────────────────────────

def _draw_flowing_skirt(surface, cx, waist_y, skirt_len,
                        waist_w, hem_w, run_t):
    """
    Flowing skirt with animated hem — wider at bottom, ripples as figure moves.
    Built from a 6-point polygon with dynamic hem points.
    """
    hem_y   = waist_y + skirt_len
    ripple  = math.sin(run_t * 2.1) * 5
    ripple2 = math.sin(run_t * 2.1 + 1.2) * 3
    drift   = math.sin(run_t * 1.0) * 4

    pts = [
        (cx - waist_w,                      waist_y),
        (cx + waist_w,                      waist_y),
        # right hem — billows out
        (cx + hem_w + ripple2 + drift,      hem_y + ripple * 0.4),
        # center dip
        (cx + drift * 0.3,                  hem_y - skirt_len * 0.05 + ripple * 0.2),
        (cx - drift * 0.2,                  hem_y - skirt_len * 0.06 - ripple2 * 0.2),
        # left hem
        (cx - hem_w + ripple + drift * 0.5, hem_y - ripple2 * 0.3),
    ]
    _poly(surface, pts)


# ─────────────────────────────────────────────────────────────────────────────
#  DAUGHTER
# ─────────────────────────────────────────────────────────────────────────────

class Daughter:
    """
    Young girl running — short dress, long open hair flying behind,
    energetic running pose.
    """
    HEIGHT    = 180
    SPEED     = 88
    STEP_FREQ = 3.2

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
        bounce= abs(math.sin(t)) * 3.8

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce * 0.35
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r

        run_t  = self.elapsed * self.STEP_FREQ

        # ── LEGS ─────────────────────────────────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.78
            knee_b = abs(math.sin(t + phase)) * 0.55

            kx = cx + math.sin(leg_a) * self.upper_leg * 0.72
            ky = hip_y + math.cos(leg_a) * self.upper_leg

            lower_a = leg_a + knee_b
            fx = kx + math.sin(lower_a) * self.lower_leg * 0.88
            fy = ky + self.lower_leg * math.cos(lower_a) * 0.90

            _line(surface, cx, hip_y, kx, ky, self.body_w * 1.15)
            _line(surface, kx, ky, fx, fy,   self.body_w * 0.90)

            # Shoe — pointed ballet-flat shape
            shoe_dir = 1 if math.sin(t + phase) > 0 else -1
            shoe_pts = [
                (fx, fy),
                (fx + shoe_dir * self.body_w * 0.5, fy - self.body_w * 0.3),
                (fx + shoe_dir * self.body_w * 2.0, fy),
                (fx + shoe_dir * self.body_w * 1.8, fy + self.body_w * 0.45),
                (fx - shoe_dir * self.body_w * 0.2, fy + self.body_w * 0.45),
            ]
            _poly(surface, shoe_pts)

        # ── SHORT SKIRT ────────────────────────────────────────────────────────
        _draw_flowing_skirt(
            surface, cx, waist_y,
            skirt_len=self.skirt_h,
            waist_w=self.body_w * 1.10,
            hem_w=self.body_w * 2.30,
            run_t=run_t
        )

        # ── TORSO ─────────────────────────────────────────────────────────────
        torso_pts = [
            (cx - self.body_w * 1.02, waist_y),
            (cx + self.body_w * 1.02, waist_y),
            (cx + self.body_w * 0.82, chest_y),
            (cx - self.body_w * 0.82, chest_y),
        ]
        _poly(surface, torso_pts)

        # ── ARMS ──────────────────────────────────────────────────────────────
        shoulder_y = chest_y + self.head_r * 0.15
        for phase in [0, math.pi]:
            arm_a  = math.sin(t + phase + math.pi) * 0.68
            elbow_x= cx + math.sin(arm_a) * self.upper_arm * 0.82
            elbow_y= shoulder_y + self.upper_arm * math.cos(arm_a) * 0.72

            fore_a = arm_a + math.sin(t + phase) * 0.38
            hand_x = elbow_x + math.sin(fore_a) * self.lower_arm * 0.82
            hand_y = elbow_y + self.lower_arm * 0.75

            _line(surface, cx, shoulder_y, elbow_x, elbow_y, self.body_w * 0.78)
            _line(surface, elbow_x, elbow_y, hand_x, hand_y, self.body_w * 0.60)
            _circle(surface, hand_x, hand_y, self.body_w * 0.42)

        # ── HEAD + NECK ────────────────────────────────────────────────────────
        _line(surface, cx, neck_y, cx, neck_y + self.neck_h, self.body_w * 0.52)
        _circle(surface, cx, head_cy, self.head_r)

        # ── LONG OPEN HAIR ────────────────────────────────────────────────────
        head_top = head_cy - self.head_r * 0.95
        _draw_long_open_hair(
            surface, cx, head_top,
            head_r=self.head_r,
            sway=math.sin(self.elapsed * 1.1) * 0.3,
            run_t=run_t
        )


# ─────────────────────────────────────────────────────────────────────────────
#  MOTHER
# ─────────────────────────────────────────────────────────────────────────────

class Mother:
    """
    Adult woman walking — long flowing skirt, medium open hair,
    graceful steady walk, small earring detail.
    """
    HEIGHT    = 200
    SPEED     = 72
    STEP_FREQ = 2.0

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
        bounce= abs(math.sin(t)) * 1.8

        foot_y  = self.ground_y
        hip_y   = foot_y - self.upper_leg - self.lower_leg + bounce * 0.28
        waist_y = hip_y
        chest_y = waist_y - self.torso_h
        neck_y  = chest_y
        head_cy = neck_y - self.neck_h - self.head_r

        walk_t  = self.elapsed * self.STEP_FREQ
        hem_y   = waist_y + self.skirt_h

        # ── LEGS (peek below long skirt hem) ─────────────────────────────────
        for phase in [0, math.pi]:
            leg_a  = math.sin(t + phase) * 0.38
            kx = cx + math.sin(leg_a) * self.upper_leg * 0.55
            ky = hip_y + self.upper_leg

            lower_a = leg_a * 0.55
            fx = kx + math.sin(lower_a) * self.lower_leg * 0.82
            fy = ky + self.lower_leg * 0.88

            # Only render below hem
            if fy > hem_y - 6:
                draw_from_y = max(ky, hem_y - 4)
                _line(surface, kx, draw_from_y, fx, fy, self.body_w * 0.95)

                # Heeled shoe
                shoe_dir = 1 if math.sin(t + phase) > 0 else -1
                shoe_pts = [
                    (fx, fy),
                    (fx + shoe_dir * self.body_w * 0.4, fy - self.body_w * 0.25),
                    (fx + shoe_dir * self.body_w * 1.85, fy - self.body_w * 0.1),
                    (fx + shoe_dir * self.body_w * 1.85, fy + self.body_w * 0.4),
                    (fx - shoe_dir * self.body_w * 0.1,  fy + self.body_w * 0.4),
                    # Small heel block under ankle
                    (fx - shoe_dir * self.body_w * 0.3,  fy + self.body_w * 0.55),
                    (fx - shoe_dir * self.body_w * 0.6,  fy + self.body_w * 0.55),
                    (fx - shoe_dir * self.body_w * 0.6,  fy + self.body_w * 0.15),
                ]
                _poly(surface, shoe_pts)

        # ── LONG FLOWING SKIRT ────────────────────────────────────────────────
        _draw_flowing_skirt(
            surface, cx, waist_y,
            skirt_len=self.skirt_h,
            waist_w=self.body_w * 1.12,
            hem_w=self.body_w * 3.40,
            run_t=walk_t
        )

        # ── TORSO (fitted blouse) ─────────────────────────────────────────────
        torso_pts = [
            (cx - self.body_w * 1.05, waist_y),
            (cx + self.body_w * 1.05, waist_y),
            (cx + self.body_w * 0.82, chest_y),
            (cx - self.body_w * 0.82, chest_y),
        ]
        _poly(surface, torso_pts)

        # ── ARMS ──────────────────────────────────────────────────────────────
        shoulder_y = chest_y + self.head_r * 0.18
        for phase in [0, math.pi]:
            arm_a  = math.sin(t + phase + math.pi) * 0.30
            elbow_x= cx + math.sin(arm_a) * self.upper_arm * 0.85
            elbow_y= shoulder_y + self.upper_arm * 0.76

            fore_a = arm_a + 0.18
            hand_x = elbow_x + math.sin(fore_a) * self.lower_arm * 0.80
            hand_y = elbow_y + self.lower_arm * 0.72

            _line(surface, cx, shoulder_y, elbow_x, elbow_y, self.body_w * 0.80)
            _line(surface, elbow_x, elbow_y, hand_x, hand_y, self.body_w * 0.62)
            _circle(surface, hand_x, hand_y, self.body_w * 0.42)

        # ── HEAD + NECK ────────────────────────────────────────────────────────
        _line(surface, cx, neck_y, cx, neck_y + self.neck_h, self.body_w * 0.50)
        _circle(surface, cx, head_cy, self.head_r)

        # ── MEDIUM OPEN HAIR ──────────────────────────────────────────────────
        head_top = head_cy - self.head_r * 0.95
        _draw_medium_open_hair(
            surface, cx, head_top,
            head_r=self.head_r,
            sway=math.sin(self.elapsed * 0.85) * 0.22,
            walk_t=walk_t
        )

        # ── EARRING (stud + drop) ─────────────────────────────────────────────
        ear_x = cx + self.head_r * 0.90
        ear_y = head_cy + self.head_r * 0.28
        _circle(surface, ear_x, ear_y, max(1, int(self.head_r * 0.13)))
        _line(surface, ear_x, ear_y + self.head_r * 0.13,
              ear_x, ear_y + self.head_r * 0.42,
              max(1, int(self.head_r * 0.09)))
        _circle(surface, ear_x, ear_y + self.head_r * 0.52,
                max(1, int(self.head_r * 0.16)))


# ─────────────────────────────────────────────────────────────────────────────
#  FIGURES MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class Figures:
    DAUGHTER_LEAD = 105

    def __init__(self, screen_w, screen_h, ground_y):
        self.sw = screen_w
        fig_y   = ground_y - 2

        self.mother   = Mother  (x=-120,                       ground_y=fig_y)
        self.daughter = Daughter(x=-120 + self.DAUGHTER_LEAD,  ground_y=fig_y)

    def update(self, dt):
        self.mother.update(dt)
        self.daughter.update(dt)
        if self.mother.x > self.sw + 150:
            self.mother.x   = -130
            self.daughter.x = -130 + self.DAUGHTER_LEAD

    def draw(self, surface):
        self.mother.draw(surface)
        self.daughter.draw(surface)