"""Pong game implemented with Pygame using clean OOP design.

Classes:
- Paddle: Represents a player or AI paddle with movement constraints.
- Ball: Handles movement, wall/paddle collisions, and scoring resets.
- Game: Sets up the window, main loop, input handling, AI, and rendering.

Controls:
- Player (left paddle): W (up), S (down)
- Quit: ESC or window close button

Screen: 800 x 600
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import Tuple

import pygame


# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 12
PADDLE_MARGIN = 24

WHITE = (240, 240, 240)
DIM_WHITE = (200, 200, 200)
DARK = (20, 20, 30)
ACCENT = (120, 170, 255)


@dataclass
class Score:
    left: int = 0
    right: int = 0


class Paddle:
    """Represents a paddle. Can be controlled by player or AI."""

    def __init__(self, x: int, y: int, speed: float) -> None:
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = speed

    def move_towards(self, target_y: float, dt: float) -> None:
        """Move vertically toward target_y with speed, clamped to screen."""
        center_y = self.rect.centery
        if abs(target_y - center_y) <= 1:
            return
        direction = 1 if target_y > center_y else -1
        dy = direction * self.speed * dt
        self.rect.y += int(dy)
        self._clamp()

    def move_input(self, up: bool, down: bool, dt: float) -> None:
        dy = 0.0
        if up and not down:
            dy = -self.speed * dt
        elif down and not up:
            dy = self.speed * dt
        self.rect.y += int(dy)
        self._clamp()

    def _clamp(self) -> None:
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, color, self.rect, border_radius=4)


class Ball:
    """Represents the ball with basic physics and collisions."""

    def __init__(self, x: int, y: int, speed: float) -> None:
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        # Initial velocity set in reset()
        self.base_speed = speed
        self.vel = pygame.Vector2(0, 0)
        self.reset(direction=random.choice((-1, 1)))

    def reset(self, direction: int) -> None:
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-0.35, 0.35)  # near-horizontal, ~+-20 degrees
        self.vel.x = direction * self.base_speed
        self.vel.y = self.base_speed * angle

    def update(self, dt: float) -> None:
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)
        # Wall collisions
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel.y = -self.vel.y
        elif self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel.y = -self.vel.y

    def collide_paddle(self, paddle: Paddle) -> None:
        if not self.rect.colliderect(paddle.rect):
            return
        # Determine from which side we hit to avoid sticking
        if self.vel.x < 0:  # moving left, hit left paddle
            self.rect.left = paddle.rect.right
        else:  # moving right, hit right paddle
            self.rect.right = paddle.rect.left
        self.vel.x = -self.vel.x

        # Add spin based on where it hits the paddle
        offset = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        spin = offset * 220  # tweakable factor for vertical velocity
        self.vel.y = max(min(self.vel.y + spin, 520), -520)

        # Slight speed up on each paddle hit (cap to avoid too fast)
        self.vel.x *= 1.04
        self.vel.x = max(min(self.vel.x, 720), -720)

    def draw(self, surface: pygame.Surface, color: Tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, color, self.rect, border_radius=3)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 36)
        self.small_font = pygame.font.SysFont("consolas", 16)

        # Entities
        left_x = PADDLE_MARGIN
        right_x = WIDTH - PADDLE_MARGIN - PADDLE_WIDTH
        start_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.player = Paddle(left_x, start_y, speed=520)
        self.ai = Paddle(right_x, start_y, speed=500)  # capped to be beatable
        self.ball = Ball(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, speed=420)

        self.score = Score()
        self.serve_dir = random.choice((-1, 1))

        # AI behavior parameters
        self.ai_reaction_ms = 140  # update target every N ms
        self.ai_timer = 0
        self.ai_target_y = HEIGHT // 2
        self.ai_error_margin = 32  # pixels of random error

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0  # seconds
            if not self._handle_events():
                return

            self._update(dt)
            self._draw()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def _update(self, dt: float) -> None:
        # Input for player
        keys = pygame.key.get_pressed()
        self.player.move_input(keys[pygame.K_w], keys[pygame.K_s], dt)

        # Update ball
        self.ball.update(dt)

        # Collisions with paddles
        self.ball.collide_paddle(self.player)
        self.ball.collide_paddle(self.ai)

        # Scoring
        if self.ball.rect.right < 0:
            self.score.right += 1
            self.ball.reset(direction=1)
        elif self.ball.rect.left > WIDTH:
            self.score.left += 1
            self.ball.reset(direction=-1)

        # AI update
        self._update_ai(dt)

    def _update_ai(self, dt: float) -> None:
        # Only actively track when ball moves towards AI
        ball_moving_to_ai = self.ball.vel.x > 0

        self.ai_timer += self.clock.get_time()
        if self.ai_timer >= self.ai_reaction_ms:
            self.ai_timer = 0
            if ball_moving_to_ai:
                # Predict target with some error
                predicted_y = self._predict_ball_y_at_x(self.ai.rect.centerx)
                noise = random.uniform(-self.ai_error_margin, self.ai_error_margin)
                self.ai_target_y = max(0, min(HEIGHT, predicted_y + noise))
            else:
                # Drift back to center when ball is going away
                self.ai_target_y = HEIGHT // 2

        # Move towards target, with capped speed
        self.ai.move_towards(self.ai_target_y, dt)

    def _predict_ball_y_at_x(self, x: int) -> float:
        """Rudimentary prediction: simulate y given current velocity, reflecting off walls."""
        pos = pygame.Vector2(self.ball.rect.center)
        vel = pygame.Vector2(self.ball.vel)
        # If velocity is zero (e.g., right after reset), avoid division by zero
        if vel.x == 0:
            return pos.y
        # Time until x coordinate reaches the target x
        time_to_x = (x - pos.x) / vel.x
        # If prediction is behind, just use current
        if time_to_x <= 0:
            return pos.y
        # Simulate vertical motion with reflections on top/bottom walls
        simulated_y = pos.y + vel.y * time_to_x
        # Reflect off walls by mirroring within [0, HEIGHT]
        period = 2 * HEIGHT
        mod = simulated_y % period
        reflected = mod if mod <= HEIGHT else period - mod
        return reflected

    def _draw_center_line(self) -> None:
        dash_h = 12
        gap = 10
        x = WIDTH // 2 - 2
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(self.screen, DIM_WHITE, (x, y, 4, dash_h), border_radius=2)
            y += dash_h + gap

    def _draw_scores(self) -> None:
        left_surf = self.font.render(str(self.score.left), True, WHITE)
        right_surf = self.font.render(str(self.score.right), True, WHITE)
        self.screen.blit(left_surf, (WIDTH * 0.25 - left_surf.get_width() / 2, 20))
        self.screen.blit(right_surf, (WIDTH * 0.75 - right_surf.get_width() / 2, 20))

        hint = self.small_font.render("W/S to move • ESC to quit", True, DIM_WHITE)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 28))

    def _draw(self) -> None:
        self.screen.fill(DARK)
        self._draw_center_line()

        # Draw entities
        self.player.draw(self.screen, WHITE)
        self.ai.draw(self.screen, WHITE)
        self.ball.draw(self.screen, ACCENT)

        # Scores and UI
        self._draw_scores()

        pygame.display.flip()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
