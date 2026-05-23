import pygame
import math

class SpringText:
    """
    Renders two lines of calligraphy text with fade-in and soft pulse.
    """

    LINE1 = "You taught me how to look at the world softly"
    LINE2 = "My first home was your voice."

    def __init__(self, screen_w, screen_h, font_path,
                 font_size=54,
                 appear_after=4.0):   # seconds before text starts fading in
        self.sw = screen_w
        self.sh = screen_h
        self.appear_after = appear_after

        self.elapsed = 0.0
        self.alpha   = 0.0     # 0→255
        self.fade_speed = 60   # alpha units per second

        # Load font — falls back to pygame default serif if file not found
        try:
            self.font_large = pygame.font.Font(font_path, font_size)
            self.font_small = pygame.font.Font(font_path, int(font_size * 0.78))
        except FileNotFoundError:
            print(f"[SpringText] Font not found at '{font_path}'. "
                  "Using fallback. Download GreatVibes-Regular.ttf from Google Fonts.")
            self.font_large = pygame.font.SysFont("serif", font_size)
            self.font_small = pygame.font.SysFont("serif", int(font_size * 0.78))

        # Text color - black
        self.text_color = (30,20,10)
        self.glow_color = (80,40, 60)

        # Pre-render surfaces (we re-blit with alpha each frame)
        self.surf1 = self.font_large.render(self.LINE1, True, self.text_color)
        self.surf2 = self.font_small.render(self.LINE2, True, self.text_color)
        self.glow1 = self.font_large.render(self.LINE1, True, self.glow_color)
        self.glow2 = self.font_small.render(self.LINE2, True, self.glow_color)

        # Vertical position — upper-center of screen (above flowers)
        self.center_x = screen_w // 2
        self.y1 = int(screen_h * 0.30)   # line 1 y
        self.y2 = int(screen_h * 0.30) + int(font_size * 1.15)  # line 2 y

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.appear_after:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)

    def draw(self, surface):
        if self.alpha <= 0:
            return

        a = int(self.alpha)

        # Pulse ONLY after fully faded in, and very subtly (±6 units, slow sine)
        # This avoids any visible shake during the fade-in phase
        if self.alpha >= 255:
            pulse = math.sin(self.elapsed * 0.6) * 6
            a = max(0, min(255, 255 + int(pulse)))

        for surf, glow, y in [
            (self.surf1, self.glow1, self.y1),
            (self.surf2, self.glow2, self.y2),
        ]:
            w = surf.get_width()
            x = self.center_x - w // 2

            # ── Soft glow: fixed offsets, no copy() per frame ────────────────
            glow_alpha = max(0, a - 100)
            if glow_alpha > 0:
                self.glow1.set_alpha(glow_alpha // 4)
                self.glow2.set_alpha(glow_alpha // 4)
                for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    surface.blit(glow, (x + ox, y + oy))

            # ── Main text ─────────────────────────────────────────────────────
            surf.set_alpha(a)
            surface.blit(surf, (x, y))