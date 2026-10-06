import math
import random
import sys
from typing import Tuple

import pygame


# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 12
PADDLE_HEIGHT = 100
PADDLE_MARGIN = 30
PADDLE_SPEED = 420  # px/s (player)
AI_MAX_SPEED = 390  # px/s (AI paddle max tracking speed)

BALL_SIZE = 14
BALL_SPEED = 360  # base speed in px/s
BALL_SPEED_INCREMENT = 18  # added after each paddle hit
BALL_SPEED_MAX = 680

SCORE_TO_WIN = 10
SERVE_DELAY = 800  # ms before ball is served after a score

# AI behavior tuning (fair, beatable)
AI_REACTION_MS = (80, 160)  # random reaction delay range
AI_AIM_ERROR_PX = (10, 48)  # random vertical error band at high speeds
AI_TRACK_DAMPING = 0.22  # low-pass filter on target tracking (0..1)
AI_LOOKAHEAD_FACTOR = 0.55  # how much to lead when ball moves toward AI

# Colors
WHITE = (240, 240, 240)
ACCENT = (80, 160, 255)
DARK = (25, 28, 35)
DIM = (60, 64, 72)


class Paddle:
    def __init__(self, x: int, y: int, is_ai: bool = False):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.is_ai = is_ai
        self.speed = AI_MAX_SPEED if is_ai else PADDLE_SPEED
        # AI state
        self._reaction_timer = 0.0
        self._next_reaction_at = self._rand_reaction_delay()
        self._target_y = float(self.rect.centery)
        self._aim_error = 0.0

    def _rand_reaction_delay(self) -> float:
        return random.uniform(*AI_REACTION_MS)

    def _rand_aim_error(self) -> float:
        return random.uniform(*AI_AIM_ERROR_PX) * random.choice([-1.0, 1.0])

    def update_player(self, dt: float, up: bool, down: bool) -> None:
        dy = 0.0
        if up:
            dy -= self.speed * dt
        if down:
            dy += self.speed * dt
        self.rect.centery = max(
            PADDLE_HEIGHT // 2, min(SCREEN_HEIGHT - PADDLE_HEIGHT // 2, int(self.rect.centery + dy))
        )

    def update_ai(self, dt: float, ball: "Ball") -> None:
        # Update reaction timer
        self._reaction_timer += dt * 1000.0
        if self._reaction_timer >= self._next_reaction_at:
            # Re-decide target periodically to avoid perfect tracking
            self._reaction_timer = 0.0
            self._next_reaction_at = self._rand_reaction_delay()

            # If ball moving toward AI, lead slightly, else drift back to center
            if ball.velocity[0] > 0:
                # Estimate where ball will be when it reaches our x
                time_to_reach = ((self.rect.left - ball.rect.right) / ball.velocity[0]) if ball.velocity[0] != 0 else 0
                predicted_y = ball.rect.centery + ball.velocity[1] * time_to_reach * AI_LOOKAHEAD_FACTOR
                # Reflect off top/bottom in prediction to avoid over-shoot
                predicted_y = reflect_off_bounds(predicted_y, BALL_SIZE // 2, SCREEN_HEIGHT - BALL_SIZE // 2)
                self._aim_error = self._rand_aim_error() * min(1.0, abs(ball.velocity[0]) / BALL_SPEED_MAX)
                self._target_y = float(predicted_y + self._aim_error)
            else:
                # Ball moving away: go back toward center with slight randomness
                self._aim_error = self._rand_aim_error() * 0.3
                self._target_y = SCREEN_HEIGHT / 2 + self._aim_error

        # Smoothly track target with damping and speed limit
        desired = self._target_y - self.rect.centery
        desired *= AI_TRACK_DAMPING
        max_step = self.speed * dt
        step = clamp(desired, -max_step, max_step)
        self.rect.centery = int(self.rect.centery + step)

        # Keep within bounds
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=6)


class Ball:
    def __init__(self, center: Tuple[int, int]):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.rect.center = center
        self.velocity = pygame.Vector2(0, 0)
        self.speed = BALL_SPEED
        self._serve_dir = random.choice([-1, 1])
        self._serve_time = pygame.time.get_ticks() + SERVE_DELAY

    def serve_if_ready(self) -> None:
        now = pygame.time.get_ticks()
        if self.velocity.length_squared() == 0 and now >= self._serve_time:
            angle = random.uniform(-0.35, 0.35)  # slightly off horizontal
            self.velocity.x = math.copysign(self.speed * math.cos(angle), self._serve_dir)
            self.velocity.y = self.speed * math.sin(angle)

    def reset(self, scorer_dir: int) -> None:
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = BALL_SPEED
        self.velocity.xy = (0, 0)
        self._serve_dir = scorer_dir
        self._serve_time = pygame.time.get_ticks() + SERVE_DELAY

    def update(self, dt: float, left_paddle: Paddle, right_paddle: Paddle) -> int:
        # Returns scoring direction: -1 if right scored (ball out left), +1 if left scored, 0 otherwise
        self.serve_if_ready()
        if self.velocity.length_squared() == 0:
            return 0

        # Move
        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)

        # Collide with top/bottom
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity.y *= -1

        # Paddle collisions
        if self.rect.colliderect(left_paddle.rect) and self.velocity.x < 0:
            self._bounce_off_paddle(left_paddle, is_left=True)
        elif self.rect.colliderect(right_paddle.rect) and self.velocity.x > 0:
            self._bounce_off_paddle(right_paddle, is_left=False)

        # Out of bounds (score)
        if self.rect.right < 0:
            return 1  # right player scores (AI)
        if self.rect.left > SCREEN_WIDTH:
            return -1  # left player scores
        return 0

    def _bounce_off_paddle(self, paddle: Paddle, is_left: bool) -> None:
        # Compute offset of hit relative to paddle center -> angle
        offset = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        offset = clamp(offset, -1.0, 1.0)
        angle = offset * 0.9  # max ~52 degrees

        # Increase speed on each hit up to a cap
        self.speed = min(BALL_SPEED_MAX, self.speed + BALL_SPEED_INCREMENT)
        direction = 1 if not is_left else -1
        vx = direction * self.speed * math.cos(angle)
        vy = self.speed * math.sin(angle)

        # Nudge ball outside paddle to avoid sticking
        if is_left:
            self.rect.left = paddle.rect.right
        else:
            self.rect.right = paddle.rect.left

        # Add a tiny randomization to avoid infinite loops
        vy += random.uniform(-8.0, 8.0)

        self.velocity.xy = (vx, vy)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, ACCENT, self.rect, border_radius=4)


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def reflect_off_bounds(y: float, min_y: float, max_y: float) -> float:
    # Reflect a value between bounds as if bouncing between them
    span = max_y - min_y
    if span <= 0:
        return clamp(y, min_y, max_y)
    # Map into a repeating sawtooth and reflect
    t = (y - min_y) % (2 * span)
    if t > span:
        t = 2 * span - t
    return min_y + t


def draw_center_net(surface: pygame.Surface) -> None:
    dash_h = 18
    gap = 12
    x = SCREEN_WIDTH // 2 - 2
    for y in range(0, SCREEN_HEIGHT, dash_h + gap):
        pygame.draw.rect(surface, DIM, pygame.Rect(x, y, 4, dash_h), border_radius=2)


def render_score(surface: pygame.Surface, font: pygame.font.Font, left: int, right: int) -> None:
    left_surf = font.render(str(left), True, WHITE)
    right_surf = font.render(str(right), True, WHITE)
    surface.blit(left_surf, (SCREEN_WIDTH * 0.25 - left_surf.get_width() / 2, 24))
    surface.blit(right_surf, (SCREEN_WIDTH * 0.75 - right_surf.get_width() / 2, 24))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Pong - Pygame")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    try:
        font = pygame.font.SysFont("Consolas", 48)
        small_font = pygame.font.SysFont("Consolas", 20)
    except Exception:
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 20)

    # Create objects
    left_paddle = Paddle(PADDLE_MARGIN, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, is_ai=False)
    right_paddle = Paddle(
        SCREEN_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH,
        SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
        is_ai=True,
    )
    ball = Ball((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    left_score = 0
    right_score = 0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        up = keys[pygame.K_w]
        down = keys[pygame.K_s]

        # Update
        left_paddle.update_player(dt, up, down)
        right_paddle.update_ai(dt, ball)
        score_dir = ball.update(dt, left_paddle, right_paddle)
        if score_dir != 0:
            if score_dir > 0:
                left_score += 1
                ball.reset(scorer_dir=1)  # serve to the right
            else:
                right_score += 1
                ball.reset(scorer_dir=-1)  # serve to the left

        # Draw
        screen.fill(DARK)
        draw_center_net(screen)
        render_score(screen, font, left_score, right_score)

        # Tips/controls text
        tip = small_font.render("Controls: W/S to move | ESC to quit", True, DIM)
        screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, SCREEN_HEIGHT - 32))

        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Win banner
        if left_score >= SCORE_TO_WIN or right_score >= SCORE_TO_WIN:
            winner = "You" if left_score > right_score else "AI"
            msg = font.render(f"{winner} win! Press ESC to exit.", True, ACCENT)
            screen.blit(
                msg,
                (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2),
            )
            # Freeze ball and paddles when game ended
            ball.velocity.xy = (0, 0)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
