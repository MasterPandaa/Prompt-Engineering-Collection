"""Pong game implemented with Pygame.

- Resolution: 800x600
- Player left paddle: W/S keys
- Right paddle: AI with reaction delay and error margin
- OOP: Paddle and Ball classes
- Physics: Accurate bounces and scoring system

Author: Cascade (Senior Python Game Developer)
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from typing import Tuple

import pygame


# -----------------------------
# Configuration and constants
# -----------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE: Tuple[int, int, int] = (240, 240, 240)
BLACK: Tuple[int, int, int] = (10, 10, 10)
GREY: Tuple[int, int, int] = (90, 90, 90)
ACCENT: Tuple[int, int, int] = (0, 200, 180)

# Gameplay
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 100
PADDLE_SPEED = 7
AI_PADDLE_SPEED = 6  # slightly slower than player for fairness
BALL_SIZE = 12
BALL_SPEED_INITIAL = 6.0
BALL_SPEED_MAX = 12.0
BALL_SPEED_INCREMENT = 0.35

SCORE_FONT_SIZE = 48
INFO_FONT_SIZE = 20


@dataclass
class Paddle:
    rect: pygame.Rect
    speed: int

    def move(self, dy: float) -> None:
        self.rect.y += int(dy)
        self.clamp_to_screen()

    def clamp_to_screen(self) -> None:
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=6)


class Ball:
    def __init__(self, rect: pygame.Rect, speed: float) -> None:
        self.rect = rect
        # Velocity components
        angle = random.uniform(-0.35 * math.pi, 0.35 * math.pi)
        direction = random.choice([-1, 1])
        self.vx = math.cos(angle) * speed * direction
        self.vy = math.sin(angle) * speed
        self.speed = speed

    def reset(self, direction: int) -> None:
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-0.35 * math.pi, 0.35 * math.pi)
        self.speed = BALL_SPEED_INITIAL
        self.vx = math.cos(angle) * self.speed * direction
        self.vy = math.sin(angle) * self.speed

    def update(self, left: Paddle, right: Paddle) -> Tuple[int, int]:
        """Update position, handle collisions, and return score delta (l, r)."""
        score_left = 0
        score_right = 0

        # Move ball
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Screen bounds (top/bottom)
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy *= -1

        # Paddle collisions
        if self.rect.colliderect(left.rect) and self.vx < 0:
            self._bounce_off_paddle(left)
        elif self.rect.colliderect(right.rect) and self.vx > 0:
            self._bounce_off_paddle(right, is_right=True)

        # Scoring (passed left/right edges)
        if self.rect.right < 0:
            score_right = 1
            self.reset(direction=-1)
        elif self.rect.left > WIDTH:
            score_left = 1
            self.reset(direction=1)

        return score_left, score_right

    def _bounce_off_paddle(self, paddle: Paddle, is_right: bool = False) -> None:
        # Push ball outside the paddle to avoid sticking
        if is_right:
            self.rect.right = paddle.rect.left
        else:
            self.rect.left = paddle.rect.right

        # Compute bounce angle based on impact point
        paddle_center_y = paddle.rect.centery
        ball_center_y = self.rect.centery
        offset = (ball_center_y - paddle_center_y) / (paddle.rect.height / 2)
        offset = max(-1.0, min(1.0, offset))

        # Increase speed slightly up to max
        self.speed = min(BALL_SPEED_MAX, self.speed + BALL_SPEED_INCREMENT)

        # New direction: reflect x, adjust y based on offset
        angle = offset * (0.45 * math.pi)  # up to ~81 degrees
        direction = 1 if is_right is False else -1  # reflect away from paddle
        self.vx = math.cos(angle) * self.speed * direction
        self.vy = math.sin(angle) * self.speed

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, ACCENT, self.rect, border_radius=3)


class AIPaddleController:
    """Fair-but-challenging AI with reaction delay and aiming error.

    The AI updates its target only at certain intervals (reaction time) and adds
    a distance/speed-dependent error. It also anticipates only when the ball is
    traveling towards it; otherwise it recenters smoothly.
    """

    def __init__(self, paddle: Paddle, ball: Ball) -> None:
        self.paddle = paddle
        self.ball = ball
        self.update_interval_ms = 120  # reaction delay
        self.last_update_time = 0
        self.target_center_y = HEIGHT // 2
        self.center_bias = 0.15  # tendency to drift back to center when ball is far

    def update(self) -> None:
        now = pygame.time.get_ticks()
        should_update = now - self.last_update_time >= self.update_interval_ms

        # Determine if ball is moving towards AI (right side)
        ball_towards_ai = self.ball.vx > 0

        if should_update:
            self.last_update_time = now

            if ball_towards_ai:
                # Error depends on distance and ball speed: further/faster => more error
                distance_x = max(1, (WIDTH - self.ball.rect.centerx))
                speed_factor = max(1.0, abs(self.ball.vx))
                # Standard deviation grows with challenge; clamp to a reasonable range
                sigma = min(80.0, 8.0 + (distance_x / 20.0) + (speed_factor * 1.2))
                noise = random.gauss(0.0, sigma)
                self.target_center_y = self.ball.rect.centery + noise
            else:
                # When ball is moving away, drift target back to center with some noise
                noise = random.gauss(0.0, 25.0)
                self.target_center_y = (1 - self.center_bias) * self.target_center_y + self.center_bias * (HEIGHT / 2 + noise)

        # Move towards target with limited speed
        dy = self.target_center_y - self.paddle.rect.centery
        if abs(dy) > self.paddle.speed:
            dy = AI_PADDLE_SPEED if dy > 0 else -AI_PADDLE_SPEED
        self.paddle.move(dy)


def draw_center_net(surface: pygame.Surface) -> None:
    segment_height = 18
    gap = 10
    x = WIDTH // 2 - 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surface, GREY, pygame.Rect(x, y, 4, segment_height), border_radius=2)
        y += segment_height + gap


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Pong - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    score_left = 0
    score_right = 0

    # Fonts
    score_font = pygame.font.SysFont("consolas", SCORE_FONT_SIZE, bold=True)
    info_font = pygame.font.SysFont("consolas", INFO_FONT_SIZE)

    # Entities
    left_paddle = Paddle(
        rect=pygame.Rect(32, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT),
        speed=PADDLE_SPEED,
    )
    right_paddle = Paddle(
        rect=pygame.Rect(WIDTH - 32 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT),
        speed=AI_PADDLE_SPEED,
    )

    ball = Ball(pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE), BALL_SPEED_INITIAL)

    ai = AIPaddleController(right_paddle, ball)

    # Game loop
    running = True
    while running:
        dt = clock.tick(FPS)  # milliseconds per frame, not used for now (frame-based speeds)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Input - player left paddle (W/S)
        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= PADDLE_SPEED
        if keys[pygame.K_s]:
            dy += PADDLE_SPEED
        if dy != 0:
            left_paddle.move(dy)

        # Update entities
        l, r = ball.update(left_paddle, right_paddle)
        score_left += l
        score_right += r

        ai.update()

        # Render
        screen.fill(BLACK)
        draw_center_net(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Score display
        score_text = f"{score_left}   {score_right}"
        score_surf = score_font.render(score_text, True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(score_surf, score_rect)

        # Info
        info_lines = [
            "W/S: Move | Esc: Quit",
            "First to any score (endless).",
        ]
        for i, line in enumerate(info_lines):
            surf = info_font.render(line, True, GREY)
            screen.blit(surf, (20, HEIGHT - 20 - (len(info_lines) - 1 - i) * (INFO_FONT_SIZE + 4)))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
