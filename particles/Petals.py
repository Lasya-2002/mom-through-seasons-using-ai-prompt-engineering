import pygame
import random
import math

class Petal:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        self.x = random.randint(0, self.width)
        self.y = random.randint(-self.height, 0)

        self.size = random.randint(4, 8)

        self.speed_y = random.uniform(1, 3)
        self.speed_x = random.uniform(-1, 1)

        self.angle = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(0.01, 0.05)

        self.color = random.choice([
            (255, 182, 193),   # light pink
            (255, 192, 203),   # pink
            (255, 228, 225),   # misty rose
            (255, 240, 245)    # lavender blush
        ])

    def update(self):
        self.y += self.speed_y

        # Gentle side movement
        self.x += math.sin(self.angle) * 0.8 + self.speed_x

        self.angle += self.rotation_speed

        # Reset when off screen
        if self.y > self.height:
            self.reset()
            self.y = random.randint(-100, -10)

    def draw(self, screen):
        pygame.draw.ellipse(
            screen,
            self.color,
            (self.x, self.y, self.size, self.size * 0.6)
        )