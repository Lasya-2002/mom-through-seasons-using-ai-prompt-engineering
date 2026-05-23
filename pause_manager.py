# pause_manager.py  —  "Mom Through Seasons"
#
# A single shared object that holds pause state.
# Import it in main.py and every scene — they all reference the same instance.
#
# Usage:
#   from pause_manager import pause_manager
#   pause_manager.handle_event(event)   # call inside event loop
#   dt = pause_manager.tick(clock, FPS) # replaces clock.tick() — returns 0 when paused
#   pause_manager.draw_indicator(screen)# optional pause icon overlay

import pygame

class PauseManager:
    def __init__(self):
        self.paused = False
        self._icon_alpha  = 0.0     # for fade-in/out of the pause icon
        self._icon_timer  = 0.0     # how long the icon has been visible

    def handle_event(self, event):
        """Call this for every pygame event. Toggles pause on SPACE."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.paused = not self.paused
            if self.paused:
                pygame.mixer.music.pause()
                self._icon_alpha = 255.0
                self._icon_timer = 0.0
            else:
                pygame.mixer.music.unpause()
                self._icon_timer = 0.0   # start fade-out

    def tick(self, clock, fps):
        """
        Drop-in replacement for clock.tick(FPS).
        Returns dt in seconds — always 0.0 while paused so nothing updates.
        """
        raw_dt = clock.tick(fps) / 1000.0
        if self.paused:
            # Still tick the clock so the window stays responsive
            return 0.0
        return raw_dt

    def update_icon(self, real_dt):
        """
        Fade the pause icon in when paused, fade out 1.5s after unpausing.
        Call once per frame with the REAL dt (not the paused 0.0).
        """
        real_dt = real_dt if real_dt > 0 else 1 / 60
        if self.paused:
            # Keep icon fully visible
            self._icon_alpha = min(255.0, self._icon_alpha + 400 * real_dt)
        else:
            # Fade out after a short delay
            self._icon_timer += real_dt
            if self._icon_timer > 0.4:
                self._icon_alpha = max(0.0, self._icon_alpha - 300 * real_dt)

    def draw_indicator(self, surface):
        """
        Draw a minimal pause icon (two rounded bars) or a play triangle,
        bottom-right corner, semi-transparent.
        """
        if self._icon_alpha <= 0:
            return

        sw = surface.get_width()
        sh = surface.get_height()
        a  = int(self._icon_alpha)

        # Background pill — soft dark circle
        pad  = 18
        size = 48
        cx   = sw - pad - size // 2
        cy   = sh - pad - size // 2

        bg = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(bg, (0, 0, 0, min(160, a)), (size//2, size//2), size//2)
        surface.blit(bg, (cx - size//2, cy - size//2))

        if self.paused:
            # Two vertical bars (pause symbol)
            bar_w = 5
            bar_h = 18
            gap   = 6
            for i, bx in enumerate([cx - gap//2 - bar_w, cx + gap//2]):
                bar = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
                bar.fill((255, 255, 255, a))
                surface.blit(bar, (bx, cy - bar_h//2))
        else:
            # Play triangle (briefly visible after unpausing)
            tri = [
                (cx - 7, cy - 10),
                (cx - 7, cy + 10),
                (cx + 10, cy),
            ]
            icon = pygame.Surface((size, size), pygame.SRCALPHA)
            shifted = [(p[0] - (cx - size//2), p[1] - (cy - size//2)) for p in tri]
            pygame.draw.polygon(icon, (255, 255, 255, a), shifted)
            surface.blit(icon, (cx - size//2, cy - size//2))


# Single shared instance — import this everywhere
pause_manager = PauseManager()