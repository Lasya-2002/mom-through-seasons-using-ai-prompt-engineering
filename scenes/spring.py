import pygame
import math
from settings import *
from particles.Petals import Petal
from particles.spring_flower import SpringFlower
from particles.butterfly import Butterfly
from particles.grass import GrassLayer
from assets.fonts.spring_text import SpringText

# ─────────────────────────────────────────────────────────────────────────────
#  scenes/spring.py
#
#  Self-contained Spring scene.
#  Called from main.py like:
#      from scenes.spring import Spring
#      Spring(screen, clock).run()
# ─────────────────────────────────────────────────────────────────────────────

# ── Spring sky gradient ───────────────────────────────────────────────────────
# Top of sky → horizon
SKY_TOP    = (255, 224, 235)   # blush pink
SKY_MID    = (255, 240, 245)   # soft white-pink
SKY_BOTTOM = (210, 235, 210)   # pale sage green (meets the grass)


def draw_spring_sky(surface, width, height, ground_y):
    """
    Three-stop gradient:
      top     → SKY_TOP    (blush pink)
      ~60%    → SKY_MID    (near-white)
      ground  → SKY_BOTTOM (pale green, blends into grass)
    """
    mid_stop = int(ground_y * 0.60)

    # Top → mid
    for y in range(mid_stop):
        t = y / mid_stop
        r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    # Mid → ground
    for y in range(mid_stop, ground_y):
        t = (y - mid_stop) / max(ground_y - mid_stop, 1)
        r = int(SKY_MID[0] + (SKY_BOTTOM[0] - SKY_MID[0]) * t)
        g = int(SKY_MID[1] + (SKY_BOTTOM[1] - SKY_MID[1]) * t)
        b = int(SKY_MID[2] + (SKY_BOTTOM[2] - SKY_MID[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


# ── Soft clouds ───────────────────────────────────────────────────────────────
class Cloud:
    def __init__(self, screen_w, screen_h, ground_y, spawn_offscreen=False):
        self.sw = screen_w
        self.sh = screen_h
        self.gy = ground_y
        self._randomize(spawn_offscreen)

    def _randomize(self, offscreen=False):
        import random
        self.y     = int(self.gy * random.uniform(0.06, 0.38))
        self.speed = random.uniform(10, 22)   # px / sec
        self.alpha = random.randint(160, 210)
        # Cloud is a cluster of overlapping ellipses
        self.puffs = []
        n = random.randint(3, 6)
        base_w = random.randint(60, 120)
        for i in range(n):
            import random as r
            ox = i * int(base_w * 0.55) + r.randint(-10, 10)
            oy = r.randint(-12, 12)
            rw = r.randint(int(base_w * 0.45), int(base_w * 0.75))
            rh = r.randint(int(rw * 0.45), int(rw * 0.65))
            self.puffs.append((ox, oy, rw, rh))
        total_w = max(p[0] + p[2] for p in self.puffs)
        if offscreen:
            self.x = -total_w - 20
        else:
            import random
            self.x = random.randint(-total_w, self.sw)
        self.total_w = total_w

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > self.sw + 20:
            self._randomize(offscreen=True)

    def draw(self, surface):
        col = (255, 255, 255)
        for ox, oy, rw, rh in self.puffs:
            cx = int(self.x + ox + rw // 2)
            cy = int(self.y + oy)
            # Draw ellipse via surface with per-pixel alpha
            s = pygame.Surface((rw * 2, rh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*col, self.alpha), (0, 0, rw * 2, rh * 2))
            surface.blit(s, (cx - rw, cy - rh))


# ── Main scene class ──────────────────────────────────────────────────────────
class Spring:
    """
    Spring scene. Call .run() to enter the loop.
    Returns when the scene is complete (currently: after text has been shown
    for SCENE_DURATION seconds, then fades to black).
    """

    GROUND_Y       = HEIGHT - 40
    SCENE_DURATION = 10.0      # seconds before transitioning out
    FADE_DURATION  = 2.5       # seconds for fade-to-black at the end
    FONT_PATH      = "C:/Users/mvsla/OneDrive/Desktop/Mother's day gift/assets/fonts/GreatVibes-Regular.ttf"

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self._build()

    def _build(self):
        import random

        # Pre-render sky (static surface — drawn once, blit every frame)
        self.sky_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_spring_sky(self.sky_surf, WIDTH, HEIGHT, self.GROUND_Y)

        # Clouds
        self.clouds = [Cloud(WIDTH, HEIGHT, self.GROUND_Y) for _ in range(5)]

        # Grass
        self.grass = GrassLayer(WIDTH, HEIGHT, ground_y=self.GROUND_Y)

        # Petals
        self.petals = [Petal(WIDTH, HEIGHT) for _ in range(80)]

        # Flowers spread across full width
        flower_configs = [
            (WIDTH * 0.04,  0),  (WIDTH * 0.10,  10), (WIDTH * 0.17, -5),
            (WIDTH * 0.23,  5),  (WIDTH * 0.30,  0),  (WIDTH * 0.36, -10),
            (WIDTH * 0.42,  8),  (WIDTH * 0.48,  0),  (WIDTH * 0.54, -5),
            (WIDTH * 0.60,  12), (WIDTH * 0.66,  0),  (WIDTH * 0.72, -8),
            (WIDTH * 0.78,  5),  (WIDTH * 0.84,  0),  (WIDTH * 0.90, -5),
            (WIDTH * 0.96,  10),
        ]
        self.flowers = [
            SpringFlower(int(x), int(self.GROUND_Y + dy))
            for x, dy in flower_configs
        ]

        # Butterflies
        self.butterflies = [
            Butterfly(WIDTH, HEIGHT, ground_y=self.GROUND_Y)
            for _ in range(10)
        ]

        # Text
        self.spring_text = SpringText(
            WIDTH, HEIGHT,
            font_path=self.FONT_PATH,
            appear_after=4.0
        )

        # Fade overlay
        self.fade_surf  = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surf.fill((0, 0, 0))
        self.fade_alpha = 0     # 0=transparent, 255=black

        self.elapsed    = 0.0
        self.fading_out = False

    def run(self):
        """Enter the scene loop. Returns when scene is done."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed += dt

            # ── Events ────────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit

            # ── Trigger fade-out ───────────────────────────────────────────────
            if self.elapsed >= self.SCENE_DURATION and not self.fading_out:
                self.fading_out = True
                self._fade_start = self.elapsed

            if self.fading_out:
                progress = (self.elapsed - self._fade_start) / self.FADE_DURATION
                self.fade_alpha = min(255, int(progress * 255))
                if self.fade_alpha >= 255:
                    running = False   # scene complete

            # ── Update ────────────────────────────────────────────────────────
            self.grass.update(dt)
            for cloud in self.clouds:
                cloud.update(dt)
            for petal in self.petals:
                petal.update()
            for flower in self.flowers:
                flower.update(dt)
            for b in self.butterflies:
                b.update(dt)
            self.spring_text.update(dt)

            # ── Draw ──────────────────────────────────────────────────────────
            self._draw()

        # Leave screen black, ready for next scene
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def _draw(self):
        # 1. Sky gradient
        self.screen.blit(self.sky_surf, (0, 0))

        # 2. Clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)

        # 3. Floating petals
        for petal in self.petals:
            petal.draw(self.screen)

        # 4. Grass + ground
        self.grass.draw(self.screen)

        # 5. Flowers
        for flower in self.flowers:
            flower.draw(self.screen)

        # 6. Butterflies
        for b in self.butterflies:
            b.draw(self.screen)

        # 7. Text
        self.spring_text.draw(self.screen)

        # 8. Fade overlay (black, used for transition out)
        if self.fade_alpha > 0:
            self.fade_surf.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surf, (0, 0))

        pygame.display.update()