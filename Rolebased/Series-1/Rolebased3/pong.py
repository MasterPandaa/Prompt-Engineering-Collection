import math
import random
import sys
from dataclasses import dataclass
from typing import Tuple

import pygame

# --- Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 12, 100
BALL_SIZE = 14

PADDLE_SPEED = 6
BALL_SPEED_START = 5.0
BALL_SPEED_MAX = 11.0
BALL_SPEED_INCREMENT_ON_HIT = 0.35

SCORE_TO_WIN = 11

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)


@dataclass
class Paddle:
    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    speed: int = PADDLE_SPEED

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dy: float) -> None:
        self.y += dy
        # Clamp to screen
        self.y = max(0, min(HEIGHT - self.height, self.y))

    def ai_follow(self, target_y: float, reaction: float, error_margin: float) -> None:
        """
        Simple yet fair AI:
        - reaction: [0..1] how much of the distance to correct per frame; lower = slower reaction.
        - error_margin: pixels to offset target to make AI imperfect.
        """
        center = self.y + self.height / 2
        # Apply error margin by offsetting the target toward a noisy point
        desired = target_y + error_margin
        diff = desired - center
        move_amount = diff * reaction

        # Cap movement by paddle max speed
        move_amount = max(-self.speed, min(self.speed, move_amount))
        self.move(move_amount)

    @property
    def center(self) -> Tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2


@dataclass
class Ball:
    x: float
    y: float
    size: int = BALL_SIZE
    speed: float = BALL_SPEED_START
    angle: float = 0.0  # Radians; 0 to the right, pi to the left.

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size / 2), int(self.y - self.size / 2), self.size, self.size)

    def reset(self, direction: int) -> None:
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.speed = BALL_SPEED_START
        # Launch angle with slight randomness; direction: -1 left, 1 right
        base = random.uniform(-0.35, 0.35)
        self.angle = base if direction > 0 else math.pi - base

    def update(self) -> None:
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Bounce on top/bottom
        if self.y - self.size / 2 <= 0:
            self.y = self.size / 2
            self.angle = -self.angle
        elif self.y + self.size / 2 >= HEIGHT:
            self.y = HEIGHT - self.size / 2
            self.angle = -self.angle

        # Normalize angle to keep within -pi..pi
        self.angle = (self.angle + math.pi) % (2 * math.pi) - math.pi

    def reflect_from_paddle(self, paddle: Paddle) -> None:
        """
        Reflect ball off a paddle with angle based on contact point.
        Hitting near paddle center reflects mostly horizontally; near edges gives more vertical angle.
        Also, slightly increase ball speed up to a max.
        """
        # Determine relative intersection point on the paddle [-1..1]
        paddle_rect = paddle.rect()
        rel = ((self.y - paddle_rect.centery) / (paddle_rect.height / 2))
        rel = max(-1.0, min(1.0, rel))

        max_deflection = math.radians(50)  # limit to avoid near-vertical shots
        deflection = rel * max_deflection

        # Determine horizontal direction after hit (depends on which side)
        going_right = math.cos(self.angle) > 0
        if paddle_rect.centerx < WIDTH / 2:
            # Left paddle should send ball to the right
            self.angle = deflection
            if self.x < paddle_rect.right:
                self.x = paddle_rect.right + self.size / 2
        else:
            # Right paddle should send ball to the left
            self.angle = math.pi - deflection
            if self.x > paddle_rect.left:
                self.x = paddle_rect.left - self.size / 2

        # Ensure we maintain vertical direction continuity when hitting edge cases
        if going_right and math.cos(self.angle) < 0:
            pass
        if (not going_right) and math.cos(self.angle) > 0:
            pass

        # Increase speed slightly on each paddle hit
        self.speed = min(BALL_SPEED_MAX, self.speed + BALL_SPEED_INCREMENT_ON_HIT)


class ScoreBoard:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.left = 0
        self.right = 0

    def draw(self, surface: pygame.Surface) -> None:
        left_text = self.font.render(str(self.left), True, WHITE)
        right_text = self.font.render(str(self.right), True, WHITE)
        surface.blit(left_text, (WIDTH * 0.25 - left_text.get_width() / 2, 20))
        surface.blit(right_text, (WIDTH * 0.75 - right_text.get_width() / 2, 20))

    def reset(self) -> None:
        self.left = 0
        self.right = 0


class PongGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong - Pygame")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 36)
        self.small_font = pygame.font.SysFont("consolas", 20)

        # Entities
        self.left_paddle = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.right_paddle = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(WIDTH / 2, HEIGHT / 2)
        self.ball.reset(direction=random.choice([-1, 1]))

        self.score = ScoreBoard(self.font)

        # AI control parameters
        self.ai_reaction = 0.22  # fraction per frame; lower=slower
        self.ai_error_base = 18.0  # base error margin in pixels
        self.ai_error_random = 22.0  # additional random component
        self.ai_sample_interval_ms = 90  # how often AI updates target
        self._ai_next_sample_time = 0
        self._ai_tracked_target_y = HEIGHT / 2
        self._ai_error_current = 0.0

        self.running = True

    def process_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w]:
            dy -= self.left_paddle.speed
        if keys[pygame.K_s]:
            dy += self.left_paddle.speed
        self.left_paddle.move(dy)

    def update_ai(self) -> None:
        now = pygame.time.get_ticks()
        if now >= self._ai_next_sample_time:
            self._ai_next_sample_time = now + self.ai_sample_interval_ms
            # Predict a bit into the future using current velocity
            vx = math.cos(self.ball.angle) * self.ball.speed
            vy = math.sin(self.ball.angle) * self.ball.speed
            if vx != 0:
                # time for ball to reach AI paddle x
                distance_x = (self.right_paddle.x - self.ball.x)
                t = distance_x / vx
            else:
                t = 0
            # Predict y with simple wall bounces approximation
            predicted_y = self.ball.y + vy * max(0, t)
            predicted_y = self._reflect_y_over_bounds(predicted_y)

            self._ai_tracked_target_y = predicted_y
            # New error margin each sample to keep human-beatable
            self._ai_error_current = (random.uniform(-self.ai_error_random, self.ai_error_random) +
                                      random.choice([-1, 1]) * self.ai_error_base)

        self.right_paddle.ai_follow(self._ai_tracked_target_y, self.ai_reaction, self._ai_error_current)

    @staticmethod
    def _reflect_y_over_bounds(y_value: float) -> float:
        """
        Reflect a y value across the top/bottom bounds as if it bounced in a straight corridor.
        This is a helper to keep AI prediction reasonable without simulating full physics.
        """
        corridor = HEIGHT
        if corridor <= 0:
            return y_value
        # Bring into repeating corridor [0, 2H]
        y = y_value % (2 * corridor)
        if y > corridor:
            y = 2 * corridor - y
        return max(0, min(HEIGHT, y))

    def update(self) -> None:
        self.ball.update()

        # Check paddle collisions
        if self.ball.rect().colliderect(self.left_paddle.rect()):
            self.ball.reflect_from_paddle(self.left_paddle)
        elif self.ball.rect().colliderect(self.right_paddle.rect()):
            self.ball.reflect_from_paddle(self.right_paddle)

        # Scoring
        if self.ball.x < -self.ball.size:
            self.score.right += 1
            self.ball.reset(direction=1)
        elif self.ball.x > WIDTH + self.ball.size:
            self.score.left += 1
            self.ball.reset(direction=-1)

        # Update AI after physics so it reacts to latest state
        self.update_ai()

    def draw_center_line(self) -> None:
        dash_height = 14
        gap = 10
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(self.screen, GRAY, pygame.Rect(WIDTH // 2 - 2, y, 4, dash_height))
            y += dash_height + gap

    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.draw_center_line()

        # Draw paddles and ball
        pygame.draw.rect(self.screen, WHITE, self.left_paddle.rect())
        pygame.draw.rect(self.screen, WHITE, self.right_paddle.rect())
        pygame.draw.rect(self.screen, WHITE, self.ball.rect())

        # Draw score
        self.score.draw(self.screen)

        # Draw help
        help_text = self.small_font.render("W/S to move | ESC to quit", True, GRAY)
        self.screen.blit(help_text, (WIDTH / 2 - help_text.get_width() / 2, HEIGHT - 30))

        # Draw win text
        if self.score.left >= SCORE_TO_WIN or self.score.right >= SCORE_TO_WIN:
            winner = "Player" if self.score.left > self.score.right else "AI"
            win_text = self.font.render(f"{winner} wins! Press R to reset", True, WHITE)
            self.screen.blit(win_text, (WIDTH / 2 - win_text.get_width() / 2, HEIGHT / 2 - 30))

        pygame.display.flip()

    def maybe_reset_or_quit(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False
        if keys[pygame.K_r] and (self.score.left >= SCORE_TO_WIN or self.score.right >= SCORE_TO_WIN):
            self.score.reset()
            self.ball.reset(direction=random.choice([-1, 1]))

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.process_input()
            self.update()
            self.draw()
            self.maybe_reset_or_quit()

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    PongGame().run()
